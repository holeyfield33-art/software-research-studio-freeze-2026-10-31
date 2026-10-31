# SurfaceTrace UXEC maintenance pilot — preregistration DRAFT

Status: NOT STARTED. No tasks or budgets approved yet.

## Research question
Does UXEC improve independently accepted maintenance outcomes and reduce critical regressions at acceptable total effort compared with the existing 003R-informed workflow?

## Conditions
Control: approved task requirements, frozen 003R reference, ordinary workflow.
Treatment: identical requirements and baseline plus approved UXEC contracts and verification discipline.

## Candidate pilot
Six real bounded tasks across three interaction categories, each attempted under both conditions, two fresh-agent runs per task per condition = 24 runs. This is a feasibility pilot, not a powered generalization. Select tasks only after SurfaceTrace source inspection. Freeze tasks, acceptance oracles and budgets before execution.

## Control variables
Same starting commit/dependencies, model and settings, tools, limits and approved user requirements. Isolated working trees, fresh contexts, randomized/counterbalanced order and independent blinded review where practical. If treatment obtains additional task knowledge, share it with control or explicitly change the estimand to end-to-end process effect.

## Metrics
Primary: independently accepted outcomes, critical/major defects, regressions.
Secondary: elapsed time, agent runtime/tokens/charges, CI cost, human preparation/review/intervention/correction, contract creation/upkeep, rework and trace completeness. Include failures and timeouts, not only successful runs. Disclose amortization assumptions separately.

## Stop / pause
Stop run for secrets exposure, unauthorized destructive action, frozen 003R mutation, invalid baseline or budget limit. Pause pilot for oracle leakage, changed tools/models, corrupt fixtures or new safety-critical scope. Retain all stopped runs in analysis.

## Reporting
Paired task-level raw outcomes; PASS/FAIL/BLOCKED/NOT RUN; reviewer disagreements; no unverified percentage claims. Continuation thresholds must be approved before trials.
