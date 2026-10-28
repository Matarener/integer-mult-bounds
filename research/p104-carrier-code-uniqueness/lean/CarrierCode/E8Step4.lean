import CarrierCode.E8Step3
import CarrierCode.E8Defs4

/-!
# Step 4: symmetry and A2 triangles kill `v_t`

From step 3 and the symmetry of `N`, `r_x ⬝ v_t = r_t ⬝ v_x` for non-orthogonal ports.  Along an A2 triangle this
forces `r_x ⬝ v_t = 0` (`a2_gen`), and the checked spanning triangles give `v_t = 0`.  Hence `N t x = 1`, so `M` is
symmetric and `M t x = ±1` for every non-orthogonal pair.
-/

namespace CarrierCode.E8

open Matrix

variable {M : Matrix ι ι (ZMod 3)} {A : Matrix ι (Fin 8) (ZMod 3)} {B : Matrix (Fin 8) ι (ZMod 3)}

/-- The checks of steps 1–3 (proved by the kernel in `E8Checks.lean`). -/
def Checks3 : Prop := framesOK ∧ ∀ t : ι, seedOK t.val ∧ ∀ x : ι, check3 t.val x.val

theorem step3' (h : Hyp M A B) (hC : Checks3) (t x : ι) (hnz : dotN t x % 3 ≠ 0) :
    Nm M t x = 1 + Gm t x * (r x ⬝ᵥ vv M t) := step3 h hC.1 hC.2 t x hnz

theorem two_mul_ne (a b : ZMod 3) (ha : a ≠ 0) (hb : b ≠ 0) : 2 * a * b ≠ 0 := by
  revert a b; decide

/-- The A2 trick for a general triangle `r_y = a r_t + b r_x` in characteristic 3. -/
theorem a2_gen {n : Type*} [Fintype n] (rt rx ry vt vx vy : n → ZMod 3) (a b : ZMod 3) (ha : a ≠ 0) (hb : b ≠ 0)
    (hy : ry = a • rt + b • rx) (ht : rt ⬝ᵥ vt = 0) (hx : rx ⬝ᵥ vx = 0) (hyy : ry ⬝ᵥ vy = 0)
    (stx : rx ⬝ᵥ vt = rt ⬝ᵥ vx) (sty : ry ⬝ᵥ vt = rt ⬝ᵥ vy) (sxy : rx ⬝ᵥ vy = ry ⬝ᵥ vx) :
    rx ⬝ᵥ vt = 0 := by
  have e1 : ry ⬝ᵥ vt = b * (rx ⬝ᵥ vt) := by
    rw [hy, add_dotProduct, smul_dotProduct, smul_dotProduct, ht, smul_eq_mul, smul_eq_mul, mul_zero, zero_add]
  have e2 : ry ⬝ᵥ vx = a * (rx ⬝ᵥ vt) := by
    rw [hy, add_dotProduct, smul_dotProduct, smul_dotProduct, hx, smul_eq_mul, smul_eq_mul, mul_zero, add_zero, stx]
  have e3 : ry ⬝ᵥ vy = a * (rt ⬝ᵥ vy) + b * (rx ⬝ᵥ vy) := by
    rw [hy, add_dotProduct, smul_dotProduct, smul_dotProduct, smul_eq_mul, smul_eq_mul]
  rw [← sty, sxy, e1, e2, hyy] at e3
  have key : (2 * a * b) * (rx ⬝ᵥ vt) = 0 := by linear_combination -e3
  exact (mul_eq_zero.mp key).resolve_left (two_mul_ne a b ha hb)

theorem dotN_comm (i j : ℕ) : dotN i j = dotN j i := by
  simp only [dotN, dotW, rv, rL]; ring

theorem Gm_ne {t x : ι} (hnz : dotN t x % 3 ≠ 0) : Gm t x ≠ 0 := by
  rw [Gm, ← dotN_cast]; exact fun e => hnz ((cast_eq_zero_iff _).mp e)

/-- (4) of E8-PROOF.md. -/
theorem symm_rel (h : Hyp M A B) (hC : Checks3) {t x : ι} (hnz : dotN t x % 3 ≠ 0) :
    r x ⬝ᵥ vv M t = r t ⬝ᵥ vv M x := by
  have e1 := step3' h hC t x hnz
  have e2 := step3' h hC x t (by rwa [dotN_comm])
  have hN : Nm M t x = Nm M x t := mul_comm _ _
  rw [e1, e2, Gm_comm x t] at hN
  exact mul_left_cancel₀ (Gm_ne hnz) (add_left_cancel hN)

theorem rv_vec (i : ℕ) (k : Fin 8) : ((rv i k : ℕ) : ZMod 3) = r i k := rfl

theorem tri_vec {t i : ℕ} (hT : tri4 t i) :
    r (ay t i) = ((aa t i : ℕ) : ZMod 3) • r t + ((ab t i : ℕ) : ZMod 3) • r (ax t i) := by
  funext k
  have e := hT.2.2.2.2.2.2.2 k
  have e' := congrArg (fun n : ℕ => (n : ZMod 3)) e
  simp only [cast_mod] at e'
  push_cast at e'
  simp only [Pi.add_apply, Pi.smul_apply, smul_eq_mul]
  rw [rv_vec, rv_vec, rv_vec] at e'
  have h3 : (3 : ZMod 3) = 0 := by decide
  linear_combination e' - (r t k * (aa t i : ZMod 3) + r (ax t i) k * (ab t i : ZMod 3)) * h3

theorem unit3 {n : ℕ} (h : n = 1 ∨ n = 2) : ((n : ℕ) : ZMod 3) ≠ 0 := by
  rcases h with rfl | rfl <;> decide

theorem vv_self (hC : Checks3) (u : ι) : r u ⬝ᵥ vv M u = 0 := rt_dot_vv (hC.2 u).1

/-- Every row `r_x` of the spanning set is orthogonal to `v_t`. -/
theorem row_dot_vv (h : Hyp M A B) (hC : Checks3) (h4 : step4OK) (t : ι) (i : Fin 7) :
    r (ax t i) ⬝ᵥ vv M t = 0 := by
  have hT := (h4 t).1 i
  obtain ⟨hx, hy, htx, hty, hxy, ha, hb, -⟩ := (h4 t).1 i
  have ex : ((toι (ax t i) : ι) : ℕ) = ax t i := toι_val hx
  have ey : ((toι (ay t i) : ι) : ℕ) = ay t i := toι_val hy
  have stx := symm_rel h hC (t := t) (x := toι (ax t i)) (by rwa [ex])
  have sty := symm_rel h hC (t := t) (x := toι (ay t i)) (by rwa [ey])
  have sxy := symm_rel h hC (t := toι (ay t i)) (x := toι (ax t i)) (by rw [ex, ey, dotN_comm]; exact hxy)
  have vx := vv_self (M := M) hC (toι (ax t i))
  have vy := vv_self (M := M) hC (toι (ay t i))
  rw [ex] at stx sxy vx
  rw [ey] at sty sxy vy
  exact a2_gen (r t) (r (ax t i)) (r (ay t i)) (vv M t) (vv M (toι (ax t i))) (vv M (toι (ay t i)))
    _ _ (unit3 ha) (unit3 hb) (tri_vec hT) (vv_self hC t) vx vy stx sty sxy

theorem sum_range8 (g : ℕ → ℕ) : (((List.range 8).map g).sum : ℕ) = ∑ j : Fin 8, g j := by
  simp [List.sum_range_succ, Fin.sum_univ_eight]

/-- Step 4: `v_t = 0`. -/
theorem vv_zero (h : Hyp M A B) (hC : Checks3) (h4 : step4OK) (t : ι) : vv M t = 0 := by
  have hrow : ∀ i : Fin 8, vec (rowL t i) ⬝ᵥ vv M t = 0 := by
    intro i
    by_cases hi : (i : ℕ) = 0
    · simp only [rowL, if_pos hi]; exact vv_self hC t
    · simp only [rowL, if_neg hi]
      have := row_dot_vv h hC h4 t ⟨i - 1, by omega⟩
      exact this
  funext k
  have hinv : ∀ l : Fin 8, ∑ i : Fin 8, ((cL t k i : ℕ) : ZMod 3) * vec (rowL t i) l = if k = l then 1 else 0 := by
    intro l
    have e := (h4 t).2 k l
    rw [sum_range8] at e
    have e' := congrArg (fun n : ℕ => (n : ZMod 3)) e
    simp only [cast_mod] at e'
    push_cast at e'
    exact e'
  calc vv M t k = ∑ l : Fin 8, (if k = l then (1 : ZMod 3) else 0) * vv M t l := by simp
    _ = ∑ l : Fin 8, ∑ i : Fin 8, ((cL t k i : ℕ) : ZMod 3) * vec (rowL t i) l * vv M t l := by
        simp_rw [← hinv, Finset.sum_mul]
    _ = ∑ i : Fin 8, ((cL t k i : ℕ) : ZMod 3) * (vec (rowL t i) ⬝ᵥ vv M t) := by
        rw [Finset.sum_comm]; simp only [dotProduct, Finset.mul_sum, mul_assoc]
    _ = 0 := by simp [hrow]

/-- After step 4: `N t x = 1` for non-orthogonal pairs. -/
theorem N_one (h : Hyp M A B) (hC : Checks3) (h4 : step4OK) {t x : ι} (hnz : dotN t x % 3 ≠ 0) : Nm M t x = 1 := by
  rw [step3' h hC t x hnz, vv_zero h hC h4, dotProduct_zero, mul_zero, add_zero]

/-- (5) of E8-PROOF.md: `M` is symmetric and `M t x = ±1` off the conflict pattern. -/
theorem M_symm_pm (h : Hyp M A B) (hC : Checks3) (h4 : step4OK) {t x : ι} (hnz : dotN t x % 3 ≠ 0) :
    M x t = M t x ∧ M t x * M t x = 1 := by
  have e := N_one h hC h4 hnz
  simp only [Nm] at e
  generalize M t x = a at e ⊢
  generalize M x t = b at e ⊢
  revert a b; decide

end CarrierCode.E8
