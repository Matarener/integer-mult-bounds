# Diagnostic: the lowest open quadruple class (LP 12.571)

This is local, exploratory evidence. It is not part of the registered verifier and is not a theorem.

## The class

The example quadruple is planes `(7, 8, 15, 52)`. Its single-plane cross tariffs are

- `A–B` and `C–D`: 0, so messages between those planes are free;
- every other cross pair: 2, with each such plane pair's joint Gram of rank 2 ("aligned").

The full closure costs 8. The best zeroed-block LP value is 88/7 = 12.571.

## Why the zeroed-block family stops short here

Take `Z = {AB, BA, CD, DC}`. The candidate `L(M) = 2·rank(Φ_Z(M))` has `L(I) = 16` and satisfies 221 of
the 225 atom inequalities. It fails only on `(ABC, ABD)`, `(ABD, ABC)`, `(ACD, BCD)` and
`(BCD, ACD)`, which each cost 4. On `(ABC, ABD)` the image `Φ_Z(u vᵀ)` has row vectors

    w_A = (v_A, 0, v_D),   w_B = (0, v_B, v_D),   w_C = (v_A, v_B, 0),

with `w_A + w_B − w_C = (0, 0, 2v_D)`. This is rank 2 in characteristic 2, where the functional
would give `L ≤ 4`, but generically rank 3 in characteristic 0, where `L = 6 > 4`. So the obstruction
to certifying 16 is characteristic-dependent. The combinatorial atom bound cannot see that
difference.

## A border decomposition at mass 14 over ℝ

The LP's fractional covering suggested the patterns. `lowreal.py` searches small multisets of those
patterns plus free atoms with alternating least squares. The best mass-14 multiset is
`AC×AC, AD×AD, 2·BD×BD, BCD×ACD, AB×CD` plus two of each free atom. `border.py` tracks it:

| ALS iteration | `‖Σ u vᵀ − I‖` | `max ‖u‖‖v‖` |
| --- | --- | --- |
| 100 | 2.44e-1 | 2.5e3 |
| 1,000 | 7.41e-2 | 2.9e5 |
| 3,000 | 4.26e-2 | 2.7e6 |
| 10,000 | 2.33e-2 | 3.0e7 |
| 20,000 | 1.65e-2 | 1.2e8 |

The residual tends to 0 only as the coefficients diverge. That is the signature of a border
decomposition (border rank), not an exact one. No exact decomposition below 16 was found. An exact
`F₂` ILP, over 65,025 atoms with mass at most 15, timed out at 1,500 s.

## Reading

Over ℝ and ℂ, mass 14 is approached but apparently not attained. A finite-precision decoder cannot
use diverging coefficients, so this is consistent with the open floor being 16, and it explains why
the zeroed-block LP falls below 16. Proving 16 needs a characteristic-0 argument that uses
cancellation, for example the closedness of the set of exact mass-14 decompositions.
