# STUDIO-KNOWLEDGE-003R — Corrective directive: prove selection, not just fixture consistency

**To:** independent research/QA agent  
**Mode:** research-only corrective increment. Begin from frozen `STUDIO_KNOWLEDGE_003_checkpoint.zip`; never overwrite it. Do not touch Block-Wise Studio, hosted systems, commercial product code, or the 001/002 originals. **Do not launch Stage 004.**

## Outcome

Prove that a small, deterministic, evidence-grounded selection policy can independently compute a tailored SDLC, agent coding prompt contract, and dependency-aware roadmap for the three known project archetypes **and deliberate variations**. Keep 003's dataset as the baseline. Do not add unrelated software categories, agents, search, frontend, vector DB, deployment, payments, or broad knowledge gathering.

## P0-A — create one minimal independent selector

1. Define an input contract with `software_type_ids`, scoped machine-readable requirement facts, explicit `unknown` versus false, approvals/authority, and optionally untrusted descriptive text. State that descriptive text is non-authoritative *unless* parsed into reviewed structured facts. Validate required facts and contradictory input states; for material contradictions, return `INCOMPLETE` and list missing/contradictory facts.
2. Implement a **read-only, deterministic research selector** (CLI accepted; no Studio integration). It must accept `brief.json` and the versioned knowledge graph and produce a candidate `selection.json`, `rejections.json`, and `decision_trace.json` from explicit rule conditions. It **must not read any `expected_*` or golden oracle files** while making decisions. Do not hardcode fixture IDs as a branching substitute for requirements.
3. Define stable rule IDs, priorities and exclusion precedence. Rules must distinguish `RECOMMENDED`, `CONDITIONAL`, `INAPPLICABLE`, and `INCOMPLETE`; reject unsafe defaults, unsupported categories, contradictory requirements, unavailable approvals, and evidence gaps. Preserve stage/gate status `INCOMPLETE` absent actual candidate-specific test/run evidence. No fabricated PASS.
4. Each mandatory selected practice/stage/gate/prompt/roadmap action must include `rule_id`, factual predicate matches, scope conditions, exact `record_id`, and source/claim locator. Where actionable dependencies are claimed, traverse applicable `requires`, `verified_by`, `produces`, and related typed edges rather than stopping at `software_type -> record -> source`. Distinguish descriptive examples from hard prerequisites.
5. Never infer multi-tenant isolation, billing, cloud hosting, Kubernetes, or vector databases from the software category alone. Apply explicit feature-creep exclusions unless the brief demands and justifies them.

## P0-B — use oracle independently

1. Freeze a separate golden expectation set authored *without* relying on the selector's output. Test **exact selected IDs, rejected IDs, status classifications, rule IDs, non-applicable decisions, gate evidence status, and required deliverable/task roles**, not just ID membership.
2. Preserve the original three base scenarios and shared negative-control branch.
3. Add at least **three structured-fact counterfactuals per base scenario** (nine or more total). Suggested controls:
   - Agent: no write tool; write tool but no accountable approver; explicit production request without candidate-bound test evidence.
   - API: public unauthenticated read-only API; explicitly multi-tenant data; a project requesting queues but lacking load/operational justification.
   - CLI: local destructive overwrite request; network-enabled upload requested; reusable library distribution requested without service deployment.
4. Add four targeted mutation tests, expected to FAIL: flip recommended status with golden fixed; reverse critical rejection rationale/typed reason; insert fake test/deployment PASS acceptance evidence; contradict free-text brief and authoritative facts (or explicitly remove descriptive text from all decision outputs and document it as non-authoritative).
5. Verify unknown category IDs, source scope mismatch, unsupported features, absent authority, changed standard edition and unexecuted tests all yield explicit abstention or conditional handling rather than silent guesses.

## P1 — protect catalog and provenance

- Keep all inherited 001/002/003 stable IDs and typed graph preservation; record added rules/versions and rationale in migration/change log.
- `jsonschema`, graph integrity, source claim locator, roadmap DAG, read-only operation and non-destructive reapplication must pass.
- No required action can cite only a broad category name or unscoped source. No `PASS` for tests/CI/release without candidate ID, linked executed result, and required approvals.
- Treat source-claim provenance honestly: source guidance vs observed source file vs synthesis vs actually executed results. Do not broaden the spot-check into a generalized research sprint.
- Provide a detached archive SHA-256 file beside the return ZIP, or explicitly revise the archive-verification contract to not promise one. The delivered archive must pass both internal member hashes and the archive verifier.

## Acceptance gates

- A clean-run selector, with no access to expected outputs, computes each of three base outcomes matching a frozen independent oracle.
- Nine or more counterfactual structured briefs produce the correct changed decisions; all four independent adversarial controls and baseline negative controls fail/abstain where appropriate.
- All selected required actions have machine-checkable facts/rule IDs/typed paths/source locators; contested/missing evidence returns `INCOMPLETE`.
- Zero mandatory false obligations in offline CLI; no unauthorized/unsafe agent side-effect approval; API authorization conditional on actual auth/user/tenant facts.
- 001, 002 and 003 parent IDs/digests and no destructive data loss; base and typed schemas, graph and roadmap DAG, tests and manifest all PASS.
- Report separately: **dataset integrity**, **novel brief selection reliability**, **safety abstention**, and **Studio integration readiness**. Even a 003R GO does not authorize production or Studio code changes.

## Return package

`STUDIO_KNOWLEDGE_003R_checkpoint.zip` containing versioned data/rules, schemas, three base fixtures, >=9 counterfactual briefs and independent expectations, selector and tests, human-readable rule table, source/decision path traces, mutation-test results, manifest/checksums, and a concise GO/PARTIAL/NO-GO decision report. Include the detached ZIP sidecar if promised. Preserve original 003 ZIP immutably.

**Do not start Stage 004 or commercial features in this phase.**
