# UX Engineering Contract — candidate v0.1.0

## Purpose
Make approved UX intent discoverable to coding agents and verifiable without new infrastructure. A contract is a scoped specification, not proof of usability, accessibility conformance or standards certification.

## Minimum artifacts
1. Change packet: baseline revision, user outcome, owner, scope, assumptions, applicable requirements and acceptance oracle.
2. Requirements register: experiment-local stable IDs, status, acceptance conditions and verbatim references to existing 003R records.
3. Component/flow contract: ID, version, source paths, observable states/transitions, keyboard/focus/error behavior, optional token scope and typed verification refs.
4. Gate manifest: rule/tool versions, policies, finding-level baseline, exception owner and expiry.
5. Evidence ledger: exact commands and environment, PASS/FAIL/BLOCKED/NOT RUN, artifacts and independent review.

## Agent protocol
Read approved change packet and applicable contracts before edits. Inspect current implementation. Stop on consequential ambiguity. Do not invent frozen IDs, change gates to evade failures or claim unexecuted checks passed. Report changed files, commands, findings and unknowns.

## Five layers
V1 authority and change boundary.
V2 artifact structure, source existence, valid 003R resolution when available.
V3 independent behavior/regression oracles, including errors and recovery where applicable.
V4 applicable accessibility and task review, automated and manual.
V5 honest release evidence, finding-level ratchet, reviewed exceptions and unknowns.

## Implementation constraints
No MCP dependency. File-based workflow. A stdlib validator may implement a declared schema subset with positive/negative fixtures; it must not claim full JSON Schema Draft 2020-12 coverage. No universal DOM data-req requirement or formal state machines. No silent baseline regeneration. Existing defects can be documented but new critical regressions cannot be excused as inherited debt.

## Adoption
Inventory SurfaceTrace at pinned revision; choose one existing simple component and one consequential flow; capture observed contracts; freeze finding-level baseline; author independent acceptance tests; compare control/treatment; decide continuation on observed quality and total cost.
