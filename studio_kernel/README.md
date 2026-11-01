# Canonical Studio kernel — initial implementation

> **Agent intake/report routing:** Before evaluating a repository or interpreting an external checkpoint update, read [the universal agent intake contract](../docs/AGENT_INTAKE.md) and [the agent entrypoint](../AGENTS.md). The kernel does not choose a report type from a repository URL; default to a universal project assessment unless another deliverable is explicitly requested. No linked-product registration is implied.

This module targets the existing `architecture/UNIVERSAL-ARCH-001/contracts.schema.json` directly. No new record dialect is introduced. The old `studio_contracts/` prototype remains a historical experiment; new kernel work belongs here. The architecture remains a candidate, and broader acceptance gates remain pending.

Connected planning is now available through `python -m studio_kernel plan`; see `PLANNING.md` for the intake contract, reviewed risk/selection boundary, five synthetic examples and history handoff. Planning creates proposals, never execution permission.

Signed evidence import and task acceptance are now available through `import-evidence` and `accept`; see `EVIDENCE.md` for public-key trust configuration, proof retention, review binding and limits. This supplies a concrete receipt-verification integration; a real enforcing/signing host adapter remains to be built.

## What works

- Full declared Draft 2020-12 structural validation through `jsonschema` with format checking, using the canonical candidate schema unchanged.
- Deterministic UTF-8 canonical JSON with LF terminator, sorted keys, compact separators, no non-finite numbers and duplicate-key rejection on import. Record references bind exact ID, revision and canonical-byte SHA-256. Frozen records keep their original raw-byte digests.
- Exact reference resolution, retained version history, consistent project identity, typed task/run/gate/release links, dependency checks and transitive invalidation after input or candidate changes.
- Structured conflicts at overlapping fact scopes, unknown-value handling, registry checkpoint/partition/line/ID/version checks and source/edge membership checks. These do not prove source relevance, narrative truth or applicability-predicate correctness.
- Actual output file hash verification, execution-shape/timestamp checks, gate aggregation, candidate matching and conservative release approval checks.
- Separate trusted-host callbacks for authority verification, execution/oracle verification and release review. Without these, affected readiness is INCOMPLETE and effective release disposition is HOLD. A GRANTED field or builder-authored PASS is not sufficient.
- Immutable local record/event history, expected-revision write protection, atomic commits, replay, history-chain verification and derived snapshots.

The kernel records and evaluates declarations and evidence. It does **not** execute project commands, deploy software, authenticate users or enforce process capabilities. Tests use synthetic host callbacks and fixtures, not live approval or proof of independent execution. A trusted integration must authenticate receipts and bind them to exact records; passing `lambda: True` is only a test stub, never a production verifier.

## Use

Python 3.10+ with the pinned packages in `requirements.txt`. Run from repository root:

```text
python -m unittest studio_kernel.test_kernel -v
python -m studio_kernel validate records.json --project my-project --candidate candidate.json --artifacts path/to/evidence
python -m studio_kernel record records.json --project my-project --store path/to/history.sqlite --expected 0 --candidate candidate.json --actor operator --reason "Initial reviewed import"
python -m studio_kernel status --project my-project --store path/to/history.sqlite
```

`records.json` is a list of canonical schema entities. `candidate.json` contains `identity` and `sha256`. Candidate identity is supplied by the operator; the kernel does not hash a whole checkout to establish it. `record` means persistence, not verification acceptance. It intentionally preserves incomplete and failed observations, subject to structural/reference/history integrity. Run `validate` or inspect the separate validation result from `status` for readiness limitations. CLI validation never accepts self-asserted external receipts, so live release approval cannot be manufactured through this interface.

Validation exits 0 for implemented checks PASS, 1 for invalid input/FAIL and 2 for missing evidence/INCOMPLETE. History import/status exit 0 means the storage operation succeeded, not that the project is ready. Raw stored record decisions and the computed `release_disposition` are separate: an imported APPROVE stays queryable while missing verification yields HOLD.

## History design decision

The architecture's initial loose-file storage proposal does not itself provide atomic multi-record commits, stale-writer exclusion or crash recovery. This implementation uses one local SQLite file with FULL synchronous transactions for those demonstrated requirements. It adds no server or hosted dependency. Canonical records and canonical ChangeEvent objects are stored as exact byte blobs, preserving portable JSON representations.

Each transaction adds immutable record revisions and one canonical event. A commit wrapper additionally binds candidate identity and the previous commit digest; canonical `prior_event_sha256` continues to bind the previous event itself. Records, event and wrapper commit together under `BEGIN IMMEDIATE`. An expected state revision prevents concurrent stale commits. Update/delete triggers protect the supported API; reopening verifies record hashes, event links, reference bytes and invalidation projections. StateSnapshot is derived at read time, not trusted input and not the authority source.

This is a storage implementation decision for the local kernel. It does not prescribe SQLite for projects developed by Studio. Old records remain unchanged; supersession is derived by increasing revision rather than editing prior snapshots. Changed canonical byte representation or schema requires an explicit future migration; no prototype data is silently translated.

The process-interruption test exits a subprocess after writes but before commit, reopens history and checks that no partial records or event survived. Two concurrent writers using the same expected revision produce one commit and one stale-write rejection. Reopen, rollback, corruption detection and changed-input invalidation are covered independently.

## Remaining boundaries

- No automatic selector, risk-tier calculation or conditional planning policy is implemented. Registry matches do not establish a recommendation's correctness. Project-policy/synthesis choices are declarations, not independently approved policy.
- Artifact verification confines resolved paths to an evidence root, but does not provide race-free filesystem isolation or execution authorization. Task path checks are lexical; the trusted host must enforce actual paths, symlinks, operations, budgets and permitted scope at runtime.
- Authority callbacks must verify grantor, principal, action, scope, candidate, expiry and current host revocation state. Run callbacks must verify actual execution, complete required checks, independently defined oracles and producer/environment identity. Release callbacks must verify the complete required gate set, current owner approval and real support/recovery evidence. These integrations are not built yet.
- No dedicated finding/exception/incident entity exists in the canonical candidate schema. The earlier prototype's versions are not quietly accepted. Approval exceptions and incidents need explicitly versioned design work.
- History detects inconsistent bytes/chains; it does not defend against a privileged editor replacing an entire database and recomputing every digest. Durable external anchors, encryption, backup/export/import tooling, adversarial power-loss/filesystem testing and schema migrations remain future work.
- Replay restores committed records and invalidation. Task scheduling/resume workflow, run interruption states, complete lifecycle command set, multi-project orchestration and real cross-category trials remain unimplemented. Snapshot ACTIVE means recorded history exists, not accepted project readiness.
- DomainContract modules conservatively return INCOMPLETE until their pinned schemas and validators are registered. Unsupported capabilities cannot be accepted from wrapper shape alone.

This checkpoint implements part of the canonical semantic/state kernel. It does not claim G3 acceptance, autonomous development readiness, a measured productivity improvement, selector reliability or production integration.
