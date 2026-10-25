/-
Copyright (c) 2026 conorholds. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Prepared with substantial OpenAI Codex assistance.
-/
import Init

/-!
# Partial actual-basis equality arithmetic

This Init-only file proves the natural-number consequence of the written
actual-basis count. It does not derive the count, feasible-root rank bound,
or missing-low implication from scalar spaces or E8 geometry.
-/

namespace CoupledPartialBasis

/-- A bill-72 basis cannot omit a low direction when the scalar root rank
is at most eight and a single missing direction leaves a positive low bill.
All links from these numbers to an actual reader basis are explicit premises.
-/
theorem equality_forces_zero_missing_low
    (d κ r W : Nat)
    (root_rank_cap : r ≤ 8)
    (actual_basis_count : 72 + 8 * d + κ ≤ W + r)
    (equality_bill : W = 72)
    (single_missing_has_low : d = 1 → 1 ≤ κ) : d = 0 := by
  have hcancel : 8 * d + κ ≤ r := by
    apply Nat.le_of_add_le_add_left (a := 72)
    simpa [equality_bill, Nat.add_assoc] using actual_basis_count
  have hsmall : 8 * d + κ ≤ 8 := Nat.le_trans hcancel root_rank_cap
  cases d with
  | zero => rfl
  | succ d =>
    cases d with
    | zero =>
      have hlow : 1 ≤ κ := single_missing_has_low rfl
      have hlarge : 9 ≤ 8 + κ := Nat.add_le_add_left hlow 8
      have hupper : 8 + κ ≤ 8 := by simpa using hsmall
      exact False.elim ((by decide : ¬ (9 ≤ 8)) (Nat.le_trans hlarge hupper))
    | succ d =>
      have htwo : 2 ≤ Nat.succ (Nat.succ d) :=
        Nat.succ_le_succ (Nat.succ_le_succ (Nat.zero_le d))
      have hlarge : 16 ≤ 8 * Nat.succ (Nat.succ d) :=
        Nat.mul_le_mul_left 8 htwo
      have hupper : 8 * Nat.succ (Nat.succ d) ≤ 8 :=
        Nat.le_trans (Nat.le_add_right _ κ) hsmall
      exact False.elim ((by decide : ¬ (16 ≤ 8)) (Nat.le_trans hlarge hupper))

#print axioms equality_forces_zero_missing_low

end CoupledPartialBasis
