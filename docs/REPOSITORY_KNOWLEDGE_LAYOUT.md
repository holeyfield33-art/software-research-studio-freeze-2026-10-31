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

## Migration without breaking repositories

**Do not mass-rename documents or create empty folders.** First inventory files and internal links, label each with one role, identify the current authority and conflicts, then add a one-page AGENTS entry and a one-page current STATUS if truly absent. Redirect duplicate agent entries; preserve immutable historical files and working links. Consolidate one source at a time, with a diff and link check. Do not silently overwrite archival checkpoints or change unverified statements into facts.

## Studio engine boundary

Keep the existing `studio_kernel` (canonical records, planning, history and evidence) and research archive. Documentation organization is a **knowledge delivery interface** for frontier models, not a substitute for the engine or a mandate to rewrite it. Use the kernel where its rigor adds value; leave its existing implementation and NO-GO limitations unchanged. Pause new Studio features until repository handoff and comparison quality are understood.

**Success metric:** a fresh frontier model can find the current truth, relevant established practices, a safe minimal next change, and appropriate verification quickly—without needing the vibecoder to know which engineering questions to ask or reading every historical experiment.
