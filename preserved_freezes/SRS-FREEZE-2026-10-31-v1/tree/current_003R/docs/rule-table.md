# 003R deterministic selection rules

Rules version **1.0.0**. Precedence is safety-first and follows priority descending. Unknown remains distinct from false; explicit exclusions suppress inferred defaults.

| Priority | Stable rule ID | Name | Predicate | Effect |
|---:|---|---|---|---|
| 1000 | `R-INPUT-001` | Contradictory or malformed facts abstain | Duplicate fact_id with incompatible state, malformed contract, or incompatible authority/evidence tuple | Return INCOMPLETE; enumerate conflict IDs; do not emit positive recommendations based on disputed facts. |
| 950 | `R-CATEGORY-001` | Calibrated category boundary | A requested software_type_id is unknown or not in the calibrated list | Emit INCOMPLETE for that category branch; do not infer category-derived features or service components. |
| 900 | `R-EXCLUSION-001` | Explicit feature exclusions dominate defaults | A feature fact is explicitly false, or a category alone is the only basis for the feature | Emit INAPPLICABLE; exclude the feature and its architecture/service patterns. |
| 850 | `R-AUTHORITY-001` | No authority, no high-impact side effect | Write/destructive action is requested but scope authorization, accountable approver or action-specific approval is false/unknown | Emit INCOMPLETE; disallow execution/authorization; state a safe read-only or non-destructive interim and required authority evidence. |
| 800 | `R-EVIDENCE-001` | Candidate-bound gates cannot pass on authored source | Candidate identity, linked run record, candidate match, required approval or executed result is absent | Gate status stays INCOMPLETE; PASS is not an available output value. |
| 780 | `R-STANDARD-001` | Standard edition and adoption boundary | Requested edition differs from catalog-current edition or organization adoption is unknown | Emit INCOMPLETE/CONDITIONAL with exact catalog locator; do not assert normative applicability or compliance. |
| 700 | `R-AGENT-001` | Untrusted agent input requires boundary design | AI-agent type and untrusted input, tool use or possible side effect is true | Select bounded tool-boundary and threat-model work; model output and external content are not authority. |
| 700 | `R-API-001` | Network API boundary follows explicit API scope | API type and network_api true | Select API boundary design; auth only when explicit auth/user/role facts require it. |
| 700 | `R-CLI-001` | Offline local-file CLI scope | CLI type and local_filesystem_input true with offline_only true | Select local input/output/exit contract and non-destructive file tests; reject network/account/tenant/service obligations when explicitly false. |
| 695 | `R-API-AUTH-001` | Authentication follows explicit identity requirements | authenticated_users, authentication_required and role_based_authorization are false for a public read-only API | Mark authentication feature INAPPLICABLE; do not add auth middleware or account model by default. |
| 690 | `R-AGENT-002` | Bounded-write agent needs per-action controls | Write-capable tool or side effect is true | Select authorization/approval design; absent accountable approver makes write path INCOMPLETE and unauthorized. |
| 690 | `R-API-002` | Tenant isolation follows explicit tenant requirement | multi_tenant or tenant_isolation_required true | Select tenant-isolation design CONDITIONALLY pending mapping, threat, recovery and isolation evidence; never infer from API/SaaS category. |
| 690 | `R-CLI-002` | CLI conditional dependency, upload and distribution controls | Dependency, network upload or distribution fact is requested or unknown | Keep packaging/upload conditional until target, authorization, data scope and dependencies are known; never add service deployment solely from distribution. |
| 680 | `R-AGENT-003` | No write capability means no write-approval obligation | Write tool and side effects are explicitly false | Mark high-impact write action INAPPLICABLE; retain only read-scoped allowlisted tool design. |
| 680 | `R-API-003` | Queue requires operational justification | Queue requested but load/durability justification or accountable operations owner false/unknown | Do not recommend broker; retain queue as INCOMPLETE/CONDITIONAL and list evidence needed. |
| 670 | `R-API-004` | Network API risk review | Authenticated or publicly reachable API is in scope | Select scoped threat/risk review; do not equate it to a passed security gate. |
| 500 | `R-BASE-001` | Core lifecycle plan | Category is calibrated and facts are not contradictory | Select applicable discovery, requirements/risk, architecture, implementation and verification stages; add release planning only when explicitly required. |
| 495 | `R-RELEASE-001` | Release planning is not release authorization | Release plan explicitly required | Select release planning only; release readiness remains INCOMPLETE without candidate-bound execution evidence and approval. |
| 490 | `R-TYPE-BASE-001` | Use category as scope, not feature inference | Requested type is calibrated and each emitted record has an active typed applicability edge | Select type overview as scoped context; do not infer database, tenancy, cloud, Kubernetes, billing or vector search. |
| 480 | `R-ARCH-001` | Architecture patterns are options bounded by facts | An architecture record is applicable through an active typed edge and all explicit exclusions are respected | Select only applicable architecture options; include trade-offs and missing design inputs; no mandatory unrequested component. |
| 470 | `R-PRACTICE-001` | Core practice scope | Practice is applicable to type and supports a stated requirement or baseline quality obligation | Select requirements traceability/change review only within its applicability and mark unresolved candidate-specific work incomplete. |
| 465 | `R-PRACTICE-002` | Verification plan is not execution | A test strategy is applicable | Select test plan and evidence needs; never claim a run or a pass without linked candidate-specific execution evidence. |
| 460 | `R-ROADMAP-001` | Dependency-aware roadmap | A calibrated project needs staged work | Use risk-first ordering for material agent/tool uncertainty; otherwise smallest increment plus dependency-aware sequence. Preserve typed task dependencies; do not invent calendar estimates. |
| 450 | `R-PROMPT-001` | Prompt contract is scoped and evidence-aware | A prompt record is applicable to a selected task | Use scoped implementation/test/review contracts; prompts cannot authorize side effects or claim tests passed. |
| 300 | `R-EXAMPLE-001` | Reference project is a scoped example | A pinned example exists for the calibrated type and example use is requested | Select as contextual evidence only; pin commit, paths and source locators; do not treat test files or CI configuration as execution. |
| 200 | `R-SCOPE-001` | Applicability mismatch abstains | No active typed edge supports requested category-to-record or record-to-source path | Reject the claim as INAPPLICABLE/INCOMPLETE; never substitute a broad category label for evidence. |

## Scoped source exclusions

- `source.mobile_applications.01` may support only `software_type.mobile_applications`. For other types, the selector records `SOURCE_STACK_SCOPE_MISMATCH` under `R-SCOPE-001`: The source locator concerns Android/native mobile application architecture and is not evidence for an API-specific claim.

## Deterministic tie handling

The selector uses fixed rule order, sorted record IDs, stable relationship IDs, and lexicographically ordered ready roadmap tasks. It does not call an LLM, access the network, read expected/golden outputs, or write into the dataset.
