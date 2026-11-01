# Studio current status and next gates

**Date:** 2026-11-01. **Current phase:** research baseline and partial kernel exist; **Studio's effect on frontier-model engineering quality has not yet been measured**. Lifecycle artifacts are supporting tools, not the objective. See [product intent](PRODUCT_INTENT.md).

| Concern | Status | Evidence boundary |
|---|---|---|
| 003/003R frozen knowledge | GO for documented archive/curated checks | 715 records, 601 relationships; [003 resubmission receipt](../checkpoint_intake/2026-11-01/STUDIO_003_REVERIFICATION.md) |
| 003R automatic novel-input selection | **NO-GO** | Known rationale, authority contradiction, malformed-input and side-effect selection failures |
| Universal architecture | CANDIDATE | [Design checkpoint](../architecture/UNIVERSAL-ARCH-001/README.md) |
| Canonical kernel, reviewed planning, signed evidence and SQLite history | Partial implementation with local tests | [Kernel contract and limitations](../studio_kernel/README.md); no enforcing host |
| Brownfield evidence pilot | Started / HOLD | [STUDIO-PILOT-001](../pilots/STUDIO-PILOT-001/README.md); report-mode and evidence controls only |
| Greenfield build | Local MVP 19 tests PASS; lifecycle HOLD | [Agent B ScanPlan](../experiments/agent_b_scanplan/README.md), an offline non-scanning CLI |
| General product integration and release | **NO-GO** | No independent complete lifecycle trial, approved selector, or production authorization |

## What not to infer

An agent's report is not a verified code change. A plan's COMPLETE status is not execution authorization; a signature without a truthful trusted host is not complete evidence. A GitHub Actions workflow that never runs steps is NOT_RUN, not a passing or failing application suite. The example scanner does not scan real targets. No performance multiplier or commercial value claim has been measured.

## Smallest next milestones

1. **Evaluate the actual model-assistance value:** give separate frontier-model sessions the same natural, under-specified vibecoder request, with and without curated Studio context. Ask for a working change, not a report.
2. **Score engineering outcomes:** independent acceptance, relevant omissions discovered, unnecessary modifications, regressions, user clarifications, UX fit and actual time/token cost.
3. **Improve knowledge selection:** use the evidence to determine which research records helped, distracted or caused feature creep; repair applicability before automating recommendations. Canonical planning and trusted receipts remain optional supporting gates where risk warrants them. No 50–75% improvement claim without comparable trials.

No product links, Stage 004 expansion, additional autonomous scanners or deployment work are authorized by these milestones.
