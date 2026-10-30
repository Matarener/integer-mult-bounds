# Proof: hand proofs of RootFact and SpanFact, and Cases II/III of the B-form floor without the census

Notation and setting are those of research/p104-bform-nine-term-floor (PR6188, PROOF.md there): P104 = #968's unit,
ports `t` with roots `r_t` and labels `l_t ∈ F₂⁹`, `N(x)` = ports non-orthogonal to `x`, B-form
`M = D₁ G D₂ + c βᵀ` of rank 9, `A = supp c`, `B = supp β`, decoder `M = Σ_{j ≤ 9} p_j q_jᵀ`,
cost `Σ_j rank_F₂ B[R_j, A_j]`. Characteristic 0 throughout.

## 1. RootFact by hand (PROVEN; Lean theorem)
Statement (`BForm.RootFact`): every `x ≠ 0` is non-orthogonal to at least 49 ports. Full proof:
[hand/HAND-ROOTFACT.md](hand/HAND-ROOTFACT.md); finite facts (A)-(E) by `hand/check_hand_rootfact.py` (< 1 s).
Idea: move `x` into the dominant chamber by simple reflections; there the roots orthogonal to `x` form a parabolic
subsystem; by the table of maximal parabolics only E7 holds more than 42 lines, and the E7 case (`x` a multiple of a
root) gives `57 − 8 = 49` because a root meets each removed frame in 4 lines (or 1 if it lies in it).

## 2. SpanFact by hand (PROVEN; Lean theorem)
Statement (`BForm.SpanFact`, the corrected span lemma of PR6188 with the port exception). Full proof:
[hand/HAND-SPANFACT.md](hand/HAND-SPANFACT.md); finite facts by `hand/check_hand_spanfact.py` (about 1 min).
Idea: the labels are E8 modulo 2 (`u_r = l_r + 1` runs over the 120 vectors of `Q = 1` in the even-weight space,
orthogonality is `B(u, u') = 0`); for `S = O(z) ∩ N(y)` with `1 ≤ |S| ≤ 4` Gauss sums over the parabolic cases
(general `|S| ≥ 7`, E7 `|S| ≥ 16` unless `z = l_r`, D7 `|S| ≥ 10`) leave only `z = l_w`, `w ∈ S`.

## 3. Lean (PROVEN, `lean/`)
`BForm.E8h.rootFact_h : BForm.RootFact (rK K)` and `BForm.E8h.spanFact_h : BForm.SpanFact labK (rK K)` follow the
hand proofs: induction on the number of positive roots with negative inner product (each simple reflection permutes
the other positive roots), a kernel-checked table of the 2⁸ parabolic subsystems (`cnt`, `paraP`), explicit E7 and
D7 linear-combination certificates (`Cert.lean`), and reduction from `K` to `ℚ` (`rootQ`, `reduceExact`). SpanFact
uses 104-bit masks of the odd ports `O(l)` (`atLeast5` clears the highest bit four times; `hb` is a binary search
proved equal to `Nat.log2`). All finite checks are `decide +kernel` on small lists, split into eight chunks.
`BForm.E8h.bform_floor_P104_h` is `BForm.bform_floor` of PR6188 with both hypotheses discharged; the remaining
hypotheses are `Capacity`, `BicliqueFact` and `CensusFact`. `#print axioms`: `propext`, `Classical.choice`,
`Quot.sound` for all three theorems. The files `BForm/{CaseI,CaseII,Cost,MJ,Main,NormalForm,Rank,YZero}.lean` are
byte-identical copies of PR6188's (checked by `verify.py`), so this project builds on its own.

## 4. Cases II/III without the census (PROVEN from Lemma P; Lemma P CHECKED)
Case II: `|B| ≤ 4`, any `D` (singular allowed). Case III (`|A| ≤ 4`) is Case II for `Mᵀ` (PR6188). Case I is
unchanged. Inputs, all proved in PR6188 (§3 Case II steps 1, 2, 3, 5 there):
- (F) a free term (`B[R_j, A_j] = 0`) leaves `≤ 8` paid terms: cost `≥ 56` (#2338).
- (Y) a term with `y_j = 0` gives cost `≥ 56` (Lean `yzero`). Otherwise `|A_j| ≥ |N(y_j) \ B| ≥ 45 > 36 = f(7)`,
  so the column label span `U_A(j)` has codimension `≤ 1`.
- (M) for terms `i ≠ j` and the rows `T` dead for both (every port outside `R_i ∪ R_j`):
  `rank{r_t : t ∈ T \ Z_r} ≤ 7`, where `Z_r = {α = 0}` is pairwise non-orthogonal with `≤ 4` ports (empty if `D`
  is invertible). So the ports outside `R_i ∪ R_j`, except at most 4 pairwise non-orthogonal ones, lie in a
  hyperplane.
- (H) a hyperplane holds `≤ 55` ports (RootFact, §1).

**Step 1 (accounting).** `U_j = span l(R_j)`, `d_j = 9 − dim U_j` (`R_j ≠ ∅` for paid terms, so `d_j ≤ 8`). By the
rank formula `r_j = dim U_j − dim(U_j ∩ U_A(j)^⊥) ≥ dim U_j − 1 = 8 − d_j` (by (Y)). With `σ'_j = 7 − r_j`:
`σ'_j ≤ d_j − 1`, `σ'_j ≤ 6`, and cost `≤ 55` iff `Σ_j σ'_j ≥ 8`. Terms with `d_j ≤ 1` have `σ'_j ≤ 0`; call the
others big. A single big gives `Σ σ' ≤ 6`, so a decoder of cost `≤ 55` has at least 2 bigs.

**Step 2 (label counting).** `f(k)` = max number of port labels in a `k`-dimensional subspace of `F₂⁹`:
`f(1..8) = 1, 2, 4, 8, 12, 20, 36, 60` (`checks/fk.py` exhaustive over spans for `k ≤ 4`; `checks/f56.py` over all
788035 three-dimensional `Z` for `k = 5, 6`; `f(7)`, `f(8)` as in PR6188 S0). Since the labels of `R_j` lie in
`U_j`, `|R_j| ≤ f(9 − d_j)`. By (M) and (H), two bigs have `|R_i ∪ R_j| ≥ 104 − 55 − 4 = 45`. As `20 + 20 < 45` and
`36 + 8 < 45`, among `≥ 2` bigs at most one has `d ≥ 3`, and it has `d ≤ 4`. So `k ≥ 2` bigs give
`Σ σ' ≤ 3 + (k − 1)`, and cost `≤ 55` needs `k ≥ 6` bigs.

**Step 3 (planes).** For a 2-dimensional subspace `Z ⊂ F₂⁹` let `L(Z)` = ports whose label is orthogonal to `Z`
(`|L(Z)| ≤ 36`). Call `Z, Z'` *compatible* if the ports outside `L(Z) ∪ L(Z')`, except at most 4 pairwise
non-orthogonal ones, lie in a hyperplane of ℝ⁸. For each big pick a plane `Z_j ⊂ U_j^⊥` (`dim U_j^⊥ = d_j ≥ 2`).
Then `R_j ⊆ L(Z_j)`, so by (M) the planes of two bigs are compatible (a larger `R_j` only weakens the condition, and
the exceptions are ports of `Z_r`). They are distinct, since `Z_i = Z_j` would give `|R_i ∪ R_j| ≤ 36 < 45`.

**Lemma P (CHECKED, `checks/planes.py`, `checks/cliq.py`).** Among the 43435 planes there are exactly 15240
compatible pairs. Every plane is compatible with at most two others, and no 4 planes are pairwise compatible
(maximal families: 11880 of size 2, 1120 of size 3). Every compatible pair has disjoint live sets with
`|L ∪ L'| ∈ {48, 52}`, and its hyperplane is `r_y^⊥` for a root `y` (E7 type).
Method: the ports outside `L ∪ L'` minus the exceptions number `≥ 104 − 72 − 4 = 28`, so they lie in a root
hyperplane with `≥ 28` lines. Every root hyperplane is `W(E8)`-conjugate to some `ω_i^⊥` (the dominant-chamber step
of §1), of type D7, A7, A1A6, A1A2A4, A3A4, A2D5, A1E6, E7 with 42, 28, 22, 14, 16, 23, 37, 63 lines; only D7, A7,
A1E6, E7 reach 28, with normals of norm 4, 8, 6, 2. The flat list of PR6188 `checks/lbz.py` takes every E8 vector of
norm `≤ 8` as a normal, so it contains them all. For each such flat, every plane covering enough of its complement,
then every pair, with the exact `≤ 4` pairwise non-orthogonal exception test.

**Conclusion.** By Lemma P at most 3 bigs, so `Σ σ' ≤ 3 + 2 = 5 < 8`: **every Case II/III decoder costs `≥ 56`,
for invertible and singular `D`.** With Case I: every nine-term decoder of a rank-9 B-form realisation of P104 costs
`≥ 56`, without the repo census (cnt9b), the propagation bound `lb`, survivor and port classes, the clique and
support filters, or the M_J bound for `|J| ≥ 3`. The margin is large: only "no 6 pairwise compatible planes" is
used. With "compatible planes have disjoint live sets" alone, `k` pairwise compatible bigs have disjoint `R_j` with
pairwise sums `≥ 45`, so at most one `|R_j| ≤ 22`, and `9 + 23(k − 1) ≤ 104` gives `k ≤ 5`.

**Why Lemma P is not proved by hand here** (`checks/rootcase.py`, `checks/maxu.py`). Flats with `≤ 33` ports are
excluded by counting (the largest `|L ∪ L'|` over all plane pairs is 66 `< 104 − 33 − 4`), but the root-normal case
has no slack: there are plane pairs with only 3 or 4 uncovered ports of `N(y)` (see `evidence/rootcase.txt`), which
are excluded only because those ports are not pairwise non-orthogonal. A hand proof must track exact uncovered sets.

## 5. Dependencies and limits
- CITED: PR6188 (normal form, Case I, (F), (Y), (M), coverage S3, Lean `bform_floor`), #2338 ("`≤ 8` paid terms ⇒
  `≥ 56`"), research/nine-term-outside-colspace (rank formula; label classes and port data through `setup9.py`).
- Not formalised: Step 1-3 of §4 and Lemma P (so `CensusFact` stays a hypothesis in Lean); `Capacity`, `BicliqueFact`.
- Not covered (unchanged): rank-9 realisations of P104 that are neither B-form nor A2; `≥ 10` terms; P112 and E8.
