# STUDIO-PILOT-001 — bounded universal-intake gate

**Status:** STARTED / INCOMPLETE. **Assessment type:** `UNIVERSAL_PROJECT_ASSESSMENT`. **Date:** 2026-11-01 UTC.

## 1. Executive finding

This pilot checks whether Studio can retain an honest, risk-aware assessment of an independently developed Linux CLI/MCP behavioral test harness. It is an **ephemeral external subject**, not a product link, submodule or integration. The previous agent's corrected narrative assessment was not available here; this package is a focused new intake/evidence gate, **not** a replacement report.

## 2. Intake and factual baseline

Target: `holeyfield33-art/mcp-behavior` at `0634e209d98fcf29f688f7a294ae73e5cec6b552` (GitHub). Studio at `eea09fb27ee2d9afec36e889d7eb68c5cdc69cd2`. Both commits were observed through GitHub repository APIs. Target `pyproject.toml` identifies a Python 3.11+ CLI, version `0.2.0.dev5`. `docs/STATUS.md` records local behavioral development GO, full containment UNKNOWN, and broad security certification NO-GO. These are **source claims**, not independently executed runtime results.

## 3. Lifecycle and user experience

The reviewed product is headless: **CLI/API usability and reasoned errors apply**, not visual screen design. Existing README, SDLC, roadmap and tests are present, but substantive usability testing, externally sealed runtime, end-to-end acceptance and operations are not verified by this pilot. This distinction is intentional: do not fabricate UI screens to satisfy a template.

## 4. Risk and evidence

Privilege and external side effects are consequential because namespace and cgroup supervision run externally configured processes. Most other dimensions remain UNKNOWN without an approved operator review. Treat uncalibrated risk as potentially consequential, and do not run arbitrary hostile MCP subjects. The pilot has **no execution authorization**.

## 5. Research applicability

Proposed, not autonomously selected or approved: `practice.test_strategy`, `gate.unit_integration_execution`, `gate.release_readiness` (real frozen record IDs, subject to applicability and reviewer confirmation). The frozen 003R novel-input selector is still NO-GO and was not run. UX visual screens, new MCP protocols, hosted marketing, and new scanners are omitted as unnecessary for the narrow task.

## 6. Connected specification and tasks

`pilot.json` records T1 (Studio-side report-evidence negative controls), T2 (review the already corrected report and form canonical planning inputs) and T3 (one authorized bounded code change with independent host evidence). Only **T1** can be demonstrated here. T2 and T3 deliberately stay BLOCKED. No target source changes.

## 7. Verification ledger

Observed: `pyproject.toml`, `docs/ROADMAP.md`, `docs/STATUS.md` pinned Git blob IDs; target hosted [run 41325740177](https://github.com/holeyfield33-art/mcp-behavior/actions/runs/41325740177) reports failure, but **both jobs had zero executed steps**. Do not report this as a code failure or passing test suite.

Reproduce this Studio-side contract from this directory:

```bash
python3 verify_pilot.py -v
python3 verify_pilot.py --check
python3 -m json.tool pilot.json >/dev/null
```

Locally observed in this pilot preparation: **7/7 validator tests pass**, including deliberate report-type, unexecuted-CI, false pass, product-link, unauthorized GO and stale-candidate controls. `--check` returns `{"status":"PASS","errors":[]}`. This only verifies the **reported evidence envelope and claims**, not source behavior, target security, Studio runtime planning or release readiness.

Not run: the target's 128-test suite on this pinned revision, live cgroup/bwrap acceptance, fixed Sentinel-Zero retest, Studio planner with reviewed canonical project records, independent signed host execution, or external user testing.

## 8. Decision

**HOLD / INCOMPLETE** for the end-to-end lifecycle pilot. The Studio-side report-evidence formatting/negative-control gate passes its finite seven tests; none of the target's release or containment gates is promoted. Studio integration is NO-GO and the freeze is unchanged.

## 9. Smallest next executable checkpoint

1. Acquire the corrected report and reviewer sign-off, compare its pinned candidate and evidence to this ledger; material differences become explicit new findings.
2. Form one reviewed canonical `studio_kernel` planning intake (not a fake synthetic risk assessment); verify it preserves unknowns and returns no execution authority.
3. On an explicitly authorized capable Linux host, execute **one** bounded target task with independent oracle and signed evidence, run targeted regression and update the project decision. No broad commercial or autonomy features.

Machine-readable source of truth for this pilot slice: `pilot.json`. Validator: `verify_pilot.py`. These additions live **outside frozen snapshots** and create no lasting product association.