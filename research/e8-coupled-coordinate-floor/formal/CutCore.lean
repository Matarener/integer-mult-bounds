/-
Copyright (c) 2026 conorholds. All rights reserved.
Released under Apache 2.0 license as described in the repository LICENSE.
Prepared with substantial OpenAI Codex assistance.
-/
import Init

/-!
# Partial core of the actual-basis cut argument

This file isolates two pieces of the written coupling proof:

* an actual additive evaluation map annihilating a set cannot simultaneously
  annihilate q0, take value one at qh, and annihilate q0 + qh;
* natural-number tariffs below the basis floor force an equality basis, zero extra
  regular readers, a one-unit hole rebate, and a zero singleton-pivot bill.

Addition preservation, zero-addition and zero/one separation are explicit
laws of the scalar model in this Init-only file. A Mathlib linear-functional
or submodule bridge is NOT derived here. The E8 singleton-ray classification,
binary pairing tariffs, existence of the actual reader basis, its basis-weight
floor, and its support-cut spanning property are also NOT derived here.
Neither the general exact-factorization theorem nor its E8 application is
claimed as formalized by this file.
-/

namespace CoupledCoordinateCut

section LinearCut

variable {K V : Type} [Zero K] [One K] [Add K] [Add V]

/-- The actual evaluation-map contradiction. The map is evaluated on vectors,
and its addition-preservation law derives the key scalar equation. A future
linear-map instantiation must discharge these explicit scalar laws. -/
theorem cut_contradiction (T : V → Prop) (φ : V → K)
    (q0 qh : V)
    (map_add : ∀ x y, φ (x + y) = φ x + φ y)
    (zero_add : ∀ k : K, 0 + k = k)
    (zero_ne_one : (0 : K) ≠ 1)
    (annihilates : ∀ t, T t → φ t = 0)
    (hole_coordinate : φ qh = 1)
    (quotient_relation : T (q0 + qh))
    (cut_coordinate : φ q0 = 0) : False := by
  have hzero := annihilates (q0 + qh) quotient_relation
  rw [map_add, cut_coordinate, hole_coordinate, zero_add] at hzero
  exact zero_ne_one hzero.symm

end LinearCut

section NaturalTariffs

/-- Only the critical tariff state can violate the floor. W is the actual
selected basis weight, extra is the regular-reader surplus bound, rebate is
the hole rebate, and pivot is the singleton bill. The tariff bound is written
additively over Nat to avoid truncating subtraction. All links from these
numbers to decoder supports remain written-proof obligations. -/
theorem below_floor_forces_critical_state
    (L W extra rebate pivot COPY : Nat)
    (basis_floor : L ≤ W)
    (rebate_at_most_one : rebate ≤ 1)
    (tariff_bound : W + extra + pivot ≤ COPY + rebate)
    (below_floor : COPY < L) :
    W = L ∧ extra = 0 ∧ rebate = 1 ∧ pivot = 0 := by
  have hupper : COPY + rebate < L + 1 :=
    Nat.lt_of_lt_of_le (Nat.add_lt_add_right below_floor rebate)
      (Nat.add_le_add_left rebate_at_most_one L)
  have htotal : W + extra + pivot ≤ L :=
    Nat.le_of_lt_succ (Nat.lt_of_le_of_lt tariff_bound hupper)
  have hWle : W ≤ W + extra + pivot :=
    Nat.le_trans (Nat.le_add_right W extra) (Nat.le_add_right (W + extra) pivot)
  have hW : W = L := Nat.le_antisymm (Nat.le_trans hWle htotal) basis_floor
  have hzero : extra + pivot ≤ 0 := by
    apply Nat.le_of_add_le_add_left (a := L)
    simpa [hW, Nat.add_assoc] using htotal
  have hparts : extra = 0 ∧ pivot = 0 :=
    Nat.add_eq_zero.mp (Nat.eq_zero_of_le_zero hzero)
  have hrebate_ne : rebate ≠ 0 := by
    intro hz
    have hpaid : L ≤ COPY := by
      simpa [hW, hparts.1, hparts.2, hz] using tariff_bound
    exact Nat.not_le_of_lt below_floor hpaid
  have hrebate : rebate = 1 :=
    Nat.le_antisymm rebate_at_most_one (Nat.pos_of_ne_zero hrebate_ne)
  exact ⟨hW, hparts.1, hrebate, hparts.2⟩

/-- A strict one-sided basis floor pays the only possible hole rebate. No
 equality-basis cut condition is needed in this branch. -/
theorem strict_basis_floor_pays_rebate
    (L W extra rebate pivot COPY : Nat)
    (strict_basis_floor : L + 1 ≤ W)
    (rebate_at_most_one : rebate ≤ 1)
    (tariff_bound : W + extra + pivot ≤ COPY + rebate) : L ≤ COPY := by
  have hWle : W ≤ W + extra + pivot :=
    Nat.le_trans (Nat.le_add_right W extra) (Nat.le_add_right (W + extra) pivot)
  have hupper : W ≤ COPY + 1 :=
    Nat.le_trans (Nat.le_trans hWle tariff_bound)
      (Nat.add_le_add_left rebate_at_most_one COPY)
  exact Nat.le_of_add_le_add_right (Nat.le_trans strict_basis_floor hupper)

/-- The tariff reduction combined with a separately supplied obstruction to
 the critical equality state. The functional cut lemma above supplies the
 final contradiction once the actual reader basis and its cut geometry have
 supplied its hypotheses; that geometric bridge is not formalized here. -/
theorem floor_of_critical_state_impossible
    (L W extra rebate pivot COPY : Nat)
    (basis_floor : L ≤ W)
    (rebate_at_most_one : rebate ≤ 1)
    (tariff_bound : W + extra + pivot ≤ COPY + rebate)
    (critical_impossible :
      W = L → extra = 0 → rebate = 1 → pivot = 0 → False) : L ≤ COPY := by
  apply Nat.ge_of_not_lt
  intro below_floor
  have critical := below_floor_forces_critical_state
    L W extra rebate pivot COPY basis_floor rebate_at_most_one
    tariff_bound below_floor
  exact critical_impossible critical.1 critical.2.1
    critical.2.2.1 critical.2.2.2

end NaturalTariffs

#print axioms cut_contradiction
#print axioms below_floor_forces_critical_state
#print axioms strict_basis_floor_pays_rebate
#print axioms floor_of_critical_state_impossible

end CoupledCoordinateCut
