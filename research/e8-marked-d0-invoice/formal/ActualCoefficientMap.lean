/-
Copyright (c) 2026 conorholds. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Prepared with substantial OpenAI Codex assistance.
-/
import Mathlib.LinearAlgebra.Basis.Defs
import Mathlib.Tactic.Abel

/-!
# Actual low coefficients of the correction map

The input is an actual basis indexed by low and high slots, a code map,
and a quotient splitting. The high basis vectors project to a specified
basis of the code-coordinate space; the low basis vectors project to zero.

We first derive the actual high coordinates of EVERY vector from its
quotient. We then specialize to the code section and prove the correction
identity by the actual basis expansion. Neither the high-coordinate
identity nor the resulting low-coefficient identity is a hypothesis.

No E8 label geometry, invoice bound, or nonzero-low-dual assumption is
formalized here. The code map, quotient, bases, and section identity are
explicit mathematical data.
-/

noncomputable section

open scoped BigOperators

namespace ActualCoefficientMap

variable {K J I H S : Type*} [Field K] [Fintype J] [Fintype I]
variable [AddCommGroup H] [Module K H]
variable [AddCommGroup S] [Module K S]

/-- The actual low coordinate of a code vector, as a linear functional. -/
def actualXi (b : Basis (J ⊕ I) K S) (c : H →ₗ[K] S) (a : J) : H →ₗ[K] K :=
  (b.coord (Sum.inl a)).comp c

omit [Fintype J] [Fintype I] in
@[simp]
theorem actualXi_apply (b : Basis (J ⊕ I) K S) (c : H →ₗ[K] S)
    (a : J) (h : H) :
    actualXi b c a h = b.repr (c h) (Sum.inl a) := by
  rfl

/-- The correction of the actual high basis vector from its code lift. -/
def highCorrection (b : Basis (J ⊕ I) K S) (c : H →ₗ[K] S)
    (e : Basis I K H) (i : I) : S :=
  b (Sum.inr i) - c (e i)

/-- The correction map defined from its actual high-basis corrections. -/
def correctionMap (b : Basis (J ⊕ I) K S) (c : H →ₗ[K] S)
    (e : Basis I K H) : H →ₗ[K] S :=
  e.constr K (highCorrection b c e)

omit [Fintype J] in
/-- This is the finite-sum definition used in the written decoder proof. -/
theorem correctionMap_apply (b : Basis (J ⊕ I) K S) (c : H →ₗ[K] S)
    (e : Basis I K H) (h : H) :
    correctionMap b c e h =
      ∑ i : I, e.repr h i • highCorrection b c e i := by
  simp only [correctionMap, Basis.constr_apply_fintype, Basis.equivFun_apply]

omit [Fintype J] [Fintype I] in
@[simp]
theorem correctionMap_high_basis (b : Basis (J ⊕ I) K S)
    (c : H →ₗ[K] S) (e : Basis I K H) (i : I) :
    correctionMap b c e (e i) = highCorrection b c e i := by
  exact e.constr_basis K (highCorrection b c e) i

variable (b : Basis (J ⊕ I) K S) (c : H →ₗ[K] S)
variable (e : Basis I K H) (π : S →ₗ[K] H)

/-- Projection of the actual basis expansion determines every high
coordinate. No section or code-coordinate identity is assumed here. -/
theorem high_coordinate_of_quotient
    (low_quotient : ∀ a : J, π (b (Sum.inl a)) = 0)
    (high_quotient : ∀ i : I, π (b (Sum.inr i)) = e i)
    (s : S) (i : I) :
    b.repr s (Sum.inr i) = e.repr (π s) i := by
  classical
  have hproject := congrArg π (b.sum_repr s)
  have hexpand : (∑ j : I, b.repr s (Sum.inr j) • e j) = π s := by
    simpa only [map_add, map_sum, map_smul, Fintype.sum_sum_type,
      low_quotient, high_quotient, smul_zero, Finset.sum_const_zero,
      zero_add] using hproject
  have hcoord := congrArg (fun y : H => e.repr y i) hexpand
  simpa only [Basis.repr_sum_self] using hcoord

/-- The actual high coordinates of a code vector are derived from the
quotient section, rather than postulated as decoder coefficients. -/
theorem actual_high_coordinate
    (section_identity : ∀ h : H, π (c h) = h)
    (low_quotient : ∀ a : J, π (b (Sum.inl a)) = 0)
    (high_quotient : ∀ i : I, π (b (Sum.inr i)) = e i)
    (h : H) (i : I) :
    b.repr (c h) (Sum.inr i) = e.repr h i := by
  rw [high_coordinate_of_quotient b e π low_quotient high_quotient,
    section_identity]

/-- The actual code expansion, separated into its low and high slots.
The high-slot coefficients have just been proved using the quotient. -/
theorem actual_code_expansion
    (section_identity : ∀ h : H, π (c h) = h)
    (low_quotient : ∀ a : J, π (b (Sum.inl a)) = 0)
    (high_quotient : ∀ i : I, π (b (Sum.inr i)) = e i)
    (h : H) :
    (∑ a : J, actualXi b c a h • b (Sum.inl a)) +
      (∑ i : I, e.repr h i • b (Sum.inr i)) = c h := by
  classical
  have hcoordinates := actual_high_coordinate b c e π
    section_identity low_quotient high_quotient h
  simpa only [Fintype.sum_sum_type, actualXi_apply, hcoordinates] using
    b.sum_repr (c h)

/-- The actual correction identity used by the marked decoder proof.
Its low coefficients are the restrictions of the ACTUAL dual basis.
There is no nonzero-dual assumption and no assumed correction identity. -/
theorem actual_coefficient_identity
    (section_identity : ∀ h : H, π (c h) = h)
    (low_quotient : ∀ a : J, π (b (Sum.inl a)) = 0)
    (high_quotient : ∀ i : I, π (b (Sum.inr i)) = e i)
    (h : H) :
    correctionMap b c e h =
      -(∑ a : J, actualXi b c a h • b (Sum.inl a)) := by
  classical
  have hexpand := actual_code_expansion b c e π
    section_identity low_quotient high_quotient h
  have hcode : (∑ i : I, e.repr h i • c (e i)) = c h := by
    calc
      (∑ i : I, e.repr h i • c (e i)) =
          c (∑ i : I, e.repr h i • e i) := by
            simp only [map_sum, map_smul]
      _ = c h := by rw [e.sum_repr]
  calc
    correctionMap b c e h =
        (∑ i : I, e.repr h i • b (Sum.inr i)) -
          (∑ i : I, e.repr h i • c (e i)) := by
            rw [correctionMap_apply]
            simp only [highCorrection, smul_sub, Finset.sum_sub_distrib]
    _ = (∑ i : I, e.repr h i • b (Sum.inr i)) - c h := by rw [hcode]
    _ = -(∑ a : J, actualXi b c a h • b (Sum.inl a)) := by
      rw [← hexpand]
      abel

omit [Fintype J] [Fintype I] in
/-- Each high correction really lies in the quotient kernel. -/
theorem highCorrection_quotient_zero
    (section_identity : ∀ h : H, π (c h) = h)
    (high_quotient : ∀ i : I, π (b (Sum.inr i)) = e i)
    (i : I) : π (highCorrection b c e i) = 0 := by
  simp [highCorrection, high_quotient, section_identity]

#print axioms high_coordinate_of_quotient
#print axioms actual_high_coordinate
#print axioms actual_code_expansion
#print axioms actual_coefficient_identity

end ActualCoefficientMap
