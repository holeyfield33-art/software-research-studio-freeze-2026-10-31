"""Validate a project packet without executing commands or trusting its claims.

python -m studio_contracts.validate packet.json [--grants grants.json]
The contract is a small explicit format, not JSON Schema support.
"""
from pathlib import Path, PurePosixPath
import argparse
import hashlib
import json
import re

SPEC = json.loads(Path(__file__).with_name('contract.json').read_text(encoding='utf-8'))
ROOT = Path(__file__).resolve().parents[1]
DATA = ROOT / 'preserved_freezes/SRS-FREEZE-2026-10-31-v1/tree/current_003R/dataset/v1'
BASELINE = 'STUDIO-KNOWLEDGE-003R'
DIGEST = re.compile(r'^[0-9a-f]{64}$')


def frozen_registry():
    registry = {}
    for path in DATA.glob('*.jsonl'):
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        for line in path.read_text(encoding='utf-8').splitlines():
            if line.strip():
                record = json.loads(line)
                registry[record['id']] = digest
    return registry


def safe_path(value):
    return isinstance(value, str) and bool(value) and value != '.' and not PurePosixPath(value).is_absolute() and not any(p in ('', '..', '.') for p in value.split('/')) and not any(c in value for c in '\\:*?\x00') and not value.endswith('/')


def under(path, roots):
    return any(path == root or path.startswith(root + '/') for root in roots)


def valid_ref(value):
    return isinstance(value, dict) and set(value) == {'id', 'version'} and isinstance(value['id'], str) and type(value['version']) is int and value['version'] > 0


def matches(value, rule):
    if isinstance(rule, list):
        return value in rule
    if rule == 'any':
        return True
    if rule == 'text':
        return isinstance(value, str) and bool(value.strip())
    if rule == 'texts':
        return isinstance(value, list) and bool(value) and all(matches(v, 'text') for v in value)
    if rule == 'positive_integer':
        return type(value) is int and value > 0
    if rule == 'nonnegative_integer':
        return type(value) is int and value >= 0
    if rule == 'digest':
        return isinstance(value, str) and DIGEST.fullmatch(value) is not None
    if rule == 'ref':
        return valid_ref(value)
    if rule == 'refs':
        return isinstance(value, list) and all(valid_ref(v) for v in value)
    if rule == 'research_refs':
        return isinstance(value, list) and all(isinstance(v, dict) and set(v) == {'id', 'checkpoint', 'partition_sha256'} and all(matches(v[k], 'text') for k in v) for v in value)
    return False


def validate(packet, grants=None):
    """Return findings and transitive stale records. Grants are external input."""
    findings = []
    def error(code, record, message):
        findings.append({'code': code, 'record': record, 'message': message})
    def result(stale=()):
        return {'status': 'FAIL' if findings else 'PASS', 'findings': findings,
                'stale_records': sorted(stale), 'scope': 'Contract consistency only; no behavioral or authority authenticity verification'}
    required_top = {'contract_version', 'project', 'records', 'events'}
    if not isinstance(packet, dict) or set(packet) != required_top:
        error('PACKET_SHAPE', 'packet', 'Expected exactly contract_version, project, records, events')
        return result()
    if packet['contract_version'] != SPEC['contract_version']:
        error('VERSION', 'packet', 'Unsupported contract version')
    project = packet['project']
    fields = {'id', 'categories', 'entry_stage', 'candidate_revision', 'outcomes', 'non_goals', 'owners'}
    if not isinstance(project, dict) or set(project) != fields or not all(matches(project[k], 'texts' if k in {'categories', 'outcomes', 'non_goals', 'owners'} else 'text') for k in fields):
        error('PROJECT_SHAPE', 'project', 'Invalid project profile')
        return result()
    registry = frozen_registry()
    if not registry:
        error('REGISTRY_UNAVAILABLE', 'project', 'Frozen registry unavailable')
    for category in project['categories']:
        if not category.startswith('software_type.') or category not in registry:
            error('UNSUPPORTED_CATEGORY', 'project', category)
    if not project['entry_stage'].startswith('sdlc.') or project['entry_stage'] not in registry:
        error('STAGE', 'project', 'Unknown entry concern')
    if not isinstance(packet['records'], list) or not isinstance(packet['events'], list):
        error('COLLECTION_SHAPE', 'packet', 'records and events must be arrays')
        return result()
    common = {'id', 'version', 'project_id', 'created_by', 'provenance', 'status', 'supersedes', 'depends_on', 'type', 'data'}
    records = {}
    ids = {}
    for row in packet['records']:
        if not isinstance(row, dict) or set(row) != common:
            error('RECORD_SHAPE', 'record', 'Unexpected or missing common fields')
            continue
        label = row['id'] if isinstance(row['id'], str) else 'record'
        if not isinstance(row['id'], str) or not row['id'].startswith(project['id'] + ':') or type(row['version']) is not int or row['version'] < 1:
            error('IDENTITY', label, 'IDs require project namespace and positive integer version')
            continue
        if row['project_id'] != project['id'] or not all(matches(row[k], 'text') for k in ('created_by', 'provenance', 'status')) or not matches(row['depends_on'], 'refs') or not (row['supersedes'] is None or valid_ref(row['supersedes'])):
            error('COMMON_FIELDS', label, 'Invalid provenance, dependencies or project identity')
            continue
        kind = row['type']
        if not isinstance(kind, str) or kind not in SPEC['record_types']:
            error('RECORD_TYPE', label, 'Unsupported record type')
            continue
        rules = SPEC['record_types'][kind]
        if not isinstance(row['data'], dict) or set(row['data']) != set(rules) or not all(matches(row['data'].get(k), rule) for k, rule in rules.items()):
            error('DATA_SHAPE', label, 'Invalid typed data fields')
            continue
        if row['status'] not in (tuple(SPEC['task_transitions']) + ('superseded',) if kind == 'task' else ('current', 'superseded')):
            error('STATUS', label, 'Invalid status for record type')
        key = (row['id'], row['version'])
        if key in records:
            error('DUPLICATE', label, 'Duplicate identity and version')
        records[key] = row
        ids.setdefault(row['id'], []).append(row)
    if findings:
        return result()
    latest = {key: max(rows, key=lambda r: r['version']) for key, rows in ids.items()}
    known_facts = {}
    for row in latest.values():
        if row['type'] == 'fact' and row['status'] == 'current' and row['data']['knowledge'] == 'known':
            data = row['data']
            subject = (data['subject'], data['scope'], data['revision'])
            value = json.dumps(data['value'], sort_keys=True)
            if subject in known_facts and known_facts[subject] != value:
                error('FACT_CONFLICT', row['id'], 'Contradictory current facts must be marked conflicting')
            known_facts[subject] = value
    def resolve(ref, label, expected=None):
        row = records.get((ref['id'], ref['version']))
        if row is None or (expected and row['type'] != expected):
            error('REFERENCE', label, 'Missing or incorrectly typed reference: ' + ref['id'])
            return None
        return row
    stale = set()
    dependencies = {}
    for key, row in records.items():
        label, version = key
        prior = row['supersedes']
        versions = sorted(r['version'] for r in ids[label])
        if versions != list(range(1, max(versions) + 1)):
            error('VERSION_CHAIN', label, 'Retain complete version history')
        if len({r['type'] for r in ids[label]}) != 1:
            error('IDENTITY_TYPE', label, 'Record type cannot change across versions')
        if version == 1 and prior is not None or version > 1 and prior != {'id': label, 'version': version - 1}:
            error('SUPERSESSION', label, 'Version must supersede the preceding version of the same ID')
        if row != latest[label] and row['status'] != 'superseded':
            error('SUPERSESSION', label, 'Older record must be superseded')
        deps = list(row['depends_on'])
        data, kind = row['data'], row['type']
        typed = {'decision': {'facts': 'fact'}, 'task': {'requirements': 'requirement', 'prerequisites': 'task'}, 'attempt': {'task': 'task'}, 'artifact': {'producer': 'task', 'requirements': 'requirement'}, 'evidence': {'requirements': 'requirement'}, 'finding': {'requirements': 'requirement', 'resolution_evidence': 'evidence'}, 'gate': {'requirements': 'requirement', 'evidence': 'evidence'}}.get(kind, {})
        for field, expected in typed.items():
            refs = data[field] if isinstance(data[field], list) else [data[field]]
            for ref in refs:
                resolve(ref, label, expected)
                deps.append(ref)
        # Acceptance gate is a forward evaluation link, not a prerequisite dependency.
        if kind == 'task':
            resolve(data['acceptance_gate'], label, 'gate')
        dependencies[key] = deps
        for ref in deps:
            target = resolve(ref, label)
            if target and (target != latest[target['id']] or target['status'] == 'superseded'):
                stale.add(key)
        if kind == 'decision':
            facts = [resolve(r, label, 'fact') for r in data['facts']]
            if not facts or not data['research']:
                error('DECISION_SUPPORT', label, 'Decision needs fact and research references')
            if data['outcome'] in ('selected', 'excluded') and any(f and f['data']['knowledge'] != 'known' for f in facts):
                error('UNCERTAIN_DECISION', label, 'Unknown/conflicting facts cannot support settled applicability')
            for ref in data['research']:
                if ref['checkpoint'] != BASELINE or registry.get(ref['id']) != ref['partition_sha256']:
                    error('RESEARCH_REFERENCE', label, 'Frozen ID/checkpoint/partition digest mismatch')
        if kind == 'fact' and data['knowledge'] == 'unknown' and data['value'] is not None:
            error('UNKNOWN_VALUE', label, 'Unknown facts must use null, not false or an invented value')
        if kind in ('task', 'attempt'):
            if not all(safe_path(p) for p in data['paths']):
                error('PATH', label, 'Paths must be literal project-relative files/directories')
        if kind == 'artifact' and not safe_path(data['path']):
            error('PATH', label, 'Artifact path must be project-relative')
        if kind == 'artifact':
            producer = resolve(data['producer'], label, 'task')
            if producer and not under(data['path'], producer['data']['paths']):
                error('ARTIFACT_SCOPE', label, 'Artifact lies outside its producing task scope')
        if kind in ('fact', 'artifact', 'evidence', 'task', 'attempt', 'finding'):
            rev = data.get('candidate_revision', data.get('revision'))
            if rev != project['candidate_revision']:
                stale.add(key)
        if kind == 'task':
            grant = grants.get(data['grant']) if isinstance(grants, dict) else None
            if not isinstance(grant, dict) or set(grant) != {'project_id', 'actions', 'paths', 'max_steps'} or grant.get('project_id') != project['id'] or not matches(grant.get('actions'), 'texts') or not matches(grant.get('paths'), 'texts') or not matches(grant.get('max_steps'), 'positive_integer') or not all(safe_path(p) for p in grant.get('paths', [])):
                error('AUTHORITY', label, 'Task requires a valid grant supplied separately by operator')
            elif not set(data['actions']) <= set(grant['actions']) or not all(under(p, grant['paths']) for p in data['paths']) or data['budget_steps'] > grant['max_steps']:
                error('AUTHORITY', label, 'Task exceeds operator grant')
            if not data['requirements']:
                error('REQUIREMENTS', label, 'Task must address at least one requirement')
        if kind == 'attempt':
            task = resolve(data['task'], label, 'task')
            if task and (not set(data['actions']) <= set(task['data']['actions']) or not all(under(p, task['data']['paths']) for p in data['paths']) or data['steps_used'] > task['data']['budget_steps']):
                error('ATTEMPT_SCOPE', label, 'Recorded attempt exceeds task scope or budget')
        if kind == 'evidence' and data['result'] == 'PASS' and data['origin'] not in ('executed', 'reviewed'):
            error('FALSE_EVIDENCE', label, 'Proposed or merely observed evidence cannot PASS')
    # Detect cycles among prerequisites/consumed inputs without recursive traversal.
    pending = {k: {(r['id'], r['version']) for r in refs if (r['id'], r['version']) in records} for k, refs in dependencies.items()}
    while pending:
        ready = {k for k, refs in pending.items() if not refs}
        if not ready:
            error('DEPENDENCY_CYCLE', 'packet', 'Prerequisites and consumed inputs must form a DAG')
            break
        pending = {k: refs - ready for k, refs in pending.items() if k not in ready}
    changed = True
    while changed:
        before = len(stale)
        for key, refs in dependencies.items():
            if any((r['id'], r['version']) in stale for r in refs):
                stale.add(key)
        changed = len(stale) != before
    for row in latest.values():
        key = (row['id'], row['version'])
        if row['status'] != 'superseded' and key in stale:
            error('STALE', row['id'], 'Candidate or consumed input changed; reassessment required')
        if row['type'] == 'gate':
            d = row['data']
            ev = [resolve(r, row['id'], 'evidence') for r in d['evidence']]
            required = {(r['id'], r['version']) for r in d['requirements']}
            covered = {(r['id'], r['version']) for e in ev if e for r in e['data']['requirements']}
            if d['result'] == 'PASS' and (not required or not ev or any(e is None or e['data']['result'] != 'PASS' or (e['id'], e['version']) in stale for e in ev) or not required <= covered):
                error('GATE_EVIDENCE', row['id'], 'PASS requires current passing evidence for every requirement')
            open_findings = [f for f in latest.values() if f['type'] == 'finding' and f['status'] == 'current' and f['data']['disposition'] == 'open' and required & {(r['id'], r['version']) for r in f['data']['requirements']}]
            if d['result'] == 'PASS' and open_findings:
                error('OPEN_FINDING', row['id'], 'PASS cannot conceal open findings affecting required properties')
            if d['result'] == 'NOT_APPLICABLE' and (required or ev):
                error('GATE_APPLICABILITY', row['id'], 'N/A cannot waive declared requirements or evidence')
        if row['type'] == 'finding' and row['data']['disposition'] == 'resolved':
            evidence = [resolve(r, row['id'], 'evidence') for r in row['data']['resolution_evidence']]
            required = {(r['id'], r['version']) for r in row['data']['requirements']}
            covered = {(r['id'], r['version']) for e in evidence if e for r in e['data']['requirements']}
            if not required or not evidence or not required <= covered or any(e is None or e['data']['result'] != 'PASS' or (e['id'], e['version']) in stale for e in evidence):
                error('FINDING_RESOLUTION', row['id'], 'Resolution requires current passing evidence covering its requirements')
        if row['type'] == 'task':
            if row['status'] in ('running', 'review', 'complete'):
                for ref in row['data']['prerequisites']:
                    prerequisite = resolve(ref, row['id'], 'task')
                    if prerequisite and prerequisite['status'] != 'complete':
                        error('PREREQUISITE', row['id'], 'Active task has an incomplete prerequisite')
            attempts = [r for r in latest.values() if r['type'] == 'attempt' and r['data']['task'] == {'id': row['id'], 'version': row['version']}]
            if row['status'] in ('review', 'complete') and not any(r['data']['outcome'] == 'succeeded' and (r['id'], r['version']) not in stale for r in attempts):
                error('ATTEMPT_REQUIRED', row['id'], 'Review/completion requires a current successful recorded attempt')
            task_events = [e for e in packet['events'] if isinstance(e, dict) and e.get('task') == {'id': row['id'], 'version': row['version']}]
            state = 'planned'
            for event in task_events:
                if set(event) != {'task', 'from', 'to', 'reason'} or not matches(event.get('reason'), 'text') or event.get('from') != state or event.get('to') not in SPEC['task_transitions'].get(state, []):
                    error('TRANSITION', row['id'], 'Illegal or discontinuous task transition')
                    break
                state = event['to']
            if state != row['status']:
                error('TRANSITION_STATE', row['id'], 'Task status must equal replayed event state')
            if row['status'] == 'complete':
                gate = resolve(row['data']['acceptance_gate'], row['id'], 'gate')
                requirements = {(r['id'], r['version']) for r in row['data']['requirements']}
                if not gate or gate != latest[gate['id']] or gate['status'] != 'current' or gate['data']['result'] != 'PASS' or not requirements <= {(r['id'], r['version']) for r in gate['data']['requirements']}:
                    error('COMPLETION_GATE', row['id'], 'Complete requires a current passing gate covering task requirements')
    for event in packet['events']:
        if not isinstance(event, dict) or not valid_ref(event.get('task')):
            error('EVENT_SHAPE', 'event', 'Event requires a task/version reference')
        elif resolve(event['task'], 'event', 'task') is None:
            pass
    return result(f'{i}@{v}' for i, v in stale)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('packet', type=Path)
    parser.add_argument('--grants', type=Path)
    args = parser.parse_args()
    try:
        packet = json.loads(args.packet.read_text(encoding='utf-8'))
        grants = json.loads(args.grants.read_text(encoding='utf-8')) if args.grants else None
        report = validate(packet, grants)
    except (ValueError, OSError) as exc:
        report = {'status': 'FAIL', 'findings': [{'code': 'INPUT', 'message': str(exc)}], 'stale_records': []}
    print(json.dumps(report, indent=2))
    return 0 if report['status'] == 'PASS' else 1


if __name__ == '__main__':
    raise SystemExit(main())
