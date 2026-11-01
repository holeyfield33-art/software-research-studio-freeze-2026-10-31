# STUDIO-KNOWLEDGE-003 — resubmission verification receipt

**Review date:** 2026-11-01  
**Scope:** the user-provided 003 research-only ZIP and the preserved 003 archive in this repository; **not** the 003R frozen selector, 003R2 directive, Stage 004, or Studio product integration.

## Archive identity

- User-supplied filename: `STUDIO_KNOWLEDGE_003_checkpoint.zip`
- Size: **249,809 bytes**
- Calculated archive SHA-256: `78d0977bd77f35b56aba5af0ca3f1719d77e4d5089d291ac6a36593ab0a983df`
- **Exact SHA-256 match** to the already preserved `original_checkpoints/STUDIO_KNOWLEDGE_003_checkpoint.zip`, independently documented in [the 2026-10-31 archival manifest](../2026-10-31/MANIFEST.json). No additional original archive should be copied into the repository.
- ZIP CRC: PASS; expected member set: 79/79; manifest contents: 77/77 verified SHA-256 digests; internal `manifest.sha256`: PASS.
- Original external ZIP SHA-256 sidecar was not uploaded with this resubmission. The existing archival manifest independently supplies the same whole-archive SHA-256; no sidecar contents are invented.

## Locally reproduced checks against the uploaded archive

Extracted safely to an isolated scratch directory; the uploaded ZIP itself was not edited. Ran the package's checks with Python and installed `jsonschema`:

| Command / check | Observed result |
|---|---|
| `python scripts/verify_manifest.py --root .` | PASS, 77 files, zero errors |
| `python scripts/validate_dataset.py --report /tmp/srs003-dataset-validation.json` | PASS, 715 records, 601 relationships, 65 sources, zero errors |
| `python scripts/verify_fixtures.py --report /tmp/srs003-fixture-validation.json` | PASS, 4 branches, zero errors |
| `python scripts/run_regression_tests.py` | PASS, 12 tests, zero failures/errors |
| Direct SHA-256 replay of 77 manifest entries and manifest digest | PASS |
| Compared all 003 dataset IDs against embedded checkpoint 001 and 002 record indexes | PASS, **45/45** and **522/522** preserved; zero missing |
| Five negative controls within the fixture verifier | Expected statuses observed; PASS |

The archive is byte-identical to the preserved, previously verified 003 archive, but the parent indexes used for this ID check were embedded in the 003 package; the earlier 2026-10-31 intake independently verified the actual original 001/002 archives.

## Decision: narrowly scoped

| Gate | Disposition |
|---|---|
| Archive identity and integrity | **GO** |
| 003 dataset/fixture internal validation | **GO**, for the 3 curated scenarios and 1 negative-control branch only |
| Unseen briefs / general-purpose research applicability selection | **NOT ESTABLISHED** |
| Later 003R novel-input selector reliability | **NO-GO** (existing freeze decision unchanged) |
| Studio runtime/product integration | **NO-GO** (existing freeze decision unchanged) |
| Production release, Stage 004 | **NOT AUTHORIZED** |

Seven of ten software types remain `NOT_CALIBRATED`. Curated scenario gates remain `INCOMPLETE` without project-candidate-bound execution proof; no security/release claim follows from this archive. No external standards or source applicability assertions were independently audited in this recheck.

## Follow-up

Use [the universal agent intake contract](../../docs/AGENT_INTAKE.md) for the next real project pilot. Do not rerun a corrected external repository assessment just to establish product linkage; targets are temporary assessment subjects. Keep MOTHERSHIP/D-004, the immutable freeze, and Studio integration authority separate.

**Files changed for this receipt:** one additive Markdown document; no archived bytes, manifest, historical results, selector, source records or project runtime were modified.
