"""Local canonical record validation, history import and derived status."""
import argparse
import json
from pathlib import Path
import sqlite3
import jsonschema

from .canonical import load_json
from .store import HistoryError, Store
from .validate import validate
from .planning import plan
from .receipts import Receipts
from .evidence import verify_import, retain_bundle, saved_receipts
from .acceptance import accept_task


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    commands = parser.add_subparsers(dest='command', required=True)
    planning = commands.add_parser('plan', help='Assemble reviewed intake into canonical planning records')
    planning.add_argument('intake', type=Path)
    planning.add_argument('--output', type=Path, help='New output directory; existing directories are never overwritten')
    check = commands.add_parser('validate')
    check.add_argument('records', type=Path)
    check.add_argument('--project', required=True)
    check.add_argument('--candidate', type=Path)
    check.add_argument('--artifacts', type=Path)
    check.add_argument('--trust-config', type=Path)
    check.add_argument('--receipts', type=Path)
    importing = commands.add_parser('import-evidence', help='Verify signed run observations before recording them')
    importing.add_argument('records', type=Path)
    importing.add_argument('--project', required=True)
    importing.add_argument('--store', type=Path, required=True)
    importing.add_argument('--expected', type=int, required=True)
    importing.add_argument('--candidate', type=Path, required=True)
    importing.add_argument('--actor', required=True)
    importing.add_argument('--trust-config', type=Path, required=True)
    importing.add_argument('--receipts', type=Path, required=True)
    importing.add_argument('--artifacts', type=Path, required=True)
    acceptance = commands.add_parser('accept', help='Propose a task-bound gate from verified evidence')
    acceptance.add_argument('--project', required=True)
    acceptance.add_argument('--store', type=Path, required=True)
    acceptance.add_argument('--candidate', type=Path, required=True)
    acceptance.add_argument('--task-ref', type=Path, required=True)
    acceptance.add_argument('--policy-ref', type=Path, required=True)
    acceptance.add_argument('--review-ref', type=Path, required=True)
    acceptance.add_argument('--gate-id', required=True)
    acceptance.add_argument('--created-at', required=True)
    acceptance.add_argument('--trust-config', type=Path, required=True)
    acceptance.add_argument('--receipts', type=Path)
    acceptance.add_argument('--artifacts', type=Path, required=True)
    commit = commands.add_parser('record')
    commit.add_argument('records', type=Path)
    commit.add_argument('--project', required=True)
    commit.add_argument('--store', type=Path, required=True)
    commit.add_argument('--expected', type=int, required=True)
    commit.add_argument('--candidate', type=Path, required=True)
    commit.add_argument('--actor', required=True)
    commit.add_argument('--reason', required=True)
    status = commands.add_parser('status')
    status.add_argument('--project', required=True)
    status.add_argument('--store', type=Path, required=True)
    status.add_argument('--trust-config', type=Path)
    status.add_argument('--receipts', type=Path)
    status.add_argument('--artifacts', type=Path)
    args = parser.parse_args()
    try:
        if args.command == 'plan':
            report = plan(load_json(args.intake.read_bytes()))
            if args.output:
                args.output.mkdir(parents=True, exist_ok=False)
                (args.output / 'plan.json').write_text(json.dumps(report, indent=2) + '\n', encoding='utf-8')
                (args.output / 'records.json').write_text(json.dumps(report['records'], indent=2) + '\n', encoding='utf-8')
            print(json.dumps(report, indent=2))
            return 0 if report['plan_status'] == 'COMPLETE' else 2
        if args.command == 'validate':
            candidate = load_json(args.candidate.read_bytes()) if args.candidate else None
            records = load_json(args.records.read_bytes())
            if bool(args.trust_config) != bool(args.receipts):
                raise ValueError('Signed validation requires both operator trust config and receipts')
            verifier = Receipts(load_json(args.trust_config.read_bytes()), load_json(args.receipts.read_bytes())) if args.trust_config else None
            report = validate(records, project_id=args.project, candidate=candidate, artifact_root=args.artifacts,
                              **(verifier.callbacks(records) if verifier else {}))
            print(json.dumps(report, indent=2))
            return 0 if report['status'] == 'PASS' else 2 if report['status'] == 'INCOMPLETE' else 1
        if args.command in ('status', 'import-evidence', 'accept') and not args.store.is_file():
            raise HistoryError('History file does not exist')
        store = Store(args.store, args.project)
        if args.command in ('import-evidence', 'accept'):
            state = store.read()
            candidate = load_json(args.candidate.read_bytes())
            proofs = saved_receipts(args.store, state['events'])
            if args.receipts:
                proofs.extend(load_json(args.receipts.read_bytes()))
            verifier = Receipts(load_json(args.trust_config.read_bytes()), proofs)
            if args.command == 'import-evidence':
                incoming = load_json(args.records.read_bytes())
                report = verify_import(state['records'], incoming, project_id=args.project,
                                       candidate=candidate, verifier=verifier, artifact_root=args.artifacts)
                if report['status'] == 'PASS':
                    sha = retain_bundle(args.store, proofs)
                    event = store.commit(incoming, expected_revision=args.expected, candidate=candidate,
                                         actor=args.actor, reason='receipt_bundle_sha256=' + sha + '; verified execution observations imported')
                    report = {'status': 'RECORDED', 'event': event, 'notice': 'Verified observation import; not task acceptance or release'}
            else:
                report = accept_task(state['records'], load_json(args.task_ref.read_bytes()),
                    project_id=args.project, candidate=candidate, gate_id=args.gate_id,
                    policy_ref=load_json(args.policy_ref.read_bytes()), review_ref=load_json(args.review_ref.read_bytes()),
                    created_at=args.created_at, receipt_verifier=verifier, artifact_root=args.artifacts)
            print(json.dumps(report, indent=2))
            return 0 if report['status'] in ('RECORDED', 'PASS') else 2 if report['status'] == 'INCOMPLETE' else 1
        if args.command == 'record':
            event = store.commit(load_json(args.records.read_bytes()), expected_revision=args.expected, candidate=load_json(args.candidate.read_bytes()), actor=args.actor, reason=args.reason)
            print(json.dumps({'status': 'RECORDED', 'event': event, 'notice': 'Persistence only; no readiness, authorization or execution granted'}, indent=2))
        else:
            state = store.read()
            proofs = saved_receipts(args.store, state['events'])
            if args.receipts:
                proofs.extend(load_json(args.receipts.read_bytes()))
            if args.receipts and not args.trust_config:
                raise ValueError('Receipt verification requires operator-pinned trust config')
            verifier = Receipts(load_json(args.trust_config.read_bytes()), proofs) if args.trust_config else None
            print(json.dumps({'snapshot': store.snapshot(), 'validation': validate(state['records'], project_id=args.project,
                candidate=state['candidate'], artifact_root=args.artifacts, **(verifier.callbacks(state['records']) if verifier else {}))}, indent=2))
        return 0
    except (ValueError, OSError, sqlite3.Error, RecursionError, jsonschema.ValidationError) as exc:
        print(json.dumps({'status': 'FAIL', 'error': str(exc)}, indent=2))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
