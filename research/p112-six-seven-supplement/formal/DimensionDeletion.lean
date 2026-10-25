/-
Copyright (c) 2026 conorholds. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Prepared with substantial OpenAI Codex assistance.
-/
import Mathlib.LinearAlgebra.FiniteDimensional.Lemmas
import Mathlib.LinearAlgebra.Dimension.Constructions
import Mathlib.LinearAlgebra.Pi
import Mathlib.LinearAlgebra.Basis.Basic

/-!
# Dimension deletion for actual linear combinations

A finite-dimensional space has a nonzero vector annihilated by any smaller
family of scalar linear constraints. For basis-coordinate constraints this
produces a vector in the span of the undeleted basis vectors, not merely a
support-union relaxation. The last theorem applies to a code subspace inside
the span of an independent family and deletes any `d - 1` of its basis pieces.

No E8 geometry or P112 capacity premise is used in this file.
-/

namespace SixSevenSupplement

open Module

variable {K V : Type*} [DivisionRing K] [AddCommGroup V] [Module K V]

/-- Fewer scalar linear constraints than dimensions have a common nonzero
kernel vector. The constraints need not be independent or nonzero. -/
theorem exists_nonzero_annihilating
    [FiniteDimensional K V] {Constraint : Type*} [Fintype Constraint]
    (coeff : Constraint → V →ₗ[K] K)
    (hsize : Fintype.card Constraint < finrank K V) :
    ∃ v : V, v ≠ 0 ∧ ∀ i, coeff i v = 0 := by
  let f : V →ₗ[K] (Constraint → K) := LinearMap.pi coeff
  have hdim : finrank K (Constraint → K) < finrank K V := by
    simpa only [Module.finrank_pi] using hsize
  have hker : LinearMap.ker f ≠ ⊥ :=
    LinearMap.ker_ne_bot_of_finrank_lt hdim
  obtain ⟨v, hvker, hvzero⟩ := (LinearMap.ker f).ne_bot_iff.mp hker
  refine ⟨v, hvzero, ?_⟩
  intro i
  have hz : f v = 0 := LinearMap.mem_ker.mp hvker
  exact congrFun hz i

/-- The nonzero vector can be required to lie in a given finite-dimensional
subspace even when the ambient space itself is not finite-dimensional. -/
theorem exists_nonzero_in_submodule_annihilating
    (D : Submodule K V) [FiniteDimensional K D]
    {Constraint : Type*} [Fintype Constraint]
    (coeff : Constraint → V →ₗ[K] K)
    (hsize : Fintype.card Constraint < finrank K D) :
    ∃ v : V, v ∈ D ∧ v ≠ 0 ∧ ∀ i, coeff i v = 0 := by
  obtain ⟨v, hvzero, hcoeff⟩ := exists_nonzero_annihilating
    (fun i => (coeff i).comp D.subtype) hsize
  refine ⟨v, v.property, ?_, ?_⟩
  · intro hv
    exact hvzero (Subtype.ext hv)
  · exact hcoeff

/-- Deleting fewer than `dim D` basis pieces leaves an actual nonzero vector
of D in the span of the remaining pieces. The killed coefficients are also
retained explicitly in the conclusion. -/
theorem exists_nonzero_after_basis_deletion
    {Index : Type*} (b : Basis Index K V)
    (D : Submodule K V) [FiniteDimensional K D]
    (deleted : Finset Index) (hsize : deleted.card < finrank K D) :
    ∃ v : V, v ∈ D ∧ v ≠ 0 ∧
      (∀ i ∈ deleted, b.repr v i = 0) ∧
      v ∈ Submodule.span K (b '' (deleted : Set Index)ᶜ) := by
  classical
  have hcard : Fintype.card deleted < finrank K D := by
    simpa only [Fintype.card_coe] using hsize
  obtain ⟨v, hvD, hvzero, hcoord⟩ :=
    exists_nonzero_in_submodule_annihilating D
      (fun i : deleted => b.coord i.val) hcard
  have hzero : ∀ i ∈ deleted, b.repr v i = 0 := by
    intro i hi
    simpa only [Basis.coord_apply] using hcoord ⟨i, hi⟩
  refine ⟨v, hvD, hvzero, hzero, ?_⟩
  apply b.mem_span_image.mpr
  intro i hi
  show i ∉ deleted
  intro hdeleted
  exact (Finsupp.mem_support_iff.mp hi) (hzero i hdeleted)

/-- Literal code-subspace form of the `d - 1` deletion principle. A basis of
the piece span T is supplied; its intersection with the ambient code C has
dimension d. Every choice of d - 1 deleted basis pieces leaves a nonzero
ambient codeword in the span of the undeleted pieces. -/
theorem exists_codeword_after_dimension_minus_one_deletions
    {Index : Type*} (T C : Submodule K V)
    (b : Basis Index K T) [FiniteDimensional K (C.submoduleOf T)]
    (deleted : Finset Index)
    (hpositive : 0 < finrank K (C.submoduleOf T))
    (hdeleted : deleted.card = finrank K (C.submoduleOf T) - 1) :
    ∃ v : T, (v : V) ∈ C ∧ (v : V) ≠ 0 ∧
      (∀ i ∈ deleted, b.repr v i = 0) ∧
      v ∈ Submodule.span K (b '' (deleted : Set Index)ᶜ) := by
  have hsize : deleted.card < finrank K (C.submoduleOf T) := by omega
  obtain ⟨v, hvC, hvzero, hcoord, hspan⟩ :=
    exists_nonzero_after_basis_deletion b (C.submoduleOf T) deleted hsize
  refine ⟨v, hvC, ?_, hcoord, hspan⟩
  intro hv
  exact hvzero (Subtype.ext hv)

#print axioms exists_nonzero_annihilating
#print axioms exists_nonzero_in_submodule_annihilating
#print axioms exists_nonzero_after_basis_deletion
#print axioms exists_codeword_after_dimension_minus_one_deletions

end SixSevenSupplement
