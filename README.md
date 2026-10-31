# SOFTWARE RESEARCH STUDIO — FROZEN BASELINE (2026-10-31)

**Freeze ID:** SRS-FREEZE-2026-10-31-v1  
**Latest research checkpoint:** STUDIO-KNOWLEDGE-003R  
**Disposition:** dataset integrity GO; bounded frozen-case replay GO; novel-input selector reliability NO-GO; Studio product integration NO-GO.

> **This repository is an immutable archival baseline.** Do not edit files in place. Any new research or selector fixes require a separately named checkpoint and new manifest/digest.

## What this preserves

- `current_003R/` — complete 003R snapshot (715 knowledge records, deterministic selector, 13-case oracle, rules, schemas, tests, fixtures, decision traces)
- `original_checkpoints/` — exact 001 → 002 → 003 → 003R source checkpoint ZIPs + detached SHA-256
- `independent_reviews/` — prior independent audits and directives
- `next_unexecuted/` — the 003R2 corrective directive (not implemented)
- Top-level: `FROZEN_STATE.json`, `INVENTORY.json`, `SHA256SUMS.txt`, `VERIFY_FREEZE.py`

## Inventory (003R only)

| Collection | Records |
|---|---:|
| Software types | 10 |
| SDLC stages | 7 |
| Engineering practices | 8 |
| Architecture patterns | 6 |
| Prompt patterns | 6 |
| Roadmap patterns | 3 |
| Verification gates | 6 |
| Reference projects | 3 |
| Sources | 65 |
| Relationships | 601 (598 active) |
| **Total** | **715** |

## Known blockers (why selector is NO-GO for generalization)

- Misleading queue rationale when justification + owner are both present
- Cross-field authority / authentication contradictions not always detected
- Malformed facts can raise unhandled AttributeError
- Unjustified tool/side-effect recommendations can survive explicit exclusions

## How to use this freeze

1. Clone or download the full tree (or the original freeze ZIP from the conversation).
2. Run `python3 VERIFY_FREEZE.py` (stdlib only) to confirm integrity.
3. For current artifacts: `current_003R/README.md` and `current_003R/manifest.json`.
4. Next corrective work: follow `next_unexecuted/STUDIO_KNOWLEDGE_003R2_DIRECTIVE_UNEXECUTED.md` and produce a **new** checkpoint. Do not mutate this one.
5. Read the independent 003R audit before claiming selection reliability.

## Project boundaries

- This is **Software Research Studio** knowledge (for Block-Wise Studio).
- **MOTHERSHIP** (vulnerability/advisory intelligence) and D-004 acquisition archive are deliberately excluded.
- No silent cross-project merge was performed.

## Verification status at freeze

- Dataset schema + graph validation: PASS (0 errors)
- Manifest integrity: PASS (151 files)
- Frozen 13-case oracle: PASS (per prior independent audit; not re-run at freeze time)
- Novel-input generalization: **NO-GO**
- Studio product integration: **NO-GO**

Freeze policy: preserve bytes and status.
