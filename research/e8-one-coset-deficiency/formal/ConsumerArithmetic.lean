/-
Copyright (c) 2026 conorholds. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Prepared with substantial OpenAI Codex assistance.
-/
import Init

/-!
# Arithmetic of the final deficiency consumer

This proves only the natural-number consequence of the two displayed budget
inequalities. It does not derive either premise from ranks or E8 geometry.
-/

namespace OneCosetDeficiency

/-- A ninefold budget and deficiency at least eight force at least 72 COPY
units. Both inequalities are explicit premises; no geometric assembly is
asserted here. -/
theorem copy_ge_seventy_two (COPY m s t : Nat)
    (hbudget : 9 * m ≤ COPY + 9 * s + 9 * t)
    (hdeficiency : 8 + s + t ≤ m) : 72 ≤ COPY := by
  have hscaled := Nat.mul_le_mul_left 9 hdeficiency
  rw [Nat.mul_add, Nat.mul_add] at hscaled
  change 72 + 9 * s + 9 * t ≤ 9 * m at hscaled
  have hcombined := Nat.le_trans hscaled hbudget
  exact Nat.le_of_add_le_add_right (Nat.le_of_add_le_add_right hcombined)

#print axioms copy_ge_seventy_two

end OneCosetDeficiency
