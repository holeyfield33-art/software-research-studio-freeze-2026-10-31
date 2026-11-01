# Minimal complete MVP and implementation roadmap

## MVP boundary

A local, single-project, single-writer, file-based CLI workflow supporting one bounded change from understood intent through evidence-backed acceptance, release/hold and a subsequent feedback-driven revision. An existing coding agent can perform the approved task; the system need not generate code or orchestrate agents itself. Reviewable artifacts and honest state are the product's core. Diagnosis alone, a template generator alone, and a selector alone each leave the loop incomplete.

Required commands (proposed interface): `init`, `inspect`, `assess`, `select`, `plan`, `validate`, `packet`, `record-run`, `decide`, `status`, `revise`. Inspection is static/read-only unless separately authorized execution is explicitly requested. Each command receives an expected state revision; mutations are transactional. First runner integration may be a manual handoff/import adapter with execution performed by an existing trusted host. A manual adapter cannot claim that it enforces capabilities; acceptance requires evidence from the enforcing host or the affected execution remains blocked.

Included: greenfield and existing-state intake, pinned registry reference, scoped facts and contradictions, reviewed risk tier, explainable selection/omission, requirements and ADR, task DAG, bounded packet/grant, exact candidate/run evidence, required gate aggregation, human decision, stale invalidation, interrupted resume and release/hold/support disposition. UXEC can be one optional domain contract; it is not required for a headless utility.

Deferred: hosted service/UI, billing/auth product, vector retrieval, autonomous multi-agent scheduling, generalized rule DSL, automatic deployment, broad category expansion, distributed writers, autonomous T3 actions, certification claims and measured productivity promises. Normal project identity controls remain applicable when the target project requires them; these exclusions describe the development-system product, not permission to omit target requirements.

## Demonstration and acceptance

Preregister three distinct cases: a reversible offline CLI change; a small network interface with explicit public/protected scope; a local agent task with no tools, contrasted with one explicitly bounded side effect. Use at least one greenfield case and one brownfield case. Freeze independent acceptance expectations before builder work. SurfaceTrace is optional after these cases and cannot substitute for them.

For each case demonstrate the full loop: intent→risk→selection/rejection→requirements/ADR→task→diff→candidate-bound verification→accepted/held release→feedback→invalidation→revised task. Include a deliberately failed check, missing evidence, scope conflict, stale candidate, interrupted run, budget exhaustion and unauthorized-write attempt. No unsupported capability receives readiness GO. Independently review all mandatory recommendations and rejected controls against facts and source scope.

MVP acceptance requires zero unauthorized actions, zero fabricated/stale PASS decisions, no silently unresolved mandatory feature, no archive mutation, reproducible artifact/registry resolution, detected stale writes and recovery without lost committed events. Any unjustified mandatory component must be resolved before acceptance. Feasibility costs and user comprehension are reported descriptively; no performance target is fabricated. Set time/token/cost limits with the project owner before live trials.

## Phased sequence

| Phase | Deliverable and dependencies | Exit evidence / stop gate |
|---|---|---|
| A — design reconciliation | This checkpoint, after preservation/UX branch; no product code | Independent architecture/policy/contract review, resolve P0 questions; G0/G1. |
| B — parallel prerequisite tracks | B1: separately versioned 003R2 stabilization; B2: contract/state kernel with simulated records and reviewed policies, no production selector wiring | B1 meets unexecuted directive including independent frozen oracle and archive sidecar; B2 passes semantic negative fixtures, crash/replay/stale-write checks. G2/G3. Neither track rewrites frozen files. |
| C — connected planning slice | Intake/inspection, profile/facts/risk, reviewed research mapping, requirements/ADR, task graph and packet; depends on B2 | Deterministic planning with omission/conflict traces; no automatic selector generalization claim. Automatic selection integration additionally requires B1 and G2. |
| D — bounded execution and evidence | Trusted-host adapter, grants, candidate/run import, gate aggregation and independent review; depends on C and approved execution boundary | Unauthorized/path/budget attempts stop; real positive/negative run evidence; G4/G5. |
| E — complete lifecycle pilot | Release/hold, recovery/support record, feedback/change invalidation and interrupted resume; depends on D | Three preregistered cases complete or explicitly block for correct reasons; independent end-to-end disposition, G6. |
| F — scoped expansion | Add ecosystem adapters, UXEC pilot, migration/retirement/data controls only from demonstrated need; depends on E | Each extension gets sources, contracts, independent cases, measured costs and explicit promotion review; G7. |

“Parallel” denotes independent implementation workstreams, not permission to publish or integrate either early. No calendar estimates without actual capacity and scope evidence. Stop at a failed gate, retain the failure, fix the relevant cause and rerun affected checks. Existing authorization for bounded work persists; gate promotion, release and baseline exceptions require the named accountable decision.
