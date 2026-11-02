import RankNine.T2Zero

/-!
# T2.4: rank argument on rows dead for two terms

Rows dead for two terms with independent dead vectors `u, u'` lie in a 7-dimensional space, so no 8 of them are
independent (`eight_not_indep`).  On the other hand, an 8 × 8 block of `M` with non-zero determinant makes its 8 rows
independent (`rows_indep_of_det`).  After T2.3 the block is a rescaled Gram block, whose determinant is non-zero by
an integer adjugate certificate (`det_ne_of_adj`).
-/

namespace RankNine.T2

open Matrix RankNine

variable {K : Type*} [Field K]

set_option linter.unusedSectionVars false

/-- 8 vectors orthogonal to two independent vectors in `K⁹` are dependent -/
theorem eight_not_indep (u u' : Fin 9 → K) (hind : LinearIndependent K ![u, u']) (v : Fin 8 → Fin 9 → K)
    (hv : ∀ i, v i ⬝ᵥ u = 0) (hv' : ∀ i, v i ⬝ᵥ u' = 0) : ¬ LinearIndependent K v := by
  intro hli
  let Q : Matrix (Fin 2) (Fin 9) K := Matrix.of ![u, u']
  have hrank : Q.rank = 2 := by
    rw [Matrix.rank_eq_finrank_span_rows]
    show Module.finrank K (Submodule.span K (Set.range ![u, u'])) = 2
    rw [finrank_span_eq_card hind, Fintype.card_fin]
  have hker : ∀ i, v i ∈ LinearMap.ker Q.mulVecLin := by
    intro i
    have h0 : u ⬝ᵥ v i = 0 := by rw [dotProduct_comm]; exact hv i
    have h1 : u' ⬝ᵥ v i = 0 := by rw [dotProduct_comm]; exact hv' i
    rw [LinearMap.mem_ker, Matrix.mulVecLin_apply]
    funext r
    fin_cases r
    · simpa [Matrix.mulVec, Q] using h0
    · simpa [Matrix.mulVec, Q] using h1
  let w : Fin 8 → LinearMap.ker Q.mulVecLin := fun i => ⟨v i, hker i⟩
  have hw : LinearIndependent K w := LinearIndependent.of_comp (LinearMap.ker Q.mulVecLin).subtype hli
  have h8 := hw.fintype_card_le_finrank
  have hrn := LinearMap.finrank_range_add_finrank_ker Q.mulVecLin
  have hr : Module.finrank K (LinearMap.range Q.mulVecLin) = 2 := hrank
  simp only [Fintype.card_fin, Module.finrank_fin_fun] at h8 hrn
  omega

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
