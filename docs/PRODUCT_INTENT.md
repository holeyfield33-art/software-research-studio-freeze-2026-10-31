# Studio's product intent — frontier-model engineering intelligence

**Authoritative operating interpretation, 2026-11-01.** This document is a product/design correction, not a new frozen research checkpoint, a selector promotion or a runtime implementation.

## What Studio is

Software Research Studio is a **contextual engineering knowledge and judgment toolkit for frontier coding models**, particularly when users are vibecoding and do not know which technical questions to ask.

The frontier model remains the engineer, author and executor within its existing tool permissions. Studio augments that work with curated software engineering knowledge: architecture patterns, software-development and prompt practices, roadmap/sequencing patterns, UX and product-design considerations, verification gates, reference projects, supporting sources and the relationships among these records.

Studio's value is **better decisions and changes at the moment of need**, not compulsory lifecycle management or autonomous project orchestration.

## The user's actual experience

A user can say: **"Build a SaaS app for appointment requests"**, **"Fix this fragile repository"**, **"Make this CLI ready for people to use"**, or **"Add this feature without breaking the existing product."** They should *not* need to separately request discovery, accessibility, error handling, data model, auth boundaries, migration safety, tests, deployment readiness or maintenance strategy.

The model should use Studio to:
1. **Inspect enough context** to infer product type, maturity, user journeys, constraints, prior decisions, existing conventions and gaps. Distinguish observed facts from assumptions.
2. **Identify high-leverage blind spots** a non-engineer probably missed. Ask at most the essential blocking questions; otherwise continue with explicit, reversible assumptions.
3. **Select and justify only relevant established patterns.** Use verified research identifiers and supporting sources when available; leave uncalibrated/unsupported choices as suggestions rather than automated verdicts.
4. **Choose the smallest coherent change** that satisfies the user's actual goal while fitting existing design, minimizing churn, and retaining interoperability.
5. **Build or repair with existing model tools.** Do not force a separate lifecycle engine, full report, custom executor, database, signed-receipt workflow, or arbitrary acceptance process for ordinary low-risk tasks.
6. **Verify proportional to risk** with focused tests, negative controls, previews or independent evidence when needed. Never invent a pass.
7. **Return the useful output:** working code/artifact and a concise explanation of the decisions, important hidden gaps and what remains. Preserve a small handoff/decision note only when it will help future work.

An optional deeper architecture, UX, safety, security or release review should be applied when the task warrants it, not as boilerplate.

## Operating modes (intensity, not workflow stages)

| Mode | Appropriate request | Model behavior |
|---|---|---|
| **Build** | Create a new project or feature | Fill critical product/engineering omissions while delivering the working requested slice |
| **Maintain** | Repair/refactor/extend existing code | Respect conventions; diagnose root cause; patch surgically; test relevant behavior |
| **Improve** | User asks what's missing or how to make a build usable | Identify the highest-impact blind spots, prioritize them and implement within scope |
| **Review** | Explicit audit or architecture/UX request | Produce a scoped, evidence-based report; include omissions and next actions |
| **Research** | Checkpoint, registry or practice questions | Preserve sources, IDs, hashes and uncertainty; do not silently promote experimental selector results |

Detailed report templates, canonical records, risk classifications and signed evidence remain available for projects and tasks that *need* them. They are not the default user interaction and their existence does not prove that Studio is valuable.

## Avoid these failure modes

- Mistaking **coverage of every lifecycle stage** for engineering intelligence.
- Turning a simple bug fix into an elaborate planning bureaucracy.
- Producing a nine-section document instead of the requested working change.
- Imposing a generic architecture on an existing project or building unnecessary infrastructure.
- Treating missing context as license to invent user requirements or silently expand scope.
- Applying research without software-type relevance or without distinguishing curated checks from generalizable selection.
- Confusing a test suite of the demonstration project with a test of **Studio's effect on model performance**.
- Requiring signed host receipts for every routine edit; retain stronger verification for consequential claims and autonomous operations.

## Research and implementation boundaries

The original 001/002/003/003R research archives and their IDs remain unchanged. 003R novel-input selector generalization is **NO-GO**. The partial canonical Studio kernel is a possible support component, **not the product definition or a prerequisite to every useful interaction**. MOTHERSHIP is separate. Evaluating another repository does not create a product link.

The central research question is: **Does access to Studio's appropriate engineering knowledge and context allow a frontier model to make materially better product and maintenance decisions than the same model without it, when given a normal underspecified vibecoder request?**

## Appropriate experimental design

Pin comparable tasks and repositories; use the same model and equivalent tool permissions in two independent arms. Ask in ordinary vibecoder language, without enumerating all overlooked engineering requirements. The Studio-assisted arm may consult relevant verified patterns, references and guidelines; the control arm uses ordinary model/tool behavior. An independent reviewer scores:

- **Useful omissions discovered** (gaps neither requested nor invented)
- **Working result and acceptance correctness**
- **Minimality/surgical precision** (unnecessary files, churn, regressions)
- **UX and product fit** for the actual software type
- **Test quality and defects missed**
- **Amount of user engineering guidance needed**
- **Effort/cost** (actual recorded tokens, time, interventions)
- **Maintenance/handoff clarity**

Count helpful inferred needs separately from unrequested feature creep. Compare outcomes, not how many documents, gates, records or tool calls were produced. The proposed 50–75% improvement is an **unverified hypothesis**, not a claim.

Read [agent instructions](../AGENTS.md), [intake](AGENT_INTAKE.md), and [experiments](EXPERIMENTS.md) for execution details.
