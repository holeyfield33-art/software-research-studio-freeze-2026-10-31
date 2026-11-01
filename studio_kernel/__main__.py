"""Local canonical record validation, history import and derived status."""
import argparse
import json
from pathlib import Path
import sqlite3

from .canonical import load_json
from .store import HistoryError, Store
from .validate import validate
from .planning import plan


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
            report = validate(load_json(args.records.read_bytes()), project_id=args.project, candidate=candidate, artifact_root=args.artifacts)
            print(json.dumps(report, indent=2))
            return 0 if report['status'] == 'PASS' else 2 if report['status'] == 'INCOMPLETE' else 1
        if args.command == 'status' and not args.store.is_file():
            raise HistoryError('History file does not exist')
        store = Store(args.store, args.project)
        if args.command == 'record':
            event = store.commit(load_json(args.records.read_bytes()), expected_revision=args.expected, candidate=load_json(args.candidate.read_bytes()), actor=args.actor, reason=args.reason)
            print(json.dumps({'status': 'RECORDED', 'event': event, 'notice': 'Persistence only; no readiness, authorization or execution granted'}, indent=2))
        else:
            state = store.read()
            print(json.dumps({'snapshot': store.snapshot(), 'validation': validate(state['records'], project_id=args.project, candidate=state['candidate'])}, indent=2))
        return 0
    except (ValueError, OSError, sqlite3.Error, RecursionError) as exc:
        print(json.dumps({'status': 'FAIL', 'error': str(exc)}, indent=2))
        return 1


if __name__ == '__main__':
    raise SystemExit(main())
