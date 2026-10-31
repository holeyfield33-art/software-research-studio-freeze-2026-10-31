# STUDIO-KNOWLEDGE-003R2 — Selection-policy stabilization directive

**To:** independent research/builder agent  
**Mode:** corrective research-only increment. Work from the frozen 003R checkpoint; preserve all 001–003 data.  
**Strict exclusions:** no Stage 004, no new software categories, no UI, no Studio repository changes, no hosted services, no LLM orchestration, no vector DB, no auth/payments/deployment products. No attempt to build a general-purpose policy engine.

## Objective

Move the existing deterministic selector from **13 curated cases passed** to **defensible rule behavior under unseen combinations of structured facts**, without widening the product surface.

## P0-A — Fix false rationales and authority contradictions

1. For `R-API-003`, evaluate `async_queue_required`, `queue_load_justification`, and `operations_owner_available` separately. If the last two are true, **do not emit `QUEUE_JUSTIFICATION_OR_OWNER_MISSING`**. The positive outcome may remain conditional on other explicitly named facts. Every reason code must identify a *currently* missing or contradicted predicate.
2. Add a cross-field contradiction matrix for project-scoped facts, not just duplicate `fact_id` rows. At minimum: authenticated users vs. `authentication_required=false` where scope is the same; `destructive_write_authorized=true` vs. explicit `write_scope_authorized=false`; any high-impact tool approval claims that conflict with named accountable authority. If both public and authenticated endpoints must coexist, require per-endpoint scope rather than silently flattening them into one project fact.
3. For a material conflict, set overall `INCOMPLETE`, emit typed `conflicting_fact_ids` and `reason_code`, and do not claim authorization or a completed selection.
4. Keep source-based authorization fail-closed. A mere boolean `true` must not be treated as an executed approval or release authorization; use correct distinctions among *requested*, *declared*, and *independently evidenced* authority.

## P0-B — Reject malformed input safely

1. Validate the full brief before iterating facts or assuming object/list types. Catch malformed JSON and JSON Schema errors; emit a machine-readable `INCOMPLETE/INPUT_SCHEMA_INVALID` rejection or a clearly documented stable error envelope with nonzero exit code, **without an unhandled exception**.
2. Test `facts` as string/null, a string fact row, missing `software_type_ids`, duplicate facts with conflicting scope/state, invalid state vocabulary, bad authority object, and missing evidence object.
3. Ensure the selector never reads oracle/expected files, even on malformed input. Preserve deterministic and read-only operation.

## P0-C — Replace unconditional obligation selection with actual fact checks

1. Inspect each member of `PROFILE` and `ROLE_PROFILE`. For records that impose tool, write, approval, tenancy, authentication, queue, upload or service work, require a specific positive predicate or an explicitly labeled **optional consideration**. No generic category alone may create a mandatory service or dangerous-action obligation.
2. The no-tool/no-untrusted-content agent probe must **not** mandate write-tool-boundary or approval/recovery work without a fact-driven reason. Keep baseline non-tool work only if its justification is explicit.
3. Do not invent dependencies or select an unsupported architecture. Preserve explicit `INCOMPLETE`, `CONDITIONAL`, `INAPPLICABLE` and `RECOMMENDED` semantics.
4. Make `overall_decision` unambiguous: a recommended *plan* is not a green light for unresolved required features. Either return overall `INCOMPLETE` whenever a requested critical capability remains unresolved, or separate `plan_selection_status` from `authorization_status` in a versioned output contract.
5. Check rule-to-implementation consistency. Prefer a small table/function predicate per existing rule; do not add a DSL, rules service or another subsystem.

## P0-D — Independent acceptance tests, frozen before code updates

Freeze a new oracle for **at least eight genuinely unseen combinations**, created independently from the selector outputs. Include the four bug demonstrations above, with exact expected status, IDs, reason codes, rejected records, relevant deliverable/task roles and explicit scope conditions:

- Requested queue with valid justification and named operations owner.
- Queue requested with justification true but owner unknown (missing *owner only*).
- CLI destructive-write authorization flag in conflict with a known false authority object.
- Authorized CLI write with a valid typed evidence reference (if the research dataset has no such evidence source, explicitly abstain with `EVIDENCE_UNAVAILABLE`; do not manufacture one).
- Project-scoped authenticated-user/public-read-only conflict.
- Agent with no read/write tools and no untrusted-content intake.
- API requiring tenancy with mapping unknown; then mapping known (state transition).
- Malformed `facts` string and malformed fact row (both must fail safely).

Add metamorphic invariants: toggling unrelated facts must not alter unrelated decisions; resolving a missing required fact must not preserve a reason claiming that fact is missing; `false -> true -> unknown` transitions must be handled consistently for critical facts.

Keep the 13 original oracle cases green unless a correction is intentionally breaking and documented in a versioned migration map. In that case obtain independent acceptance of the new expected behavior rather than modifying the frozen oracle to force a pass.

## P1 — Provenance, reproducibility and packaging

- Maintain 001/002/003 immutable parent hashes and 003R provenance, all ten versioned dataset partitions, stable IDs, typed graph integrity, and SHA-256 manifest.
- Run full Draft 2020-12 validation, selector/fixture tests, new independent mutation tests, DAG checks, rule coverage and read-only checks.
- Record exactly which rules have executable predicates, which remain advisory text, and the evidence paths used for each mandatory choice.
- Include a detached `STUDIO_KNOWLEDGE_003R2_checkpoint.zip.sha256` beside the archive and demonstrate that `verify_manifest.py --archive ...` returns `PASS` on the actual delivered archive.
- Produce a short report separating **dataset integrity**, **new-brief behavior**, **conflict and safety abstention**, **archive integrity**, and **Studio integration**.

## Acceptance criteria

**GO for bounded selector research only** if: every new counterfactual and all retained valid originals pass; no stale missing-fact reasons; cross-field material conflicts abstain; malformed inputs never throw unhandled errors; no mandatory no-tool write/approval obligations; proof of independent oracle authorship; full manifest plus detached archive hash pass.

**NO-GO for Studio integration** until a separate authorization and a practical end-to-end evaluation show that outputs can guide a small real project without unjustified work. Do not begin Stage 004 or commercial features as a side effect of this checkpoint.

## Return artifacts

`STUDIO_KNOWLEDGE_003R2_checkpoint.zip`, detached `.zip.sha256`, revised rule table, schemas if changed, tests plus independently frozen expectations, exact changed-case traces, updated changelog, and gate-by-gate decision report.
