# Design decisions

- **ADR-001 — A CLI, not an active scanner.** Goal is to test Studio's full design/test documentation loop without host/network attack surfaces. Rejected: extending Agent B's incomplete active/network scanner as the first greenfield project. User asked for a quick side experiment, not a security certification.
- **ADR-002 — JSON with exact allowed keys.** Standard-library validator and deterministic SHA-256 of canonical intake prevent ambiguous attribution of the plan. This is not a signed receipt or authenticated project candidate.
- **ADR-003 — Every proposed test must have positive, negative and independent oracle statements.** Prevents a hypothesized attack becoming a finding just because a tool said so.
- **ADR-004 — No false success.** `NOT_RUN`, `UNKNOWN`, `UNVERIFIED`, `HOLD` fixed until an independent host later supplies actual scoped evidence. No real test execution in v0.1.
- **ADR-005 — No product linkage.** The example lives in a Studio `experiments/` directory as a disposable case study. It is not a persistent registration or dependency on Agent B or MCP Behavior, and does not modify their code.
