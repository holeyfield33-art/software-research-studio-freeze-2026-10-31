# Failed-negative-controls.md — adversarial abstention checks

“Failed” here names the controls that would fail unsafe/unsupported claims; all five controls behaved as designed in the verifier. No test, CI, standard-conformance, or release outcome is claimed.

| Control | Expected status | Derived status | Result | Rationale |
|---|---|---|---|---|
| `mobile_source_cannot_support_api_claim` | `INAPPLICABLE` | `INAPPLICABLE` | PASS | Source is attached to the mobile-app software-type record, not the API record, and is scoped to another stack. |
| `superseded_edition_without_adoption` | `INCOMPLETE` | `INCOMPLETE` | PASS | Catalog currency is established, but adoption and normative applicability remain unresolved. |
| `repository_test_source_without_run` | `INCOMPLETE` | `INCOMPLETE` | PASS | Pinned test and workflow sources are configuration only; no candidate-bound run result exists. |
| `source_specific_guidance_is_not_a_universal_default` | `CONDITIONAL` | `CONDITIONAL` | PASS | Different source scopes remain attributed; no universal architecture winner is inferred. |
| `unknown_requirement_abstains` | `INCOMPLETE` | `INCOMPLETE` | PASS | No stable catalog match exists; the unknown requirement is not silently mapped to a recommendation. |

## Interpretation

- Mobile-stack documentation is not selected as evidence for the API record: `INAPPLICABLE`.
- The official IEEE catalog identifies ISO/IEC/IEEE 12207:2026 as active and superseding 2017, but organizational adoption and normative applicability remain unreviewed: `INCOMPLETE`; no compliance assertion is allowed.
- Pinned test source and workflow configuration describe authored/configured content only. With no candidate identity or execution artifact, the test gate remains `INCOMPLETE`.
- AWS workload-segmentation and Twelve-Factor process guidance stay within their respective scopes; architecture selection remains `CONDITIONAL`, not a universal winner.
- Unknown requirement IDs with no catalog match cause explicit `INCOMPLETE` abstention; they are not silently mapped.

Regression tests intentionally mutate each negative case and assert that the control then reports an error.
