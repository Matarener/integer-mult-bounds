import BForm.Rank

/-!
# B. Normal form of a square decoder of `M = X Yᵀ`

If `M = X * Yᵀ = P * Qᵀ`, where `X, Y` have left inverses (full column rank `r`) and `P, Q` have the same number `r`
of columns, then `U := Xl * P`, `W := Yl * Q` satisfy `P = X * U`, `Q = Y * W`, `U * Wᵀ = 1`.
For the B-form, `X = [D₁R, c]`, `Y = [D₂R, β]` and `r = 9` (BFORM2 Lemma 1).
-/

namespace BForm

open Matrix

variable {F : Type*} [Field F] {L r : Type*} [Fintype L] [Fintype r] [DecidableEq r]

theorem normal_form (X Y P Q : Matrix L r F) (Xl Yl : Matrix r L F)
    (hX : Xl * X = 1) (hY : Yl * Y = 1) (h : X * Yᵀ = P * Qᵀ) :
    (Xl * P) * (Yl * Q)ᵀ = 1 ∧ P = X * (Xl * P) ∧ Q = Y * (Yl * Q) := by
  set U := Xl * P
  set W := Yl * Q
  have hUW : U * Wᵀ = 1 := by
    have : Xl * (X * Yᵀ) * Ylᵀ = 1 := by
      rw [← Matrix.mul_assoc, hX, Matrix.one_mul, ← Matrix.transpose_mul, hY, Matrix.transpose_one]
    rw [h] at this
    simpa [U, W, Matrix.transpose_mul, Matrix.mul_assoc] using this
  have hWU : Wᵀ * U = 1 := mul_eq_one_comm.mp hUW
  -- `X = P * Wᵀ` and `Y = Q * Uᵀ`
  have hXP : X = P * Wᵀ := by
    have : X * Yᵀ * Ylᵀ = X := by
      rw [Matrix.mul_assoc, ← Matrix.transpose_mul, hY, Matrix.transpose_one, Matrix.mul_one]
    rw [← this, h]; simp [W, Matrix.transpose_mul, Matrix.mul_assoc]
  have hYQ : Y = Q * Uᵀ := by
    have h' : Y * Xᵀ = Q * Pᵀ := by
      have := congrArg Matrix.transpose h
      simpa [Matrix.transpose_mul] using this
    have : Y * Xᵀ * Xlᵀ = Y := by
      rw [Matrix.mul_assoc, ← Matrix.transpose_mul, hX, Matrix.transpose_one, Matrix.mul_one]
    rw [← this, h']; simp [U, Matrix.transpose_mul, Matrix.mul_assoc]
  refine ⟨hUW, ?_, ?_⟩
  · rw [hXP, Matrix.mul_assoc, hWU, Matrix.mul_one]
  · have hUW' : Uᵀ * W = 1 := by
      have := congrArg Matrix.transpose hWU
      simpa [Matrix.transpose_mul] using this
    rw [hYQ, Matrix.mul_assoc, hUW', Matrix.mul_one]

end BForm
