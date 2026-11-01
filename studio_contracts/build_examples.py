"""Generate explicitly synthetic format examples across five software categories."""
from pathlib import Path
import json
from .validate import BASELINE, frozen_registry

HERE = Path(__file__).with_name('examples')


def example(name, category, stage, need, acceptance, scope):
    project = 'example-' + name
    def ref(key):
        return {'id': project + ':' + key, 'version': 1}
    def row(key, kind, data, depends=()):
        return {'id': project + ':' + key, 'version': 1, 'project_id': project,
                'created_by': 'fixture-author', 'provenance': 'Synthetic example; no real execution or authority claimed',
                'status': 'planned' if kind == 'task' else 'current', 'supersedes': None,
                'depends_on': [ref(k) for k in depends], 'type': kind, 'data': data}
    registry = frozen_registry()
    records = [
        row('fact', 'fact', {'subject': 'requested-behavior', 'scope': scope, 'value': need, 'knowledge': 'known', 'revision': 'example-revision-1'}),
        row('requirement', 'requirement', {'need': need, 'acceptance': acceptance, 'owner': 'example-owner', 'oracle': 'Independently specified expected result for supplied valid and invalid inputs'}),
        row('decision', 'decision', {'facts': [ref('fact')], 'outcome': 'selected', 'rationale': 'This bounded increment requires explicit acceptance and test planning', 'predicate_version': 'manual-example-1', 'research': [{'id': 'practice.test_strategy', 'checkpoint': BASELINE, 'partition_sha256': registry['practice.test_strategy']}]}, ['requirement']),
        row('task', 'task', {'objective': need, 'requirements': [ref('requirement')], 'prerequisites': [], 'actions': ['read', 'edit', 'test'], 'paths': [scope], 'grant': 'example-grant', 'budget_steps': 20, 'stop_conditions': ['Stop on unexpected access requirement or contradictory facts'], 'candidate_revision': 'example-revision-1', 'acceptance_gate': ref('gate')}, ['decision']),
        row('evidence', 'evidence', {'requirements': [ref('requirement')], 'property': acceptance, 'method': 'Synthetic placeholder; actual commands and captured outputs required during real work', 'candidate_revision': 'example-revision-1', 'result': 'NOT_RUN', 'origin': 'proposed', 'environment': 'example environment, not executed', 'input_sha256': '0' * 64, 'output_sha256': '0' * 64, 'reviewer': 'fixture-author'}),
        row('gate', 'gate', {'requirements': [ref('requirement')], 'evidence': [ref('evidence')], 'result': 'NOT_RUN', 'rationale': 'No implementation or behavioral execution claimed', 'reviewer': 'fixture-author'}),
    ]
    return {'contract_version': '0.1.0', 'project': {'id': project, 'categories': [category], 'entry_stage': stage, 'candidate_revision': 'example-revision-1', 'outcomes': [need], 'non_goals': ['No platform-wide refactor or unrelated feature'], 'owners': ['example-owner']}, 'records': records, 'events': []}


def build():
    HERE.mkdir(exist_ok=True)
    cases = [
        ('new-cli', 'software_type.cli_tools', 'sdlc.discovery_scope', 'Produce deterministic transformed output from a local input file', 'Known inputs produce expected output; malformed input produces a documented error and exit status', 'cli'),
        ('library-change', 'software_type.libraries', 'sdlc.requirements_risk', 'Extend an existing public function without breaking supported callers', 'Existing callers retain behavior; new input and unsupported input cases match the interface contract', 'library'),
        ('api-change', 'software_type.apis', 'sdlc.architecture_design', 'Restrict access to a private operation by verified identity', 'Authorized identity succeeds; unauthorized and missing identity are denied', 'api'),
        ('ui-correction', 'software_type.web_applications', 'sdlc.verification', 'Preserve the latest user edit when responses arrive out of order', 'A deliberately reordered response cannot replace a newer edit; keyboard interaction remains usable', 'ui'),
        ('pipeline-recovery', 'software_type.data_pipelines', 'sdlc.maintenance_feedback', 'Recover an interrupted batch without silently duplicating committed records', 'Retry after an injected interruption produces expected records and surfaces invalid input', 'pipeline'),
    ]
    grants = {}
    for name, category, stage, need, acceptance, scope in cases:
        packet = example(name, category, stage, need, acceptance, scope)
        (HERE / (name + '.json')).write_text(json.dumps(packet, indent=2) + '\n', encoding='utf-8')
        grants[name] = {'example-grant': {'project_id': packet['project']['id'], 'actions': ['read', 'edit', 'test'], 'paths': [scope], 'max_steps': 20}}
        (HERE / (name + '.grants.json')).write_text(json.dumps(grants[name], indent=2) + '\n', encoding='utf-8')


if __name__ == '__main__':
    build()
