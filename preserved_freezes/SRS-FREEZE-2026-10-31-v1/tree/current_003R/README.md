# STUDIO-KNOWLEDGE-003R — deterministic selection research checkpoint

This research-only corrective increment tests whether a small deterministic policy can select a scoped SDLC, prompt contract, and dependency-aware roadmap for three calibrated project archetypes. It starts from the frozen 003 dataset and does not modify the original 003 checkpoint, 001/002 archives, Studio, hosted systems, or commercial product code.

## Contents

- `dataset/v1/` — inherited 003 versioned JSONL dataset, unchanged in this increment.
- `selection_cases/` — three structured base briefs plus ten counterfactual briefs.
- `oracles/frozen-oracle.json` — independently authored exact expectations; selector never reads it.
- `rules/selection-rules.json` — prioritized deterministic rule catalog and reviewed source-scope override.
- `scripts/select.py` — read-only selector CLI.
- `schemas/selector-input.schema.json` and `schemas/*output.schema.json` — Draft 2020-12 contracts.
- `selector_runs/` — candidate selections, rejections, and decision traces for every brief.
- `tests/test_selector.py` — exact expectations, source/graph checks, negative controls, and adversarial mutations.
- `reports/decision-003r.md` — separate integrity, selection, safety, and integration decisions.

## Reproduce

Requires Python 3.10+ and `jsonschema` with Draft 2020-12 support. From the project directory:

```bash
python3 scripts/select.py --brief selection_cases/base_ai_agent/brief.json --dataset dataset/v1 --rules rules/selection-rules.json --out /tmp/selector-output
python3 scripts/verify_selector.py
python3 scripts/run_regression_tests.py
python3 scripts/verify_manifest.py --root .
```

The selector reads a brief, the versioned graph and the rule catalog only. The separate verifier may read the frozen oracle. Selector output files are not read back by the selector.

## Decision boundary

GO applies only to dataset integrity, exact replay of these 13 cases, and safety-abstention tests. Overall disposition is PARTIAL. This is not a general product generator or Studio integration; Stage 004 remains prohibited by the directive. No test/CI/deployment/release/compliance PASS is claimed.
