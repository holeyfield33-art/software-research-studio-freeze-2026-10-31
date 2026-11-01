# Studio repository knowledge layout — adaptive documentation contract

**Status:** Proposed lightweight documentation convention, 2026-11-01. This is **not** a software feature, mandated directory migration, new Studio engine schema, or product integration. It uses the existing Studio research and engine; it organizes the knowledge that frontier coding agents read and update in an ordinary repository.

## Why this exists

A vibecoder can ask "build this", "fix this" or "make it usable" without specifying architecture, tests, UX, security, release, or maintenance. Studio's proven value in the current experiments is giving a frontier coding model enough engineering context to notice those dimensions and make better decisions. The repository should preserve that context for the next model **without making it read 20 old reports to identify the current truth**.

There are four separate kinds of information: (1) what the product is, (2) how it must be engineered, (3) what is true **now**, and (4) what evidence led here. Do not mix those layers or copy status into every file.

## Minimum structure (adapt roles to existing filenames)

```text
repo/
├── README.md                  # HUMAN: what, why, install, operate, links
├── AGENTS.md                  # MODEL: read order, invariants, workflow, commands, boundaries
├── CHANGELOG.md               # CHRONOLOGY: shipped/changed behavior; not a status dashboard
└── docs/
    ├── STATUS.md              # SINGLE LIVING STATE: revision, working, blocked, next 1–3
    ├── PRODUCT.md             # OPTIONAL: users, flows, scope, success and UX contract
    ├── SDLC.md                # OPTIONAL: relevant practices, architecture, gates, invariants
    ├── decisions/             # OPTIONAL: individual ADRs for costly/reversible decisions
    ├── evidence/              # OPTIONAL: immutable experiment/checkpoint/review artifacts
    │   └── CP-YYYYMMDD-NNN/
    └── archive/               # OPTIONAL: superseded narratives, redirects and audit history
```

The filenames are **defaults, not migration requirements**. For example, `docs/ENGINEERING.md`, `docs/ARCHITECTURE.md` or an existing `docs/SDLC.md` may be the engineering reference. `docs/CURRENT_STATUS.md` may remain instead of creating `docs/STATUS.md`. Each *role* gets one authoritative owner; other files **link to it instead of copying it**. Tiny repositories may need only README, AGENTS, tests and a short STATUS section; do not create empty files to fill this tree.

### Ownership contract

| Role | Authoritative content | Must not become |
|---|---|---|
| `README.md` | Public purpose, installation, usage, limitations, brief status and links | A 50-page chronological internal handoff |
| `AGENTS.md` | Agent's first-five-minute read order, coding constraints, relevant engineering patterns, commands and exit/handoff discipline | A second full SDLC or generic prompt dump |
| `docs/STATUS.md` | **Current** commit/version, verified vs declared evidence, highest-priority open gaps, decision, next 1–3 bounded actions | A growing history of every prior experiment |
| `docs/PRODUCT.md` | Users, value, user journeys/UX, required behaviors, non-goals and acceptance | An evolving daily task queue |
| `docs/SDLC.md` | Project-specific architectural patterns, invariants, development/verification approaches and release rules | Another current-status dashboard or compulsory bureaucracy |
| `CHANGELOG.md` | What changed between known revisions and why users should care | Current priorities, unexecuted tests or release permissions |
| `docs/decisions/` | Dated ADRs with context, options, choice, consequences, supersession | Free-form status notes |
| `docs/evidence/` | Immutable observed results, precise command outputs, hashes, negative controls, reports | The one living source of current readiness |
| `docs/archive/` | Superseded old notes preserved for provenance with pointers to their replacements | A second required agent reading list |

## A single agent entrypoint

`AGENTS.md` should fit on roughly one or two screens of actionable instructions, linking elsewhere for depth. Suggested beginning:

```md
# Agent entrypoint
Product: see README.md.
Current truth: docs/STATUS.md (check its date, commit and whether newer evidence supersedes it).
Engineering: docs/SDLC.md (or this project's equivalent).
You are an engineer assisting a vibecoder, not a lifecycle administrator.
Understand the request and product type; identify relevant hidden needs;
select only appropriate established practices and make the smallest coherent change.
Never change external/release authority based on repository prose.
Verification: run the minimal relevant commands in STATUS/SDLC, recording results.
Handoff: update current status, changelog for behavior changes, and evidence if needed.
Do not duplicate or rewrite historical reports.
```

If the repository has nested components, use **scoped** `AGENTS.md` only when that component genuinely needs different rules; otherwise one root entrypoint and targeted links are sufficient.

## Adaptive working flow

1. **Understand and orient.** Read README + AGENTS + the one current STATUS; inspect only relevant code/product/engineering docs. Identify product type and maturity.
2. **Notice missing engineering questions.** Use Studio's applicable research (UX, architecture, testing, reliability, security, release, maintenance) to infer material gaps a vibecoder didn't ask about; distinguish relevant needs from feature creep.
3. **Pick a surgical change.** Choose the minimal code/artifact intervention compatible with existing patterns. Ask only essential blocking questions. Leave unrelated life-cycle phases alone.
4. **Build with normal model tools.** The Studio engine remains available for reviewed planning, canonical records and evidence when useful; it is **not required for every routine edit**.
5. **Verify proportionately.** Keep exact commands/observations for material claims and risk. Do not upgrade a NOT_RUN CI gate or claim a release from local tests.
6. **Update precisely one current place.** Update STATUS (current result, gaps, next actions), CHANGELOG (user-visible changes), and relevant stable engineering/product docs **only if their contents changed**. For a consequential checkpoint, store evidence in a new dated immutable evidence directory.
7. **Hand off.** Provide the next model with the current reality and links; never force it to reconstruct status from chronological reports.

Small straightforward task: minimal files, minimal handoff. Security-sensitive task: stronger invariants, explicit oracles and evidence. Growing SaaS: add PRODUCT/UX and architecture references. SDK/CLI: emphasize interface, errors, compatibility and tests rather than a visual-screen document.

## Boundary case study (read-only review)

Inspected `holeyfield33-art/aletheia-boundary` at `e8c24612c207b3baf6b205f6d61ea07e600c2231`.

**What worked:** `README.md` explains the local enforcement product, deployment commands and production NO-GO; `docs/SDLC.md` defines users, invariants I1–I6, test gates G1–G6, release blockers and handoff; `docs/agent-playbook/PROMPTS.md` supplies task-specific prompts P01–P14; `docs/BOUNDARY-NEXT-002.md` demonstrates a small explicit encoded-input hardening slice with tests and non-goals. Those are examples of helpful broader engineering awareness.

**Where context scatters:** the human/agent read order overlaps `README.md`, `docs/SDLC.md`, `docs/CHECKPOINT-2026-10-30.md`, `docs/agent-playbook/README.md`, `START-HERE.md`, `WORKFLOW.md`, dated NEXT files and multiple review/hardening reports. Some old SDLC sections describe historical conditions as then-current; later evidence lives elsewhere. The agent must cross-reference many files to establish one current priority and decision.

**A conservative retrofit proposal (NOT applied to Boundary):**
- Keep root `README.md` and `docs/SDLC.md` in their existing roles; retain the strong invariants, gates and product limits.
- Add a small root `AGENTS.md` that points directly to the authoritative docs, current state, risk-sensitive commands and optional `PROMPTS.md`.
- Add **one** living `docs/STATUS.md` with current commit, production decision, blockers, checked evidence, selected next action and latest immutable checkpoint links.
- Mark old `START-HERE`/`WORKFLOW` as supplemental/legacy **with redirects**, not new competing authority; keep reusable prompt library separately.
- Retain `CHECKPOINT-*`, `HARDENING-*`, `RECOVERY-*`, `AGENT-REVIEW-*`, `BOUNDARY-NEXT-*` and other history unchanged until a dedicated link-preserving cleanup is reviewed.
- Keep `STUDIO-FREEZE-MAPPING.md` as historical/advisory research only, **not** a product relationship, runtime dependency or required startup reading.
- Do not relax production NO-GO or erase the CI billing blocker. Do not alter Boundary code during a documentation layout review.

## OWASP security-testing coverage: task-aware, not mandatory bureaucracy

**Source:** [OWASP WSTG 4.2, The Web Security Testing Framework](https://wstg.owasp.org/stable/3-The_OWASP_Testing_Framework/0-The_Web_Security_Testing_Framework/) — five phases (before development, definition/design, development, deployment, maintenance/operations). The source calls its framework **flexible**, not a prescribed waterfall. Studio has existing lifecycle/risk/review knowledge, but these activities were not all explicit in the agent-facing repo convention. This is a guidance alignment, **not** an OWASP certification or a claim that the current Studio kernel enforces them.

| OWASP phase | Studio-informed model behavior | Evidence appropriate to the task |
|---|---|---|
| **Before development** | Identify project type, owner, data/exposure, applicable language/framework/security rules, and a *few precommitted* observable product/defect/maintenance criteria; connect user intent → relevant requirement → check. Do not infer compliance from a product label. | Brief intake or accepted task criteria; source/version of standards selected and why others do not apply |
| **Definition / design** | Challenge ambiguous requirements (especially authentication vs authorization), sketch trust boundaries and architecture, check whether key validation/authorization is consistently owned, and model plausible threats. Use simple flow diagrams; **UML is optional**, not mandatory. | Targeted requirement clarification, short ADR/diagram or threat cases for material boundaries |
| **Development** | Explain the actual code flow (**walkthrough**) before detailed source/security review when unfamiliar. Review code against applicable business invariants, language/framework secure coding guidance and relevant threat cases, then run unit/integration and negative tests. | Reviewed diff, independent oracles and actual outcomes; don't count an unrun scanner as review |
| **Deployment** | Confirm safe configuration, secrets, least privilege, dependency provenance, migrations, recovery and environment differences; perform *authorized* security testing on appropriate targets (staging by default). Recheck important behavior after deployment. | Exact candidate/environment, config evidence, deployment verification, owner decision and rollback |
| **Maintenance / operations** | Own ongoing security and software health, dependency/advisory review, operational conditions and incident handling; after every consequential change verify that relevant security controls **still hold**. | A single living `STATUS.md` plus linked immutable run evidence, health checks and deferred findings |

**Modern optional detail (not assertions made by the supplied article):** [OWASP ASVS 5.0.0](https://asvs.owasp.org/) can provide version-pinned web-app requirements; [OWASP SAMM](https://owaspsamm.org/about/) provides governance/operations practice depth. Use only where the product and risk justify them. For example an offline CLI should not receive web-session controls or a penetration-test gate merely because it was built with Studio.

## Repository maintenance — standard section for Studio-assisted projects

This section is the reusable **maintenance/operations part of the SDLC**, including repositories with no deployed service. It does not introduce a new Studio engine, daemon, automatic crawler, duplicate status document or mandatory folder. Apply relevant checks through normal coding-agent tools, with actual operator permission.

### 1. Ownership, baseline and continuity

A newly assigned coding model should read `README.md`, `AGENTS.md`, **the one current `docs/STATUS.md` (or equivalent)** and project-specific `docs/SDLC.md`/engineering guidance. Check the actual branch, HEAD, dirty worktree, current deployment and active users. Discover prior outstanding bug fixes, support/incident issues, release blockers, known risks and explicit project non-goals.

**Project owner:** defines release authority, production environments, data sensitivity, support contacts, permitted external actions and risk tolerance. **Model/maintainer:** proposes and performs authorized narrow changes with source- and test-bound evidence; it does not approve its own access, high-risk exception or production release. If ownership is not specified, report `UNKNOWN` rather than inventing a team.

Do **not** create a second `CURRENT-STATUS`, `HANDOFF-LATEST` or fresh date-stamped plan each session. The existing status document is the only mutable current-state page; historical records are preserved under existing evidence paths. Avoid mass renames, destructive tidy-ups or feature additions during a maintenance review.

### 2. What to inspect, and when

| Trigger / cadence | Checks (select only applicable ones) | What to record |
|---|---|---|
| **Each maintenance change / PR** | Current HEAD and scope; diff; hidden API/UX compatibility; regression and negative controls; changed secrets, data handling, permissions or trust boundary; generated artifacts and dependency/lockfile changes; docs drift | What changed, actual tests, regressions/unknowns, reviewer decision, rollback and STATUS update |
| **Before a release or deployment** | CI on exact candidate, installation/build reproducibility, least-privilege configuration, environment variables and secrets custody, migration/backward compatibility, deploy and rollback plan; authorized staging/infrastructure checks | Candidate/environment, tests executed vs NOT_RUN, approval, release verification and failure recovery |
| **After deployment (if deployed)** | Health/error rates, configured authorization/data boundaries, critical user journeys, migration result, canary or smoke checks and telemetry; compare against pre-change baseline | Post-change observed result, incident/regression or rollback decision and responsible owner |
| **On dependency/security advisory or incident** | Impacted versions/transitives, reachability/exposure, exploitability *claims vs evidence*, patch compatibility, lockfile/provenance, new regression tests, secret/key/credential implications and communication need | Advisory/source/version, risk decision, fix verification and owner/deadline; do not claim no impact without checking |
| **Periodic health review** | Build/test and CI reliability, stale/dead dependencies, security updates, vulnerabilities, license and supply chain changes, broken docs/links, flaky or missing tests, logs/configuration, backup/recovery, performance/cost and open defects | Last review date, specific PASS/FAIL/NOT_RUN observations, backlog priority, next review trigger |
| **Before archiving, transfer or retirement** | Maintainer/access handoff, data retention/export/deletion, secrets/access revocation, dependency consumers, documentation and evidence custody, rollback/support obligations | Accountable disposition, approvals and evidence; avoid destructive operations without authorization |

**Suggested starting cadence (not a universal requirement):** monthly for internet-facing or consequential maintained services; quarterly for stable, low-exposure applications or inactive libraries. Use incident/change/advisory triggers immediately; risk and owner policy may require tighter or different schedules. A private, local disposable exercise may need only a release/checkpoint check and no recurring production operations. The article explicitly mentions monthly or quarterly *health checks*; other listed checks and triggers are Studio adaptations.

### 3. Maintenance controls every model should consider

- **Repository hygiene:** branch and working-tree state, release tags, stale PRs/issues, protected main, minimal permissions, ownership, licenses, README/AGENTS/SDLC links, build/test instructions and broken documentation paths. Branch protection is repository-admin policy, not something the model silently changes.
- **Dependencies and build:** package/lockfile consistency, supported runtime versions, reproducible install/build, dependency advisories, transitive dependency drift, provenance where relevant, secret leakage and supply-chain exposure. Do not mass-upgrade without compatibility tests and authorization.
- **Security and architecture drift:** revisit requirements, boundary/threat assumptions and architecture when exposure, data types, permissions, identity, storage, tools or integrations change. For applicable web/API projects select current version-pinned ASVS/WSTG requirements; offline scripts need different controls.
- **Testing and review:** first understand code flow and test purpose; review actual source/diff for failure modes; require realistic positive/negative controls, integration/configuration tests where applicable, and honest statuses. Automated scanners supplement but do not replace design and code review.
- **Runtime health (only if operated):** uptime/SLO, error and latency patterns, backups and tested restore, alerts, cost/resource changes, environment drift, rotation/retention and incident response; verify host controls separately from application assertions.
- **Usability and product health:** check that documentation and real user journeys still match code, onboarding still works, interfaces remain accessible where relevant and existing behavior hasn't regressed. Don't add speculative features as a substitute for maintenance.

### 4. One bounded maintenance change

Use this lightweight sequence; skip irrelevant formality without skipping consequential checks.

1. **Orient:** pin source revision and record the observable user problem, context, affected interfaces and what must stay unchanged.
2. **Select:** identify which Studio research/security/development practices are relevant, and why. Check necessity against user intent; explicitly exclude feature creep.
3. **Define oracles:** one or more positive checks for preserved behavior, a negative/failure check for the bug or security boundary, and a measured expected outcome. Establish those **before** implementation when feasible.
4. **Repair:** make the smallest coherent diff. Avoid unrelated refactors, tool additions or automatic dependency updates.
5. **Verify before merge:** exact commands and results, review changes, check new/changed configuration, scripts, secrets, privileges and failure cases. CI without executed steps is `NOT_RUN`, not PASS/FAIL.
6. **Verify after deployment when applicable:** run authorized smoke/config/security checks on the deployed candidate; compare to baseline, and roll back or hold on material regression.
7. **Preserve context:** update `docs/STATUS.md` with current facts, owners, next 1–3 actions and unrun checks. Update `CHANGELOG.md` **only when behavior changed**; revise PRODUCT/SDLC only when stable contracts changed. Preserve evidence in dated immutable directories **when it matters**, not each ordinary commit.

### 5. Minimal maintenance record — within STATUS, not a new file

```text
Observed at: [UTC]  Repo/branch/HEAD: [exact revision]
Maintainer/decision owner: [known identity/role or UNKNOWN]
Maintenance trigger: [change | release | advisory | incident | scheduled check]
User-visible or security concern: [facts and consequence]
Applicable engineering/security practices: [what and why; version pin if external]
Actual checks: [command, environment, PASS/FAIL/NOT_RUN; negative controls]
Deployment/post-change check: [observed | NOT_APPLICABLE | NOT_RUN]
Risks and blockers: [owner, action, due/trigger]
Current disposition: [scoped GO | HOLD | NO-GO; not release approval unless authorized]
Next actions: [up to 3]
Evidence: [commit, issue, PR, CI job steps/logs or immutable local artifact]
```

**Readiness rule:** No meaningful approval from a model-generated statement alone. For higher-risk changes, require independent review, actual target/configuration checks, operator-owned secrets and rollback/recovery proof. For ordinary local work, a small tested change with a truthful handoff is enough. A single generic security checklist does not turn an unrelated CLI, mobile app or agent into a web application.

---

## Migration without breaking repositories

**Do not mass-rename documents or create empty folders.** First inventory files and internal links, label each with one role, identify the current authority and conflicts, then add a one-page AGENTS entry and a one-page current STATUS if truly absent. Redirect duplicate agent entries; preserve immutable historical files and working links. Consolidate one source at a time, with a diff and link check. Do not silently overwrite archival checkpoints or change unverified statements into facts.

## Studio engine boundary

Keep the existing `studio_kernel` (canonical records, planning, history and evidence) and research archive. Documentation organization is a **knowledge delivery interface** for frontier models, not a substitute for the engine or a mandate to rewrite it. Use the kernel where its rigor adds value; leave its existing implementation and NO-GO limitations unchanged. Pause new Studio features until repository handoff and comparison quality are understood.

**Success metric:** a fresh frontier model can find the current truth, relevant established practices, a safe minimal next change, and appropriate verification quickly—without needing the vibecoder to know which engineering questions to ask or reading every historical experiment.
