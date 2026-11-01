# Evidence ledger — 2026-11-01

**Environment:** local Python 3.13.5, stdlib only. **Subject:** new ScanPlan v0.1 under `experiments/agent_b_scanplan`. **Verification mode:** local observed; no Studio kernel signed host receipts.

| Evidence | Result | Limit |
|---|---|---|
| `PYTHONPATH=. python -m unittest discover -s tests -v` | **PASS: 19/19** | Local suite only; includes malicious-input/negative controls |
| `PYTHONPATH=. python -m scanplan plan examples/demo.json --output /mnt/data/scanplan_work/scanplan_demo_output.json` | **PASS: exit 0**, 4 proposals, none executed | Static test plans, not actual vulnerability findings |
| `python -m json.tool <output>` | PASS: valid JSON | Syntactic only |
| SHA-256 of generated output | `e46237e1e3573ca04f260d1fb0d4b6cbe84ce8564a62561d2cba56c52d0ac373` | Output bytes from this exact code/input snapshot only |
| Canonical Studio `studio_kernel plan` | NOT_RUN | Reviewed canonical records/authority not yet supplied |
| Independent host execution/oracle | NOT_RUN | Planned tests not executed |
| Release decision | **HOLD** | This is experimental software, not a certified scanner |

Some checks use static source inspection; these do not constitute OS-level isolation, network-denial proof or signed evidence. A user-supplied name in `scope.review_owner` is *not* authenticated authorization.

## Next bounded experiment

Measure whether Studio can accept a reviewed canonical intake for this experiment, emit task packets retaining unknown risks, record an externally executed test with a trusted host receipt, and decide a single verification gate. Compare setup effort, defects and resulting evidence quality against the same small build without Studio. No claimed 50–75% improvement from this pilot alone.
