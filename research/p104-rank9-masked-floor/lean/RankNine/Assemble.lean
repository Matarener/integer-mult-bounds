import RankNine.GlueData

set_option linter.unusedSectionVars false

/-!
# T3: assembly of rows and columns

Abstract input (from `rows_rep` and T3.1): `M v s = P v ⬝ c s + λ v η s`, `λ = 0` on `Z`, `P x = d x ρ x` and
`c s = (g s / 18) ρ s` on `Z`, `P v ⬝ 𝟙 = c s ⬝ 𝟙 = 0`, non-zero diagonal and the mask.  Per type:
* line certificates on `OL` (outer lines except the bad line `u`): columns in `OL` and dead rows in `OL` are
  multiples of their roots (`col_gramm`, `row_dead`);
* the dead bad row `u` is a multiple of `ρ_u` by two orthogonal columns `s ⊥ t` (`dead_special`): a column with
  `c = 0` forces a live row, and two such columns cannot be orthogonal;
* pair certificates over the mask `Sm` (`Z` and the columns of `OL`; a column orthogonal to a live row is non-zero,
  `col_ne`) glue the live rows of `OG` (`row_hyp`, `GlueH`).
Output (`assemble`): every column except `u` and every dead row is a multiple of its root, and either at most four
rows of `OG` are live or there is a centre `Λ` with `P v ∈ K ρ_v + λ v Λ` for all rows.
-/

namespace RankNine

open Matrix

/-- line certificate whose lines lie in `Z ∪ {s}` -/
def lcxOK (Zm s : ℕ) (v k0 : ℕ) (C : RCert) : Bool :=
  certOK C.X C.N C.No C.D C.pm && decide (v < 104) && decide (k0 < 9) &&
    (List.range 9).all (fun i => !C.pm.testBit i || i == k0) && ((root v).getD k0 0 != 0) &&
    (List.range C.X.length).all (fun t => (Zm.testBit (C.X.getD t 0) || C.X.getD t 0 == s) &&
      dot v (C.X.getD t 0) == 0)

theorem lcx_sound {K : Type*} [Field K] [CharZero K] {Zm s v k0 : ℕ} {C : RCert}
    (hp : lcxOK Zm s v k0 C = true) (d : Fin 9 → K) (h1 : d ⬝ᵥ vK K ones9L = 0)
    (hd : ∀ x, Zm.testBit x = true → dot v x = 0 → d ⬝ᵥ rho K x = 0) (hs : d ⬝ᵥ rho K s = 0) :
    ∃ a : K, d = a • rho K v := by
  simp only [lcxOK, Bool.and_eq_true, decide_eq_true_eq] at hp
  obtain ⟨⟨⟨⟨⟨hc, hv⟩, hk0⟩, hpm⟩, hρ⟩, hX⟩ := hp
  have hx : ∀ t < C.X.length, (Zm.testBit (C.X.getD t 0) = true ∨ C.X.getD t 0 = s) ∧
      dot v (C.X.getD t 0) = 0 := by
    intro t ht
    have := (List.all_eq_true.mp hX) t (List.mem_range.mpr ht)
    simp only [Bool.and_eq_true, Bool.or_eq_true, beq_iff_eq] at this
    exact this
  have hpiv : ∀ i : Fin 9, C.pm.testBit i = true → (i : ℕ) = k0 := by
    intro i hi
    have := (List.all_eq_true.mp hpm) i (List.mem_range.mpr i.2)
    simp only [Bool.or_eq_true, Bool.not_eq_true', beq_iff_eq] at this
    rcases this with e | e
    · rw [hi] at e; exact absurd e (by simp)
    · exact e
  have hρ' : (root v).getD k0 0 ≠ 0 := by simpa using hρ
  refine ⟨_, line_of_cert C hc hv hk0 hpiv hρ' (fun t ht => (hx t ht).2) d (fun t ht => ?_) h1⟩
  rcases (hx t ht).1 with e | e
  · exact hd _ e (hx t ht).2
  · rw [e]; exact hs

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
  diag : ∀ x < 104, M x x ≠ 0
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

/-- a dead row is orthogonal to the roots of `Z ∩ O_v` -/
theorem row_dead_dot (R : Rep M P c lam eta zm d g) (hz : zm < 2 ^ 104) {v : ℕ} (hv' : v < 104)
    (hl : lam v = 0) : ∀ s, zm.testBit s = true → dot v s = 0 → P v ⬝ᵥ rho K s = 0 := by
  intro s hs hdot
  have hs' := zm_lt hz hs
  have e := R.mask v hv' s hs' (orth_of_dot hdot)
  rw [R.rep, R.cZ s hs' hs, hl, zero_mul, add_zero, dotProduct_smul, smul_eq_mul] at e
  exact (mul_eq_zero.mp e).resolve_left (div_ne_zero (R.gne s) (by norm_num))

theorem row_dead (R : Rep M P c lam eta zm d g) (hz : zm < 2 ^ 104) {O : List ℕ} (HL : LineH K zm O)
    {v : ℕ} (hv : v ∈ O) (hv' : v < 104) (hl : lam v = 0) : ∃ a : K, P v = a • rho K v :=
  HL v hv (P v) (R.P1 v) (row_dead_dot R hz hv' hl)

theorem col_beta {s : ℕ} (hs : s < 104) {b : K} (hb : c s = b • rho K s) : c s ⬝ᵥ rho K s / 18 = b := by
  rw [hb, smul_dotProduct, rho_dot, dot_self hs, smul_eq_mul]
  push_cast
  exact mul_div_cancel_right₀ b (by norm_num)

/-- a column orthogonal to a live row is not zero -/
theorem col_ne (R : Rep M P c lam eta zm d g) {v s : ℕ} (hv : v < 104) (hs : s < 104) (hl : lam v ≠ 0)
    (hvs : dot v s = 0) {b : K} (hb : c s = b • rho K s) : b ≠ 0 := by
  intro h0
  rw [h0, zero_smul] at hb
  have e := R.mask v hv s hs (orth_of_dot hvs)
  rw [R.rep, hb, dotProduct_zero, zero_add] at e
  have he : eta s = 0 := (mul_eq_zero.mp e).resolve_left hl
  apply R.diag s hs
  rw [R.rep, hb, dotProduct_zero, he, mul_zero, add_zero]

/-- the live rows satisfy the row hypothesis of `GlueData` for every mask of non-zero-free gramm columns -/
theorem row_hyp (R : Rep M P c lam eta zm d g) {Sm : ℕ} {O : List ℕ} (hO : ∀ v ∈ O, v < 104)
    (hS : ∀ s, Sm.testBit s = true → s < 104 ∧ ∃ b : K, c s = b • rho K s) :
    RowHyp Sm (fun v => (lam v)⁻¹ • P v) (fun s => -(eta s / (c s ⬝ᵥ rho K s / 18)))
      (fun v => v ∈ O ∧ lam v ≠ 0) := by
  intro v ⟨hv, hl⟩
  refine ⟨by show (lam v)⁻¹ • P v ⬝ᵥ vK K ones9L = 0; rw [smul_dotProduct, R.P1, smul_zero],
    fun s hs hdot => ?_⟩
  obtain ⟨hs', b, hb⟩ := hS s hs
  have hb0 := col_ne R (hO v hv) hs' hl hdot hb
  have e := R.mask v (hO v hv) s hs' (orth_of_dot hdot)
  rw [R.rep, hb, dotProduct_smul, smul_eq_mul] at e
  show (lam v)⁻¹ • P v ⬝ᵥ rho K s = -(eta s / (c s ⬝ᵥ rho K s / 18))
  rw [col_beta hs' hb, smul_dotProduct, smul_eq_mul, eq_neg_iff_add_eq_zero, inv_mul_eq_div,
    div_add_div _ _ hl hb0, div_eq_zero_iff]
  left
  linear_combination e

theorem glued_row {v : ℕ} (hl : lam v ≠ 0) {Λ : Fin 9 → K}
    (G : Gl (fun v => (lam v)⁻¹ • P v) Λ v) : ∃ a : K, P v = a • rho K v + lam v • Λ := by
  obtain ⟨a, e⟩ := G
  have e2 : (lam v)⁻¹ • P v = Λ + a • rho K v := e
  refine ⟨lam v * a, ?_⟩
  have e' : P v = lam v • ((lam v)⁻¹ • P v) := by rw [smul_smul, mul_inv_cancel₀ hl, one_smul]
  rw [e', e2, smul_add, smul_smul, add_comm]

/-- a zero column `c s = 0` forces `λ s ≠ 0` and `η s ≠ 0` -/
theorem zero_col (R : Rep M P c lam eta zm d g) {s : ℕ} (hs : s < 104) (h0 : c s = 0) :
    lam s ≠ 0 ∧ eta s ≠ 0 := by
  have e := R.diag s hs
  rw [R.rep, h0, dotProduct_zero, zero_add] at e
  exact ⟨left_ne_zero_of_mul e, right_ne_zero_of_mul e⟩

/-- **the dead bad row**: two orthogonal columns `s ⊥ t`, both orthogonal to `r`, each with a rank-7
certificate on `Z ∩ O_r ∪ {s}` (resp. `{t}`) -/
theorem dead_special (R : Rep M P c lam eta zm d g) (hz : zm < 2 ^ 104) {r s t k0 k1 : ℕ} {Cs Ct : RCert}
    (hr : r < 104) (hs : s < 104) (ht : t < 104) (hl : lam r = 0) (hst : dot s t = 0) (hrs : dot r s = 0)
    (hrt : dot r t = 0) (cs : ∃ b : K, c s = b • rho K s) (ct : ∃ b : K, c t = b • rho K t)
    (hCs : lcxOK zm s r k0 Cs = true) (hCt : lcxOK zm t r k1 Ct = true) : ∃ a : K, P r = a • rho K r := by
  have base := row_dead_dot R hz hr hl
  have pin : ∀ x < 104, dot r x = 0 → ∀ b : K, c x = b • rho K x → b ≠ 0 → P r ⬝ᵥ rho K x = 0 := by
    intro x hx hrx b hb hb0
    have e := R.mask r hr x hx (orth_of_dot hrx)
    rw [R.rep, hb, hl, zero_mul, add_zero, dotProduct_smul, smul_eq_mul] at e
    exact (mul_eq_zero.mp e).resolve_left hb0
  obtain ⟨bs, hbs⟩ := cs
  obtain ⟨bt, hbt⟩ := ct
  by_cases h1 : bs = 0
  · by_cases h2 : bt = 0
    · exfalso
      rw [h1, zero_smul] at hbs
      rw [h2, zero_smul] at hbt
      obtain ⟨-, hes⟩ := zero_col R hs hbs
      obtain ⟨hlt, -⟩ := zero_col R ht hbt
      have e := R.mask t ht s hs (orth_of_dot (by rw [dot_comm]; exact hst))
      rw [R.rep, hbs, dotProduct_zero, zero_add] at e
      exact mul_ne_zero hlt hes e
    · exact lcx_sound hCt (P r) (R.P1 r) base (pin t ht hrt bt hbt h2)
  · exact lcx_sound hCs (P r) (R.P1 r) base (pin s hs hrs bs hbs h1)

/-- a dead certified row `s ⊥ U` pins the column `c U` -/
theorem col_pin (R : Rep M P c lam eta zm d g) (hz : zm < 2 ^ 104) {U s k0 : ℕ} {C : RCert} (hU : U < 104)
    (hs : s < 104) (hl : lam s = 0) (hsU : dot s U = 0) (hrow : ∃ a : K, P s = a • rho K s)
    (hC : lcxOK zm s U k0 C = true) : ∃ b : K, c U = b • rho K U := by
  obtain ⟨a, ha⟩ := hrow
  have ha0 : a ≠ 0 := by
    rintro rfl
    have e := R.diag s hs
    rw [R.rep, ha, hl, zero_smul, zero_dotProduct, zero_mul, add_zero] at e
    exact e rfl
  refine lcx_sound hC (c U) (R.c1 U) (fun x hx hdot => ?_) ?_
  · have hx' := zm_lt hz hx
    have e := R.mask x hx' U hU (orth_of_dot (by rw [dot_comm]; exact hdot))
    rw [R.rep, R.PZ x hx' hx, R.lamZ x hx, zero_mul, add_zero, smul_dotProduct, smul_eq_mul] at e
    rw [dotProduct_comm]
    exact (mul_eq_zero.mp e).resolve_left (R.dne x hx')
  · have e := R.mask s hs U hU (orth_of_dot hsU)
    rw [R.rep, ha, hl, zero_mul, add_zero, smul_dotProduct, smul_eq_mul] at e
    rw [dotProduct_comm]
    exact (mul_eq_zero.mp e).resolve_left ha0

/-- **T3 per type.**  `OL`: lines with line certificates, `OG`: lines glued over the mask `Sm`, `u`: the bad line
(`u = 104` if there is none), whose dead row is handled by `hu`. -/
theorem assemble (R : Rep M P c lam eta zm d g) (hz : zm < 2 ^ 104) {OL OG : List ℕ} {Sm u : ℕ}
    (hOL : ∀ v ∈ OL, v < 104) (hOG : ∀ v ∈ OG, v < 104)
    (hcov : ∀ v < 104, zm.testBit v = true ∨ v ∈ OL ∨ v = u)
    (hlive : ∀ v < 104, zm.testBit v = false → v ∉ OG → lam v = 0)
    (hS : ∀ s, Sm.testBit s = true → zm.testBit s = true ∨ s ∈ OL)
    (HL : LineH K zm OL) (HG : GlueH K Sm OG) (hu : u < 104 → lam u = 0 → ∃ a : K, P u = a • rho K u) :
    (∀ s < 104, s ≠ u → ∃ b : K, c s = b • rho K s) ∧ (∀ v < 104, lam v = 0 → ∃ a : K, P v = a • rho K v) ∧
      ((∃ Λ : Fin 9 → K, ∀ v < 104, ∃ a : K, P v = a • rho K v + lam v • Λ) ∨
        ¬ ∃ x1 x2 x3 x4 x5, (x1 ∈ OG ∧ lam x1 ≠ 0) ∧ (x2 ∈ OG ∧ lam x2 ≠ 0) ∧ (x3 ∈ OG ∧ lam x3 ≠ 0) ∧
          (x4 ∈ OG ∧ lam x4 ≠ 0) ∧ (x5 ∈ OG ∧ lam x5 ≠ 0) ∧ dist5B x1 x2 x3 x4 x5 = true) := by
  have hcol : ∀ s < 104, s ≠ u → ∃ b : K, c s = b • rho K s := by
    intro s hs hsu
    rcases hcov s hs with h | h | h
    · exact ⟨_, R.cZ s hs h⟩
    · exact col_gramm R hz HL h hs
    · exact absurd h hsu
  have hrow : ∀ v < 104, lam v = 0 → ∃ a : K, P v = a • rho K v := by
    intro v hv hl
    rcases hcov v hv with h | h | h
    · exact ⟨_, R.PZ v hv h⟩
    · exact row_dead R hz HL h hv hl
    · rw [h] at hv hl ⊢; exact hu hv hl
  refine ⟨hcol, hrow, ?_⟩
  have hS' : ∀ s, Sm.testBit s = true → s < 104 ∧ ∃ b : K, c s = b • rho K s := by
    intro s hs
    rcases hS s hs with h | h
    · exact ⟨zm_lt hz h, _, R.cZ s (zm_lt hz h) h⟩
    · exact ⟨hOL s h, col_gramm R hz HL h (hOL s h)⟩
  by_cases h5 : ∃ x1 x2 x3 x4 x5, (x1 ∈ OG ∧ lam x1 ≠ 0) ∧ (x2 ∈ OG ∧ lam x2 ≠ 0) ∧ (x3 ∈ OG ∧ lam x3 ≠ 0) ∧
      (x4 ∈ OG ∧ lam x4 ≠ 0) ∧ (x5 ∈ OG ∧ lam x5 ≠ 0) ∧ dist5B x1 x2 x3 x4 x5 = true
  · left
    obtain ⟨Λ, hΛ⟩ := HG _ _ (fun v => lam v ≠ 0) (row_hyp R hOG hS') h5
    refine ⟨Λ, fun v hv => ?_⟩
    by_cases hl : lam v = 0
    · obtain ⟨a, e⟩ := hrow v hv hl
      exact ⟨a, by rw [e, hl, zero_smul, add_zero]⟩
    · by_cases hzv : zm.testBit v = true
      · exact absurd (R.lamZ v hzv) hl
      · by_cases hg : v ∈ OG
        · exact glued_row hl (hΛ v hg hl)
        · exact absurd (hlive v hv (by simpa using hzv) hg) hl
  · exact Or.inr h5

end

end RankNine
