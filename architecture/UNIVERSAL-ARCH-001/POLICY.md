# Proposed risk and research-selection policy v0.1.0

These tiers are design synthesis, pending independent calibration. They are not NIST/ISO classifications and imply no certification. Risk attaches to component, change and action; project summary reports the highest applicable tier and unresolved dimensions. Complexity and risk are separate: a short destructive script can require more rigor than a large read-only prototype.

## Risk dimensions and tier floors

Record severity, exposure, reversibility, data sensitivity, privilege, user/operational dependence, external side effects, novelty, and uncertainty with evidence and accountable owner. Do not average high impact away. Unknown consequential dimensions block the affected action; a provisional tier may guide research but cannot authorize execution. Effort/cost tailors artifact depth within the floor, never overrides a blocking safety condition.

| Tier | Trigger/floor | Minimum rigor beyond shared kernel |
|---|---|---|
| T0 contained | All relevant dimensions known: disposable/local, reversible, no sensitive data, no external writes, no dependent users | One concise change packet may hold scope, criterion, decision and evidence; focused behavioral check, inspectable diff, recovery by discard. |
| T1 ordinary | Maintained tool/product or bounded user-facing change; consequences recoverable and below T2/T3 | Versioned requirements/ADR where choices matter, regression evidence for affected behavior, review by project policy, compatibility and support/release disposition. |
| T2 consequential | Sensitive data; meaningful external writes; identity/tenant boundary; difficult recovery; public exposed control boundary; materially costly operational dependence | Scoped threat/risk review, action-specific authority, independent acceptance oracle and review, required negative/recovery checks, dependency/provenance and release evidence where applicable. |
| T3 critical | Plausible severe physical harm, systemic financial/data loss, critical infrastructure function, or applicable high-assurance obligation | Qualified domain authority, explicit assurance plan, independent verification/release review, validated recovery and applicable normative evidence. Automated autonomous execution is outside MVP. |

An authorized expert can tailor T3 controls; this system cannot infer regulatory applicability from a product label. A security product is not automatically T3; an agent without tools does not automatically require write controls. A static website need not become T2 merely because users can read it: assess assets and exposed control boundaries. The floor is chosen from concrete consequences, not category names.

Shared kernel for all tiers: scoped goal and non-goals, owner, versioned inputs/candidate, observable acceptance, record/source resolution, explicit uncertainty, truthful run results, bounded authorization, change history, and release/hold disposition. Applicable checks can be co-located in a small packet. Formal state machines, full threat workshops, deployment services and dashboards remain conditional.

## Selection algorithm and precedence

1. Validate full typed input before dereferencing facts. Reject malformed JSON/types as `INPUT_SCHEMA_INVALID`; no partial positive decision or unhandled traceback.
2. Normalize scopes and detect incompatible facts at the same or overlapping scope. Identity/auth and destructive-write/authority contradictions require reconciliation. Mixed public/private endpoints need distinct scopes; never flatten them silently.
3. Apply explicit exclusions and authority constraints. A feature excluded by intent is INAPPLICABLE; if excluding it conflicts with a required outcome/control, emit `REQUIREMENT_EXCLUSION_CONFLICT` and INCOMPLETE rather than silently dropping either side. A source or category cannot override intent or grant authority.
4. Establish risk floor and evidence sufficiency. Unknown critical facts generate targeted questions/research tasks. Keep unaffected work available when dependencies permit.
5. Retrieve candidate records via active typed applicability edges. Evaluate executable predicates over exact fact revisions and source limitations. For unsupported/un-calibrated branches return INCOMPLETE or explicitly optional guidance for human review; do not claim reliable automatic selection.
6. Emit every considered choice as RECOMMENDED, CONDITIONAL, INAPPLICABLE or INCOMPLETE with matched predicates, current missing/conflicting facts, rejected alternatives and original source/edge paths. No stale missing-fact reason survives resolution.
7. Derive required artifacts, task dependencies and gate plans from the chosen facts/requirements; verify each mandatory dependency and detect task cycles. Do not infer mandatory work from profile lists alone.
8. Produce separate `plan_status` COMPLETE/INCOMPLETE, action authority GRANTED/DENIED/UNKNOWN, and gate decisions. Plan COMPLETE means selection is internally resolved for its declared scope, not that work is accepted or released.

Deterministic ordering: priority then stable rule ID, then record ID. Equal-priority incompatible effects produce an explicit conflict, not last-write-wins. Unknown ≠ false. A newer registry/policy version requires reevaluation; never silently swap versions. Simple predicates/functions plus tests suffice; no DSL or general policy platform in the MVP.

## Concrete conditional rules

| Concern | Select when | Omit / hold when | Frozen basis |
|---|---|---|---|
| Queue | Explicit async/durability/load need, justified option and named operations owner | Absent need: omit; owner unknown: missing-owner reason only; both known: remove that reason, assess remaining trade-offs | `R-API-003`, `arch.event_queue`; E04/E05 defect remains unresolved in frozen code |
| Authentication | Scoped identity requirement, protected action or justified control | Public read-only/no protected assets: omit account system; conflicting identity facts: hold | `R-API-AUTH-001`, `R-INPUT-001` |
| Tenant isolation | Explicit shared tenancy/isolation need and known mapping | Category alone: omit; mapping unknown: conditional design, no readiness | `R-API-002`, `arch.multitenancy_isolation` |
| Tool/write controls | Actual capability or possible side effect | No tools/side effects: omit tool controls; no authority: block write, allow separately authorized read-only work | `R-AGENT-001/002/003`, `arch.agent_tool_boundary` |
| Packaging/release | Intended delivery/distribution | Local exploratory run does not require hosted deployment | `R-CLI-002`, `R-RELEASE-001` |
| UXEC/accessibility | Human interaction surface and relevant user needs/platform | Headless task: omit UI contracts; inspect actual context before choosing checks | E08/E10/E12, design extension outside frozen registry |
| Formal state model | Transition complexity, concurrency or failure consequence justifies it | Simple local behavior can use examples and explicit assertions | E08 D06; new calibration required |
| Standards controls | Exact edition/scope and organizational/legal adoption established | Catalog summary alone yields applicability question, never conformance | `R-STANDARD-001`, source limitations |

## Required calibration before automatic use

Retain original 13-case oracle unmodified; independently author and freeze at least the eight 003R2 combinations before fixes, including malformed input, no-tool agent, cross-field conflicts, justified queue and tenant transition. Preserve `EVIDENCE_UNAVAILABLE` where authoritative approval proof is absent. Add counterfactuals for each tier floor, exclusion conflict, equal-priority conflict and uncalibrated category. Test unrelated-fact invariance, true→false→unknown transitions, resolved-reason removal, superseded-edge exclusion and repeatable output. Original tests passing alone cannot promote generalization GO.
