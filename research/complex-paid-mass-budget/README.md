# Paid-mass elimination budget for the selected complex local word

**Screening budget for the `complex-new-helper-inventory` card. No new κ; the
selected record is unchanged; no physical realization is proposed.**

The selected complex supplier (#1094) pays the per-call local profile
`{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}` — 3,494 paid children, 5,586 mass
units — and its certified packing ceiling is `a < 0.001690054109089`
([predecessor package](../complex-local-word-ceiling/README.md)). That ceiling
holds the local profile *fixed*: it allows every idle-remainder repacking but no
change in the paid word.

A helper-inventory or decoder proposal changes the paid word. Before any
synthesis, such a proposal must say **how much paid local mass it removes**.
This package prices that axis exactly and turns the card's screening step into a
budget curve: for every target saving `a`, the minimum fraction `φ(a)` of the
5,586 paid mass units per call that must be removed for the inherited relaxation
to certify `a`.

## Model and method

The model, the exact 256-bit rational arithmetic and the coverage identity
(paid mass `= 72·w + 64` per call, `w = 896/9` live families) are inherited
unchanged from `research/complex-local-word-ceiling/ceiling.py`, imported as a
live source. Everything added here is one linear-freedom axis:

* a proposal removes `μ` paid mass units per call, `0 ≤ μ ≤ 5,586`;
* the removed mass stays inside the coverage budget and is re-packed as ideal
  rank-`R = 51` idle children;
* **removal is free**: no decoder, helper, restoration or consumer cost is
  charged. This is the most favorable version of the proposal.

The optimal removal is lowest rank first. A rank-`r` child costs
`(r/m)^(1-a)`; re-packing one unit of its mass at rank `R` costs
`(R/m)^(1-a)/R`, so the saving per unit of removed mass is

```text
r^(-a) m^(a-1) - R^(-a) m^(a-1)  >  0   for every r < R,
```

which is strictly decreasing in `r`. Greedy removal from ranks `1,2,3,4,5,8` in
that order is therefore the exact optimum of this relaxation at every `μ`;
`verify.py` checks the ordering at four exponents and rejects a rank-reversed
control.

## Results (certified rational enclosures, `verify.py`)

### Whole-child curve (the physical steps)

| removed mass / call | φ | certified ceiling |
|---:|---:|---:|
| 0 | 0 | **0.001690054109089** |
| 2,412 (all rank-1) | 0.431793770 | 0.003081073334575 |
| 3,248 (+ all rank-2) | 0.581453634 | 0.004028350731628 |
| 4,544 (+ all rank-3) | 0.813462226 | 0.006916067471101 |
| 5,112 (+ all rank-4) | 0.915145005 | 0.009650209177053 |
| 5,522 (+ all rank-5) | 0.988542785 | 0.013070495581102 |
| 5,586 (all paid mass) | 1 | **0.013675160009708** |

### Decision thresholds (continuous φ, fractional children allowed)

| target `a` | what it means | minimum φ | removed mass |
|---|---:|---:|---:|
| 0.001675460000 | selected complex endpoint | 0 | 0 |
| 0.001690054109 | inherited ceiling | 0 | 0 |
| 0.001733430000 | published bit primitive budget | **0.023948528** | 133.776 |
| 0.002000000000 | round target | 0.148297888 | 828.392 |
| 0.010101010101 | planning target `1/99` | **0.927698485** | 5,182.124 |

Bisection tolerance is `10⁻⁹` mass units; each reported ceiling is the
certified bracket `[a_lo, a_hi]` with `relax(a_lo) < 1 < relax(a_hi)` and
width below `10⁻¹⁵`.

## What this changes

1. **A price for making the bit side bind.** Under the retained balanced
   reduction the selected κ is limited by the complex primitive, and that
   primitive can only stop binding if its saving reaches the bit primitive's.
   On this word's packing relaxation that requires **φ ≥ 2.3949 %** at the
   published approximate bit budget `0.00173343`, i.e. 133.8 of the 5,586 paid
   mass units per call — under a relaxation that charges nothing for the
   removal. So any proposal on this word that removes less cannot make the bit
   side bind, whatever its other merits; a proposal that removes more has only
   passed this screen and still owes a construction.
2. **Mass elimination is a weak lever.** The entire paid word is worth only
   `8.0916×` the inherited ceiling, and `1/99` needs `φ ≥ 92.77 %`. Even
   deleting every paid child and paying all 7,232 mass units as ideal rank-51
   children certifies only `a = 0.013675160009708`, which is `1.354×` the
   planning target. So a target-scale gain cannot be bought by shrinking the
   local word at this template and coverage law: it needs the coverage law, the
   centre charge, the template or the outer recipe to change.
3. **A screen, not a construction.** The card asks for an optimistic exact
   moment before synthesis. This is that moment, as a function of the one
   quantity every proposal can state: its per-call paid mass.

The predecessor's remark that a target-scale gain needs a local word whose fully
priced excess spend is "about 95 % lower" is a statement about excess spend. The
`92.77 %` figure here is a different, mass-based criterion measured against a
strictly more favorable relaxation (free removal). The two do not contradict
each other, and neither is a lower bound for multiplication.

## Scope and limits

* **Favorable relaxation.** Removal costs nothing. A real decoder, helper
  interface or consumer that removes paid mass pays something, so a physical
  proposal must remove *more* than these thresholds. This package cannot admit
  or reject a specific physical proposal; it prices the entrance fee.
* Fixed to the selected word, 112 ports, the nine-stage four-pair template, one
  unpaid coordinate per live family, centre charge 64 and the halving guard
  `R = 51`. Other words, templates, coverage laws, centre charges and outer
  recipes are outside it.
* Fractional child counts are allowed, as in the inherited relaxation; the
  whole-child breakpoints are reported separately for physical reading.
* At the selected endpoint `φ = 0`: the relaxation is not tight there, so this
  budget does not measure the selected construction's remaining slack.
* No κ, certificate, selected-frontier or supplier change. This is not a
  complete multiplication theorem.

## Controls rejected by `verify.py`

1. inherited ceiling not reproduced from the pinned module;
2. a whole-child breakpoint with a bracket wider than the grid;
3. a non-increasing step in the whole-child curve;
4. a non-positive per-unit saving for some rank `r < R`;
5. a saving ordering that is not strictly decreasing in `r`;
6. a rank-reversed removal that is not strictly more expensive at half the mass;
7. full elimination that does not equal the closed-form pure-idle moment;
8. the bit-budget crossing falling outside the first half of the paid mass, or
   the `1/99` crossing outside the last tenth;
9. a target above the full-elimination ceiling reported as reachable.

## Reproduce

```sh
python3 -I -B research/complex-paid-mass-budget/verify.py    # ~17 s, PASS_COMPLEX_PAID_MASS_BUDGET
python3 -B scripts/research_package.py --package research/complex-paid-mass-budget
python3 -B scripts/check_research_commit.py --package research/complex-paid-mass-budget --check-source-history
```

The card's first working example is the inherited positive control:

```sh
python3 -B research/complex-local-word-ceiling/verify.py
# PASS_COMPLEX_LOCAL_WORD_CEILING a_ceiling 0.00169005410908900006
```

Python 3.12 at `~/git/integer-mult-bounds/.venv/bin/python3.12`; standard
library only.

## Open next questions

* **Is the elimination axis attainable by any stated physical interface?** A
  candidate decoder or helper inventory would have to state a per-call profile
  with at least `φ` fewer paid mass units at the same coverage law, then pay for
  the removal. First step: take one submitted candidate's per-call profile and
  run `ceiling.ceiling()` on it. Blocked by: no submitted candidate states a
  per-call profile below 5,586 paid mass units under this coverage law.
* **How does the budget curve scale with the port count V?** `φ` is normalized
  per call, and the coverage budget grows with `w = 2·pairs·V/stages`, so a word
  whose paid mass grows more slowly than V would need a smaller `φ`. First step:
  run the same curve on a recorded word with a different V on a comparable
  template. Blocked by: per-call paid profiles at other V are not collected in
  one place.
* **Does the centre path's own 64 mass units have a cheaper elimination than the
  generic rank-51 re-packing?** The eight rank-8 children are the last group in
  the curve and the most valuable to remove per unit. First step: bind a
  submitted centre-sharing contract's per-call centre mass. Blocked by: the
  centre-sharing proposals state sharing ratios, not eliminated mass.

## Credit

The coverage identity is PR1012's. The packing ceiling, its exact arithmetic and
the lever table are Douglas Colkitt's `complex-local-word-ceiling` package; this
package imports that module unchanged. The selected construction's credits are
in its review. Prepared by Nick Petalas with AI assistance; independent human
and formal proof-kernel review are unclaimed. Apache-2.0.
