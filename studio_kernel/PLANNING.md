# Connected reviewed-planning slice

The kernel now connects supplied intent and facts to a risk record, reviewed research choices, requirements and dependency-ordered task proposals. It consumes canonical input records and produces canonical output records. The intake JSON object is a transport format, not a replacement for the canonical record schema.

## Run

```text
python -m studio_kernel plan studio_kernel/planning_examples/cli.intake.json --output path/to/new-plan
```

The output directory must not already exist. It receives `plan.json` (disposition, blockers and records) and `records.json` (the canonical record list, suitable for the existing history `record` command). Exit 0 means the declared planning inputs are internally resolved; exit 2 means incomplete planning. Malformed JSON and file-operation failures exit 1. A malformed but readable intake produces INPUT_SCHEMA_INVALID and incomplete planning.

`plan_status`, `execution_authority` and `release_disposition` are separate. Even a COMPLETE plan has execution authority UNKNOWN and release HOLD. Planning neither executes tasks nor supplies a trusted grant. The kernel still reports MISSING_GRANT or missing authenticated receipts when the resulting records are evaluated for execution/readiness.

## Inputs

`planning_examples/intake.schema.json` describes the closed intake shape. Supply a project ID, profile ID, pinned candidate, expected state revision, authored timestamp, canonical records, scoped risk-dimension declarations, reviewed choices and proposed tasks.

Allowed seed record kinds are ProjectProfile, Fact, Requirement, DesignDecision and Authority. They must satisfy the canonical schema, exact references, project identity and structured fact consistency. Run/gate/release assertions cannot be smuggled through this planning entrypoint. Existing records are not edited or silently migrated.

Each research choice names an actual frozen record, relevant fact IDs, disposition/obligation and a recorded DesignDecision review. The declaration must be ACCEPTED, name the exact target as its chosen option, match the declared reviewer/owner and cover the project scope. These checks establish a consistent **recorded review declaration**, not authenticated human approval or proof of source applicability. Runtime authority still comes from the trusted host boundary.

The planner resolves the original checkpoint digest, registry partition, JSONL line, original version and attached source IDs. Output is checked with the canonical kernel, including comparison with the preserved checkpoint bytes. It does not infer applicability from category labels, run the unreliable legacy selector, manufacture missing IDs, or claim that attached sources prove the chosen interpretation. Duplicate reviews for one target are blocked instead of choosing the last one.

## Risk and missing information

The nine declared dimensions are severity, exposure, reversibility, data sensitivity, privilege, operational dependence, external side effects, novelty and uncertainty. A known dimension requires supplied non-unknown fact support, a consequence label and rationale. Missing/unknown dimensions remain unknown and produce targeted RISK_EVIDENCE_MISSING blockers.

The proposed tier is the highest supplied consequence floor: contained→T0, ordinary→T1, consequential→T2, critical→T3. Unknown dimensions retain an explicitly unresolved provisional result; the tier is not proof of low risk. A T3 declaration prevents task proposals in this MVP. These tiers are design synthesis inherited from the candidate policy, not calibrated probabilities, regulatory classifications or autonomous risk analysis. The quality and relevance of the supplied assessment still require independent review.

Unknown facts supporting a choice produce INCOMPLETE and a current missing-input reason. Resupplying known facts recomputes the result and removes resolved reasons. Structured contradictions block the intake before positive selection. Unrelated facts do not alter choice dispositions or task objectives, though they change the pinned overall input digest.

## Tasks and history

Tasks explicitly name requirements, oracle records, paths, operations, budgets, stop triggers and prerequisites. The planner checks literal safe paths, conflicting allowed/forbidden operations, unique keys, missing prerequisites, cycles and coverage of required outcomes in the profile scope and its descendants. It orders tasks deterministically and binds hard prerequisites through exact record references. It does not execute or consider a prerequisite completed merely because its packet exists.

Any unresolved risk, required choice, input, coverage or task-graph condition yields no task packets. Risk and selection diagnostics remain reviewable. Task proposals are emitted only after these planning checks resolve. They can still be blocked by actual authority, runtime capability or verification requirements.

Generated records carry the supplied authored timestamp and stable project-derived IDs. Repeated identical inputs produce identical outputs. The initial planner refuses to overwrite a generated identity already present in the seed; explicit versioned replanning/migration remains future work. Record the whole canonical output batch with the specified expected state revision. Atomic history import and replay preserve the resulting chain without executing it. A stale history revision must be reconciled, not refreshed automatically.

## Examples and checks

Five committed synthetic inputs cover CLI, library, API, web and pipeline **planning format scenarios**, not real platform trials. `unknown-risk.intake.json` is a negative example that must yield no task packets. None contains an actual execution grant or demonstrated project outcome. Tests cover the connected CLI path from intake through planning, history import and replay; positive/negative fact states; tier floors; reason removal; unrelated-fact invariance; source resolution; task ordering and blockers.

Regenerate the examples/schema with `python -m studio_kernel.build_planning_examples`. This development helper reuses explicit synthetic test builders; runtime planning never imports tests. Run `python -m unittest studio_kernel.test_planning -v`.

Remaining work includes real intake inspection, source-scope and applicability evaluation, calibrated domain policies, independently verified reviews, authenticated grant/evidence import, actual prerequisite acceptance scheduling, explicit revision/replanning and the complete release/maintenance loop. The legacy selector's generalization NO-GO and the product integration NO-GO remain unchanged.
