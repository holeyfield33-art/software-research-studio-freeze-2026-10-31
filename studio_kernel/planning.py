"""Deterministic assembly of reviewed planning inputs into canonical records.

No legacy selector, model invocation, command execution or authority creation.
"""
import hashlib
import json
from pathlib import Path

import jsonschema

from .canonical import ROOT, canonical, digest, reference, schema_errors
from .store import entity
from .validate import contains, safe_path, validate

DIMENSIONS = ('severity', 'exposure', 'reversibility', 'data_sensitivity', 'privilege',
              'operational_dependence', 'external_side_effects', 'novelty', 'uncertainty')
LEVELS = {'contained': 0, 'ordinary': 1, 'consequential': 2, 'critical': 3}
TEXT = {'type': 'string', 'minLength': 1}
TEXTS = {'type': 'array', 'items': TEXT, 'minItems': 1, 'uniqueItems': True}


def obj(properties, required=None):
    return {'type': 'object', 'additionalProperties': False, 'properties': properties,
            'required': list(properties) if required is None else required}


INTAKE_SCHEMA = obj({
    'intake_version': {'const': '0.1.0'}, 'project_id': TEXT, 'profile_id': TEXT,
    'created_at': {'type': 'string', 'format': 'date-time'},
    'expected_state_revision': {'type': 'integer', 'minimum': 0},
    'candidate': obj({'identity': TEXT, 'sha256': {'type': 'string', 'pattern': '^[a-f0-9]{64}$'}}),
    'records': {'type': 'array', 'items': {'type': 'object'}, 'minItems': 1},
    'risk_dimensions': {'type': 'object', 'additionalProperties': False,
                        'properties': {name: obj({'state': {'enum': ['known', 'unknown']},
                            'consequence': {'enum': list(LEVELS) + ['unknown']}, 'rationale': TEXT,
                            'fact_ids': {'type': 'array', 'items': TEXT, 'uniqueItems': True}}) for name in DIMENSIONS}},
    'reviews': {'type': 'array', 'minItems': 1, 'items': obj({
        'target': TEXT, 'review_id': TEXT, 'reviewer': TEXT, 'fact_ids': TEXTS,
        'status': {'enum': ['RECOMMENDED', 'CONDITIONAL', 'INAPPLICABLE', 'INCOMPLETE']},
        'obligation': {'enum': ['mandatory', 'optional', 'omitted']}, 'reasons': TEXTS})},
    'tasks': {'type': 'array', 'minItems': 1, 'items': obj({
        'key': {'type': 'string', 'pattern': '^[a-z0-9][a-z0-9_-]*$'}, 'goal': TEXT,
        'owner': TEXT, 'requirement_ids': TEXTS, 'oracle_ids': TEXTS,
        'paths': TEXTS, 'operations': TEXTS,
        'forbidden_operations': {'type': 'array', 'items': TEXT, 'uniqueItems': True},
        'budget': obj({'seconds': {'type': 'integer', 'minimum': 1},
                      'attempts': {'type': 'integer', 'minimum': 1},
                      'tokens': {'type': 'integer', 'minimum': 0},
                      'cost_limit': {'type': 'number', 'minimum': 0}, 'currency': TEXT}),
        'depends_on': {'type': 'array', 'items': TEXT, 'uniqueItems': True},
        'grant_ids': {'type': 'array', 'items': TEXT, 'uniqueItems': True}, 'stop_triggers': TEXTS})},
})
INTAKE_VALIDATOR = jsonschema.Draft202012Validator(INTAKE_SCHEMA, format_checker=jsonschema.FormatChecker())
POLICY = {'version': 'reviewed-planning-0.1.0', 'dimensions': DIMENSIONS, 'floors': LEVELS,
          'unknown': 'block affected planning', 'T3': 'no executable task proposal in MVP',
          'selection': 'recorded human review only; no automatic applicability assertion'}


def plan(intake):
    blockers = []
    def block(code, detail):
        blockers.append({'code': code, 'detail': detail})
    def result(records=(), proposals=()):
        return {'plan_status': 'INCOMPLETE' if blockers else 'COMPLETE',
                'execution_authority': 'UNKNOWN', 'release_disposition': 'HOLD',
                'blockers': blockers, 'records': list(records), 'task_refs': list(proposals),
                'scope': 'Reviewed planning declarations only; not automatic research selection, authorization or readiness'}
    try:
        canonical(intake)
        errors = list(INTAKE_VALIDATOR.iter_errors(intake))
    except (ValueError, TypeError, RecursionError) as exc:
        block('INPUT_SCHEMA_INVALID', str(exc))
        return result()
    if errors:
        for error in errors:
            block('INPUT_SCHEMA_INVALID', error.message)
        return result()
    project, records = intake['project_id'], intake['records']
    seed = validate(records, project_id=project, candidate=intake['candidate'])
    if any(f['level'] == 'FAIL' for f in seed['findings']):
        for finding in seed['findings']:
            if finding['level'] == 'FAIL':
                block(finding['code'], finding['record'] + ': ' + finding['message'])
        return result()
    # Planning accepts declarations, not imported run/gate/release assertions.
    allowed = {'ProjectProfile', 'Fact', 'Requirement', 'DesignDecision', 'Authority'}
    if any(r['kind'] not in allowed for r in records):
        block('SEED_KIND', 'Intake accepts profile/fact/requirement/design-decision/authority records only')
        return result()
    index = {}
    for r in records:
        if r['revision'] > index.get(r['id'], {}).get('revision', 0):
            index[r['id']] = r
    def lookup(identifier, kinds):
        row = index.get(identifier)
        if not row or row['kind'] not in kinds or digest(row) in seed['stale_sha256']:
            block('INPUT_REFERENCE', 'Missing, stale or incorrectly typed input: ' + identifier)
            return None
        return row
    profile = lookup(intake['profile_id'], {'ProjectProfile'})
    if not profile:
        return result()
    if profile['body']['baseline'] != intake['candidate']['identity']:
        block('BASELINE', 'Profile baseline and candidate identity differ')
    prefix = 'ua.plan.' + hashlib.sha256(project.encode('utf-8')).hexdigest()[:16]
    generated = []
    def make(kind, key, body, inputs):
        row = entity(kind, prefix + '.' + key, project, profile['owner'], body, profile['scope'])
        row['created_at'] = intake['created_at']
        row['derived_from'] = sorted({(r['id'], r['revision'], digest(r)): reference(r) for r in inputs if r}.values(), key=lambda r: (r['id'], r['revision']))
        if row['id'] in index:
            block('REVISION_REQUIRED', 'Initial planner cannot overwrite an existing generated identity: ' + row['id'])
        if schema_errors(row):
            block('GENERATED_SCHEMA', kind + ' failed canonical validation')
        generated.append(row)
        return row
    dimensions, unresolved, triggers, risk_inputs = [], [], [], [profile]
    tier = 0
    for name in DIMENSIONS:
        supplied = intake['risk_dimensions'].get(name)
        facts = [lookup(key, {'Fact'}) for key in supplied['fact_ids']] if supplied else []
        known = supplied and supplied['state'] == 'known' and supplied['consequence'] in LEVELS and facts and all(f and f['body']['state'] != 'unknown' for f in facts)
        if known:
            floor = LEVELS[supplied['consequence']]
            tier = max(tier, floor)
            if floor:
                triggers.append(name + ':' + supplied['consequence'])
        else:
            unresolved.append(name)
            block('RISK_EVIDENCE_MISSING', name)
        dimensions.append({'name': name, 'state': 'known' if known else 'unknown',
                           'consequence': supplied['consequence'] if known else 'unknown',
                           'rationale': supplied['rationale'] if supplied else 'No scoped assessment supplied',
                           'evidence_refs': [reference(f) for f in facts if f]})
        risk_inputs.extend(f for f in facts if f)
    risk = make('RiskAssessment', 'risk', {'tier': 'T' + str(tier), 'dimensions': dimensions,
                 'floor_triggers': sorted(triggers), 'unresolved': unresolved, 'tailoring_refs': []}, risk_inputs)
    if tier == 3:
        block('T3_OUTSIDE_MVP', 'Qualified domain assurance/review required; no executable task proposal')
    corpus = ROOT / 'preserved_freezes/SRS-FREEZE-2026-10-31-v1/tree/current_003R'
    registry = {}
    for path in sorted((corpus / 'dataset/v1').glob('*.jsonl')):
        for line, text in enumerate(path.read_text(encoding='utf-8').splitlines(), 1):
            if text.strip():
                r = json.loads(text)
                registry[r['id']] = (r, path.relative_to(corpus).as_posix(), line)
    choices, choice_inputs, seen = [], [profile, risk], set()
    for review in sorted(intake['reviews'], key=lambda r: r['target']):
        target = review['target']
        if target in seen:
            block('REVIEW_CONFLICT', 'Multiple reviews target the same record: ' + target)
        seen.add(target)
        declaration = lookup(review['review_id'], {'DesignDecision'})
        facts = [lookup(key, {'Fact'}) for key in review['fact_ids']]
        support = [f for f in facts if f]
        missing = [f['id'] for f in support if f['body']['state'] == 'unknown']
        reviewed = declaration and declaration['body']['status'] == 'ACCEPTED' and declaration['owner'] == review['reviewer'] and declaration['body']['chosen'] == target and contains(declaration['scope'], profile['scope'])
        if not reviewed:
            missing.append('accepted scoped review declaration')
        selectable = {'software_types', 'sdlc_stages', 'engineering_practices', 'architecture_patterns', 'prompt_patterns', 'roadmap_patterns', 'verification_gates', 'reference_projects'}
        if target not in registry or registry[target][0].get('knowledge_category') not in selectable:
            block('RESEARCH_TARGET', 'Unknown or unsupported research target: ' + target)
            continue
        original, partition, line = registry[target]
        reg = {'checkpoint_sha256': '5fea1fe5e8f19064df7ee9af4386aeb85046003c99ee83f9b4569432f0992aa8',
               'record_id': target, 'record_version': original['version'], 'partition': partition,
               'line': line, 'source_ids': original.get('source_ids', []), 'edge_ids': []}
        status = 'INCOMPLETE' if missing or any(f is None for f in facts) else review['status']
        if review['obligation'] == 'mandatory' and status != 'RECOMMENDED':
            block('MANDATORY_UNRESOLVED', target)
        if status in ('INCOMPLETE', 'CONDITIONAL'):
            block('REVIEW_INCOMPLETE', target)
        if review['obligation'] == 'omitted' and status != 'INAPPLICABLE' or status == 'INAPPLICABLE' and review['obligation'] != 'omitted':
            block('OMISSION_CONFLICT', target)
        reasons = review['reasons'] + (['Missing: ' + key for key in missing])
        choices.append({'target': target, 'status': status, 'obligation': review['obligation'],
                        'basis': 'research', 'rule_id': POLICY['version'] + ':' + target,
                        'fact_refs': [reference(f) for f in support], 'registry_refs': [reg],
                        'reasons': reasons, 'missing': missing, 'conflicts': []})
        choice_inputs.extend(support + ([declaration] if declaration else []))
    if not choices:
        block('NO_RESEARCH', 'No resolvable reviewed choices')
        return result(records + generated)
    selection = make('SelectionDecision', 'selection', {'policy_sha256': digest(POLICY),
                 'input_sha256': digest(intake), 'rules_version': POLICY['version'],
                 'plan_status': 'INCOMPLETE' if blockers else 'COMPLETE', 'choices': choices}, choice_inputs)
    tasks = {task['key']: task for task in intake['tasks']}
    if len(tasks) != len(intake['tasks']):
        block('TASK_IDENTITY', 'Task keys must be unique')
    order, pending = [], {key: set(task['depends_on']) for key, task in tasks.items()}
    for key, deps in pending.items():
        if deps - tasks.keys():
            block('TASK_DEPENDENCY', key + ' refers to unknown prerequisites')
    while pending and not any(b['code'] == 'TASK_DEPENDENCY' for b in blockers):
        ready = sorted(key for key, deps in pending.items() if not deps)
        if not ready:
            block('TASK_CYCLE', 'Task prerequisites contain a cycle')
            break
        order.extend(ready)
        pending = {key: deps - set(ready) for key, deps in pending.items() if key not in ready}
    resolved = {}
    for key in order:
        task = tasks[key]
        reqs = [lookup(rid, {'Requirement'}) for rid in task['requirement_ids']]
        oracles = [lookup(rid, {'Requirement', 'DesignDecision'}) for rid in task['oracle_ids']]
        grants = [lookup(rid, {'Authority'}) for rid in task['grant_ids']]
        if not all(safe_path(p) for p in task['paths']):
            block('TASK_PATH', key)
        if set(task['operations']) & set(task['forbidden_operations']):
            block('TASK_OPERATIONS', key)
        resolved[key] = (reqs, oracles, grants)
    covered = {r['id'] for reqs, _, _ in resolved.values() for r in reqs if r}
    for r in index.values():
        if r['kind'] == 'Requirement' and r['body']['priority'] == 'required' and contains(profile['scope'], r['scope']) and r['id'] not in covered:
            block('REQUIREMENT_UNPLANNED', r['id'])
    # An incomplete selection or unresolved risk never becomes an executable packet.
    if blockers:
        selection['body']['plan_status'] = 'INCOMPLETE'
        return result(records + generated)
    proposals, built = [], {}
    for key in order:
        task = tasks[key]
        reqs, oracles, grants = resolved[key]
        row = make('TaskPacket', 'task.' + key, {'goal': task['goal'],
                   'requirement_refs': [reference(r) for r in reqs], 'baseline': intake['candidate'],
                   'expected_state_revision': intake['expected_state_revision'], 'allowed_paths': task['paths'],
                   'allowed_operations': task['operations'], 'forbidden_operations': task['forbidden_operations'],
                   'budget': task['budget'], 'dependencies': [{'task': reference(built[dep]), 'kind': 'hard', 'condition': 'Prerequisite accepted before starting this task'} for dep in sorted(task['depends_on'])],
                   'oracle_refs': [reference(r) for r in oracles], 'grant_refs': [reference(r) for r in grants],
                   'stop_triggers': task['stop_triggers']}, [profile, risk, selection] + reqs)
        row['owner'] = task['owner']
        built[key] = row
        proposals.append(reference(row))
    output = records + generated
    checked = validate(output, project_id=project, candidate=intake['candidate'])
    for f in checked['findings']:
        if f['level'] == 'FAIL':
            block(f['code'], f['record'] + ': ' + f['message'])
    if blockers:
        selection['body']['plan_status'] = 'INCOMPLETE'
        output = records + [row for row in generated if row['kind'] != 'TaskPacket']
    return result(output, proposals if not blockers else [])
