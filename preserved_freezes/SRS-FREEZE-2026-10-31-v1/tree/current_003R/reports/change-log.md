# Change log — STUDIO-KNOWLEDGE-003

## 2026-10-31 — research-only calibration

- Preserved every stable record ID found in the immutable 001 and 002 checkpoint indexes; added record-version changes instead of replacing IDs. The original archive digests are recorded in `research/immutable-input-digests.json`; prior ZIPs are intentionally not included.
- Added strict Draft 2020-12 typed contracts for lifecycle stages, prompt patterns, tri-state verification gates, roadmap tasks/dependencies, architecture options/tradeoffs, and repository reference metadata. Schema/data versions are 1.1.0/1.2.0.
- Reworked six architecture patterns to use explicit option IDs, applicability conditions, benefits, costs, risks, exclusions, evidence classes, and separate failure-mode lists. No architecture is declared a universal default.
- Scoped agent-instruction findings to FastAPI, ripgrep, and OpenAI Agents SDK separately; pinned reference files to commit plus path and kept test/CI/release execution status `not_run`.
- Updated source metadata/claims for AWS workload guidance, Twelve-Factor process guidance, the CLI guide, the OpenAI Agents SDK trace test, selected commit-pinned files, and the IEEE 12207 catalog entry. Added three pinned tree-inventory sources. Full normative text was not inspected.
- Retained three stable inherited relationship IDs as `superseded` history when repository applicability was narrowed. Active graph is validated separately from superseded history.
- Added three deterministic acceptance fixtures and one dedicated abstention/control branch, with exact source locators and typed graph paths. Added a golden-ID index to detect silent selection/rejection changes.
- Added five machine-checkable negative controls: stack mismatch, superseded standard, absent test execution, source-scope tension, and unknown requirement abstention.
- Added a safe migration completion marker and pristine-baseline guard; completed migration reruns do not write dataset files. Regression test confirms versioned user enrichment survives a rerun.
- Added schema/graph/roadmap/fixture/manifest/idempotency and preservation regressions. No Studio, product code, hosted service, generator, ingestion path, vector search, frontend, API, or payment system was implemented or modified.

## Known limits

- The fixture checker verifies curated expected selections; it is not a general brief-to-selection generator.
- Seven software types remain `NOT_CALIBRATED`; even the three represented types have only one narrow worked scenario each.
- No tests, CI, releases, deployments, or standard-conformance assessments were executed.
