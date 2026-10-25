/-
Copyright (c) 2026 conorholds. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Prepared with substantial OpenAI Codex assistance.
-/
import Init

/-!
# Binary compatibility cliques have no nonempty zero relation

An Init-only proof of the abstract binary clique argument. The operations and
their algebraic laws are explicit parameters, not axioms or imported E8 facts.
No equivalence with Mathlib.LinearIndependent or E8 instantiation is claimed.
-/

namespace OneCosetDeficiency

universe u

variable {V : Type u}

private theorem bool_three_colors_impossible (a b c : Bool)
    (hab : a ≠ b) (hac : a ≠ c) (hbc : b ≠ c) : False := by
  cases a <;> cases b <;> cases c <;>
    first | exact hab rfl | exact hac rfl | exact hbc rfl

/-- A finite binary relation, with the empty sum explicitly specified. -/
def binarySum (zero : V) (add : V → V → V) : List V → V
  | [] => zero
  | x :: xs => add x (binarySum zero add xs)

/-- A linear Boolean-valued detector vanishes on a sum of vectors which it
annihilates individually. -/
theorem detector_sum_zero (zero : V) (add : V → V → V)
    (β : V → V → Bool)
    (hzero : ∀ x, β x zero = false)
    (hadd : ∀ x y z, β x (add y z) = Bool.xor (β x y) (β x z))
    (x : V) (xs : List V) :
    (∀ y ∈ xs, β x y = false) → β x (binarySum zero add xs) = false := by
  induction xs with
  | nil =>
      intro _
      exact hzero x
  | cons y ys ih =>
      intro h
      rw [binarySum, hadd, h y List.mem_cons_self,
        ih (fun z hz => h z (List.mem_cons_of_mem y hz))]
      rfl

/-- In a distinct finite family, a detector which is one on a selected vector
and zero on the other vectors evaluates to one on the whole sum. -/
theorem detector_sum_selected (zero : V) (add : V → V → V)
    (β : V → V → Bool)
    (hzero : ∀ x, β x zero = false)
    (hadd : ∀ x y z, β x (add y z) = Bool.xor (β x y) (β x z))
    (x : V) (xs : List V) :
    xs.Nodup → x ∈ xs → β x x = true →
    (∀ y ∈ xs, y ≠ x → β x y = false) →
    β x (binarySum zero add xs) = true := by
  classical
  induction xs with
  | nil =>
      intro _ hx
      cases hx
  | cons y ys ih =>
      intro hnd hx hdiag hoff
      have htail := List.nodup_cons.mp hnd
      by_cases hxy : x = y
      · subst y
        have hsumtail : β x (binarySum zero add ys) = false := by
          apply detector_sum_zero zero add β hzero hadd x ys
          intro z hz
          apply hoff z (List.mem_cons_of_mem x hz)
          intro hzx
          exact htail.1 (hzx ▸ hz)
        rw [binarySum, hadd, hdiag, hsumtail]
        rfl
      · have hxtail : x ∈ ys := (List.mem_cons.mp hx).resolve_left hxy
        have hih := ih htail.2 hxtail hdiag
          (fun z hz hzx => hoff z (List.mem_cons_of_mem y hz) hzx)
        rw [binarySum, hadd,
          hoff y List.mem_cons_self (fun hyx => hxy hyx.symm), hih]
        rfl

/-- Abstract binary clique independence, stated as absence of a nonempty
distinct zero-sum list. Pairing additivity kills any odd member of a relation.
Pairwise distinct Boolean colors then allow at most two remaining even members;
nonzero singleton and characteristic-two cancellation exclude those cases.

`hcancel` is the characteristic-two law `x + y = 0 ↔ x = y`. All required
algebraic and compatibility facts are premises. -/
theorem compatible_clique_zero_sum_empty
    (zero : V) (add : V → V → V) (β : V → V → Bool) (color : V → Bool)
    (haddzero : ∀ x, add x zero = x)
    (hcancel : ∀ x y, add x y = zero ↔ x = y)
    (hβzero : ∀ x, β x zero = false)
    (hβadd : ∀ x y z, β x (add y z) = Bool.xor (β x y) (β x z))
    (xs : List V) (hnodup : xs.Nodup)
    (hnonzero : ∀ x ∈ xs, x ≠ zero)
    (horth : ∀ x ∈ xs, ∀ y ∈ xs, x ≠ y → β x y = false)
    (hcolor : ∀ x ∈ xs, ∀ y ∈ xs, x ≠ y →
      β x x = false → β y y = false → color x ≠ color y)
    (hsum : binarySum zero add xs = zero) : xs = [] := by
  have heven : ∀ x ∈ xs, β x x = false := by
    intro x hx
    cases hdiag : β x x with
    | false => rfl
    | true =>
        have hdet := detector_sum_selected zero add β hβzero hβadd x xs
          hnodup hx hdiag
            (fun y hy hyx => horth x hx y hy (fun hxy => hyx hxy.symm))
        rw [hsum, hβzero] at hdet
        cases hdet
  cases xs with
  | nil => rfl
  | cons x rest =>
      cases rest with
      | nil =>
          have hxzero : x = zero := by
            simpa only [binarySum, haddzero] using hsum
          exact False.elim (hnonzero x List.mem_cons_self hxzero)
      | cons y rest =>
          cases rest with
          | nil =>
              have hxy : x = y := (hcancel x y).mp (by
                simpa only [binarySum, haddzero] using hsum)
              have hnot := (List.nodup_cons.mp hnodup).1
              exact False.elim (hnot (List.mem_cons.mpr (Or.inl hxy)))
          | cons z rest =>
              have hx : x ∈ x :: y :: z :: rest := List.mem_cons_self
              have hy : y ∈ x :: y :: z :: rest :=
                List.mem_cons_of_mem x List.mem_cons_self
              have hz : z ∈ x :: y :: z :: rest :=
                List.mem_cons_of_mem x (List.mem_cons_of_mem y List.mem_cons_self)
              have hnx := (List.nodup_cons.mp hnodup).1
              have hny := (List.nodup_cons.mp (List.nodup_cons.mp hnodup).2).1
              have hxy : x ≠ y := by
                intro h
                exact hnx (List.mem_cons.mpr (Or.inl h))
              have hxz : x ≠ z := by
                intro h
                exact hnx (List.mem_cons.mpr
                  (Or.inr (List.mem_cons.mpr (Or.inl h))))
              have hyz : y ≠ z := by
                intro h
                exact hny (List.mem_cons.mpr (Or.inl h))
              have hcxy := hcolor x hx y hy hxy (heven x hx) (heven y hy)
              have hcxz := hcolor x hx z hz hxz (heven x hx) (heven z hz)
              have hcyz := hcolor y hy z hz hyz (heven y hy) (heven z hz)
              exact False.elim
                (bool_three_colors_impossible (color x) (color y) (color z) hcxy hcxz hcyz)

/-- The grouped-relation step for a family of binary subspaces, expressed using
their membership predicates `Z`. A nonzero grouped vector from each selected
index gives a distinct compatible clique: trivial intersections exclude vector
collisions. Hence its sum can vanish only when no index was selected.

Closure of `Z i` under binary sums is not needed here: the theorem takes the
already grouped vectors. No finrank or scalar-field instantiation is asserted. -/
theorem compatible_transversal_zero_sum_empty {I : Type u}
    (zero : V) (add : V → V → V) (β : V → V → Bool) (color : V → Bool)
    (compatible : V → V → Prop) (Z : I → V → Prop)
    (haddzero : ∀ x, add x zero = x)
    (hcancel : ∀ x y, add x y = zero ↔ x = y)
    (hβzero : ∀ x, β x zero = false)
    (hβadd : ∀ x y z, β x (add y z) = Bool.xor (β x y) (β x z))
    (horth : ∀ x y, compatible x y → β x y = false)
    (hcolor : ∀ x y, compatible x y →
      β x x = false → β y y = false → color x ≠ color y)
    (hdisjoint : ∀ i j, i ≠ j → ∀ x, Z i x → Z j x → x = zero)
    (hcompatible : ∀ i j, i ≠ j → ∀ x, Z i x → x ≠ zero →
      ∀ y, Z j y → y ≠ zero → compatible x y)
    (indices : List I) (v : I → V) (hindices : indices.Nodup)
    (hv : ∀ i ∈ indices, Z i (v i))
    (hnonzero : ∀ i ∈ indices, v i ≠ zero)
    (hsum : binarySum zero add (indices.map v) = zero) : indices = [] := by
  have hdistinct : (indices.map v).Nodup := by
    apply List.pairwise_map.mpr
    apply List.Pairwise.imp_of_mem (p := hindices)
    intro i j hi hj hij heq
    have hzero : v i = zero :=
      hdisjoint i j hij (v i) (hv i hi) (heq.symm ▸ hv j hj)
    exact hnonzero i hi hzero
  have hempty : indices.map v = [] := by
    apply compatible_clique_zero_sum_empty zero add β color haddzero hcancel hβzero hβadd
      (indices.map v) hdistinct
    · intro x hx
      obtain ⟨i, hi, rfl⟩ := List.mem_map.mp hx
      exact hnonzero i hi
    · intro x hx y hy hxy
      obtain ⟨i, hi, rfl⟩ := List.mem_map.mp hx
      obtain ⟨j, hj, rfl⟩ := List.mem_map.mp hy
      have hij : i ≠ j := fun hij => hxy (congrArg v hij)
      exact horth _ _ (hcompatible i j hij (v i) (hv i hi) (hnonzero i hi)
        (v j) (hv j hj) (hnonzero j hj))
    · intro x hx y hy hxy hxeven hyeven
      obtain ⟨i, hi, rfl⟩ := List.mem_map.mp hx
      obtain ⟨j, hj, rfl⟩ := List.mem_map.mp hy
      have hij : i ≠ j := fun hij => hxy (congrArg v hij)
      exact hcolor _ _ (hcompatible i j hij (v i) (hv i hi) (hnonzero i hi)
        (v j) (hv j hj) (hnonzero j hj)) hxeven hyeven
    · exact hsum
  exact List.eq_nil_of_map_eq_nil hempty

#print axioms detector_sum_zero
#print axioms detector_sum_selected
#print axioms compatible_clique_zero_sum_empty
#print axioms compatible_transversal_zero_sum_empty

namespace BinaryNine

/-- The concrete nine-dimensional binary coordinate space. -/
abbrev Vector := Fin 9 → Bool

def zero : Vector := fun _ => false

def add (x y : Vector) : Vector := fun i => Bool.xor (x i) (y i)

private def coordinates : List (Fin 9) := [0, 1, 2, 3, 4, 5, 6, 7, 8]

private def pairingOn : List (Fin 9) → Vector → Vector → Bool
  | [], _, _ => false
  | i :: is, x, y => Bool.xor (Bool.and (x i) (y i)) (pairingOn is x y)

/-- The usual binary dot product, evaluated over all nine coordinates. -/
def beta (x y : Vector) : Bool := pairingOn coordinates x y

private theorem xor_zero_iff (a b : Bool) : Bool.xor a b = false ↔ a = b := by
  cases a <;> cases b <;> simp

private theorem add_zero (x : Vector) : add x zero = x := by
  funext i
  change Bool.xor (x i) false = x i
  cases x i <;> rfl

private theorem add_cancel (x y : Vector) : add x y = zero ↔ x = y := by
  constructor
  · intro h
    funext i
    exact (xor_zero_iff (x i) (y i)).mp (congrFun h i)
  · intro h
    subst y
    funext i
    exact Bool.xor_self (x i)

private theorem dot_distribute (a b c r s : Bool) :
    Bool.xor (Bool.and a (Bool.xor b c)) (Bool.xor r s) =
      Bool.xor (Bool.xor (Bool.and a b) r) (Bool.xor (Bool.and a c) s) := by
  cases a <;> cases b <;> cases c <;> cases r <;> cases s <;> rfl

private theorem pairingOn_zero (is : List (Fin 9)) (x : Vector) :
    pairingOn is x zero = false := by
  induction is with
  | nil => rfl
  | cons i is ih =>
      change Bool.xor (Bool.and (x i) false) (pairingOn is x zero) = false
      rw [ih]
      cases x i <;> rfl

private theorem pairingOn_add (is : List (Fin 9)) (x y z : Vector) :
    pairingOn is x (add y z) = Bool.xor (pairingOn is x y) (pairingOn is x z) := by
  induction is with
  | nil => rfl
  | cons i is ih =>
      change Bool.xor (Bool.and (x i) (Bool.xor (y i) (z i)))
        (pairingOn is x (add y z)) =
          Bool.xor (Bool.xor (Bool.and (x i) (y i)) (pairingOn is x y))
            (Bool.xor (Bool.and (x i) (z i)) (pairingOn is x z))
      rw [ih]
      exact dot_distribute (x i) (y i) (z i) (pairingOn is x y) (pairingOn is x z)

/-- Concrete binary-nine clique independence. All addition and pairing laws
are discharged here. Orthogonality and the even-color compatibility condition
remain explicit geometric premises; no E8 instantiation or finrank is asserted. -/
theorem clique_zero_sum_empty (color : Vector → Bool) (xs : List Vector)
    (hnodup : xs.Nodup) (hnonzero : ∀ x ∈ xs, x ≠ zero)
    (horth : ∀ x ∈ xs, ∀ y ∈ xs, x ≠ y → beta x y = false)
    (hcolor : ∀ x ∈ xs, ∀ y ∈ xs, x ≠ y →
      beta x x = false → beta y y = false → color x ≠ color y)
    (hsum : binarySum zero add xs = zero) : xs = [] :=
  OneCosetDeficiency.compatible_clique_zero_sum_empty zero add beta color
    add_zero add_cancel (pairingOn_zero coordinates) (pairingOn_add coordinates)
    xs hnodup hnonzero horth hcolor hsum

#print axioms clique_zero_sum_empty

end BinaryNine

end OneCosetDeficiency
