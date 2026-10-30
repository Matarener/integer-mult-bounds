# Exact reorder+re-frame optimum on PR5678's P104 word: conditional kappa .00310871312

Complete conditional kappa **.00310871312** (claim line, tested at .003108713125). The exact raw crossing is in
(0.00310871314031, 0.00310871314032). That is **+5.546e-7** over the raw crossing 0.0031081585098 of
[PR5678](https://github.com/CrocSwap/integer-mult-bounds/pull/5678) (Ali Romman, claim .00310815849), the newest
P104 head when this was written.

**Conditional on** exactly the assumptions of PR5678 and its inherited P104 line, including free helper endpoints
(PR5561, audited in PR5567). This word changes one helper start frame. The selected record is not changed.
No independent human or proof-kernel acceptance is claimed.

## What changes

The word is the optimum of R22's exact reorder+re-frame MIP (commutation poset × subspace charts) on PR5678's word.
The restricted domain and the wide domain (dim gap <= 3) give the same optimum: four re-framed ADDs and one helper start.

1. **Helper 473** (also in #5666 on PR5660):
   - It starts on the empty chart 3 (dim 0) instead of 594 (dim 1). Its credit rises from H8 to H9.
   - `213 += 1/2*473` runs on chart 3. It is ordered before the T/T-commuting `213 += 2*706` and that ADD's `MOVE 213 3 -> 594`.
   - `473 += 100` runs on 716 (dim 3) instead of 718 (dim 4), so `MOVE 100 716 -> 718` disappears.
2. **Helper 733** (new on PR5678's word):
   - 733 moves 597 -> 772 (dim 1 -> 4) before it is read into 585. Before, it moved 597 -> 794 (dim 6) later.
   - `585 += -4*733` now runs on 772 instead of 597, so 585 moves 3 -> 772 directly.
   - `438 += -4*733` now runs on 772 instead of 794.
   - 733 later moves 772 -> 127 instead of 794 -> 127.

Per local call:
- paid MOVE jobs H1 -3, H4 +1 (66402 -> 66366 paid calls in all);
- helper credits H8 -1, H9 +1;
- rank-mass surplus unchanged at 760, productive fields still 12958.

## Check

```
python3 -W error -B research/p104-reframe-r22/verify.py          # ~4 minutes; compares with RESULT.json
python3 -W error -B research/p104-reframe-r22/verify.py --write  # regenerates RESULT.json
```

`verify.py` runs these checks:
1. Pins PR5678's `WORD.json.gz` (SHA256) and regenerates `WORD.json.gz` from it with `construct.py`. Each edit
   replaces one unique event run.
2. Checks that only helper 473's start changes.
3. Checks that the new scalar order is a linear extension of the dependence order: T/T and S/S pairs commute,
   every other pair on a shared register keeps its order, and owned registers are exclusive.
4. Runs PR5678's own unmodified stack from its exported sources (`sources.py`, then the retained `sources.py`):
   exact replay, every dense transpose column, every native map and phase, the complete physical caller, and
   PR5678's `pricing.py`. Only the four literals in `LITERALS` change: claim/tested kappa, previous claim, and the
   paid-call total.
5. Runs six controls, all of which must be rejected:
   - old helper start;
   - read left on the old chart;
   - missing helper MOVE;
   - unpaid query;
   - extra target credit;
   - helper read swapped after its write.

## Attribution

All retained checkers, words and pricing are by the PR5678 authors and their sources; see `NOTICE`.
R22's search tools (`loop104.py`, `mip104.py`, `poset104.py`, `realize104.py`) are on branch
`r22-p104-reframe-optimum`.

Joel Pulikkan (GamingPuzzled) with Claude Opus 5.5 (Anthropic) via Claude Code. Apache-2.0.
