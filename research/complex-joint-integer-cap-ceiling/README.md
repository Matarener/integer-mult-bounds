# Exact attained ceiling of the rank-capped complex local mass

**Scoped bound inside the ceiling model of `research/complex-local-word-ceiling`. No new κ; the
selected record is unchanged.**

The parent package prices the selected complex local word with two *fractional* relaxations:

- its idle remainder sits in `1646/51` fractional rank-51 children, because cost per unit of paid
  mass `r^(-a) m^(a-1)` falls with the child rank `r`; and
- its rank-cap continuation reshapes the local paid mass `5586` into `5586/s` fractional rank-`s`
  children, the one lever that raises the ceiling with the coverage law, the centre charge and the
  outer halving guard all untouched.

Both are upper bounds, because a real packing uses an integer multiset of children in each pool.
This package computes the **attained optimum over joint integer packings** for every cap
`s = 1..51` the guard `m² > 2R²` allows: the local paid mass in integer children of rank at most
`s`, the idle remainder in integer children of rank at most `R = 51`, both by dynamic programming
over the mass axis, and each cap is certified in both directions.

## Result

Model inputs are unchanged from the parent and re-checked here from the pinned certificate: paid
local mass `5586` per call, idle remainder `1646`, parent width `m = 73`, `2·4·112` live data
families per nine-stage replica (`w = 896/9`), centre charge `64`, the PR1012 coverage identity
`mass = 72·W + 64·N`, and the outer halving guard `R = 51`. The only addition is that both child
counts are integers.

| Quantity | Value |
|---|---|
| Cap at which the **joint integer** class first clears the planning target `a = 1/99` | **44** (caps 43 and below fail) |
| Joint ceiling at cap 44 | `a = 0.01031470`, `κ ≤ 0.01020939`, ×6.10 the selected κ |
| Joint ceiling at the guard cap 51, histogram `{51: 109, 27: 1}` | `a = 0.01349051`, `κ ≤ 0.01331094`, ×7.96 the selected κ |
| Worst integrality loss anywhere on the curve | **1.35033 %**, at cap 51 |
| — of which paid-mass rounding | 0.66054 % |
| — of which idle-remainder rounding | 0.68979 % |
| Paid-mass dynamic-program optimum vs largest-first greedy | equal cost at **all 51 caps**; equal histogram at all 51 |

The idle packing is the same at every cap — `{51: 32, 14: 1}`, i.e. `32·51 + 14 = 1646` — because
the idle pool does not depend on the paid cap. At the guard cap the joint figure is **0.99 % below**
the class relaxation `0.01367517`, and the selected κ is untouched.

Representative rows (all 51 are in [RESULT.json](RESULT.json), each a grid bracket of width `1e-8`
with both ends witnessed):

| cap `s` | class relaxation | greedy paid histogram + fractional idle | joint integer ceiling | integrality loss |
|---:|---:|---:|---:|---:|
| 1 | 0.00144351 | 0.00144351 | 0.00144246 | 0.0727 % |
| 8 | 0.00273951 | 0.00273892 | 0.00273511 | 0.1606 % |
| 16 | 0.00390946 | 0.00390766 | 0.00389990 | 0.2445 % |
| 43 | 0.00999974 | 0.00998900 | 0.00993809 | 0.6165 % |
| 44 | 0.01037551 | 0.01036958 | **0.01031470** | 0.5861 % |
| 48 | 0.01209571 | 0.01202288 | 0.01194905 | 1.2125 % |
| 51 | 0.01367517 | 0.01358484 | **0.01349051** | 1.3503 % |

## Integrality has two halves, and the published column counts one

A live rank-cap table (open peer PR #3701, not on this main) reports, for the same class,
`a_frac(s)` — the fractional relaxation — and `a_int(s)` — the largest-first greedy integer paid
histogram with the **fractional** idle block. Its headline consequence is that rank-51 delivery
alone clears `1/99` arithmetically, and its control is "integrality is not the obstruction": the
worst integrality loss anywhere on its curve is `0.6605 %`.

This package reproduces that column independently, exactly, at its own grid: cap 44 →
`0.010369575356` against the reported `0.0103695754`, cap 51 → `0.013584830798` against the
reported `0.0135848308`, with the same histograms `{44: 126, 42: 1}` and `{51: 109, 27: 1}`. Both
numbers are certified in [RESULT.json](RESULT.json).

The corrected reading is that `0.6605 %` measures the **paid-mass** rounding only. A real packing
must also round the idle remainder, which adds `0.68979 %` at the guard cap and is the *whole* loss
at cap 1. The joint worst case is **1.35033 %**, about 2.04× the published figure, and the idle
share shrinks as the cap grows rather than staying constant. The qualitative conclusion is the same
and is now reached on an attainable object: cap 43 fails (`0.00993809 < 1/99`) and cap 44 clears
(`0.01031470 > 1/99`), with a margin of 2.1 % of `a` instead of the mixed figure's 2.7 %.

## Controls

`verify.py` records twelve control groups; `RESULT.json` stores every value.

- The class relaxation computed here equals the pinned parent's own `ceiling()` on the reshaped
  profile `{s: 5586/s}` at caps 8, 16 and 51 (within one grid step), which is the cross-check that
  the two packages use one model. At caps 8 and 16 those rows are the parent's lever table entries
  "local mass delivered as rank-8 / rank-16 children".
- The live rank-cap column is reproduced at its grid at caps 44 and 51, and the paid-mass
  elimination endpoint of the fourth cited package equals this class relaxation at the guard cap
  (`0.013675160009708`, agreement below `1e-9`).
- The paid dynamic-program optimum equals the largest-first greedy cost *and* histogram at all 51
  caps, extending the live table's recorded 11-cap check to the full guard range with no ambiguity.
- Every bracket is witnessed on both sides: an explicit joint integer packing with certified moment
  `< 1`, and a certified lower bound of every joint integer packing `> 1`.
- Both histograms conserve their mass exactly and use only ranks inside their cap, at every cap.
- The joint bracket lies at or below the class relaxation at every cap, and is monotone in the cap.
- Twenty-five randomly drawn joint packings at each of caps 8, 16, 44 and 51 never reach the
  rejected saving; the sampling control is retained only as a weaker statement.
- The coarse `1e-8` bracket contains the `1e-12` bracket at caps 8, 16 and 51.
- The local profile, its split and the coverage identity are re-derived from the pinned certificate
  and audit file, not copied.

## Relation to adjacent work

- **`research/complex-idle-integrality-ceiling` (open peer PR #3729)** fixes integrality of the idle
  remainder for the *incumbent* paid profile and reports `a < 0.001688603446527`. This package is a
  different degree of freedom: it reshapes the paid mass into rank-`s` children and prices the
  same idle rounding inside every cap class. Both packages build on the parent's exact intervals;
  this one imports `ceiling.py` and re-derives the profile independently.
- **Open peer PR #3701** is the rank-cap continuation cited above. This package extends its column
  with the second half of integrality and reproduces its numbers as a control; it does not restate
  its rank-shape conclusion.
- **`research/complex-local-word-ceiling`** supplies the model, the coverage identity (PR1012), the
  halving guard and the lever table, unmodified and pinned in [SOURCES.json](SOURCES.json).

## Related open work

Three open peer packages price the same selected complex local word inside the same parent ceiling
model. None is modified here, and each is cited for comparison only.

- **`research/complex-idle-integrality-ceiling` (#3729)** holds the incumbent paid profile fixed and
  makes the idle counts integral per call: its optimum is `{51: 32, 14: 1}` per call and its ceiling
  is `a < 0.001688603446527`. **Agreement:** this package uses exactly that idle packing at every
  cap (`32·51 + 14 = 1646`) and the same per-call premise. **What differs:** #3729 re-optimises the
  idle remainder of the incumbent word, while the cap-`s` rows here reshape the *paid* mass into
  rank-`s` children, so the cap-8 row `0.00273511` is the integer-idle version of the parent's
  rank-8 lever row, not #3729's incumbent ceiling.
- **`research/idle-rank-cap-sensitivity` (#3805)** prices the idle *rank cap* and separates two
  pooling premises: an aggregate optimum that pools the idle mass across the replica
  (`4647×51 + 27` at cap 51, certified gain `+0.870319 %`) and a per-call-forced optimum that does
  not (`32×51 + 14` per call, `+0.784307 %`). **This package uses the per-call premise throughout:**
  every row packs one call's own `1646` units, which is integral, so its rows belong with #3805's
  per-call row and with #3729, and are **not** comparable with #3805's aggregate rows. The two
  packages also sweep different axes: #3805 varies the idle cap `46..51` at a fixed paid word; the
  cap here is the largest *paid* child rank, with the idle cap held at the guard `R = 51`.
- **`research/complex-paid-mass-budget` (#3799)** prices a free removal of paid mass at fixed rank
  shape. Its full-elimination endpoint `0.013675160009708` (all `5586` paid units removed and
  re-packed as ideal rank-51 children) is **the same object as this package's cap-51 class
  relaxation**, and the agreement is registered as a control below; its `φ = 0` row is the parent's
  inherited ceiling `0.001690054109089`. **What differs:** #3799's `1/99` threshold `φ ≥ 92.7698485 %`
  is a *mass-removal* budget, whereas cap 44 here clears `1/99` with **no mass removed at all**, by
  delivering the same paid mass in rank-`≤44` children. Same model, same target, different lever;
  neither statement bounds the other, and both are relaxation-level screens.

## Scope and limits

- This is a bound **within the parent's ceiling model**: one fixed paid local mass and one fixed idle
  remainder per call, `m = 73`, 896 families over nine stages, centre charge 64, the coverage law
  and the halving guard. It is **not** a bound for other local words, port counts, templates,
  coverage laws or outer recipes.
- The cap-`s` rows describe **reshaped** classes, not the incumbent word: the incumbent's paid
  profile is `{1: 2412, 2: 418, 3: 432, 4: 142, 5: 82, 8: 8}` and its own ceiling is the parent's.
  A cap-`s` row answers "what could a word whose paid mass is delivered in rank-`s` children
  reach", not "what does the selected word reach".
- A histogram is not a circuit. Every row still allows every repacking without checking physical
  realizability, frames, copies or restoration, and the class is priced per call.
- Brackets are grid-quantized to `1e-8` in `a` (fine-grid control at `1e-12`); a tighter interval
  can be read straight off the same predicates.
- No κ is claimed, no supplier is admitted, and the selected frontier is unchanged.

## Reproduce

```sh
python3 -I -B research/complex-joint-integer-cap-ceiling/verify.py          # ~2.5 min, PASS_COMPLEX_JOINT_INTEGER_CAP_CEILING
python3 scripts/research_package.py --package research/complex-joint-integer-cap-ceiling
```

`verify.py --write` regenerates `RESULT.json`. Standard library only; exact rational arithmetic with
outward rounding to 2⁻²⁵⁶, re-using `ceiling.py`'s logarithm, exponential and interval primitives.

## Open next questions

- **Does any candidate packing that was screened against a cap-`s` ceiling survive the joint integer
  curve of the same class?** Such a candidate was screened against a figure that mixes an integer
  paid histogram with a fractional idle block; the certified joint curve is lower by up to 1.35 % of
  the ceiling, so a candidate sitting near its own cap's ceiling can be rejected by the corrected
  value. Blocker: the candidate histograms live in their own packages.
- **Does the idle remainder's share of the integrality loss keep falling as the cap grows?** At cap 1
  the whole loss is the idle rounding, at cap 51 its share is 0.51. Blocker: per-call idle masses
  for other words on a comparable template are inside their own packages.

## Credit

Prepared by Nick Petalas with AI assistance. Apache-2.0. The ceiling model, the coverage identity
(PR1012), the fixed-word packing-ceiling lineage (static44, PR525, PR643) and the lever table are
Douglas Colkitt's and his credited predecessors'; see
`research/complex-local-word-ceiling/README.md`. The rank-cap continuation of that model is an open
peer artifact (#3701) and the idle-integrality companion is another (#3729); both are cited above and
neither is modified here.
