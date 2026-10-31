# Independent review brief and explicit stop gates

This checkpoint supplies questions, not an independent review verdict. Existing independent research is reconciled in EVIDENCE.md; the new universal architecture and proposed risk policy have not yet received independent review. Reviewer expectations must be frozen before implementation output is visible where feasible.

## Review questions

1. Does the architecture support greenfield, brownfield, incident, maintenance and retirement entry without importing SurfaceTrace or MOTHERSHIP assumptions?
2. For every mandatory artifact/control, can the reviewer trace a scoped requirement/fact, executable rule, exact original record, active edge and source locator with limitations? Which choices are policy synthesis instead?
3. Do tiers reflect consequences and uncertainty, avoid category-based defaults, and prevent severity averaging? Is the T2/T3 boundary clear enough for consistent independent decisions?
4. Do explicit exclusions ever suppress a required safety obligation silently? Can a contradiction or unknown authority produce plan COMPLETE or executable authorization?
5. Do all schemas reject malformed branch payloads and unknown fields? Which invariants need semantic validation? Can a well-formed fake run or approval pass without producer/authority verification?
6. Can the implementation distinguish a run failure, unexecuted check, incomplete evidence, stale result, blocked task and legitimate omission? Does every PASS bind the exact candidate, scope, oracle, tools and required approval?
7. Does the complete trace chain resolve actual assertions and observed outputs, rather than merely files and labels? How are weak/mocked/tautological tests detected by review?
8. Can a task alter its own acceptance oracle, policy, authority or baseline? Does the trusted host enforce capability restrictions independently of agent instructions?
9. On changed facts, code, source versions or policy, which downstream nodes become stale? Can stale writers, interrupted transactions or user edits preserve false readiness?
10. Is the minimal loop usable at T0 without excessive paperwork and adequate for T2 with independent evidence? What measurable burden would falsify the proposed boundary?
11. Are accessibility, usability, structural checks, security and domain correctness reported separately, with unsupported normative/productivity claims removed?
12. Does the MVP actually close the feedback loop and issue release/hold/support decisions, or does it stop at diagnosis/templates? Are specialist gaps and uncalibrated types exposed honestly?

Reviewer roles: architecture/requirements reviewer for lifecycle and MVP; selector reviewer for independent oracle/predicate correctness; verification/security reviewer for authority, evidence and host boundaries; domain/UX reviewer only where applicable. The builder cannot be the sole approver of its own acceptance oracle or consequential release. Reviewer identity, disagreements and unresolved findings must be recorded. No reviewers have been contacted or assigned by this checkpoint.

## Gates

| Gate | Required evidence / decision owner | Explicit stop condition and safe continuation |
|---|---|---|
| G0 preservation | Exact archive/dataset/hash comparison; checkpoint custodian | Any mismatch, rewritten ID or cross-project import: stop checkpoint production; preserve copies and investigate. Archival rerun passed here. |
| G1 architecture acceptance | Evidence-linked design, gap/selection/MVP/contracts review; accountable product owner plus independent architect | Unresolved P0 boundary/schema/risk questions: do not claim accepted architecture or begin product integration. Design refinement remains allowed. |
| G2 selector reliability | 003R2 independent expectations and all specified counterfactual/metamorphic/packaging checks; independent selector reviewer | Any false rationale, malformed crash, conflict miss or unjustified mandatory work: retain NO-GO for automatic novel selection. Manual reviewed research mapping only. |
| G3 state/contract integrity | Full declared schema validator plus graph, authority, candidate, invalidation and replay semantic tests; kernel reviewer | Invalid refs, stale update accepted, lost committed event or unsupported validation keyword: stop dependent execution; diagnostics allowed. |
| G4 bounded action | Exact packet/grant match, host enforcement, valid candidate baseline, budget and recovery conditions; action authority | Missing/revoked/expired authority, scope drift, unauthorized path/network/action, secret exposure or budget exceeded: stop run immediately, retain evidence, revoke affected grant. Independently authorized read-only work may continue. |
| G5 verification acceptance | Candidate-bound results for every required gate, independent assertions, applicable manual/domain review; verification owner | Required FAIL/INCOMPLETE/stale evidence or oracle leakage: no acceptance/release; allow bounded correction and new evidence. Never regenerate baseline to clear result. |
| G6 release/loop acceptance | Exact candidate approval, support/recovery disposition and full cross-case feedback/resume evidence; release/product owner and independent reviewer | Approval/candidate mismatch, unresolved critical risk or absent required recovery: HOLD. A held candidate may still supply honest pilot evidence. |
| G7 expansion/promotion | New scoped evidence, independent cases, costs, known limits and explicit decision; product/domain owner | Unsupported category/generalization, unexplained cost or unresolved critical regression: no scope promotion. Keep bounded existing use. |

Gate outcomes are PASS, FAIL or INCOMPLETE for applicable checks. Run statuses BLOCKED/NOT_RUN and task states are different vocabularies. NOT_APPLICABLE is an independently inspectable selection/omission result, not a gate PASS. Any policy exception names scope, rationale, owner, expiry and compensating evidence; it cannot authorize an otherwise unauthorized action or turn a failed run into PASS.

Present disposition: G0 archival preservation PASS; design package mechanical validation reported separately. G1–G7 acceptance not executed. Frozen selector novel-input and product integration NO-GO remain. The proposed architecture may be refined and reviewed without executing 003R2 or integrating a product.
