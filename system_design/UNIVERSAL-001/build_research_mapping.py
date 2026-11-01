"""Build/check exact local research provenance; does not validate product behavior."""
from pathlib import Path
import hashlib
import json
import sys

HERE = Path(__file__).resolve().parent
ROOT = HERE.parents[1]
DATA = ROOT / 'preserved_freezes/SRS-FREEZE-2026-10-31-v1/tree/current_003R/dataset/v1'


def build():
    registry = {}
    locations = {}
    partitions = []
    for path in sorted(DATA.glob('*.jsonl')):
        data = path.read_bytes()
        partitions.append({'path': path.relative_to(ROOT).as_posix(), 'sha256': hashlib.sha256(data).hexdigest()})
        for line, text in enumerate(data.decode('utf-8').splitlines(), 1):
            if text.strip():
                record = json.loads(text)
                assert record['id'] not in registry
                registry[record['id']] = record
                locations[record['id']] = {'path': path.relative_to(ROOT).as_posix(), 'line': line}
    groups = {
        'project_understanding': ['sdlc.discovery_scope', 'sdlc.requirements_risk', 'practice.requirements_traceability'],
        'applicability_and_design': ['arch.minimal_viable_structure', 'arch.layered_modular', 'arch.client_server_api_boundary', 'arch.event_queue', 'arch.multitenancy_isolation', 'arch.agent_tool_boundary', 'roadmap.risk_first_poc'],
        'planning': ['roadmap.smallest_releasable_increment', 'roadmap.dependency_aware_sequence', 'practice.test_strategy'],
        'execution': ['prompt.implement_scoped_task', 'prompt.add_test', 'prompt.review_change', 'prompt.threat_model', 'prompt.investigate_failure', 'prompt.prepare_release', 'practice.version_control_review', 'practice.dependency_secret_handling'],
        'verification_release_feedback': ['gate.requirements_acceptance', 'gate.security_risk_review', 'gate.unit_integration_execution', 'gate.dependency_provenance', 'gate.release_readiness', 'gate.operational_rollback', 'practice.ci_reproducible_release', 'practice.observability_incident', 'practice.change_maintenance'],
    }
    groups['lifecycle'] = sorted(k for k in registry if k.startswith('sdlc.'))
    groups['software_categories'] = sorted(k for k in registry if k.startswith('software_type.'))
    groups['illustrative_references'] = sorted(k for k in registry if k.startswith('reference.'))
    selected = sorted({k for values in groups.values() for k in values})
    records = []
    for key in selected:
        r = registry[key]
        for source in r.get('source_ids', []):
            assert source in registry, source
        records.append({'id': key, **locations[key], 'name': r.get('name'),
                        'source_ids': r.get('source_ids', []), 'limitations': r.get('limitations'),
                        'classification': 'Inherited research; module assignment is UNIVERSAL-001 design synthesis'})
    edges = []
    for key, r in registry.items():
        if r.get('source_endpoint') in selected and r.get('target_endpoint') in selected:
            for source in r.get('source_ids', []):
                assert source in registry
            edges.append({'id': key, **locations[key], 'source_endpoint': r['source_endpoint'],
                          'target_endpoint': r['target_endpoint'], 'predicate': r['predicate'],
                          'scope_qualifier': r.get('scope_qualifier'), 'status': r.get('status', 'not explicitly specified'),
                          'source_ids': r.get('source_ids', [])})
    return {'design_id': 'UNIVERSAL-001', 'baseline': 'STUDIO-KNOWLEDGE-003R',
            'status': 'Proposed architecture, not implemented or behaviorally validated',
            'mapping_scope': 'Exact local IDs and inherited sources; not independent external-source verification or exhaustive research coverage',
            'baseline_partitions': partitions, 'groups': groups, 'records': records,
            'relationships_between_selected_records': edges,
            'relationship_policy': 'Preserve qualification and status; edges indicate related evidence, not automatic applicability or permission'}


if __name__ == '__main__':
    rendered = json.dumps(build(), indent=2, ensure_ascii=True) + '\n'
    path = HERE / 'RESEARCH_MAPPING.json'
    if '--check' in sys.argv:
        assert path.read_text(encoding='utf-8') == rendered, 'Mapping differs from preserved records'
        print('PASS: exact frozen IDs, source references, relationship metadata and partition digests')
    else:
        path.write_text(rendered, encoding='utf-8')
        print('Built RESEARCH_MAPPING.json')
