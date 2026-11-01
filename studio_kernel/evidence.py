"""Verify signed execution records and retain proof bundles before history import."""
from pathlib import Path
import re

from .canonical import canonical, digest, load_json, reference, references, schema_errors
from .validate import validate


def dependency_closure(records, roots):
    chosen = {digest(r) for r in roots}
    changed = True
    while changed:
        before = len(chosen)
        for record in records:
            if digest(record) in chosen:
                chosen.update(ref['sha256'] for ref in references(record))
        ids = {r['id'] for r in records if digest(r) in chosen}
        chosen.update(digest(r) for r in records if r['id'] in ids)
        changed = len(chosen) != before
    return [r for r in records if digest(r) in chosen]


def verify_import(existing, incoming, *, project_id, candidate, verifier, artifact_root):
    records = existing + incoming if isinstance(existing, list) and isinstance(incoming, list) else None
    if records is None or not incoming or any(schema_errors(r) or r['kind'] != 'EvidenceRun' for r in incoming):
        return {'status': 'FAIL', 'findings': [{'code': 'EVIDENCE_INPUT', 'message': 'Import requires a nonempty list of canonical EvidenceRun records'}]}
    # Structural validation of the complete history also detects duplicates/dangling refs.
    full = validate(records, project_id=project_id, candidate=candidate)
    structural = [f for f in full['findings'] if f['code'] in ('SCHEMA', 'PROJECT', 'DUPLICATE', 'REFERENCE', 'HISTORY', 'CYCLE')]
    if structural:
        return {'status': 'FAIL', 'findings': structural}
    scoped = dependency_closure(records, incoming)
    checked = validate(scoped, project_id=project_id, candidate=candidate,
                       artifact_root=artifact_root, **verifier.callbacks(scoped))
    # A verified FAIL is a valid observation, not a passing acceptance result.
    for run in incoming:
        if not run['body']['executed'] or run['body']['status'] not in ('PASS', 'FAIL') or not verifier.verify(run, 'run'):
            checked['findings'].append({'code': 'EXECUTION_RECEIPT', 'record': run['id'],
                                        'message': 'Import requires a signed, executed PASS/FAIL observation', 'level': 'INCOMPLETE'})
    if checked['findings']:
        checked['status'] = 'FAIL' if any(f.get('level') == 'FAIL' for f in checked['findings']) else 'INCOMPLETE'
    return checked


def retain_bundle(store_path, receipts):
    """Content-addressed public proof sidecar, prepared before the DB transaction.

    An interrupted import may leave an unreferenced proof file; committed imports
    always record its digest in the canonical event reason. No private keys.
    """
    receipts = [r for _, r in sorted({digest(r): r for r in receipts}.items())]
    sha = digest(receipts)
    folder = Path(str(store_path) + '.receipts')
    folder.mkdir(exist_ok=True, parents=True)
    target = folder / (sha + '.json')
    data = canonical(receipts)
    try:
        with target.open('xb') as stream:
            stream.write(data)
            stream.flush()
            import os
            os.fsync(stream.fileno())
    except FileExistsError:
        if target.read_bytes() != data:
            raise ValueError('Existing receipt sidecar differs from its digest')
    return sha


def saved_receipts(store_path, events):
    receipts = []
    for event in events:
        match = re.match(r'^receipt_bundle_sha256=([a-f0-9]{64});', event['body']['reason'])
        if not match:
            continue
        sha = match.group(1)
        path = Path(str(store_path) + '.receipts') / (sha + '.json')
        bundle = load_json(path.read_bytes())
        if not isinstance(bundle, list) or digest(bundle) != sha:
            raise ValueError('Missing or corrupt receipt proof bundle')
        receipts.extend(bundle)
    return [r for _, r in sorted({digest(r): r for r in receipts}.items())]
