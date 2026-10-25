/-
SPDX-License-Identifier: Apache-2.0
Specializes the residual-visit projection of `CompilerAudit.Visit` to the
generated selected interval data. The data module is produced by the Python
authenticated source extraction (`lean/extract_census.py`, see
`CERTIFICATE-CONTRACT.md`); that bridge is NOT a formal theorem about Python,
and GL64 LOW cardinality remains a source premise (`N` stays symbolic here).
No request-ID list is expanded: closed facts are decided on the 19 tuples.
-/
import CompilerAudit.Visit
import CompilerAudit.SelectedData

namespace CompilerAudit.Selected

/-- Tuple `(start, count, common, lowMajor)` as a literal request interval. -/
def toGroup (q : Nat × Nat × Bool × Bool) : Group :=
  ⟨List.range' q.1 q.2.1, q.2.2.1, q.2.2.2⟩

def groups : List Group := SelectedData.intervals.map toGroup

/-- Interval separation: one interval ends before the other starts. -/
def sepB (a b : Nat × Nat × Bool × Bool) : Bool :=
  decide (a.1 + a.2.1 ≤ b.1) || decide (b.1 + b.2.1 ≤ a.1)

/-! ### Closed certificates on the 19 data tuples (no ID expansion) -/

set_option maxRecDepth 4096 in
theorem intervals_sep : SelectedData.intervals.Pairwise (fun a b => sepB a b = true) := by
  decide

set_option maxRecDepth 4096 in
theorem intervals_bound : ∀ q ∈ SelectedData.intervals, q.1 + q.2.1 ≤ 28278 := by
  decide

set_option maxRecDepth 4096 in
theorem counts_sum : (SelectedData.intervals.map fun q => q.2.1).sum = 28278 := by
  decide

set_option maxRecDepth 4096 in
theorem intervals_view : ∀ q ∈ SelectedData.intervals, q.2.2.1 = q.2.2.2 := by
  decide

theorem intervals_length : SelectedData.intervals.length = 19 := by decide

theorem replica_eq : SelectedData.replicaCount = 32 := rfl

theorem request_eq : SelectedData.requestCount = 28278 := rfl

theorem replica_pos : 0 < SelectedData.replicaCount := by decide

/-! ### Structural lemmas -/

theorem groups_length : groups.length = 19 := by
  rw [groups, List.length_map]; exact intervals_length

theorem groups_common_eq_lowMajor : ∀ g ∈ groups, g.common = g.lowMajor := by
  intro g hg
  obtain ⟨q, hq, rfl⟩ := List.mem_map.mp (show g ∈ SelectedData.intervals.map toGroup from hg)
  exact intervals_view q hq

theorem disjoint_of_sep {a b : Nat × Nat × Bool × Bool} (h : sepB a b = true) :
    List.Disjoint (toGroup a).ids (toGroup b).ids := by
  refine List.disjoint_left.mpr fun x hx hy => ?_
  have ha := List.mem_range'_1.mp (show x ∈ List.range' a.1 a.2.1 from hx)
  have hb := List.mem_range'_1.mp (show x ∈ List.range' b.1 b.2.1 from hy)
  simp only [sepB, Bool.or_eq_true, decide_eq_true_eq] at h
  omega

theorem length_flatIds_map (qs : List (Nat × Nat × Bool × Bool)) :
    (flatIds (qs.map toGroup)).length = (qs.map fun q => q.2.1).sum := by
  induction qs with
  | nil => rfl
  | cons q qs ih => simp [flatIds, toGroup, ih]

/-! ### Request-ID partition -/

theorem ids_nodup : (flatIds groups).Nodup := by
  rw [flatIds_eq_flatMap]
  refine List.nodup_flatMap.mpr ⟨?_, ?_⟩
  · intro g hg
    obtain ⟨q, -, rfl⟩ := List.mem_map.mp (show g ∈ SelectedData.intervals.map toGroup from hg)
    exact (show (List.range' q.1 q.2.1).Nodup from List.nodup_range')
  · rw [groups, List.pairwise_map]
    exact intervals_sep.imp fun h => disjoint_of_sep h

theorem ids_length : (flatIds groups).length = 28278 :=
  (length_flatIds_map SelectedData.intervals).trans counts_sum

theorem ids_lt {x : Nat} (hx : x ∈ flatIds groups) : x < 28278 := by
  rw [flatIds_eq_flatMap, List.mem_flatMap] at hx
  obtain ⟨g, hg, hxg⟩ := hx
  obtain ⟨q, hq, rfl⟩ := List.mem_map.mp (show g ∈ SelectedData.intervals.map toGroup from hg)
  have hm := List.mem_range'_1.mp (show x ∈ List.range' q.1 q.2.1 from hxg)
  have hb := intervals_bound q hq
  omega

/-- Coverage by subset plus cardinality, not by enumerating the IDs. -/
theorem ids_toFinset : (flatIds groups).toFinset = Finset.range 28278 := by
  apply Finset.eq_of_subset_of_card_le
  · intro x hx
    exact Finset.mem_range.mpr (ids_lt (List.mem_toFinset.mp hx))
  · exact le_of_eq (by rw [Finset.card_range, List.toFinset_card_of_nodup ids_nodup, ids_length])

/-! ### Selected visit word at symbolic LOW size `N` -/

def word (N : Nat) : List Key := visitWord groups SelectedData.replicaCount N

theorem word_length (N : Nat) : (word N).length = 904896 * N := by
  unfold word
  rw [visitWord_length, ids_length]
  show 32 * (28278 * N) = 904896 * N
  omega

theorem word_distinct (N : Nat) : (word N).toFinset.card = 28278 * N := by
  unfold word
  rw [visitWord_distinct groups _ N replica_pos ids_nodup, ids_length]

theorem word_mem (N : Nat) (k : Key) : k ∈ word N ↔ k ∈ onePass groups N :=
  visitWord_mem groups _ N k replica_pos

/-- Every visited source key is visited exactly once per replica. -/
theorem word_multiplicity (N : Nat) (k : Key) (hk : k ∈ word N) : (word N).count k = 32 :=
  visitWord_multiplicity groups _ N k ids_nodup ((word_mem N k).mp hk)

/-- For nonempty LOW, the compiler visits strictly more often than distinct keys. -/
theorem word_strict (N : Nat) (hN : 0 < N) : (word N).toFinset.card < (word N).length := by
  rw [word_distinct, word_length]
  omega

end CompilerAudit.Selected