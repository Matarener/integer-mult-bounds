# Local rung-removal search on the PR5907 word (no kappa claim)

Base: CrocSwap/integer-mult-bounds main `19fdb086e`, word `research/p104-helper468-rung-removal/WORD.json.gz` (PR #5907).
Python 3.12 standard library, plus `ortools` for `retime.py` only. `CROC` in `p104.py` points to a checkout of main.

`p104.py` is an independent exact replay / invoice / Decimal kappa root; it reproduces the published crossings of PR5811, PR5827 and PR5907.

| script | move class | validation | on PR5907 |
|---|---|---|---|
| `rung.py` | delete a stop by relocating its events (no new events) | - | 0 / 2665 stops |
| `retime.py` | CP-SAT frame retime of the fixed circuit (after `p104-designer-toolkit`), strict and `--stopfree` | - | lattice optimum = base (dims-only relaxation 2.1e-4, not realisable) |
| `rung2.py` | stop removal by compensated read shifts | finds PR5827 from the PR5811 word (`--regs 695`), same crossing .00312476681507 | 0 / 2665 |
| `rung4.py` | same with recursive compensations (depth 2) | finds PR5827 likewise | 0 / 2665 |
| `subst.py` (+ `subst_census.py`) | partner swaps an adjacent stop for B or A, displaced events repaired by shifts | finds PR5907 from the PR5827 word (helper 468, partner 703), same crossing .00312528909884, with 0 added events | 0 / 2030 variants (1487 stops) |

Every candidate and its outcome is in `logs/*.jsonl`. These are heuristic move classes, not an impossibility proof
(the retime optimum is exact only within its frame domains).
