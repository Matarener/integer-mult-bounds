import Mathlib.Data.Matrix.Mul
import Mathlib.Data.ZMod.Basic
import Mathlib.Algebra.CharP.Two

/-! The semidirect inverse only; physical tape/cost claims are informal. -/
namespace QQ16CoverRoute
theorem semidirect_pull_push (n l : Nat) (g h : Matrix (Fin n) (Fin n) (ZMod 2)) (hg : h * g = 1) (delta : Fin n → ZMod 2) (e : Matrix (Fin n) (Fin n) (ZMod 2)) (w : Fin l → Fin n → ZMod 2) : ((e * h) * g = e) ∧ (∀ j, (w j + e.mulVec (h.mulVec delta)) + (e * h).mulVec delta = w j) := by
  constructor
  · rw [mul_assoc, hg, mul_one]
  · intro j
    rw [Matrix.mulVec_mulVec]
    funext i
    change (w j i + (e * h).mulVec delta i) + (e * h).mulVec delta i = w j i
    rw [add_assoc, CharTwo.add_self_eq_zero, add_zero]

end QQ16CoverRoute
