# Agent B ScanPlan — preserved Studio greenfield experiment

**Historical experiment only.** Ongoing development moved to the independent [ScanPlan repository](https://github.com/holeyfield33-art/ScanPlan) after the Studio test/fix baseline was preserved. The standalone repository uses Studio-derived product/engineering knowledge, not the Studio engine as a runtime dependency. This directory retains the originally executed example, provenance and negative-control evidence; do **not** maintain two active copies or silently migrate fixes between repositories. The archived tool was an experimental offline plan generator, never a live scanner.

This is a self-contained **greenfield trial** of Software Research Studio's documented lifecycle approach, inspired by Agent B's threat-to-test planning pattern. It does **not** incorporate or link the existing Agent B scanner codebase, does not assess live targets, and is not a Studio product integration.

## What is built

A stdlib-only Python CLI takes a controlled JSON threat-model intake and returns deterministic, human-reviewable test proposals. Each result preserves the claim, positive and negative controls, an independent oracle requirement, and honest `NOT_RUN`/`UNKNOWN`/`HOLD` evidence fields. Four supported kinds: `path_traversal`, `prompt_injection`, `tool_authority`, and `secret_exposure`.

No HTTP, socket, shell execution, finding detection, host-identity validation or external targets. The user-supplied review owner is *claimed*, never authenticated. No license to probe a target is inferred.

## Run (Python 3.11+, no dependencies)

```bash
cd experiments/agent_b_scanplan
PYTHONPATH=. python3 -m unittest discover -s tests -v
PYTHONPATH=. python3 -m scanplan plan examples/demo.json --output /tmp/scanplan-demo.json
python3 -m json.tool /tmp/scanplan-demo.json
```

Use a fresh output path; the CLI refuses existing files and symlinked intake files. Omit `--output` to write JSON to stdout. Exit 0 = a **proposal was generated**, **not** a verified execution or release. Exit 1 = rejected input/output; argparse usage errors return 2.

## Explicit acceptance criteria

1. Valid input yields identical canonical bytes under repeated evaluation.
2. Plans contain one evidence-aware test proposal per uniquely identified threat.
3. All proposed tests have an independently defined oracle and both positive/negative controls.
4. Duplicate IDs/keys, unknown attack types, oversized JSON, extra authority fields and network scope are rejected.
5. No approved scan, target execution, trusted grant, or release claim is created.
6. Existing outputs remain unmodified and no network is accessed.

The included test suite checks these locally; it does not prove absence of every possible filesystem side effect or general security.

## Studio lifecycle and decisions

Read [SPEC.md](SPEC.md), [DECISIONS.md](DECISIONS.md) and [EVIDENCE.md](EVIDENCE.md). They describe the greenfield intake, requirements, CLI user experience, risks, research rationale, task sequence, independent oracles, test execution and release **HOLD**. This experiment exercises the **documented Studio workflow**; it has **not** run Studio's canonical `studio_kernel plan`, authenticated host receipts or kernel acceptance gate. Those remain future gates, not hidden achievements.

## STUDIO-PILOT-002 — Unicode error-contract regression

A bounded follow-up repaired one malformed-input crash: escaped unpaired Unicode surrogates in free-text fields now raise a controlled `IntakeError`. Four regression tests were added; **23/23 local tests passed** after an intentional red phase (1 failure, 4 errors). The four-case demo output is unchanged. [Read the exact trial report and evidence](trials/STUDIO-PILOT-002/README.md). This is local program evidence only: Studio canonical `plan`, independent host receipts and a comparative baseline remain NOT_RUN; release remains HOLD.
