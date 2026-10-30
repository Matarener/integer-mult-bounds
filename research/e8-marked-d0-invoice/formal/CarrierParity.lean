/-
Copyright (c) 2026 conorholds. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Prepared with substantial OpenAI Codex assistance.
-/
import Mathlib.Data.ZMod.Defs
import Mathlib.LinearAlgebra.BilinearMap

/-!
# A carrier triple cannot contain the indicated pure swap

The quadratic function and its bilinear polar companion are actual data.
Their polarization identity is an explicit hypothesis; homogeneity of the
quadratic function is not needed by this obstruction. This avoids importing
the uncached quadratic-form modules or asserting an E8 instantiation.

If `z = a + b + u`, all four labels have quadratic value one, `a,b` have
polar pairing one, and `u` has polar pairing zero with both, the quadratic
value of `z` is instead zero. The final theorem obtains these polar pairings
from an augmented bilinear pairing `beta`, a leading linear functional,
and their exact compatibility identity.

For the E8 application, the conversion from real root evaluations to the
displayed binary `beta` values, and the carrier's XOR identity, remain
external hypotheses. No carrier enumeration or decoder invoice is proved.
-/

noncomputable section

namespace CarrierParity

abbrev F₂ := ZMod 2

variable {V : Type*} [AddCommGroup V] [Module F₂ V]

/-- Expand the quadratic value of three labels using the actual bilinear
polar companion. The parenthesization records the two applications of
polarization and the bilinear expansion, without arithmetic automation. -/
theorem quadratic_three_sum (Q : V → F₂) (B : LinearMap.BilinForm F₂ V)
    (polar : ∀ x y, Q (x + y) = Q x + Q y + B x y) (a b u : V) :
    Q (a + b + u) = (Q a + Q b + B a b) + Q u + (B a u + B b u) := by
  rw [polar (a + b) u, polar a b]
  simp only [map_add, LinearMap.add_apply]

/-- The three-root/XOR parity obstruction used when one carrier is
supplemented by a unit-supported vector. All root and frame quadratic
values and all three required polar pairings are explicit hypotheses. -/
theorem carrier3_unit_parity (Q : V → F₂) (B : LinearMap.BilinForm F₂ V)
    (polar : ∀ x y, Q (x + y) = Q x + Q y + B x y)
    (a b u z : V)
    (qa : Q a = 1) (qb : Q b = 1) (qu : Q u = 1) (qz : Q z = 1)
    (xor_relation : z = a + b + u)
    (ab : B a b = 1) (au : B a u = 0) (bu : B b u = 0) : False := by
  have qz_zero : Q z = 0 := by
    rw [xor_relation, quadratic_three_sum Q B polar, qa, qb, qu, ab, au, bu]
    decide
  have one_zero : (1 : F₂) = 0 := qz.symm.trans qz_zero
  exact (by decide : (1 : F₂) ≠ 0) one_zero

/-- Recover the polar pairing from the augmented pairing on leading-one
labels. A zero augmented pairing gives polar value one, and augmented
value one gives polar value zero. -/
theorem polar_values_from_augmented_pairing
    (B beta : LinearMap.BilinForm F₂ V) (leading : V →ₗ[F₂] F₂)
    (compatible : ∀ x y, beta x y = leading x * leading y + B x y)
    (a b u : V)
    (la : leading a = 1) (lb : leading b = 1) (lu : leading u = 1)
    (ab : beta a b = 0) (au : beta a u = 1) (bu : beta b u = 1) :
    B a b = 1 ∧ B a u = 0 ∧ B b u = 0 := by
  have hab : (1 : F₂) + B a b = 0 := by
    simpa only [la, lb, one_mul] using (compatible a b).symm.trans ab
  have hau : (1 : F₂) + B a u = 1 := by
    simpa only [la, lu, one_mul] using (compatible a u).symm.trans au
  have hbu : (1 : F₂) + B b u = 1 := by
    simpa only [lb, lu, one_mul] using (compatible b u).symm.trans bu
  refine ⟨?_, ?_, ?_⟩
  · apply add_left_cancel (a := (1 : F₂))
    exact hab.trans (by decide : (0 : F₂) = 1 + 1)
  · apply add_left_cancel (a := (1 : F₂))
    simpa only [add_zero] using hau
  · apply add_left_cancel (a := (1 : F₂))
    simpa only [add_zero] using hbu

/-- The same obstruction with the E8-style augmented-pairing hypotheses.
The root-label/nonzero-evaluation bridge itself is not assumed silently. -/
theorem carrier3_unit_parity_from_augmented_pairing
    (Q : V → F₂) (B beta : LinearMap.BilinForm F₂ V)
    (leading : V →ₗ[F₂] F₂)
    (polar : ∀ x y, Q (x + y) = Q x + Q y + B x y)
    (compatible : ∀ x y, beta x y = leading x * leading y + B x y)
    (a b u z : V)
    (qa : Q a = 1) (qb : Q b = 1) (qu : Q u = 1) (qz : Q z = 1)
    (xor_relation : z = a + b + u)
    (la : leading a = 1) (lb : leading b = 1) (lu : leading u = 1)
    (ab : beta a b = 0) (au : beta a u = 1) (bu : beta b u = 1) : False := by
  obtain ⟨hab, hau, hbu⟩ := polar_values_from_augmented_pairing
    B beta leading compatible a b u la lb lu ab au bu
  exact carrier3_unit_parity Q B polar a b u z qa qb qu qz xor_relation hab hau hbu

#print axioms carrier3_unit_parity
#print axioms polar_values_from_augmented_pairing
#print axioms carrier3_unit_parity_from_augmented_pairing

end CarrierParity
