"""Canonical schema plus semantic checks; host receipts are supplied by trusted code."""
from datetime import datetime, timezone
from pathlib import Path
import hashlib
import json
import zipfile

from .canonical import ROOT, digest, reference, references, schema_errors


def parse_time(value):
    return datetime.fromisoformat(value.replace('Z', '+00:00'))


def contains(parent, child):
    return parent == child or child.startswith(parent.rstrip('/') + '/')


def safe_path(value):
    return isinstance(value, str) and bool(value) and all(p not in ('', '.', '..') and not p.endswith((' ', '.')) for p in value.split('/')) and not any(c in value for c in '\\:*?\x00')


def invalidated(records, candidate=None):
    """Derive stale identities from explicit references and candidate changes."""
    latest = {}
    for r in records:
        if r['revision'] > latest.get(r['id'], {}).get('revision', 0):
            latest[r['id']] = r
    stale = set()
    for r in records:
        b = r['body']
        bound = b.get('candidate', b.get('baseline') if r['kind'] in ('TaskPacket', 'Authority') else None)
        if candidate is not None and bound is not None and bound != candidate:
            stale.add(digest(r))
        for ref in references(r):
            if ref['id'] in latest and ref['revision'] != latest[ref['id']]['revision']:
                stale.add(digest(r))
    changed = True
    while changed:
        before = len(stale)
        for r in records:
            if any(ref['sha256'] in stale for ref in references(r)):
                stale.add(digest(r))
        changed = len(stale) != before
    return stale


def validate(records, *, project_id, candidate=None, artifact_root=None,
             authority_receipt=None, run_receipt=None, release_receipt=None, now=None):
    """Receipt callbacks must verify host-issued evidence, not record assertions.

    PASS means implemented consistency checks pass; it is not product readiness.
    Unsupported domain modules and missing external receipts return INCOMPLETE.
    """
    findings = []
    def add(code, record, message, level='FAIL'):
        findings.append({'code': code, 'record': record, 'message': message, 'level': level})
    def report(stale=()):
        status = 'FAIL' if any(f['level'] == 'FAIL' for f in findings) else 'INCOMPLETE' if findings else 'PASS'
        releases = [r for r in records if isinstance(r, dict) and r.get('kind') == 'ReleaseDecision' and isinstance(r.get('body'), dict)] if isinstance(records, list) else []
        disposition = 'APPROVE' if releases and status == 'PASS' and all(r['body'].get('decision') == 'APPROVE' for r in releases) else 'HOLD' if releases else 'NOT_REQUESTED'
        return {'status': status, 'release_disposition': disposition, 'findings': findings, 'stale_sha256': sorted(stale), 'scope': 'Canonical structure and implemented semantic checks; not universal development acceptance'}
    if not isinstance(records, list):
        add('COLLECTION', 'records', 'Expected a list of canonical records')
        return report()
    index, latest = {}, {}
    for r in records:
        errors = schema_errors(r)
        if errors:
            add('SCHEMA', r.get('id', 'record') if isinstance(r, dict) else 'record', '; '.join(errors))
            continue
        if r['project_id'] != project_id:
            add('PROJECT', r['id'], 'Cross-project reference/record forbidden')
        key = (r['id'], r['revision'])
        if key in index:
            add('DUPLICATE', r['id'], 'Duplicate ID/revision')
        index[key] = r
        if r['revision'] > latest.get(r['id'], {}).get('revision', 0):
            latest[r['id']] = r
    if findings:
        return report()
    def resolve(ref, owner, kind=None):
        r = index.get((ref['id'], ref['revision']))
        if r is None or digest(r) != ref['sha256'] or (kind and r['kind'] != kind):
            add('REFERENCE', owner, 'Missing, hash-mismatched or incorrectly typed reference: ' + ref['id'])
            return None
        return r
    for r in records:
        for ref in references(r):
            resolve(ref, r['id'])
    if findings:
        return report()
    for identifier in latest:
        versions = sorted(r['revision'] for r in records if r['id'] == identifier)
        if versions != list(range(1, max(versions) + 1)):
            add('HISTORY', identifier, 'Missing record revisions')
        if len({r['kind'] for r in records if r['id'] == identifier}) != 1:
            add('HISTORY', identifier, 'Record kind changed under same identity')
    stale = invalidated(records, candidate)
    # All exact references are dependencies; cyclic hash-linked records are invalid.
    pending = {digest(r): {ref['sha256'] for ref in references(r)} for r in records}
    while pending:
        ready = {key for key, deps in pending.items() if not deps}
        if not ready:
            add('CYCLE', 'records', 'Reference graph must be acyclic')
            break
        pending = {key: deps - ready for key, deps in pending.items() if key not in ready}
    current = list(latest.values())
    clock = now or datetime.now(timezone.utc)
    facts = [r for r in current if r['kind'] == 'Fact']
    for i, fact in enumerate(facts):
        b = fact['body']
        if b['state'] == 'unknown' and b['value'] is not None:
            add('UNKNOWN_VALUE', fact['id'], 'Unknown facts cannot carry a known scalar value')
        for other in facts[i + 1:]:
            ob = other['body']
            overlap = contains(fact['scope'], other['scope']) or contains(other['scope'], fact['scope'])
            if overlap and b['predicate'] == ob['predicate'] and b['state'] != 'unknown' and ob['state'] != 'unknown' and (b['state'], b['value'], b['unit']) != (ob['state'], ob['value'], ob['unit']):
                add('FACT_CONFLICT', fact['id'], 'Overlapping structured facts conflict: ' + other['id'])
    corpus = ROOT / 'preserved_freezes/SRS-FREEZE-2026-10-31-v1/tree/current_003R'
    def registry_ref(ref, rid):
        if ref['checkpoint_sha256'] != '5fea1fe5e8f19064df7ee9af4386aeb85046003c99ee83f9b4569432f0992aa8' or not safe_path(ref['partition']):
            add('REGISTRY', rid, 'Wrong checkpoint digest or unsafe partition')
            return
        path = (corpus / ref['partition']).resolve()
        if not path.is_relative_to(corpus.resolve()) or not path.is_file():
            add('REGISTRY', rid, 'Unknown partition')
            return
        checkpoint = corpus.parent / 'original_checkpoints/STUDIO_KNOWLEDGE_003R_checkpoint.zip'
        if not checkpoint.is_file() or hashlib.sha256(checkpoint.read_bytes()).hexdigest() != ref['checkpoint_sha256']:
            add('REGISTRY', rid, 'Original checkpoint archive missing or altered')
            return
        with zipfile.ZipFile(checkpoint) as archive:
            if ref['partition'] not in archive.namelist() or archive.read(ref['partition']) != path.read_bytes():
                add('REGISTRY', rid, 'Partition not byte-identical to original checkpoint')
                return
        # Pin partition bytes to the archived manifest before resolving line IDs.
        manifest = json.loads((corpus / 'manifest.json').read_text(encoding='utf-8'))
        if hashlib.sha256(path.read_bytes()).hexdigest() != manifest['sha256'].get(ref['partition']):
            add('REGISTRY', rid, 'Partition differs from frozen manifest')
            return
        lines = path.read_text(encoding='utf-8').splitlines()
        record = json.loads(lines[ref['line'] - 1]) if 0 < ref['line'] <= len(lines) else {}
        if record.get('id') != ref['record_id'] or record.get('version') != ref['record_version']:
            add('REGISTRY', rid, 'Registry ID/version/line mismatch')
        sources = set(record.get('source_ids', []))
        if not set(ref['source_ids']) <= sources:
            add('REGISTRY_SOURCE', rid, 'Claimed source not attached to original record')
        edges = {r['id']: r for line in (corpus / 'dataset/v1/relationships.jsonl').read_text(encoding='utf-8').splitlines() if line.strip() for r in [json.loads(line)]}
        for key in ref['edge_ids']:
            edge = edges.get(key, {})
            if edge.get('status', 'active') != 'active' or ref['record_id'] not in (edge.get('source_endpoint'), edge.get('target_endpoint')):
                add('REGISTRY_EDGE', rid, 'Unknown, inactive or unrelated relationship')
    def authority(grant, action, scope, principal, baseline):
        if not grant:
            return
        b = grant['body']
        if grant != latest[grant['id']] or digest(grant) in stale or b['status'] != 'GRANTED' or b['action'] != action or b['principal'] != principal or b['baseline'] != baseline or not any(contains(s, scope) for s in b['allowed_scope']) or parse_time(b['expires_at']) <= clock:
            add('AUTHORITY', grant['id'], 'Grant is stale, expired, revoked, denied or does not match action/principal/scope/candidate')
        elif authority_receipt is None or not authority_receipt(grant):
            add('AUTHORITY_RECEIPT', grant['id'], 'No independently authenticated host receipt', 'INCOMPLETE')
    def artifact(path, expected, owner):
        if not safe_path(path):
            add('PATH', owner, 'Unsafe artifact path')
            return
        if artifact_root is None:
            add('ARTIFACT_UNAVAILABLE', owner, 'No artifact root supplied', 'INCOMPLETE')
            return
        root = Path(artifact_root).resolve()
        target = (root / path).resolve()
        if not target.is_relative_to(root):
            add('PATH', owner, 'Artifact resolves outside its permitted root')
        elif not target.is_file() or hashlib.sha256(target.read_bytes()).hexdigest() != expected:
            add('ARTIFACT_DIGEST', owner, 'Artifact missing or digest mismatch')
    for r in current:
        b, kind, rid = r['body'], r['kind'], r['id']
        if digest(r) in stale:
            add('STALE', rid, 'Candidate or referenced input superseded', 'INCOMPLETE')
        if kind == 'DomainContract':
            add('DOMAIN_UNSUPPORTED', rid, 'No module-specific schema/validator registered', 'INCOMPLETE')
        if kind == 'SelectionDecision':
            for choice in b['choices']:
                for ref in choice['registry_refs']:
                    registry_ref(ref, rid)
                choice_facts = [resolve(ref, rid, 'Fact') for ref in choice['fact_refs']]
                if choice['status'] == 'RECOMMENDED' and (choice['missing'] or choice['conflicts'] or not choice_facts or any(f and f['body']['state'] == 'unknown' for f in choice_facts)):
                    add('SELECTION_UNRESOLVED', rid, 'Recommended choice has unknown facts, missing support or conflicts')
                if choice['basis'] == 'research' and choice['status'] == 'RECOMMENDED' and (not choice['registry_refs'] or choice['target'] not in [ref['record_id'] for ref in choice['registry_refs']]):
                    add('SELECTION_SUPPORT', rid, 'Research-backed recommendation lacks its exact registry target')
                if b['plan_status'] == 'COMPLETE' and (choice['status'] == 'INCOMPLETE' or choice['missing'] or choice['conflicts']):
                    add('PLAN_INCOMPLETE', rid, 'Complete plan contains unresolved choices')
        if kind == 'TaskPacket':
            if set(b['allowed_operations']) & set(b['forbidden_operations']):
                add('OPERATIONS', rid, 'Allowed and forbidden operations overlap')
            if not all(safe_path(p) for p in b['allowed_paths']):
                add('PATH', rid, 'Task paths must be literal relative paths')
            for field, expected in [('requirement_refs', 'Requirement'), ('grant_refs', 'Authority')]:
                for ref in b[field]:
                    resolve(ref, rid, expected)
            grants = [resolve(ref, rid, 'Authority') for ref in b['grant_refs']]
            for action in b['allowed_operations']:
                matching = [g for g in grants if g and g['body']['action'] == action]
                if not matching:
                    add('MISSING_GRANT', rid, 'No grant for ' + action, 'INCOMPLETE')
                for g in matching:
                    authority(g, action, r['scope'], r['owner'], b['baseline'])
            for dep in b['dependencies']:
                resolve(dep['task'], rid, 'TaskPacket')
        if kind == 'EvidenceRun':
            packet = resolve(b['packet_ref'], rid, 'TaskPacket')
            if packet and b['oracle_refs'] != packet['body']['oracle_refs']:
                add('ORACLE', rid, 'Run must use the packet oracle references')
            if b['executed'] and (b['started_at'] is None or b['ended_at'] is None or parse_time(b['ended_at']) < parse_time(b['started_at'])):
                add('RUN_TIME', rid, 'Executed run requires ordered start/end timestamps')
            if b['status'] in ('PASS', 'FAIL'):
                for entry in b['artifacts']:
                    artifact(entry['path'], entry['sha256'], rid)
                if run_receipt is None or not run_receipt(r):
                    add('RUN_RECEIPT', rid, 'No independently verified execution/oracle receipt', 'INCOMPLETE')
        if kind == 'GateDecision':
            runs = [resolve(ref, rid, 'EvidenceRun') for ref in b['required_run_refs']]
            if any(run and run['body']['candidate'] != b['candidate'] for run in runs):
                add('GATE_CANDIDATE', rid, 'Gate/run candidates differ')
            expected = 'FAIL' if any(run and run['body']['status'] == 'FAIL' for run in runs) else 'PASS' if runs and all(run and run['body']['status'] == 'PASS' and digest(run) not in stale for run in runs) else 'INCOMPLETE'
            if b['status'] != expected:
                add('GATE_RESULT', rid, 'Gate outcome must be ' + expected)
            if b['status'] == 'PASS' and not b['review_refs']:
                add('GATE_REVIEW', rid, 'No independent review evidence', 'INCOMPLETE')
        if kind == 'ReleaseDecision':
            gates = [resolve(ref, rid, 'GateDecision') for ref in b['required_gate_refs']]
            grant = resolve(b['authority_ref'], rid, 'Authority')
            if b['decision'] == 'APPROVE':
                if not gates or any(g is None or g != latest[g['id']] or g['body']['status'] != 'PASS' or g['body']['candidate'] != b['candidate'] or digest(g) in stale for g in gates):
                    add('RELEASE_GATES', rid, 'Approval requires current passing gates on the same candidate')
                authority(grant, 'release', r['scope'], r['owner'], b['candidate'])
                if not b['support_owner'].strip() or not b['recovery_distribution_disposition'].strip():
                    add('RELEASE_RECOVERY', rid, 'Support and recovery disposition required')
                if release_receipt is None or not release_receipt(r):
                    add('RELEASE_REVIEW', rid, 'Host must verify gate-set completeness, current approval and actual support/recovery evidence', 'INCOMPLETE')
    return report(stale)
