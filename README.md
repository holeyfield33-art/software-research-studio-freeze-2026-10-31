# Software Research Studio

**Status (2026-11-01): experimental engineering-intelligence toolkit for frontier coding models; frozen research preserved.** Studio helps models build, maintain and improve vibecoded projects by recognizing missing engineering needs and selecting appropriate established practices **without requiring users to know what to ask for**. The model keeps using its normal coding tools, supported by Studio's **existing research and canonical planning/evidence engine**. The engine is retained, not deprecated or replaced; its depth should be proportionate to the task. Studio is not a mandatory lifecycle bureaucracy. See [product intent](docs/PRODUCT_INTENT.md) and [the adaptive repository knowledge layout](docs/REPOSITORY_KNOWLEDGE_LAYOUT.md).

> New agents: start with [AGENTS.md](AGENTS.md), [universal intake](docs/AGENT_INTAKE.md), and [getting started](docs/GETTING_STARTED.md). Do not treat an assessment target as a linked product.

## What lives here

| Area | Purpose | Current state |
|---|---|---|
| `preserved_freezes/SRS-FREEZE-2026-10-31-v1/`, `original_checkpoints/`, `checkpoint_intake/` | Immutable research/history and later independent verification receipts | 003/003R research archival integrity verified in scoped checks; 003R selector generalization **NO-GO** |
| `architecture/UNIVERSAL-ARCH-001/` | Evidence-linked universal lifecycle, schema, risk policy and gates | Design **candidate**, not full verified product |
| `studio_kernel/` | Canonical record checking, reviewed planning, SQLite history/replay and signed evidence acceptance | Implemented partial kernel; trusted execution host and end-to-end trials **missing** |
| `pilots/STUDIO-PILOT-001/` | Existing-repository intake/evidence-contract pilot | Started; narrow negative-control gate passed; lifecycle completion **HOLD** |
| `experiments/agent_b_scanplan/` | New greenfield CLI build exercising the documented Studio workflow | Offline prototype with initial 19 and follow-up 23 local tests; no network scanning or Studio host execution |
| `docs/` | Current intake, user guides, status and handoff | Active instructions |

The root-level `FROZEN_STATE.json`, `VERIFY_FREEZE.py` and `NEW_THREAD_HANDOFF.md` are historical archival artifacts. Do not rewrite them to pretend the original freeze changed, and do not use them as the latest operating instructions. The frozen archive itself must remain byte-identical. MOTHERSHIP and D-004 are separate evidence domains.

## Start here

```bash
git clone https://github.com/holeyfield33-art/software-research-studio.git
cd software-research-studio
python -m pip install -r studio_kernel/requirements.txt
python -m unittest studio_kernel.test_receipts studio_kernel.test_planning studio_kernel.test_kernel studio_contracts.test_validate
```

Those checks test the implemented kernel, **not** a real project's lifecycle. See [Getting Started](docs/GETTING_STARTED.md) for the model-assistance workflow, optional planning/evidence commands and the isolated greenfield build. A complete canonical lifecycle run is not a prerequisite for Studio to provide useful engineering guidance.

## Research and safety boundaries

- `SRS-FREEZE-2026-10-31-v1` / `STUDIO-KNOWLEDGE-003R` is immutable. Its 715 records and 601 relationships are research input, not permission to run the unreliable selector.
- The resubmitted research-only 003 checkpoint was independently rechecked and receipt merged in [the 2026-11-01 checkpoint intake](checkpoint_intake/2026-11-01/STUDIO_003_REVERIFICATION.md). Curated-fixture GO is **not** novel-input GO.
- Reviewed planning produces proposals, not command authorization. Signed receipts authenticate attestations but do not establish their real-world truth without a trusted host and independent oracles.
- Software Research Studio can assess any authorized external project without editing or linking that project's repository.

For current distinctions and gates, read [CURRENT_STATUS](docs/CURRENT_STATUS.md), [EXPERIMENTS](docs/EXPERIMENTS.md), [kernel implementation](studio_kernel/IMPLEMENTATION_STATUS.md), and [CHANGELOG](CHANGELOG.md).
