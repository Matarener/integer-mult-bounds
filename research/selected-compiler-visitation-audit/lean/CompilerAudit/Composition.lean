/-
SPDX-License-Identifier: Apache-2.0
Released under the Apache 2.0 license; see the repository LICENSE.
The source/compiler lineage retains the credits in the audit README and
original README/NOTICE files. OpenAI Codex assisted this formalization.
-/

import CompilerAudit.Visit
import CompilerAudit.Retention

/-!
# Compose the visit schedule with fresh residual-wrapper emission

These results count actual constructed operations and their wrapper IDs in the
abstract model. The key-indexed block budget is arbitrary, including zero;
repeated visits to the same key receive the same budget. For arbitrary per-visit
budgets, use Retention.emitFrom. No Python or native semantics, source-certificate
validity, or physical lifetime is asserted.
-/

namespace CompilerAudit.Composition

/-- Compile the ordered visits, allocating a fresh wrapper for every occurrence. -/
def compileResiduals (groups : List Group) (replicas N : Nat)
    (blocks : Key → Nat) : List Retention.Op :=
  Retention.emitFrom 0 ((visitWord groups replicas N).map blocks)

/-- All visits retain distinct wrappers, even when their source keys coincide. -/
theorem compile_retained_count (groups : List Group) (replicas N : Nat)
    (blocks : Key → Nat) :
    (Retention.retained (compileResiduals groups replicas N blocks)).card =
      replicas * ((flatIds groups).length * N) := by
  rw [compileResiduals, Retention.emit_retained_count, List.length_map, visitWord_length]

/-- Count both boundary references and every emitted block reference. -/
theorem compile_reference_count (groups : List Group) (replicas N : Nat)
    (blocks : Key → Nat) :
    (Retention.refs (compileResiduals groups replicas N blocks)).length =
      2 * (replicas * ((flatIds groups).length * N)) +
        ((visitWord groups replicas N).map blocks).sum := by
  rw [compileResiduals, Retention.emit_reference_count, List.length_map, visitWord_length]

/-- The wrapper/source-key ratio is replicas, expressed without division. -/
theorem compile_key_ratio (groups : List Group) (replicas N : Nat)
    (blocks : Key → Nat) (hids : (flatIds groups).Nodup) (hr : 0 < replicas) :
    (Retention.retained (compileResiduals groups replicas N blocks)).card =
      replicas * (visitWord groups replicas N).toFinset.card := by
  rw [compile_retained_count, visitWord_distinct groups replicas N hr hids]

/-- With multiple replicas and a nonempty key space, wrappers strictly outnumber keys. -/
theorem compile_retained_gt_keys (groups : List Group) (replicas N : Nat)
    (blocks : Key → Nat) (hids : (flatIds groups).Nodup) (hr : 1 < replicas)
    (hR : 0 < (flatIds groups).length) (hN : 0 < N) :
    (visitWord groups replicas N).toFinset.card <
      (Retention.retained (compileResiduals groups replicas N blocks)).card := by
  have hr0 : 0 < replicas := Nat.lt_trans Nat.zero_lt_one hr
  rw [compile_retained_count, visitWord_distinct groups replicas N hr0 hids]
  simpa only [Nat.one_mul] using
    Nat.mul_lt_mul_of_pos_right hr (Nat.mul_pos hR hN)

end CompilerAudit.Composition
