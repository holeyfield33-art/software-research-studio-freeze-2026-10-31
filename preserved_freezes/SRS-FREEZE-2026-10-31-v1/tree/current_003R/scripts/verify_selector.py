#!/usr/bin/env python3
"""Independent 003R verifier; the selector itself never reads oracle files."""
from pathlib import Path
import hashlib
import json
import shutil
import subprocess
import sys
import tempfile
import jsonschema

ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'dataset/v1'
ORACLE = ROOT / 'oracles/frozen-oracle.json'
PY = sys.executable


def readjson(path):
    return json.loads(Path(path).read_text(encoding='utf-8'))


def jsonl(path):
    return [json.loads(line) for line in Path(path).read_text(encoding='utf-8').splitlines() if line.strip()]


def load_data():
    records, sources, edges = {}, {}, []
    for path in DATA.glob('*.jsonl'):
        rows = jsonl(path)
        if path.name == 'relationships.jsonl':
            edges = rows
        elif path.name == 'sources.jsonl':
            sources = {row['id']: row for row in rows}
        else:
            records.update({row['id']: row for row in rows})
    return records, sources, edges


def run_selector(brief, output_dir):
    subprocess.run([
        PY, str(ROOT / 'scripts/select.py'), '--brief', str(brief),
        '--dataset', str(DATA), '--rules', str(ROOT / 'rules/selection-rules.json'),
        '--out', str(output_dir)
    ], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
    return {name: readjson(Path(output_dir) / name) for name in
            ('selection.json', 'rejections.json', 'decision_trace.json')}


def exact_case(name, bundle, expected):
    selection = bundle['selection.json']
    rejection = bundle['rejections.json']
    fields = [
        ('selected_records', [(x['record_id'], x['status'], x['rule_id']) for x in selection['selected_records']],
         [(x['record_id'], x['status'], x['rule_id']) for x in expected['selected_records']]),
        ('rejected_records', [(x['record_id'], x['status'], x['rule_id'], x.get('reason_code')) for x in rejection['rejected_records']],
         [(x['record_id'], x['status'], x['rule_id'], x.get('reason_code')) for x in expected['rejected_records']]),
        ('feature_decisions', [(x['decision_id'], x['status'], x['rule_id'], x.get('reason_code')) for x in rejection['feature_decisions']],
         [(x['decision_id'], x['status'], x['rule_id'], x.get('reason_code')) for x in expected['feature_decisions']]),
        ('authority_decisions', rejection['authority_decisions'], expected['authority_decisions']),
        ('standard_reviews', selection['standard_reviews'], expected['standard_reviews']),
        ('gate_results', selection['gate_results'], expected['gate_results']),
        ('deliverable_roles', [(x['role_id'], x['phase'], x['status']) for x in selection['deliverable_roles']],
         [(x['role_id'], x['phase'], x['status']) for x in expected['deliverable_roles']]),
        ('roadmap_task_ids', [x['task_id'] for x in selection['roadmap_tasks_topological_order']], expected['roadmap_task_ids']),
        ('prompt_record_ids', selection['prompt_contract']['selected_prompt_record_ids'], expected['prompt_record_ids']),
    ]
    errors = []
    for field, actual, wanted in fields:
        if actual != wanted:
            errors.append({'case': name, 'field': field, 'actual': actual, 'expected': wanted})
    return errors


def validate_paths(bundle, brief, records, sources, edges):
    active = {e['id']: e for e in edges if e.get('status') != 'superseded'}
    rules = readjson(ROOT / 'rules/selection-rules.json')
    overrides = rules.get('source_scope_overrides', {})
    errors = []
    types = brief['software_type_ids']
    selection = bundle['selection.json']
    trace = bundle['decision_trace.json']
    trace_by_id = {x['record_id']: x for x in trace['selected_record_trace']}
    for row in selection['selected_records']:
        rid = row['record_id']
        record = records.get(rid)
        if not record:
            errors.append(f'unknown selected record {rid}')
            continue
        if rid not in trace_by_id:
            errors.append(f'missing trace for {rid}')
        if not row['evidence_paths']:
            errors.append(f'no evidence route {rid}')
        for route in row['evidence_paths']:
            type_id = route['software_type_id']
            if type_id not in types and rid != type_id:
                errors.append(f'wrong type route {rid} via {type_id}')
            if rid != type_id:
                edge = active.get(route.get('applicability_relationship_id'))
                if not edge or edge.get('source_endpoint') != type_id or edge.get('target_endpoint') != rid or edge.get('predicate') not in ('applies_to', 'informs', 'exemplified_by', 'verifies', 'supports'):
                    errors.append(f'broken typed applicability edge for {rid}')
                if type_id not in record.get('applicable_software_types', []):
                    errors.append(f'category applicability field mismatch for {rid}')
            for source_path in route.get('sources', []):
                sid = source_path['source_id']
                source = sources.get(sid)
                if not source:
                    errors.append(f'unknown source {sid}')
                    continue
                override = overrides.get(sid)
                if override and type_id not in override.get('allowed_software_type_ids', []):
                    errors.append(f'source scope mismatch {type_id}->{sid}')
                if sid not in record.get('source_ids', []):
                    errors.append(f'source {sid} not declared by {rid}')
                edge = active.get(source_path.get('relationship_id'))
                if not edge or edge.get('source_endpoint') != rid or edge.get('target_endpoint') != sid or edge.get('predicate') != 'supported_by':
                    errors.append(f'broken supported_by edge {rid}->{sid}')
                locator = source.get('claim_locator') or source.get('locator') or source.get('repo_path')
                if locator != source_path.get('claim_locator'):
                    errors.append(f'claim locator mismatch {rid}->{sid}')
                if not source_path.get('source_type'):
                    errors.append(f'missing source type {rid}->{sid}')
    for excluded in trace.get('source_exclusions', []):
        sid = excluded['source_id']
        source = sources.get(sid)
        override = overrides.get(sid)
        if not source or not override:
            errors.append(f'unregistered source exclusion {sid}')
            continue
        if excluded['software_type_id'] in override.get('allowed_software_type_ids', []):
            errors.append(f'allowed source wrongly excluded {sid}')
        if excluded['rule_id'] != override['rule_id'] or excluded['reason_code'] != override['reason_code']:
            errors.append(f'source exclusion rule mismatch {sid}')
        if excluded['claim_locator'] != source.get('claim_locator'):
            errors.append(f'source exclusion locator mismatch {sid}')
    for item in trace['dependency_edges']:
        edge = active.get(item['relationship_id'])
        if not edge or edge.get('source_endpoint') != item['from_record_id'] or edge.get('target_endpoint') != item['to_record_id'] or edge.get('predicate') != item['predicate']:
            errors.append(f'broken dependency edge {item}')
        if item['predicate'] == 'requires' and item['dependency_kind'] != 'hard_prerequisite':
            errors.append(f'requires edge mislabeled {item}')
    for item in trace['related_context_edges']:
        if item['dependency_kind'] != 'related_context_not_prerequisite':
            errors.append(f'related context promoted to dependency {item}')
        if item.get('origin') == 'typed_relationship':
            edge = active.get(item.get('relationship_id'))
            if item.get('predicate') != 'informs' or not edge or edge.get('predicate') != 'informs' or edge.get('source_endpoint') != item['from_record_id'] or edge.get('target_endpoint') != item['related_record_id']:
                errors.append(f'broken typed related-context edge {item}')
            target = records.get(item['related_record_id'], {})
            if item.get('software_type_id') and item['software_type_id'] not in target.get('applicable_software_types', []):
                errors.append(f'related-context type scope mismatch {item}')
            for source_path in item.get('source_paths', []):
                source = sources.get(source_path['source_id'])
                if not source or source_path['source_id'] not in (edge or {}).get('source_ids', []):
                    errors.append(f'broken related-context source path {item}')
                    continue
                locator = source.get('claim_locator') or source.get('locator') or source.get('repo_path')
                if locator != source_path.get('claim_locator'):
                    errors.append(f'related-context locator mismatch {item}')
    tasks = selection['roadmap_tasks_topological_order']
    positions = {task['task_id']: index for index, task in enumerate(tasks)}
    for task in tasks:
        for dep in task.get('depends_on', []):
            if dep in positions and positions[dep] >= positions[task['task_id']]:
                errors.append(f'roadmap dependency order violation {dep}->{task["task_id"]}')
    if selection['roadmap_cycle_nodes']:
        errors.append('roadmap task cycle')
    if any(value == 'PASS' for value in selection['gate_results'].values()):
        errors.append('forbidden PASS gate outcome')
    return errors


def validate_schemas(bundle):
    errors = []
    for name, schema_name in (
        ('selection.json', 'selection-output.schema.json'),
        ('rejections.json', 'rejections-output.schema.json'),
        ('decision_trace.json', 'decision-trace.schema.json'),
    ):
        try:
            schema = readjson(ROOT / 'schemas' / schema_name)
            jsonschema.Draft202012Validator.check_schema(schema)
            jsonschema.Draft202012Validator(schema).validate(bundle[name])
        except Exception as exc:
            errors.append(f'{name}: {getattr(exc, "message", str(exc))}')
    return errors


def validate_rules(bundle):
    rules = readjson(ROOT / 'rules/selection-rules.json')
    rows = rules['rules']
    ids = [row['rule_id'] for row in rows]
    precedence = rules['precedence_high_to_low']
    errors = []
    if len(ids) != len(set(ids)):
        errors.append('duplicate stable rule IDs')
    if set(ids) != set(precedence) or len(ids) != len(precedence):
        errors.append('precedence must contain every stable rule ID exactly once')
    priorities = {row['rule_id']: row['priority'] for row in rows}
    if set(priorities) == set(precedence) and [priorities[rid] for rid in precedence] != sorted(priorities.values(), reverse=True):
        errors.append('precedence order is not descending by priority')
    used = set()
    selection = bundle['selection.json']
    rejection = bundle['rejections.json']
    trace = bundle['decision_trace.json']
    used.update(row['rule_id'] for row in selection['selected_records'])
    used.update(row['rule_id'] for row in rejection['rejected_records'])
    used.update(row['rule_id'] for row in rejection['feature_decisions'])
    used.update(row['rule_id'] for row in rejection['authority_decisions'])
    used.update(row['rule_id'] for row in rejection['unsupported_categories'])
    used.update(row['rule_id'] for row in trace['source_exclusions'])
    used.update(row['rule_id'] for row in selection['standard_reviews'])
    used.update(row['rule_id'] for row in trace['selected_record_trace'])
    if not used.issubset(set(ids)):
        errors.append(f'output references undefined stable rules: {sorted(used - set(ids))}')
    return errors


def oracle_run():
    check = subprocess.run(['sha256sum', '-c', 'oracles/frozen-oracle.sha256'], cwd=ROOT, text=True, capture_output=True)
    if check.returncode:
        raise AssertionError('frozen oracle hash mismatch: ' + check.stderr)
    oracle = readjson(ORACLE)
    expected_cases = oracle['base_and_counterfactual_cases']
    records, sources, edges = load_data()
    input_schema = readjson(ROOT / 'schemas/selector-input.schema.json')
    reports = []
    with tempfile.TemporaryDirectory(prefix='003r-run-') as temp:
        for name, expected in expected_cases.items():
            brief_path = ROOT / expected['case_path']
            brief = readjson(brief_path)
            output = run_selector(brief_path, Path(temp) / name)
            errors = []
            try:
                jsonschema.Draft202012Validator(input_schema).validate(brief)
            except Exception as exc:
                errors.append(f'brief input schema: {getattr(exc, "message", str(exc))}')
            errors += exact_case(name, output, expected)
            errors += validate_schemas(output)
            errors += validate_paths(output, brief, records, sources, edges)
            errors += validate_rules(output)
            reports.append({'case': name, 'status': 'PASS' if not errors else 'FAIL', 'errors': errors})
    return oracle, reports


def cleanroom_check():
    with tempfile.TemporaryDirectory(prefix='003r-cleanroom-') as temp:
        root = Path(temp)
        for name in ('scripts', 'schemas', 'rules', 'inputs', 'dataset/v1'):
            (root / name).mkdir(parents=True, exist_ok=True)
        shutil.copy(ROOT / 'scripts/select.py', root / 'scripts/select.py')
        shutil.copy(ROOT / 'schemas/selector-input.schema.json', root / 'schemas/selector-input.schema.json')
        shutil.copy(ROOT / 'rules/selection-rules.json', root / 'rules/selection-rules.json')
        shutil.copy(ROOT / 'selection_cases/base_ai_agent/brief.json', root / 'inputs/brief.json')
        for path in DATA.glob('*.jsonl'):
            shutil.copy(path, root / 'dataset/v1' / path.name)
        subprocess.run([PY, str(root / 'scripts/select.py'), '--brief', str(root / 'inputs/brief.json'), '--dataset', str(root / 'dataset/v1'), '--rules', str(root / 'rules/selection-rules.json'), '--out', str(root / 'out')], check=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        return 'PASS' if all((root / 'out' / name).exists() for name in ('selection.json', 'rejections.json', 'decision_trace.json')) and not (root / 'oracles').exists() else 'FAIL'


def main():
    oracle, cases = oracle_run()
    failures = [case for case in cases if case['status'] != 'PASS']
    source_errors = []
    for case in oracle['inherited_negative_controls']:
        missing = [sid for sid in case['evidence_source_ids'] if sid not in load_data()[1]]
        if missing:
            source_errors.append({'case_id': case['case_id'], 'missing_sources': missing})
    if len(oracle['inherited_negative_controls']) != 5:
        source_errors.append({'error': 'expected five inherited negative controls'})
    cleanroom = cleanroom_check()
    report = {
        'oracle_cases': len(cases), 'oracle_pass': len(cases) - len(failures), 'oracle_fail': len(failures),
        'case_results': cases,
        'negative_controls': {'count': len(oracle['inherited_negative_controls']), 'status': 'PASS' if not source_errors else 'FAIL', 'errors': source_errors},
        'cleanroom_no_oracle_access': cleanroom,
    }
    output = ROOT / 'reports/selector-verification.json'
    output.parent.mkdir(exist_ok=True)
    output.write_text(json.dumps(report, indent=2, ensure_ascii=False) + '\n')
    print(json.dumps({'oracle_pass': report['oracle_pass'], 'oracle_fail': report['oracle_fail'], 'negative_controls': report['negative_controls']['status'], 'cleanroom': cleanroom, 'report': str(output)}, indent=2))
    return 1 if failures or source_errors or cleanroom != 'PASS' else 0


if __name__ == '__main__':
    sys.exit(main())
