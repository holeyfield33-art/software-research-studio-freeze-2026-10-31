# STUDIO-KNOWLEDGE-002 — Independent checkpoint acceptance review

Date: 2026-10-31
Decision: **PARTIAL ACCEPT** for research/data foundation; **NO-GO** for importing into a production SDLC/prompt/roadmap generator.

## Executed checks

- Reviewed the original uploaded checkpoint ZIP, extracted the 002 archive into an isolated audit directory, and reran `scripts/validate_dataset.py` with Python 3 and installed `jsonschema`. **PASS: zero reported schema, ID, endpoint, and foreign-key errors**.
- Ran `python3 -m unittest discover -s tests -v`. **PASS: 1 test** confirming a second `seed_core.py` invocation preserves enriched data and is independent of the current working directory for the tested case. Not a comprehensive migration or concurrency test.
- Independently counted all partitions: 10 software types, 8 practices, 7 SDLC stages, 6 architectures, 6 prompts, 3 roadmaps, 6 gates, 3 references, 62 sources, 411 relationship edges: **522 total rows**.
- Independently checked original 001 ZIP SHA-256 against 002 provenance: **match** (`30a2cd7746064c36ea24b7e43c302942db6e10b674edcc06de7ced7f97a4732c`). Preserved original IDs: 10/10 software types, 35/35 sources.
- Independently checked graph endpoints: 0 orphan nodes, 0 dangling endpoints, 0 duplicate edge tuples on (source, predicate, target, scope).
- Checked embedded manifest's 47 file digests against included content: **all matched** (the separate 002 manifest was excluded from its own digest).
- Spot-checked three public source URLs (IEEE 12207 catalog; pinned OpenAI Agents SDK SECURITY.md; pinned FastAPI test workflow): all resolve and the cited material is present. These are spot checks, not a complete 62-source verification.

## Accepted improvements over 001

- All ten originally empty or populated partitions now carry records; 001's 8 empty partitions are populated.
- Non-destructive seeding tested; source and relationship schemas exist; source metadata substantially improved; repository file URLs are commit-pinned.
- Three clear **paper** traceability exercises exist (AI agent with tools; authenticated API; offline CLI). The offline CLI case explicitly rejects unsupported database, tenant, cloud, and auth mandates.
- Tests/configurations are described as observed source code, not tested outcomes; absence of run evidence makes gates `INCOMPLETE`.

## Material gaps

1. **Graph reachability vs. declared category applicability.** Four software types—`web_applications`, `mobile_applications`, `developer_tools`, `data_pipelines`—have only 1-2 direct `applies_to` graph edges and zero direct `informs` edges to prompts/roadmaps. Applicability arrays and coverage-matrix totals are not full typed recommendation routes. The three priority paper exercises are hand-authored, not machine-replayed from the graph.
2. **Unvalidated category-specific contracts.** `knowledge-record.schema.json` permits any object for `category_specific`, so malformed/missing SDLC entry/exit gates, prompt input contracts, roadmap task graph shapes, or verification tri-state structures can pass general schema checks. Fields such as description, arrays, source claim locators, and edge scope also have weak semantic constraints. 'Zero JSON Schema errors' means base shape passes, not a complete contract for generator input.
3. **Generic architecture alternatives.** `arch.minimal_viable_structure` lists 'AWS architecture guidance; tradeoffs are qualitative' as an `alternatives` entry; `arch.client_server_api_boundary` lists a caution about offline software. Such items are not concrete architecture alternatives. A selection engine would need an explicit option/conditions/benefits/costs/exclusion structure.
4. **Evidence reproducibility.** 0/62 sources has a retained content SHA-256, 34/62 publication/version dates are pending, and 1/62 publishers is pending. Pending dates are appropriate when pages do not provide them; inventing them is not the fix. Preserve lawful text snippets/metadata and hashes for a focused sample, and keep unavailable metadata pending. No source hash coverage is currently possible.
5. **Packaging hygiene and manifest completeness.** The shipped ZIP contains `reports/validation-run-1.tmp` (a discarded early validation run with 669 errors) and compiled `tests/__pycache__/` content, which should not be distributed in the normalized research release. The `manifest.json` lacks an explicit build timestamp/date requested in the 002 directive. It refers to detached checksum sidecars that were not attached with the uploaded ZIP; distribute or adjust that statement.
6. **Limited verification of source-to-claim correctness and project performance.** A source ID and locator do not prove an individual synthesized recommendation is directly supported. Human sampling of the highest-impact graph claims remains necessary. Three pinned reference projects were *not* executed; no product, reference-project, or generated-plan runtime success is established.
7. **Reference metadata granularity.** `reference.fastapi`, `reference.ripgrep`, and `reference.openai_agents_sdk` each repeat the same aggregate `agent_instruction_findings` paragraph rather than per-reference findings. Scope per-project observations to their individual reference records.

## Acceptance gates

| Gate | Result | Scope |
|---|---|---|
| Base JSON Schema, IDs and typed graph endpoints | PASS | Included validator and independent graph checks |
| Original 001 preservation | PASS | Immutable ZIP SHA and inherited stable IDs |
| Basic seed non-destructive regression | PASS | 1 test only |
| Three paper traces and CLI negative control | PASS as paper examples | Human-authored, not executable/generator-proven |
| Detailed schema contracts and conditional selection | PARTIAL | Category-specific data not fully typed |
| Content-level claim/source verification | PARTIAL | Source metadata and limited spot checks, no retained content hashes |
| Production generator integration | NO-GO | No deterministic selection test, no real briefs or approval evidence |

## Decision

Accept 002 as the frozen baseline research checkpoint. **Do not add an ingestion service, vector database, web app, or production Studio wiring yet.** Conduct the narrowly scoped 003 calibration defined in the accompanying directive. Its central question: *Can two contrasting briefs and one negative control be selected and traced reproducibly from data without inventing obligations, tests, or deployment requirements?*
