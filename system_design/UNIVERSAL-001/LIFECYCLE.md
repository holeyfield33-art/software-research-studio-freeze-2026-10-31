# Lifecycle and recurring research questions

The seven frozen SDLC stages organize responsibilities. They are iterative concerns, not a mandatory sequence of isolated document approvals. Existing projects can enter through maintenance, verification or design; the system reconstructs missing prerequisites only where the current decision requires them.

At every concern, answer the same seven questions using applicable research and observed project context:

1. Architecture: what structure and boundaries does this work require, and why?
2. Prompts: what instructions, permissions, inputs and stop conditions must a human or agent receive?
3. Roadmap: what must happen first, and what is the smallest useful increment?
4. Gates: what observable evidence would establish readiness or failure?
5. References: what comparable implementation illustrates an option, and what differs here?
6. Sources: which exact research records support the decision, with what limitations?
7. Relationships: which dependencies, conflicts and downstream artifacts does the decision affect?

An unanswered question is recorded as unknown or not applicable with rationale. The system must not manufacture a reference project or force an architecture pattern to fill a template.

| Concern and frozen ID | Required inputs | Produced work | Exit decision / rework |
|---|---|---|---|
| Discovery — `sdlc.discovery_scope` | Problem, users, intended outcomes and constraints | Bounded scope, success measures, exclusions, assumptions, project profile | Proceed when the outcome and bounds are understandable; research or stop when value is unsupported |
| Requirements and risk — `sdlc.requirements_risk` | Scope, relevant operational facts, stakeholder needs | Testable requirements, quality attributes, risk register, acceptance oracle plan | Resolve consequential ambiguity or block affected decisions; changed needs reopen scope |
| Architecture and design — `sdlc.architecture_design` | Requirements, risk, observed implementation and constraints | Alternatives, decisions, interfaces, data model, relevant UX/interaction designs, dependency and verification plans | Justify tradeoffs and feasibility; uncertainty triggers a bounded experiment |
| Implementation — `sdlc.implementation` | Ready task, required design decisions, real permissions, pinned inputs | Reviewable changes, dependency updates, execution records and maintained artifacts | Candidate is ready for independent verification; blocked or failed attempts return to planning |
| Verification — `sdlc.verification` | Candidate revision, acceptance criteria and applicable risk controls | Executed evidence, independent findings, regression comparison, manual evaluations where needed | Pass only supported properties; failures return to responsible tasks or requirements |
| Release — `sdlc.release` | Known candidate, applicable evidence, owner and recovery constraints | Release decision, provenance, packaging, migration and rollback instructions, communications | Authorized delivery with known residual risk; otherwise block or defer |
| Maintenance — `sdlc.maintenance_feedback` | Operational evidence, incidents, dependency/support signals and user feedback | Diagnosis, corrective tasks, support/deprecation decisions and proposed knowledge improvements | Verify resolution and feed changed facts back through relevant concerns |

For example, a local one-command utility may use a compact project packet and output/exit-status tests; a multi-tenant service may require tenant isolation, deployment recovery and operational evidence. The same record structure supports both. Work is selected from demonstrated needs, not inflated to match the most complex project.

No frozen-source record certifies a project. `RESEARCH_MAPPING.json` binds this design's stage references and foundations to preserved records and inherited sources. Detailed field-level schema and source-to-requirement coverage remain next-stage deliverables.
