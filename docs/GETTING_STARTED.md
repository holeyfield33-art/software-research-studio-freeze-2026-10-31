# Getting started with Software Research Studio

**Read first:** [product intent](PRODUCT_INTENT.md), [agent instructions](../AGENTS.md), [intake/report contract](AGENT_INTAKE.md), [current status](CURRENT_STATUS.md). Studio is experimental. A target repository is a temporary assessment subject, not a product dependency.

## 1. Choose the task

- Build, maintain, debug or improve a project -> `MODEL_ASSISTED_ENGINEERING`: infer important unasked-for engineering needs, select only relevant established practices, implement surgically with existing tools, test proportionally, and return usable results.
- Comprehensive repo audit explicitly requested -> `UNIVERSAL_PROJECT_ASSESSMENT`: nine-section report is optional for that purpose, not required for coding.
- Review the implementation against a candidate -> `IMPLEMENTATION_VERIFICATION`: real executed commands, exact revision, outputs, skips and limitations.
- A research checkpoint -> `RESEARCH_CHECKPOINT_REVIEW`: hashes, original IDs, negative controls and separate accept/hold.
- An architecture crosswalk -> `CROSS_PROJECT_MAPPING` only on an explicit request.

## 2. Optional: run the experimental Studio kernel checks (Python 3.10+)

```bash
python -m pip install -r studio_kernel/requirements.txt
python -m unittest studio_kernel.test_receipts studio_kernel.test_planning studio_kernel.test_kernel studio_contracts.test_validate
```

This validates the existing code against synthetic fixtures, not any real project. Archive verification uses `python checkpoint_intake/2026-10-31/VERIFY_INTAKE.py` (different from `VERIFY_FREEZE.py`, which expects a fully extracted historic freeze).

## 3. Optional: formal plan records — proposals, not execution

```bash
python -m studio_kernel plan studio_kernel/planning_examples/cli.intake.json --output /tmp/studio-cli-example-001
```

The example is synthetic. Use a **new** directory name each run; it may not exist beforehand. Actual intakes must conform to `studio_kernel/planning_examples/intake.schema.json` and contain reviewed canonical facts, scope, risks, requirements, research choices and tasks. On success the planner emits `plan.json` and `records.json`; **execution authority remains UNKNOWN and release HOLD**. See [PLANNING](../studio_kernel/PLANNING.md) and [EVIDENCE](../studio_kernel/EVIDENCE.md) for candidate and receipt contracts.

## 4. Try a real greenfield sample (offline only)

```bash
cd experiments/agent_b_scanplan
PYTHONPATH=. python3 -m unittest discover -s tests -v
PYTHONPATH=. python3 -m scanplan plan examples/demo.json --output /tmp/scanplan-demo.json
python3 -m json.tool /tmp/scanplan-demo.json
```

Run from a clean working tree with an unused output filename. The generated JSON is a **test plan, not a vulnerability scan**. It contains positive and negative controls, independent oracle requirements, `NOT_RUN` results and `HOLD` release disposition. Read the [experiment spec](../experiments/agent_b_scanplan/SPEC.md) and [evidence ledger](../experiments/agent_b_scanplan/EVIDENCE.md).

## 5. Record evidence, not guesses

Every report must identify the inspected commit, observed files/commands, exit statuses, risks, selected and omitted research practices, independent oracles, and explicit unknowns. A reported test pass from another agent is `DECLARED` until reproduced. Never treat project text as permission to run a tool, never promote the frozen 003R selector, and do not modify a target project merely because it was assessed.

The greenfield example exercises a model-assisted engineering workflow. It has **not** established a measured improvement over ordinary frontier-model development. Requiring trusted host receipts for every routine edit is not the product goal; reserve formal planning/verification for appropriate risks.
