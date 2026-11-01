# UNIVERSAL-ARCH-001 — canonical architecture candidate

Status: **PROPOSED / REVIEW REQUIRED**, 2026-10-31. Canonical within this design checkpoint; not an approved product specification or implementation. Base: preservation/UX commit `62c8381`; public main inspected at `e537349`. No 003R2 implementation or Stage 004 is claimed.

The system understands a project's intended outcomes and actual state, selects justified lifecycle work, maintains connected artifacts, delegates bounded changes, and decides readiness from candidate-bound evidence. Rigor varies by consequence and uncertainty. The lifecycle is iterative and can begin with an existing project, incident, new product, library, or retirement decision.

Read in order:

1. [Evidence and reconciliation](EVIDENCE.md): what was read, verified, retained, narrowed or rejected.
2. [Architecture](ARCHITECTURE.md): modules, boundaries, lifecycle and state transitions.
3. [Coverage and gaps](COVERAGE.md): research support versus design and implementation gaps.
4. [Risk and selection](POLICY.md): proposed tiers, precedence and omission rules.
5. [Contracts](CONTRACTS.md) and [schema](contracts.schema.json): versioned records and semantic invariants.
6. [MVP and roadmap](ROADMAP.md): smallest complete loop, phases and acceptance criteria.
7. [Review and stop gates](REVIEW.md): decision owners, blockers and independent questions.

Generated `evidence-index.json` inventories all 715 original IDs, original JSONL line locations and raw-line digests; it does not replace the original records. `coverage.json` links design concerns to exact frozen records and their existing edges/sources. `validation.json` records checks actually performed on this package. These are derivative design artifacts, outside the freeze.

Reproduce from the repository root with Python 3.12 and dependencies in `requirements-validation.txt`: run `python architecture/UNIVERSAL-ARCH-001/build_evidence.py`, then `python architecture/UNIVERSAL-ARCH-001/verify_design.py`. The builder writes only derivative design files; the verifier writes illustrative examples and its result. Run `python checkpoint_intake/2026-10-31/VERIFY_RECOVERED_FREEZE.py` for the separate archival check. Semantic runtime tests and an independent architecture review remain future gates.

MOTHERSHIP and D-004 remain separate evidence domains with no imports or implicit authority. SurfaceTrace-specific runtime details, layouts and identifiers do not enter the universal core. SurfaceTrace remains an optional later validation case. “Universal” describes the extensible architecture and lifecycle contract; calibrated effectiveness across all software types is unproven.
