# Paired development comparison protocol — not yet executed

**Experiment:** STUDIO-PILOT-002 / ScanPlan malformed Unicode input. The purpose is to measure *development-process overhead, reproducibility and correctness* rather than prove that a security scanner finds vulnerabilities.

## Controlled setup

1. Pin **the same unmodified baseline** Studio commit `3795c1736b20ac3d6955e1587f4c7f7a8c778ec3` for each run. Give separate independently operated agents equivalent clean copies.
2. Supply identical task brief and tests: reject an escaped unpaired surrogate in all free-text fields; preserve valid Unicode, deterministic output and CLI no-output refusal. Control the Python version, fixtures, token/attempt budget and time window.
3. **Studio arm:** access to Studio agent intake, applicable reviewed research, canonical planner (when usable), requirement→task→oracle traceability, evidence gate and handoff.
4. **Baseline arm:** ordinary coding-agent instructions and the same explicit product requirements and acceptance tests, but without Studio's planning/research/evidence workflow. Baseline must still follow ordinary safety rules.
5. Randomize assignment and have an evaluator who did not build either change run the identical tests and inspect diffs/evidence. Do not reuse the same builder sequentially without marking contamination; the Studio-run fix is already known to this session.
6. Collect timestamps and model usage in each independent session from the host. Do not derive them from chat message timestamps. Record regression results, incomplete checks, human clarifications, code churn, unsupported authority claims and any unintended side effects.

## Metrics and precommitted acceptance

| Metric | How measured | Status |
|---|---|---|
| First-pass success | Independent acceptance test exit and failures on first submitted candidate | NOT_MEASURED |
| Final correctness | Independent 23-case suite + additional unseen Unicode controls | Studio local PASS; baseline NOT_RUN |
| Time to accepted solution | Monotonic host timer, from brief receipt to independent gate completion | NOT_MEASURED |
| Tokens and dollar cost | Actual provider usage, same model/configuration | NOT_MEASURED |
| Rework | Iterations to accepted change, unrelated lines changed, reviewer corrections | NOT_MEASURED |
| Evidence completeness | Exact commit, commands, outputs, environment, unknowns, accepted receipts | Studio local partial; signed evidence NOT_RUN |
| Scope compliance | Unexpected target edits, network calls or unapproved execution | Local fixture tests only; host containment not verified |

A valid improvement claim needs two fully completed independent arms and matching acceptance conditions. The desired 50–75% increase in development efficiency is **a hypothesis**, not a result. Successful local tests do not authorize a product or release GO.

## Next action

After the canonical planning and independently signed host gate can run, have a separate agent complete the baseline arm using a clean pinned checkout. Preserve both arm records and any failed attempts unchanged. If either arm cannot pass identical acceptance gates, report the comparison INCOMPLETE rather than comparing incomparable outputs.
