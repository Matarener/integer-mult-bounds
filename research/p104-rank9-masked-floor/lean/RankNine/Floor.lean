import RankNine.Bridge9

set_option linter.unusedSectionVars false

/-!
# From the T3 output to the floor (types without a special line)

`left_inv`: if `X Yᵀ = A Bᵀ` and `A`, `B` (`104 × 9`) have left inverses, so do `X` and `Y`.
`floor_noU`: rows `P v = a ρ_v + λ_v Λ` (glued) or at most four live rows, all columns along their roots
⇒ every nine-term decoder of `N` costs at least 56 (F1 → `bform_floor_P104_h`, F3 → `caseII_gen` on `Nᵀ`).
The remaining hypotheses are those of BForm (#6188/#6218): `Capacity`, `BicliqueFact`, `CensusFact`.
-/

namespace RankNine

open Matrix

attribute [local instance] Classical.propDecidable

variable {K : Type*} [Field K] [CharZero K]

theorem left_inv {X Y : Matrix (Fin 104) BForm.C9 K} {A B : Matrix (Fin 104) (Fin 9) K}
    (Al Bl : Matrix (Fin 9) (Fin 104) K) (hA : Al * A = 1) (hB : Bl * B = 1) (h : X * Yᵀ = A * Bᵀ) :
    ∃ Xl Yl : Matrix BForm.C9 (Fin 104) K, Xl * X = 1 ∧ Yl * Y = 1 := by
  have h1 : (Al * X) * (Bl * Y)ᵀ = 1 := by
    calc (Al * X) * (Bl * Y)ᵀ = Al * (X * Yᵀ) * Blᵀ := by rw [transpose_mul]; simp only [Matrix.mul_assoc]
      _ = (Al * A) * (Bl * B)ᵀ := by rw [h, transpose_mul]; simp only [Matrix.mul_assoc]
      _ = 1 := by rw [hA, hB, transpose_one, Matrix.one_mul]
  have h2 : (Bl * Y)ᵀ * (Al * X) = 1 :=
    (Matrix.mul_eq_one_comm_of_card_eq (Fin 9) BForm.C9 K (A := Al * X) (B := (Bl * Y)ᵀ) (by simp)).mp h1
  refine ⟨(Bl * Y)ᵀ * Al, (Al * X)ᵀ * Bl, ?_, ?_⟩
  · rw [Matrix.mul_assoc]; exact h2
  · rw [Matrix.mul_assoc]
    have := congrArg Matrix.transpose h2
    rwa [transpose_mul, transpose_transpose, transpose_one] at this

theorem live_le_four (lam : ℕ → K) (OG : List ℕ) (hin : ∀ v < 104, lam v ≠ 0 → v ∈ OG)
    (h : ¬ ∃ x1 x2 x3 x4 x5, (x1 ∈ OG ∧ lam x1 ≠ 0) ∧ (x2 ∈ OG ∧ lam x2 ≠ 0) ∧ (x3 ∈ OG ∧ lam x3 ≠ 0) ∧
          (x4 ∈ OG ∧ lam x4 ≠ 0) ∧ (x5 ∈ OG ∧ lam x5 ≠ 0) ∧ dist5B x1 x2 x3 x4 x5 = true) :
    (Finset.univ.filter fun v : Fin 104 => lam v ≠ 0).card ≤ 4 := by
  by_contra hc
  rw [not_le] at hc
  obtain ⟨x1, h1, x2, h2, x3, h3, x4, h4, x5, h5, d12, d13, d14, d15, d23, d24, d25, d34, d35, d45⟩ :=
    card_ge_five (by omega : 5 ≤ (Finset.univ.filter fun v : Fin 104 => lam v ≠ 0).card)
  simp only [Finset.mem_filter, Finset.mem_univ, true_and] at h1 h2 h3 h4 h5
  apply h
  refine ⟨x1, x2, x3, x4, x5, ⟨hin _ x1.2 h1, h1⟩, ⟨hin _ x2.2 h2, h2⟩, ⟨hin _ x3.2 h3, h3⟩, ⟨hin _ x4.2 h4, h4⟩,
    ⟨hin _ x5.2 h5, h5⟩, ?_⟩
  simp [dist5B, Fin.val_inj, d12, d13, d14, d15, d23, d24, d25, d34, d35, d45]

/-- **Floor from the T3 output** (all columns along their roots). -/
theorem floor_noU (hcap : BForm.Capacity BForm.E8.labK) (hbic : BForm.BicliqueFact (BForm.E8.rK K))
    (hcensus : BForm.CensusFact BForm.E8.labK (BForm.E8.rK K))
    (N : Matrix (Fin 104) (Fin 104) K) (P c : ℕ → Fin 9 → K) (lam eta : ℕ → K)
    (hN : ∀ v s : Fin 104, N v s = P v ⬝ᵥ c s + lam v * eta s)
    (hcol : ∀ s < 104, ∃ b : K, c s = b • rho K s)
    (hrowd : ∀ v < 104, lam v = 0 → ∃ a : K, P v = a • rho K v)
    (hPs : ∀ v s : Fin 104, 9 / 4 * (BForm.E8.rK K s ⬝ᵥ (FK *ᵥ P v)) = rho K s ⬝ᵥ P v)
    (hglue : (∃ Λ : Fin 9 → K, ∀ v < 104, ∃ a : K, P v = a • rho K v + lam v • Λ) ∨
      (Finset.univ.filter fun v : Fin 104 => lam v ≠ 0).card ≤ 4)
    (hdiag : ∀ t, N t t ≠ 0) (hmask : ∀ u s : Fin 104, dot u s = 0 → N u s = 0)
    (Am Bm : Matrix (Fin 104) (Fin 9) K) (Al Bl : Matrix (Fin 9) (Fin 104) K) (hA : Al * Am = 1) (hB : Bl * Bm = 1)
    (hNAB : N = Am * Bmᵀ)
    (P' Q' : Matrix (Fin 104) BForm.C9 K) (h : N = P' * Q'ᵀ) : 56 ≤ BForm.cost BForm.E8.labK P' Q' := by
  rcases hglue with ⟨Λ, hrow⟩ | hL
  · obtain ⟨α, α', cc, β, hd, hbi, hpat, hform⟩ :=
      bform_F1 (BForm.E8.rK K) hr_P104 N P c lam eta Λ hN hrow hcol hdiag hmask
    obtain ⟨Xl, Yl, hX, hY⟩ := left_inv Al Bl hA hB (hform.symm.trans hNAB)
    exact BForm.E8h.bform_floor_P104_h hcap hbic hcensus α α' cc β hd hbi hpat Xl Yl hX hY P' Q'
      (hform.symm.trans h)
  · obtain ⟨α, cc, α', Y, hY, hZr, hcl, hpat, hform⟩ :=
      bform_F3 (BForm.E8.rK K) hr_P104 FK hF_P104 N P c lam eta hN hcol hrowd hPs hdiag hmask hL
    have hT : BForm.bX (BForm.E8.rK K) α cc * Yᵀ = Bm * Amᵀ := by
      rw [← hform, hNAB, transpose_mul, transpose_transpose]
    obtain ⟨Xl, Yl, hX, hYl⟩ := left_inv Bl Al hB hA hT
    have h' : BForm.bX (BForm.E8.rK K) α cc * Yᵀ = Q' * P'ᵀ := by
      rw [← hform, h, transpose_mul, transpose_transpose]
    rw [← BForm.cost_swap BForm.E8.labK P' Q']
    exact BForm.caseII_gen BForm.E8.labK hcap (BForm.E8.rK K) BForm.E8h.rootFact_h BForm.E8h.spanFact_h hcensus
      α cc Y _ α' hY hL hZr hcl hpat Xl Yl hX hYl Q' P' h'

end RankNine
