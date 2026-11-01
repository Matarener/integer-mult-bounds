import RankNine.RankCert

set_option linter.unusedSectionVars false

/-!
# T3.4 linear algebra on roots

* `indep2`, `indep3`: roots with non-zero Gram determinant are linearly independent (Cramer with the adjugate).
* `line_of_cert`: a vector orthogonal to `𝟙` and to the roots of a rank-7 certificate set inside `ρ_v^⊥` is a
  multiple of `ρ_v` (one pivot coordinate `k0` with `ρ_v k0 ≠ 0`).
* `pair_of_cert`: the same with a rank-6 set inside `ρ_v^⊥ ∩ ρ_w^⊥` and two pivots: a combination of `ρ_v, ρ_w`.
-/

namespace RankNine

open Matrix

variable {K : Type*} [Field K] [CharZero K]

theorem cramer2 {x y a : K} (h : 324 - a * a ≠ 0) (e1 : x * 18 + y * a = 0) (e2 : x * a + y * 18 = 0) :
    x = 0 ∧ y = 0 := by
  constructor
  · have : x * (324 - a * a) = 0 := by linear_combination 18 * e1 - a * e2
    exact (mul_eq_zero.mp this).resolve_right h
  · have : y * (324 - a * a) = 0 := by linear_combination 18 * e2 - a * e1
    exact (mul_eq_zero.mp this).resolve_right h

theorem cramer3 {x y z a b c : K} (h : 5832 + 2 * a * b * c - 18 * (a * a + b * b + c * c) ≠ 0)
    (e1 : x * 18 + y * a + z * b = 0) (e2 : x * a + y * 18 + z * c = 0) (e3 : x * b + y * c + z * 18 = 0) :
    x = 0 ∧ y = 0 ∧ z = 0 := by
  refine ⟨?_, ?_, ?_⟩
  · have : x * (5832 + 2 * a * b * c - 18 * (a * a + b * b + c * c)) = 0 := by
      linear_combination (324 - c ^ 2) * e1 + (b * c - 18 * a) * e2 + (a * c - 18 * b) * e3
    exact (mul_eq_zero.mp this).resolve_right h
  · have : y * (5832 + 2 * a * b * c - 18 * (a * a + b * b + c * c)) = 0 := by
      linear_combination (b * c - 18 * a) * e1 + (324 - b ^ 2) * e2 + (a * b - 18 * c) * e3
    exact (mul_eq_zero.mp this).resolve_right h
  · have : z * (5832 + 2 * a * b * c - 18 * (a * a + b * b + c * c)) = 0 := by
      linear_combination (a * c - 18 * b) * e1 + (a * b - 18 * c) * e2 + (324 - a ^ 2) * e3
    exact (mul_eq_zero.mp this).resolve_right h

/-- Gram determinant of two lines -/
def gram2 (u v : ℕ) : ℤ := 324 - dot u v * dot u v

/-- Gram determinant of three lines -/
def gram3 (u v w : ℕ) : ℤ :=
  5832 + 2 * dot u v * dot u w * dot v w - 18 * (dot u v * dot u v + dot u w * dot u w + dot v w * dot v w)

theorem indep2 {u v : ℕ} (hu : u < 104) (hv : v < 104) (h : gram2 u v ≠ 0) {x y : K}
    (e : x • rho K u + y • rho K v = 0) : x = 0 ∧ y = 0 := by
  have e1 := congrArg (fun w => w ⬝ᵥ rho K u) e
  have e2 := congrArg (fun w => w ⬝ᵥ rho K v) e
  simp only [add_dotProduct, smul_dotProduct, smul_eq_mul, zero_dotProduct, rho_dot] at e1 e2
  rw [dot_self hu, dot_comm v u] at e1
  rw [dot_self hv] at e2
  push_cast at e1 e2
  have hK : ((gram2 u v : ℤ) : K) ≠ 0 := Int.cast_ne_zero.mpr h
  unfold gram2 at hK; push_cast at hK
  exact cramer2 hK e1 e2

theorem indep3 {u v w : ℕ} (hu : u < 104) (hv : v < 104) (hw : w < 104) (h : gram3 u v w ≠ 0) {x y z : K}
    (e : x • rho K u + y • rho K v + z • rho K w = 0) : x = 0 ∧ y = 0 ∧ z = 0 := by
  have e1 := congrArg (fun t => t ⬝ᵥ rho K u) e
  have e2 := congrArg (fun t => t ⬝ᵥ rho K v) e
  have e3 := congrArg (fun t => t ⬝ᵥ rho K w) e
  simp only [add_dotProduct, smul_dotProduct, smul_eq_mul, zero_dotProduct, rho_dot] at e1 e2 e3
  rw [dot_self hu, dot_comm v u, dot_comm w u] at e1
  rw [dot_self hv, dot_comm w v] at e2
  rw [dot_self hw] at e3
  push_cast at e1 e2 e3
  have hK : ((gram3 u v w : ℤ) : K) ≠ 0 := Int.cast_ne_zero.mpr h
  unfold gram3 at hK; push_cast at hK
  exact cramer3 hK e1 e2 e3

/-- generic certificate data for `line_of_cert` / `pair_of_cert` -/
structure RCert where
  X : List ℕ
  N : List (List ℤ)
  No : List ℤ
  D : ℤ
  pm : ℕ

theorem rho_apply (x : ℕ) (i : Fin 9) : rho K x i = (((root x).getD i 0 : ℤ) : K) := rfl

theorem line_of_cert (C : RCert) (hc : certOK C.X C.N C.No C.D C.pm = true) {v k0 : ℕ} (hv : v < 104)
    (hk0 : k0 < 9) (hpiv : ∀ i : Fin 9, C.pm.testBit i = true → (i : ℕ) = k0) (hρ : (root v).getD k0 0 ≠ 0)
    (hX : ∀ t < C.X.length, dot v (C.X.getD t 0) = 0) (d : Fin 9 → K)
    (hd : ∀ t < C.X.length, d ⬝ᵥ rho K (C.X.getD t 0) = 0) (h1 : d ⬝ᵥ vK K ones9L = 0) :
    d = (d ⟨k0, hk0⟩ / rho K v ⟨k0, hk0⟩) • rho K v := by
  have hρK : rho K v ⟨k0, hk0⟩ ≠ 0 := by rw [rho_apply]; exact_mod_cast hρ
  set c := d ⟨k0, hk0⟩ / rho K v ⟨k0, hk0⟩ with hcd
  refine sub_eq_zero.mp (cert_zero C.X C.N C.No C.D C.pm hc (d - c • rho K v) (fun t ht => ?_) ?_ (fun i hi => ?_))
  · rw [sub_dotProduct, hd t ht, smul_dotProduct, rho_dot, hX t ht, Int.cast_zero, smul_zero, sub_zero]
  · rw [sub_dotProduct, h1, smul_dotProduct, rho_ones hv, smul_zero, sub_zero]
  · have e : i = ⟨k0, hk0⟩ := Fin.ext (hpiv i hi)
    subst e
    simp only [Pi.sub_apply, Pi.smul_apply, smul_eq_mul, hcd]
    rw [div_mul_cancel₀ _ hρK, sub_self]

theorem pair_of_cert (C : RCert) (hc : certOK C.X C.N C.No C.D C.pm = true) {v w k0 k1 : ℕ} (hv : v < 104)
    (hw : w < 104) (hk0 : k0 < 9) (hk1 : k1 < 9)
    (hpiv : ∀ i : Fin 9, C.pm.testBit i = true → (i : ℕ) = k0 ∨ (i : ℕ) = k1)
    (hdet : (root v).getD k0 0 * (root w).getD k1 0 - (root v).getD k1 0 * (root w).getD k0 0 ≠ 0)
    (hX : ∀ t < C.X.length, dot v (C.X.getD t 0) = 0 ∧ dot w (C.X.getD t 0) = 0) (d : Fin 9 → K)
    (hd : ∀ t < C.X.length, d ⬝ᵥ rho K (C.X.getD t 0) = 0) (h1 : d ⬝ᵥ vK K ones9L = 0) :
    ∃ a b : K, d = a • rho K v + b • rho K w := by
  set v0 := rho K v ⟨k0, hk0⟩ with hv0
  set v1 := rho K v ⟨k1, hk1⟩ with hv1
  set w0 := rho K w ⟨k0, hk0⟩ with hw0
  set w1 := rho K w ⟨k1, hk1⟩ with hw1
  set d0 := d ⟨k0, hk0⟩ with hd0
  set d1 := d ⟨k1, hk1⟩ with hd1
  have hdetK : v0 * w1 - v1 * w0 ≠ 0 := by
    rw [hv0, hv1, hw0, hw1, rho_apply, rho_apply, rho_apply, rho_apply]
    exact_mod_cast hdet
  have hz : d - ((d0 * w1 - d1 * w0) / (v0 * w1 - v1 * w0)) • rho K v -
      ((v0 * d1 - v1 * d0) / (v0 * w1 - v1 * w0)) • rho K w = 0 := by
    refine cert_zero C.X C.N C.No C.D C.pm hc _ (fun t ht => ?_) ?_ (fun i hi => ?_)
    · rw [sub_dotProduct, sub_dotProduct, hd t ht, smul_dotProduct, smul_dotProduct, rho_dot, rho_dot,
        (hX t ht).1, (hX t ht).2, Int.cast_zero, smul_zero, smul_zero, sub_zero, sub_zero]
    · rw [sub_dotProduct, sub_dotProduct, h1, smul_dotProduct, smul_dotProduct, rho_ones hv, rho_ones hw,
        smul_zero, smul_zero, sub_zero, sub_zero]
    · rcases hpiv i hi with e | e
      · have e' : i = ⟨k0, hk0⟩ := Fin.ext e
        rw [e']
        simp only [Pi.sub_apply, Pi.smul_apply, smul_eq_mul]
        rw [← hv0, ← hw0, ← hd0, div_mul_eq_mul_div, div_mul_eq_mul_div, sub_sub, sub_eq_zero, eq_comm,
          ← add_div, div_eq_iff hdetK]
        ring
      · have e' : i = ⟨k1, hk1⟩ := Fin.ext e
        rw [e']
        simp only [Pi.sub_apply, Pi.smul_apply, smul_eq_mul]
        rw [← hv1, ← hw1, ← hd1, div_mul_eq_mul_div, div_mul_eq_mul_div, sub_sub, sub_eq_zero, eq_comm,
          ← add_div, div_eq_iff hdetK]
        ring
  rw [sub_sub] at hz
  exact ⟨_, _, sub_eq_zero.mp hz⟩

end RankNine
