import copy
import json
from pathlib import Path
import subprocess
import sys
import tempfile
import unittest

from .canonical import digest, reference, schema_errors
from .planning import DIMENSIONS, plan
from .store import Store, entity
from .validate import validate


def intake_fixture(category='cli'):
    def row(kind, key, body):
        r = entity(kind, 'ua.intake.' + category + '.' + key, 'example-' + category, 'reviewer', body, 'component/' + category)
        r['created_at'] = '2026-10-31T00:00:00Z'
        return r
    candidate = {'identity': 'synthetic-' + category + '-1', 'sha256': 'b' * 64}
    target = 'practice.test_strategy'
    profile = row('ProjectProfile', 'profile', {'goals': ['Bounded ' + category + ' change'], 'users_context': ['Synthetic development fixture'], 'non_goals': ['No unrelated work'], 'constraints': ['Explicit permissions'], 'mode': 'greenfield' if category == 'cli' else 'brownfield', 'baseline': candidate['identity'], 'component_scopes': ['component/' + category], 'success_criteria': ['Expected behavior and explicit error result']})
    fact = row('Fact', 'fact', {'predicate': 'change_required', 'state': 'true', 'value': None, 'unit': None, 'origin': 'declared', 'evidence_refs': []})
    review = row('DesignDecision', 'review', {'problem': 'Select a proportionate verification strategy', 'alternatives': [{'name': target, 'conditions': ['Bounded behavior change'], 'costs': ['Author behavioral checks'], 'exclusions': []}], 'chosen': target, 'rationale': 'Synthetic recorded human review; not an authenticated approval', 'status': 'ACCEPTED'})
    requirement = row('Requirement', 'requirement', {'outcome': 'The requested change behaves as specified', 'acceptance': ['Valid and invalid inputs match independently authored expectations'], 'priority': 'required', 'acceptance_owner': 'oracle-owner', 'oracle_refs': [reference(review)]})
    return {'intake_version': '0.1.0', 'project_id': profile['project_id'], 'profile_id': profile['id'],
            'created_at': profile['created_at'], 'expected_state_revision': 0, 'candidate': candidate,
            'records': [profile, fact, review, requirement],
            'risk_dimensions': {name: {'state': 'known', 'consequence': 'contained', 'rationale': 'Synthetic local/reversible scope; no actual assessment claimed', 'fact_ids': [fact['id']]} for name in DIMENSIONS},
            'reviews': [{'target': target, 'review_id': review['id'], 'reviewer': 'reviewer', 'fact_ids': [fact['id']], 'status': 'RECOMMENDED', 'obligation': 'mandatory', 'reasons': ['Selected in this synthetic scoped review']}],
            'tasks': [{'key': 'change', 'goal': 'Make the bounded ' + category + ' change', 'owner': 'builder', 'requirement_ids': [requirement['id']], 'oracle_ids': [review['id']], 'paths': [category], 'operations': ['edit', 'test'], 'forbidden_operations': ['deploy'], 'budget': {'seconds': 120, 'attempts': 2, 'tokens': 1000, 'cost_limit': 1, 'currency': 'USD'}, 'depends_on': [], 'grant_ids': [], 'stop_triggers': ['Stop on contradictory facts, unexpected access or failed acceptance']} ]}


class PlanningTests(unittest.TestCase):
    def setUp(self):
        self.intake = intake_fixture()

    def code(self, code):
        output = plan(self.intake)
        self.assertEqual(output['plan_status'], 'INCOMPLETE', output)
        self.assertIn(code, {b['code'] for b in output['blockers']}, output)
        self.assertEqual(output['task_refs'], [])
        self.assertFalse(any(r['kind'] == 'TaskPacket' for r in output['records']))
        return output

    def test_connected_canonical_records_in_five_categories(self):
        for category in ['cli', 'library', 'api', 'web', 'pipeline']:
            with self.subTest(category=category):
                intake = intake_fixture(category)
                output = plan(intake)
                self.assertEqual(output['plan_status'], 'COMPLETE', output['blockers'])
                self.assertEqual(output['execution_authority'], 'UNKNOWN')
                self.assertEqual(output['release_disposition'], 'HOLD')
                self.assertTrue(output['task_refs'])
                for r in output['records']:
                    self.assertEqual(schema_errors(r), [])
                checked = validate(output['records'], project_id=intake['project_id'], candidate=intake['candidate'])
                self.assertEqual(checked['status'], 'INCOMPLETE')
                self.assertEqual({f['code'] for f in checked['findings']}, {'MISSING_GRANT'})

    def test_deterministic_output(self):
        self.assertEqual(plan(self.intake), plan(copy.deepcopy(self.intake)))

    def test_malformed_inputs(self):
        for value in [None, 'facts', [], {}, {'intake_version': '9'}]:
            with self.subTest(value=value):
                self.assertEqual(plan(value)['blockers'][0]['code'], 'INPUT_SCHEMA_INVALID')

    def test_nonfinite_budget(self):
        self.intake['tasks'][0]['budget']['cost_limit'] = float('nan')
        self.code('INPUT_SCHEMA_INVALID')

    def test_unknown_dimension_blocks_tasks(self):
        del self.intake['risk_dimensions']['reversibility']
        output = self.code('RISK_EVIDENCE_MISSING')
        risk = next(r for r in output['records'] if r['kind'] == 'RiskAssessment')
        self.assertIn('reversibility', risk['body']['unresolved'])

    def test_known_risk_requires_fact_support(self):
        self.intake['risk_dimensions']['severity']['fact_ids'] = []
        self.code('RISK_EVIDENCE_MISSING')

    def test_each_risk_floor_and_critical_stop(self):
        for value, tier in [('contained', 'T0'), ('ordinary', 'T1'), ('consequential', 'T2'), ('critical', 'T3')]:
            with self.subTest(value=value):
                self.intake['risk_dimensions']['severity']['consequence'] = value
                output = plan(self.intake)
                risk = next(r for r in output['records'] if r['kind'] == 'RiskAssessment')
                self.assertEqual(risk['body']['tier'], tier)
                self.assertEqual(output['plan_status'], 'INCOMPLETE' if tier == 'T3' else 'COMPLETE')
                if tier == 'T3':
                    self.assertEqual(output['task_refs'], [])

    def test_unknown_fact_does_not_become_false(self):
        self.intake['records'][1]['body']['state'] = 'unknown'
        self.code('RISK_EVIDENCE_MISSING')

    def test_conflicting_fact_is_reported(self):
        other = copy.deepcopy(self.intake['records'][1])
        other['id'] += '.opposite'
        other['body']['state'] = 'false'
        self.intake['records'].append(other)
        self.code('FACT_CONFLICT')

    def test_unreviewed_choice_blocks(self):
        self.intake['reviews'][0]['reviewer'] = 'unrelated-person'
        self.code('REVIEW_INCOMPLETE')

    def test_review_for_different_target_does_not_count(self):
        self.intake['reviews'][0]['target'] = 'arch.event_queue'
        self.code('REVIEW_INCOMPLETE')

    def test_duplicate_target_does_not_last_write_win(self):
        other = copy.deepcopy(self.intake['reviews'][0])
        other['status'] = 'INAPPLICABLE'
        other['obligation'] = 'omitted'
        self.intake['reviews'].append(other)
        self.code('REVIEW_CONFLICT')

    def test_invented_frozen_identifier(self):
        self.intake['reviews'][0]['target'] = '003R-DISC-001'
        self.code('RESEARCH_TARGET')

    def test_missing_task_requirement(self):
        self.intake['tasks'][0]['requirement_ids'] = ['ua.unknown']
        self.code('INPUT_REFERENCE')

    def test_unknown_dependency(self):
        self.intake['tasks'][0]['depends_on'] = ['missing-task']
        self.code('TASK_DEPENDENCY')

    def test_task_cycle(self):
        self.intake['tasks'][0]['depends_on'] = ['change']
        self.code('TASK_CYCLE')

    def test_unsafe_path(self):
        self.intake['tasks'][0]['paths'] = ['../outside']
        self.code('TASK_PATH')

    def test_topological_order_and_requirement_links(self):
        initial = copy.deepcopy(self.intake['tasks'][0])
        initial['key'] = 'prepare'
        self.intake['tasks'][0]['depends_on'] = ['prepare']
        self.intake['tasks'].append(initial)
        output = plan(self.intake)
        self.assertEqual(output['plan_status'], 'COMPLETE')
        tasks = [r for r in output['records'] if r['kind'] == 'TaskPacket']
        self.assertTrue(tasks[0]['id'].endswith('.prepare'))
        self.assertEqual(tasks[1]['body']['dependencies'][0]['task'], reference(tasks[0]))

    def test_required_outcome_cannot_be_silently_omitted(self):
        other = copy.deepcopy(self.intake['records'][-1])
        other['id'] += '.uncovered'
        self.intake['records'].append(other)
        self.code('REQUIREMENT_UNPLANNED')

    def test_plans_persist_and_replay(self):
        output = plan(self.intake)
        with tempfile.TemporaryDirectory() as temp:
            store = Store(Path(temp) / 'history.sqlite', self.intake['project_id'])
            store.commit(output['records'], expected_revision=0, candidate=self.intake['candidate'], actor='operator', reason='Record synthetic reviewed plan')
            self.assertEqual(store.read()['records'], output['records'])
            self.assertEqual(store.snapshot()['body']['state_revision'], 1)

    def test_original_input_records_are_unchanged(self):
        before = copy.deepcopy(self.intake)
        plan(self.intake)
        self.assertEqual(self.intake, before)

    def test_cli_plan_then_persist_then_replay(self):
        with tempfile.TemporaryDirectory() as temp:
            root = Path(temp)
            intake = root / 'intake.json'
            intake.write_text(json.dumps(self.intake), encoding='utf-8')
            candidate = root / 'candidate.json'
            candidate.write_text(json.dumps(self.intake['candidate']), encoding='utf-8')
            completed = subprocess.run([sys.executable, '-m', 'studio_kernel', 'plan', str(intake), '--output', str(root / 'plan')], capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            completed = subprocess.run([sys.executable, '-m', 'studio_kernel', 'record', str(root / 'plan/records.json'), '--project', self.intake['project_id'], '--store', str(root / 'history.sqlite'), '--expected', '0', '--candidate', str(candidate), '--actor', 'operator', '--reason', 'Synthetic connected CLI test'], capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            completed = subprocess.run([sys.executable, '-m', 'studio_kernel', 'status', '--project', self.intake['project_id'], '--store', str(root / 'history.sqlite')], capture_output=True, text=True)
            self.assertEqual(completed.returncode, 0, completed.stdout + completed.stderr)
            status = json.loads(completed.stdout)
            self.assertEqual(status['snapshot']['body']['state_revision'], 1)
            self.assertEqual(status['validation']['status'], 'INCOMPLETE')

    def test_missing_reason_removed_after_resolution(self):
        self.intake['records'][1]['body']['state'] = 'unknown'
        self.assertEqual(plan(self.intake)['plan_status'], 'INCOMPLETE')
        self.intake['records'][1]['body']['state'] = 'true'
        output = plan(self.intake)
        self.assertEqual(output['plan_status'], 'COMPLETE')
        selection = next(r for r in output['records'] if r['kind'] == 'SelectionDecision')
        self.assertEqual(selection['body']['choices'][0]['missing'], [])
        self.assertFalse(any(reason.startswith('Missing: ') for reason in selection['body']['choices'][0]['reasons']))

    def test_unrelated_fact_does_not_change_selection_or_tasks(self):
        initial = plan(self.intake)
        extra = copy.deepcopy(self.intake['records'][1])
        extra['id'] += '.unrelated'
        extra['body']['predicate'] = 'unrelated_observation'
        extra['body']['state'] = 'false'
        self.intake['records'].append(extra)
        output = plan(self.intake)
        self.assertEqual(output['plan_status'], 'COMPLETE')
        old = next(r for r in initial['records'] if r['kind'] == 'SelectionDecision')
        new = next(r for r in output['records'] if r['kind'] == 'SelectionDecision')
        # The overall input digest changes, but choices and task objectives do not.
        self.assertEqual(old['body']['choices'], new['body']['choices'])
        self.assertEqual([r['body']['goal'] for r in initial['records'] if r['kind'] == 'TaskPacket'], [r['body']['goal'] for r in output['records'] if r['kind'] == 'TaskPacket'])

    def test_contradictory_operations_never_emit_packet(self):
        self.intake['tasks'][0]['forbidden_operations'] = ['edit']
        self.code('TASK_OPERATIONS')


if __name__ == '__main__':
    unittest.main()
