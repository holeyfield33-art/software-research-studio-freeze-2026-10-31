# STUDIO-KNOWLEDGE-003 — Independent checkpoint audit

Review date: 2026-10-31  
Input: `STUDIO_KNOWLEDGE_003_checkpoint.zip`  
Input SHA-256: `78d0977bd77f35b56aba5af0ca3f1719d77e4d5089d291ac6a36593ab0a983df`  
Scope: offline independent validation and focused external public-source spot checks. No Studio or existing products modified.

## Verdict

| Decision area | Status | Meaning |
| --- | --- | --- |
| Dataset integrity | **GO** | Schema, ID, relationship, roadmap DAG, regression and manifest-member integrity checks pass. |
| Curated fixture consistency | **GO, narrow** | The verifier confirms three curated golden fixtures and one negative-control suite against the existing dataset. |
| Actual selection correctness on unseen briefs | **NOT PROVEN** | The tool consumes expected selections and a golden-ID map; it does not compute selections from a novel input brief. |
| Studio integration | **NO-GO** | Not part of this checkpoint; refrain from building Studio integration until the corrective gate passes and is separately authorized. |

## Independently reproduced baseline checks

- `python scripts/validate_dataset.py --report <temp_path>` -> PASS; 0 errors.
- `python scripts/verify_fixtures.py --report <temp_path>` -> PASS; 0 errors; four fixtures including one conflict/missing-evidence fixture.
- `python -m unittest discover -s tests -v` -> 12/12 PASS.
- `python scripts/verify_manifest.py` -> PASS; internal 77-file manifest digest verification.
- ZIP member count: 79; manifest tracks 77 files; the remaining two are `manifest.json` and `manifest.sha256`.
- Record partitions: 10 software types, 8 engineering practices, 7 SDLC stages, 6 architecture patterns, 6 prompt patterns, 3 roadmap patterns, 6 verification gates, 3 reference projects, 65 sources and 601 typed relationships = 715 records.
- Relationships: 598 active, 3 superseded.
- Parent archive checksums for 001 and 002 match the ZIP files mounted in this review.
- `python scripts/verify_manifest.py --archive <input_zip>` -> FAIL solely because `<input_zip>.sha256` was not supplied. The archive itself opens and internal member hashes pass; do not confuse the missing detached sidecar with a content mismatch.

## Adversarial tests (performed on isolated temporary copies)

Each following modification was made to one fixture JSON file; all untouched files stayed constant. The intended verifier's `verify_fixtures.py` still exited 0 and returned PASS with zero errors in all four tests:

1. `fixtures/ai_agent/expected_selection.json`: switched `arch.agent_tool_boundary` status from `RECOMMENDED` to `INCOMPLETE` while keeping golden ID map unchanged.
2. `fixtures/ai_agent/brief.json`: replaced the free-text description with “This is a static public HTML page with no AI agents, no external content and no tool access,” contradicting existing structured attributes and selection.
3. `fixtures/offline_cli/expected_rejections.json`: replaced the rejected `feature.authentication` rationale with “Authentication is mandatory, include the full hosted identity system.”
4. `fixtures/authenticated_api/expected_deliverables.json`: replaced the first deliverable acceptance criteria with “All tests passed and production launched. No tests needed.”

Interpretation: the fixture verifier enforces data schemas, a preauthored ID oracle, graph/source presence, the boolean conditions recorded by the fixture, certain missing inputs, and limited negative cases. It does **not** independently infer all decisions from user requirements, compare status/rationale to an independent decision oracle, check natural-language contradictions, or certify the truth of deliverable acceptance-criterion text. This is a narrower result than recommendation correctness. Intentional separation of descriptive text and structured attributes would be acceptable if documented and excluded from the decision surface; currently contradictory text is accepted without warning.

## Positive results and limits

- It keeps execution-bound verification gates `INCOMPLETE`, preventing fabricated PASS statuses in the `gate_outcomes` object.
- It rejects dangling relationships, malformed category-specific records, unknown category IDs, unknown/cyclic roadmap dependencies, and several simulated unsafe mutations.
- Three curated scenarios exercise a tool-using AI agent (18 selected records), a small authenticated API (27), and an offline CLI (17). CLI explicitly rejects eight false obligations.
- Per-record evidence traces check an active `software_type -> knowledge_record -> source` typed graph path and source-record locator. They do **not** establish a task-specific derivation linking selected stages, controls, gates, prompts, and roadmap actions via `requires`, `verified_by`, `produces`, etc.
- All seven categories outside AI agent/API/CLI are correctly marked `NOT_CALIBRATED`; one scenario per calibrated type is not category-wide generalization.
- Source-claim review contains 15 agent-reported mappings (10 CONFIRMED, 5 SYNTHESIS). Independently spot-checked the linked OpenAI prompt-injection article, AWS workload segmentation, and Twelve-Factor processes pages. Their text supports the caution that their distinct scopes do not mandate a universal architecture. These three external checks are not an independent certification of all 15 mappings.

## Blockers, ordered by priority

**P0 — selector/oracle gap**: Add a read-only deterministic rule evaluator that *produces* selected/rejected records and statuses from a structured brief without consulting expected-selection files. Preserve the separate oracle only for comparison. This is a research QA fixture selector, not a Studio feature.

**P0 — semantic safety gap**: Ensure changes to actionable statuses, required outputs, exclusion rationales and gate evidence cause a test failure where contradictory. Use normalized rule IDs, typed decision reasons, source/claim IDs, candidate-bound evidence rather than trying to validate arbitrary prose with schemas alone. Treat free text as non-authoritative or reconcile it with structured facts.

**P0 — unsupported decision paths**: Make selected gating and roadmap actions trace to applicable requirement facts, rules, and specific source/record paths beyond generic category/source edges. Absent/mismatched facts should yield `INCOMPLETE` or `CONDITIONAL` explicitly.

**P1 — meaningful counterfactual coverage**: Add independent outcomes for at least three variations per base case, including changes that reverse an outcome, plus unsafe/unknown data handling. Mutation tests must demonstrate that the evaluator responds to changed structured facts, not merely expected files.

**P2 — archive sidecar**: Provide `STUDIO_KNOWLEDGE_003_checkpoint.zip.sha256` (or a corrected documentation/verification contract), and test the archive-specific checksum path.

## Product decision

The research base is preserved and structurally sound. The next action is **003R: selection and oracle hardening**, not broad category expansion or Stage 004 Studio integration. Keep the 003 artifact immutable and version all changes. Do not claim that any project tests, CI, deployment, external approvals, or compliance checks were executed.
