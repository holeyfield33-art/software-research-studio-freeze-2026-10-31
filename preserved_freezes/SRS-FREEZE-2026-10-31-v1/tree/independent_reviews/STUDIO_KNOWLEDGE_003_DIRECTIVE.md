# STUDIO-KNOWLEDGE-003 — Calibrate knowledge selection and evidence (research-only)

**Mode:** independent research/data QA. Treat `STUDIO_KNOWLEDGE_001_initial_checkpoint.zip` and `STUDIO_KNOWLEDGE_002_checkpoint.zip` as immutable inputs. Do not modify Block-Wise Studio, production applications, existing repositories, or hosted services. Do not implement a generator, ingestion service, vector search, frontend, API, or payment system. Preserve current stable IDs; use record versions and a change log for corrections. Never label hypothetical outputs as executed outcomes.

## Goal

Turn 002's paper examples into **replayable, evidence-backed acceptance fixtures**, not more broad category content. The initial marketable promise is three consistent deliverables from a software brief: a tailored SDLC, an agent coding prompt, and a dependency-aware roadmap. Prove the data can support these before writing the product integration.

## P0 — repair correctness and packaging

1. Add typed JSON Schema contracts (or discriminated `if/then` schemas) for `category_specific` by record category: SDLC entry/exit/owner/rework; prompt variables/constraints/outputs/stop triggers; gate tri-state/evidence; roadmap task IDs/dependencies/acceptance; architecture option sets; reference repo metadata. Reject empty or malformed elements where structurally necessary. Keep schema migration notes and version bumps.
2. Make architecture alternatives concrete (`option_id`, `when_applicable`, `benefits`, `costs`, `risks`, `excluded_when`) and separate failure modes from tradeoffs. Specifically correct the vague `alternatives` for minimal structure and API boundaries; review the other four patterns.
3. Clean package contents: exclude `__pycache__`, `.pyc`, `*.tmp`, and stale validation artifacts. Add `build_date_utc`, validate the manifest hashes, and either include checksum sidecars in the deliverable or correct references to them. Repackage only from a clean, fresh validation run.
4. Increase regression coverage: 001-to-002-to-003 preservation test, idempotent enrichment/source import, failure on unknown category IDs/dangling relationships, rejection of malformed `category_specific`, exact manifest/hash verification, and reference to unknown roadmap task dependencies/cycles. Seed or migration scripts must never overwrite user-enriched rows.

## P1 — three machine-checkable golden fixtures

Define fixtures as data only: `brief.json`, `expected_selection.json`, `expected_rejections.json`, `expected_deliverables.json`, `evidence_trace.json`. Implement a **read-only deterministic fixture checker** (not the Studio generator): validate IDs, typed graph paths, branch conditions, required-input gaps, rejected requirements, and evidence citations against the dataset. Do not make the checker write generated code or modify Studio. The three fixtures:

A. **Tool-using AI agent:** external/untrusted content; read and bounded write tools; side effects possible; no standing approval for high-impact actions. Include expected trust boundary, authorization/approval, rollback and test-evidence conditions. Reject unrequired vector DB, autonomous multi-agent setup, and production deployment.

B. **Small authenticated API:** persisted records, role/user auth, simple single-service release; tenant isolation only if multiple tenant boundaries are explicitly in the brief. Include API authorization and unauthorized-path acceptance tests as **required future evidence**, not existing passes. Reject mandatory microservices, Kubernetes, queues and billing.

C. **Offline file-processing CLI:** local files, no accounts, no persistent shared state, no network access, no destructive writes. Require CLI argument/output/exit contracts and filesystem test fixtures. Explicitly reject auth, tenants, DB, cloud/container, API gateway and queue. Treat operational service rollback as inapplicable; local packaging/recovery remains conditional.

For each fixture, enumerate stable, linked record IDs and source claim locators that support stage, practice, architecture, gate, prompt and roadmap choices. Include required inputs, conditional exclusions, missing evidence/authority, and phase-specific status (`RECOMMENDED`, `CONDITIONAL`, `INAPPLICABLE`, `INCOMPLETE`). No mandatory claim may rely only on a category label or a loose free-text array.

## P1 — graph-to-brief reconciliation

1. Compare typed relationships with `applicable_software_types`. For each fixture's categories, ensure the intended selections are navigable from category through appropriate stages/practices/architectures/gates/prompts/roadmaps to sources/reference files, or explicitly document the graph rule used. Resolve duplicate/conflicting rules deterministically and record decision rationale.
2. Identify and handle sparse categories (`web_applications`, `mobile_applications`, `developer_tools`, `data_pipelines`) as **NOT_CALIBRATED** unless evidence and a worked fixture justify support. Do not equate arrays of applicable IDs with complete research coverage. Do not expand the other categories in 003 unless required to fix a high-impact false universal mandate.
3. Test three conflict/missing-evidence cases as a machine-readable fixture: stack mismatch, superseded standard, absent test execution. Assert `INCOMPLETE`/abstention rather than unsupported selection or a fabricated PASS.
4. Scope `agent_instruction_findings` to each reference repo, rather than repeating the aggregate paragraph in every record. Confirm each pinned path in the three reference slices and distinguish inspected files from executed CI.

## P1 — focused provenance calibration

1. Pick the highest-impact 12-15 source-to-claim mappings used in the three fixtures (not all 62 indiscriminately). Verify the exact document section/file/path and whether the claim is documented guidance, observed repo behavior, or synthesis. Flag unsupported/overbroad edges and repair via versioned records.
2. Store permissible source metadata, excerpt hashes, or reproducible canonical-file content hashes where license allows. For living pages without stated dates retain `pending`; do not manufacture dates. Require per-claim locator and inspectable evidence on all mandatory outputs.
3. Verify the edition and normativity of 12207 and NIST SP 800-53 only for claims actually used; if full normative text is unavailable, prohibit automatic compliance claims and label guidance as informative.

## Gate to finish 003

- Base and category-specific schema checks **PASS**, all IDs/edges resolve, no unintended data loss, manifest hashes all match; regression tests include both positive and negative cases.
- All three golden fixtures replay with exactly the expected selected and rejected IDs; CLI false obligations **zero**; unknown requirements cause a documented abstention.
- Every selected required action has a grounded source/reference locator and an applicable condition; the trace path to each selected gate, prompt and roadmap task is machine-checkable.
- No gate returns `PASS` without a candidate-bound actual result and necessary approvals; paper research remains `INCOMPLETE` when evidence is absent.
- At least 12 high-impact source/claim mappings independently spot-checked, with dispositions (`CONFIRMED`, `SYNTHESIS`, `UNRESOLVED`, `CONTRADICTED`).
- Keep unsupported or uncalibrated software categories **NOT_CALIBRATED**; do not treat dataset completeness as market readiness.
- Studio/product code untouched. Report `GO`, `PARTIAL`, or `NO-GO` separately for (a) dataset integrity, (b) fixture selection reliability, and (c) Studio integration. Do not claim production GO because a paper fixture passed.

## Required return package

`STUDIO_KNOWLEDGE_003_checkpoint.zip`: `dataset/v1/` and increment/version map, `schemas/`, `fixtures/ai_agent|authenticated_api|offline_cli/`, `tests/`, read-only `scripts/verify_fixtures.py`, `reports/source-claim-review.csv`, `reports/graph-coverage.md`, `reports/failed-negative-controls.md`, `reports/validation-report.json`, `reports/decision.md`, `reports/change-log.md`, and manifest with UTC build timestamp and hashes. Include prior original ZIP digests, not the prior ZIPs themselves.

**Do not start Stage 004 product integration** unless 003 establishes a deterministic, traceable, correctly abstaining selection path for these three cases.
