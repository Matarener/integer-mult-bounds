import Mathlib.Algebra.Order.Archimedean.Real.Basic
import Mathlib.Algebra.Order.Floor.Ring
import Mathlib.Data.Real.Basic
import Mathlib.Tactic.Linarith
import Mathlib.Tactic.Ring

/-!
Strict half-unit recovery and a shared butterfly endpoint.
This module proves local algebra/recovery only; the fixed-point FFT propagation
and the executable certificate are separate artifacts, not kernel-checked here.
-/
namespace Mathproof.IntegerKernelRecovery20261024

/-- A strict half-unit error recovers the intended integer under floor(x+1/2).
The strict inequality rules out tie dependence. -/
theorem recover_integer_of_strict_half (x : ℝ) (z : ℤ)
    (h : |x - (z : ℝ)| < 1 / 2) :
    Int.floor (x + 1 / 2) = z := by
  apply Int.floor_eq_iff.mpr
  rcases abs_lt.mp h with ⟨hl, hu⟩
  constructor <;> linarith

/-- A shared product computes both outputs, for every commutative ring. -/
theorem shared_butterfly {R : Type*} [CommRing R] (u v w : R) :
    let t := w * v
    (u + t, u - t) = (u + w * v, u - w * v) := by
  rfl

/-- No division or characteristic assumption is hidden in the sum law. -/
theorem butterfly_sum {R : Type*} [CommRing R] (u v w : R) :
    (u + w * v) + (u - w * v) = 2 * u := by
  ring

/-- The corresponding difference law preserves the one shared product. -/
theorem butterfly_difference {R : Type*} [CommRing R] (u v w : R) :
    (u + w * v) - (u - w * v) = 2 * (w * v) := by
  ring

end Mathproof.IntegerKernelRecovery20261024
