# Proof: nine-term decoders of B-form realisations of P104 cost at least 56

Labels: **PROVEN** (argument here; the parts marked [Lean] are also machine-checked in `lean/`, theorem
`BForm.bform_floor`), **CHECKED** (finite computation re-run by `verify.py`), **RECORDED** (Kaggle run, log
shipped, hash pinned in RESULT.json, numbers re-read by `verify.py`), **CITED** (another package or PR).

## 0. Setting

`K` a field of characteristic 0. `P104` = #968's unit (E8 minus the orthogonal frames `F0`, `F1`, 104 lines), roots
`r_t`, Gram `G`, labels `l_t ∈ F₂⁹` with the dense table `B_ts = l_t ⬝ l_s` (`= 1` iff `t = s` or `t ⊥ s`).
Pattern: `M_tt ≠ 0`, `M_ts = 0` for `t ⊥ s`. **B-form** (e8-rank9-realisations, #2819): `M = D₁ G D₂ + c βᵀ`,
`D_i` diagonal, `c_u β_s = 0` whenever `u ⊥ s`, rank `M = 9`; `A = supp c`, `B = supp β`, `α = diag D₁`,
`α' = diag D₂`. Then `A × B` is pairwise non-orthogonal and `M_tt = 2 α_t α'_t + c_t β_t`, so `α_t α'_t ≠ 0` off
`A ∩ B`; "singular D" means `α_t α'_t = 0` somewhere on `A ∩ B` (allowed throughout).
Decoder: `M = Σ_{j ≤ 9} p_j q_jᵀ`, cost `Σ_j rank_F₂ B[R_j, A_j]` with `R_j = supp p_j`, `A_j = supp q_j`.
`N(x) = {t : ⟨r_t, x⟩ ≠ 0}`.

## 1. Finite facts (CHECKED, `checks/spanlemma.py`, `checks/bicliques.py`)
- **S0** `f(7) = 36`, `f(8) = 60`: a 7-dim (8-dim) label subspace holds at most 36 (60) ports. So `≥ 37` ports
  have label span `≥ 8`.
- **S1** E7 hyperplanes hold 63 E8 lines, D7 hyperplanes 42, every other root hyperplane `≤ 37` (maximal
  parabolics of E8); E7/D7 hyperplanes hold `≤ 55` ports, so `|N(x)| ≥ 49` for every `x ≠ 0`.
- **S2'** For every label `z ≠ 0` and E7/D7 hyperplane `H`, `|O(z) \ H|` is 0 or `≥ 5`, except exactly the 104 pairs
  `z = l_p`, `H = r_p^⊥`, where `O(z) \ H = {p}` (`O(z) = {t : l_t ⬝ z = 1}`).
- **S3** A pairwise non-orthogonal rectangle `A × B` with `|A| ≥ 13` has `|B| ≤ 4` (closed bicliques).

## 2. Algebra (PROVEN [Lean])
- **Rank formula.** `B[R, S] = L_R L_Sᵀ`, so `rank B[R,S] ≥ dim span l(R) + dim span l(S) − 9` (Sylvester).
- **Normal form.** `X = [c, D₁R]`, `Y = [β, D₂R]` have rank 9 (left inverses) and `M = X Yᵀ`. With
  `U = X⁺P`, `W = Y⁺Q`: `P = X U`, `Q = Y W`, `U Wᵀ = 1`. Write column `j` of `U` as `(a_j, x_j)`, of `W` as
  `(b_j, y_j)`: `p_j(t) = c_t a_j + α_t ⟨r_t, x_j⟩`, `q_j(s) = β_s b_j + α'_s ⟨r_s, y_j⟩`, `Σ_j x_j y_jᵀ = I₈`,
  `Σ_j a_j y_j = 0`, `Σ_j x_j b_j = 0`, `Σ_j a_j b_j = 1`.
- **M_J bound.** If the rows `T` are dead for every term of `J`, then `rank X[T, :] ≤ 9 − |J|` (`U` invertible).
- **Span lemma** (from S0, S1, S2'). For `y ≠ 0` and `|S| ≤ 4`: `span l(N(y) \ S) = span l(N(y))`, unless `y ∥ r_p`
  for a port `p ∈ S`; then `N(y) ∩ O(l_p) = {p}` and removing `p` drops the span to `l_p^⊥`.

## 3. The three cases
**Case I** (`|A|, |B| ≤ 12`) [Lean `caseI`]. At least 8 terms have `x_j ≠ 0 ≠ y_j` (rank of `I₈`). For them
`R_j ⊇ N(x_j) \ A`, `A_j ⊇ N(y_j) \ B`, both `≥ 49 − 12 = 37` ports, so both spans `≥ 8` and each costs `≥ 7`.
Singular `D` is irrelevant here.

**Case II** (`|B| ≤ 4`, any `D`) [Lean `caseII`, with `CensusFact`].
1. *A term with `y_{j₀} = 0`* [Lean `yzero`]. The other eight `y_j` form a basis dual to the `x_j`;
   `Σ a_j y_j = 0` gives `a_j = 0` for `j ≠ j₀`, so `R_j ⊇ N(x_j) \ Z_r` with `Z_r = {α = 0} ⊆ B` (`≤ 4` ports),
   and `A_j ⊇ N(y_j) \ B`. Both `≥ 45`: eight terms of cost `≥ 7`. (The `b_j` need not vanish.)
2. Otherwise every `y_j ≠ 0`, so `|A_j| ≥ 45`, `δ_A(j) := 9 − dim span l(A_j) ≤ 1`.
3. *Rows.* For `t ∉ Z_r`, `X[t, :]` restricted to the root part is `α_t r_t` with `α_t ≠ 0`; on `Z_r` it is 0.
   `Z_r ⊆ A ∩ B` is pairwise non-orthogonal and has `≤ 4` ports. So for every `J` and every set `T` of rows dead for
   `J`: `rank{r_t : t ∈ T \ Z_r} + |J| ≤ 9`. The census uses
   `lbz(X) = min over non-orthogonal S ⊆ X, |S| ≤ 4, of rank(roots of X \ S)` (for invertible `D` also the repo's
   propagation bound `lb`, valid because `D₁GD₂` is then a rank-8 realisation of the pattern).
4. *Columns.* Off `B`, `q_j(s) = α'_s ⟨r_s, y_j⟩` with `α'_s ≠ 0`, so `A_j ⊇ N(y_j) \ B`. If `δ_A(j) = 1` at class `z`,
   the span lemma gives either `N(y_j) ⊆ l-class z^⊥`, i.e. `y_j` is orthogonal to every root of `O(z)`, so
   `rank roots(O(z)) ≤ 7` and `z` is a survivor (the repo's survivor set, `lb < 8`, contains these), or
   `z = l_p` for a port `p` ("port class").
5. *Free terms* (`B[R_j, A_j] = 0`) are deleted, leaving `≤ 8` paid terms of an exact masked decoder: `≥ 56` by
   #2338 (CITED). So all terms are paid and the repo's accounting applies: `σ'_j = 7 − r_j = d_j − 2 + τ_j`,
   cost `≤ 55` iff `Σ σ' ≥ 8`, and the support filter (D) and the clique filter (C) hold for `M`.
6. *Census* (RECORDED). The repo's P104 multi-big census (`cnt9b.py` of research/nine-term-outside-colspace)
   with the column τ-classes extended by the 104 port classes and survivors allowed to repeat
   (`checks/cnt9c.py` V1-V3; V0 = unchanged control, 701 configurations, 0 alive, equal to the repo log), and for
   singular `D` the same census with `lb` replaced by `lbz` and the pair table recomputed with `lbz`
   (`checks/cnt104z.py`: 415 pairs; `checks/cnt9z.py` V3: union with the repo table 740 pairs, 446 configurations).
   **Every variant: 0 configurations reach `Σ σ' ≥ 8`, 0 alive.**

**Case III** (`|A| ≤ 4`): the transpose of Case II (`Mᵀ = Y Xᵀ`, decoder `(Q, P)`, the pattern and the cost are
transpose-invariant) [Lean `caseIII`].

**Coverage.** If `|A|, |B| ≤ 12`: Case I. If `|A| ≥ 13`: `|B| ≤ 4` by S3, Case II. If `|B| ≥ 13`: `|A| ≤ 4`, Case III.

## 4. lbz is computed exactly enough (CHECKED, `checks/lbz.py`)
For `|X| ≥ 28` a flat `V` with `|X \ V| ≤ 4` holds `≥ 24` ports; such flats are the rank-7 flats of type E7, D7,
E6A1, A7 (normals: E8 vectors of norm 2, 4, 6, 8 whose orthogonal roots have rank 7) and the rank-6 flats E6, D6
(complements of A2 and A1A1); all other parabolic flats hold `≤ 23` lines. Smaller `X` are handled exhaustively.
Ranks are taken mod `2^31 − 1` (never above the rational rank: the safe direction). Self-test: every random port
hyperplane with `≥ 24` ports (4150 of 6000 samples) is in the list; fast = exhaustive on 40 random sets.

## 5. Dependencies and limits
- CITED: #2338 (Theorem P, "`≤ 8` paid terms ⇒ `≥ 56`", Theorem R), research/nine-term-outside-colspace (rank
  formula, M_J bound, support/clique filters, census logic; its P104 part is CHECKED there but not independently
  re-implemented), e8-rank9-realisations (the B-form definition; on P104 the classification of rank-9 realisations
  is NOT known, so this is a floor for B-form realisations only).
- Not covered: rank-9 realisations of P104 that are neither B-form nor A2; decoders with `≥ 10` terms; P112 and E8.
