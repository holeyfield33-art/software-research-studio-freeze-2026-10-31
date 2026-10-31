# Studio checkpoint intake — 2026-10-31

This is an additive preservation checkpoint on `srs-ux-002-integration`, based on commit `a613558dfeeb30beeba8f90c837756ecde824466`. It does not supersede or modify `SRS-FREEZE-2026-10-31-v1` / `STUDIO-KNOWLEDGE-003R`. Original record IDs, JSONL formats, ZIP contents, prior documents, and research dispositions are unchanged. No MOTHERSHIP or D004 archive or dataset is included.

## Preserved originals

| Archive under `original_checkpoints/` | Bytes | ZIP entries / files | Parsed records | Verification |
|---|---:|---:|---:|---|
| `STUDIO_KNOWLEDGE_001_initial_checkpoint.zip` | 19,258 | 24 / 18 | 45 | CRC PASS; SHA-256 matches reference in 002 and 003 |
| `STUDIO_KNOWLEDGE_002_checkpoint.zip` | 140,049 | 48 / 48 | 522 | CRC PASS; 47 internal hashes PASS; SHA-256 matches 003 reference |
| `STUDIO_KNOWLEDGE_003_checkpoint.zip` | 249,809 | 79 / 79 | 715 | CRC PASS; 77 internal hashes and detached manifest digest PASS |

001 has no internal manifest. This intake records a new member inventory; it does not invent an original manifest. For 002 the manifest excludes itself; for 003 the manifest excludes itself and its detached digest. All 145 regular members receive SHA-256 entries in `MANIFEST.json`. Directory entries are counted separately. Duplicate names and unsafe paths were checked. All ten dataset partitions in each archive were parsed; IDs are unique within each checkpoint.

The archives came from the mounted attachments to **Revise UX UI Blueprint**, conversation `6ae6478e-de24-83e8-b633-85405ed5d892`. Mounted filenames have a `(1)` suffix; the repository uses the canonical names referenced inside subsequent checkpoints. Only the filenames changed. Each copied archive also matches the corresponding file in Downloads byte-for-byte. `MANIFEST.json` records exact source paths, sizes, archive and member hashes, partition counts, and ID transitions.

001 → 002 retains all 45 IDs and adds 477. 002 → 003 retains all 522 IDs and adds 193. Neither transition removes an ID. Record content changes under retained IDs are explicitly enumerated in the manifest; retained identity does not imply identical content. 003 contains 65 sources, 601 relationships, 10 software types and 39 other knowledge records.

## Relationship to frozen 003R

The preserved prior `evidence/STUDIO_KNOWLEDGE_003R_INDEPENDENT_AUDIT.md` reports that 003R preserved all ten 003 dataset partitions byte-for-byte and verified the inherited 001/002/003 archive hashes. Its reported counts match the locally parsed 003 dataset and existing `FROZEN_STATE.json`: 715 records, 601 relationships. This establishes a documented predecessor relationship, not a fresh byte-level verification of 003R.

The original 003R ZIP and complete freeze ZIP are unavailable in this Windows workspace. The attachment named `STUDIO_KNOWLEDGE_003R_checkpoint` is **103 bytes of checksum text, not an archive**. It is preserved under that original name in `evidence/`, together with both original 003R checksum attachments and the freeze ZIP checksum attachment. None is represented as recovered archive content.

Expected 003R ZIP SHA-256: `5fea1fe5e8f19064df7ee9af4386aeb85046003c99ee83f9b4569432f0992aa8`.

Expected complete freeze ZIP SHA-256: `a39b30fee3304e843b0291770efe7a42e993d733c3c09d5321ea5f2d53e6ad04`.

The prior audit predates delivery of the detached 003R checksum and reports a packaging failure for that absence. Preserve that historical verdict as written; the later checksum attachments do not constitute a new archive verification. No selector, schema/graph validator, oracle, benchmark or external-source verification was executed in this intake. Generalized selection and Studio integration remain NO-GO. 003R2 remains unexecuted.

## Independent Round 2 reports

Two original attachments are preserved without rewriting under `rounds/SRS-UX-002/original_reports/`: DeepSeek (`Pasted text(6).txt`, 30,369 bytes) and Perplexity (`Pasted text(5).txt`, 22,579 bytes). Their authorship is supported by their opening text and the source conversation. Existing encoding artifacts and line endings are preserved. The Gemini original was not exposed by the accessible conversation attachments or mounted files; no substitute, synthesis, or reconstructed report is provided. Its original remains an outstanding preservation item.

## Reproduce verification

From the repository root:

```text
python checkpoint_intake/2026-10-31/VERIFY_INTAKE.py
```

This checks preserved file sizes and SHA-256, all archive member hashes and CRCs, internal manifests and embedded predecessor checksum references, parsed counts, and ID transition inventories. It never executes archived scripts. `VERIFICATION.json` contains the recorded run result. `SHA256SUMS.txt` covers originals and `MANIFEST.json`; the verifier and explanatory documents are versioned by Git.

The pre-existing top-level `VERIFY_FREEZE.py` still requires the unavailable full freeze's `INVENTORY.json` and `SHA256SUMS.txt`. Do not use this intake's differently scoped manifest to satisfy that verifier or claim 175-file freeze verification.

Remaining retrieval work: obtain the real 003R and complete freeze ZIPs, verify against the preserved expected digests, then verify their full inventories and dataset equality; retrieve Gemini's original Round 2 attachment. None of these unavailable items was recreated or marked complete.
