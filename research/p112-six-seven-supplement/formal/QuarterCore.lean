/-
Copyright (c) 2026 conorholds. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Prepared with substantial OpenAI Codex assistance.
-/
import Mathlib.Data.Fintype.Prod
import Mathlib.Data.Finset.Card
import Lean.Elab.Tactic.Omega

/-!
# The 24-point deleted-quarter normal form and the sparse-cover obstruction

The finite model is the six one-points of the hyperbolic quadratic form
`x₀x₁ + x₂x₃`, with a two-dimensional radical. Every nonconstant affine
linear cut has at most 16 of its 24 points. The finite-model theorems use
kernel reduction (`decide`), not `native_decide` or an external certificate.

The last two theorems prove the covering argument for arbitrary finite sets.
The E8 root/label identification, reduction to this normal form, completion
rigidity, and rank-dependent intersection premises are not asserted here.
-/

namespace SixSevenSupplement

abbrev Bits2 := Bool × Bool
abbrev Bits4 := Bits2 × Bits2
abbrev Bits6 := Bits4 × Bits2

def zero2 : Bits2 := (false, false)
def zero4 : Bits4 := (zero2, zero2)

/-- Coordinatewise addition in the explicit two-coordinate binary model. -/
def xor2 (x y : Bits2) : Bits2 :=
  (Bool.xor x.1 y.1, Bool.xor x.2 y.2)

/-- Coordinatewise addition in the explicit four-coordinate binary model. -/
def xor4 (x y : Bits4) : Bits4 :=
  (xor2 x.1 y.1, xor2 x.2 y.2)

/-- The standard binary dot product in two coordinates. -/
def dot2 (a x : Bits2) : Bool :=
  Bool.xor (a.1 && x.1) (a.2 && x.2)

/-- Every linear functional on the four explicit binary coordinates. -/
def dot4 (a x : Bits4) : Bool :=
  Bool.xor (dot2 a.1 x.1) (dot2 a.2 x.2)

/-- The split, nondegenerate four-dimensional binary quadratic form. -/
def hyperbolic4 (x : Bits4) : Bool :=
  Bool.xor (x.1.1 && x.1.2) (x.2.1 && x.2.2)

def quadric4 : Finset Bits4 :=
  Finset.univ.filter fun x => hyperbolic4 x = true

def quadricSection (a : Bits4) (theta : Bool) : Finset Bits4 :=
  quadric4.filter fun x => dot4 a x = theta

theorem quadric4_card : quadric4.card = 6 := by decide

/-- All nonconstant affine hyperplanes meet the split quadric in at most four
points; both affine offsets and every nonzero normal are quantified. -/
theorem quadric_hyperplane_cap :
    ∀ a : Bits4, a ≠ zero4 → ∀ theta : Bool,
      (quadricSection a theta).card ≤ 4 := by decide

/-- The six one-points contain no affine binary plane: four distinct
one-points never have coordinatewise sum zero. -/
theorem quadric_no_affine_plane :
    ∀ x ∈ quadric4, ∀ y ∈ quadric4, ∀ z ∈ quadric4, ∀ w ∈ quadric4,
      x ≠ y → x ≠ z → x ≠ w → y ≠ z → y ≠ w → z ≠ w →
      xor4 (xor4 x y) (xor4 z w) ≠ zero4 := by decide

/-- Every pair of distinct one-points is avoided by a nonconstant affine
hyperplane section containing exactly four of the six one-points. -/
theorem quadric_pair_avoiding_section :
    ∀ x ∈ quadric4, ∀ y ∈ quadric4, x ≠ y →
      ∃ a : Bits4, ∃ theta : Bool, a ≠ zero4 ∧
        (quadricSection a theta).card = 4 ∧
        x ∉ quadricSection a theta ∧ y ∉ quadricSection a theta := by decide

/-- The two last coordinates are the radical coordinates. -/
def quarter : Finset Bits6 :=
  Finset.univ.filter fun x => hyperbolic4 x.1 = true

def quarterSection (a : Bits4) (b : Bits2) (theta : Bool) : Finset Bits6 :=
  quarter.filter fun x => Bool.xor (dot4 a x.1) (dot2 b x.2) = theta

theorem quarter_card : quarter.card = 24 := by decide

/-- A cut nonconstant on the radical takes exactly half the points. -/
theorem quarter_radical_cut_card :
    ∀ a : Bits4, ∀ b : Bits2, b ≠ zero2 → ∀ theta : Bool,
      (quarterSection a b theta).card = 12 := by decide

/-- A radical-constant nonconstant cut has four radical lifts per quadric
point. This statement includes every such normal and both affine offsets. -/
theorem quarter_constant_radical_card :
    ∀ a : Bits4, ∀ theta : Bool,
      (quarterSection a zero2 theta).card =
        4 * (quadricSection a theta).card := by decide

/-- The new capacity-16 bound in the explicit deleted-quarter normal form. -/
theorem quarter_hyperplane_cap (a : Bits4) (b : Bits2) (theta : Bool)
    (hnonzero : a ≠ zero4 ∨ b ≠ zero2) :
    (quarterSection a b theta).card ≤ 16 := by
  by_cases hb : b = zero2
  · subst b
    have ha : a ≠ zero4 := hnonzero.resolve_right (by simp)
    rw [quarter_constant_radical_card]
    have hcap := quadric_hyperplane_cap a ha theta
    omega
  · rw [quarter_radical_cut_card a b hb theta]
    decide

/-- The bound is attained, so replacing 16 by 15 would be false. -/
theorem quarter_capacity_sharp :
    (quarterSection ((true, false), (false, false)) zero2 true).card = 16 := by
  decide

section Covering

variable {Site : Type*} [DecidableEq Site]

/-- If a high flat avoids the core, a three-part cover of the live core
reduces to a cover by the low flat and the exceptional sites. -/
private theorem live_cover (C F L H E : Finset Site)
    (havoid : ∀ x ∈ C, x ∉ H)
    (hcover : C \ F ⊆ L ∪ H ∪ E) :
    C \ F ⊆ (C ∩ L) ∪ E := by
  intro x hx
  have hxC := (Finset.mem_sdiff.mp hx).1
  rcases Finset.mem_union.mp (hcover hx) with hLH | hE
  · rcases Finset.mem_union.mp hLH with hL | hH
    · exact Finset.mem_union.mpr (Or.inl (Finset.mem_inter.mpr ⟨hxC, hL⟩))
    · exact False.elim (havoid x hxC hH)
  · exact Finset.mem_union.mpr (Or.inr hE)

/-- A symbolic capacity bound for any finite core. If the high part avoids
the core, all remaining core points are charged to the exceptional set.
No restriction is imposed on overlaps between the cover parts. -/
theorem core_cover_card_le (C L H E : Finset Site)
    (havoid : ∀ x ∈ C, x ∉ H)
    (hcover : C ⊆ L ∪ H ∪ E) :
    C.card ≤ (C ∩ L).card + E.card := by
  have hcover' : C \ ∅ ⊆ L ∪ H ∪ E := by simpa using hcover
  have hsub := live_cover C ∅ L H E havoid hcover'
  have hcard := (Finset.card_le_card hsub).trans (Finset.card_union_le _ _)
  simpa using hcard

/-- For an unpunctured 24-point quarter, capacity 16 forces at least eight
exceptional sites. This is the frame-normal floor used by the root proof. -/
theorem unpunctured_quarter_exceptional_floor
    (C L H E : Finset Site)
    (hC : C.card = 24) (hL : (C ∩ L).card ≤ 16)
    (havoid : ∀ x ∈ C, x ∉ H)
    (hcover : C ⊆ L ∪ H ∪ E) : 8 ≤ E.card := by
  have hcard := core_cover_card_le C L H E havoid hcover
  omega

/-- This includes a frame normal, whose full quarter has no deleted sites,
as well as a nonframe normal with at most three deleted quarter sites. -/
theorem no_sparse_cover_of_at_most_three_deleted
    (C F L H E : Finset Site)
    (hC : C.card = 24) (hF : (C ∩ F).card ≤ 3)
    (hL : (C ∩ L).card ≤ 16) (hE : E.card ≤ 4)
    (havoid : ∀ x ∈ C, x ∉ H)
    (hcover : C \ F ⊆ L ∪ H ∪ E) : False := by
  have hsub := live_cover C F L H E havoid hcover
  have hcard := (Finset.card_le_card hsub).trans (Finset.card_union_le _ _)
  have hpartition := Finset.card_sdiff_add_card_inter C F
  omega

/-- The all-four-frame-deletions case retains the self site. If the low
flat carries self, its core intersection has capacity 12. Otherwise the
exceptional set must spend a site on self. These are the genuine geometric
premises used by the handwritten proof, rather than a presumed conclusion. -/
theorem no_sparse_cover_with_self
    (C F L H E : Finset Site) (self : Site)
    (hC : C.card = 24) (hF : (C ∩ F).card ≤ 4)
    (hL : (C ∩ L).card ≤ 16) (hE : E.card ≤ 4)
    (hselfC : self ∉ C) (hselfH : self ∉ H)
    (hselfL : self ∈ L → (C ∩ L).card ≤ 12)
    (havoid : ∀ x ∈ C, x ∉ H)
    (hcover : insert self (C \ F) ⊆ L ∪ H ∪ E) : False := by
  have hcorecover : C \ F ⊆ L ∪ H ∪ E := by
    intro x hx
    exact hcover (Finset.mem_insert_of_mem hx)
  have hsub := live_cover C F L H E havoid hcorecover
  have hpartition := Finset.card_sdiff_add_card_inter C F
  by_cases hsL : self ∈ L
  · have hsmall := hselfL hsL
    have hcard := (Finset.card_le_card hsub).trans (Finset.card_union_le _ _)
    omega
  · have hsE : self ∈ E := by
      have hscover := hcover (Finset.mem_insert_self self (C \ F))
      rcases Finset.mem_union.mp hscover with hsLH | hsE
      · rcases Finset.mem_union.mp hsLH with hsL' | hsH
        · exact False.elim (hsL hsL')
        · exact False.elim (hselfH hsH)
      · exact hsE
    have hsuberase : C \ F ⊆ (C ∩ L) ∪ E.erase self := by
      intro x hx
      rcases Finset.mem_union.mp (hsub hx) with hxL | hxE
      · exact Finset.mem_union.mpr (Or.inl hxL)
      · have hxself : x ≠ self := by
          intro heq
          exact hselfC (heq ▸ (Finset.mem_sdiff.mp hx).1)
        exact Finset.mem_union.mpr (Or.inr (Finset.mem_erase.mpr ⟨hxself, hxE⟩))
    have herase := Finset.card_erase_add_one hsE
    have hcard := (Finset.card_le_card hsuberase).trans (Finset.card_union_le _ _)
    omega

end Covering

#print axioms quadric4_card
#print axioms quadric_hyperplane_cap
#print axioms quadric_no_affine_plane
#print axioms quadric_pair_avoiding_section
#print axioms quarter_card
#print axioms quarter_radical_cut_card
#print axioms quarter_constant_radical_card
#print axioms quarter_hyperplane_cap
#print axioms quarter_capacity_sharp
#print axioms core_cover_card_le
#print axioms unpunctured_quarter_exceptional_floor
#print axioms no_sparse_cover_of_at_most_three_deleted
#print axioms no_sparse_cover_with_self

end SixSevenSupplement
