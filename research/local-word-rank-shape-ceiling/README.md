# Rank-shape ceilings for the selected #1094 complex local word

**Scoped exact obstruction and planning table. No new κ, no construction, and the
selected record is unchanged.**

The retained packing ceiling for the selected complex local word
(`research/complex-local-word-ceiling`) is `a < 0.001690054109089`. Its ideal
lever table prices "local mass delivered as rank-8 children" and "as rank-16
children" and stops there. This package fills in the whole range the outer
halving guard allows (`R = 51`), and replaces the fractional child counts in that
table with exact integer ones.

## Question

Under the selected template, coverage law and halving guard, **how much of the
ceiling does the shape of the paid local child histogram recover on its own?**

Cost per unit of paid mass is `m^(a-1) r^(-a)`, strictly decreasing in `r`, so a
larger child is cheaper per unit. Rank shape is the only lever that moves the
ceiling without changing the coverage law, the centre charge or the outer guard.
That makes it the lever with the fewest unpriced obligations, and its ideal budget
should be known exactly before anyone synthesises a block-climb decoder.

## Model

Per call the selected word pays `local = 5586` units of rank mass on ranks ≤ 8
(`{1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}`), and the coverage law (PR1012)
fixes the remaining `idle = 1646` of the call's `7232 = 72w + 64` units on
`w = 896/9` live families. The sibling ceiling model places every idle unit in
fractional rank-`R` children with `R = 51`, the largest rank with `73² > 2·51²`.

Restricting **only the local word's paid children** to ranks `≤ s` and leaving the
coverage law, the centre charge `64`, `w` and the idle treatment untouched gives
two certified ceilings per cap:

| bound | histogram | meaning |
|---|---|---|
| `a_frac(s)` | `{s: 5586/s}`, fractional | ideal relaxation; **upper**-bounds the cap-`s` class |
| `a_int(s)` | `greedy(5586, s)`, integer counts | exact child count; **lower**-bounds the cap-`s` class |

So `a_int(s) ≤ cap_s ≤ a_frac(s)` is a sandwich obtained without any search over
histograms. Both bounds use the sibling package's exact rational-interval
arithmetic (`ceiling.py`) unchanged, at that package's own `1e-15` grid, so the
incumbent ceiling can be compared to its stored value exactly.

## Results

Incumbent ceiling, re-derived from the pinned assembly inputs and matched against
the pinned sibling `RESULT.json`: `a = 0.001690054109089` (κ = 0.001672660197076918).

**The a = 1/99 crossing is at rank cap 44, for both bounds.**

| cap `s` | certified `a_int(s)` | ×incumbent | κ bound |
|---:|---:|---:|---:|
| 8 | 0.0027389163 | 1.62× | 0.0027314352 |
| 16 | 0.0039076562 | 2.31× | 0.0038924459 |
| 32 | 0.0068096685 | 4.03× | 0.0067636105 |
| 40 | 0.0089514766 | 5.30× | 0.0088720586 |
| **43** | **0.0099889993** | 5.91× | 0.0098902060 |
| **44** | **0.0103695754** | **6.14×** | **0.0102631508** |
| 48 | 0.0120228772 | 7.11× | 0.0118800448 |
| **51** | **0.0135848308** | **8.04×** | **0.0134027566** |

Three consequences, all measured:

1. **Rank-cap obstruction.** No local word all of whose paid children have rank
   `≤ 43` can certify `a ≥ 1/99` on this template. The class `{paid ranks ≤ 43}`
   tops out at `a < 0.0099889993`. This is a strict bound, not a relaxation gap:
   even the ideal fractional relaxation gives only `a_frac(43) = 0.0099997320`,
   and `1/99 = 0.0101010101`.
2. **The lever alone suffices at the guard cap.** With the centre charge, the
   coverage law and the outer recipe untouched, delivering the local mass in
   rank-51 children reaches `a < 0.0135848308`, κ ≤ 0.0134027566, **8.04× the
   incumbent ceiling** and well past the `1/99` planning target. The retained
   lever table reaches `1/99` only in the combined row that *also* makes the
   centre path free; that additional obligation is not needed for a
   target-scale complex saving on arithmetic grounds alone.
3. **Integrality is not the obstruction.** Requiring integer child counts costs at
   most **0.6605%** of the ceiling anywhere on the curve (worst at `s = 51`), and
   where the cap divides 5586 the two bounds coincide exactly. Divisibility is
   not what makes the lever table's fractional rows unrealisable.

Supporting checks, all exact:

- The greedy histogram `greedy(5586, s)` equals the optimum of an independent
  exact-enclosure dynamic program at 11 caps × 3 screening savings
  (5e-05, 0.005, 0.01375), with **0 ambiguous comparisons** — every dynamic-program
  comparison was decided by disjoint enclosures.
- The curve is asserted monotone in `s` for both bounds, and every reported
  histogram is checked to be a positive integer child list of total mass 5586
  with largest rank `≤ s`.
- The incumbent ceiling recomputed here equals the pinned sibling `RESULT.json`
  value as an exact `Fraction`, so this package re-derives the baseline instead of
  trusting a stored number.
- At `a = 0` the per-call moment is `local/m` for *every* histogram, so the whole
  ceiling model is second-order in `a`. No rank shape is preferred at zero
  saving; the entire curve comes from second-order terms. This is checked
  directly in exact `Fraction` arithmetic.

### The crossing at 44 is not robust to residual shape

Under a stricter bimodal model — `k` children of rank `s`, everything else rank 1
— the target is **unreachable at `s = 44`**: even `k = 126` plus 42 rank-1 units
tops out at `a = 0.00990611`. The cap-44 optimum `{44: 126, 42: 1}` clears it at
`0.01036958`. The 5% difference is entirely the 42 residual units. The first
reaching caps are:

| `s` | minimum `k` rank-`s` children | share of local mass | `a(k)` | `a(k-1)` |
|---:|---:|---:|---:|---:|
| 43 | unreachable | — | 0.009596 | — |
| 44 | unreachable | — | 0.009906 | — |
| 48 | 114 | 97.96% | 0.010485 | 0.009931 |
| 51 | 106 | 96.78% | 0.010696 | 0.010078 |

Each `k` is bisected over the integers and then bracketed by two certified
ceilings (`a(k) ≥ 1/99 > a(k-1)`). The share matters for planning: **a partial
adoption of large-rank children does not move κ at target scale.** At the guard
cap, 97% of the local paid mass must ride on rank-51 children; a pilot that
converts a quarter of the word gains nothing at this scale.

## What this does not establish

- **It is a relaxation, not a construction.** `a_int(s)` is a histogram, not a
  word. Nothing here shows any decoder can emit a rank-44 or rank-51 child, and
  the ceiling model already assumes fractional idle children of rank 51 are free.
- **It does not meet the card's acceptance gate**, which requires a per-call local
  profile with copies, frames and restoration counted. The card says an optimistic
  passing relaxation alone is not acceptance; this package is that relaxation,
  certified and inverted. `TASK.json` records the scope as `refined`.
- **It is not a bound for other local words**, port counts, templates, coverage
  laws or outer recipes. The cap curve is a function of the incumbent word's mass
  (5586) under the incumbent template.
- **κ = a/(1+a) is the retained balanced reduction's planning ceiling**, not a
  realised κ. No number here is a supplier for the selected record.
- The dynamic-program optimality check is exact only where no comparison was
  ambiguous. All 33 reported cap/saving pairs had zero ambiguities, but the check
  is a bounded screening, not a proof of greedy optimality for every integer mass.

## Reproduce

```sh
python3 -I -B research/local-word-rank-shape-ceiling/verify.py   # ~40 s, PASS_LOCAL_WORD_RANK_SHAPE_CEILING
python3 scripts/research_package.py --package research/local-word-rank-shape-ceiling
```

`verify.py --write` regenerates `RESULT.json`. No dependencies beyond the Python
standard library. The exact arithmetic, the coverage identity and the incumbent
ceiling all come from
[`research/complex-local-word-ceiling`](../complex-local-word-ceiling/README.md);
`rankshape.py` only adds the integer-histogram construction, the sandwich and the
dynamic program.

## Open next questions

- **What is the largest paid child rank a physical local word on this template can
  actually emit, with copies, frames and restoration counted?** This is the
  missing lemma the card asks for, and the curve now says it has to be `≥ 44`.
  Until it is bounded, further moment arithmetic below cap 44 is wasted.
  Blocked: no source-bound itinerary carries a child-rank inventory.
- **Which residual shapes near the crossing are physically available?** The cap-44
  optimum and the bimodal-44 reading differ by 5% on 42 units of residual mass.
  A fixed block size produces only "one block plus one smaller block" shapes, so
  the certified optima for `s = 40..51` should be classified that way.
  Blocked: the same missing itinerary.
- **Does the curve move with the port count `V`?** The budget grows with families
  per call and a decoder's excess spend need not grow as fast.
  Blocked: per-call local profiles for `V ≠ 112` on a comparable template.

## Credit

The coverage identity is PR1012's. The packing-ceiling model, the exact interval
arithmetic and the lever framing are
[`research/complex-local-word-ceiling`](../complex-local-word-ceiling/README.md)
(Douglas Colkitt with substantial Claude/Anthropic assistance), which in turn
credits the static44 / PR525 / PR643 lineage and Ali Romman's
heterogeneous-owner assembly bound. The selected construction credits are in its
review. This package's rank-cap sandwich, integer-histogram construction,
dynamic-program check and target inversion are by Nick Petalas. Apache-2.0.