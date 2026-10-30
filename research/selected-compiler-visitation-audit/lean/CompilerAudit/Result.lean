/-
SPDX-License-Identifier: Apache-2.0
Concrete corollaries for the authenticated selected interval data. These are
statements about the defined trace/allocation model, not Python execution.
-/
import CompilerAudit.Composition
import CompilerAudit.Selected

namespace CompilerAudit.Result

/-- Residual-operation projection of one complete selected model compilation. -/
def program (N : Nat) (blocks : Key → Nat) : List Retention.Op :=
  Composition.compileResiduals Selected.groups SelectedData.replicaCount N blocks

/-- The unpriced number of block-reference occurrences in the model word. -/
def blockTotal (N : Nat) (blocks : Key → Nat) : Nat :=
  ((Selected.word N).map blocks).sum

theorem distinct_source_keys (N : Nat) :
    (Selected.word N).toFinset.card = 28278 * N := Selected.word_distinct N

theorem retained_wrappers (N : Nat) (blocks : Key → Nat) :
    (Retention.retained (program N blocks)).card = 904896 * N := by
  rw [program, Composition.compile_retained_count, Selected.ids_length]
  change 32 * (28278 * N) = 904896 * N
  omega

theorem direct_references (N : Nat) (blocks : Key → Nat) :
    (Retention.refs (program N blocks)).length = 1809792 * N + blockTotal N blocks := by
  rw [program, Composition.compile_reference_count, Selected.ids_length]
  change 2 * (32 * (28278 * N)) + blockTotal N blocks =
    1809792 * N + blockTotal N blocks
  omega

theorem wrapper_key_ratio (N : Nat) (blocks : Key → Nat) :
    (Retention.retained (program N blocks)).card =
      32 * (Selected.word N).toFinset.card := by
  rw [retained_wrappers, distinct_source_keys]
  omega

theorem wrappers_strictly_exceed_keys (N : Nat) (blocks : Key → Nat) (hN : 0 < N) :
    (Selected.word N).toFinset.card < (Retention.retained (program N blocks)).card := by
  rw [distinct_source_keys, retained_wrappers]
  omega

/-- The central result: symbolic LOW size, no enumerated GL64 word. -/
theorem selected_compiler_model (N : Nat) (blocks : Key → Nat) :
    (Selected.word N).toFinset.card = 28278 * N ∧
    (Retention.retained (program N blocks)).card = 904896 * N ∧
    (Retention.refs (program N blocks)).length = 1809792 * N + blockTotal N blocks := by
  exact ⟨distinct_source_keys N, retained_wrappers N blocks, direct_references N blocks⟩

end CompilerAudit.Result
