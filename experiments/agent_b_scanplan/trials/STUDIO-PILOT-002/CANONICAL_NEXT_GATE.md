# Canonical Studio kernel continuation gate (NOT RUN)

The validated ScanPlan code change is deliberately **not** being called a completed `studio_kernel` lifecycle run. In this execution environment only the experiment subtree was locally available for Python tests; a full Studio repository checkout with the canonical kernel and frozen 003R registry could not be materialized. GitHub hosted jobs also still need working runners. The canonical planner and authenticated acceptance commands were therefore **NOT_RUN**, not FAIL/PASS.

## Exact candidate to review

- Baseline Studio `main`: `3795c1736b20ac3d6955e1587f4c7f7a8c778ec3`
- Initial `scanplan/core.py` Git blob: `6b6851fd1d294fe7113bddfcd5e2ab2937704545`
- Fixed `scanplan/core.py` Git blob: `b4392ca21bed68de95ce83520729fe9232e57a91`
- New test file Git blob: `72ee69bf180f2a52b20382d5ab0b5dab333dcd37`
- Test evidence: [evidence.json](evidence.json)

## Candidate canonical records (must be created and reviewed, not assumed approved)

Create these using `architecture/UNIVERSAL-ARCH-001/contracts.schema.json` and the actual registered frozen 003R IDs/digests:

1. `ProjectProfile` — a greenfield CLI with a local input-validation repair; exact starting tree identity and allowed paths.
2. `Fact` — confirmed escaped-surrogate crash and red-phase reproducer; observed file/test outputs with stable file hashes. Other risk dimensions remain unknown unless evidenced.
3. `Requirement` — controlled `IntakeError`, CLI exit 1, output not created, supported Unicode continues to work, deterministic demo unchanged.
4. `DesignDecision` — explicitly reviewed, scoped selection of `practice.test_strategy`, `gate.requirements_acceptance` and `practice.version_control_review`, with applicable source IDs/hashes; no automatic 003R selector.
5. `TaskPacket` — bounded to `experiments/agent_b_scanplan/scanplan/core.py` and `tests/test_unicode_boundary.py`, with commands, oracle refs, budgets and stop rules.
6. `Authority` — must come from the actual trusted operator/host; **not** invented from an agent string.
7. `EvidenceRun`, `GateDecision`, `ReleaseDecision` — only after the host authenticates the tested candidate, execution and independent reviews.

With a full, independent Studio checkout and reviewed canonical intake file, execute from the repository root:

```bash
python -m pip install -r studio_kernel/requirements.txt
python -m unittest studio_kernel.test_receipts studio_kernel.test_planning studio_kernel.test_kernel studio_contracts.test_validate
python -m studio_kernel plan PATH_TO_REVIEWED_INTAKE.json --output /tmp/studio-pilot-002-plan
```

The referenced JSON **does not exist yet** because neither the risk/research reviewer nor a real host grant has supplied the required authenticated records. Use `studio_kernel/planning_examples/intake.schema.json` and `studio_kernel/PLANNING.md` to construct it; do not substitute the synthetic example as real acceptance. Output directory must not exist. Inspect `plan_status`, `execution_authority` and `release_disposition` separately. Any missing required risk/review should yield INCOMPLETE, not a fabricated recommendation.

For future independent execution evidence, follow `studio_kernel/EVIDENCE.md` exactly with operator-pinned public keys and independently obtained signed host receipts:

```bash
python -m studio_kernel import-evidence PATH_TO_SIGNED_RUNS.json --project PROJECT_ID --store PATH_TO_HISTORY.sqlite --expected REVISION --candidate PATH_TO_CANDIDATE.json --actor operator --trust-config PATH_TO_TRUST.json --receipts PATH_TO_RECEIPTS.json --artifacts PATH_TO_ARTIFACT_ROOT
python -m studio_kernel accept --project PROJECT_ID --store PATH_TO_HISTORY.sqlite --candidate PATH_TO_CANDIDATE.json --task-ref PATH_TO_TASK_REF.json --policy-ref PATH_TO_POLICY_REF.json --review-ref PATH_TO_SIGNED_TASK_REVIEW_REF.json --gate-id gate.unit_integration_execution --created-at RFC3339_UTC --trust-config PATH_TO_TRUST.json --artifacts PATH_TO_ARTIFACT_ROOT
```

These are **templates**, not executed shell results. Private signing keys must be managed by a genuine trusted host, never by this documentation or by untrusted ScanPlan input. Local builder logs, hashes and a builder-signed assertion alone cannot meet independent acceptance.

**Stop state:** task code tests PASS, canonical planning NOT_RUN, signed host acceptance NOT_RUN, benchmark baseline NOT_RUN, release HOLD.
