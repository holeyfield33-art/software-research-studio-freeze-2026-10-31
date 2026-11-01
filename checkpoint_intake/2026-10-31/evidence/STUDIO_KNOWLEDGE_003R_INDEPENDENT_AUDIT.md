# STUDIO-KNOWLEDGE-003R — Independent checkpoint audit

**Review date:** 2026-10-31  
**Subject:** `STUDIO_KNOWLEDGE_003R_checkpoint.zip`  
**Verdict:** **PARTIAL ACCEPT as a bounded research checkpoint; NO-GO for generalized selection and Studio integration.**

## 1. Verified strengths

- `scripts/verify_selector.py` independently reran and returned **13/13** oracle cases passing, five inherited negative controls passing, and a clean-room oracle isolation check passing.
- Independently executed `scripts/validate_dataset.py`: **715 records**, **0 errors**, 10 partitions, **601 relationships (598 active, 3 superseded)**.
- Independent SHA-256 comparison verified all three inherited ZIP digests (001/002/003) and byte-for-byte equality of all ten dataset JSONL partitions with the original uploaded 003 ZIP.
- `scripts/verify_manifest.py --root .` returned **PASS** for all **151 manifest-tracked files**; the package advertises 153 total ZIP members including manifest and manifest checksum.
- Independently executed the exact-oracle unit test: **PASS** (one test, exact match for all 13 cases).
- Included regression report records **34/34** passing. A full regression-suite independent rerun was attempted but timed out in this review environment; do **not** characterize all 34 as independently rerun here.
- Safety-positive: failed test executions cannot become PASS; side-effect authorization is not granted by the sampled fixtures; descriptive text is explicitly ignored as non-authoritative. No Studio or production artifacts appear to have been modified by this uploaded package.

## 2. Packaging gate: FAIL

`python3 scripts/verify_manifest.py --root . --archive /mnt/data/STUDIO_KNOWLEDGE_003R_checkpoint.zip` returns:

```
"status": "FAIL",
"errors": ["detached archive checksum sidecar missing"]
```

Uploaded archive SHA-256, independently calculated:

```
5fea1fe5e8f19064df7ee9af4386aeb85046003c99ee83f9b4569432f0992aa8
```

This is a missing detached artifact, not a mismatch in the inner manifest or evidence of tampering.

## 3. Independent counterfactual findings

Probe implementation and output are included alongside this report. These probes provide new inputs not contained in the frozen 13-case oracle.

### P0 — Queues remain incorrectly blocked after explicit justification

Base input: `selection_cases/api_queue_without_justification/brief.json`. Change `queue_load_justification=true` and `operations_owner_available=true` while retaining `async_queue_required=true`. Output still reads:

```
feature.queue = INCOMPLETE
reason_code = QUEUE_JUSTIFICATION_OR_OWNER_MISSING
arch.event_queue = INCOMPLETE, same reason
```

There may be further design-review requirements before *recommending* the queue, but **the stated missing-facts reason is false**. Both `scripts/select.py` branches for `async_queue_required=true` ignore the two justification facts. An overall `RECOMMENDED` result despite the unresolved requested queue compounds the ambiguity.

### P0 — Contradictory structured authority/identity inputs not detected

1. Start from `cli_destructive_overwrite_unauthorized`; change only `destructive_write_authorized=true` while keeping `authority.write_scope_authorized.state=false`. The selector returns overall `RECOMMENDED`, with `feature.destructive_overwrite=INCOMPLETE` and `DESTRUCTIVE_WRITE_NOT_AUTHORIZED`, but does **not** report a contradiction between structured authorization claims. Conservatively withholding actual permission is good; failing to identify the contradictory facts is a correctness gap.
2. Start from `base_authenticated_api`; set `public_read_only=true`, `authentication_required=false`, and `role_based_authorization=false`, but leave `authenticated_users=true` at project scope. The selector returns overall `RECOMMENDED` and `feature.authentication=INAPPLICABLE` without identifying the inconsistent identity contract. If mixed public/private endpoints are allowed, the input contract needs endpoint-level scopes; the current project-scoped facts do not express that distinction.

### P0 — Malformed input causes a process crash, not a structured abstention

Submitting a brief whose `facts` field is a string, or has a string as an individual fact row, exits nonzero with:

```
AttributeError: 'str' object has no attribute 'get'
```

The code collects JSON Schema errors but subsequently dereferences invalid structures before returning `INCOMPLETE`. A safe research CLI should return an explicit schema-invalid rejection without an unhandled traceback.

### P1 — Static profile over-selection / feature creep

Starting from the AI-agent base brief, set all six facts below to `false`:

```
reads_untrusted_external_content
has_read_access
has_bounded_write_tool
can_cause_side_effects
high_impact_action_possible
approval_required_for_high_impact
```

Output remains overall `RECOMMENDED`, still selects 18 records including `arch.agent_tool_boundary`, `practice.threat_modeling` and `prompt.threat_model` as `RECOMMENDED`, and retains `deliverable.authorization_controls`. A reduced-scope agent may still need some risk review, but mandatory write/tool boundary obligations need predicate-level justification. The current hard-coded `PROFILE` and `ROLE_PROFILE` tables reproduce much of the frozen bundle even when relevant risk facts are explicitly negated.

This is the principal reason to withhold **generalized selection GO** despite 13/13 curated fixture results.

### P1 — Rule table and execution can drift

`rules/selection-rules.json` contains descriptive predicate/effect strings, while many selections and statuses in `scripts/select.py` come from unconditional `PROFILE` tuples. The policy file is not itself an executable declarative rule engine. Require automated tests that ensure critical rule text, executable predicates, and emitted `predicate_matches` agree; do **not** build a separate rule engine just to solve this.

## 4. Gate decisions

| Gate | Verdict | Reason |
|---|---|---|
| Dataset integrity | GO | Independent schema/relationship validation plus parent hash preservation |
| Frozen-oracle reproducibility | GO (bounded) | Independent 13/13 exact replay; clean-room check |
| Current negative-control safety | GO (bounded) | Known controls and fail-closed evidence handling |
| Input error-handling | NO-GO | Schema-invalid inputs crash |
| Novel-fact selection reliability | NO-GO | Queue false reason, unflagged contradictions, unnecessary static obligations |
| Archive-level packaging | NO-GO | Detached ZIP `.sha256` not delivered |
| Studio integration | NO-GO | Research calibration remains insufficient; no integration authorization |

**Recommended disposition:** Accept this checkpoint as the 003R research baseline. Execute a strictly limited **STUDIO-KNOWLEDGE-003R2** stabilization phase. Do not start Stage 004, extend categories, or change Studio code.

## 5. Reproduction

From the extracted checkpoint directory:

```bash
python3 scripts/verify_selector.py
python3 scripts/validate_dataset.py --report /tmp/studio003r-dataset-check.json
python3 scripts/verify_manifest.py --root .
python3 scripts/verify_manifest.py --root . --archive /path/to/STUDIO_KNOWLEDGE_003R_checkpoint.zip
```

For the independent new probes, run the included `adversarial_probe.py` and `adversarial_probe_extended.py` in the review directory. They reference the extracted `input` directory as mounted in the review and can be trivially adjusted to any extraction root.

**Scope note:** These tests establish reproducible code-behavior findings, not a comprehensive external-source audit or a claim that this selector is production-ready.
