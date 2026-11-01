# Schema contracts v0.1.0

[contracts.schema.json](contracts.schema.json) is a Draft 2020-12 **candidate design contract** for project records. It does not change the frozen 003R schema. Validate with a real Draft 2020-12 implementation; the mechanical package check uses `jsonschema` with format checking. No stdlib subset is advertised as full conformance. Schema-valid records can still be false or unauthorized; semantic checks below remain mandatory future kernel work.

## Common envelope and reference model

Every entity has `contract_version`, `kind`, project-local `id`, positive integer `revision`, `project_id`, explicit `scope`, `owner`, timestamp, `derived_from` revisioned references, and a kind-specific closed `body`. IDs are not overloaded with research IDs. References carry ID, revision and SHA-256; resolve exact bytes, not latest by default. Registry references also carry checkpoint digest, partition/line, original record/version, edge IDs and source IDs. Missing references produce INCOMPLETE, not a generated replacement.

Hash bytes use UTF-8 without BOM and LF for newly authored canonical JSON. The kernel's proposed canonical JSON representation is sorted object keys, compact separators, finite JSON numbers and no duplicate keys; schemas alone do not enforce this. Frozen file hashes remain raw-byte hashes, never canonicalized. Run artifact digests bind exact raw bytes. Timestamps are metadata; event sequence/revision, not wall clock, controls ordering.

| Kind | Required payload and role |
|---|---|
| ProjectProfile | Goals, users/context, non-goals, constraints, greenfield/brownfield/hybrid mode, baseline locator, component scopes, success criteria. |
| Fact | Predicate, assertion state true/false/unknown, scalar value and unit (null for boolean-only predicates), scope in envelope, origin declared/observed/inferred/unknown, evidence refs. Numeric observations retain units; they do not become booleans. Conflicts remain separate facts until adjudicated. |
| Requirement | Outcome, observable acceptance, priority, acceptance owner and oracle refs; no implication that acceptance has run. |
| RiskAssessment | Dimensions with known/unknown state, consequence/rationale, tier, floor triggers, unresolved inputs and tailoring decisions. |
| SelectionDecision | Rule/policy/input digests, matched fact refs, original registry refs, per-choice disposition, omissions/conflicts/missing inputs and plan status. No execution grant or gate PASS. |
| DesignDecision | Problem, alternatives with conditions/costs/exclusions, chosen option, rationale and review status. |
| DomainContract | Module name/version, file locator/hash and applicability; payload validated with the module's own closed schema. Unknown modules cannot be accepted through this generic wrapper. |
| TaskPacket | Goal, requirement refs, baseline identity, expected state revision, allowed paths/operations, forbidden operations, budgets, dependencies, acceptance oracle refs, grant refs and stop triggers. |
| Authority | Principal, grantor, action, allowed scope, candidate/baseline binding, status requested/declared/granted/denied/revoked, decision evidence and expiry. Typed status is not proof the grantor has authority. |
| EvidenceRun | Candidate identity, packet/oracle refs, command/tool/environment identity, start/end, observed status PASS/FAIL/BLOCKED/NOT_RUN, producer, output artifact digests and limits. Missing execution cannot be PASS. |
| GateDecision | Gate/policy revision, candidate, required run refs, status PASS/FAIL/INCOMPLETE, reasons and reviewer/approval refs. |
| ReleaseDecision | Candidate, required gate refs, APPROVE/HOLD, authority ref, support owner and recovery/distribution disposition. Approval does not itself perform deployment. |
| ChangeEvent | Sequence/expected state revision, prior event digest, actor, changed node refs, invalidation refs and reason. |
| StateSnapshot | State revision, last committed event ref, per-scope status, blockers, current candidate and next task refs. Derived projection, never source of authority. |

Proposed storage: `.development/project/`, `facts/`, `requirements/`, `decisions/`, `contracts/`, `tasks/`, `runs/`, `gates/`, `events/`, `state.json`. Store raw evidence as local artifacts referenced by digest; keep secrets out of packets/log exports with a declared redaction policy. Redacted evidence must state its limits and preserve access-controlled original provenance where appropriate. No storage format implies encryption or secure isolation.

## Semantic invariants required by implementation

1. ID/revision unique; project/scope ownership consistent; no dangling or hash-mismatched references. Registry IDs actually exist; edges active and scope-compatible; source claims support the particular selection. Policy-only synthesis is labeled explicitly and cannot masquerade as sourced guidance.
2. Facts at overlapping scope cannot disagree silently. Structured true does not override denied authority. Unknown has no implicit false value. Free-text/structured contradictions require intake reconciliation when material; free text never authorizes actions.
3. Every mandatory selection has relevant facts, rule version, rationale and source path or approved explicit project-policy basis. Unresolved required capability makes plan INCOMPLETE. INAPPLICABLE requires a scoped omission reason; exclusions conflicting with requirements produce conflict.
4. Every task dependency resolves; hard dependencies form a DAG. Task packet baseline and expected state must match current state. Requested paths cannot escape the workspace by traversal, symlink or alternate path encoding. Trusted host enforces grants, not string matching alone.
5. Authority must be independently authenticated in the trusted host and match principal/action/scope/baseline/expiry. Denied, expired or revoked grants block affected effects. A declared approval or research source is not authorization.
6. PASS evidence requires actual execution, output artifacts, matching candidate and independently defined oracle, complete required checks and known producer/tool/environment. Missing/mismatched evidence yields INCOMPLETE gate decision; actual required failure yields FAIL. Gate authority checks cannot be discharged by the builder's own assertion.
7. APPROVE requires all required applicable gate decisions PASS on the same candidate, current grants, and required support/recovery evidence. HOLD is valid with unresolved evidence. Exceptions do not rewrite historical outcomes.
8. Changed requirements/facts/code/policy/registry invalidate dependent outputs. Superseded evidence stays queryable but cannot count for current readiness. Kernel rejects stale writes by expected revision and handles interrupted commit/replay atomically.
9. Domain modules must pin their schemas/validators and applicable checks. UXEC label strings are not verified frozen references. Existence checks cannot report usability, accessibility or runtime behavior PASS.

The schema encodes shape, closed fields, vocabularies and selected local conditions. These nine invariants require a semantic validator and trusted execution/review integration, which are outside this design checkpoint. Mechanical checks of the schema and illustrative fixtures must not be reported as an implemented development system.

## Versioning and compatibility

Reject unknown major contract versions and unsupported kind/module versions. Additive optional fields still require a declared schema update because objects are closed. Migrate in a new namespace/revision with old/new digests, migration rationale and owner decision; preserve originals and references. Changes to outcome vocabularies or meaning require explicit migration tests. Never migrate frozen corpus IDs into `ua.*`, or reinterpret report-local UX IDs as frozen knowledge.
