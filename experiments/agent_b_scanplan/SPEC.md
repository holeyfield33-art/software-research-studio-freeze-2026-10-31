# Greenfield specification — ScanPlan v0.1

**Intake mode:** UNIVERSAL_PROJECT_ASSESSMENT / greenfield. **Owner decision:** user requested a small new build using Studio; a minimal offline slice was chosen from an Agent B threat-model-to-test idea.

## Product intent and users

Problem: security work often jumps from untrusted threat descriptions straight to scanners or unsupported vulnerability claims. Intended users: a developer or reviewer preparing safe fixture tests. Success: given a valid offline JSON threat-model intake, return a stable plan that identifies each hypothesis and exactly what external evidence would be needed to assess it. No live scanning, monetization, web service, UX screens or multi-agent coordinator in v0.1.

## UX/UI and contracts

The interface is CLI-first. User journey: prepare JSON -> run `python -m scanplan plan` -> inspect JSON -> reviewer decides next work. Help/errors remain concise, output machine-readable, stable; screen UI intentionally not applicable. Input fields are closed: `version`, `project_id`, `subject`, `scope` (`review_owner`, `fixture_only: true`, `network_allowed: false`), and `threats` (`id`, `kind`, `component`, `observation`). Input is restricted to 1 MiB and 1..40 uniquely identified threats.

## Risk and responsibilities

Threat descriptions are **untrusted**. Privilege and side effects are deliberately limited by *not executing commands or network requests*. Review owner is only a string. Risk dimensions not independently inspected are UNKNOWN, and this package does not assign a Studio risk tier. Output must preserve `execution_authority: UNVERIFIED` and `release_disposition: HOLD`.

## Requirements and traceability

| ID | Requirement | Task | Independent oracle |
|---|---|---|---|
| R1 | Canonical deterministic JSON from valid input | T1 parser/planner | Repeated byte comparison |
| R2 | Each threat has case, positive/negative controls and independent oracle | T2 patterns | Contract assertions against all 4 types |
| R3 | Refuse unsafe/ambiguous input, duplicate IDs, extra keys and unauthorized scope | T3 guards | Malformed/negative fixtures must fail |
| R4 | Never mark execution PASS, authority GRANTED or release GO | T3 guards | Inspect complete generated JSON + tests |
| R5 | CLI produces valid JSON, refuses overwrite and symlinked input | T4 CLI | Subprocess return code, stdout, exact output bytes, canary |
| R6 | Document limitations, commands and handoff | T5 evidence/docs | Human documentation review |

## Bounded plan

T1->T2->T3->T4->T5. Allowed: edit local experimental paths, run stdlib tests. Forbidden: scan other systems, invoke Agent B active/web/network scanners, change frozen Studio archives, change external repositories, treat output as vulnerability verification. Stop on any unexpected IO, command execution, test failure or unsupported authority claim.

## Research selection (review candidates, not automatic)

- `practice.threat_modeling`: maintain hypotheses as hypotheses; justified by security-test planning.
- `practice.test_strategy`: positive/negative controls with independent oracles.
- `gate.requirements_acceptance`: tie each promised behavior to a check.
- `gate.security_risk_review`: no authorization or production claims without separate review.

These are existing frozen research IDs, used as **proposed applicability**, not a 003R selector output, signed decision or independent review. Omitted: visual UX framework, live network tests, deployment pipelines, policy enforcement adapter, additional scanner integrations. Reconsider only after a complete experiment review.

## Completion decision

Bounded local generator: testable MVP with a deterministic artifact. Studio `studio_kernel` integration: NOT_RUN. Production/security and release readiness: HOLD. A new version requires verified usability, permissions, threat coverage and an independent reviewer, not simply green unit tests.
