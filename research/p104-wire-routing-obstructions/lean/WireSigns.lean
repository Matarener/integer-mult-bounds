/-
Wire sign lemmas for P104 ports seen as E8 root lines (norm 2, inner products in {0, ±1} off the diagonal).
(1) third_root_or_sign: for roots r_k, r_i with <r_k,r_i> = c = ±1 and a reader root r_j with <r_j,r_k>, <r_j,r_i> = ±1,
    either r_j = ±(r_k - c r_i) (the third root of their A2), or <r_j,r_k> * <r_j,r_i> = c.
(2) triangle_iff: for three roots with pairwise inner products a, b, c in {±1}
    (a = <r_k,r_m>, b = <r_m,r_i>, c = <r_k,r_i>), a*b*c = -1 iff r_i = c r_k + b r_m.
Apache-2.0.
-/
import Mathlib

open RealInnerProductSpace

variable {E : Type*} [NormedAddCommGroup E] [InnerProductSpace ℝ E]

lemma pm_one_sq {x : ℝ} (h : x = 1 ∨ x = -1) : x * x = 1 := by
  rcases h with h | h <;> subst h <;> norm_num

theorem third_root_or_sign (rj rk ri : E)
    (hj : ⟪rj, rj⟫ = 2) (hk : ⟪rk, rk⟫ = 2) (hi : ⟪ri, ri⟫ = 2)
    (c : ℝ) (hc : c = 1 ∨ c = -1) (hki : ⟪rk, ri⟫ = c)
    (hjk : ⟪rj, rk⟫ = 1 ∨ ⟪rj, rk⟫ = -1) (hji : ⟪rj, ri⟫ = 1 ∨ ⟪rj, ri⟫ = -1) :
    rj = rk - c • ri ∨ rj = -(rk - c • ri) ∨ ⟪rj, rk⟫ * ⟪rj, ri⟫ = c := by
  have hc2 := pm_one_sq hc
  have hik : ⟪ri, rk⟫ = c := by rw [real_inner_comm]; exact hki
  have hkj : ⟪rk, rj⟫ = ⟪rj, rk⟫ := real_inner_comm _ _
  have hij : ⟪ri, rj⟫ = ⟪rj, ri⟫ := real_inner_comm _ _
  -- squared distances to the third root t = rk - c ri and to -t
  have e1 : ⟪rj - (rk - c • ri), rj - (rk - c • ri)⟫ = 4 - 2 * (⟪rj, rk⟫ - c * ⟪rj, ri⟫) := by
    simp only [inner_sub_left, inner_sub_right, real_inner_smul_left, real_inner_smul_right, hj, hk, hi, hki, hik, hkj, hij]
    ring
  have e2 : ⟪rj + (rk - c • ri), rj + (rk - c • ri)⟫ = 4 + 2 * (⟪rj, rk⟫ - c * ⟪rj, ri⟫) := by
    simp only [inner_add_left, inner_add_right, inner_sub_left, inner_sub_right, real_inner_smul_left,
      real_inner_smul_right, hj, hk, hi, hki, hik, hkj, hij]
    ring
  have key : (⟪rj, rk⟫ - c * ⟪rj, ri⟫) = 2 ∨ (⟪rj, rk⟫ - c * ⟪rj, ri⟫) = -2 ∨ ⟪rj, rk⟫ * ⟪rj, ri⟫ = c := by
    rcases hjk with hx | hx <;> rcases hji with hy | hy <;> rcases hc with hcv | hcv <;>
      rw [hx, hy, hcv] <;> norm_num
  rcases key with h | h | h
  · left
    have h0 : ⟪rj - (rk - c • ri), rj - (rk - c • ri)⟫ = 0 := by rw [e1, h]; norm_num
    exact sub_eq_zero.mp ((inner_self_eq_zero (𝕜 := ℝ)).mp h0)
  · right; left
    have h0 : ⟪rj + (rk - c • ri), rj + (rk - c • ri)⟫ = 0 := by rw [e2, h]; norm_num
    exact eq_neg_of_add_eq_zero_left ((inner_self_eq_zero (𝕜 := ℝ)).mp h0)
  · right; right; exact h

theorem triangle_iff (rk rm ri : E)
    (hk : ⟪rk, rk⟫ = 2) (hm : ⟪rm, rm⟫ = 2) (hi : ⟪ri, ri⟫ = 2)
    (a b c : ℝ) (ha : a = 1 ∨ a = -1) (hb : b = 1 ∨ b = -1) (hc : c = 1 ∨ c = -1)
    (hkm : ⟪rk, rm⟫ = a) (hmi : ⟪rm, ri⟫ = b) (hki : ⟪rk, ri⟫ = c) :
    a * b * c = -1 ↔ ri = c • rk + b • rm := by
  have ha2 := pm_one_sq ha; have hb2 := pm_one_sq hb; have hc2 := pm_one_sq hc
  have hmk : ⟪rm, rk⟫ = a := by rw [real_inner_comm]; exact hkm
  have him : ⟪ri, rm⟫ = b := by rw [real_inner_comm]; exact hmi
  have hik : ⟪ri, rk⟫ = c := by rw [real_inner_comm]; exact hki
  -- squared distance from ri to c rk + b rm equals 2 + 2abc
  have hd : ⟪ri - (c • rk + b • rm), ri - (c • rk + b • rm)⟫ = 2 + 2 * (a * b * c) := by
    simp only [inner_sub_left, inner_sub_right, inner_add_left, inner_add_right, real_inner_smul_left,
      real_inner_smul_right, hk, hm, hi, hkm, hmk, hmi, him, hki, hik]
    nlinarith [ha2, hb2, hc2]
  constructor
  · intro h
    rw [← sub_eq_zero, ← inner_self_eq_zero (𝕜 := ℝ), hd, h]; norm_num
  · intro h
    have : ⟪ri - (c • rk + b • rm), ri - (c • rk + b • rm)⟫ = 0 := by rw [h]; simp
    linarith [hd]
