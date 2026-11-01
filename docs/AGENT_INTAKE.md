# Universal Studio agent intake and report contract

**Status:** active *agent workflow* documentation; additive to, not part of, the immutable `SRS-FREEZE-2026-10-31-v1` baseline. This contract selects report structure and evidence expectations. It does **not** change `UNIVERSAL-ARCH-001` from a design candidate, authorize execution, or promote the unreliable 003R selector.

**Purpose:** An agent given a repo or software idea should assess the **software project across its lifecycle**, not infer from a prior conversation or neighboring project that it was asked for a one-off architecture mapping. The target is temporary input to an assessment, not a registered or linked Studio product.

## 1. Identify the deliverable before using tools

| Request | Required mode | Output |
| --- | --- | --- |
| "Assess this repo", "point Studio at this", "dogfood the framework", "what does it need?" | `UNIVERSAL_PROJECT_ASSESSMENT` (default) | Current state, prioritized development gaps, risk-adaptive practices, connected specifications/tasks, and verification plan |
| "Run these tests", "verify this checkpoint", "validate implementation" | `IMPLEMENTATION_VERIFICATION` | Exact commands, pinned candidate, observed outputs/results and residual uncertainty |
| "Review this architecture/spec" | `DESIGN_REVIEW` | Evidence-linked design findings, gaps, proposed changes and review disposition |
| "Manus/another agent finished checkpoint N", "review these new research files" | `RESEARCH_CHECKPOINT_REVIEW` | Receipt/inventory, hashes, structural checks, deltas, adversarial results, provenance and an explicit accept/hold decision |
| "Map project A to B", "make an advisory crosswalk" | `CROSS_PROJECT_MAPPING` (**explicit request only**) | Advisory comparison with clear non-authority boundaries |

A previous report type is **not** inherited when the user changes the deliverable. If a corrected report already exists, review/use it as supplied evidence rather than silently repeat it. When the request lacks a report type, use the default mode; record missing facts as `UNKNOWN` instead of inventing them.

## 2. Open a scoped intake record

Record at least:

- `intake_id`, UTC date, request text/goal, chosen report mode and actor/owner.
- Subject kind (existing repository, new project, system design or research checkpoint), repository URL **when supplied**, and exact commit/revision or `UNPINNED`.
- Requested lifecycle mode: discovery, greenfield, brownfield maintenance, bug investigation, release review or retirement; select the one supported by evidence.
- Intended users, success criteria, constraints, non-goals, allowed actions, forbidden actions, risk/side-effect concerns, and unknowns.
- Studio research checkpoint/manifest **actually verified**, separate from target repository identity. Never call a supplied project link an official integration.
- Existing decision or corrected assessment and provenance, when available. Label independent observations separately from user/agent claims.

No repo link is a standing authorization to clone, execute, modify, push, release or link products. Read and scope first. When permission to execute or edit is absent, keep executable work in `PROPOSED` / `NOT_RUN`.

## 3. Baseline the target and classify evidence

For existing code, inspect the actual repo HEAD/commit, project documentation, architecture, source and interfaces, package/lock files, tests, workflows, releases and known incidents as applicable. Cite exact paths and commit hashes; identify inaccessible files and non-executed tests. For new projects, separate supplied intent from assumptions and missing requirements.

Classify each consequential statement:

- **OBSERVED:** checked against pinned bytes, command output or independent measurement;
- **DECLARED:** claimed by the owner or another agent and not independently tested;
- **PROPOSED:** recommendation or design choice not implemented;
- **UNKNOWN:** necessary information missing or inconsistent.

An upstream CI job with no executed steps is `NOT_RUN` or `INCOMPLETE`, not a code-test failure and not a PASS. Previous local test counts are `DECLARED` until results are verified for the exact candidate and environment.

## 4. Apply the universal lifecycle, not a product-specific checklist

Proceed through this risk-adaptive control loop (start at the relevant state; do not manufacture steps already done):

1. **Understand:** goals, user experience, current code/state, ownership, constraints, acceptance criteria, unknowns.
2. **Assess:** nine risk dimensions (severity, exposure, reversibility, data sensitivity, privilege, operational dependence, side effects, novelty, uncertainty) with evidence and an explicit provisional T0–T3 tier. Unknown risk cannot be silently scored low.
3. **Select research:** identify applicable `practice.*`, `gate.*`, architecture and prompt/roadmap patterns with pinned real registry IDs/source hashes and rationale; record omissions. Never auto-promote the 003R selector.
4. **Specify:** requirements, important UX flows where relevant, ADRs/design choices, task dependencies and measurable independent oracles.
5. **Propose bounded work:** paths, operations, budgets, approvals, stop triggers, rollback/recovery. Plan packets are **not** execution grants.
6. **Verify:** command-level evidence, negative controls, integrity, scope, failures/skips, candidate binding and independent review requirements. Distinguish local suite evidence from production qualification.
7. **Decide:** GO / CONDITIONAL / NO-GO or HOLD with explicit scope, unresolved blockers and decision owner; never let the model self-authorize release.
8. **Update state:** preserve candidate-linked results, superseded decisions and a clear handoff. Never rewrite prior negative observations.

If working with the kernel CLI, read [planning](../studio_kernel/PLANNING.md) and [evidence](../studio_kernel/EVIDENCE.md) first. It requires validated canonical inputs and trusted receipts for acceptance. It does **not** inspect repositories, run arbitrary projects or sign real execution.

## 5. Mandatory assessment/report layout

Every report starts with an explicit header:

```text
Report type: UNIVERSAL_PROJECT_ASSESSMENT | IMPLEMENTATION_VERIFICATION | DESIGN_REVIEW | RESEARCH_CHECKPOINT_REVIEW | CROSS_PROJECT_MAPPING
Subject: [repo/project/checkpoint]
Candidate: [exact SHA or UNPINNED]
Studio baseline: [verified freeze/checkpoint or NOT_VERIFIED]
Evidence window: [UTC dates]
Scope/actions authorized: [read-only / bounded commands / edit review]
Disposition: [GO / CONDITIONAL / NO-GO / HOLD / INCOMPLETE, with explicit scope]
```

For `UNIVERSAL_PROJECT_ASSESSMENT`, use these **nine sections in order**:

1. **Executive finding:** what the project is, where it stands, why the assessment was requested.
2. **Intake and factual baseline:** goals, users/UX, constraints, code/revision, observed artifacts, known unknowns.
3. **Lifecycle coverage:** discovery/UX, requirements, architecture, implementation, testing, release, operations/maintenance; evidence vs gaps.
4. **Risk/evidence assessment:** dimensions, provisional tier, side effects and explicit exclusions.
5. **Applicable Studio research:** exact verified IDs, origin and reasons; unresolved review decisions and omitted practices.
6. **Connected specification and task plan:** requirements → decisions → changes → independent oracles; ordered minimum work, owners/authority, stop/rollback.
7. **Verification ledger:** exact command/path/commit, environment, actual output or prior evidence source, status (`PASS`/`FAIL`/`NOT_RUN`/`INCOMPLETE`/`UNKNOWN`), limitations.
8. **Decision and blockers:** bounded readiness judgment and what would change it; do not infer production approval from unit tests.
9. **Next executable checkpoint:** 1–3 minimal steps with unambiguous acceptance criteria and handoff artifacts.

For other modes keep the same header but center the document on the asked-for deliverable and evidence. A `CROSS_PROJECT_MAPPING` must be clearly labeled **advisory only** and must not pretend to be a universal assessment. Do not silently turn the nine-section assessment into a mapping report.

## 6. Standard commands (Studio itself)

From the Studio root, with Python 3.10+ and a working package installer:

```bash
python -m pip install -r studio_kernel/requirements.txt
python -m unittest studio_kernel.test_receipts studio_kernel.test_planning studio_kernel.test_kernel studio_contracts.test_validate
python -m studio_kernel plan studio_kernel/planning_examples/cli.intake.json --output /tmp/studio-cli-intake-example
```

The final command is a **synthetic CLI planning example**, not a real evaluation of the subject repository. Its output path must not already exist. Refer to `studio_kernel/README.md`, `PLANNING.md`, and `EVIDENCE.md` for exact validation/import/acceptance options and their exit-code meanings. Test the target with its **own** reviewed commands and environment; never substitute Studio's synthetic tests for target evidence.

## 7. Checkpoint submissions from other agents

A message such as "003 finished" establishes claimed completion only. Require the submitted artifact/version, manifest, sha256, exact diff/record IDs, source links, reproducible checks, known failure log, reviewer and decision before integration. Distinguish `003`, `003R`, `003R2` and any newly named checkpoint. Stage promotion needs independent verification and a separately versioned checkpoint; no modification of the 003R freeze. MOTHERSHIP / D-004 remain out of scope unless separately authorized.

## 8. Stop rules and repository separation

Stop or hold if the target commit is unpinned for consequential claims; requirements contradict; source facts cannot be resolved; task authority/permissions are absent; critical risk is unreviewed; real oracles are unavailable; or verification lacks the required independent evidence. Report what is missing. Do not fabricate command results or mark skipped checks as passed.

Studio may **evaluate** any consenting project. It must **not** create persistent "linked products" entries, reciprocal links, forks/submodules, dependency edges or target-repo documentation solely because an assessment occurred. Any actual integration is a separate, explicit decision with its own authority, design, tests and release gates.


## 9. Greenfield experiment reference — no automatic acceptance

[Agent B ScanPlan v0.1](../experiments/agent_b_scanplan/README.md) demonstrates *writing* an intake, UX/CLI interaction, requirement-to-task specification, positive/negative test cases, evidence log and explicit HOLD. This new offline utility is not a linked product and is not a vulnerability scanner. Its local 19-test result is an observed **project** check; it does not establish that Studio's canonical planner, host executor or task-bound independent receipt verification ran. A correct agent must preserve that boundary in any report, even when the newly built code works.
