"""CLI: python -m scanplan plan <intake.json> [--output <path>]"""
from __future__ import annotations

import argparse
import os
from pathlib import Path
import sys
import tempfile

from .core import IntakeError, build_plan, canonical, parse_input


def main(argv=None):
    parser = argparse.ArgumentParser(description="Offline Agent B threat-to-test plan generator (no scans)")
    sub = parser.add_subparsers(dest="cmd", required=True)
    plan = sub.add_parser("plan", help="Create an unexecuted, evidence-aware plan")
    plan.add_argument("intake", help="Path to local JSON intake")
    plan.add_argument("--output", help="New JSON output path; never overwrites")
    args = parser.parse_args(argv)
    try:
        path = Path(args.intake)
        if path.is_symlink() or not path.is_file():
            raise IntakeError("Intake must be an existing regular file, not a symlink")
        raw = path.read_bytes()
        result = build_plan(parse_input(raw))
        payload = canonical(result)
        if args.output:
            out = Path(args.output)
            if not out.parent.is_dir() or out.exists() or out.is_symlink():
                raise IntakeError("Output requires an existing directory and new non-symlink filename")
            # Exclusive creation avoids clobbering an existing output, even during races.
            fd = os.open(out, os.O_WRONLY | os.O_CREAT | os.O_EXCL, 0o600)
            try:
                with os.fdopen(fd, "wb") as stream:
                    stream.write(payload)
            except BaseException:
                out.unlink(missing_ok=True)
                raise
        else:
            sys.stdout.buffer.write(payload)
        return 0
    except (IntakeError, OSError) as exc:
        print(f"scanplan: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    raise SystemExit(main())
