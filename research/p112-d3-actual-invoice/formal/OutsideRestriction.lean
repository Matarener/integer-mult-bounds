/-
Copyright (c) 2026 conorholds. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Prepared with substantial OpenAI Codex assistance.
-/
import Init

/-!
# Restriction of actual outside duals to the code

This Init-only core proves the common additive-map deduction used in the
nonadapted d=3 invoice. If every vector is a sum of a code vector and an
inside-span vector, restriction to the code is injective on additive maps
annihilating the inside span. Actual outside-coordinate evaluations then
detect every coefficient of a relation that vanishes on the code.

The vector-space dimension argument giving C + L = S, the construction of
actual duals and finite scalar linear combinations, and their instantiation
by characteristic-zero linear maps remain outside this file. No E8 support,
frame, correction count, minimum basis, or adapted r=0 result is formalized.
-/

namespace NonadaptedD3

section AdditiveRestriction

variable {K V : Type} [Add K] [Add V]

/-- Agreement on two additively covering sets determines an additive map.
No subspace structure or scalar-field laws are needed for this step. -/
theorem additive_maps_equal_of_sum_cover
    (C L : V → Prop)
    (cover : ∀ v, ∃ c l, C c ∧ L l ∧ v = c + l)
    (f g : V → K)
    (f_add : ∀ x y, f (x + y) = f x + f y)
    (g_add : ∀ x y, g (x + y) = g x + g y)
    (agree_C : ∀ c, C c → f c = g c)
    (agree_L : ∀ l, L l → f l = g l) :
    f = g := by
  funext v
  rcases cover v with ⟨c, l, hc, hl, hv⟩
  calc
    f v = f c + f l := by rw [hv, f_add]
    _ = g c + g l := by rw [agree_C c hc, agree_L l hl]
    _ = g v := by rw [hv, g_add]

variable [Zero K]

/-- Restriction to C is injective among additive maps annihilating L,
provided C + L covers the ambient space. Applied to linear functionals,
this is the written proof's injectivity of Ann(L) → C*. -/
theorem restriction_injective_on_annihilator
    (C L : V → Prop)
    (cover : ∀ v, ∃ c l, C c ∧ L l ∧ v = c + l)
    (f g : V → K)
    (f_add : ∀ x y, f (x + y) = f x + f y)
    (g_add : ∀ x y, g (x + y) = g x + g y)
    (f_ann_L : ∀ l, L l → f l = 0)
    (g_ann_L : ∀ l, L l → g l = 0)
    (agree_C : ∀ c, C c → f c = g c) :
    f = g := by
  apply additive_maps_equal_of_sum_cover C L cover f g f_add g_add agree_C
  intro l hl
  exact (f_ann_L l hl).trans (g_ann_L l hl).symm

/-- Vanishing on C and L implies vanishing everywhere. The single scalar
zero-addition law is supplied explicitly, as in the repository's other
Init-only additive cores. -/
theorem annihilates_of_sum_cover
    (C L : V → Prop)
    (cover : ∀ v, ∃ c l, C c ∧ L l ∧ v = c + l)
    (f : V → K)
    (f_add : ∀ x y, f (x + y) = f x + f y)
    (zero_add : ∀ k : K, 0 + k = k)
    (f_ann_C : ∀ c, C c → f c = 0)
    (f_ann_L : ∀ l, L l → f l = 0) :
    ∀ v, f v = 0 := by
  intro v
  rcases cover v with ⟨c, l, hc, hl, hv⟩
  rw [hv, f_add, f_ann_C c hc, f_ann_L l hl, zero_add]

end AdditiveRestriction

section ActualOutsideCoordinates

variable {K V I : Type} [Zero K] [Add K] [Add V]

/-- The actual outside-dual independence implication.

For a genuine finite family of actual outside coordinate functionals phi_i,
instantiate `combination a` by sum_i a_i phi_i. Additivity and annihilation
of L are inherited from the actual coordinate functionals. Biorthogonality
on the outside actual basis vectors gives `outside_evaluation`.

The theorem then derives, rather than assumes, that any restricted relation
vanishing on C has every coefficient zero. Constructing the finite sum and
the vector-space/actual-basis bridge is not included in this Init-only core.
-/
theorem outside_coefficients_zero_of_restricted_relation
    (C L : V → Prop)
    (cover : ∀ v, ∃ c l, C c ∧ L l ∧ v = c + l)
    (outside : I → V)
    (combination : (I → K) → V → K)
    (combination_add : ∀ a x y,
      combination a (x + y) = combination a x + combination a y)
    (combination_ann_L : ∀ a l, L l → combination a l = 0)
    (outside_evaluation : ∀ a i, combination a (outside i) = a i)
    (zero_add : ∀ k : K, 0 + k = k)
    (a : I → K)
    (restricted_relation : ∀ c, C c → combination a c = 0) :
    ∀ i, a i = 0 := by
  have all_zero : ∀ v, combination a v = 0 :=
    annihilates_of_sum_cover C L cover (combination a)
      (combination_add a) zero_add restricted_relation (combination_ann_L a)
  intro i
  exact (outside_evaluation a i).symm.trans (all_zero (outside i))

end ActualOutsideCoordinates

#print axioms additive_maps_equal_of_sum_cover
#print axioms restriction_injective_on_annihilator
#print axioms annihilates_of_sum_cover
#print axioms outside_coefficients_zero_of_restricted_relation

end NonadaptedD3
