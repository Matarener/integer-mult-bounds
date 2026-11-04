import RankNine.T2Minor
import BForm.Rank

/-!
# T2 pair step

Rows `X` (8 lines) dead for two independent directions `u, v` and 8 columns `Y` on which `M = D₁ G D₂` with an
integer block `G[X,Y]` of non-zero determinant cannot exist: the rows `A(X i)` would be 8 independent vectors
(`rows_indep_of_det`) in the 7-dimensional `{u, v}^⊥` (`rank_add_rank_le_of_mul_eq_zero`).
-/

namespace RankNine.T2

open Matrix RankNine

variable {K : Type*} [Field K] [CharZero K]

set_option linter.unusedSectionVars false

theorem rank_rows_indep {m : Type*} [Fintype m] (A8 : Matrix m (Fin 9) K) (h : LinearIndependent K fun i => A8 i) :
    A8.rank = Fintype.card m := by
  rw [Matrix.rank_eq_finrank_span_row]
  exact finrank_span_eq_card h

theorem rank_two_cols (u v : Fin 9 → K) (h : LinearIndependent K ![u, v]) :
    (Matrix.of fun (r : Fin 9) (c : Fin 2) => ![u, v] c r).rank = 2 := by
  rw [Matrix.rank_eq_finrank_span_cols]
  exact (finrank_span_eq_card (show LinearIndependent K (Matrix.of fun (r : Fin 9) (c : Fin 2) => ![u, v] c r).col
    from h)).trans (Fintype.card_fin 2)

/-- **Pair step.** -/
theorem pair_minor (A B : ℕ → Fin 9 → K) (u v : Fin 9 → K) (huv : LinearIndependent K ![u, v])
    (X Y : Fin 8 → ℕ) (hXu : ∀ i, A (X i) ⬝ᵥ u = 0) (hXv : ∀ i, A (X i) ⬝ᵥ v = 0)
    (p q : ℕ → K) (hp : ∀ x, p x ≠ 0) (hq : ∀ y, q y ≠ 0) (D : Matrix (Fin 8) (Fin 8) ℤ)
    (hD : D.det ≠ 0) (hM : ∀ i k, Mx A B (X i) (Y k) = (D i k : K) / (p (X i) * q (Y k))) : False := by
  have hG : (D.map (Int.castRingHom K)).det ≠ 0 := by
    rw [← RingHom.mapMatrix_apply, ← RingHom.map_det]; simpa using hD
  have hdet : (Matrix.of fun i k => A (X i) ⬝ᵥ B (Y k)).det ≠ 0 := by
    have e : (Matrix.of fun i k => A (X i) ⬝ᵥ B (Y k)) =
        Matrix.of fun i k => (p (X i))⁻¹ * (D.map (Int.castRingHom K)) i k * (q (Y k))⁻¹ := by
      ext i k
      simp only [Matrix.of_apply, Matrix.map_apply, eq_intCast]
      rw [show A (X i) ⬝ᵥ B (Y k) = Mx A B (X i) (Y k) from rfl, hM]
      first | ring | (field_simp; done) | (field_simp; ring)
    rw [e]
    exact det_scaled_ne _ _ _ (fun i => inv_ne_zero (hp _)) (fun k => inv_ne_zero (hq _)) hG
  have hind := rows_indep_of_det A B X Y hdet
  let A8 : Matrix (Fin 8) (Fin 9) K := Matrix.of fun i => A (X i)
  let UV : Matrix (Fin 9) (Fin 2) K := Matrix.of fun r c => ![u, v] c r
  have h0 : A8 * UV = 0 := by
    ext i c
    fin_cases c
    · simpa [A8, UV, Matrix.mul_apply, dotProduct] using hXu i
    · simpa [A8, UV, Matrix.mul_apply, dotProduct] using hXv i
  have h1 := BForm.rank_add_rank_le_of_mul_eq_zero A8 UV h0
  rw [rank_rows_indep A8 hind, rank_two_cols u v huv] at h1
  simp at h1

end RankNine.T2
