# Ideal combined-lever budget grid for the selected complex local word

**Planning/screening table inside the retained ceiling model. No new κ; the selected
record is unchanged (`certificates/selected-result.json` stays at
κ = 0.001672660197076918).** No supplier admission, no frontier change, and no
statement about any real construction: every cell is a favorable relaxation that
omits the cost of realizing its levers (the same caveat as the published
one-at-a-time lever rows).

## What this package computes

`research/complex-local-word-ceiling/levers.py` prices seven one-at-a-time lever
rows; `docs/research/current-priorities.md` records one combined row (centre free +
rank-16, ×6.51). This package runs the **full 3 × 4 × 2 grid** of the three
published lever families through the parent exact-rational `ceiling()` at grid 1e-12,
under unchanged parent premises: `m = 73`, 896 live families over nine stages
(`w = 896/9`), outer halving guard `R = 51`, fractional idle remainder at rank `R`,
paid centre charge in PR1012's coverage identity.

* centre charge: `selected` (C = 64, eight rank-8 centre copies), `shared`
  (C = 32, four copies), `free` (C = 0, copies removed);
* local shape: the published word `{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}`
  (mass 5,586), or all paid local mass delivered as (fractional) children of rank
  8, 16 or 32. `selected` rows reshape the whole mass (as the published rank-8/16
  rows do); `shared`/`free` rows reshape the non-centre mass 5,522 and keep or drop
  the retained rank-8 copies;
* unpaid coordinates per live family: 1 (current coverage law) or 2 (the recorded
  what-if changed coverage law).

## Results (exact rational brackets in `RESULT.json`; decimals rounded)

| centre | local shape | unpaid u | a cap | × baseline | κ cap = a/(1+a) | κ ≥ 1/99? |
|---|---|---:|---:|---:|---:|---|
| selected (C=64) | published word | 1 | 0.001690054 | x1.000 | 0.001687203 | no |
| selected (C=64) | published word | 2 | 0.006377984 | x3.774 | 0.006337563 | no |
| selected (C=64) | all mass -> rank 8 | 1 | 0.002739504 | x1.621 | 0.002732020 | no |
| selected (C=64) | all mass -> rank 8 | 2 | **0.010354258** | x6.127 | **0.010248146** | **yes** |
| selected (C=64) | all mass -> rank 16 | 1 | 0.003909456 | x2.313 | 0.003894232 | no |
| selected (C=64) | all mass -> rank 16 | 2 | 0.014797223 | x8.755 | 0.014581458 | yes |
| selected (C=64) | all mass -> rank 32 | 1 | 0.006823270 | x4.037 | 0.006777028 | no |
| selected (C=64) | all mass -> rank 32 | 2 | 0.025914724 | x15.334 | 0.025260115 | yes |
| shared (C=32) | published word | 1 | 0.003212973 | x1.901 | 0.003202683 | no |
| shared (C=32) | published word | 2 | 0.007893112 | x4.670 | 0.007831299 | no |
| shared (C=32) | all mass -> rank 8 | 1 | 0.005219872 | x3.089 | 0.005192767 | no |
| shared (C=32) | all mass -> rank 8 | 2 | 0.012842951 | x7.599 | 0.012680101 | yes |
| shared (C=32) | all mass -> rank 16 | 1 | 0.007430577 | x4.397 | 0.007375771 | no |
| shared (C=32) | all mass -> rank 16 | 2 | 0.018307802 | x10.833 | 0.017978652 | yes |
| shared (C=32) | all mass -> rank 32 | 1 | 0.012887708 | x7.626 | 0.012723728 | yes |
| shared (C=32) | all mass -> rank 32 | 2 | 0.031857575 | x18.850 | 0.030874004 | yes |
| free (C=0) | published word | 1 | 0.004737653 | x2.803 | 0.004715314 | no |
| free (C=0) | published word | 2 | 0.009409964 | x5.568 | 0.009322242 | no |
| free (C=0) | all mass -> rank 8 | 1 | 0.007714442 | x4.565 | 0.007655385 | no |
| free (C=0) | all mass -> rank 8 | 2 | 0.015345904 | x9.080 | 0.015113967 | yes |
| free (C=0) | all mass -> rank 16 | 1 | 0.011008425 | x6.514 | 0.010888560 | yes |
| free (C=0) | all mass -> rank 16 | 2 | 0.021929660 | x12.976 | 0.021459070 | yes |
| free (C=0) | all mass -> rank 32 | 1 | 0.019209068 | x11.366 | 0.018847034 | yes |
| free (C=0) | all mass -> rank 32 | 2 | 0.038398085 | x22.720 | 0.036978194 | yes |

**Screening verdict (measured here).** Inside this model and these three lever
families, 12 of 24 cells reach the ambitious planning target κ ≥ 1/99
(≈ 0.010101010). The reaching set is upward closed in the lever lattice
(verified, 0 violations), and its minimal elements are exactly

* `selected centre + all-mass-rank-8 + u = 2` — κ cap 0.010248146 (+1.46 % over target),
* `shared centre + all-mass-rank-32 + u = 1` — κ cap 0.012723728,
* `free centre + all-mass-rank-16 + u = 1` — κ cap 0.010888560 (the published pair row).

Notable non-reaches: free centre + published word + u = 2 tops out at 0.009322242
(7.7 % short), and free centre + rank-8 delivery + u = 1 at 0.007655385 — so within
these families no combination of {centre relief} × {coverage relief} reaches the
target without reshaping the local delivery rank, and coverage relief (u = 2) is the
only single lever that, paired with rank-8 delivery at the full centre charge,
crosses 1/99. The tightest reaching cell sits barely 1.46 % over the target, while
#3811 reports a worst-case joint-integrality loss ≈ 1.35 % in the baseline centre
model — so that row's margin over the target is comparable to the reported integrality
cost and should not be treated as target-clearing under integer counts.

## Controls (all in `verify.py`, PASS_IDEAL_LEVER_GRID_BUDGETS)

1. All 24 exact brackets recompute and byte-match `RESULT.json`.
2. Every recorded endpoint certified: `relax(a_lo) < 1 < relax(a_hi)` on outward
   rational enclosures (`ceiling.py`, 2^-256 rounding).
3. Profile invariants: idle mass 1,646 at the selected cell (published value);
   child ranks in `(0, m)` and `≤ R`; local mass 5,586 / 5,554 / 5,522 for
   selected / shared / free centre rows.
4. **Live parent control:** the pinned `levers.py` is executed and its seven
   published rows agree with the matching grid cells at printed precision
   (`×1.00, ×2.80, ×1.90, ×2.31, ×1.62, ×3.77, ×6.51`; baseline cap
   0.001690054109089).
5. Lever monotonicity across the whole lattice: 0 violations.
6. Fail-closed guards: `R = 52` rejected (halving guard), `unpaid = 0` rejected,
   over-weight local profile rejected.
7. Bracket nesting: the 1e-8 brackets contain the 1e-12 brackets for three cells.

## Scope and limits — read before citing

* Ideal favorable relaxations for planning: fractional child counts, ideal idle
  packing at rank 51, no realization, hosting, restoration, precision or
  all-size cost for any lever. A reaching cell means "no packing/shape obstruction
  inside this model", **not** feasibility. #3811 shows attained integer optima sit
  up to ≈ 1.35 % below the fractional reading in the baseline model.
* Complex side only. The ambitious κ > 1/99 program additionally needs the bit
  supplier's effective budget above ≈ 1/99 (see the bottleneck brief); nothing
  here addresses the bit side, chronology or interfaces.
* Single fixed local-word family: the four shapes keep the paid mass fixed and
  reshape ranks; other coverage laws, port counts, templates or outer recipes are
  outside the parent ceiling model and outside this table.
* These are planning numbers under the retained balanced reduction κ < a/(1+a);
  the seven-step recipe attains slightly less. No new κ, no supplier, no
  selected-frontier change, and no claim that any lever is realizable.

## Reproduce

```sh
python3 -I -B research/ideal-lever-grid-budgets/verify.py     # ~11 s, PASS_IDEAL_LEVER_GRID_BUDGETS
python3 -I -B research/ideal-lever-grid-budgets/grid.py       # ~7 s, prints the table
python3 scripts/research_package.py --package research/ideal-lever-grid-budgets
```

`verify.py --write` regenerates `RESULT.json`. Exact arithmetic is the parent
`ceiling.py` (atanh log chains, Taylor exp with remainder, outward rounding to
2^-256); this package adds only the grid enumeration and controls.

## Open next questions

- **Integer-count twin of the minimal antichain.** Re-price the three minimal
  reaching cells with joint integer child counts (the #3811 DP at caps ≥ 32, plus
  integer idle), because the `sel|8|u2` margin over the target (1.46 %) is the same
  order as the known ≈ 1.35 % integrality loss. First step: reuse
  `research/complex-joint-integer-cap-ceiling`'s DP harness on the reshaped
  profiles; no new inputs needed if that PR's package lands.
- **Bit-side twin.** The same grid on the bit primitive's local word would say
  whether the target needs a third lever on the currently cheaper side. Blocked by:
  the bit word's published per-call local profile and coverage identity need to be
  pinned first (the ceiling tool is complex-side).
- **Realization pricing.** For `u = 2` (the cheapest crossing lever) no contract is
  known that leaves a second unpaid coordinate (`research/p104-*` and the coverage
  maps treat one unpaid coordinate as forced by the line-port contract); a plane-port
  discussion exists upstream. First useful evidence: a priced contract, not a better
  ceiling.

## Related open work

Peer packages pricing budgets/ceilings for the same selected complex local word
(none modified here; numeric cross-checks below were run against `RESULT.json`).

* [#3729](https://github.com/CrocSwap/integer-mult-bounds/pull/3729) — same model
  as my baseline cell but with integer idle counts (32x51 + 1x14). Overlap: the
  shared fractional anchor `0.001690054109089` lies inside my `sel|word|u1` bracket
  `[0.001690054109, 0.001690054110]`, and its attained integer ceiling
  `0.001688603446527` sits strictly below it, as integer tightening implies. Its
  0.0858 % integrality-loss column recomputes to 0.0858 % against my cap: agreement.
* [#3799](https://github.com/CrocSwap/integer-mult-bounds/pull/3799) — same
  inherited relaxation at φ = 0 (anchor identical to the baseline quote above,
  checked inside my bracket), then prices *free removal* of paid mass re-packed as
  ideal idle — an axis this grid does not touch (I reshape ranks, remove nothing),
  so no cell overlaps beyond the baseline. Its full-elimination figure
  `0.013675160009708` reproduces the stated 8.0916x against my grid-level cap.
* [#3805](https://github.com/CrocSwap/integer-mult-bounds/pull/3805) — same word,
  coverage law and centre, but sweeps the idle rank cap with optimal integer idle
  packing (aggregate 144-call normalization, same w = 896/9). My grid fixes idle at
  rank 51, so no cap endpoints coincide; the quoted fractional ceiling
  κ < 0.001687202646 agrees with my baseline κ cap to the quoted 12 decimals, and
  their per-call integer bracket lower end `0.0016886034465262156` lies below my
  baseline bracket exactly as integer tightening implies.
* [#3811](https://github.com/CrocSwap/integer-mult-bounds/pull/3811) — the
  integer twin of my shape lever at baseline centre/unpaid: attained joint integer
  packings for paid-mass caps 1..51. Shared quantity: its fractional class-relaxation
  control at cap 16 is the parent rank-16 lever row, which my `sel|16|u1` cell
  reproduces live (`[0.003909456001, 0.003909456002]`); its cap-8 integer-idle row
  `0.00273511` sits 0.160 % below my fractional `sel|8|u1` cap, the consistent
  direction. Its cap-44 κ `0.01020939` and my minimal reaching cell `sel|8|u2`
  κ `0.010248146` are close in magnitude but differ in premises (integer caps at
  baseline centre/u1 vs fractional rank-8 delivery with u = 2) — no shared quantity,
  no comparison claimed.
* [#1791](https://github.com/CrocSwap/integer-mult-bounds/pull/1791) — planning
  overhead budgets for centre-path sharing on the actual selected profiles; the
  centre rows here are ideal relaxations of the same lever paired with shape and
  coverage changes, not a realization price. No numeric overlap.

No contradiction found with any of the above; the three shared (or transitively
shared) quantities — the baseline relaxation ceiling, the parent rank-16 lever row,
and #3729's integrality-loss column — all agree numerically.

## Credit

Prepared by Nick Petalas with AI assistance. Independent human and formal
proof-kernel review are unclaimed. Model, coverage identity and ceiling tool are
credited to their authors above; no source file is modified by this package.
Apache-2.0.
