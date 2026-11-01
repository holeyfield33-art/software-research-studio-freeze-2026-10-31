# STUDIO-KNOWLEDGE-003R change log

This is an additive research-only continuation from the frozen STUDIO-KNOWLEDGE_003 checkpoint. The 003 ZIP and 001/002 archives were not edited or embedded.

## Changes

- Added a small deterministic CLI selector that reads only structured briefs, the stable rule catalog, and the versioned 003 JSONL dataset; it does not load expected/golden files.
- Added strict input and three output schemas, stable prioritized rules, contradiction/missing-input handling, explicit unknown/false semantics, unsupported-category abstention, and a no-PASS gate contract.
- Added explicit source-scope override for `source.mobile_applications.01`; an API branch cannot cite mobile-only guidance. The exclusion is emitted with exact claim locator and rationale in the decision trace.
- Added catalog-derived prompt requirements, candidate-bound evidence guards, authority checks, and typed graph traversal for `requires`, `verified_by`, and `produces`; typed `informs` edges remain separately traced context and cannot become prerequisites. The inherited baseline has no active `produces` edges.
- Independently froze the oracle before selector implementation; base expectations derive from the immutable 003 fixtures and counterfactuals from structured facts and directive criteria.
- Added ten counterfactual briefs (three per required archetype plus a standards-edition case), four mutation tests, five inherited negative controls, clean-room isolation checks, and exact oracle comparison.
- Added final selector runs, path traces, human-readable rule table, source/decision path report, mutation report, 003R validation report, and detached archive hash at packaging.

## Reproducibility and limitations

- Re-running the selector overwrites only its designated output directory; JSONL dataset partitions are read-only.
- Fixture/oracle status is evidence about these defined cases only. Seven catalog categories remain uncalibrated; no Studio integration or Stage 004 work was performed.
- No product test, CI workflow, deployment, release, action approval, or compliance result is claimed. All applicable execution gates remain incomplete.
