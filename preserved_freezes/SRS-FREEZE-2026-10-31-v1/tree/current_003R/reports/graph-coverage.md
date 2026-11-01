# Graph coverage and calibration boundary

Dataset version **1.2.0**; schema version **1.1.0**. This report describes graph navigability and fixture scope, not general product coverage.

## Fixture branches

| Fixture | Software type | Selected records | Rejected records | Rejected requirements | Exact source traces | Gate outcomes |
|---|---|---:|---:|---:|---:|---|
| `ai_agent` | `software_type.ai_agents` | 18 | 0 | 3 | 62 | gate.requirements_acceptance: INCOMPLETE, gate.security_risk_review: INCOMPLETE, gate.unit_integration_execution: INCOMPLETE, gate.release_readiness: INCOMPLETE, gate.operational_rollback: INCOMPLETE |
| `authenticated_api` | `software_type.apis` | 27 | 2 | 4 | 80 | gate.requirements_acceptance: INCOMPLETE, gate.security_risk_review: INCOMPLETE, gate.unit_integration_execution: INCOMPLETE, gate.dependency_provenance: INCOMPLETE, gate.release_readiness: INCOMPLETE |
| `offline_cli` | `software_type.cli_tools` | 17 | 7 | 8 | 49 | gate.requirements_acceptance: INCOMPLETE, gate.unit_integration_execution: INCOMPLETE |

The checker validates each selected record against its declared software-type applicability, an active typed category-to-record edge, a `supported_by` edge to the source record, and that source record’s exact claim locator. All selected records in these three narrow scenarios have at least one trace; the trace files enumerate the selected records’ linked sources. Rejected requirements and rejected records remain separately identified. The negative-control branch is not a fourth product category.

## Dataset and graph totals

| Partition | Records |
|---|---:|
| `software_types` | 10 |
| `engineering_practices` | 8 |
| `sdlc_stages` | 7 |
| `architecture_patterns` | 6 |
| `prompt_patterns` | 6 |
| `roadmap_patterns` | 3 |
| `verification_gates` | 6 |
| `reference_projects` | 3 |
| `sources` | 65 |
| `relationships` | 601 |

Relationships: **601 total; 598 active; 3 superseded historical edges**. All active edge endpoints and source IDs resolve. Applicability arrays mirror typed category edges but are not treated as research-coverage evidence. Three broad repository-example edges remain as explicit superseded history.

## Calibration boundary

A fixture proves only the scenario it exercises, not all products in the same category. The AI-agent, API, and CLI rows below have one worked scenario each; they are not general category certification.

| Software type | 003 status | Evidence boundary |
|---|---|---|
| `software_type.ai_agents` | `FIXTURE_DEMONSTRATED_NARROW_SCENARIO` | An AI agent reads untrusted external content, has read access and a bounded write-capable tool, and can cause side effects. It has no standing approval for high-impact actions. Design must state trust boundaries, authorization and approval, rollback/recovery, and test evidence conditions. No test or CI execution has occurred. |
| `software_type.apis` | `FIXTURE_DEMONSTRATED_NARROW_SCENARIO` | A small, single-service API for authenticated users, role-based authorization, and persisted records. |
| `software_type.cli_tools` | `FIXTURE_DEMONSTRATED_NARROW_SCENARIO` | Offline file-processing CLI with local filesystem input only; no network, service, account, or tenant boundary. No destructive-write behavior is authorized. Packaging and local recovery are conditional on distribution and write behavior. No tests, CI, or release execution occurred. |
| `software_type.data_pipelines` | `NOT_CALIBRATED` | No dedicated 003 acceptance fixture or category-specific claim calibration; do not infer support from applicability arrays. |
| `software_type.developer_tools` | `NOT_CALIBRATED` | No dedicated 003 acceptance fixture or category-specific claim calibration; do not infer support from applicability arrays. |
| `software_type.libraries` | `NOT_CALIBRATED` | No dedicated 003 acceptance fixture or category-specific claim calibration; do not infer support from applicability arrays. |
| `software_type.mobile_applications` | `NOT_CALIBRATED` | No dedicated 003 acceptance fixture or category-specific claim calibration; do not infer support from applicability arrays. |
| `software_type.saas` | `NOT_CALIBRATED` | No dedicated 003 acceptance fixture or category-specific claim calibration; do not infer support from applicability arrays. |
| `software_type.security_products` | `NOT_CALIBRATED` | No dedicated 003 acceptance fixture or category-specific claim calibration; do not infer support from applicability arrays. |
| `software_type.web_applications` | `NOT_CALIBRATED` | No dedicated 003 acceptance fixture or category-specific claim calibration; do not infer support from applicability arrays. |

### Explicitly sparse/un-calibrated categories

The required sparse categories—`web_applications`, `mobile_applications`, `developer_tools`, and `data_pipelines`—remain `NOT_CALIBRATED`. SaaS, security products, and libraries also remain `NOT_CALIBRATED` because no dedicated fixture was built in this research-only increment.

### Graph policy

Active relationship predicates distinguish `applies_to` (category to knowledge record), `exemplified_by` (category/reference example mapping), and `supported_by` (knowledge record to source). Reference-project applicability was narrowed to the verified primary category; the three displaced inherited edges were retained with a supersession status and are excluded from active traversal. A category/source/edge link is not proof that a recommendation applies or that a practice was executed.

The 003R selector additionally traverses applicable active `requires` edges as prerequisites and `verified_by` edges as verification obligations; `informs` edges are validated and reported only as related context, never as prerequisites. The versioned graph contains 26 active `requires`, 5 active `verified_by`, and 58 active `informs` relationships. It contains no `produces` relationships, so the selector reports none rather than inventing dependencies. These dataset-wide counts describe graph structure, not category-level recommendation coverage or executed evidence.
