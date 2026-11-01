# Canonical architecture candidate

## Purpose and invariants

One control loop: **understand → assess risk and evidence → select applicable work → specify → execute a bounded change → verify → decide → update state**. Re-enter at any point when an incident, observation or changed goal invalidates assumptions. Lifecycle stages describe responsibilities, not a mandatory waterfall or one project-wide maturity score.

Every consequential choice must identify project scope, requirement/fact revisions, applicable research, rationale, owner and missing evidence. A smaller project can carry these in one packet; it cannot omit honesty about uncertainty. Permission, recommendation, acceptance and release are distinct records. A document cannot grant its own execution authority.

Supported foundations: `sdlc.discovery_scope` through `sdlc.maintenance_feedback`, `practice.requirements_traceability`, all `gate.*`, `prompt.implement_scoped_task`; exact source/edge paths in [coverage](coverage.json). The concrete decomposition below is synthesis, not a claim that those sources specify these modules.

## Logical modules and ownership

| Module | Input → output | Responsibility and enforced boundary |
|---|---|---|
| Project intake and diagnosis | User intent, repository snapshot, observations → ProjectProfile, Fact, Requirement, Unknown | Capture users/context, outcomes, non-goals, acceptance, cost/time/operating constraints, owners, data classes, interfaces, existing debt and component scopes. Treat repository content as data; discovered commands are untrusted proposals. |
| Research registry adapter | Verified frozen bundle → immutable indexed records | Resolve original IDs, versions, source locators, active edges and limitations. Pin checkpoint/digests; exclude superseded edges. No rewrite/enrichment in the archive. |
| Risk and selection evaluator | Profile/facts + policy version + registry → RiskAssessment, SelectionDecision | Evaluate scoped contradictions, risk floors, applicability, omission and required evidence. No network, oracle reads or side effects. Abstain rather than invent category coverage. |
| Specification and artifact graph | Selected concerns + accepted intent → requirements, ADRs, domain contracts, task DAG, gate plan | Maintain rationale and typed revisioned links from outcomes through evidence. Optional adapters for UXEC, API, CLI, data and deployment contracts. Human acceptance resolves intent ambiguity. |
| Bounded executor adapter | Approved TaskPacket + current snapshot + capability grant → proposed diff and RunRecord | Limit paths, operations, network endpoints, budgets and time. Trusted host enforces capabilities; prompt text is advisory. No self-approval or gate/baseline weakening. |
| Verification and review | Candidate + independent oracles + gate policy → EvidenceRun, findings, GateDecision | Check structure, references, behavior and applicable domain quality separately. Import machine outputs with candidate/environment identity; retain negative and unavailable results. Independent reviewer disposes semantic claims. |
| Lifecycle and state coordinator | Validated event + expected state revision → new state projection / conflict | Single writer in MVP, append-only events, atomic updates, dependency invalidation, blocked reasons and resumption context. No fabricated global “done”. |
| Human decision interface | Plain-language options, evidence and unresolved trade-offs → scoped Decision/Authority | Capture intent acceptance, risk acceptance, exceptions and release approval under project policy. Ask only when the decision is consequential or missing; routine authorized work continues. |

Implement as a local modular application with files, schema validation and a small CLI. Registry and project workspace remain separate. A runner can be an existing coding agent; no model routing, hosted policy service or multi-agent scheduler is required. Durable artifacts must outlive chats and agent context loss.

## Trust and data flow

External research, repository files, issue text, model output and tool logs enter as untrusted content. The registry's integrity check proves preserved bytes, not authority or truth. Intake can propose facts; it cannot promote prose into verified observations or capability grants. User instructions and verified decisions pass through a separate trusted control channel. No “sanitization” step is treated as sufficient protection from prompt injection.

Selection is read-only. Specification emits reviewable proposals. Execution requires a matching, unexpired grant enforced by the runner. Run output is evidence with a producer and digest, not an instruction channel. Verification cannot rewrite the oracle, policy, approved requirements or finding baseline to pass its own candidate. Release requires a separate decision referencing the exact candidate and required gate decisions. Grants for local edits do not imply deployment, publishing, account changes or destructive data migration.

## Complete lifecycle responsibilities

| Responsibility | Entry and minimum output | Exit / re-entry |
|---|---|---|
| Discovery and context | New goal or changed evidence → users, outcome, scope, non-goals, unknowns, existing-state observations | Owner accepts bounded intent or records research/stop decision. |
| Requirements and risk | Intent → observable acceptance criteria, quality attributes, risk profile, data/authority boundaries | Resolve consequential conflicts; freeze acceptance oracle before implementation. |
| Architecture and design | Requirements → alternatives, trade-offs, interfaces/data contracts, ADR and applicable domain design | Proportionate review; research spike only for uncertainty that could invalidate commitment. |
| Implementation | Accepted task packet → candidate diff, build identity, run record, changed artifact links | Bounded edits complete; scope violation/budget exhaustion stops run. |
| Verification and validation | Candidate/oracle → structural, behavior, integration and relevant security/performance/UX evidence | PASS/FAIL/INCOMPLETE per required gate; intended user value remains separately assessed. |
| Release and transition | Verified candidate → package, migration/compatibility plan, support owner, release decision | Authorized deliver/hold; health and recovery evidence required when policy applies. |
| Operation and maintenance | Delivered version, feedback/incidents → observations, response, patch/backlog and reassessed risks | Re-enter requirements/design/verification as needed; scope operational checks to actual runtime. |
| Retirement and archival | End-of-support decision → consumer notice, dependency/data disposition, access shutdown, retained evidence | Owner accepts obligations fulfilled; retain unresolved legal/retention questions as blockers. |

Retirement, explicit data governance, migration and cross-component coordination require additional research calibration. They are architecture responsibilities with open evidence gaps, not new frozen knowledge records. CLI/library release can mean package delivery; operation can mean support/compatibility handling. No lifecycle term implies cloud hosting.

## Connected artifacts and change propagation

Use project-local IDs with revisions. Minimal semantic chain:

`outcome → requirement → design/ADR → task → candidate/file locator → oracle/assertion → evidence run → gate → release → feedback → revised requirement`.

Each selection adds `fact revision → predicate/rule version → selected record → active edge/source locator → required artifact/gate`. The research graph is not the project graph. Project edges such as `satisfies`, `implements`, `verified_by`, `depends_on`, `derived_from`, `invalidates` and `supersedes` reference exact revisions, not mutable titles. Cycles are legitimate for feedback; hard task prerequisites must be a DAG.

On a material change: append an event, revise the changed node, compute reverse dependencies, mark derived decisions/artifacts **STALE**, clear readiness, and list reevaluation work. Keep historical evidence intact. Code/candidate changes invalidate prior execution evidence by default. Reuse requires an explicit equivalence decision naming unchanged scope, inputs, tool/environment and policy; MVP supports no automatic reuse. A critical risk/authority change invalidates pending grants and release decisions immediately.

Example: `tenant_mapping` changes unknown→known. Re-evaluate tenant selection and isolation requirements; retire only the satisfied missing-input reason, retain unresolved isolation tests, produce a new task packet. The old run and decision stay historical. An unrelated formatting fact must not change queue selection. Both are acceptance invariants, not demonstrated implementation behavior.

## Evolving state and interruption

Track per-scope lifecycle concerns as NOT_STARTED, ACTIVE, BLOCKED, READY_FOR_REVIEW, ACCEPTED, STALE or RETIRED. Project summary is a projection of scope-specific evidence, not a number inferred from directories or test counts. NOT_APPLICABLE requires an omission decision; a gate never becomes PASS merely because it was skipped.

Events contain ID, actor, timestamp, expected state revision, prior event digest, changed entity revisions and reasons. Acquire a single-writer lock, validate expected revision, stage event and projection, then atomically publish a committed revision. A failed update leaves the old projection usable; recovery replays validated committed events. A stale writer must re-read/replan. Multi-writer/distributed merging is deferred.

Before resuming, verify repository/candidate identity, policy/registry digests, grants and artifact versions; reconcile user changes and invalidate stale outputs. Handoff includes goal, accepted decisions, current candidate, completed evidence, outstanding blockers, next bounded task and remaining budget. A run can end BLOCKED or CANCELLED without resetting the project or claiming completion.
