/-
Copyright (c) 2026 conorholds. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Prepared with substantial OpenAI Codex assistance.

-/
import Init

/-!
# Constructed finite combinations of actual outside coordinate maps

The scalar combination is an explicit recursion over a List of indices.
Its additivity, annihilation, and coefficient-recovery laws are proved below;
they are not premises of the final outside-independence theorem.

To avoid importing Mathlib or needing decidable equality, `Listed` and
`NoRepeated` are elementary recursive list membership and no-duplication
predicates. Scalars have explicitly supplied operation laws. `unit` denotes
their multiplicative identity; no field/ring hierarchy is imported.

The remaining external bridge is the actual vector-space construction:
produce the finite list of actual outside indices and its no-repetition
proof, the actual additive coordinate maps annihilating L, their ordinary
biorthogonality on the outside basis vectors, and the dimension-derived
cover C+L=S. All characteristic-zero and E8 geometry remains external.
-/

namespace NonadaptedD3Finite

def Listed {I : Type} (k : I) : List I → Prop
  | [] => False
  | i :: rest => k = i ∨ Listed k rest

def NoRepeated {I : Type} : List I → Prop
  | [] => True
  | i :: rest => (¬ Listed i rest) ∧ NoRepeated rest

def scalarCombination {I K V : Type} [Zero K] [Add K] [Mul K] :
    List I → (I → K) → (I → V → K) → V → K
  | [], _, _, _ => 0
  | i :: rest, a, phi, v =>
      a i * phi i v + scalarCombination rest a phi v

section AdditiveLaws

variable {K : Type} [Add K]

/-- The only rearrangement needed to prove additivity of the finite sum. -/
theorem add_shuffle
    (h_assoc : ∀ a b c : K, (a + b) + c = a + (b + c))
    (h_comm : ∀ a b : K, a + b = b + a)
    (w x y z : K) :
    (w + x) + (y + z) = (w + y) + (x + z) := by
  calc
    (w + x) + (y + z) = w + (x + (y + z)) :=
      h_assoc w x (y + z)
    _ = w + ((x + y) + z) :=
      congrArg (fun t => w + t) (h_assoc x y z).symm
    _ = w + ((y + x) + z) := by rw [h_comm x y]
    _ = w + (y + (x + z)) :=
      congrArg (fun t => w + t) (h_assoc y x z)
    _ = (w + y) + (x + z) := (h_assoc w y (x + z)).symm

end AdditiveLaws

section FiniteCoordinates

variable {I K V : Type} [Zero K] [Add K] [Mul K]

/-- Constructed additivity, from the additivity of each coordinate map. -/
theorem scalarCombination_add [Add V]
    (phi : I → V → K)
    (phi_add : ∀ i x y, phi i (x + y) = phi i x + phi i y)
    (h_zero_add : ∀ a : K, 0 + a = a)
    (h_assoc : ∀ a b c : K, (a + b) + c = a + (b + c))
    (h_comm : ∀ a b : K, a + b = b + a)
    (h_mul_add : ∀ a b c : K, a * (b + c) = a * b + a * c)
    (indices : List I) (a : I → K) (x y : V) :
    scalarCombination indices a phi (x + y) =
      scalarCombination indices a phi x + scalarCombination indices a phi y := by
  induction indices with
  | nil =>
      change (0 : K) = 0 + 0
      exact (h_zero_add 0).symm
  | cons i rest ih =>
      change a i * phi i (x + y) + scalarCombination rest a phi (x + y) =
        (a i * phi i x + scalarCombination rest a phi x) +
        (a i * phi i y + scalarCombination rest a phi y)
      rw [phi_add i x y, h_mul_add (a i) (phi i x) (phi i y), ih]
      exact add_shuffle h_assoc h_comm
        (a i * phi i x) (a i * phi i y)
        (scalarCombination rest a phi x) (scalarCombination rest a phi y)

/-- Constructed annihilation of L, with no assumption on the combination. -/
theorem scalarCombination_annihilates
    (L : V → Prop) (phi : I → V → K)
    (phi_ann : ∀ i l, L l → phi i l = 0)
    (h_mul_zero : ∀ a : K, a * 0 = 0)
    (h_zero_add : ∀ a : K, 0 + a = a)
    (indices : List I) (a : I → K) :
    ∀ l, L l → scalarCombination indices a phi l = 0 := by
  intro l hl
  induction indices with
  | nil => rfl
  | cons i rest ih =>
      change a i * phi i l + scalarCombination rest a phi l = 0
      rw [phi_ann i l hl, h_mul_zero (a i), ih, h_zero_add 0]

/-- Off-diagonal biorthogonality kills a sum whose list omits k. -/
theorem scalarCombination_zero_of_absent
    (phi : I → V → K) (outside : I → V)
    (phi_off : ∀ i k, i ≠ k → phi i (outside k) = 0)
    (h_mul_zero : ∀ a : K, a * 0 = 0)
    (h_zero_add : ∀ a : K, 0 + a = a)
    (indices : List I) (a : I → K) (k : I) :
    (¬ Listed k indices) → scalarCombination indices a phi (outside k) = 0 := by
  induction indices with
  | nil =>
      intro _
      rfl
  | cons i rest ih =>
      intro h_absent
      have h_ne : i ≠ k := by
        intro h
        exact h_absent (Or.inl h.symm)
      have h_rest : ¬ Listed k rest := by
        intro h
        exact h_absent (Or.inr h)
      change a i * phi i (outside k) + scalarCombination rest a phi (outside k) = 0
      rw [phi_off i k h_ne, h_mul_zero (a i), ih h_rest, h_zero_add 0]

/-- Coefficient recovery is DERIVED from individual actual biorthogonality
and the absence of repeated indices in the finite list. -/
theorem scalarCombination_at_listed
    (unit : K) (phi : I → V → K) (outside : I → V)
    (phi_diag : ∀ i, phi i (outside i) = unit)
    (phi_off : ∀ i k, i ≠ k → phi i (outside k) = 0)
    (h_mul_zero : ∀ a : K, a * 0 = 0)
    (h_mul_unit : ∀ a : K, a * unit = a)
    (h_zero_add : ∀ a : K, 0 + a = a)
    (h_add_zero : ∀ a : K, a + 0 = a)
    (indices : List I) (a : I → K) (k : I) :
    NoRepeated indices → Listed k indices →
      scalarCombination indices a phi (outside k) = a k := by
  induction indices with
  | nil =>
      intro _ h
      exact False.elim h
  | cons i rest ih =>
      intro h_distinct h_listed
      change (¬ Listed i rest) ∧ NoRepeated rest at h_distinct
      change k = i ∨ Listed k rest at h_listed
      rcases h_listed with h_head | h_tail
      · subst k
        change a i * phi i (outside i) + scalarCombination rest a phi (outside i) = a i
        rw [phi_diag i, h_mul_unit (a i),
          scalarCombination_zero_of_absent phi outside phi_off
            h_mul_zero h_zero_add rest a i h_distinct.1,
          h_add_zero (a i)]
      · have h_ne : i ≠ k := by
          intro h
          have h_bad : Listed i rest := by
            rw [h]
            exact h_tail
          exact h_distinct.1 h_bad
        change a i * phi i (outside k) + scalarCombination rest a phi (outside k) = a k
        rw [phi_off i k h_ne, h_mul_zero (a i),
          ih h_distinct.2 h_tail, h_zero_add (a k)]

/-- Finite actual outside restricted independence, with a CONSTRUCTED scalar
combination. The premises concern only C+L coverage, individual coordinate
maps, their actual biorthogonality, scalar laws, and list no-duplication.
Neither combination additivity nor coefficient recovery is assumed. -/
theorem actual_outside_coefficients_zero [Add V]
    (unit : K)
    (C L : V → Prop)
    (cover : ∀ v, ∃ c l, C c ∧ L l ∧ v = c + l)
    (phi : I → V → K) (outside : I → V)
    (phi_add : ∀ i x y, phi i (x + y) = phi i x + phi i y)
    (phi_ann_L : ∀ i l, L l → phi i l = 0)
    (phi_diag : ∀ i, phi i (outside i) = unit)
    (phi_off : ∀ i k, i ≠ k → phi i (outside k) = 0)
    (h_zero_add : ∀ a : K, 0 + a = a)
    (h_add_zero : ∀ a : K, a + 0 = a)
    (h_assoc : ∀ a b c : K, (a + b) + c = a + (b + c))
    (h_comm : ∀ a b : K, a + b = b + a)
    (h_mul_zero : ∀ a : K, a * 0 = 0)
    (h_mul_unit : ∀ a : K, a * unit = a)
    (h_mul_add : ∀ a b c : K, a * (b + c) = a * b + a * c)
    (indices : List I) (h_distinct : NoRepeated indices)
    (a : I → K)
    (restricted_relation : ∀ c, C c → scalarCombination indices a phi c = 0) :
    ∀ k, Listed k indices → a k = 0 := by
  have all_zero : ∀ v, scalarCombination indices a phi v = 0 := by
    intro v
    rcases cover v with ⟨c, l, hc, hl, hv⟩
    calc
      scalarCombination indices a phi v =
          scalarCombination indices a phi c + scalarCombination indices a phi l := by
        rw [hv]
        exact scalarCombination_add phi phi_add h_zero_add h_assoc h_comm
          h_mul_add indices a c l
      _ = 0 := by
        rw [restricted_relation c hc,
          scalarCombination_annihilates L phi phi_ann_L h_mul_zero
            h_zero_add indices a l hl,
          h_zero_add 0]
  intro k hk
  have recover : scalarCombination indices a phi (outside k) = a k :=
    scalarCombination_at_listed unit phi outside phi_diag phi_off
      h_mul_zero h_mul_unit h_zero_add h_add_zero indices a k h_distinct hk
  exact recover.symm.trans (all_zero (outside k))

end FiniteCoordinates

#print axioms add_shuffle
#print axioms scalarCombination_add
#print axioms scalarCombination_annihilates
#print axioms scalarCombination_zero_of_absent
#print axioms scalarCombination_at_listed
#print axioms actual_outside_coefficients_zero

end NonadaptedD3Finite
