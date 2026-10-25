# R20: the p19 coded-reverse invoice (#5270 / #5440) with the reviewed costs charged

**Result: the claim collapses. No positive saving remains.** The missing `Q` on the stage letters is enough on
its own to kill it. No κ claim is made here.

Base: DaysSky's package `research/coded-reverse-word-p19` at #5440 head `c0f52b5b1`, worktree `~/imb-r20`.
(#5270 head `225a19a18` has the same `invoice()`.) Prices come from the package's own `invoice()` and
`listing()`, a 60-digit Decimal moment M(C) = Σ_T n k^(1−C) − Σ_P n r^(1−C), and the exact concave-order hinge
test from `scripts/compare_recursive_invoices.py`.

## How much the original invoice can absorb
- Raw root: 0.007578535190.
- Rank-mass surplus: 2016 out of 265,533.
- Spare moment at C = 0.0034 (BIT): 1103.28. Spare moment at the selected frontier 0.003027288235: 1202.6683. At
  our 0.0030272882489783 it is also 1202.6683.
- So the invoice can absorb at most **1202** extra rank-1 jobs and still beat the frontier.

## Charges (all exact counts taken from the listing)
| variant | added cost | mass at C=0 | M(U_sel) | root |
|---|---|---:|---:|---:|
| V1: `Q` on every stage letter. The native call supplies `D`, but the listing applies `R = D·Q`. 19 LETTER gates × 2 roles × 112 owners | **+4256 rank-1** | −2240 | **−3053.33** | **0** (dead for every r^t, min hinge 2240) |
| V2: V1 plus R-type idles in the fresh-block geometry. Q^|S| on the central line for odd |S|. Charged most favourably as merges 8k→8k+1 at k ∈ {1,3,5,7,9}, 448 fields each | +2240 rank | −4480 | −5263.21 | 0 |
| V3: V2 plus the 18 middle idles, priced as the listing actually executes them (R on 224 fields, rank 9; the invoice prices them at 0) | +4032 × rank 9 | −40768 | −41310.6 | 0 |
| VB: letter `D` instead, with the Q-conjugated terminal gauge decoded by one paid `Q` per owner on the 19 coded banks; credit 8k instead of 1+8k | +2128 rank-1, −2128 credit | −2240 | −3023.90 | 0 |
| VB0: terminal decoder only, all credit kept (lower bound for the VB route) | +2128 rank-1 | −112 | −925.33 | 0 |

**Merge-robust bound.** Suppose the 4256 `Q` axes are not paid as separate jobs but merged into existing
paid jobs.
- Adding one Gaussian axis to a job of rank r (with r+1 ≤ 153, the ambient rank) costs
  (r+1)^(1−C) − r^(1−C) ≥ (1−C)·153^(−C). At C = U_sel this is ≥ 0.981905 H1-equivalent.
- So the 4256 `Q` axes cost ≥ 4179 against a budget of 1202.67. At most 1224 such axes fit.
- Merging therefore cannot rescue the invoice.
- Assumption: no existing paid job already acts Gaussianly on the central (query) axis. PHYSICAL.md supports
  this: the native backward call is `diag(D,D)·upper(−QC)`, and its `D` is rank 8 on the stage block.

**The charge that kills it: the missing letter `Q`** (#5440 reviews by Matarener, zxv and gvconly).
- It overshoots the budget by 4256 − 1202 = 3054 rank-1 jobs, i.e. 3.5× the available margin.
- Even the cheapest identified alternative overshoots: the terminal-gauge decoder alone (2128) is 1.8× the
  budget.
- Compiler constants (jwr404) do not matter here. They only move κ below the raw root. #5440 already uses the
  shape-correct h = 1/64 majorant, and it closes.
- The distinct-axis issue (zxv, #5349, gvconly) only adds more charges (V2/V3). It also explains why the
  9-axis replay missed them: every listed idle power (2, 4, …, 18) is even, and R^even is monomial on the same
  nine axes.

## What a rescue would need (not attempted)
Either of these would change the conclusion:
- a coded realization of `controller()` itself: letter `D`, fresh blocks, exact, with every `Q` charged;
- a gauge repair costing ≤ 1202 rank-1-equivalents per p=19 unit, i.e. ≤ 63 per thick stage against 224
  independent fields.

R17's one-vector-per-paid-job lemma suggests that ≥ 224 jobs per stage are needed when the 224 fields are
formally independent. That puts the second option out of reach unless a new native call supplies `R` with no
additional rank mass. At C = 0 that is impossible: rank mass is additive, so mass = −2240 for any realization.

## Reproduce
```sh
cd ~/imb-harness/r20/tools && OPENBLAS_NUM_THREADS=1 /opt/homebrew/bin/python3.12 -B corrected_invoice.py   # ~8 s
```
Outputs: `corrected_invoice.txt`, `corrected_invoice.json`.

Credits:
- DaysSky: the p19 word, invoice and package (#5270, #5440).
- Reviewers:
  - jwr404 / James Reed: compiler constants and the #5349 follow-up.
  - #5349: standard() ≠ controller().
  - zxv: same nine axes, unpriced middle idles, the 4256 repair and the concave-order audit.
  - Matarener / Mark: the Q-conjugated terminal gauge, letter R vs D, 4256, and the 1103/1202 tolerances.
  - Clear1nsight / Chris R: the IDLE stage-list decoding bug and the native C_jj = 0 counterexample.
  - gvconly / G. V. Chudnovsky: the independent simulator and the fresh-block coded replay failures.
- Lineage: PR4940 controller (Cayden Burkart / SethBurkart123), PR4929 producer (Dugongue), PR4933 code
  (Dillon Amburgey), Cinna Davis / 1337isnot1337.

This note re-derives their numbers independently from the package's own invoice and adds the merge-robust
bound and the idle-Q census. Prepared with Claude Opus 5.5 (Anthropic) via Claude Code, directed by Joel
Pulikkan (GamingPuzzled).
