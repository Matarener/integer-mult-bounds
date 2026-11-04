import RankNine.T1Stage3

set_option linter.unusedSectionVars false

/-!
# T2 for one frameless representative (hand route, SCHEME.md §3 "T2 (pair step)", NOTE §13.21–§13.24, §13.28)

The dead set `c` of a row-big term with witness `u` is frameless.  The stage-3 machinery (`St3`, with type mask
`m0 = c` and target `zm ⊇ c`) gives Gram on `c × c` in every branch (supports of `u` included).  A second
independent witness `v` with dead set `c'` kills the rows of `c ∩ c'` for both `u` and `v`, so every `8 × 8` minor
on them vanishes (`pair_minor`); a pair certificate (8 lines `X ⊆ zm ∩ c ∩ c'`, 8 lines `Y ⊆ zm`, and the adjugate of
the integer matrix `dot X Y`) gives a Gram block with non-zero minor (`pair_false`).  Contradiction.

The pair certificates replace, for now, the hand proof of §13.28 (root rank 8 of `C ∩ C'`), by Mark's decision
(04.11 17:46Z): a table checked by `#eval`, the hand proof to be formalised later.
-/

namespace RankNine.T2

open Matrix RankNine

variable {K : Type*} [Field K] [CharZero K]

/-- a pair certificate on the Gram set `zm` of `c` for the partner `c'` -/
def pcOK2 (zm c c' : ℕ) (Y X : List ℕ) (J : List (List ℤ)) (dd : ℤ) : Bool :=
  decide (X.length = 8) && decide (Y.length = 8) &&
  X.all (fun x => decide (x < 104) && zm.testBit x && c.testBit x && c'.testBit x) &&
  Y.all (fun y => decide (y < 104) && zm.testBit y) &&
  dd != 0 && decide (dotM X Y * jM J = dd • (1 : Matrix (Fin 8) (Fin 8) ℤ))

/-- **Pair step.**  Gram on `zm`, rows of `c` dead for `u`, rows of `c'` dead for `v`, `u, v` independent, and a pair
certificate: contradiction. -/
theorem pair_false (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0) (u v : Fin 9 → K)
    (huv : LinearIndependent K ![u, v]) (g : ℕ → K) (hg : ∀ x, g x ≠ 0) (zm c c' : ℕ)
    (hG : ∀ x < 104, ∀ y < 104, zm.testBit x = true → zm.testBit y = true → GramP A B g x y)
    (hu : ∀ x, c.testBit x = true → A x ⬝ᵥ u = 0) (hv : ∀ x, c'.testBit x = true → A x ⬝ᵥ v = 0)
    (Y X : List ℕ) (J : List (List ℤ)) (dd : ℤ) (h : pcOK2 zm c c' Y X J dd = true) : False := by
  classical
  unfold pcOK2 at h
  simp only [Bool.and_eq_true, decide_eq_true_eq, bne_iff_ne, ne_eq, List.all_eq_true] at h
  obtain ⟨⟨⟨⟨⟨hXl, hYl⟩, hX⟩, hY⟩, hdd⟩, hDJ⟩ := h
  have hXi : ∀ i : Fin 8, X.getD i 0 < 104 ∧ zm.testBit (X.getD i 0) = true ∧ c.testBit (X.getD i 0) = true ∧
      c'.testBit (X.getD i 0) = true := fun i => by
    have := hX _ (getD_mem8 hXl i)
    try simp only [Bool.and_eq_true, decide_eq_true_eq] at this
    exact ⟨this.1.1.1, this.1.1.2, this.1.2, this.2⟩
  have hYi : ∀ k : Fin 8, Y.getD k 0 < 104 ∧ zm.testBit (Y.getD k 0) = true := fun k => by
    have := hY _ (getD_mem8 hYl k)
    try simp only [Bool.and_eq_true, decide_eq_true_eq] at this
    exact this
  refine pair_minor A B u v huv (fun i => X.getD i 0) (fun k => Y.getD k 0)
    (fun i => hu _ (hXi i).2.2.1) (fun i => hv _ (hXi i).2.2.2)
    (fun x => if dS A B g x = 0 then 1 else 18 / dS A B g x) (fun y => (g y)⁻¹) ?_
    (fun y => inv_ne_zero (hg y)) (dotM X Y) (det_of_adj _ _ dd hdd hDJ) ?_
  · intro x
    split_ifs with h
    · exact one_ne_zero
    · exact div_ne_zero (by norm_num) h
  · intro i k
    have hdx : dS A B g (X.getD i 0) ≠ 0 := div_ne_zero (hdiag _ (hXi i).1) (hg _)
    have hGik := hG _ (hXi i).1 _ (hYi k).1 (hXi i).2.1 (hYi k).2
    unfold GramP gam at hGik
    rw [if_neg hdx, hGik]
    simp only [dotM, Matrix.of_apply]
    have hgk := hg (Y.getD k 0)
    first | (field_simp; done) | (field_simp; ring)

/-- the T2 record of one frameless representative: its stage-3 record and one pair certificate per partner
(`(c', X, J, dd)`, with a fixed `Y`) -/
structure T2R where
  st : St3
  Y : List ℕ
  P : List (ℕ × List ℕ × List (List ℤ) × ℤ)

/-- **the check of a T2 record** for the frameless set `c` and the partner list `FL` -/
def T2R.ok (r : T2R) (c : ℕ) (FL : List ℕ) : Bool :=
  r.st.ok && r.st.m0 == c &&
  FL.all fun c' => r.P.any fun p => p.1 == c' && pcOK2 r.st.zm c c' r.Y p.2.1 p.2.2.1 p.2.2.2

/-- **T2 for one frameless representative**: two independent witnesses with dead sets `c` (the representative) and
`c' ∈ FL` do not exist. -/
theorem T2R.sound (r : T2R) (c : ℕ) (FL : List ℕ) (h : r.ok c FL = true) (A B : ℕ → Fin 9 → K)
    (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0) (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (u v : Fin 9 → K) (huv : LinearIndependent K ![u, v]) (c' : ℕ) (hc' : c' ∈ FL)
    (hu : ∀ x, c.testBit x = true → A x ⬝ᵥ u = 0) (hv : ∀ x, c'.testBit x = true → A x ⬝ᵥ v = 0) : False := by
  unfold T2R.ok at h
  simp only [Bool.and_eq_true, beq_iff_eq, List.all_eq_true, List.any_eq_true] at h
  obtain ⟨⟨hst, hm⟩, hP⟩ := h
  have hu0 : u ≠ 0 := fun h0 => by
    have := huv.ne_zero 0
    simp [h0] at this
  obtain ⟨g, hg, hG⟩ := r.st.sound hst A B hdiag hmask u hu0 (by rw [hm]; exact hu)
  obtain ⟨p, -, -, hp⟩ := hP c' hc'
  exact pair_false A B hdiag u v huv g hg r.st.zm c c' hG hu hv r.Y _ _ _ hp

end RankNine.T2
