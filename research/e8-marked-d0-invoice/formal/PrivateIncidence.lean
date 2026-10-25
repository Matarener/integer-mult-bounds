/-
Copyright (c) 2026 conorholds. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Prepared with substantial OpenAI Codex assistance.
-/
import Mathlib.Data.Fintype.EquivFin
import Lean.Elab.Tactic.Omega

/-!
# Private corrected-high frame incidence

The hypotheses are finite incidence data, not a decoder ledger or a desired
cardinality bound. There are eight frame axes. Each root uses four axes,
including its own matched axis and no other axis in `allMatched`. Pairwise
root-support intersections have even cardinality. `allMatched` may include
additional corrected-high axes whose high normals are not roots.

We derive the four-root bound, exclusion of every additional matched axis
in the four-root case, and the bijection between roots and omitted unmatched
axes. The E8 geometric input and actual high-basis duality that produce this
finite incidence datum remain external to this file.
-/

noncomputable section

namespace PrivateIncidence

abbrev Axis := Fin 8

/-- Private-root incidence, allowing additional corrected-high frame axes. -/
structure Family (ι : Type*) [Fintype ι] where
  support : ι → Finset Axis
  matched : ι → Axis
  allMatched : Finset Axis
  support_card : ∀ i, (support i).card = 4
  own_mem : ∀ i, matched i ∈ support i
  other_absent : ∀ i j, i ≠ j → matched j ∉ support i
  matched_mem : ∀ i, matched i ∈ allMatched
  private_mem : ∀ i a, a ∈ support i → a ∈ allMatched → a = matched i
  even_intersection : ∀ i j, i ≠ j → (support i ∩ support j).card % 2 = 0

namespace Family

variable {ι : Type*} [Fintype ι] (F : Family ι)

/-- Matched axes are distinct as a consequence of privacy. -/
theorem matched_injective : Function.Injective F.matched := by
  intro i j hij
  by_contra hne
  apply F.other_absent i j hne
  rw [← hij]
  exact F.own_mem i

/-- The intersection of each support with all matched axes is its own axis. -/
theorem support_inter_matched (i : ι) :
    F.support i ∩ F.allMatched = {F.matched i} := by
  ext a
  simp only [Finset.mem_inter, Finset.mem_singleton]
  constructor
  · exact fun h => F.private_mem i a h.1 h.2
  · intro h
    subst a
    exact ⟨F.own_mem i, F.matched_mem i⟩

/-- Every private root has exactly three unmatched incident axes. -/
theorem tail_card (i : ι) : (F.support i \ F.allMatched).card = 3 := by
  have h := Finset.card_sdiff_add_card_inter (F.support i) F.allMatched
  rw [F.support_inter_matched i, Finset.card_singleton, F.support_card i] at h
  omega

theorem tail_subset_compl (i : ι) : F.support i \ F.allMatched ⊆ F.allMatchedᶜ := by
  intro a ha
  exact Finset.mem_compl.mpr (Finset.mem_sdiff.mp ha).2

/-- Privacy removes both matched axes from a distinct pair's intersection. -/
theorem intersection_eq_tail_intersection (i j : ι) (hne : i ≠ j) :
    F.support i ∩ F.support j =
      (F.support i \ F.allMatched) ∩ (F.support j \ F.allMatched) := by
  ext a
  simp only [Finset.mem_inter, Finset.mem_sdiff]
  constructor
  · intro h
    have ha : a ∉ F.allMatched := by
      intro ham
      have hai := F.private_mem i a h.1 ham
      have haj := F.private_mem j a h.2 ham
      exact hne (F.matched_injective (hai.symm.trans haj))
    exact ⟨⟨h.1, ha⟩, ⟨h.2, ha⟩⟩
  · exact fun h => ⟨h.1.1, h.2.1⟩

/-- Two private roots cannot have the same three unmatched incident axes:
their support intersection would have the forbidden odd cardinality three. -/
theorem tail_injective : Function.Injective (fun i => F.support i \ F.allMatched) := by
  intro i j hij
  change F.support i \ F.allMatched = F.support j \ F.allMatched at hij
  by_contra hne
  have h := F.even_intersection i j hne
  rw [F.intersection_eq_tail_intersection i j hne, hij, Finset.inter_self,
    F.tail_card j] at h
  omega

/-- Two private roots force at least four unmatched axes. This is derived
from actual 3-element tails and parity, rather than an assumed inequality. -/
theorem four_le_unmatched (i j : ι) (hne : i ≠ j) : 4 ≤ F.allMatchedᶜ.card := by
  by_contra hsmall
  have hcardi := F.tail_card i
  have hcardj := F.tail_card j
  have heqi : F.support i \ F.allMatched = F.allMatchedᶜ :=
    Finset.eq_of_subset_of_card_le (F.tail_subset_compl i) (by omega)
  have heqj : F.support j \ F.allMatched = F.allMatchedᶜ :=
    Finset.eq_of_subset_of_card_le (F.tail_subset_compl j) (by omega)
  exact hne (F.tail_injective (heqi.trans heqj.symm))

/-- As soon as there are two private roots, *all* corrected-high axes,
including any additional weight-nine axes, number at most four. -/
theorem allMatched_card_le_four (hpair : 1 < Fintype.card ι) : F.allMatched.card ≤ 4 := by
  obtain ⟨i, j, hne⟩ := Fintype.exists_pair_of_one_lt_card hpair
  have hcomp := F.four_le_unmatched i j hne
  have htotal := Finset.card_add_card_compl F.allMatched
  have hframe : Fintype.card Axis = 8 := by decide
  rw [hframe] at htotal
  omega

theorem root_card_le_matched : Fintype.card ι ≤ F.allMatched.card := by
  classical
  have hsub : Finset.univ.image F.matched ⊆ F.allMatched := by
    intro a ha
    obtain ⟨i, _, rfl⟩ := Finset.mem_image.mp ha
    exact F.matched_mem i
  have h := Finset.card_le_card hsub
  simpa only [Finset.card_image_of_injective _ F.matched_injective,
    Finset.card_univ] using h

include F in
/-- The incidence obstruction `m ≤ 4` used in SMALL section 3.3. -/
theorem root_card_le_four : Fintype.card ι ≤ 4 := by
  by_cases hsmall : Fintype.card ι ≤ 1
  · omega
  · have hmatched := F.allMatched_card_le_four (by omega)
    have hroots := F.root_card_le_matched
    omega

/-- Four private roots exhaust every corrected-high frame index. Therefore
no additional corrected weight-nine high frame axis exists. -/
theorem quartet_exhausts_matched (hfour : Fintype.card ι = 4) :
    F.allMatched = Finset.univ.image F.matched := by
  classical
  apply (Finset.eq_of_subset_of_card_le ?_ ?_).symm
  · intro a ha
    obtain ⟨i, _, rfl⟩ := Finset.mem_image.mp ha
    exact F.matched_mem i
  · rw [Finset.card_image_of_injective _ F.matched_injective, Finset.card_univ,
      hfour]
    exact F.allMatched_card_le_four (by omega)

/-- Explicit exclusion of an additional corrected-high frame axis. -/
theorem no_extra_matched_axis (hfour : Fintype.card ι = 4) (a : Axis)
    (ham : a ∈ F.allMatched) (hnew : ∀ i, a ≠ F.matched i) : False := by
  classical
  rw [F.quartet_exhausts_matched hfour] at ham
  obtain ⟨i, _, hi⟩ := Finset.mem_image.mp ham
  exact hnew i hi.symm

theorem quartet_matched_card (hfour : Fintype.card ι = 4) : F.allMatched.card = 4 := by
  classical
  rw [F.quartet_exhausts_matched hfour,
    Finset.card_image_of_injective _ F.matched_injective, Finset.card_univ, hfour]

theorem quartet_unmatched_card (hfour : Fintype.card ι = 4) : F.allMatchedᶜ.card = 4 := by
  rw [Finset.card_compl, F.quartet_matched_card hfour]
  decide

/-- A quartet root omits exactly one of the four unmatched axes. -/
theorem quartet_omission_singleton (hfour : Fintype.card ι = 4) (i : ι) :
    ∃ a, F.allMatchedᶜ \ F.support i = {a} := by
  apply Finset.card_eq_one.mp
  have hinter : F.allMatchedᶜ ∩ F.support i = F.support i \ F.allMatched := by
    ext a
    simp only [Finset.mem_inter, Finset.mem_compl, Finset.mem_sdiff]
    exact and_comm
  have h := Finset.card_sdiff_add_card_inter F.allMatchedᶜ (F.support i)
  rw [hinter, F.tail_card i, F.quartet_unmatched_card hfour] at h
  omega

/-- The actual uniquely omitted unmatched axis, chosen from its singleton. -/
def omittedAxis (hfour : Fintype.card ι = 4) (i : ι) : Axis :=
  Classical.choose (F.quartet_omission_singleton hfour i)

theorem omittedAxis_spec (hfour : Fintype.card ι = 4) (i : ι) :
    F.allMatchedᶜ \ F.support i = {F.omittedAxis hfour i} :=
  Classical.choose_spec (F.quartet_omission_singleton hfour i)

theorem omittedAxis_mem_compl (hfour : Fintype.card ι = 4) (i : ι) :
    F.omittedAxis hfour i ∈ F.allMatchedᶜ := by
  have h : F.omittedAxis hfour i ∈ F.allMatchedᶜ \ F.support i := by
    rw [F.omittedAxis_spec hfour i]
    exact Finset.mem_singleton_self _
  exact (Finset.mem_sdiff.mp h).1

theorem omittedAxis_not_mem_support (hfour : Fintype.card ι = 4) (i : ι) :
    F.omittedAxis hfour i ∉ F.support i := by
  have h : F.omittedAxis hfour i ∈ F.allMatchedᶜ \ F.support i := by
    rw [F.omittedAxis_spec hfour i]
    exact Finset.mem_singleton_self _
  exact (Finset.mem_sdiff.mp h).2

theorem tail_eq_erase_omitted (hfour : Fintype.card ι = 4) (i : ι) :
    F.support i \ F.allMatched = F.allMatchedᶜ.erase (F.omittedAxis hfour i) := by
  ext a
  have h := Finset.ext_iff.mp (F.omittedAxis_spec hfour i) a
  simp only [Finset.mem_sdiff, Finset.mem_compl, Finset.mem_singleton] at h
  simp only [Finset.mem_sdiff, Finset.mem_erase, Finset.mem_compl]
  constructor
  · intro ha
    exact ⟨fun heq => (h.mpr heq).2 ha.1, ha.2⟩
  · intro ha
    exact ⟨by by_contra hn; exact ha.1 (h.mp ⟨ha.2, hn⟩), ha.2⟩

/-- Distinct quartet roots omit distinct unmatched axes. -/
theorem omittedAxis_injective (hfour : Fintype.card ι = 4) :
    Function.Injective (F.omittedAxis hfour) := by
  intro i j hij
  apply F.tail_injective
  change F.support i \ F.allMatched = F.support j \ F.allMatched
  rw [F.tail_eq_erase_omitted hfour i, F.tail_eq_erase_omitted hfour j, hij]

/-- Every unmatched axis is omitted by exactly one quartet root. -/
theorem omittedAxis_image (hfour : Fintype.card ι = 4) :
    Finset.univ.image (F.omittedAxis hfour) = F.allMatchedᶜ := by
  classical
  apply Finset.eq_of_subset_of_card_le
  · intro a ha
    obtain ⟨i, _, rfl⟩ := Finset.mem_image.mp ha
    exact F.omittedAxis_mem_compl hfour i
  · rw [Finset.card_image_of_injective _ (F.omittedAxis_injective hfour),
      Finset.card_univ, F.quartet_unmatched_card hfour, hfour]

/-- The complete private-quartet incidence structure: each root consists
of its own matched axis and all but its uniquely omitted unmatched axis. -/
theorem quartet_support (hfour : Fintype.card ι = 4) (i : ι) :
    F.support i = insert (F.matched i)
      (F.allMatchedᶜ.erase (F.omittedAxis hfour i)) := by
  rw [← F.tail_eq_erase_omitted hfour i]
  ext a
  simp only [Finset.mem_insert, Finset.mem_sdiff]
  constructor
  · intro ha
    by_cases ham : a ∈ F.allMatched
    · exact Or.inl (F.private_mem i a ha ham)
    · exact Or.inr ⟨ha, ham⟩
  · intro ha
    rcases ha with heq | ha
    · subst a
      exact F.own_mem i
    · exact ha.1

/-- Every frame axis is perpendicular to some root of the private quartet.
In this incidence model, perpendicularity means absence from the support. -/
theorem quartet_axis_missed (hfour : Fintype.card ι = 4) (a : Axis) :
    ∃ i, a ∉ F.support i := by
  classical
  by_cases ham : a ∈ F.allMatched
  · rw [F.quartet_exhausts_matched hfour] at ham
    obtain ⟨i, _, hi⟩ := Finset.mem_image.mp ham
    obtain ⟨j, hji⟩ := Fintype.exists_ne_of_one_lt_card (by omega) i
    refine ⟨j, ?_⟩
    rw [← hi]
    exact F.other_absent j i hji
  · have hac : a ∈ F.allMatchedᶜ := Finset.mem_compl.mpr ham
    rw [← F.omittedAxis_image hfour] at hac
    obtain ⟨i, _, hi⟩ := Finset.mem_image.mp hac
    exact ⟨i, hi ▸ F.omittedAxis_not_mem_support hfour i⟩

#print axioms root_card_le_four
#print axioms quartet_exhausts_matched
#print axioms no_extra_matched_axis
#print axioms omittedAxis_injective
#print axioms omittedAxis_image
#print axioms quartet_support
#print axioms quartet_axis_missed

end Family

/-- A concrete compatible quartet: axis `i` is private, and unmatched axis
`i+4` is omitted. Kernel `decide` checks every incidence hypothesis. -/
def standardQuartet : Family (Fin 4) where
  support i := Finset.univ.filter fun a =>
    a.val = i.val ∨ (4 ≤ a.val ∧ a.val ≠ i.val + 4)
  matched i := ⟨i.val, Nat.lt_trans i.isLt (by decide)⟩
  allMatched := Finset.univ.filter fun a => a.val < 4
  support_card := by decide
  own_mem := by decide
  other_absent := by decide
  matched_mem := by decide
  private_mem := by decide
  even_intersection := by decide

example : Fintype.card (Fin 4) ≤ 4 := standardQuartet.root_card_le_four

example (a : Axis) : ∃ i, a ∉ standardQuartet.support i :=
  standardQuartet.quartet_axis_missed (by decide) a

end PrivateIncidence
