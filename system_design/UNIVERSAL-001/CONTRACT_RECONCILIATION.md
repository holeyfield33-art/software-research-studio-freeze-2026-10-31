# Concurrent architecture and prototype reconciliation

During development of the initial project-packet prototype, the shared branch advanced to `c8d7b032bab3d4299df7c4b5b0b4a7d6d1991d84`, merging PR #2 and `architecture/UNIVERSAL-ARCH-001/`. Both histories are preserved by a normal merge. No remote commit was overwritten.

The merged architecture names itself the canonical candidate design, with acceptance still pending. That design remains the target. `studio_contracts/` is a bounded prototype of semantic checks using **simulated** records, corresponding to its B2 research track; it is not product integration, a live executor, or the G3 acceptance implementation.

| Area | Canonical candidate | Prototype / migration required |
|---|---|---|
| Record envelope | kind, revision, scope, owner, timestamp, derived_from and closed body | type, version, project ID, provenance and data; convert to canonical envelope |
| References | Exact record revision and SHA-256; richer registry provenance | Exact ID/version plus registry partition digest; add record-byte digests and edge/source qualification |
| Gates | PASS/FAIL/INCOMPLETE; omission separate | Five result values; move NOT_APPLICABLE to selection and map missing evidence to INCOMPLETE |
| Evidence PASS | Actual execution, oracle, artifacts, producer and candidate | Checks shape/current candidate and declared origin; a reviewed assertion alone can satisfy prototype rules, so it cannot establish canonical acceptance |
| Authority | Trusted host verifies principal, grantor, action, baseline, expiry and scope | Operator-supplied grant file checks action/path/budget consistency only; no authentication or runtime enforcement |
| State | Transactional events, expected state revision, prior-event digest and replay | In-memory version history and task-event replay; durable concurrency/crash guarantees absent |
| Risk and full lifecycle | RiskAssessment, DesignDecision, DomainContract, ReleaseDecision and snapshots | Requirement/task/evidence/finding core only; do not infer lifecycle completeness |

Useful implemented checks to retain when migrating: malformed typed inputs, unknown/conflicting facts, exact frozen ID resolution, dangling references, task dependency cycles, stale-input propagation, legal task transitions, task/attempt scope and budget consistency, requirement coverage and unresolved finding checks. The 35 unit tests exercise these properties across five synthetic category examples; they do not validate the canonical schema or demonstrate a functioning runtime.

Next: consolidate on the canonical envelope and reference model before adding more record dialects. Use its real Draft 2020-12 validator for structure; port semantic negative cases to canonical fixtures, strengthen PASS evidence to require actual execution and artifact binding, add authority/state-revision checks and durable event tests. Review exceptions, release and incident coverage against canonical requirements. Keep automatic novel selection NO-GO pending the separate selector reliability gate.

The earlier universal design documents and this prototype remain traceable development checkpoints. No claim is made that architecture acceptance, G3, execution authorization or release readiness has passed.
