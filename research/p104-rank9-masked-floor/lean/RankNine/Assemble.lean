import RankNine.GlueData

set_option linter.unusedSectionVars false

/-!
# T3: assembly of rows and columns (types without a bad line)

Abstract input (from `rows_rep` and T3.1): `M v s = P v ⬝ c s + λ v η s`, `λ = 0` on `Z`, `P x = d x ρ x` and
`c s = (g s / 18) ρ s` on `Z`, `P v ⬝ 𝟙 = c s ⬝ 𝟙 = 0`, and the mask.  With the per-type line certificates
(`LineH`) and gluing data (`GlueH`) for the outer lines `O = P104 \ Z`:
* every column is a multiple of its root;
* every row with `λ v = 0` is a multiple of its root;
* either at most four rows are live, or there is a centre `Λ` with `P v ∈ K ρ_v + λ v Λ` for all rows.
-/

namespace RankNine

open Matrix

variable {K : Type*} [Field K] [CharZero K]

structure Rep (M : ℕ → ℕ → K) (P c : ℕ → Fin 9 → K) (lam eta : ℕ → K) (zm : ℕ) (d g : ℕ → K) : Prop where
  rep : ∀ v s, M v s = P v ⬝ᵥ c s + lam v * eta s
  lamZ : ∀ x, zm.testBit x = true → lam x = 0
  PZ : ∀ x < 104, zm.testBit x = true → P x = d x • rho K x
  cZ : ∀ s < 104, zm.testBit s = true → c s = (g s / 18) • rho K s
  dne : ∀ x < 104, d x ≠ 0
  gne : ∀ x, g x ≠ 0
  P1 : ∀ v, P v ⬝ᵥ vK K ones9L = 0
  c1 : ∀ s, c s ⬝ᵥ vK K ones9L = 0
  mask : ∀ v < 104, ∀ s < 104, orth v s = true → M v s = 0

/-- per-type line certificates on the outer lines -/
def LineH (K : Type*) [Field K] (zm : ℕ) (O : List ℕ) : Prop :=
  ∀ v ∈ O, ∀ d : Fin 9 → K, d ⬝ᵥ vK K ones9L = 0 → (∀ s, zm.testBit s = true → dot v s = 0 → d ⬝ᵥ rho K s = 0) →
    ∃ a : K, d = a • rho K v

/-- per-type gluing on the outer lines -/
def GlueH (K : Type*) [Field K] (zm : ℕ) (O : List ℕ) : Prop :=
  ∀ (h : ℕ → Fin 9 → K) (τ : ℕ → K) (L : ℕ → Prop), RowHyp zm h τ (fun v => v ∈ O ∧ L v) →
    (∃ x1 x2 x3 x4 x5, (x1 ∈ O ∧ L x1) ∧ (x2 ∈ O ∧ L x2) ∧ (x3 ∈ O ∧ L x3) ∧ (x4 ∈ O ∧ L x4) ∧
      (x5 ∈ O ∧ L x5) ∧ dist5B x1 x2 x3 x4 x5 = true) → ∃ Λ, ∀ v, v ∈ O → L v → Gl h Λ v

theorem zm_lt {zm : ℕ} (hz : zm < 2 ^ 104) {x : ℕ} (hx : zm.testBit x = true) : x < 104 := by
  by_contra hc
  have : zm.testBit x = false :=
    Nat.testBit_eq_false_of_lt (lt_of_lt_of_le hz (Nat.pow_le_pow_right (by norm_num) (by omega)))
  rw [hx] at this; exact absurd this (by simp)

theorem orth_of_dot {x y : ℕ} (h : dot x y = 0) : orth x y = true := by
  simp [orth, h]

section

variable {M : ℕ → ℕ → K} {P c : ℕ → Fin 9 → K} {lam eta : ℕ → K} {zm : ℕ} {d g : ℕ → K}

theorem col_gramm (R : Rep M P c lam eta zm d g) (hz : zm < 2 ^ 104) {O : List ℕ} (HL : LineH K zm O)
    {s : ℕ} (hs : s ∈ O) (hs' : s < 104) : ∃ b : K, c s = b • rho K s := by
  refine HL s hs (c s) (R.c1 s) fun x hx hdot => ?_
  have hx' := zm_lt hz hx
  have e := R.mask x hx' s hs' (orth_of_dot (by rw [dot_comm]; exact hdot))
  rw [R.rep, R.PZ x hx' hx, R.lamZ x hx, zero_mul, add_zero, smul_dotProduct, smul_eq_mul] at e
  rw [dotProduct_comm]
  exact (mul_eq_zero.mp e).resolve_left (R.dne x hx')

theorem row_dead (R : Rep M P c lam eta zm d g) (hz : zm < 2 ^ 104) {O : List ℕ} (HL : LineH K zm O)
    {v : ℕ} (hv : v ∈ O) (hv' : v < 104) (hl : lam v = 0) : ∃ a : K, P v = a • rho K v := by
  refine HL v hv (P v) (R.P1 v) fun s hs hdot => ?_
  have hs' := zm_lt hz hs
  have e := R.mask v hv' s hs' (orth_of_dot hdot)
  rw [R.rep, R.cZ s hs' hs, hl, zero_mul, add_zero, dotProduct_smul, smul_eq_mul] at e
  exact (mul_eq_zero.mp e).resolve_left (div_ne_zero (R.gne s) (by norm_num))

/-- the live rows satisfy the row hypothesis of `GlueData` -/
theorem row_hyp (R : Rep M P c lam eta zm d g) (hz : zm < 2 ^ 104) {O : List ℕ} (hO : ∀ v ∈ O, v < 104) :
    RowHyp zm (fun v => (lam v)⁻¹ • P v) (fun s => -(eta s / (g s / 18))) (fun v => v ∈ O ∧ lam v ≠ 0) := by
  intro v ⟨hv, hl⟩
  refine ⟨by show (lam v)⁻¹ • P v ⬝ᵥ vK K ones9L = 0; rw [smul_dotProduct, R.P1, smul_zero], fun s hs hdot => ?_⟩
  have hs' := zm_lt hz hs
  have e := R.mask v (hO v hv) s hs' (orth_of_dot hdot)
  rw [R.rep, R.cZ s hs' hs, dotProduct_smul, smul_eq_mul] at e
  have hk : g s / 18 ≠ 0 := div_ne_zero (R.gne s) (by norm_num)
  show (lam v)⁻¹ • P v ⬝ᵥ rho K s = -(eta s / (g s / 18))
  rw [smul_dotProduct, smul_eq_mul, eq_neg_iff_add_eq_zero, inv_mul_eq_div, div_add_div _ _ hl hk,
    div_eq_zero_iff]
  left
  linear_combination e

theorem glued_row {v : ℕ} (hl : lam v ≠ 0) {Λ : Fin 9 → K}
    (G : Gl (fun v => (lam v)⁻¹ • P v) Λ v) : ∃ a : K, P v = a • rho K v + lam v • Λ := by
  obtain ⟨a, e⟩ := G
  have e2 : (lam v)⁻¹ • P v = Λ + a • rho K v := e
  refine ⟨lam v * a, ?_⟩
  have e' : P v = lam v • ((lam v)⁻¹ • P v) := by rw [smul_smul, mul_inv_cancel₀ hl, one_smul]
  rw [e', e2, smul_add, smul_smul, add_comm]

/-- **T3 for a type without a bad line.** -/
theorem assemble (R : Rep M P c lam eta zm d g) (hz : zm < 2 ^ 104) {O : List ℕ} (hO : ∀ v ∈ O, v < 104)
    (hcov : ∀ v < 104, zm.testBit v = true ∨ v ∈ O) (HL : LineH K zm O) (HG : GlueH K zm O) :
    (∀ s < 104, ∃ b : K, c s = b • rho K s) ∧ (∀ v < 104, lam v = 0 → ∃ a : K, P v = a • rho K v) ∧
      ((∃ Λ : Fin 9 → K, ∀ v < 104, ∃ a : K, P v = a • rho K v + lam v • Λ) ∨
        ¬ ∃ x1 x2 x3 x4 x5, (x1 ∈ O ∧ lam x1 ≠ 0) ∧ (x2 ∈ O ∧ lam x2 ≠ 0) ∧ (x3 ∈ O ∧ lam x3 ≠ 0) ∧
          (x4 ∈ O ∧ lam x4 ≠ 0) ∧ (x5 ∈ O ∧ lam x5 ≠ 0) ∧ dist5B x1 x2 x3 x4 x5 = true) := by
  have hcol : ∀ s < 104, ∃ b : K, c s = b • rho K s := by
    intro s hs
    rcases hcov s hs with h | h
    · exact ⟨_, R.cZ s hs h⟩
    · exact col_gramm R hz HL h hs
  have hrow : ∀ v < 104, lam v = 0 → ∃ a : K, P v = a • rho K v := by
    intro v hv hl
    rcases hcov v hv with h | h
    · exact ⟨_, R.PZ v hv h⟩
    · exact row_dead R hz HL h hv hl
  refine ⟨hcol, hrow, ?_⟩
  by_cases h5 : ∃ x1 x2 x3 x4 x5, (x1 ∈ O ∧ lam x1 ≠ 0) ∧ (x2 ∈ O ∧ lam x2 ≠ 0) ∧ (x3 ∈ O ∧ lam x3 ≠ 0) ∧
      (x4 ∈ O ∧ lam x4 ≠ 0) ∧ (x5 ∈ O ∧ lam x5 ≠ 0) ∧ dist5B x1 x2 x3 x4 x5 = true
  · left
    obtain ⟨Λ, hΛ⟩ := HG _ _ (fun v => lam v ≠ 0) (row_hyp R hz hO) h5
    refine ⟨Λ, fun v hv => ?_⟩
    by_cases hl : lam v = 0
    · obtain ⟨a, e⟩ := hrow v hv hl
      exact ⟨a, by rw [e, hl, zero_smul, add_zero]⟩
    · rcases hcov v hv with h | h
      · exact absurd (R.lamZ v h) hl
      · exact glued_row hl (hΛ v h hl)
  · exact Or.inr h5

end

end RankNine
