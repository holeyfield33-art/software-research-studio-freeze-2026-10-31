# Software Research Studio — development changelog

This file records **additive Studio development changes**. Frozen research manifests, original reports and historical checkpoint identities remain unchanged.

## 2026-11-01

- Verified a resubmitted `STUDIO-KNOWLEDGE-003` research archive against the preserved original; scope-limited verification receipt merged in PR #5.
- Standardized agent routing with `AGENTS.md` and `docs/AGENT_INTAKE.md`; default is universal project assessment, not architecture mapping or product linking.
- Merged STUDIO-PILOT-001's pinned brownfield intake/evidence negative-control checkpoint (PR #6); complete lifecycle verdict remains HOLD.
- Replaced outdated archive-only top-level README with active Studio guidance and current truth-of-implementation matrix.
- Added user-facing getting-started, status and experiments guides.
- Started Agent B ScanPlan v0.1 as a standalone offline greenfield experiment, with deterministic CLI output, test controls and explicit limitations. Local execution: 19 tests PASS (including malformed-kind regression). **No full Studio kernel plan/host acceptance ran** for this greenfield build.

### OWASP SDLC alignment and repository maintenance guidance

- Reviewed the OWASP Web Security Testing Framework's five testing phases against existing Studio engineering guidance. Documentation gaps were most pronounced around early security standards/metrics, distinction between walkthrough and code review, deployed-configuration verification and recurring maintenance.
- Added a task-adaptive OWASP phase crosswalk and a **repository maintenance** section to the existing `docs/REPOSITORY_KNOWLEDGE_LAYOUT.md`; linked from agent intake, AGENTS and getting started rather than creating another competing status or SDLC file.
- Defined change-triggered and risk-based periodic health checks, dependency/advisory response, post-deployment verification where relevant and a minimal single-STATUS maintenance record.
- Documentation-only guidance. **No** Studio engine changes, frozen-research edits, automatic maintenance execution, third-party repo changes, or OWASP compliance/certification claims.

## Preserved historical boundaries

`SRS-FREEZE-2026-10-31-v1` and `STUDIO-KNOWLEDGE-003R` remain immutable. Novel-input selector generalization and product integration remain NO-GO. MOTHERSHIP/D-004 remain separate.


### Studio purpose and operator experience correction

- Defined the product as **contextual engineering knowledge and decision support for frontier models helping vibecoders**, rather than an autonomous SDLC controller.
- Set `MODEL_ASSISTED_ENGINEERING` as default for normal build/fix/maintain requests. Formal assessment reports and canonical planning are optional/intensity-dependent.
- Updated README, agent intake, getting started, experiment scorecard, current status and handoff without changing frozen research or partial runtime kernel.
- Reviewed Aletheia Boundary's SDLC/playbook/checkpoint files and proposed a **role-based, adaptive repository knowledge layout** so agents find current context without reading scattered reports. Existing research and canonical Studio engine remain in place; new feature expansion paused. Initial 19-test ScanPlan MVP and merged 23-test follow-up PR #8 remain distinct; no quantified performance increase claimed.

### STUDIO-PILOT-002 — bounded Unicode input repair

- Added a failing negative-control suite for escaped unpaired surrogates in four free-text inputs (red phase: 1 failure, 4 errors).
- Rejected surrogate code points at input validation; added four tests and reproduced **23/23 PASS** with unchanged deterministic example output.
- Preserved exact local source Git blob identity and machine-readable executed-command evidence; published a scoped trial record and an unexecuted A/B protocol.
- Marked canonical Studio planning, trusted signed host evidence and independent baseline as **NOT_RUN**; no GO or productivity gain claim.

### Standalone greenfield extraction / documentation boundary

- Verified the independent [ScanPlan repository](https://github.com/holeyfield33-art/ScanPlan), created from the Studio-born greenfield experiment; its exact baseline core matches the Studio Unicode-corrected blob.
- Preserved `experiments/agent_b_scanplan/` as historical sample/evidence rather than a second active application repository. ScanPlan merged its local test/CI portability PR #1 (24/24 local Linux tests, hosted CI job steps NOT_RUN) and now owns active development and status independently.
- No changes to Studio runtime engine, frozen research, selectors, checkpoints, or ScanPlan application code in this Studio documentation update. Studio feature expansion stays paused.
