import RankNine.T3

set_option linter.unusedSectionVars false

/-!
# Rank-7 pinning on the Gram set (NOTE §13.25, LEAN-SCHEME lemma 4)

If `M` is Gram on `zm` (inside the dead mask `m`, with a frame `f` in `zm`) and a dead line `v ∉ zm` has
orthogonal lines in `zm` of root rank 7 (certificate `lcOK`), then `M` is Gram on `zm ∪ {v}` after changing the
gauge at `v` only (`pin_one`): by `rows_rep`, `P v ⊥ ρ_s` and `c v ⊥ ρ_s` for `s ∈ zm ∩ v^⊥`, so both are multiples
of `ρ_v` (`lc_sound`).  `pin_all` iterates over a list of pins.
-/

namespace RankNine

open Matrix

variable {K : Type*} [Field K] [CharZero K]

theorem bit_or_pow {zm v x : ℕ} : (zm ||| 2 ^ v).testBit x = true ↔ zm.testBit x = true ∨ x = v := by
  rw [Nat.testBit_or, Bool.or_eq_true, Nat.testBit_two_pow, decide_eq_true_eq]
  exact or_congr Iff.rfl eq_comm

theorem pin_one (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (g : ℕ → K) (hg : ∀ x, g x ≠ 0)
    (zm : ℕ) (hz : zm < 2 ^ 104) (hzm : ∀ x, zm.testBit x = true → m.testBit x = true)
    (hG : ∀ x < 104, ∀ y < 104, zm.testBit x = true → zm.testBit y = true → GramP A B g x y)
    (f : ℕ) (hf : ∀ k < 8, m.testBit (frL f k) = true ∧ zm.testBit (frL f k) = true) (hfv : fvecOK f = true)
    (v k0 : ℕ) (C : RCert) (hv : m.testBit v = true) (hvn : zm.testBit v = false) (hc : lcOK zm v k0 C = true)
    (hself : dot v v = 18) :
    ∃ g' : ℕ → K, (∀ x, g' x ≠ 0) ∧ ∀ x < 104, ∀ y < 104, (zm ||| 2 ^ v).testBit x = true →
      (zm ||| 2 ^ v).testBit y = true → GramP A B g' x y := by
  obtain ⟨lam, eta, hrep, hlam, hPZ, hcZ⟩ := rows_rep A B u hu m hZ hdiag hmask g hg zm hG f hf hfv
  have hv104 : v < 104 := by
    have hc' := hc
    simp only [lcOK, Bool.and_eq_true, decide_eq_true_eq] at hc'
    exact hc'.1.1.1.1.2
  have hlv : lam v = 0 := hlam v hv
  obtain ⟨a, ha⟩ := lc_sound hc (PV A B g f v) (PV_ones A B g f v) fun s hs hd => by
    have hs' := zm_lt hz hs
    have e : Mx A B v s = 0 := hmask v hv104 s hs' (orth_of_dot hd)
    rw [hrep v s, hcZ s hs' hs, hlv, zero_mul, add_zero, dotProduct_smul, smul_eq_mul] at e
    exact (mul_eq_zero.mp e).resolve_left (div_ne_zero (hg s) (by norm_num))
  obtain ⟨b, hb⟩ := lc_sound hc (cS A B g f v) (cS_ones A B g f v) fun x hx hd => by
    have hx' := zm_lt hz hx
    have e : Mx A B x v = 0 := hmask x hx' v hv104 (orth_of_dot (by rw [dot_comm]; exact hd))
    rw [hrep x v, hPZ x hx' hx, hlam x (hzm x hx), zero_mul, add_zero, smul_dotProduct, smul_eq_mul] at e
    rw [dotProduct_comm]
    exact (mul_eq_zero.mp e).resolve_left (dS_ne A B g hg hdiag hx')
  have hvv : Mx A B v v = a * b * 18 := by
    rw [hrep v v, ha, hb, hlv, zero_mul, add_zero, smul_dotProduct, dotProduct_smul, smul_eq_mul, smul_eq_mul,
      rho_dot, hself]
    push_cast
    ring
  have hb0 : b ≠ 0 := fun h0 => hdiag v hv104 (by
    rw [show A v ⬝ᵥ B v = Mx A B v v from rfl, hvv, h0]; ring)
  have hg'ne : ∀ z, z ≠ v → Function.update g v (18 * b) z = g z := fun z hz => Function.update_of_ne hz _ _
  have hg'v : Function.update g v (18 * b) v = 18 * b := Function.update_self _ _ _
  have hzv : ∀ z, zm.testBit z = true → z ≠ v := fun z hz e => by rw [e, hvn] at hz; exact absurd hz (by simp)
  have hdz : ∀ z, zm.testBit z = true → dS A B (Function.update g v (18 * b)) z = dS A B g z := by
    intro z hz'
    unfold dS
    rw [hg'ne z (hzv z hz')]
  have hdv : dS A B (Function.update g v (18 * b)) v = a := by
    unfold dS
    rw [hg'v, hvv]
    first | (field_simp; done) | (field_simp; ring)
  refine ⟨Function.update g v (18 * b), fun x => ?_, ?_⟩
  · by_cases hx : x = v
    · rw [hx, hg'v]; exact mul_ne_zero (by norm_num) hb0
    · rw [hg'ne x hx]; exact hg x
  intro x hx y hy hxm hym
  rw [bit_or_pow] at hxm hym
  unfold GramP
  rcases hxm with hxz | hxv <;> rcases hym with hyz | hyv
  · have h1 := hG x hx y hy hxz hyz
    unfold GramP at h1
    rw [hdz x hxz, hg'ne y (hzv y hyz)]
    exact h1
  · have e1 : Mx A B x v = dS A B g x * b * (dot x v : K) := by
      rw [hrep x v, hPZ x hx hxz, hlam x (hzm x hxz), zero_mul, add_zero, hb, smul_dotProduct, dotProduct_smul,
        smul_eq_mul, smul_eq_mul, rho_dot]
      ring
    rw [hyv, hdz x hxz, hg'v, e1]
    unfold gam
    ring
  · have e2 : Mx A B v y = a * (g y / 18) * (dot v y : K) := by
      rw [hrep v y, ha, hcZ y hy hyz, hlv, zero_mul, add_zero, smul_dotProduct, dotProduct_smul, smul_eq_mul,
        smul_eq_mul, rho_dot]
      ring
    rw [hxv, hdv, hg'ne y (hzv y hyz), e2]
    unfold gam
    ring
  · rw [hxv, hyv, hdv, hg'v, hvv]
    unfold gam
    rw [hself]
    push_cast
    ring

/-- a list of pins: each line dead, new, with a rank-7 certificate over the Gram set so far -/
def pinOK (m : ℕ) : ℕ → List (ℕ × ℕ × RCert) → Bool
  | _, [] => true
  | zm, (v, k0, C) :: r => m.testBit v && !zm.testBit v && lcOK zm v k0 C && dot v v == 18 &&
      pinOK m (zm ||| 2 ^ v) r

/-- the Gram set after the pins -/
def pinZ : ℕ → List (ℕ × ℕ × RCert) → ℕ
  | zm, [] => zm
  | zm, (v, _, _) :: r => pinZ (zm ||| 2 ^ v) r

theorem pin_all (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (f : ℕ) (hfv : fvecOK f = true) :
    ∀ (PL : List (ℕ × ℕ × RCert)) (zm : ℕ) (g : ℕ → K), (∀ x, g x ≠ 0) → zm < 2 ^ 104 →
      (∀ x, zm.testBit x = true → m.testBit x = true) →
      (∀ k < 8, m.testBit (frL f k) = true ∧ zm.testBit (frL f k) = true) → pinOK m zm PL = true →
      (∀ x < 104, ∀ y < 104, zm.testBit x = true → zm.testBit y = true → GramP A B g x y) →
      ∃ g' : ℕ → K, (∀ x, g' x ≠ 0) ∧
        ∀ x < 104, ∀ y < 104, (pinZ zm PL).testBit x = true → (pinZ zm PL).testBit y = true → GramP A B g' x y
  | [], zm, g, hg, _, _, _, _, hG => ⟨g, hg, hG⟩
  | (v, k0, C) :: r, zm, g, hg, hz, hzm, hf, hp, hG => by
    unfold pinOK at hp
    simp only [Bool.and_eq_true, Bool.not_eq_true', beq_iff_eq] at hp
    obtain ⟨⟨⟨⟨hv, hvn⟩, hc⟩, hself⟩, hr⟩ := hp
    obtain ⟨g1, hg1, hG1⟩ := pin_one A B u hu m hZ hdiag hmask g hg zm hz hzm hG f hf hfv v k0 C hv hvn hc hself
    have hv104 : v < 104 := by
      have hc' := hc
      simp only [lcOK, Bool.and_eq_true, decide_eq_true_eq] at hc'
      exact hc'.1.1.1.1.2
    have hz1 : zm ||| 2 ^ v < 2 ^ 104 :=
      Nat.or_lt_two_pow hz (Nat.pow_lt_pow_right (by norm_num) hv104)
    have hzm1 : ∀ x, (zm ||| 2 ^ v).testBit x = true → m.testBit x = true := by
      intro x hx
      rcases bit_or_pow.mp hx with h | h
      · exact hzm x h
      · rw [h]; exact hv
    have hf1 : ∀ k < 8, m.testBit (frL f k) = true ∧ (zm ||| 2 ^ v).testBit (frL f k) = true :=
      fun k hk => ⟨(hf k hk).1, bit_or_pow.mpr (Or.inl (hf k hk).2)⟩
    exact pin_all A B u hu m hZ hdiag hmask f hfv r (zm ||| 2 ^ v) g1 hg1 hz1 hzm1 hf1 hr hG1

end RankNine
