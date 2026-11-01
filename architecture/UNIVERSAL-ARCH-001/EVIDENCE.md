# Evidence basis and reconciliation

## Provenance and limits

Read the recovered freeze, all ten 003R dataset partitions, checkpoint reviews 001/002/003/003R, the unexecuted 003R2 directive, current rule/input/gate contracts, source-claim review, UXEC synthesis and adjudication, proposed experiment, and original Gemini scope/UX, DeepSeek UXEC and Perplexity evidence reports. The original 001/002/003/003R ZIPs were inspected through archive verification and predecessor comparisons; this is not a fresh exhaustive external-source audit or a rerun of their behavioral suites.

The original archive is `preserved_freezes/SRS-FREEZE-2026-10-31-v1/SOFTWARE_RESEARCH_STUDIO_FREEZE_2026-10-31_v1.zip`, SHA-256 `a39b30fee3304e843b0291770efe7a42e993d733c3c09d5321ea5f2d53e6ad04`. Recovery verifier rerun: PASS, 177 byte-identical extracted files, 175 inventory entries, 151 inner manifest hashes, eight nested ZIP CRC checks, 715 records, 601 relationships. The 003R ZIP digest is `5fea1fe5e8f19064df7ee9af4386aeb85046003c99ee83f9b4569432f0992aa8`; all ten 003→003R partitions remain byte-identical. Recovery verification does not resolve selector defects. The freeze includes the detached 003R checksum; its earlier absence in the independent audit is a historical packaging finding, not current corruption.

All frozen paths below resolve under [the preserved tree](../../preserved_freezes/SRS-FREEZE-2026-10-31-v1/tree/). `evidence-index.json` stores full paths, line locators and hashes. Its original record and relationship IDs are authoritative references; no new `003R-*` identifiers are minted. Package-specific IDs begin `ua.` and have no frozen-registry standing.

## Source register

| Key | Preserved evidence | Architectural consequence |
|---|---|---|
| E01 | `independent_reviews/STUDIO_KNOWLEDGE_001_REVIEW.md` | Non-destructive ingestion, stable IDs, exact claim locators; inventory completeness is insufficient. |
| E02 | `independent_reviews/STUDIO_KNOWLEDGE_002_REVIEW.md` | Typed category payloads; preserve source uncertainty; graph reachability is not applicability or semantic support. |
| E03 | `independent_reviews/STUDIO_KNOWLEDGE_003_INDEPENDENT_AUDIT.md` | Separate selector from expected outputs; derive task/gate decisions from facts, not copied goldens. |
| E04 | `independent_reviews/STUDIO_KNOWLEDGE_003R_INDEPENDENT_AUDIT.md` | Keep known queue, contradiction, malformed-input and over-selection defects as blockers; 13/13 remains bounded. |
| E05 | `next_unexecuted/STUDIO_KNOWLEDGE_003R2_DIRECTIVE_UNEXECUTED.md` | Corrective selector lane: unseen combinations, metamorphic checks, typed conflict evidence, no automatic integration. |
| E06 | `current_003R/docs/rule-table.md`, `rules/selection-rules.json`, `scripts/select.py` | Priority/unknown/exclusion semantics retained as design inputs; narrative rule tables are not executable enforcement. |
| E07 | `current_003R/dataset/v1/*.jsonl`, `reports/source-claim-review.md`, `reports/coverage-gaps.md` | Research remains guidance with explicit scope. Seven types lack calibration; three types have narrow examples only. |
| E08 | [UXEC candidate](../../rounds/SRS-UX-002/UXEC_SPEC.md), [adjudication](../../rounds/SRS-UX-002/DECISIONS.md) | Change packet, external requirement mapping, finding-level ratchet, structural/behavior/accessibility/usability separation. |
| E09 | [Gemini scope original](../../rounds/STUDIO-SCOPE-001/original_reports/gemini/Pasted%20text.txt) | Diagnose actual project before adapter generation; bounded execution and drift checks. Proposed scoring/AST metrics are hypotheses. |
| E10 | [Gemini UX original](../../rounds/SRS-UX-002/original_reports/gemini/ux-ui-architecture/Pasted%20text.txt) | Eight iterative UX concerns retained as optional domain coverage; SurfaceTrace details and universal styling/navigation rules excluded. |
| E11 | [DeepSeek original](../../rounds/SRS-UX-002/original_reports/deepseek/Pasted%20text%286%29.txt) | Useful contract/gate/fixture structure, narrowed by E08/E12; proposed tests and code remain unexecuted. |
| E12 | [Perplexity original](../../rounds/SRS-UX-002/original_reports/perplexity/Pasted%20text%285%29.txt) | Each verifier claims only evaluated properties; independent oracles, clean controls, honest standards and productivity claims. |

Later [Gemini preservation confirmation](../../rounds/SRS-UX-002/original_reports/gemini/README.md) supersedes earlier “missing Gemini” notes. Historical notes remain unchanged. Original report provenance is retained; neither report independence nor authorship establishes technical correctness.

## Reconciliation decisions

| Decision | Adopt / narrow / reject | Evidence and rationale |
|---|---|---|
| ua.adr.001 | Adopt project diagnosis before plan generation; allow greenfield intent intake when code does not exist | E09 plus `sdlc.discovery_scope`; static inspection yields observations and hypotheses, never runtime correctness. |
| ua.adr.002 | Adopt local versioned files and one validation CLI first | E08/E09; straightforward inspection/review, no need yet for hosted services, vector database or orchestration platform. This topology is design synthesis. |
| ua.adr.003 | Narrow graph-based selection to scoped claim paths and executable predicates | E02–E06; category labels nominate candidates; explicit facts justify obligations. Fail closed on missing consequential evidence. |
| ua.adr.004 | Adopt separate plan, execution, verification and release decisions | E03–E05 and all six `gate.*` records; a plan recommendation cannot authorize or certify a candidate. |
| ua.adr.005 | Adopt UXEC as optional interaction-contract module | E08/E10–E12; no universal DOM instrumentation, state machine, draft-buffering, depth≤3 or raw-pixel ban. |
| ua.adr.006 | Reject assumed registry membership of UX labels | Resolve actual IDs from E07; `003R-DISC-001` and peers in originals are report-local proposals, not frozen records. Keep raw text unchanged and unresolved mappings explicit. |
| ua.adr.007 | Narrow diagnostic metrics | E09/E12; assertion counts, mock ratios, test files and green CI do not establish meaningful acceptance coverage. Require oracle/assertion review. |
| ua.adr.008 | Adopt immutable events plus revisioned state projection | `practice.change_maintenance`, `practice.requirements_traceability`, E08/E09; compare-and-swap, invalidation and concurrency behavior are new design proposals requiring tests. |
| ua.adr.009 | Reject universal performance/compliance claims | E08/E12; reported percentages, seeded-error rates, certification and generalization are unverified. Standards summaries support only their stated scope, edition and organizational adoption. |

Risk tiers, schemas, invalidation algorithms, gate IDs and the MVP boundary in this checkpoint are **proposed synthesis**. Frozen source links support underlying concerns; they do not prescribe this exact system. No external sources were refreshed or newly ingested. The two memory connectors were unavailable; all substantive evidence used here came from local preserved files and the GitHub connector. Secret-bearing connector diagnostics are excluded from artifacts.
