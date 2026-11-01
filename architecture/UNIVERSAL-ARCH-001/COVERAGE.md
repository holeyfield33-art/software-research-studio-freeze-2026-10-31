# Coverage and gap matrix

Coverage means research is available for a concern; it does not mean working product capability. All rows below are proposed design. Exact original record IDs, source locators, raw hashes and active edge IDs are available in [coverage.json](coverage.json) and [evidence-index.json](evidence-index.json). Frozen classifications and limitations remain visible there. Research summaries were not upgraded to independent execution evidence.

| Concern | Preserved support | Coverage / material gap | Design response / priority |
|---|---|---|---|
| Project intent and existing-state understanding | `sdlc.discovery_scope`, `sdlc.requirements_risk`; E09 | General guidance; no complete project profile, domain/user model, mixed-scope diagnosis or truth adjudication | Versioned profile, scoped facts, owner acceptance and observation provenance; P0 |
| Full lifecycle | Seven `sdlc.*` records | Discovery→maintenance represented; retirement, transition and data disposition lack dedicated calibrated coverage | Iterative responsibilities plus explicit retirement gap; P1 research before consequential use |
| Risk adaptation | `practice.threat_modeling`, `roadmap.risk_first_poc`, scoped source limitations | No calibrated universal tier rubric or cost model | Proposed tiers/floors, unknown handling and tailoring decisions; P0 review |
| Research selection | `R-*`, active `applies_to`/`supported_by` graph, E03–E05 | Known novel-input defects; seven types NOT_CALIBRATED | Independent stabilization lane and no integration GO until passed; P0 |
| Requirements and traceability | `practice.requirements_traceability`, `gate.requirements_acceptance` | Typed research graph is not requirement→task→assertion→run linkage | Project artifact graph, revision checks and semantic review; P0 |
| Architecture decisions | Six `arch.*` records | No universal option evaluator; source scopes differ and trade-offs are mostly qualitative | Alternatives with conditions/costs/exclusions and ADR; P1 |
| UX and accessibility | E08/E10–E12 | Candidate contracts, disputed invented frozen IDs, no verified implementation or benefit | Optional UXEC module with resolved references and independent behavior/manual evidence; P1 |
| Bounded implementation | Six `prompt.*` records, `arch.agent_tool_boundary` | Prompts cannot enforce capability limits; no trusted runner demonstrated | Task packet, host-enforced grant, budget/stop, diff and evidence import; P0 |
| Verification and acceptance | Six `gate.*`, five `verified_by` edges, E12 | No product verifier; links, test files and schemas do not establish behavior | Separate structural/behavior/domain/human gates, candidate-bound runs and oracles; P0 |
| Release and supply chain | `sdlc.release`, `practice.ci_reproducible_release`, `gate.dependency_provenance` | Pinned CI files are observed configuration only; ecosystem packaging and migration coverage limited | Release or hold, provenance/compatibility/recovery checks selected by scope; P1 |
| Operations and feedback | `sdlc.maintenance_feedback`, `practice.observability_incident`, `gate.operational_rollback` | Monitoring ownership/SLO and incident/runbook completeness not calibrated | Support/operations plan, incident facts and corrective backlog; P1 |
| Evolving state and drift | `practice.change_maintenance`, E08/E09 | No tested state store, concurrency, invalidation or interruption protocol | Revisioned events, single writer, stale marking and resume reconciliation; P0 |
| Domain quality and data | `practice.test_strategy`, source/type overviews | Performance, reliability, privacy, retention, migration and domain hazard controls not complete | Quality-attribute registry and explicit specialist review; P1/P2 scoped research |
| Broad universality | Ten type records, three narrow fixtures | Seven types uncalibrated; composite projects and noncatalog types unsupported | Extensible typed modules; abstain on automatic inference; cross-case validation before claims; P0 claim boundary |

Corpus snapshot: 10 software types, 7 lifecycle stages, 8 practices, 6 architectures, 6 prompts, 3 roadmaps, 6 gates, 3 references, 65 sources, 601 edges. Predicates: 307 `applies_to`, 52 `exemplified_by`, 58 `informs`, 26 `requires`, 153 `supported_by`, 5 `verified_by`; three `exemplified_by` edges superseded. No `produces` or `implemented_with` edges are instantiated, although the schema allows them. This limits derivation coverage; adding project graph edges here does not modify or repair the research graph.

Calibration remains narrow for `software_type.ai_agents`, `software_type.apis`, `software_type.cli_tools`. The other seven types remain NOT_CALIBRATED. Composite projects are assessed per component and cross-boundary change; a supported API fixture does not calibrate an entire SaaS product.

P0 means architecture/MVP acceptance blocker; P1 means required before use in affected scope; P2 means extension work justified by actual demand. A gap can remain outside MVP only if the system reports the unsupported scope and prevents a false readiness claim.
