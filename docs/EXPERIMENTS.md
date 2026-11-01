# Studio dogfooding and experiments

Experiments test the **universal software-development method**, not a permanent relationship between software products. Each experiment must preserve intake, lifecycle specification, risk/omissions, task dependencies, code or artifacts, real verification, independent review gaps, and its own HOLD/GO decision.

## Existing-repository pilot: STUDIO-PILOT-001

[Read the pilot](../pilots/STUDIO-PILOT-001/README.md). Uses MCP Behavior as a **temporary pinned repository assessment subject**; it does not alter or link the target repo. The early evidence-envelope validator had 7 local tests passed. Task execution, full canonical planning and external signed acceptance remain NOT_RUN.

## New-build pilot: Agent B ScanPlan v0.1

[Open the standalone code sample](../experiments/agent_b_scanplan/README.md). A small offline CLI accepts threat hypotheses and proposes reviewer-owned positive/negative tests with independent oracles. It **never scans** a website or network. A local 18-test suite passed on Python 3.13.5; the generated four-case sample is deterministic and retains HOLD status. This is a new greenfield experiment *inspired by* the earlier Agent B threat-to-test idea, not linked code or a merged product.

**Studio comparison scorecard (not yet measured):** setup effort, lead time, required versus implemented acceptance criteria, post-build defects, number of unauthorized side effects, independent evidence completeness, human corrections, and maintenance effort. No claimed 50–75% productivity gain without a measured baseline and repeatable comparison.

## Next experimental gate

Construct a canonical `studio_kernel` planning intake from the new-build spec, explicitly resolve unknown risk and independent review, then capture a pinned, scoped execution receipt for **one** test. Passing local tests alone cannot close that gate. Do not expand to live scanning or product integration merely because the offline generator passes.
