"""Propose canonical task acceptance gates from verified evidence; never execute."""
from .canonical import digest, reference, references, schema_errors
from .store import entity
from .validate import validate


def accept_task(records, task_ref, *, project_id, candidate, gate_id, policy_ref,
                review_ref, created_at, receipt_verifier, artifact_root):
    # Validate shape and all exact references before any semantic dereference.
    initial = validate(records, project_id=project_id, candidate=candidate)
    malformed = [f for f in initial['findings'] if f['code'] in ('SCHEMA', 'COLLECTION', 'PROJECT', 'DUPLICATE', 'REFERENCE', 'HISTORY', 'CYCLE')]
    if malformed:
        return {'status': 'FAIL', 'gate': None, 'findings': malformed}
    index = {(r['id'], r['revision']): r for r in records}
    latest = {}
    for r in records:
        if r['revision'] > latest.get(r['id'], {}).get('revision', 0):
            latest[r['id']] = r
    def resolve(ref, kind):
        if not isinstance(ref, dict) or set(ref) != {'id', 'revision', 'sha256'}:
            return None
        if not isinstance(ref['id'], str) or type(ref['revision']) is not int or not isinstance(ref['sha256'], str):
            return None
        row = index.get((ref['id'], ref['revision']))
        return row if row and row['kind'] == kind and reference(row) == ref and row == latest[row['id']] else None
    task = resolve(task_ref, 'TaskPacket')
    policy = resolve(policy_ref, 'DesignDecision')
    review = resolve(review_ref, 'DesignDecision')
    if not task or not policy or not review or policy['body']['status'] != 'ACCEPTED':
        return {'status': 'FAIL', 'gate': None, 'findings': [{'code': 'ACCEPTANCE_REFERENCE', 'message': 'Current task and accepted policy/review references required'}]}
    if review['owner'] == task['owner'] or task_ref not in review['derived_from'] or not receipt_verifier.verify(review, 'review') or not receipt_verifier.verify(policy, 'review'):
        return {'status': 'INCOMPLETE', 'gate': None, 'findings': [{'code': 'ACCEPTANCE_REVIEW', 'message': 'Requires signed policy and task-bound accepted review owned independently of builder'}]}
    if gate_id not in receipt_verifier.trust['required_gate_ids']:
        return {'status': 'FAIL', 'gate': None, 'findings': [{'code': 'GATE_POLICY', 'message': 'Gate ID is not in operator-pinned policy'}]}
    runs = [r for r in latest.values() if r['kind'] == 'EvidenceRun' and r['body']['packet_ref'] == task_ref and r['body']['candidate'] == candidate]
    if any(reference(run) not in review['derived_from'] for run in runs):
        return {'status': 'INCOMPLETE', 'gate': None, 'findings': [{'code': 'ACCEPTANCE_RUN_REVIEW', 'message': 'Signed acceptance review must bind every evaluated execution record, not only the task plan'}]}
    prerequisite_gates = []
    for dep in task['body']['dependencies']:
        if dep['kind'] == 'conditional':
            return {'status': 'INCOMPLETE', 'gate': None, 'findings': [{'code': 'PREREQUISITE_CONDITION', 'message': 'Conditional dependency requires explicit applicability adjudication'}]}
        if dep['kind'] != 'hard':
            continue
        matches = [g for g in latest.values() if g['kind'] == 'GateDecision' and dep['task'] in g['derived_from'] and g['body']['candidate'] == candidate and g['body']['status'] == 'PASS']
        if not matches:
            return {'status': 'INCOMPLETE', 'gate': None, 'findings': [{'code': 'PREREQUISITE_ACCEPTANCE', 'message': 'Hard prerequisite has no current passing task-bound gate'}]}
        prerequisite_gates.extend(matches)
    # Isolate this task's exact dependency closure, preserving history for resolved IDs.
    selected = {digest(task), digest(policy), digest(review)} | {digest(r) for r in runs + prerequisite_gates}
    changed = True
    while changed:
        before = len(selected)
        for r in records:
            if digest(r) in selected:
                selected.update(ref['sha256'] for ref in references(r))
        # Include all revisions of participating IDs so staleness cannot be hidden.
        participating = {r['id'] for r in records if digest(r) in selected}
        selected.update(digest(r) for r in records if r['id'] in participating)
        changed = len(selected) != before
    scoped = [r for r in records if digest(r) in selected]
    checks = validate(scoped, project_id=project_id, candidate=candidate,
                      artifact_root=artifact_root, **receipt_verifier.callbacks(scoped))
    # A rejected signature/artifact/oracle cannot become task acceptance.
    if checks['status'] != 'PASS':
        return {'status': checks['status'], 'gate': None, 'findings': checks['findings']}
    status = 'FAIL' if any(r['body']['status'] == 'FAIL' for r in runs) else 'PASS' if runs and all(r['body']['status'] == 'PASS' for r in runs) else 'INCOMPLETE'
    identifier = task['id'] + '.acceptance'
    revision = latest.get(identifier, {}).get('revision', 0) + 1
    gate = entity('GateDecision', identifier, project_id, review['owner'], {
        'gate_id': gate_id, 'policy_ref': policy_ref, 'candidate': candidate,
        'required_run_refs': [reference(r) for r in sorted(runs, key=lambda r: r['id'])],
        'status': status, 'reasons': ['Verified candidate-bound evidence for exact task' if runs else 'No current candidate-bound execution evidence'],
        'review_refs': [review_ref]}, task['scope'])
    gate['revision'] = revision
    gate['created_at'] = created_at
    gate['derived_from'] = [task_ref]
    if schema_errors(gate):
        return {'status': 'FAIL', 'gate': None, 'findings': [{'code': 'ACCEPTANCE_SCHEMA', 'message': 'Invalid gate envelope or timestamp'}]}
    return {'status': status, 'gate': gate, 'findings': [], 'notice': 'Decision proposal only; no release or project command executed'}
