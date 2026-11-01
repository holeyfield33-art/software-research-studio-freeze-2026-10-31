# Studio current status and next gates

**Date:** 2026-11-01. **Current phase:** research-integrity and kernel baseline established; real-world lifecycle proof **incomplete**.

| Concern | Status | Evidence boundary |
|---|---|---|
| 003/003R frozen knowledge | GO for documented archive/curated checks | 715 records, 601 relationships; [003 resubmission receipt](../checkpoint_intake/2026-11-01/STUDIO_003_REVERIFICATION.md) |
| 003R automatic novel-input selection | **NO-GO** | Known rationale, authority contradiction, malformed-input and side-effect selection failures |
| Universal architecture | CANDIDATE | [Design checkpoint](../architecture/UNIVERSAL-ARCH-001/README.md) |
| Canonical kernel, reviewed planning, signed evidence and SQLite history | Partial implementation with local tests | [Kernel contract and limitations](../studio_kernel/README.md); no enforcing host |
| Brownfield evidence pilot | Started / HOLD | [STUDIO-PILOT-001](../pilots/STUDIO-PILOT-001/README.md); report-mode and evidence controls only |
| Greenfield build | Local MVP tests PASS; lifecycle HOLD | [Agent B ScanPlan](../experiments/agent_b_scanplan/README.md), an offline non-scanning CLI |
| General product integration and release | **NO-GO** | No independent complete lifecycle trial, approved selector, or production authorization |

## What not to infer

An agent's report is not a verified code change. A plan's COMPLETE status is not execution authorization; a signature without a truthful trusted host is not complete evidence. A GitHub Actions workflow that never runs steps is NOT_RUN, not a passing or failing application suite. The example scanner does not scan real targets. No performance multiplier or commercial value claim has been measured.

## Smallest next milestones

1. **Greenfield lifecycle replay:** turn the ScanPlan assessment/spec into reviewed canonical kernel records, verify the task-graph and risk unknowns, and persist a history event.
2. **Independent execution/receipt gate:** on a clearly authorized local host, execute exactly one bounded verification action for a pinned candidate, retain evidence, and check receipt authority and output bytes.
3. **Measured comparison:** run the same small change with and without Studio, compare acceptance-criteria coverage, observed defects, agent interventions and minutes/tokens. Do not claim the target 50–75% boost until the comparison has replicable results.

No product links, Stage 004 expansion, additional autonomous scanners or deployment work are authorized by these milestones.
