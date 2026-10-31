# Round 2 adjudication register

| ID | Topic | Decision |
|---|---|---|
| D01 | Independence | Keep all three source reports independent; synthesize only afterward |
| D02 | Lifecycle | Eight iterative UX concerns, not rigid waterfall; accessibility begins upstream |
| D03 | Async edits | Require correctness under latency, not universal draft buffering |
| D04 | Navigation | No universal three-level maximum |
| D05 | Styling | Scoped tokens and justified exceptions; no universal px ban |
| D06 | State models | Formal machines only when complexity warrants |
| D07 | Accessibility | Applicable WCAG 2.2 checks plus manual verification; no scanner-only conformance claim |
| D08 | Traceability | External mapping first; data-req optional and not proof |
| D09 | Ratchet | Compare finding identity, severity and tool version, never counts alone |
| D10 | Verification | Separate structural, behavior, accessibility, usability and release evidence |
| D11 | Standards | Applicable references, not certification |
| D12 | Outcomes | 50–75% and 7/7 remain unverified |
| D13 | SurfaceTrace | Inspect actual revision before selecting tasks or declaring verified features |
| D14 | JSON Schema | Document stdlib subset limitations; no full 2020-12 conformance claim |
| D15 | Governance | Human-approved exceptions and baseline changes; no silent refresh |

## DeepSeek corrections before implementation
- Baseline counts 37/11/4 are illustrative, not observed.
- CSS focus-visible is not an ARIA attribute.
- Native button does not require redundant role=button.
- Context cannot be reduced to fixed ARIA role mapping; inside-listbox does not automatically imply combobox.
- A state-name-preserving transition swap cannot be detected by name-coverage alone.
- Test-file existence is not evidence that the test asserts a requirement.
- The submitted implementation sequence conflicts on whether G1/G5 initially block; resolve in an explicit phase policy.
- Do not automatically deprecate a component merely because its contract is difficult.
- Validate conditional schema semantics, including kind absence and unsupported keywords.
- Validate 003R identifiers against the actual frozen registry, not only a regex.

## Open
003R ID mapping, owner of gate baseline changes, SurfaceTrace inventory, experiment budget and continuation threshold.
