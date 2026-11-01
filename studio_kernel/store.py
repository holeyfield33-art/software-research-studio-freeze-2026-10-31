"""Local transactional history. Canonical JSON records remain immutable.

SQLite is used for atomic record/event commits and stale-writer exclusion, not
as a service. Hashes detect inconsistent history, not a malicious DB owner.
"""
from datetime import datetime, timezone
from contextlib import contextmanager
from pathlib import Path
import sqlite3

from .canonical import canonical, digest, load_json, reference, references, schema_errors
from .validate import invalidated


class HistoryError(ValueError):
    pass


def entity(kind, identifier, project, owner, body, scope='project'):
    return {'contract_version': '0.1.0', 'kind': kind, 'id': identifier,
            'revision': 1, 'project_id': project, 'scope': scope, 'owner': owner,
            'created_at': datetime.now(timezone.utc).isoformat(), 'derived_from': [], 'body': body}


class Store:
    def __init__(self, path, project_id):
        self.path = Path(path)
        self.project_id = project_id
        self.path.parent.mkdir(parents=True, exist_ok=True)
        with self.connect() as db:
            db.executescript('''
                CREATE TABLE IF NOT EXISTS config (project TEXT NOT NULL);
                CREATE TABLE IF NOT EXISTS records (
                    id TEXT, revision INTEGER, sha TEXT, data BLOB,
                    PRIMARY KEY(id, revision));
                CREATE TABLE IF NOT EXISTS commits (
                    sequence INTEGER PRIMARY KEY, event BLOB NOT NULL,
                    candidate BLOB NOT NULL, prior_commit TEXT, sha TEXT NOT NULL);
                CREATE TRIGGER IF NOT EXISTS records_no_update BEFORE UPDATE ON records
                BEGIN SELECT RAISE(ABORT, 'immutable records'); END;
                CREATE TRIGGER IF NOT EXISTS records_no_delete BEFORE DELETE ON records
                BEGIN SELECT RAISE(ABORT, 'immutable records'); END;
                CREATE TRIGGER IF NOT EXISTS commits_no_update BEFORE UPDATE ON commits
                BEGIN SELECT RAISE(ABORT, 'immutable commits'); END;
                CREATE TRIGGER IF NOT EXISTS commits_no_delete BEFORE DELETE ON commits
                BEGIN SELECT RAISE(ABORT, 'immutable commits'); END;
            ''')
            rows = db.execute('SELECT project FROM config').fetchall()
            if not rows:
                db.execute('INSERT INTO config VALUES (?)', (project_id,))
            elif rows != [(project_id,)]:
                raise HistoryError('Store belongs to another project')

    @contextmanager
    def connect(self):
        db = sqlite3.connect(self.path, timeout=10)
        try:
            db.execute('PRAGMA synchronous=FULL')
            with db:
                yield db
        finally:
            db.close()

    def _replay(self, db):
        records, events = [], []
        prior_event, prior_commit, candidate = None, None, None
        stored = {}
        for rid, revision, sha, data in db.execute('SELECT id, revision, sha, data FROM records'):
            r = load_json(data)
            if canonical(r) != data or digest(r) != sha or schema_errors(r) or (r['id'], r['revision']) != (rid, revision) or r['project_id'] != self.project_id:
                raise HistoryError('Corrupt or noncanonical stored record')
            stored[(rid, revision)] = r
        committed = set()
        for sequence, raw_event, raw_candidate, previous, sha in db.execute('SELECT sequence,event,candidate,prior_commit,sha FROM commits ORDER BY sequence'):
            event, candidate = load_json(raw_event), load_json(raw_candidate)
            wrapper = {'event': event, 'candidate': candidate, 'prior_commit_sha256': previous}
            if sequence != len(events) + 1 or previous != prior_commit or digest(wrapper) != sha or schema_errors(event) or canonical(event) != raw_event or canonical(candidate) != raw_candidate:
                raise HistoryError('Broken commit chain')
            body = event['body']
            if event['kind'] != 'ChangeEvent' or event['project_id'] != self.project_id or body['sequence'] != sequence or body['expected_state_revision'] != sequence - 1 or body['prior_event_sha256'] != prior_event:
                raise HistoryError('Broken canonical event sequence')
            batch = []
            for ref in body['changed_refs']:
                key = (ref['id'], ref['revision'])
                row = stored.get(key)
                if key in committed or row is None or reference(row) != ref:
                    raise HistoryError('Event references missing, repeated or altered record')
                batch.append(row)
                committed.add(key)
            self._check_batch(records, batch)
            records.extend(batch)
            expected_invalid = sorted((reference(r) for r in records if digest(r) in invalidated(records, candidate)), key=lambda r: (r['id'], r['revision']))
            if body['invalidated_refs'] != expected_invalid:
                raise HistoryError('Invalidation projection differs from event')
            events.append(event)
            prior_event, prior_commit = digest(event), sha
        if committed != set(stored):
            raise HistoryError('Uncommitted/orphan stored records')
        return {'records': records, 'events': events, 'candidate': candidate, 'revision': len(events), 'commit_sha256': prior_commit}

    def _check_batch(self, old, batch):
        if not isinstance(batch, list) or not batch:
            raise HistoryError('Expected a nonempty list of records')
        index = {(r['id'], r['revision']): r for r in old}
        latest = {}
        for r in old:
            latest[r['id']] = max(latest.get(r['id'], 0), r['revision'])
        for r in batch:
            if schema_errors(r) or r['project_id'] != self.project_id or r['kind'] in ('ChangeEvent', 'StateSnapshot'):
                raise HistoryError('Invalid record, project or reserved projection kind')
            key = (r['id'], r['revision'])
            if key in index or r['revision'] != latest.get(r['id'], 0) + 1:
                raise HistoryError('Duplicate identity or missing revision history')
            prior = index.get((r['id'], r['revision'] - 1))
            if prior and prior['kind'] != r['kind']:
                raise HistoryError('Record kind cannot change')
            index[key] = r
            latest[r['id']] = r['revision']
        for r in batch:
            for ref in references(r):
                target = index.get((ref['id'], ref['revision']))
                if target is None or reference(target) != ref:
                    raise HistoryError('Missing or hash-mismatched record reference')

    def read(self):
        with self.connect() as db:
            db.execute('BEGIN')
            return self._replay(db)

    def commit(self, batch, *, expected_revision, candidate, actor, reason, before_commit=None):
        """Persist observations even when semantically incomplete; no readiness grant.

        before_commit is an injectable failure hook for transaction tests only.
        """
        if type(expected_revision) is not int or expected_revision < 0 or not isinstance(actor, str) or not actor.strip() or not isinstance(reason, str) or not reason.strip():
            raise HistoryError('Invalid commit metadata')
        # Freeze caller-owned input before validation and hashing.
        batch, candidate = load_json(canonical(batch)), load_json(canonical(candidate))
        # Use the canonical candidate schema by validating a snapshot projection.
        probe = entity('StateSnapshot', 'ua.state.probe', self.project_id, actor, {'state_revision': expected_revision, 'last_event_ref': None, 'scopes': [{'scope': 'project', 'status': 'ACTIVE'}], 'blockers': [], 'current_candidate': candidate, 'next_task_refs': []})
        if schema_errors(probe):
            raise HistoryError('Invalid candidate')
        with self.connect() as db:
            db.execute('BEGIN IMMEDIATE')
            state = self._replay(db)
            if state['revision'] != expected_revision:
                raise HistoryError('Stale writer: expected state revision mismatch')
            self._check_batch(state['records'], batch)
            for r in batch:
                if r['kind'] == 'TaskPacket' and r['body']['expected_state_revision'] != expected_revision:
                    raise HistoryError('Task was prepared against stale state')
            records = state['records'] + batch
            stale = invalidated(records, candidate)
            event = entity('ChangeEvent', f'ua.history.event.{expected_revision + 1}', self.project_id, actor, {
                'sequence': expected_revision + 1, 'expected_state_revision': expected_revision,
                'prior_event_sha256': digest(state['events'][-1]) if state['events'] else None,
                'actor': actor, 'changed_refs': [reference(r) for r in batch],
                'invalidated_refs': sorted((reference(r) for r in records if digest(r) in stale), key=lambda r: (r['id'], r['revision'])), 'reason': reason})
            if schema_errors(event):
                raise HistoryError('Invalid generated event')
            wrapper = {'event': event, 'candidate': candidate, 'prior_commit_sha256': state['commit_sha256']}
            for r in batch:
                db.execute('INSERT INTO records VALUES (?,?,?,?)', (r['id'], r['revision'], digest(r), canonical(r)))
            db.execute('INSERT INTO commits VALUES (?,?,?,?,?)', (expected_revision + 1, canonical(event), canonical(candidate), state['commit_sha256'], digest(wrapper)))
            if before_commit:
                before_commit()
        return reference(event)

    def snapshot(self, owner='operator'):
        state = self.read()
        stale = invalidated(state['records'], state['candidate'])
        latest = {}
        for r in state['records']:
            latest[r['id']] = r
        current_stale = [r['id'] for r in latest.values() if digest(r) in stale]
        snapshot = entity('StateSnapshot', 'ua.state.snapshot', self.project_id, owner, {
            'state_revision': state['revision'], 'last_event_ref': reference(state['events'][-1]) if state['events'] else None,
            'scopes': [{'scope': 'project', 'status': 'STALE' if current_stale else 'ACTIVE' if state['revision'] else 'NOT_STARTED'}],
            'blockers': ['Reassess stale input: ' + rid for rid in sorted(current_stale)],
            'current_candidate': state['candidate'], 'next_task_refs': []})
        if schema_errors(snapshot):
            raise HistoryError('Invalid derived snapshot')
        return snapshot
