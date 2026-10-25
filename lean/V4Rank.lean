import Mathlib

/-!
# V4: every plane-port decoder costs at least 2 × (number of ports)

Setting (over any field `F`).  Each port `p : ι` carries the two label vectors `L p 0, L p 1 : d → F` of its plane.
A decoder is `M = ∑ₖ uₖ vₖᵀ` (`u v : K → ι → F`).  The term `k` is priced by `rank ((A k)ᵀ * B k)`, where the columns of
`A k` (resp. `B k`) span a subspace containing the labels of every port in the support of `uₖ` (resp. `vₖ`); with bases
this is exactly the rank of the dot-product pairing between the source-plane span and the reader-plane span (the tariff).

`lift L u` is the `d × (2 × ι)` matrix whose column `(a, p)` is `u p • L p a`.  Hypotheses `hA`, `hB` say these columns lie
in the spans of `A k`, `B k`.  The mask is used only through `hdiag` (`M p p = 1`) and `hoff` (for `p ≠ q`, `M p q` vanishes
or the two planes are orthogonal), and every plane has an invertible 2 × 2 Gram matrix (`hgram`).

Conclusion: `2 * |ι| ≤ ∑ₖ tariffₖ`.  Proof: `∑ₖ (lift uₖ)ᵀ (lift vₖ)` is block diagonal with the invertible plane Grams,
so it has rank `2|ι|`; rank is subadditive; and each summand has rank at most its tariff.
-/

open Matrix Finset

set_option linter.unusedSectionVars false

namespace V4

variable {F : Type*} [Field F] {ι d K : Type*} [Fintype ι] [DecidableEq ι] [Fintype d] [DecidableEq d] [Fintype K]

/-- column `(a, p)` is `u p • L p a` -/
def lift (L : ι → Fin 2 → d → F) (u : ι → F) : Matrix d (Fin 2 × ι) F := fun i ab => u ab.2 * L ab.2 ab.1 i

/-- the rank of one term is at most its tariff -/
theorem rank_term_le {m : Type*} [Fintype m] (X Y : Matrix d (Fin 2 × ι) F) (A B : Matrix d m F)
    (hX : ∃ C : Matrix m (Fin 2 × ι) F, X = A * C) (hY : ∃ C : Matrix m (Fin 2 × ι) F, Y = B * C) :
    (Xᵀ * Y).rank ≤ (Aᵀ * B).rank := by
  obtain ⟨C, rfl⟩ := hX
  obtain ⟨C', rfl⟩ := hY
  have h : (A * C)ᵀ * (B * C') = Cᵀ * ((Aᵀ * B) * C') := by
    simp only [transpose_mul, Matrix.mul_assoc]
  rw [h]
  exact (rank_mul_le_right _ _).trans (rank_mul_le_left _ _)

/-- rank of a sum of two matrices -/
theorem rank_add_le' {m n : Type*} [Fintype m] [Fintype n] (A B : Matrix m n F) :
    (A + B).rank ≤ A.rank + B.rank := by
  unfold Matrix.rank
  rw [Matrix.mulVecLin_add]
  have h : LinearMap.range (A.mulVecLin + B.mulVecLin)
      ≤ LinearMap.range A.mulVecLin ⊔ LinearMap.range B.mulVecLin := by
    intro y hy
    obtain ⟨x, rfl⟩ := LinearMap.mem_range.mp hy
    rw [LinearMap.add_apply]
    exact Submodule.add_mem_sup (LinearMap.mem_range_self _ x) (LinearMap.mem_range_self _ x)
  exact (Submodule.finrank_mono h).trans (Submodule.finrank_add_le_finrank_add_finrank _ _)

/-- rank is subadditive over finite sums -/
theorem rank_sum_le {m n : Type*} [Fintype m] [Fintype n] (s : Finset K) (f : K → Matrix m n F) :
    (∑ k ∈ s, f k).rank ≤ ∑ k ∈ s, (f k).rank := by
  classical
  refine Finset.induction_on s ?_ ?_
  · simp
  · intro a s ha ih
    rw [Finset.sum_insert ha, Finset.sum_insert ha]
    exact (rank_add_le' _ _).trans (Nat.add_le_add_left ih _)

/-- the sum of the lifted terms, entrywise -/
theorem sum_lift (L : ι → Fin 2 → d → F) (u v : K → ι → F) (a b : Fin 2) (p q : ι) :
    (∑ k, (lift L (u k))ᵀ * lift L (v k)) (a, p) (b, q)
      = (∑ k, u k p * v k q) * (∑ i, L p a i * L q b i) := by
  rw [Matrix.sum_apply, Finset.sum_mul]
  apply Finset.sum_congr rfl
  intro k _
  simp only [mul_apply, transpose_apply, lift, Finset.mul_sum]
  apply Finset.sum_congr rfl
  intro i _
  ring

/-- **Main theorem.** Every decoder whose mask kills all non-orthogonal off-diagonal pairs and keeps the diagonal costs
at least `2 * |ι|`. -/
theorem decoder_cost_ge (L : ι → Fin 2 → d → F) (u v : K → ι → F) {m : Type*} [Fintype m]
    (A B : K → Matrix d m F)
    (hA : ∀ k, ∃ C : Matrix m (Fin 2 × ι) F, lift L (u k) = A k * C)
    (hB : ∀ k, ∃ C : Matrix m (Fin 2 × ι) F, lift L (v k) = B k * C)
    (hdiag : ∀ p, ∑ k, u k p * v k p = 1)
    (hoff : ∀ p q, p ≠ q → ∀ a b, (∑ k, u k p * v k q) * (∑ i, L p a i * L q b i) = 0)
    (hgram : ∀ p, IsUnit (Matrix.of fun a b : Fin 2 => ∑ i, L p a i * L p b i)) :
    2 * Fintype.card ι ≤ ∑ k, ((A k)ᵀ * B k).rank := by
  classical
  set G : ι → Matrix (Fin 2) (Fin 2) F := fun p => Matrix.of fun a b => ∑ i, L p a i * L p b i with hG
  have hD : (∑ k, (lift L (u k))ᵀ * lift L (v k)) = blockDiagonal G := by
    ext ⟨a, p⟩ ⟨b, q⟩
    rw [sum_lift]
    by_cases hpq : p = q
    · subst hpq
      rw [blockDiagonal_apply_eq, hdiag, one_mul]
      simp [hG]
    · rw [blockDiagonal_apply_ne G a b hpq]
      exact hoff p q hpq a b
  have hunit : IsUnit (blockDiagonal G) := by
    rw [Matrix.isUnit_iff_isUnit_det, det_blockDiagonal]
    exact IsUnit.prod_univ_iff.mpr fun p => (Matrix.isUnit_iff_isUnit_det _).mp (hgram p)
  have hrank : (blockDiagonal G).rank = 2 * Fintype.card ι := by
    rw [rank_of_isUnit _ hunit, Fintype.card_prod, Fintype.card_fin]
  calc 2 * Fintype.card ι = (∑ k, (lift L (u k))ᵀ * lift L (v k)).rank := by rw [hD, hrank]
    _ ≤ ∑ k, ((lift L (u k))ᵀ * lift L (v k)).rank := rank_sum_le _ _
    _ ≤ ∑ k, ((A k)ᵀ * B k).rank :=
        Finset.sum_le_sum fun k _ => rank_term_le _ _ _ _ (hA k) (hB k)

end V4

#print axioms V4.rank_add_le'
#print axioms V4.rank_term_le
#print axioms V4.rank_sum_le
#print axioms V4.sum_lift
#print axioms V4.decoder_cost_ge
