# STUDIO-PILOT-002 — bounded ScanPlan Unicode repair

**Report type:** IMPLEMENTATION_VERIFICATION with connected universal project intake  
**Date:** 2026-11-01 (UTC)  
**Baseline Studio:** `3795c1736b20ac3d6955e1587f4c7f7a8c778ec3`  
**Target:** `experiments/agent_b_scanplan/`, a Studio-owned **offline** greenfield demonstration, not a linked product  
**Scope:** one input-validation defect, tests, evidence and operator-facing docs  
**Status:** LOCAL REGRESSION PASS; CANONICAL KERNEL ACCEPTANCE INCOMPLETE; RELEASE HOLD

## 1. Intake and project diagnosis

ScanPlan is an offline threat-hypothesis-to-test-plan CLI. Its subject, review owner, component and observation fields accept free text. A valid JSON document containing an escaped unpaired UTF-16 surrogate (for example `"\uD800"`) parses into a Python string but cannot be encoded to UTF-8 using the current canonical output. Before this change, `build_plan` raised an unhandled `UnicodeEncodeError`; running the CLI emitted a traceback rather than the promised concise validation error.

**Reproduced on actual pinned baseline files:** `scanplan/core.py` Git blob `6b6851fd1d294fe7113bddfcd5e2ab2937704545`, preexisting `tests/test_scanplan.py` blob `629e04e9a4fb88c13622308bced434af2d84410b`.

## 2. Users, CLI experience and exclusions

User: developer/reviewer planning fixture tests. Success: malformed escaped Unicode is rejected as an `IntakeError`; the CLI returns exit 1 with a concise message and creates **no** output. Valid Unicode including accented characters and emoji remains supported and deterministic. No screen UI is applicable. No network scan, autonomous target execution, external repo changes, deployment, or unrelated scanner features.

## 3. Risks and missing evidence

Risk dimensions for this *local validation change*: possible side effects confined to file input/output, no network feature added. Security-sensitive meanings of `review_owner` remain **unverified declarations**, not authorization. Operational dependence, external deployment environment, real-world impact and full agentic safety coverage remain UNKNOWN. Provisional low-impact code-change classification is **not** a signed risk approval or general product safety finding.

## 4. Research applicability and omissions

Proposed applicable frozen records (human/agent judgment; 003R selector NOT_RUN): `practice.test_strategy` (positive + negative regression), `gate.requirements_acceptance` (trace an error contract to tests), `gate.unit_integration_execution` (actual command results), `practice.version_control_review` (scoped diff and independent PR review). Source IDs/hashes need explicit Studio registry resolution and reviewer acceptance before they become an authenticated `SelectionDecision`.

Omitted as out of scope: UI screens, additional threat types, live scanner authorization, host adaptation and Stage 004 research changes.

## 5. Requirements, task and oracles

| Requirement | Bounded change | Independent acceptance check |
|---|---|---|
| R1 — reject malformed free text | Reject Unicode surrogate range during `_safe_string` validation in `scanplan/core.py` | Four fields containing escaped surrogate trigger `IntakeError` |
| R2 — protect CLI contract | No CLI architecture change | CLI exit 1, no created output, no traceback |
| R3 — preserve valid behavior | Existing canonical encoding unchanged | International/emoji text is accepted; valid fixture output SHA unchanged |
| R4 — keep authority honest | No runtime policy changes | Plans still report `UNVERIFIED` authority and `HOLD` release |

Allowed paths: `experiments/agent_b_scanplan/scanplan/core.py`, `tests/test_unicode_boundary.py`, and this trial's evidence/documentation. Allowed operations: local edits and offline test commands. Forbidden: network access, executing generated scan cases, altering the original 003/003R freeze, external writes and release approvals. Stop when an unexpected side effect, failing regression, scope breach or missing independent oracle occurs.

## 6. Executed test ledger

See [evidence.json](evidence.json), with exact commands, outcomes, code identity, Python version and output SHA-256.

- Baseline before new test: **19/19 PASS**.
- Red phase (new tests against unchanged code): **23 tests; 1 failure + 4 errors**, exit 1. This confirms the bug is real and the tests are capable of detecting it.
- Green phase after one-line guard: **23/23 PASS**, exit 0; independent repeat **23/23 PASS**, exit 0.
- Existing CLI demonstration: exit 0, 4 proposed cases, 0 executed; output SHA-256 `e46237e1e3573ca04f260d1fb0d4b6cbe84ce8564a62561d2cba56c52d0ac373` (unchanged).
- Git blob SHA equality between tested local code and pushed source checked for the modified core and new test.

Reproduce from the Studio repo root:

```bash
cd experiments/agent_b_scanplan
PYTHONPATH=. python3 -m unittest discover -s tests -v
PYTHONPATH=. python3 -m scanplan plan examples/demo.json
```

## 7. Studio kernel and evidence integrity boundary

**Canonical Studio planning:** NOT_RUN. No `studio_kernel plan` output or accepted TaskPacket for this real-world intake has been obtained. The available kernel cannot inspect external code and has no capability-enforcing/signing host adapter. The task specification above is **human-readable**, not a fabricated schema-valid canonical approval.

**Trusted signed host receipt:** NOT_RUN. Test logs and byte hashes are accurate local observations, but the same builder session authored the fix and executed tests. A builder-owned signature would not establish independent acceptance. No `import-evidence` or `accept` claim is made; effective release decision remains HOLD.

## 8. Comparison study boundary

This was one Studio-guided run, not a controlled A/B productivity test. No independent agent baseline, blind assignment, token/time denominator, or unassisted comparison was collected. See [COMPARISON_PROTOCOL.md](COMPARISON_PROTOCOL.md); no 50–75% improvement is claimed.

## 9. Next executable gate

An independent reviewer must approve the exact task and negative-control oracles; a trusted host must enforce one scoped command, seal the tested code identity, issue a run receipt bound to the real record hash, then an independent reviewer signs a task-bound review. Feed that evidence through Studio's existing `import-evidence` and `accept` interfaces and preserve HOLD on any mismatch. Until then **local code correctness PASS, end-to-end Studio integration NO-GO/HOLD**.
