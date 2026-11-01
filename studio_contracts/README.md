# Universal Studio project contracts — 0.1.0

This is the first executable core of UNIVERSAL-001 milestone M1: a versioned project packet with facts, requirements, applicability decisions, tasks, attempts, artifacts, evidence, findings and gates. It works with project-relative records across software categories. It does not implement the applicability evaluator, planner, execution adapters or development system as a whole.

## Run

From repository root, using Python 3.10 or newer, with no installed dependencies:

```text
python -m studio_contracts.validate studio_contracts/examples/new-cli.json --grants studio_contracts/examples/new-cli.grants.json
python -m unittest studio_contracts.test_validate -v
```

The validator reads JSON and frozen registry files only. It does not execute commands, import archived scripts, contact services, alter packets or apply changes. Exit 0 means contract consistency PASS; exit 1 means invalid input or contract FAIL. The result includes findings with stable codes and transitive stale-record identities. Missing operator grants produce AUTHORITY failures rather than assumed permission.

All five example packets and grants are **synthetic**, unexecuted format examples: new CLI, existing library change, API authorization change, UI concurrency correction and pipeline recovery. Their evidence is NOT_RUN and gates are NOT_RUN. A packet can be structurally valid while its development work is incomplete. Synthetic reviewed/passing evidence exists only inside unit tests of validation rules; it is not real development evidence or a performance benchmark.

## Contract

`contract.json` is a deliberately small declarative contract interpreted by `validate.py`. It specifies required typed data fields, enums and task transitions. It is **not JSON Schema** and makes no JSON Schema conformance claim. Unknown record types, versions and fields are rejected rather than silently ignored. The common envelope is:

```text
id, version, project_id, created_by, provenance, status,
supersedes, depends_on, type, data
```

IDs use `project-id:local-id`, with positive integer versions. References are exact `{id, version}` pairs. Version 1 has null supersession; later versions retain history, supersede the preceding version of the same ID and mark older snapshots superseded. A persistence layer must enforce historical immutability; this validator cannot prove that a caller has not rewritten an older JSON record.

The project profile declares outcomes, owners, non-goals, current candidate revision, one or more actual frozen software-category IDs and an entry lifecycle stage. Categories scope examples, not claims of platform expertise. Unknown categories are explicitly unsupported in this initial format.

Facts distinguish known, unknown and conflicting knowledge. Unknown facts use null. Contradictory current known values for the same subject/scope/revision fail. This is exact structured conflict detection, not natural-language reasoning. Settled applicability decisions require known referenced facts and exact frozen ID/checkpoint/partition-digest references. Manual applicability decisions can be represented; automatic predicate evaluation is not implemented.

The full declared fields for each record type are in `contract.json`. Requirements carry acceptance and oracle descriptions; artifacts carry a path, digest, producer, revision and requirement links; evidence carries property, method, revision, origin, result, environment, input/output digests and reviewer. The validator checks their declared shape and links, not the truth of their text, hashes of external artifacts, actual execution or independence of reviewers.

## Authority boundary

Grants arrive through a separate operator-supplied file, never a field in imported research or a packet. A grant binds project identity, explicit action names, project-relative path roots and maximum step budget. Tasks and recorded attempts must fit the respective grant and task. Directory comparisons honor path-component boundaries; traversal, absolute paths and wildcards are rejected.

The adjacent example grants are conveniences for synthetic tests, **not live permission grants**. The operator must choose a trusted source. A separate file is not authentication. This validator neither authenticates the grant issuer nor enforces filesystem access, symlinks, case normalization, process behavior or real runtime budgets. Those are required adapter/runtime responsibilities before execution automation.

## Lifecycle, transitions and invalidation

Task history starts at planned and replays ordered events. Allowed transitions are declared in the contract. Status must agree with the replay; planned cannot jump to complete. Blocked tasks may return to ready, then running, while failed/interrupted attempts remain separate records. Review and completion require a current successful attempt; completion also requires the latest passing acceptance gate covering task requirements. A successful attempt alone does not establish completion. Active tasks require complete prerequisites.

Version-specific consumed inputs and prerequisites form a DAG. Task acceptance-gate links point forward to evaluation and are not prerequisite edges. Typed references automatically contribute input dependencies; explicit `depends_on` adds further inputs. A superseded input or candidate mismatch marks the consumer stale, then invalidation propagates transitively. Current stale records fail validation until new records/evidence re-establish consistency. There is no automatic reset, refresh or deletion of old evidence.

Initial policy is deliberately strict: every revision-bound record must match the current candidate. Evidence reuse across revisions requires future explicit scoped reassessment semantics; it is not inferred. The validator can propagate only **declared** dependencies. It cannot discover undeclared semantic coupling.

PASS evidence requires executed or reviewed origin. Gate PASS requires current passing evidence for every declared requirement and no current open finding affecting those requirements. Findings cannot be resolved without current passing evidence covering their requirements. NOT_APPLICABLE requires rationale/reviewer and empty requirement/evidence lists; it cannot waive declared work. No exception or severity-waiver mechanism is implemented yet.

## Coverage and remaining M1 work

Implemented checks cover UNI-001 through UNI-010 only at the level of packet consistency: typed facts, exact references, scoped tasks, event replay, findings and stale-evidence propagation. Full requirement satisfaction is not claimed. In particular UNI-002 needs actual applicability predicates, UNI-005 needs runtime enforcement, and UNI-010 needs durable storage and crash recovery.

Still pending: exception/approval records, release and incident contracts, richer design-decision alternatives and cost records, schema migration rules, authenticated authority sources, durable append-only storage, external artifact verification and a broader held-out scenario suite. These must be specified before M1 is called complete. The legacy 003R selector remains unchanged and is not used to make recommendations here.

`build_examples.py` reproduces committed synthetic examples from the exact frozen registry. It is a development helper; validation never invokes it. Frozen originals and independent reports are unchanged.
