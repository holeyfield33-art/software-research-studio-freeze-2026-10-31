# Full freeze tree

The original freeze ZIP (`SOFTWARE_RESEARCH_STUDIO_FREEZE_2026-10-31_v1.zip`) contains the complete 177-file tree including:

- `current_003R/` (full dataset, selector, oracles, fixtures, tests, reports, decision traces)
- `original_checkpoints/` (001 / 002 / 003 / 003R ZIPs + detached hash)
- `independent_reviews/`
- `next_unexecuted/`

This GitHub repository currently holds the documentation, handoff, state, and verifier.  
The complete byte-preserving tree is available from:

1. The original uploaded freeze ZIP in the conversation that created this repo, or
2. A local extraction that has already been verified with `python3 VERIFY_FREEZE.py` (status PASS, 175 files).

**Recommendation:** Keep the original ZIP as the authoritative archival object and treat this repository as the durable index + handoff + verifier.  When you are ready to work on 003R2, extract a clean working copy from the ZIP and produce a *new* versioned checkpoint; do not mutate the freeze.
