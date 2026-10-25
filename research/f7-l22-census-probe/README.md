# Bounded length-22 probe of the corrected word census (resource budget, no f(7) claim)

This package measures the resource budget for the one remaining controlled
step of the #2973 word-census correction: a corrected length-22 census at
seven labels. It is the named next step of the
[f7-l22-split-domain](https://github.com/CrocSwap/integer-mult-bounds/pull/3708)
handoff, whose recorded blocker is *"no node-count estimate or resource
budget; #2973's stop rule was explicitly no L22 census."*

**What is established here, at its actual strength:**

1. **Engine extension, validated.** The corrected census engine of
   `research/f7-weight-parity-census-correction` (#2973, Nicholas Stone) is
   pinned at blob hash with source `sha256 265ead91…`. A copy extended by
   **exactly three header/gate lines** (`L <= 20` to `L <= 22`; nothing else)
   is included as `engine/extended_census.c`. The extension is validated by
   (a) the predecessor package's own `math/check_math.py`, (b) the
   predecessor's brute-force cross-check `validation/check_corrected_c.py`
   run against the extended engine (all small splits, all four budget
   modes, cap and fail-closed input controls), and (c) **node-exact
   reproduction of all six recorded L20/L18 receipts** of the pinned
   package with the extended binary.
2. **Capped length-22 probes with three completed exclusions.** All nine
   open splits of the #3708 domain — `(11,11), (11,10), (11,9), (10,10),
   (11,8), (10,9), (11,7), (10,8), (9,9)` — are probed with both proved
   necessary budgets enabled. Three splits completed with `complete=true`
   and zero hits — **`(11,7)`, `(10,8)` and `(11,8)` are finite
   exclusions**; the six others hit the 2e9-node cap and abort, recording
   only **lower bounds** on their tree sizes. Per-split results, including
   node counts and seconds, are in [RESULT.json](RESULT.json). **CI scope:**
   the registered commands re-run the validation stages and replay each of
   the three completed exclusions node-exactly, one command per split; the
   six capped probes are locally measured and are reproduced only by the
   opt-in `--probe-all-splits` command (about 1.4e10 nodes), not by CI.
3. **No f(7) claim.** The six loose-budget splits remain open, so nothing
   here decides whether `f(7) = 22` or `24`. No supplier, tariff, kappa,
   certificate, frozen input or selected-frontier change is made or
   implied. `scripts/research_baseline.py` still reports
   `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` with the pinned selected record.

## Why the L<=22 gate change is sound

The predecessor restricts compile-time `L` to `[2,20]`, described as keeping
"masks and all full-search counters within their exact types". At `N = 7,
L = 22`: coverage masks still use 7 of the 128 bits of `mask_t`; the largest
new counter values are `C(11,2)+C(11,2) = 110` (even budget bound), `11*11-64
= 57` (odd budget), per-label multiplicity `<= L-2(N-1) = 10`, and
`rem_even/rem_odd` table entries `< 22`. Every state variable is an exact
small integer or a fixed-width bitset at `L = 22`, so the gate is
conservative rather than necessary at 22. The behavioral controls above are
the real evidence: identical node-exact receipts at every recorded case.

## How to reproduce

From the repository root, with Python 3.12 and a C11 compiler:

```sh
# Registered CI scope: validation stages, then one fresh node-exact replay
# per completed exclusion (the registered commands run these separately).
python3 -I -B research/f7-l22-census-probe/verify.py --skip-probe
python3 -I -B research/f7-l22-census-probe/verify.py --probe-split 11,7
python3 -I -B research/f7-l22-census-probe/verify.py --probe-split 10,8
python3 -I -B research/f7-l22-census-probe/verify.py --probe-split 11,8

# Default (no flags): validation stages plus all three exclusion replays.
python3 -I -B research/f7-l22-census-probe/verify.py

# Opt-in, not run by CI: the full nine-split comparison against the
# committed RESULT.json receipt, including the six capped lower-bound
# probes (about 1.4e10 nodes; minutes on a many-core host).
python3 -I -B research/f7-l22-census-probe/verify.py --probe-all-splits
```

`verify.py` writes `LAST-RUN.json` in this package and prints
`PASS_F7_L22_CENSUS_PROBE`; the committed `RESULT.json` session receipt is
never rewritten. Probe cap default is 2,000,000,000 nodes per split; probes
run in parallel threads. All other generated files use temporary
directories. Aborted/capped probes are recorded with `complete=false` and
are never exclusions; the engine returns exit 2 for them.

## Results summary

Measured on this host (Apple arm64, CPython 3.12.15, Apple clang, 18 cores,
probes in parallel, cap 2,000,000,000 nodes per split). Node counts are
exact engine outputs; seconds are host timings and are not part of any
claim.

| Split | Nodes | Outcome | Meaning |
|---|---:|---|---|
| `(11,7)` | 8,784,744 | complete, exit 0, 0 hits | **finite split exclusion** |
| `(10,8)` | 597,933,297 | complete, exit 0, 0 hits | **finite split exclusion** |
| `(11,8)` | 1,349,702,650 | complete, exit 0, 0 hits | **finite split exclusion** |
| `(9,9)` | 2,000,000,000 (cap) | aborted | tree has more than 2e9 nodes; open |
| `(10,9)` | 2,000,000,000 (cap) | aborted | tree has more than 2e9 nodes; open |
| `(10,10)` | 2,000,000,000 (cap) | aborted | tree has more than 2e9 nodes; open |
| `(11,9)` | 2,000,000,000 (cap) | aborted | tree has more than 2e9 nodes; open |
| `(11,10)` | 2,000,000,000 (cap) | aborted | tree has more than 2e9 nodes; open |
| `(11,11)` | 2,000,000,000 (cap) | aborted | tree has more than 2e9 nodes; open |

For scale, the predecessor's recorded length-20 exclusions totalled about
9.2e8 nodes across all five splits; the three completed length-22 splits
alone reach 1.96e9 nodes, and each of the six open splits exceeds 2e9
before its cap. A complete census needs the six open splits finished, so
the probe numbers are the concrete resource datum the handoff asked for.

Certification scope, stated exactly: the three finite exclusions and the
validation stages above are re-run by the registered CI commands; the six
capped lower-bound probes are not part of CI replay and remain locally
measured, reproducible with the opt-in command in "How to reproduce".

Combined with the imported 17-point set-level exclusions of #2773/#2870
(splits `(10,7)`, `(11,6)`), any restored universal length-22 word must now
have its distinct-state split in `{(9,9), (10,9), (10,10), (11,9),
(11,10), (11,11)}`. The domain is six splits, not nine. No universal word
was found and no claim is made about `f(7)`: it remains 22 or 24.

All six recorded predecessor receipts were reproduced node-exactly with
the extended binary (`receipt_replay` in RESULT.json); the brute-force
cross-check and the predecessor math check pass. `scripts/research_baseline.py`
reports `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` unchanged.

## Credit

Predecessor and sole mathematical source: **Nicholas Stone**
(#2973 corrected census engine, budgets, split theory) on the word model of
Aaron Wang (PR2542/PR2634) and Ross Richardson (PR943), with the length-22
split domain derived by Nick Petalas (PR #3708). This package was produced
by Nick Petalas with AI assistance. Apache-2.0.

## Open next questions

1. **Is a complete nine-split L22 census affordable?** RESULT.json gives
   per-split tree-size lower bounds from the capped probes. A feasibility
   decision needs those numbers plus the loose-budget splits' completion
   behavior at higher caps; it is a resource decision, not a new mechanism.
2. **Does a restored universal length-22 word exist?** This package
   excludes the splits `(11,7)`, `(10,8)` and `(11,8)`; the domain is the
   six splits `{(9,9), (10,9), (10,10), (11,9), (11,10), (11,11)}`. The
   smallest trees there already exceed 2e9 nodes at each aborted split, so
   the next probe level (8-16e9 nodes, or a cheaper prune) is a resource
   decision, not this package's claim.
3. **Can the pair identity (`sum_x A_x B_x >= need`, MATH.md section 3)
   become a third monotone engine prune?** It is proved necessary at
   leaves but its partial quantity is not shown monotone; a non-monotone
   prune would be unsound. See TASK.json open questions.
