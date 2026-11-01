import copy
from datetime import datetime, timezone
import hashlib
import json
from pathlib import Path
import sqlite3
import subprocess
import sys
from concurrent.futures import ThreadPoolExecutor
import tempfile
import unittest

from .canonical import canonical, digest, load_json, reference, schema_errors
from .store import Store, HistoryError, entity
from .validate import validate

CANDIDATE = {'identity': 'synthetic-revision-1', 'sha256': 'b' * 64}
NOW = datetime(2026, 10, 31, tzinfo=timezone.utc)


def fixtures():
    def row(kind, key, body):
        r = entity(kind, 'ua.example.' + key, 'example', 'owner', body, 'component/cli')
        r['created_at'] = '2026-10-31T00:00:00Z'
        return r
    policy = row('DesignDecision', 'policy', {'problem': 'Synthetic review/policy fixture', 'alternatives': [{'name': 'bounded', 'conditions': ['local change'], 'costs': [], 'exclusions': []}], 'chosen': 'bounded', 'rationale': 'Synthetic oracle and policy, not independently approved', 'status': 'ACCEPTED'})
    requirement = row('Requirement', 'requirement', {'outcome': 'Produce specified local output', 'acceptance': ['Output equals expected bytes'], 'priority': 'required', 'acceptance_owner': 'independent-reviewer', 'oracle_refs': [reference(policy)]})
    def grant(key, action):
        return row('Authority', key, {'principal': 'owner', 'grantor': 'operator', 'action': action, 'allowed_scope': ['component/cli'], 'baseline': CANDIDATE, 'status': 'GRANTED', 'decision_refs': [reference(policy)], 'expires_at': '2099-01-01T00:00:00Z'})
    edit = grant('edit-grant', 'local-edit')
    release_grant = grant('release-grant', 'release')
    task = row('TaskPacket', 'task', {'goal': 'Synthetic bounded local task', 'requirement_refs': [reference(requirement)], 'baseline': CANDIDATE, 'expected_state_revision': 0, 'allowed_paths': ['src'], 'allowed_operations': ['local-edit'], 'forbidden_operations': ['network'], 'budget': {'seconds': 30, 'attempts': 1, 'tokens': 0, 'cost_limit': 0, 'currency': 'USD'}, 'dependencies': [], 'oracle_refs': [reference(policy)], 'grant_refs': [reference(edit)], 'stop_triggers': ['unexpected permission need']})
    run = row('EvidenceRun', 'run', {'candidate': CANDIDATE, 'packet_ref': reference(task), 'oracle_refs': [reference(policy)], 'command': ['synthetic-runner'], 'tool_version': 'fixture-1', 'environment_sha256': 'e' * 64, 'started_at': '2026-10-31T00:00:00Z', 'ended_at': '2026-10-31T00:00:01Z', 'executed': True, 'status': 'PASS', 'producer': 'synthetic-host', 'artifacts': [{'path': 'output.txt', 'sha256': hashlib.sha256(b'expected\n').hexdigest()}], 'limits': ['Synthetic fixture; no project execution demonstrated']})
    review = row('DesignDecision', 'task-review', copy.deepcopy(policy['body']))
    review['owner'] = 'independent-reviewer'
    review['derived_from'] = [reference(task), reference(run)]
    gate = row('GateDecision', 'gate', {'gate_id': 'gate.unit_integration_execution', 'policy_ref': reference(policy), 'candidate': CANDIDATE, 'required_run_refs': [reference(run)], 'status': 'PASS', 'reasons': ['Synthetic review'], 'review_refs': [reference(review)]})
    release = row('ReleaseDecision', 'release', {'candidate': CANDIDATE, 'required_gate_refs': [reference(gate)], 'decision': 'APPROVE', 'authority_ref': reference(release_grant), 'support_owner': 'operator', 'recovery_distribution_disposition': 'Synthetic rollback and support declaration; no real release'})
    return [policy, requirement, edit, release_grant, task, run, review, gate, release]


class KernelTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        (self.root / 'output.txt').write_bytes(b'expected\n')
        self.records = fixtures()

    def check(self, **kwargs):
        return validate(self.records, project_id='example', candidate=CANDIDATE, artifact_root=self.root, now=NOW, **kwargs)

    def code(self, code, **kwargs):
        result = self.check(**kwargs)
        self.assertIn(code, {f['code'] for f in result['findings']}, result)
        return result

    def rebind(self, old, new):
        """Update exact references downstream after a deliberate fixture mutation."""
        def walk(value):
            if value == old:
                return copy.deepcopy(new)
            if isinstance(value, dict):
                return {k: walk(v) for k, v in value.items()}
            if isinstance(value, list):
                return [walk(v) for v in value]
            return value
        for i, r in enumerate(self.records):
            before = reference(r)
            updated = walk(r)
            if updated != r:
                self.records[i] = updated
                self.rebind(before, reference(updated))

    def mutate(self, kind, **body):
        row = next(r for r in self.records if r['kind'] == kind)
        old = reference(row)
        row['body'].update(body)
        self.rebind(old, reference(row))

    def test_canonical_full_schema(self):
        for record in self.records:
            self.assertEqual(schema_errors(record), [])
        self.assertEqual(self.check(authority_receipt=lambda g: True, run_receipt=lambda r: True, review_receipt=lambda r: True, release_receipt=lambda r: True)['status'], 'PASS')

    def test_external_receipts_are_required(self):
        self.assertEqual(self.code('RUN_RECEIPT')['status'], 'INCOMPLETE')
        self.code('AUTHORITY_RECEIPT')

    def test_reject_duplicate_json_keys_and_nonfinite(self):
        for text in ['{"a":1,"a":2}', '{"value":NaN}', '{"value":Infinity}']:
            with self.subTest(text=text), self.assertRaises(ValueError):
                load_json(text)
        with self.assertRaises(ValueError):
            canonical({'value': float('nan')})

    def test_hashes_ignore_dict_order(self):
        self.assertEqual(digest({'a': 1, 'b': 2}), digest({'b': 2, 'a': 1}))

    def test_old_dialect_rejected(self):
        self.records = [{'type': 'task', 'version': 1}]
        self.code('SCHEMA')

    def test_unknown_kind_version_and_malformed(self):
        for key, value in [('kind', 'Unknown'), ('contract_version', '9.0.0'), ('body', 'bad')]:
            with self.subTest(key=key):
                self.records = fixtures()
                self.records[0][key] = value
                self.code('SCHEMA')

    def test_schema_enforces_execution(self):
        self.mutate('EvidenceRun', executed=False)
        self.code('SCHEMA')

    def test_artifact_bytes_checked(self):
        (self.root / 'output.txt').write_bytes(b'corrupt')
        self.code('ARTIFACT_DIGEST')

    def test_path_traversal_rejected(self):
        self.mutate('EvidenceRun', artifacts=[{'path': '../output.txt', 'sha256': 'a' * 64}])
        self.code('PATH')

    def test_false_artifact_does_not_authorize_release(self):
        (self.root / 'output.txt').unlink()
        self.assertEqual(self.code('ARTIFACT_DIGEST', authority_receipt=lambda g: True, run_receipt=lambda r: True)['status'], 'FAIL')

    def test_dangling_or_hash_mismatched_reference(self):
        self.records[-1]['body']['authority_ref']['sha256'] = '0' * 64
        self.code('REFERENCE')

    def test_wrong_project(self):
        self.records[0]['project_id'] = 'other'
        self.code('PROJECT')

    def test_unknown_fact_value(self):
        f = entity('Fact', 'ua.fact.x', 'example', 'owner', {'predicate': 'network', 'state': 'unknown', 'value': False, 'unit': None, 'origin': 'unknown', 'evidence_refs': []})
        self.records.append(f)
        self.code('UNKNOWN_VALUE')

    def test_overlapping_fact_conflict(self):
        f = entity('Fact', 'ua.fact.one', 'example', 'owner', {'predicate': 'network', 'state': 'true', 'value': None, 'unit': None, 'origin': 'declared', 'evidence_refs': []}, 'component')
        other = copy.deepcopy(f)
        other.update(id='ua.fact.two', scope='component/cli')
        other['body']['state'] = 'false'
        self.records.extend([f, other])
        self.code('FACT_CONFLICT')

    def test_revoked_and_expired_grants(self):
        for change in [{'status': 'REVOKED'}, {'expires_at': '2020-01-01T00:00:00Z'}]:
            with self.subTest(change=change):
                self.records = fixtures()
                self.mutate('Authority', **change)
                self.code('AUTHORITY', authority_receipt=lambda g: True)

    def test_incorrect_grant_principal(self):
        self.mutate('Authority', principal='other')
        self.code('AUTHORITY')

    def test_failed_run_cannot_be_passing_gate(self):
        self.mutate('EvidenceRun', status='FAIL')
        self.code('GATE_RESULT')

    def test_unexecuted_run_cannot_be_passing_gate(self):
        self.mutate('EvidenceRun', status='NOT_RUN', executed=False, started_at=None, ended_at=None, artifacts=[])
        self.code('GATE_RESULT')

    def test_release_requires_same_candidate(self):
        self.mutate('ReleaseDecision', candidate={'identity': 'other', 'sha256': 'c' * 64})
        self.code('RELEASE_GATES')

    def test_hold_is_not_approval(self):
        self.mutate('ReleaseDecision', decision='HOLD')
        # Missing receipt on other executed work still leaves the bundle incomplete.
        self.assertEqual(self.check()['status'], 'INCOMPLETE')

    def test_missing_host_release_review_holds_candidate(self):
        report = self.check(authority_receipt=lambda g: True, run_receipt=lambda r: True)
        self.assertEqual(report['release_disposition'], 'HOLD')
        self.assertIn('RELEASE_REVIEW', {f['code'] for f in report['findings']})

    def test_cli_rejects_old_dialect_and_reports_missing_receipts(self):
        path = self.root / 'records.json'
        path.write_bytes(canonical(self.records))
        completed = subprocess.run([sys.executable, '-m', 'studio_kernel', 'validate', str(path), '--project', 'example', '--artifacts', str(self.root)], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 2, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)['release_disposition'], 'HOLD')
        path.write_text('[{"type":"task"}]', encoding='utf-8')
        completed = subprocess.run([sys.executable, '-m', 'studio_kernel', 'validate', str(path), '--project', 'example'], capture_output=True, text=True)
        self.assertEqual(completed.returncode, 1, completed.stderr)
        self.assertEqual(json.loads(completed.stdout)['findings'][0]['code'], 'SCHEMA')

    def test_unsafe_task_path(self):
        self.mutate('TaskPacket', allowed_paths=['src/../outside'])
        self.code('PATH')

    def test_superseded_requirement_invalidates_downstream(self):
        prior = next(r for r in self.records if r['kind'] == 'Requirement')
        revised = copy.deepcopy(prior)
        revised['revision'] = 2
        revised['body']['outcome'] = 'Changed need'
        self.records.append(revised)
        report = self.code('STALE')
        self.assertIn(digest(self.records[-2]), report['stale_sha256'])

    def test_run_end_before_start(self):
        self.mutate('EvidenceRun', ended_at='2026-10-30T00:00:00Z')
        self.code('RUN_TIME')

    def test_grant_does_not_authorize_other_scope(self):
        self.mutate('Authority', allowed_scope=['component/other'])
        self.code('AUTHORITY')

    def test_gate_review_required(self):
        self.mutate('GateDecision', review_refs=[])
        self.code('GATE_REVIEW')

    def test_five_project_categories_use_same_canonical_envelope(self):
        for label in ['cli', 'library', 'api', 'web', 'pipeline']:
            with self.subTest(label=label):
                record = entity('ProjectProfile', 'ua.profile.' + label, 'example', 'owner', {'goals': ['A bounded ' + label + ' change'], 'users_context': ['Synthetic fixture'], 'non_goals': ['No unrelated work'], 'constraints': [], 'mode': 'greenfield' if label == 'cli' else 'brownfield', 'baseline': 'example-revision', 'component_scopes': ['component/' + label], 'success_criteria': ['Independent expected behavior']})
                self.assertEqual(validate([record], project_id='example')['status'], 'PASS')

    def test_registry_exact_reference_and_invented_id(self):
        from .canonical import ROOT
        corpus = ROOT / 'preserved_freezes/SRS-FREEZE-2026-10-31-v1/tree/current_003R'
        partition = 'dataset/v1/architecture_patterns.jsonl'
        original = json.loads((corpus / partition).read_text(encoding='utf-8').splitlines()[0])
        reg = {'checkpoint_sha256': '5fea1fe5e8f19064df7ee9af4386aeb85046003c99ee83f9b4569432f0992aa8', 'record_id': original['id'], 'record_version': original['version'], 'partition': partition, 'line': 1, 'edge_ids': [], 'source_ids': original['source_ids']}
        fact = entity('Fact', 'ua.fact.selection', 'example', 'owner', {'predicate': 'local_only', 'state': 'true', 'value': None, 'unit': None, 'origin': 'declared', 'evidence_refs': []})
        decision = entity('SelectionDecision', 'ua.selection.example', 'example', 'owner', {'policy_sha256': digest(self.records[0]), 'input_sha256': digest(fact), 'rules_version': 'synthetic-policy-1', 'plan_status': 'COMPLETE', 'choices': [{'target': original['id'], 'status': 'RECOMMENDED', 'obligation': 'optional', 'basis': 'research', 'rule_id': 'example-rule', 'fact_refs': [reference(fact)], 'registry_refs': [reg], 'reasons': ['Synthetic applicability proposal; not autonomous selection'], 'missing': [], 'conflicts': []}]})
        self.records.extend([fact, decision])
        self.assertEqual(self.check(authority_receipt=lambda g: True, run_receipt=lambda r: True, review_receipt=lambda r: True, release_receipt=lambda r: True)['status'], 'PASS')
        decision['body']['choices'][0]['registry_refs'][0]['record_id'] = '003R-DISC-001'
        self.code('REGISTRY')


class HistoryTests(unittest.TestCase):
    def setUp(self):
        self.temp = tempfile.TemporaryDirectory()
        self.addCleanup(self.temp.cleanup)
        self.path = Path(self.temp.name) / 'history.sqlite'
        self.store = Store(self.path, 'example')
        self.records = fixtures()

    def commit(self, batch=None, expected=0, **kwargs):
        return self.store.commit(batch or self.records, expected_revision=expected, candidate=CANDIDATE, actor='operator', reason='Synthetic test import', **kwargs)

    def test_replay_and_reopen(self):
        self.commit()
        restored = Store(self.path, 'example').read()
        self.assertEqual(restored['records'], self.records)
        self.assertEqual(restored['revision'], 1)
        self.assertEqual(schema_errors(self.store.snapshot()), [])
        self.assertEqual(self.store.snapshot()['body']['state_revision'], 1)

    def test_stale_writer_cannot_append(self):
        self.commit()
        with self.assertRaises(HistoryError):
            self.commit()
        self.assertEqual(self.store.read()['revision'], 1)

    def test_transaction_rolls_back_after_failure(self):
        def interrupt():
            raise RuntimeError('simulated interruption before commit')
        with self.assertRaises(RuntimeError):
            self.commit(before_commit=interrupt)
        self.assertEqual(self.store.read()['records'], [])
        self.commit()
        self.assertEqual(self.store.read()['revision'], 1)

    def test_reject_overwrite_and_missing_history(self):
        self.commit()
        with self.assertRaises(HistoryError):
            self.commit([self.records[0]], expected=1)
        row = copy.deepcopy(self.records[0])
        row['revision'] = 3
        with self.assertRaises(HistoryError):
            self.commit([row], expected=1)

    def test_sql_update_delete_blocked(self):
        self.commit()
        for statement in ['UPDATE records SET sha="x"', 'DELETE FROM records', 'DELETE FROM commits']:
            with self.subTest(statement=statement), self.assertRaises(sqlite3.IntegrityError), self.store.connect() as db:
                db.execute(statement)

    def test_wrong_project_reopen(self):
        with self.assertRaises(HistoryError):
            Store(self.path, 'other')

    def test_invalid_record_atomic_rejection(self):
        self.records[-1]['kind'] = 'Invalid'
        with self.assertRaises(HistoryError):
            self.commit()
        self.assertEqual(self.store.read()['revision'], 0)

    def test_changed_input_updates_snapshot(self):
        self.commit()
        record = copy.deepcopy(self.records[0])
        record['revision'] = 2
        record['body']['rationale'] = 'Revised policy'
        self.commit([record], expected=1)
        snapshot = self.store.snapshot()
        self.assertEqual(snapshot['body']['state_revision'], 2)
        self.assertEqual(snapshot['body']['scopes'][0]['status'], 'STALE')
        self.assertTrue(snapshot['body']['blockers'])

    def test_task_expected_revision_checked(self):
        self.records[4]['body']['expected_state_revision'] = 9
        # Downstream digest links are now invalid; both stale input and hash changes reject.
        with self.assertRaises(HistoryError):
            self.commit()

    def test_process_exit_before_commit_recovers_without_partial_history(self):
        script = '''
import os,sys
from studio_kernel.store import Store
from studio_kernel.test_kernel import fixtures,CANDIDATE
Store(sys.argv[1], 'example').commit(fixtures(), expected_revision=0, candidate=CANDIDATE, actor='operator', reason='Crash fixture', before_commit=lambda: os._exit(37))
'''
        completed = subprocess.run([sys.executable, '-c', script, str(self.path)], capture_output=True)
        self.assertEqual(completed.returncode, 37, completed.stderr)
        self.assertEqual(self.store.read()['revision'], 0)
        self.assertEqual(self.store.read()['records'], [])
        self.commit()
        self.assertEqual(self.store.read()['revision'], 1)

    def test_two_writers_only_one_expected_revision_can_commit(self):
        def writer(_):
            try:
                self.commit()
                return 'committed'
            except HistoryError:
                return 'stale'
        with ThreadPoolExecutor(max_workers=2) as executor:
            results = list(executor.map(writer, range(2)))
        self.assertEqual(sorted(results), ['committed', 'stale'])
        self.assertEqual(self.store.read()['revision'], 1)

    def test_corrupt_history_is_detected_on_replay(self):
        self.commit()
        # Model a privileged database editor bypassing append-only API triggers.
        with self.store.connect() as db:
            db.execute('DROP TRIGGER commits_no_update')
            db.execute('UPDATE commits SET sha=?', ('0' * 64,))
        with self.assertRaises(HistoryError):
            self.store.read()


if __name__ == '__main__':
    unittest.main()
