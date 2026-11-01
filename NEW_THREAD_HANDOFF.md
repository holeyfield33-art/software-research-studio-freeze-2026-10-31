# New thread handoff — Software Research Studio freeze

**Freeze:** SRS-FREEZE-2026-10-31-v1  
**Repo:** https://github.com/holeyfield33-art/software-research-studio  
**Disposition:** dataset integrity GO; bounded frozen-case replay GO; novel-input selector reliability NO-GO; Studio product integration NO-GO.

## Do not

- Edit freeze digests, `VERIFY_FREEZE.py` expectations, or mutate archived 003R content in place.
- Treat selector GO on the 13 frozen cases as general product or Studio integration authority.
- Merge product source trees into this archive.

## Do

1. Verify integrity with `python3 VERIFY_FREEZE.py` when the full freeze tree is present.
2. For selector corrective work, follow `next_unexecuted/` directives and produce a **new** named checkpoint.
3. For live product engineering, work in the product repository—not this freeze.

## Linked product focus (2026-11)

Primary active implementation case: **mcp-behavior**  
https://github.com/holeyfield33-art/mcp-behavior  

Details: `linked_products/mcp-behavior.md`  

Studio freeze remains immutable. Product work happens only in the product repo. Next product engineering gap: complete supervised subject run-level matrix and Sentinel-Zero retest (still no containment PASS from Studio).
