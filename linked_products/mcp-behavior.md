# Linked product: mcp-behavior

**Product repo:** https://github.com/holeyfield33-art/mcp-behavior  
**Role relative to Software Research Studio:** live implementation case — behavioral MCP server assessment harness, not part of the frozen 003R knowledge dataset.

## Boundary (read carefully)

| This studio freeze | mcp-behavior |
|---|---|
| Immutable archival baseline (SRS-FREEZE-2026-10-31-v1) | Active product development (0.2.0.dev*) |
| Deterministic selector research for Block-Wise Studio | Runtime test harness for MCP server behavior |
| Do not mutate `current_003R/` or freeze digests | Evolves on its own main branch |
| Selector reliability remains NO-GO for generalization | Helper live evidence GO; full containment PASS still NO-GO |

No silent merge of product code into this freeze. No claim that Studio selector outputs authorize mcp-behavior releases.

## Current product posture (as of 2026-11-01)

- **Product repo main** develops independently; verify tip with `git log` on the product repo.
- **Version line:** 0.2.0.dev* (see product `CHANGELOG.md` / `pyproject.toml`).
- **Proven:** native behavioral profile; fail-closed isolation interface; trusted-helper probes (host path, network endpoints, cgroup supervision) on a disposable privileged Ubuntu container with private cgroup namespace (checkpoint 3 live evidence).
- **Not proven / still open:** full run-level containment PASS; fixed Sentinel-Zero retest; hosted GitHub Actions when billing allows. Experimental subject paths, if present on product main, remain bounded by product docs—not by this freeze.

## How Studio and product relate

1. **Studio** supplies SDLC / verification / architecture *knowledge patterns* (frozen research).
2. **mcp-behavior** is a *concrete product* that can be described with those patterns (CLI tool, security-adjacent test harness, evidence-first gates).
3. New Studio research that *uses* mcp-behavior as a reference project must be a **new checkpoint**, not an edit to this freeze.
4. Product roadmap gates remain authoritative in the product repo: `docs/ROADMAP.md`, `docs/STATUS.md`, `docs/ARCHITECTURE.md`.

## Pointers (product docs)

| Doc | Path on product repo |
|---|---|
| Status | `docs/STATUS.md` |
| Roadmap | `docs/ROADMAP.md` |
| Architecture (isolation) | `docs/ARCHITECTURE.md` |
| Spec | `docs/SPEC.md` |
| Adversarial review | `docs/ADVERSARIAL_REVIEW.md` |
| Changelog | `CHANGELOG.md` |

```bash
git clone https://github.com/holeyfield33-art/mcp-behavior.git
cd mcp-behavior
PYTHONPATH=src python -m unittest discover -s tests -v
```

## Next product gaps (not Studio selector work)

1. Complete supervised MCP subject run-level matrix (protection, egress, resources, teardown).
2. Fixed Sentinel-Zero retest on the four behavioral gates.
3. Hosted CI once account billing allows workflow runs.
