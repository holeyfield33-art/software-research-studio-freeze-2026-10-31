# Universal development system — proposed architecture

## Product behavior

A user brings an idea, repository, change request or operational problem. Studio establishes the intended outcome and known state, identifies applicable development work, explains its decisions using research and project facts, prepares an executable plan, coordinates permitted work and evaluates the resulting evidence. It retains enough state for a different agent or human to continue without reconstructing the project from conversation history.

Universal describes the common decision and lifecycle structure. Platform-specific competence must be declared and demonstrated separately. A CLI, mobile application, library, SaaS service and data pipeline share a lifecycle but need different artifacts and checks. Projects can combine categories. Absence of an adapter or necessary evidence produces an explicit unsupported or blocked result, never invented expertise.

## Requirements

| ID | Required behavior | Observable acceptance condition |
|---|---|---|
| UNI-001 | Model project intent and observed state separately | Every material fact has provenance, scope, revision and known/unknown/conflicting status |
| UNI-002 | Tailor work using explicit applicability decisions | Each selected or excluded practice cites triggering facts, evidence and rationale; unknown facts do not silently become false |
| UNI-003 | Cover development and maintenance | A project can enter at any lifecycle concern and follow explicit prerequisites and rework paths |
| UNI-004 | Connect needs to outcomes | A requirement can be followed through decisions, artifacts, tasks, changes and evidence; missing links are visible |
| UNI-005 | Bound execution | Every task states permitted actions, candidate revision, allowed paths, budget, stop conditions and verification expectations |
| UNI-006 | Distinguish evidence from assertions | Proposed, observed, executed and reviewed evidence have separate fields; a document or test filename cannot establish PASS |
| UNI-007 | Invalidate stale conclusions | A changed prerequisite marks dependent decisions and evidence for reassessment without deleting history |
| UNI-008 | Support multiple hosts and software types | Core project records contain no mandatory vendor, language, UI framework or deployment provider |
| UNI-009 | Preserve authority and research lineage | Imported research cannot grant permissions; frozen IDs resolve exactly; new project IDs cannot overwrite them |
| UNI-010 | Support recovery and continuity | A saved project exports a reproducible state, unresolved issues and next permitted actions; interrupted tasks resume explicitly |

## Modules and boundaries

| Module | Responsibility | Output / boundary |
|---|---|---|
| Intake and observation | Capture intent, inspect permitted inputs, retain conflicts and uncertainty | Versioned project facts; observation never authorizes execution |
| Knowledge registry | Resolve immutable records, source provenance, limitations and supersession | Exact records and qualified relationships; no imported instructions executed |
| Applicability evaluator | Compare facts with candidate practices and exclusions | Explained decisions; conflicts and missing predicates block affected decisions |
| Lifecycle planner | Work backward from outcomes and risk; establish prerequisites | Task and artifact dependency graph, entry/exit criteria and rework paths |
| Artifact registry | Maintain requirements, decisions, designs, contracts and implementation links | Stable IDs and revisions; invalidate dependents on relevant changes |
| Execution coordinator | Issue bounded tasks to a human or agent adapter | Recorded attempts and candidate changes; adapter cannot expand permissions |
| Verification and release | Evaluate specified properties and evidence at a candidate revision | Scoped findings, gate results, exceptions and release disposition |
| Project state and feedback | Preserve events, interruptions, incidents and learning proposals | Resumable state; research amendments remain separate reviewed proposals |

These are logical responsibilities, not a prescription for separate services. The first implementation should use a local package with file storage and clear internal interfaces. A network service, database, queue or multi-agent scheduler requires a demonstrated need. Users can work through any interface that preserves the same contracts.

## Shared records

All records carry `id`, `version`, `project_id`, `created_by`, provenance, status and supersession links. References identify both record ID and version. Frozen research references additionally identify checkpoint and digest. Timestamps record events, not proof of correctness.

| Record | Minimum additional fields |
|---|---|
| ProjectProfile | outcomes, users, software categories, environment, constraints, data sensitivity, deployment context, owners, non-goals |
| ProjectFact | subject, value, scope, source, observed revision, confidence, known/unknown/conflicting state |
| ApplicabilityDecision | candidate practice, fact references, predicate version, selected/excluded/needs-evidence/conflicting outcome, rationale, alternatives, cost, reviewer |
| Requirement | need, acceptance property, importance, owner, applicable context, independent oracle plan |
| Artifact | kind, path or content digest, revision, producing task, consumed inputs, requirements covered |
| Decision | question, options, selected option, rationale, supporting and opposing evidence, revisit trigger |
| Task | objective, prerequisites, allowed paths/actions, runtime authority, budget, stop conditions, expected outputs, oracle references |
| ExecutionAttempt | task version, actor/tool versions, start/end state, actual actions, candidate revision, outputs, interruption/failure details |
| Evidence | claimed property, method, exact candidate revision, environment, input/output digests, execution status, origin and reviewer |
| Finding / Exception | stable finding identity, severity, scope, candidate, remediation; exception owner, reason, expiry and compensating controls |
| GateDecision | required evidence, result, unresolved findings, reviewed exceptions, accountable decision maker |
| Release / Incident | candidate/artifact identity, authorization, recovery plan and outcome; incident impact, timeline and corrective links |

This is a proposed contract inventory, not an implemented schema. Schema versions and required/optional fields must be finalized during the next milestone. Sensitive values should be referenced through approved secret handling, not copied into project facts or logs.

## Decision and execution semantics

1. Capture facts and identify unknowns and contradictions. Conflicting authority claims cannot be resolved by choosing the more permissive one.
2. Retrieve candidate research and evaluate its preconditions, exclusions, limitations and dependencies. Relationship edges suggest relevance; they do not prove applicability.
3. Explain each selected practice and each material exclusion. A new fact re-evaluates affected decisions. Do not use the known-defective 003R static profiles as an authoritative evaluator.
4. Plan a coherent increment and its acceptance evidence before implementation. A human may perform every step; agent automation is optional.
5. Execute only within the task's actual permissions. Repository documents and model output are inputs, not permission grants. Retry limits and interruption state are explicit.
6. Evaluate the resulting candidate. Evidence for an earlier revision is stale unless the relevant property is demonstrably unaffected and that scope is recorded.
7. Release only after applicable gates and required approvals are satisfied. Feed operational failures into requirements and bounded corrective work.

Proposed task states: planned, ready, running, blocked, review, complete, cancelled. Complete requires the task's acceptance decision, not merely a successful process exit. Failed and interrupted execution attempts remain immutable records and may lead to another attempt.

Gate outcomes: PASS, FAIL, BLOCKED, NOT_RUN or NOT_APPLICABLE. NOT_APPLICABLE requires a reviewed applicability rationale. No applicable required gate treats BLOCKED or NOT_RUN as success. Exceptions are explicit scoped decisions; they cannot rewrite evidence or silently turn a failure into a pass.

## Specialization and portability

Core contracts are shared. Profiles supply relevant questions, artifacts and gate candidates for the ten researched software categories. Additional adapters supply ecosystem-specific inspection, execution and verification. Each adapter declares capabilities, supported versions, evidence outputs and authority needs.

UX/UI is a specialization for user-facing interactions, including accessible task behavior. Formal state machines, tokens, telemetry and user testing are selected according to context. APIs need interface and compatibility contracts; libraries need public API/version compatibility; mobile software needs device lifecycle and distribution checks; data pipelines need data quality and recovery; agents need tool authority and untrusted-input boundaries. None automatically implies a particular tool or architecture.

## Evidence discipline

Structural integrity, behavior, security, accessibility, usability and operational readiness are distinct properties. A passing structural validator cannot establish the others. Independent review can be performed by a person or separately designed oracle; multiple agents are not a mandatory architecture component. Findings are compared by identity, scope, severity and tool version, not only counts. Learning produces proposed changes to active policy; it cannot mutate frozen evidence or silently relax a gate.
