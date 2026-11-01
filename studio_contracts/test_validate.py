import copy
import json
from pathlib import Path
import unittest

from .validate import validate


class ContractTests(unittest.TestCase):
    def setUp(self):
        base = Path(__file__).with_name('examples')
        self.packet = json.loads((base / 'new-cli.json').read_text(encoding='utf-8'))
        self.grants = json.loads((base / 'new-cli.grants.json').read_text(encoding='utf-8'))

    def row(self, kind):
        return next(r for r in self.packet['records'] if r['type'] == kind)

    def assert_code(self, code, grants=True):
        report = validate(self.packet, self.grants if grants else None)
        self.assertEqual(report['status'], 'FAIL', report)
        self.assertIn(code, {f['code'] for f in report['findings']}, report)
        return report

    def complete(self):
        task = self.row('task')
        task['status'] = 'complete'
        task_ref = {'id': task['id'], 'version': 1}
        states = ['planned', 'ready', 'running', 'review', 'complete']
        self.packet['events'] = [{'task': task_ref, 'from': a, 'to': b, 'reason': 'Synthetic test transition'} for a, b in zip(states, states[1:])]
        ev = self.row('evidence')['data']
        ev.update(result='PASS', origin='reviewed')
        self.row('gate')['data']['result'] = 'PASS'
        attempt = copy.deepcopy(self.row('fact'))
        attempt.update(id=self.packet['project']['id'] + ':attempt', type='attempt', data={'task': task_ref, 'outcome': 'succeeded', 'actions': ['read', 'edit', 'test'], 'paths': ['cli'], 'steps_used': 10, 'candidate_revision': 'example-revision-1', 'actor': 'synthetic-test', 'tool_version': 'example-1', 'detail': 'Synthetic test fixture, not real execution'})
        self.packet['records'].append(attempt)

    def test_all_categories_accept_unexecuted_packets(self):
        base = Path(__file__).with_name('examples')
        for p in base.glob('*.json'):
            if p.name.endswith('.grants.json'):
                continue
            with self.subTest(category=p.name):
                packet = json.loads(p.read_text(encoding='utf-8'))
                grants = json.loads(p.with_suffix('.grants.json').read_text(encoding='utf-8'))
                self.assertEqual(validate(packet, grants)['status'], 'PASS')

    def test_valid_completion(self):
        self.complete()
        self.assertEqual(validate(self.packet, self.grants)['status'], 'PASS')

    def test_malformed_packet_values(self):
        for value in [None, [], 'packet', 7, {'contract_version': '0.1.0'}]:
            with self.subTest(value=value):
                self.assertEqual(validate(value)['status'], 'FAIL')

    def test_malformed_records(self):
        for field, value in [('data', []), ('type', []), ('id', {}), ('version', True), ('depends_on', 'bad')]:
            with self.subTest(field=field):
                p = copy.deepcopy(self.packet)
                p['records'][0][field] = value
                self.assertEqual(validate(p, self.grants)['status'], 'FAIL')

    def test_unknown_fields_rejected(self):
        self.row('fact')['data']['permissions'] = ['all']
        self.assert_code('DATA_SHAPE')

    def test_dangling_reference(self):
        self.row('decision')['data']['facts'][0]['id'] += '-missing'
        self.assert_code('REFERENCE')

    def test_unknown_fact_not_false(self):
        self.row('fact')['data'].update(knowledge='unknown', value=False)
        self.assert_code('UNKNOWN_VALUE')

    def test_unsettled_fact_cannot_support_decision(self):
        for state in ['unknown', 'conflicting']:
            with self.subTest(state=state):
                self.row('fact')['data'].update(knowledge=state, value=None)
                self.assert_code('UNCERTAIN_DECISION')

    def test_contradictory_known_facts(self):
        fact = copy.deepcopy(self.row('fact'))
        fact['id'] += '-contradiction'
        fact['data']['value'] = 'incompatible observation'
        self.packet['records'].append(fact)
        self.assert_code('FACT_CONFLICT')

    def test_invented_research_identifier(self):
        self.row('decision')['data']['research'][0]['id'] = '003R-DISC-001'
        self.assert_code('RESEARCH_REFERENCE')

    def test_research_digest_mismatch(self):
        self.row('decision')['data']['research'][0]['partition_sha256'] = '0' * 64
        self.assert_code('RESEARCH_REFERENCE')

    def test_no_grant_means_no_authority(self):
        self.assert_code('AUTHORITY', grants=False)

    def test_task_exceeds_grant(self):
        self.row('task')['data']['actions'].append('deploy')
        self.assert_code('AUTHORITY')

    def test_path_prefix_does_not_escape_grant(self):
        self.row('task')['data']['paths'] = ['cli-elsewhere']
        self.assert_code('AUTHORITY')

    def test_unsafe_paths(self):
        for path in ['../secret', '/root', 'C:/secret', 'cli/../secret', 'cli\\secret', 'cli/*']:
            with self.subTest(path=path):
                self.row('task')['data']['paths'] = [path]
                self.assert_code('PATH')

    def test_budget_overrun(self):
        self.complete()
        self.row('attempt')['data']['steps_used'] = 21
        self.assert_code('ATTEMPT_SCOPE')

    def test_false_evidence(self):
        self.row('evidence')['data']['result'] = 'PASS'
        self.assert_code('FALSE_EVIDENCE')

    def test_gate_cannot_pass_not_run(self):
        self.row('gate')['data']['result'] = 'PASS'
        self.assert_code('GATE_EVIDENCE')

    def test_gate_cannot_waive_required_work(self):
        self.row('gate')['data']['result'] = 'NOT_APPLICABLE'
        self.assert_code('GATE_APPLICABILITY')

    def test_stale_candidate(self):
        self.packet['project']['candidate_revision'] = 'example-revision-2'
        report = self.assert_code('STALE')
        self.assertTrue(any(':gate@1' in key for key in report['stale_records']))

    def test_transitive_input_invalidation(self):
        fact = self.row('fact')
        new = copy.deepcopy(fact)
        new.update(version=2, supersedes={'id': fact['id'], 'version': 1})
        new['data']['value'] = 'Changed project need'
        fact['status'] = 'superseded'
        self.packet['records'].append(new)
        report = self.assert_code('STALE')
        self.assertIn(self.row('task')['id'] + '@1', report['stale_records'])

    def test_dependency_cycle(self):
        fact = self.row('fact')
        decision = self.row('decision')
        fact['depends_on'] = [{'id': decision['id'], 'version': 1}]
        self.assert_code('DEPENDENCY_CYCLE')

    def test_skipped_transition(self):
        self.complete()
        self.packet['events'] = [self.packet['events'][-1]]
        self.assert_code('TRANSITION')

    def test_completion_needs_attempt(self):
        self.complete()
        self.packet['records'] = [r for r in self.packet['records'] if r['type'] != 'attempt']
        self.assert_code('ATTEMPT_REQUIRED')

    def test_completion_needs_gate(self):
        self.complete()
        self.row('gate')['data']['result'] = 'FAIL'
        self.assert_code('COMPLETION_GATE')

    def test_interrupted_attempt_does_not_complete_task(self):
        self.complete()
        self.row('attempt')['data']['outcome'] = 'interrupted'
        self.assert_code('ATTEMPT_REQUIRED')

    def test_malformed_event(self):
        self.packet['events'] = ['not an event']
        self.assert_code('EVENT_SHAPE')

    def finding(self):
        row = copy.deepcopy(self.row('fact'))
        row.update(id=self.packet['project']['id'] + ':finding', type='finding', data={'requirements': [{'id': self.row('requirement')['id'], 'version': 1}], 'severity': 'high', 'disposition': 'open', 'scope': 'cli', 'candidate_revision': 'example-revision-1', 'detail': 'Synthetic incorrect result', 'remediation': 'Correct the failing property', 'resolution_evidence': []})
        self.packet['records'].append(row)
        return row

    def test_open_finding_blocks_pass(self):
        self.complete()
        self.finding()
        self.assert_code('OPEN_FINDING')

    def test_resolution_needs_evidence(self):
        self.finding()['data']['disposition'] = 'resolved'
        self.assert_code('FINDING_RESOLUTION')

    def test_resolved_finding_with_evidence(self):
        self.complete()
        finding = self.finding()
        finding['data'].update(disposition='resolved', resolution_evidence=[{'id': self.row('evidence')['id'], 'version': 1}])
        self.assertEqual(validate(self.packet, self.grants)['status'], 'PASS')

    def test_revised_task_retains_history(self):
        task = self.row('task')
        revised = copy.deepcopy(task)
        revised.update(version=2, supersedes={'id': task['id'], 'version': 1})
        task['status'] = 'superseded'
        self.packet['records'].append(revised)
        self.assertEqual(validate(self.packet, self.grants)['status'], 'PASS')

    def test_block_resume_preserves_interrupted_attempt(self):
        self.complete()
        task = self.row('task')
        interrupted = copy.deepcopy(self.row('attempt'))
        interrupted['id'] += '-earlier'
        interrupted['data']['outcome'] = 'interrupted'
        self.packet['records'].append(interrupted)
        states = ['planned', 'ready', 'running', 'blocked', 'ready', 'running', 'review', 'complete']
        self.packet['events'] = [{'task': {'id': task['id'], 'version': 1}, 'from': a, 'to': b, 'reason': 'Recorded interruption and retry'} for a, b in zip(states, states[1:])]
        self.assertEqual(validate(self.packet, self.grants)['status'], 'PASS')

    def test_superseded_acceptance_gate(self):
        self.complete()
        self.row('gate')['status'] = 'superseded'
        self.assert_code('COMPLETION_GATE')

    def test_type_cannot_change_under_same_id(self):
        old = self.row('fact')
        new = copy.deepcopy(self.row('requirement'))
        new.update(id=old['id'], version=2, supersedes={'id': old['id'], 'version': 1})
        old['status'] = 'superseded'
        self.packet['records'].append(new)
        self.assert_code('IDENTITY_TYPE')

    def test_artifact_outside_producer_scope(self):
        artifact = copy.deepcopy(self.row('fact'))
        artifact.update(id=self.packet['project']['id'] + ':artifact', type='artifact', data={'path': 'elsewhere/result.txt', 'sha256': '0' * 64, 'revision': 'example-revision-1', 'requirements': [{'id': self.row('requirement')['id'], 'version': 1}], 'producer': {'id': self.row('task')['id'], 'version': 1}})
        self.packet['records'].append(artifact)
        self.assert_code('ARTIFACT_SCOPE')


if __name__ == '__main__':
    unittest.main()
