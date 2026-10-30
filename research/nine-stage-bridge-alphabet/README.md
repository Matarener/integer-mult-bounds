# Nine-stage bridge schedules force the 16/32/48 idle alphabet

**Negative, scoped result. No new κ and no change to any supplier.**

On the complex side, the paid profile of every recent word includes idle children of ranks 8, 16, 32 and 48.
They come from the data route of the nine-stage template. Whole helpers are hosted into those children, and
the remainders are paid. A different idle alphabet would pack the same helpers better. In the relaxed
fixed-supplier packing model of PR3633 (no chronology), with the retimed T488 supplier of PR3653, the best
alternative alphabets would price as follows:

| idle children per side | relaxed root | vs incumbent |
|---|---|---|
| 8, 8, 8, 16, 16, 32, 32, 48, 48 (incumbent) | 0.0017304189 | reproduces PR3653 |
| 8, 8, 8, 8, 16, 32, 40, 48, 48 | 0.0017362369 | +0.336% |
| 8, 8, 8, 16, 16, 24, 40, 48, 48 (merge pair 2's prefix 32+8 into 40) | 0.0017434846 | +0.755% |

The +0.755% value lies above the open bit-side claim 0.0017366 (PR3647). This package asks whether a
different **bridge schedule** can produce such an alphabet. Within the class below, the answer is no.

## Why the alphabet is 16/32/48

`global_nine.py` and `data_phases.py` (vendored in `research/e8-signed-prefix`) define the template.
It has four data pairs (X, Y) and nine stages. Stage s takes its owner pair from level s−1 to s and shears it:
forward Y += X, reverse X −= Y. A bridge (i ← j, q) adds q·X_j to X_i and subtracts q·Y_i from Y_j.
After a final exchange (X, Y) → (Y, −X), the eight-wire matrix must be the identity. That is the exact
check in `research/e8-complex-gauge-kernel/code/replay_gk.py` (`global_check`), and this package uses it
verbatim. Idle children advance a pair between touches. Merging two of them is legal only if nothing touches
the pair in between.

Each pair needs three alternating shears, which makes 12 shears, but there are only 9 stages. Pairs 1–3
therefore ride the forward stage 2, 4 or 6 of the previous pair, using a bridge before and after that stage.
The bridges read the riding pair at levels 2j−1 and 2j. This splits its prefix into 16+8, 32+8 and 48+8,
and its tail follows from its own stages. So "merge 32+8 into 40" is not legal in RECIPE-9.

## Result

A **simple-riding design** assigns each of the 9 stages an owner pair and a direction. It then lets pairs
ride other pairs' stages, so that every pair receives three alternating shears (U L U or L U L). Riding
bridges are oriented so that the rider receives the owner's shear: (owner ← rider) on forward stages and
(rider ← owner) on reverse stages. Final bridges at level 8 cost no idle rank. They generate exactly
{diag(A, A^−T) : A ∈ SL(4, Z)}, so the closure test is exact and it constructs those final bridges explicitly.

`verify.py` checks the following (standard library only):

* RECIPE-9 closes under the copied rule, and a flipped bridge coefficient does not.
* The level model reproduces the nonzero idle ranks of all 112 DATA-PHASES ports.
* The builder rebuilds RECIPE-9, and the closure test recovers its three final bridges (3←2, 2←1, 1←0).
* **Census.** There are 2,037,336 simple-riding designs with 271 distinct idle alphabets (all children ≤ 51).
  All 37,968 designs with globally alternating directions were tested exactly. **Exactly 16 close, and all
  of them have the incumbent alphabet.** All 728 designs with the best relaxed alternative alphabet were
  also tested, and none closes. A deterministic sample of 2,000 non-alternating designs (every 1000th in census order) gives no closing
  design either.

Separate long searches (`tools/free_bridges.py`, logs in `evidence/`) add "free" bridges. A free bridge is
placed where both pairs already sit at a level they are touched at, so it creates no new idle child. With
one free bridge, 61,888 insertions over the 728 designs of the +0.336% alphabet and 8,800 over the 104
designs of 8,8,8,24,24,48,48,48 were tested. With two free bridges, all ≈2.6 million insertions over the
728 designs were tested. **None closes.** These searches are recorded runs, not part of `verify.py`.

## Scope and limits

* This is an exhaustive search inside the stated class, with sampling for non-alternating directions, not
  an impossibility theorem. A heuristic reason: 9 = 2·4 + 1 is the minimum number of rank-one shears for
  the four-pair exchange, and at the minimum the pairs must form a chain on the even stages.
* Not covered: riding across two stages, bridges with |q| > 1 inside the schedule, more than two free
  bridges, other pair-coupling mechanisms, more stages (73 = 9 + 8·8 fixes nine), and changes to the local
  word.
* The packing prices are relaxed LP planning numbers (`tools/packing_lp.py`, needs scipy;
  `evidence/packing-lp.txt`). They ignore chronology and owner windows.

## Reproduce

```sh
python3.12 -B research/nine-stage-bridge-alphabet/verify.py      # about 3 minutes, standard library
python3 scripts/research_package.py --package research/nine-stage-bridge-alphabet --check-only
python3 -B research/nine-stage-bridge-alphabet/tools/packing_lp.py 8,8,8,8,16,32,40,48,48
python3 -B research/nine-stage-bridge-alphabet/tools/free_bridges.py --k 1   # long; --k 2 takes hours
```

## Open next questions

1. **Can a coupling mechanism other than bridge riding give one pair a single 40-wide prefix?** It would be
   worth +0.755% on the complex side in the relaxed model, which is above the bit claim. First step: a
   riding variant that spans two stages, priced with `tools/packing_lp.py` and tested with
   `bridges.closure`. Blocked by: no candidate mechanism yet.
2. **Is the alternating-direction restriction provably without loss?** Sampling found no closing
   non-alternating design. First step: an invariant (for example, the rank of the accumulated shear blocks)
   that rules them out. Blocked by: none known.

## Credit

The nine-stage template, data routes and phases come from the e8 nine-stage lineage retained in
`research/e8-signed-prefix` and `research/direct-delivery504-global`. The eight-wire check comes from
`research/e8-complex-gauge-kernel`. The packing model is from PR3633 (staged-width T488), and the supplier
profile is from PR3653 (retimed T488 composition). Idle-child merging follows `research/idle-axis-hosting`.
Found and checked by Claude (Anthropic) via Claude Code, in a session donated by Mark (Matarener).
Apache-2.0. No human or formal review is claimed.
