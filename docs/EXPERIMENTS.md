# Studio dogfooding and experiments

Experiments test whether **the same capable coding model is a more context-aware, surgical engineer with Studio than without it**. Score the model's working result, newly discovered *relevant* requirements, regressions, scope control and effort—not the amount of lifecycle documentation. Capture sufficient evidence to reproduce outcomes, but do not mandate a full lifecycle artifact package for every small task. See [product intent](PRODUCT_INTENT.md).

## Existing-repository pilot: STUDIO-PILOT-001

[Read the pilot](../pilots/STUDIO-PILOT-001/README.md). Uses MCP Behavior as a **temporary pinned repository assessment subject**; it does not alter or link the target repo. The early evidence-envelope validator had 7 local tests passed. Task execution, full canonical planning and external signed acceptance remain NOT_RUN.

## New-build pilot: Agent B ScanPlan v0.1

[Open the standalone code sample](../experiments/agent_b_scanplan/README.md). A small offline CLI accepts threat hypotheses and proposes reviewer-owned positive/negative tests with independent oracles. It **never scans** a website or network. A local 19-test suite passed on Python 3.13.5; the generated four-case sample is deterministic and retains HOLD status. This is a new greenfield experiment *inspired by* the earlier Agent B threat-to-test idea, not linked code or a merged product.

**Studio comparison scorecard (not yet measured):** independently scored overlooked requirements, correct working result, surgical edit scope, regressions, UX/product fit, test quality, user clarifications, actual time/tokens and unnecessary feature additions. No claimed 50–75% productivity gain without a measured baseline and repeatable comparison.

## Next experimental gate

**Pause new feature trials.** The current reports, SDLCs and example builds already supply practical evidence of broader engineering guidance. Next, streamline how a new agent consumes and preserves that guidance, using [the adaptive documentation layout](REPOSITORY_KNOWLEDGE_LAYOUT.md). Keep existing kernel/evidence functionality available for appropriate tasks; do not mandate its invocation in every edit. Measured productivity gains remain unquantified.
