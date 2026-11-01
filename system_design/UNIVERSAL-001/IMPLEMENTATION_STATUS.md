# Implementation checkpoint — project contracts 0.1.0

The universal design now has an executable project-packet validator under `studio_contracts/`, a declared contract, five unexecuted examples across software categories, and adversarial unit tests. This is the first M1 implementation slice; M1 is still in progress.

It validates record identity and versions, typed references, research IDs and partition digests, known/unknown/conflicting facts, separately supplied operator grant scopes, task/attempt budgets, ordered lifecycle transitions, gate evidence and finding resolution. Changed candidates or superseded inputs cause transitive invalidation. It does not run a project, verify real behavioral outputs or turn passing contract checks into project readiness.

The immediate next work is completing exception/approval, release and incident contracts and durable history semantics, followed by the M2 applicability/planning core. Keep the implementation independent of SurfaceTrace and evaluate shared contracts across multiple categories. Research gaps and the 003R selector limitations remain as documented.

Reproduce checks with `python -m unittest studio_contracts.test_validate -v`. See `studio_contracts/README.md` for the CLI, scope, synthetic-example warning and remaining work.
