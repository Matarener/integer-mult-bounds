/-
Copyright (c) 2026 conorholds. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Prepared with substantial OpenAI Codex assistance.
-/
import Mathlib.Data.ZMod.Defs
import Mathlib.LinearAlgebra.BilinearMap
import Mathlib.LinearAlgebra.LinearIndependent.Defs

/-!
# Private matched root labels are independent and exclude frame labels

This formalizes a generic binary-label argument, not an E8 census or a
numeric decoder ledger. Let every root label have leading coordinate one.
Its pairing with the private matched frame labels is `1 - delta`.
Subtracting that pairing from the leading coordinate recovers the root's
individual coefficient. Thus the roots are linearly independent.

A frame label has leading coordinate one and pairs to one with every
private matched frame. All its recovered root coefficients would therefore
be zero, so it cannot belong to the root span.

No symmetry or nondegeneracy of the bilinear form is assumed. No hypothesis
about the leading coordinates of the *test* labels is needed; the candidate
frame label whose exclusion is proved has leading coordinate one explicitly.
The E8/label instantiation and the `1 - delta` hypotheses remain external.
-/

noncomputable section

open scoped BigOperators

namespace PrivateLabels

abbrev F₂ := ZMod 2

variable {ι V : Type*} [Fintype ι] [DecidableEq ι]
variable [AddCommGroup V] [Module F₂ V]

/-- The leading coordinate minus pairing with one private matched label. -/
def privateCoordinate (β : LinearMap.BilinForm F₂ V)
    (leading : V →ₗ[F₂] F₂) (test : ι → V) (j : ι) : V →ₗ[F₂] F₂ :=
  leading - β.flip (test j)

variable (β : LinearMap.BilinForm F₂ V) (leading : V →ₗ[F₂] F₂)
variable (root test : ι → V)
variable (root_leading : ∀ i, leading (root i) = 1)
variable (private_pairing : ∀ i j,
  β (root i) (test j) = 1 - if i = j then 1 else 0)

include root_leading private_pairing

omit [Fintype ι] in
/-- The derived coordinate is the Kronecker delta on the root family. -/
theorem privateCoordinate_root (i j : ι) :
    privateCoordinate β leading test j (root i) = if i = j then 1 else 0 := by
  by_cases hij : i = j
  · simp [privateCoordinate, root_leading, private_pairing, hij]
  · simp [privateCoordinate, root_leading, private_pairing, hij]

/-- Every coefficient of a finite root combination is recovered by a
specified linear functional. Coefficients and vectors are actual data. -/
theorem coefficient_recovered (a : ι → F₂) (j : ι) :
    privateCoordinate β leading test j (∑ i, a i • root i) = a j := by
  calc
    privateCoordinate β leading test j (∑ i, a i • root i) =
        ∑ i, a i • privateCoordinate β leading test j (root i) := by simp
    _ = ∑ i, if i = j then a i else 0 := by
      apply Finset.sum_congr rfl
      intro i _
      rw [privateCoordinate_root β leading root test root_leading private_pairing]
      by_cases hij : i = j <;> simp [hij, smul_eq_mul]
    _ = a j := by simp

/-- Generic binary private-label linear independence. -/
theorem root_labels_linearIndependent : LinearIndependent F₂ root := by
  rw [Fintype.linearIndependent_iff]
  intro a ha j
  have h := congrArg (privateCoordinate β leading test j) ha
  rw [coefficient_recovered β leading root test root_leading private_pairing] at h
  simpa using h

/-- A leading-one label pairing to one with every private test cannot lie
in the root span. In the E8 application this excludes every frame label. -/
theorem no_frame_label_mem_span (z : V)
    (frame_leading : leading z = 1)
    (frame_pairing : ∀ j, β z (test j) = 1) :
    z ∉ Submodule.span F₂ (Set.range root) := by
  intro hz
  obtain ⟨a, ha⟩ := (Submodule.mem_span_range_iff_exists_fun F₂).mp hz
  have ha0 : ∀ j, a j = 0 := by
    intro j
    have h := congrArg (privateCoordinate β leading test j) ha
    rw [coefficient_recovered β leading root test root_leading private_pairing] at h
    simpa [privateCoordinate, frame_leading, frame_pairing] using h
  have hz0 : z = 0 := by
    simpa [ha0] using ha.symm
  have hzero_one : (0 : F₂) = 1 := by
    simpa [hz0] using frame_leading
  exact (by decide : (0 : F₂) ≠ 1) hzero_one

/-- The two analytic consequences used together by the private-frame proof. -/
theorem independent_and_frame_free (z : V)
    (frame_leading : leading z = 1)
    (frame_pairing : ∀ j, β z (test j) = 1) :
    LinearIndependent F₂ root ∧ z ∉ Submodule.span F₂ (Set.range root) := by
  exact ⟨root_labels_linearIndependent β leading root test root_leading private_pairing,
    no_frame_label_mem_span β leading root test root_leading private_pairing
      z frame_leading frame_pairing⟩

#print axioms root_labels_linearIndependent
#print axioms no_frame_label_mem_span
#print axioms independent_and_frame_free

end PrivateLabels
