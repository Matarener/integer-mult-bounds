import RankNine.T2Zero

/-!
# T2.4: rank argument on rows dead for two terms

Rows dead for two of the nine decoder terms make `M` factor through `K⁷` on those rows, so every 8 × 8 block there is
singular (`det_zero_of_factor`).  On the other hand, an 8 × 8 block of `M` with non-zero determinant makes its 8 rows
independent (`rows_indep_of_det`).  After T2.3 the block is a rescaled Gram block, whose determinant is non-zero by
an integer adjugate certificate (`det_ne_of_adj`).
-/

namespace RankNine.T2

open Matrix RankNine

variable {K : Type*} [Field K]

set_option linter.unusedSectionVars false

/-- an 8 × 8 matrix that factors through `K⁷` (rows dead for two of the nine decoder terms) is singular -/
theorem det_zero_of_factor (M : Matrix (Fin 8) (Fin 8) K) (P : Fin 8 → Fin 7 → K) (Q : Fin 7 → Fin 8 → K)
    (h : ∀ i k, M i k = ∑ l, P i l * Q l k) : M.det = 0 := by
  have hP : ¬ LinearIndependent K P := fun hli => by
    have := hli.fintype_card_le_finrank
    simp only [Fintype.card_fin, Module.finrank_fin_fun] at this
    omega
  obtain ⟨g, hg, i, hi⟩ := Fintype.not_linearIndependent_iff.mp hP
  rw [← Matrix.exists_vecMul_eq_zero_iff]
  refine ⟨g, fun h0 => hi (by rw [h0]; rfl), ?_⟩
  funext k
  show ∑ i, g i * M i k = 0
  have hl : ∀ l, ∑ i, g i * P i l = 0 := fun l => by
    have := congrFun hg l
    simpa [Finset.sum_apply, Pi.smul_apply, smul_eq_mul] using this
  simp_rw [h, Finset.mul_sum]
  rw [Finset.sum_comm]
  refine Finset.sum_eq_zero fun l _ => ?_
  have := hl l
  calc ∑ i, g i * (P i l * Q l k) = (∑ i, g i * P i l) * Q l k := by
        rw [Finset.sum_mul]; exact Finset.sum_congr rfl fun i _ => by ring
    _ = 0 := by rw [this, zero_mul]

/-- an 8 × 8 block of `M = A Bᵀ` with non-zero determinant has independent rows `A x` -/
theorem rows_indep_of_det (A B : ℕ → Fin 9 → K) (X Y : Fin 8 → ℕ)
    (h : (Matrix.of fun i k => A (X i) ⬝ᵥ B (Y k)).det ≠ 0) : LinearIndependent K (fun i => A (X i)) := by
  rw [Fintype.linearIndependent_iff]
  intro c hc i
  by_contra hci
  apply h
  rw [← Matrix.exists_vecMul_eq_zero_iff]
  refine ⟨c, fun h0 => hci (by rw [h0]; rfl), ?_⟩
  funext k
  have h1 : (∑ i, c i • A (X i)) ⬝ᵥ B (Y k) = 0 := by rw [hc, zero_dotProduct]
  rw [sum_dotProduct] at h1
  show ∑ i, c i * (A (X i) ⬝ᵥ B (Y k)) = 0
  simpa [smul_dotProduct, smul_eq_mul] using h1

/-- a rescaled block keeps a non-zero determinant -/
theorem det_scaled_ne (G : Matrix (Fin 8) (Fin 8) K) (a b : Fin 8 → K) (ha : ∀ i, a i ≠ 0) (hb : ∀ k, b k ≠ 0)
    (hG : G.det ≠ 0) : (Matrix.of fun i k => a i * G i k * b k).det ≠ 0 := by
  have e : (Matrix.of fun i k => a i * G i k * b k) =
      Matrix.of fun i k => b k * (Matrix.of fun i k => a i * G i k) i k := by
    ext i k; simp only [Matrix.of_apply]; ring
  rw [e, Matrix.det_mul_row, Matrix.det_mul_column]
  exact mul_ne_zero (Finset.prod_ne_zero_iff.mpr fun k _ => hb k)
    (mul_ne_zero (Finset.prod_ne_zero_iff.mpr fun i _ => ha i) hG)

/-- integer adjugate certificate: `D * J = d • 1` with `d ≠ 0` gives `det D ≠ 0` over any field of char 0 -/
theorem det_ne_of_adj [CharZero K] (D J : Matrix (Fin 8) (Fin 8) ℤ) (d : ℤ) (hd : d ≠ 0)
    (hDJ : D * J = d • (1 : Matrix (Fin 8) (Fin 8) ℤ)) : (D.map (Int.castRingHom K)).det ≠ 0 := by
  have hZ : D.det * J.det = d ^ 8 := by
    rw [← Matrix.det_mul, hDJ, Matrix.det_smul, Matrix.det_one, mul_one, Fintype.card_fin]
  have hD : D.det ≠ 0 := fun h0 => by rw [h0, zero_mul] at hZ; exact pow_ne_zero 8 hd hZ.symm
  rw [← RingHom.mapMatrix_apply, ← RingHom.map_det]
  simpa using hD

end RankNine.T2
