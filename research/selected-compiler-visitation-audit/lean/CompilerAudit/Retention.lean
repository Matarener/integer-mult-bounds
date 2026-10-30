/-
SPDX-License-Identifier: Apache-2.0
Released under the Apache 2.0 license; see the repository LICENSE.

Attribution: this formalizes the existing selected-compiler-visitation census.
The underlying compiler/source contributors retain the credits recorded in the
audit README and original README/NOTICE files. OpenAI Codex assisted this work.
-/

import Mathlib.Data.Finset.Card
import Mathlib.Data.List.Range

/-!
# Fresh wrapper allocation and retained operation references

This is an abstract model, not a verification of Python semantics, compiler
source, native execution, memory sizes, or an actual object's lifetime. Each
visit allocates one fresh natural-number wrapper ID, emits a begin operation,
its prescribed number of block operations, and a finish operation. The complete
operation list retains every emitted reference. Zero-block visits are allowed.

The caller supplies the visit-ordered block budgets. Connecting that list to a
source-level visit loop or source certificate is outside this module's scope.
-/

namespace CompilerAudit.Retention

/-- Every residual operation carries the ID of the wrapper it references. -/
inductive Op where
  | begin (wrapperID : Nat)
  | block (wrapperID : Nat)
  | finish (wrapperID : Nat)
  deriving DecidableEq, Repr

/-- Forget an operation's kind, but not its wrapper identity. -/
def Op.wrapperID : Op → Nat
  | .begin wrapperID => wrapperID
  | .block wrapperID => wrapperID
  | .finish wrapperID => wrapperID

/-- All references, including repeated references to the same wrapper. -/
def refs (ops : List Op) : List Nat := ops.map Op.wrapperID

/-- Wrapper IDs at allocation/begin sites, in operation order. -/
def beginIds (ops : List Op) : List Nat :=
  ops.filterMap fun
    | .begin wrapperID => some wrapperID
    | _ => none

/-- Wrapper IDs at finish sites, in operation order. -/
def finishIds (ops : List Op) : List Nat :=
  ops.filterMap fun
    | .finish wrapperID => some wrapperID
    | _ => none

/-- The distinct wrapper IDs referenced by the complete operation list. -/
def retained (ops : List Op) : Finset Nat := (refs ops).toFinset

/-- Emit one whole begin/block/finish segment per budget, allocating consecutive IDs. -/
def emitFrom (start : Nat) : List Nat → List Op
  | [] => []
  | blocks :: budgets =>
      .begin start ::
        (List.replicate blocks (.block start) ++
          (.finish start :: emitFrom (start + 1) budgets))

/-- The constructed stream has two boundary operations plus each visit's blocks. -/
theorem emit_length (start : Nat) (budgets : List Nat) :
    (emitFrom start budgets).length = 2 * budgets.length + budgets.sum := by
  induction budgets generalizing start with
  | nil => simp [emitFrom]
  | cons blocks budgets ih =>
      simp [emitFrom, ih, Nat.mul_add, Nat.add_assoc, Nat.add_left_comm, Nat.add_comm]
      omega

/-- Count the actual projected references, not a separately defined count formula. -/
theorem emit_reference_count (start : Nat) (budgets : List Nat) :
    (refs (emitFrom start budgets)).length = 2 * budgets.length + budgets.sum := by
  simpa only [refs, List.length_map] using emit_length start budgets

/-- One visit's references include both boundaries even when its budget is zero. -/
theorem emit_refs_cons (start blocks : Nat) (budgets : List Nat) :
    refs (emitFrom start (blocks :: budgets)) =
      start :: (List.replicate blocks start ++
        (start :: refs (emitFrom (start + 1) budgets))) := by
  simp [emitFrom, refs, Op.wrapperID]

/-- Exactly one begin per visit, with monotonically allocated wrapper IDs. -/
theorem emit_begin_ids (start : Nat) (budgets : List Nat) :
    beginIds (emitFrom start budgets) = List.range' start budgets.length := by
  induction budgets generalizing start with
  | nil => simp [emitFrom, beginIds]
  | cons blocks budgets ih =>
      calc
        beginIds (emitFrom start (blocks :: budgets)) =
            start :: beginIds (emitFrom (start + 1) budgets) := by
          simp [emitFrom, beginIds]
        _ = List.range' start (blocks :: budgets).length := by
          simp only [ih, List.length_cons, List.range'_succ]

/-- Every allocated wrapper also has exactly one finish, in the same order. -/
theorem emit_finish_ids (start : Nat) (budgets : List Nat) :
    finishIds (emitFrom start budgets) = List.range' start budgets.length := by
  induction budgets generalizing start with
  | nil => simp [emitFrom, finishIds]
  | cons blocks budgets ih =>
      calc
        finishIds (emitFrom start (blocks :: budgets)) =
            start :: finishIds (emitFrom (start + 1) budgets) := by
          simp [emitFrom, finishIds]
        _ = List.range' start (blocks :: budgets).length := by
          simp only [ih, List.length_cons, List.range'_succ]

/-- Distinct visits never reuse an allocation/begin ID. -/
theorem emit_begin_nodup (start : Nat) (budgets : List Nat) :
    (beginIds (emitFrom start budgets)).Nodup := by
  rw [emit_begin_ids]
  exact List.nodup_range'

/-- There is no duplicate finish ID either. -/
theorem emit_finish_nodup (start : Nat) (budgets : List Nat) :
    (finishIds (emitFrom start budgets)).Nodup := by
  rw [emit_finish_ids]
  exact List.nodup_range'

/-- Blocks introduce no foreign IDs; every allocated ID is actually referenced. -/
theorem emit_ref_mem_range (start : Nat) (budgets : List Nat) (wrapperID : Nat) :
    wrapperID ∈ refs (emitFrom start budgets) ↔
      wrapperID ∈ List.range' start budgets.length := by
  induction budgets generalizing start with
  | nil => simp [emitFrom, refs]
  | cons blocks budgets ih =>
      simp only [emit_refs_cons, List.mem_cons, List.mem_append, List.mem_replicate,
        List.length_cons, List.range'_succ, ih]
      tauto

/-- The support of all retained references is precisely the allocated range. -/
theorem emit_support (start : Nat) (budgets : List Nat) :
    retained (emitFrom start budgets) = (List.range' start budgets.length).toFinset := by
  apply Finset.ext
  intro wrapperID
  simpa only [retained, List.mem_toFinset] using
    emit_ref_mem_range start budgets wrapperID

/-- One retained distinct wrapper per visit, regardless of the block budgets. -/
theorem emit_retained_count (start : Nat) (budgets : List Nat) :
    (retained (emitFrom start budgets)).card = budgets.length := by
  rw [emit_support, List.toFinset_card_of_nodup List.nodup_range', List.length_range']

/-- Equivalent half-open interval description, including the empty stream. -/
theorem emit_ref_mem_iff (start : Nat) (budgets : List Nat) (wrapperID : Nat) :
    wrapperID ∈ refs (emitFrom start budgets) ↔
      start ≤ wrapperID ∧ wrapperID < start + budgets.length := by
  exact (emit_ref_mem_range start budgets wrapperID).trans List.mem_range'_1

/-- Continuing allocation at the next ID is fresh relative to this entire stream. -/
theorem emit_next_id_fresh (start : Nat) (budgets : List Nat) :
    start + budgets.length ∉ refs (emitFrom start budgets) := by
  simp [emit_ref_mem_iff]

end CompilerAudit.Retention
