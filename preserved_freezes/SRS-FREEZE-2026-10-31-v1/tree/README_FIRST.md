# SOFTWARE RESEARCH STUDIO — FROZEN BASELINE (2026-10-31)

**Freeze ID:** SRS-FREEZE-2026-10-31-v1  
**Latest research checkpoint:** STUDIO-KNOWLEDGE-003R  
**Disposition:** dataset integrity GO; bounded frozen-case replay GO; novel-input selector reliability NO-GO; Studio product integration NO-GO.

## What this archive preserves

- `current_003R/`: complete byte-preserving extraction of 003R, including 10 knowledge JSONL partitions, schemas, documented sources, selector, rule catalog, tests, fixtures, research, reports, oracle and run outputs. This is the *current software research dataset*.
- `original_checkpoints/`: the exact 001, 002, 003 and 003R source checkpoint ZIPs plus the detached 003R SHA-256 sidecar. This is the immutable historical chain.
- `independent_reviews/`: the four existing audit ZIP packages and extracted reviewer documents.
- `next_unexecuted/`: the 003R2 corrective directive, **not implemented** in the frozen snapshot.
- `FROZEN_STATE.json`, `INVENTORY.json`, `SHA256SUMS.txt`, and `VERIFY_FREEZE.py`: handoff and offline integrity verification.

**Counts refer to the newest 003R snapshot only.** Do not sum counts across checkpoints; those snapshots repeat most records.

## Latest research inventory

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
| Relationships | 601 (598 active; 3 superseded) |
| **Total** | **715** |

## What is not approved

The 003R selector passed its frozen 13-case oracle but failed independent unseen-input probes involving queue predicates, authority/authentication contradictions, malformed facts and static over-selection. There is **no** authorization to treat it as a generalized selector or to integrate into Studio. The old reports are preserved *as evidence at that checkpoint*, not as blanket certification.

## Project separation

This ZIP is for **Software Research Studio**, the reusable software-engineering knowledge foundation for Block-Wise Studio. **MOTHERSHIP** is the vulnerability-evidence/intelligence project. D-004's 14,021 advisory records and original acquisition archive are **not included** and are **not counted** in this Studio dataset. Their prior verified archive SHA-256 is recorded in `FROZEN_STATE.json` as a cross-project reference. No silent migration or merge is made here. Classification of the D-004 archive can be decided separately if necessary.

## How to resume without re-researching

1. Unzip and read this file + `FROZEN_STATE.json`.
2. Verify from the extracted freeze directory with `python3 VERIFY_FREEZE.py` (standard library only).
3. For exact current artifacts see `current_003R/README.md` and `current_003R/manifest.json`.
4. If doing *new* corrective work, use `next_unexecuted/STUDIO_KNOWLEDGE_003R2_DIRECTIVE_UNEXECUTED.md`, write a new checkpoint and do not change this frozen bundle.
5. Read `independent_reviews/STUDIO_KNOWLEDGE_003R_INDEPENDENT_AUDIT.md` before making a selection-reliability claim.

## Verification boundary

At freeze time the uploaded 003R ZIP passed CRC and matched its original detached hash; its 151 manifest-tracked contents matched, and `scripts/validate_dataset.py` completed with 715 records and zero errors. The full selector verification was *not rerun* during creation of this frozen bundle. The freeze script independently validates member SHA-256 and embedded original ZIP CRC when it is executed.

**Freeze rule:** preserve bytes and status. Any change must be a newly versioned increment with separate tests and checksums.
