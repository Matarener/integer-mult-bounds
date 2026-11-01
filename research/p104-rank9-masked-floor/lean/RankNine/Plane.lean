import RankNine.Lin

/-!
# A2 planes hold at most three lines

Distinct lines of P104 have dot products `0, ±9` (`dot_vals`).  If `gram3 v x y = 0` then the three dot products are
`±9` with product `-729`, and over `ℚ` (norm argument) `ρ_y = (ρ_v·ρ_y / 9) ρ_v + (ρ_x·ρ_y / 9) ρ_x`.  Two such lines
`y ≠ z` for the same pair `v, x` would have `ρ_y·ρ_z = ±18`, impossible (`plane_unique`).
-/

namespace RankNine

open Matrix

def dotValsOK : Bool := (List.range 104).all fun a => (List.range 104).all fun b =>
  a == b || dot a b == 0 || dot a b == 9 || dot a b == -9

theorem dotVals_ok : dotValsOK = true := by decide +kernel

theorem dot_vals {a b : ℕ} (ha : a < 104) (hb : b < 104) (hab : a ≠ b) :
    dot a b = 0 ∨ dot a b = 9 ∨ dot a b = -9 := by
  have h := dotVals_ok
  simp only [dotValsOK, List.all_eq_true, List.mem_range, Bool.or_eq_true, beq_iff_eq] at h
  have := h a ha b hb
  omega

theorem a2_vals {a b c : ℤ} (ha : a = 0 ∨ a = 9 ∨ a = -9) (hb : b = 0 ∨ b = 9 ∨ b = -9)
    (hc : c = 0 ∨ c = 9 ∨ c = -9) (h : 5832 + 2 * a * b * c - 18 * (a * a + b * b + c * c) = 0) :
    a * a = 81 ∧ b * b = 81 ∧ c * c = 81 ∧ a * b * c = -729 := by
  rcases ha with rfl | rfl | rfl <;> rcases hb with rfl | rfl | rfl <;> rcases hc with rfl | rfl | rfl <;>
    omega

theorem plane_arith {a b c b' c' d : ℤ} (ha : a = 9 ∨ a = -9) (hb : b = 9 ∨ b = -9) (hc : c = 9 ∨ c = -9)
    (hb' : b' = 9 ∨ b' = -9) (hc' : c' = 9 ∨ c' = -9) (hd : d = 0 ∨ d = 9 ∨ d = -9) (h1 : a * b * c = -729)
    (h2 : a * b' * c' = -729) (h : 81 * d = 18 * b * b' + a * (b * c' + c * b') + 18 * c * c') : False := by
  rcases ha with rfl | rfl <;> rcases hb with rfl | rfl <;> rcases hc with rfl | rfl <;>
    rcases hb' with rfl | rfl <;> rcases hc' with rfl | rfl <;> rcases hd with rfl | rfl | rfl <;>
    omega

theorem pm9 {a : ℤ} (h0 : a = 0 ∨ a = 9 ∨ a = -9) (h : a * a = 81) : a = 9 ∨ a = -9 := by
  rcases h0 with rfl | h0 | h0
  · norm_num at h
  · exact Or.inl h0
  · exact Or.inr h0

/-- an A2 triple: `ρ_y` in the plane of `ρ_v, ρ_x` (over `ℚ`) -/
theorem a2_span {v x y : ℕ} (hv : v < 104) (hx : x < 104) (hy : y < 104) (hvx : v ≠ x) (hyv : y ≠ v)
    (hyx : y ≠ x) (h : gram3 v x y = 0) :
    rho ℚ y = (((dot v y : ℤ) : ℚ) / 9) • rho ℚ v + (((dot x y : ℤ) : ℚ) / 9) • rho ℚ x ∧
      dot v x * dot v y * dot x y = -729 ∧ dot v x * dot v x = 81 ∧ dot v y * dot v y = 81 ∧
      dot x y * dot x y = 81 := by
  unfold gram3 at h
  obtain ⟨h1, h2, h3, h4⟩ := a2_vals (dot_vals hv hx hvx) (dot_vals hv hy (Ne.symm hyv))
    (dot_vals hx hy (Ne.symm hyx)) h
  refine ⟨?_, h4, h1, h2, h3⟩
  set w := rho ℚ y - (((dot v y : ℤ) : ℚ) / 9) • rho ℚ v - (((dot x y : ℤ) : ℚ) / 9) • rho ℚ x with hw
  have hww : w ⬝ᵥ w = 0 := by
    rw [hw]
    simp only [sub_dotProduct, dotProduct_sub, smul_dotProduct, dotProduct_smul, smul_eq_mul, rho_dot]
    rw [dot_self hv, dot_self hx, dot_self hy, dot_comm y v, dot_comm y x, dot_comm x v]
    have h4Q : ((dot v x : ℤ) : ℚ) * ((dot v y : ℤ) : ℚ) * ((dot x y : ℤ) : ℚ) = -729 := by exact_mod_cast h4
    push_cast
    linear_combination (2 / 81 : ℚ) * h4Q
  have hw0 : w = 0 := dotProduct_self_eq_zero.mp hww
  rw [hw, sub_sub, sub_eq_zero] at hw0
  exact hw0

theorem plane_unique {v x y z : ℕ} (hv : v < 104) (hx : x < 104) (hy : y < 104) (hz : z < 104) (hvx : v ≠ x)
    (hyv : y ≠ v) (hyx : y ≠ x) (hzv : z ≠ v) (hzx : z ≠ x) (hyz : y ≠ z) (h1 : gram3 v x y = 0)
    (h2 : gram3 v x z = 0) : False := by
  obtain ⟨ey, ay1, ay2, ay3, ay4⟩ := a2_span hv hx hy hvx hyv hyx h1
  obtain ⟨ez, az1, -, az3, az4⟩ := a2_span hv hx hz hvx hzv hzx h2
  have hd := (rho_dot (K := ℚ) y z).symm
  rw [ey, ez] at hd
  simp only [add_dotProduct, dotProduct_add, smul_dotProduct, dotProduct_smul, smul_eq_mul, rho_dot] at hd
  rw [dot_self hv, dot_self hx, dot_comm x v] at hd
  have hZ : 81 * dot y z = 18 * dot v y * dot v z + dot v x * (dot v y * dot x z + dot x y * dot v z) +
      18 * dot x y * dot x z := by
    have : ((81 * dot y z : ℤ) : ℚ) = ((18 * dot v y * dot v z + dot v x * (dot v y * dot x z + dot x y * dot v z) +
        18 * dot x y * dot x z : ℤ) : ℚ) := by
      push_cast
      linear_combination (81 : ℚ) * hd
    exact_mod_cast this
  exact plane_arith (pm9 (dot_vals hv hx hvx) ay2) (pm9 (dot_vals hv hy (Ne.symm hyv)) ay3)
    (pm9 (dot_vals hx hy (Ne.symm hyx)) ay4) (pm9 (dot_vals hv hz (Ne.symm hzv)) az3)
    (pm9 (dot_vals hx hz (Ne.symm hzx)) az4) (dot_vals hy hz hyz) ay1 az1 hZ

end RankNine
