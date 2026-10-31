# STUDIO-KNOWLEDGE-002 — Research continuation directive

**Mode:** research-only; create data, schemas, checks, and reports. **Do not modify Block-Wise Studio, products, application code, or existing repositories.** Preserve `STUDIO-KNOWLEDGE-001` and its original ZIP as immutable evidence. Continue with stable IDs/versioning; never present inferred practices as tested outcomes.

## Context and objective

The accepted checkpoint has 10 category overviews and 35 source URLs, with full JSON Schema checks passed for these 45 records. Eight required partitions are still empty. Build the first complete, *traceable*, evidence-backed knowledge slice that can later drive **three Studio outputs**: (1) SDLC plan, (2) agent coding prompt, (3) dependency-aware milestone roadmap. This is a knowledge foundation, not a request to implement the generator.

## Phase A — make the dataset safe before expanding it (P0)

1. Preserve the checkpoint and record its SHA-256. Retire or replace `build_seed.py` because it overwrites JSONL files and empties subsequent research. New init/build tooling must be non-destructive, path-independent, idempotent, and covered by a regression test proving a second run does not alter enriched data.
2. Keep Draft 2020-12 validation in the project. Add validation for each populated partition, uniqueness, foreign keys, relation endpoints and type constraints, record-version rules, and applicable-software-type identifiers. Retain explicit empty-partition reporting.
3. Write a specific `relationship.schema.json` with stable edge IDs and endpoints, controlled predicates (e.g. `applies_to`, `requires`, `verified_by`, `implemented_with`, `informs`, `produces`, `exemplified_by`), scope qualifiers, source IDs, and evidence classification. Do not bend the generic knowledge envelope to represent graph edges.
4. Define immutable/provenance fields for sources: actual title, publisher, canonical URL, retrieval date, published/version date if known, standard version or repo commit and file path, source type, claim locator (heading/section), and limitations. Do not fabricate missing metadata; explicitly mark it pending.
5. Normalize the 35 existing sources and their category-to-claim mappings. For repository files, use pinned commit URLs. Keep source snapshots or content hashes when permitted; respect licenses and do not copy full copyrighted documentation.

## Phase B — populate an integrated core knowledge slice (P1)

Research reusable cross-cutting material *once*, then map applicability/exclusions to the ten software categories:

- **SDLC stages:** discovery/scope; requirements and risk; architecture/design; implementation; verification; release; maintenance/incident feedback. For each: entry conditions, required inputs, decision owners, outputs, exit gate, rollback/rework path.
- **Engineering practices:** requirements traceability; version control/review; dependency and secret handling; test strategy; threat modelling; CI/release reproducibility; observability; change/maintenance management. Record when a practice is optional, mandatory by cited authority, or context-dependent.
- **Architecture patterns:** minimal viable structure first; client/server and API boundaries; layered/modular; event/queue; multitenancy; agent/tool trust boundary. Include alternatives, tradeoffs, threat assumptions and anti-patterns, not one-size-fits-all recommendations.
- **Verification gates:** requirements acceptance; security/risk review; unit and integration execution; dependency/supply-chain checks; release readiness; operational rollback. Define required evidence, pass/fail/incomplete conditions, and safe abstention when evidence is missing. Do not report any gate as passed based solely on a document.
- **Prompt patterns:** implement-scoped-task; add-test; review-change; threat-model; investigate-failure; prepare-release. Each needs input variable contract, constraints, outputs, stop/approval triggers, evidence demands, and an explicit prohibition against inventing test results.
- **Roadmap patterns:** smallest releasable increment; dependency-aware milestone sequencing; risk-first proof-of-concept. Store task dependencies, acceptance criteria, evidence requirements, and estimation assumptions; avoid invented calendar commitments.
- **Reference projects:** inspect and pin a small, diverse set of first-party/open-source repos (at least one web/API, one CLI or library, and one agent/security example with public evidence). Link specific architecture docs, real test files, CI workflows, release manifests, and any actual agent instructions. Distinguish observed configurations from independently executed tests.
- **Relationships:** make each primary path traversable from software category -> relevant stages/practices/patterns -> verification gates and prompts -> roadmap deliverables -> sources/reference examples. Avoid orphaned core records.

Prioritize an **AI agent/security product vertical** and a **web/API or SaaS vertical** first, as contrasting use cases. Add a CLI/library negative-control case so the engine does not force database, auth, container, or cloud deployment onto inappropriate projects. Expand the breadth across the remaining categories only after those slices survive review.

## Phase C — acceptance tests and coverage reporting (P1)

1. For each of three hypothetical briefs (AI agent with tool access; small authenticated API; offline CLI), generate a *paper exercise*, not Studio code: trace category and requirements to recommended stages, concrete deliverables, prompt templates, roadmap gates, and supporting source IDs.
2. Include rejected/inapplicable recommendations and why. Example: an offline CLI with no data persistence must not be assigned mandatory multitenant database work.
3. Challenge the knowledge with three conflict cases: guidance from different stacks; a changed/obsolete source; a missing test-result artifact. Mark unresolved rather than selecting unsupported answers.
4. Produce source-quality and evidence-strength summaries, record counts and missing-field percentages per partition, orphan/broken edge counts, category applicability matrix, and an explicit **PASS/PARTIAL/FAIL** with blockers.
5. No success claims for product implementation, tested code, or production readiness without actual execution or deployment evidence.

## Required checkpoint artifact

Deliver `STUDIO_KNOWLEDGE_002_checkpoint.zip` with:

- `dataset/v1/*.jsonl` for all ten partitions, preserving existing IDs and prior records unless explicitly versioned/superseded.
- `schemas/` containing schemas for **knowledge**, **source**, and **typed relationship** records, with migration notes.
- `scripts/validate_dataset.py` and automated non-destructive-seed regression tests.
- `reports/`: data dictionary; provenance/claim map; coverage matrix; three traceability exercises; source-quality report; validation report; unresolved evidence and conflicts; change log; next blockers.
- `manifest.json` with dataset/schema versions, per-file SHA-256 digests, build date, and declared scope.

**Acceptance criteria:** 0 JSON Schema errors; 0 dangling IDs/edges; no accidental duplicate records; repeat build does not overwrite enriched content; traceable full slices for AI-agent/security and web/API; CLI negative control passes; source claims mapped to precise locations; no unsupported universal mandates. If any gate cannot be met, report exactly what was completed, what is blocked, and the smallest next action. Do not label partial work as final.

**Out of scope:** Studio UI/UX changes, prompt execution, autonomous code changes in existing products, a vector database, embeddings, an ingestion service, a hosted API, monetization integrations, and wholesale data expansion before validation. The dataset should prove useful on paper before any engineering integration.
