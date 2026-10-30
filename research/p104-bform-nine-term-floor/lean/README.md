# Lean formalisation of the B-form floor (P104, nine terms)

`lake build` (Lean v4.33.0-rc1, Mathlib 55b7917b, same pin as the p104-carrier-code-uniqueness package).
Main theorem `BForm.bform_floor` (BForm/Main.lean); axioms: propext, Classical.choice, Quot.sound. No sorry.

Proved in Lean (any field K):
- Rank.lean: Sylvester's inequality; `A * B = 0 => rank A + rank B <= k`.
- Cost.lean: label blocks `B[R,S] = L_R L_S^T`, `rank B[R,S] >= dim span l(R) + dim span l(S) - 9`, cost.
- NormalForm.lean: `X Y^T = P Q^T`, `X, Y` with left inverses => `P = X U`, `Q = Y W`, `U W^T = 1`.
- MJ.lean: rows dead for the terms `J` span `<= 9 - |J|` dimensions.
- CaseI.lean: `|A|, |B| <= 12` => cost >= 56 (at least 8 terms with both root parts non-zero, each >= 7).
- YZero.lean: a term with zero column root part => the other 8 are pure Gram terms => cost >= 56.
- CaseII.lean: `|B| <= 4`, any D (singular allowed): reduction to `CensusFact` (Zr = {alpha = 0} is a
  non-orthogonal set of <= 4 ports; J-conditions via MJ + exact root rank; column conditions via `SpanFact`).
- Main.lean: Case III by transposition, case split by `BicliqueFact`, theorem `bform_floor`.

Hypotheses (named `Prop`s, each checked by computation, not proved in Lean):
| name | content | checked by |
|---|---|---|
| `Capacity` | S0: >= 37 ports => label span >= 8 (`f(7) = 36`) | spanlemma.py |
| `RootFact` | S1: every x != 0 is non-orthogonal to >= 49 ports | spanlemma.py (E7/D7 hyperplanes hold <= 55 ports) |
| `SpanFact` | BFORM2 span lemma with the port-root exception | S0, S1, S2 (Kaggle p104-bform-floor) + E8 flats |
| `BicliqueFact` | S3: non-orthogonal rectangle with >= 13 rows has <= 4 columns | bicliques.py |
| `CensusFact` | combinatorial census statement on supports | repo case-(b) census + #2338, cnt9c V3, cnt9z V3 |
