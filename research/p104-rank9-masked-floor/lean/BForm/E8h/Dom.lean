import BForm.E8h.LvEq

/-!
# The dominant chamber argument

Over `ℚ`: a non-zero vector is orthogonal to at most 37 positive roots, or to at most 42 and it is a multiple of
`r_a ± r_b` with `r_a ⊥ r_b` (D7), or it is a multiple of a root (E7).
-/

namespace BForm.E8h

set_option linter.unusedSectionVars false

open Matrix Finset BForm.E8

abbrev V := Fin 8 → ℚ

/-- number of positive roots orthogonal to `y` -/
noncomputable def Zc (y : V) : ℕ := (univ.filter fun j : Fin 120 => lv ℚ j ⬝ᵥ y = 0).card

/-- number of positive roots with negative inner product -/
noncomputable def nNeg (y : V) : ℕ := (univ.filter fun j : Fin 120 => lv ℚ j ⬝ᵥ y < 0).card

def D7Form (y : V) : Prop := ∃ a b : ℕ, a < 120 ∧ b < 120 ∧ lv ℚ a ⬝ᵥ lv ℚ b = 0 ∧
  ∃ μ ε : ℚ, (ε = 1 ∨ ε = -1) ∧ y = μ • (lv ℚ a + ε • lv ℚ b)

def RootForm (y : V) : Prop := ∃ j < 120, ∃ μ : ℚ, y = μ • lv ℚ j

def Shape (y : V) : Prop := Zc y ≤ 37 ∨ (Zc y ≤ 42 ∧ D7Form y) ∨ RootForm y

theorem card_filter_invol {n : ℕ} (e : Fin n → Fin n) (he : Function.Involutive e) (p : Fin n → Prop)
    [DecidablePred p] : (univ.filter fun j => p (e j)).card = (univ.filter p).card := by
  apply Finset.card_bij (fun j _ => e j)
  · intro a ha; simpa using ha
  · intro a _ b _ h; exact he.injective h
  · intro b hb; exact ⟨e b, by simpa [he b] using hb, he b⟩

/-- `s_i` as an involution of the positive roots -/
def rp (i : ℕ) (hi : i < 8) (j : Fin 120) : Fin 120 := ⟨rf i j, rf_lt i j hi j.2⟩

theorem rp_invol (i : ℕ) (hi : i < 8) : Function.Involutive (rp i hi) := by
  intro j; ext; simp [rp, rf_rf i j hi j.2]

theorem rf_self (i : ℕ) (hi : i < 8) : rf i i = i := by
  have h := rfiOK_true
  rw [rfiOK, all_range] at h
  exact beq_iff_eq.mp (h i hi)

theorem sg_ne (i j : ℕ) : sg (K := ℚ) i j ≠ 0 := by unfold sg; split_ifs <;> norm_num

theorem Zc_sr (i : ℕ) (hi : i < 8) (y : V) : Zc (sr i y) = Zc y := by
  unfold Zc
  have : (univ.filter fun j : Fin 120 => lv ℚ j ⬝ᵥ sr i y = 0) =
      univ.filter fun j : Fin 120 => lv ℚ (rp i hi j) ⬝ᵥ y = 0 := by
    apply Finset.filter_congr; intro j _
    rw [sr_lv_dot i j hi j.2]; simp [rp, sg_ne]
  rw [this, card_filter_invol (rp i hi) (rp_invol i hi) (fun j => lv ℚ j ⬝ᵥ y = 0)]

theorem nNeg_sr (i : ℕ) (hi : i < 8) (y : V) (hneg : lv ℚ i ⬝ᵥ y < 0) : nNeg (sr i y) + 1 = nNeg y := by
  unfold nNeg
  set q : Fin 120 → Prop := fun k => k ≠ ⟨i, by omega⟩ ∧ lv ℚ k ⬝ᵥ y < 0 with hq
  have h1 : (univ.filter fun j : Fin 120 => lv ℚ j ⬝ᵥ sr i y < 0) = univ.filter fun j => q (rp i hi j) := by
    apply Finset.filter_congr; intro j _
    rw [sr_lv_dot i j hi j.2]
    simp only [hq, sg, rp, ne_eq, Fin.ext_iff]
    by_cases hj : (j : ℕ) = i
    · have : rf i j = i := by rw [hj, rf_self i hi]
      rw [if_pos hj, this]
      constructor
      · intro h; linarith
      · intro h; exact absurd rfl h.1
    · have : rf i j ≠ i := by
        intro h; apply hj; have := rf_rf i j hi j.2; rw [h, rf_self i hi] at this; omega
      rw [if_neg hj, one_mul]
      constructor
      · intro h; exact ⟨this, h⟩
      · intro h; exact h.2
  rw [h1, card_filter_invol (rp i hi) (rp_invol i hi) q]
  have h2 : univ.filter q = (univ.filter fun k : Fin 120 => lv ℚ k ⬝ᵥ y < 0).erase ⟨i, by omega⟩ := by
    ext k; simp [hq, and_comm]
  rw [h2, Finset.card_erase_add_one]
  simpa using hneg

theorem sr_ne_zero (i : ℕ) (hi : i < 8) (y : V) (hy : y ≠ 0) : sr i y ≠ 0 := by
  intro h; apply hy
  rw [← sr_sr i (by omega) y, h]; ext k; simp [sr]

theorem shape_of_sr (i : ℕ) (hi : i < 8) (y : V) (h : Shape (sr i y)) : Shape y := by
  have hy : y = sr i (sr i y) := (sr_sr i (by omega) y).symm
  rcases h with h | ⟨h, a, b, ha, hb, hab, μ, ε, hε, he⟩ | ⟨j, hj, μ, he⟩
  · left; rwa [Zc_sr i hi] at h
  · right; left
    refine ⟨by rwa [Zc_sr i hi] at h, rf i a, rf i b, rf_lt i a hi ha, rf_lt i b hi hb, ?_, μ * sg i a,
      ε * sg i b * sg i a, ?_, ?_⟩
    · have := sr_iso (K := ℚ) i (by omega) (lv ℚ a) (lv ℚ b)
      rw [sr_lv i a hi ha, sr_lv i b hi hb, hab, smul_dotProduct, dotProduct_smul, smul_eq_mul,
        smul_eq_mul] at this
      have h2 : sg (K := ℚ) i a * sg i b ≠ 0 := mul_ne_zero (sg_ne i a) (sg_ne i b)
      have : sg (K := ℚ) i a * sg i b * (lv ℚ (rf i a) ⬝ᵥ lv ℚ (rf i b)) = 0 := by linarith
      rcases mul_eq_zero.mp this with h3 | h3
      · exact absurd h3 h2
      · exact h3
    · unfold sg; rcases hε with rfl | rfl <;> split_ifs <;> norm_num
    · rw [hy, he, sr_smul, sr_add, sr_smul, sr_lv i a hi ha, sr_lv i b hi hb]
      have hs := sg_sq (K := ℚ) i a
      ext k; simp only [Pi.smul_apply, Pi.add_apply, smul_eq_mul]
      linear_combination (-(μ * ε * sg i b * lv ℚ (rf i b) k)) * hs
  · right; right
    refine ⟨rf i j, rf_lt i j hi hj, μ * sg i j, ?_⟩
    rw [hy, he, sr_smul, sr_lv i j hi hj, smul_smul]

end BForm.E8h
