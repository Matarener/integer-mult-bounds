/-
SPDX-License-Identifier: Apache-2.0
The source/compiler lineage is credited in the package README. This module
formalizes the residual-visit projection, not the Python interpreter.
-/
import Mathlib.Data.List.Nodup
import Mathlib.Data.List.Range
import Mathlib.Data.List.ProdSigma
import Mathlib.Data.Finset.Card

namespace CompilerAudit

abbrev Key := Nat × Bool × Nat

/-- Ordered request IDs, their fixed view, and the literal LOW/request nesting. -/
structure Group where
  ids : List Nat
  common : Bool
  lowMajor : Bool
  deriving DecidableEq, Repr

/-- One replica: LOW-major for local groups, request-major for idle groups. -/
def groupWord (N : Nat) (g : Group) : List Key :=
  if g.lowMajor then
    ((List.range N) ×ˢ g.ids).map fun p => (p.2, g.common, p.1)
  else
    (g.ids ×ˢ (List.range N)).map fun p => (p.1, g.common, p.2)

/-- Replica repetition preserves the complete order inside each group. -/
def copies {α : Type*} : Nat → List α → List α
  | 0, _ => []
  | r + 1, xs => xs ++ copies r xs

def flatIds : List Group → List Nat
  | [] => []
  | g :: gs => g.ids ++ flatIds gs

def onePass (groups : List Group) (N : Nat) : List Key :=
  match groups with
  | [] => []
  | g :: gs => groupWord N g ++ onePass gs N

/-- Schedule groups, then replicas, then each group's own literal nesting. -/
def visitWord (groups : List Group) (replicas N : Nat) : List Key :=
  match groups with
  | [] => []
  | g :: gs => copies replicas (groupWord N g) ++ visitWord gs replicas N

@[simp] theorem groupWord_length (N : Nat) (g : Group) :
    (groupWord N g).length = g.ids.length * N := by
  cases h : g.lowMajor <;> simp [groupWord, h, List.length_product, Nat.mul_comm]

@[simp] theorem copies_length {α : Type*} (r : Nat) (xs : List α) :
    (copies r xs).length = r * xs.length := by
  induction r with
  | zero => simp [copies]
  | succ r ih => simp [copies, ih, Nat.succ_mul, Nat.add_comm]

@[simp] theorem mem_copies {α : Type*} (a : α) (r : Nat) (xs : List α) :
    a ∈ copies r xs ↔ 0 < r ∧ a ∈ xs := by
  induction r with
  | zero => simp [copies]
  | succ r ih =>
    simp only [copies, List.mem_append, ih, Nat.succ_pos, true_and]
    constructor
    · rintro (ha | ⟨_, ha⟩) <;> exact ha
    · intro ha; exact Or.inl ha

@[simp] theorem count_copies {α : Type*} [BEq α] (a : α) (r : Nat) (xs : List α) :
    (copies r xs).count a = r * xs.count a := by
  induction r with
  | zero => simp [copies]
  | succ r ih => simp [copies, ih, List.count_append, Nat.succ_mul, Nat.add_comm]

theorem groupWord_mem (N : Nat) (g : Group) (k : Key) :
    k ∈ groupWord N g ↔ k.1 ∈ g.ids ∧ k.2.1 = g.common ∧ k.2.2 < N := by
  rcases k with ⟨i, v, l⟩
  cases h : g.lowMajor <;>
    simp [groupWord, h, List.mem_map, Prod.exists, and_comm, and_left_comm, and_assoc, eq_comm]

theorem groupWord_nodup (N : Nat) (g : Group) (hids : g.ids.Nodup) :
    (groupWord N g).Nodup := by
  have leftInj : Function.Injective (fun p : Nat × Nat => ((p.1, g.common, p.2) : Key)) := by
    intro a b h
    exact Prod.ext (congrArg (fun k : Key => k.1) h) (congrArg (fun k : Key => k.2.2) h)
  have rightInj : Function.Injective (fun p : Nat × Nat => ((p.2, g.common, p.1) : Key)) := by
    intro a b h
    exact Prod.ext (congrArg (fun k : Key => k.2.2) h) (congrArg (fun k : Key => k.1) h)
  cases h : g.lowMajor
  · simpa [groupWord, h] using (hids.product (List.nodup_range (n := N))).map leftInj
  · simpa [groupWord, h] using ((List.nodup_range (n := N)).product hids).map rightInj

@[simp] theorem onePass_length (groups : List Group) (N : Nat) :
    (onePass groups N).length = (flatIds groups).length * N := by
  induction groups with
  | nil => simp [onePass, flatIds]
  | cons g gs ih => simp [onePass, flatIds, ih, Nat.add_mul]

theorem visitWord_length (groups : List Group) (replicas N : Nat) :
    (visitWord groups replicas N).length = replicas * ((flatIds groups).length * N) := by
  induction groups with
  | nil => simp [visitWord, flatIds]
  | cons g gs ih => simp [visitWord, flatIds, ih, Nat.add_mul, Nat.mul_add]

theorem onePass_id_mem (groups : List Group) (N : Nat) (k : Key)
    (h : k ∈ onePass groups N) : k.1 ∈ flatIds groups := by
  induction groups with
  | nil => simp [onePass] at h
  | cons g gs ih =>
    simp only [onePass, List.mem_append] at h
    simp only [flatIds, List.mem_append]
    rcases h with hg | hgs
    · exact Or.inl ((groupWord_mem N g k).mp hg).1
    · exact Or.inr (ih hgs)

theorem onePass_nodup (groups : List Group) (N : Nat)
    (h : (flatIds groups).Nodup) : (onePass groups N).Nodup := by
  induction groups with
  | nil => simp [onePass]
  | cons g gs ih =>
    obtain ⟨hg, hgs, hd⟩ := List.nodup_append'.mp h
    apply List.Nodup.append (groupWord_nodup N g hg) (ih hgs)
    apply List.disjoint_left.mpr
    intro k hk hk'
    exact List.disjoint_left.mp hd ((groupWord_mem N g k).mp hk).1
      (onePass_id_mem gs N k hk')

theorem visitWord_count (groups : List Group) (replicas N : Nat) (k : Key) :
    (visitWord groups replicas N).count k = replicas * (onePass groups N).count k := by
  induction groups with
  | nil => simp [visitWord, onePass]
  | cons g gs ih => simp [visitWord, onePass, List.count_append, ih, Nat.mul_add]

theorem visitWord_mem (groups : List Group) (replicas N : Nat) (k : Key)
    (hr : 0 < replicas) : k ∈ visitWord groups replicas N ↔ k ∈ onePass groups N := by
  induction groups with
  | nil => simp [visitWord, onePass]
  | cons g gs ih => simp [visitWord, onePass, hr, ih]

/-- Every visited source key occurs exactly once per replica, not once per code. -/
theorem visitWord_multiplicity (groups : List Group) (replicas N : Nat) (k : Key)
    (hids : (flatIds groups).Nodup) (hk : k ∈ onePass groups N) :
    (visitWord groups replicas N).count k = replicas := by
  rw [visitWord_count, List.count_eq_one_of_mem (onePass_nodup groups N hids) hk, Nat.mul_one]

/-- Distinct source keys are R*N even though the visit word has replicas*R*N entries. -/
theorem visitWord_distinct (groups : List Group) (replicas N : Nat)
    (hr : 0 < replicas) (hids : (flatIds groups).Nodup) :
    (visitWord groups replicas N).toFinset.card = (flatIds groups).length * N := by
  have hs : (visitWord groups replicas N).toFinset = (onePass groups N).toFinset := by
    ext k
    simpa only [List.mem_toFinset] using visitWord_mem groups replicas N k hr
  rw [hs, List.toFinset_card_of_nodup (onePass_nodup groups N hids), onePass_length]

theorem flatIds_eq_flatMap (groups : List Group) :
    flatIds groups = groups.flatMap Group.ids := by
  induction groups with
  | nil => rfl
  | cons g gs ih => simp [flatIds, ih]

/-- A genuine order witness: equal census totals do not determine chronology. -/
theorem different_orders :
    groupWord 2 ⟨[0, 1], true, true⟩ ≠ groupWord 2 ⟨[0, 1], true, false⟩ := by
  decide

/-- The order mutant preserves length and support, so those checks alone are insufficient. -/
theorem same_census_different_orders :
    let left := groupWord 2 ⟨[0, 1], true, true⟩
    let right := groupWord 2 ⟨[0, 1], true, false⟩
    left ≠ right ∧ left.length = right.length ∧ left.toFinset = right.toFinset := by
  decide

end CompilerAudit
