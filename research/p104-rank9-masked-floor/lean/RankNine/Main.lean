import RankNine.Reduce
import RankNine.FactsC3

/-!
# Main theorem: the rank-9 nine-term masked floor `C(P104) ≥ 56`

Hypotheses:
* BForm facts as before (`Capacity`, `BicliqueFact` are Lean theorems; `CensusFact` stays a hypothesis) enter
  through `hFT : ∀ k < 387, FloorType K k` (the 387 kernel-checked per-type floors `Fl<k>.floor`);
* finite facts (certified logs, `MAIN-PLAN.md`): `grpOK`, `orbOK flData`, `flNoFrame flData`, `fc3OK`;
* `T2Pair K flData`: the T2 statement (two independent decoder terms cannot both have dead rows on frameless
  sets); proved separately from the T2 finite facts.

Proof: normal form `P = A U`, `Q = B W` (`col_rep`); a side of label span `≤ 6` (FC3) or a framed big side gives the
floor (`floor_framed`, T1 + T3); otherwise every side has span `≥ 7`, every big side is frameless, and the T2.1 count
(`count_big`) gives two row-big (or column-big) terms: `T2Pair` is contradicted.
-/

namespace RankNine.Main

open Matrix BForm BForm.E8 RankNine.Facts

attribute [local instance] Classical.propDecidable

set_option linter.unusedSectionVars false

variable {K : Type} [Field K] [CharZero K]

/-- **T2** (to be proved from the T2 facts): two independent decoder terms with dead rows on frameless sets
`c, c' ∈ FL` cannot exist. -/
def T2Pair (K : Type) [Field K] [CharZero K] (FL : List ℕ) : Prop :=
  ∀ (A B : ℕ → Fin 9 → K), (∀ x < 104, A x ⬝ᵥ B x ≠ 0) →
    (∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) →
    ∀ (Al Bl : Matrix (Fin 9) (Fin 104) K), Al * Matrix.of (fun (v : Fin 104) (i : Fin 9) => A v i) = 1 →
    Bl * Matrix.of (fun (v : Fin 104) (i : Fin 9) => B v i) = 1 →
    ∀ u v : Fin 9 → K, LinearIndependent K ![u, v] → ∀ c c' : ℕ, FL.contains c = true → FL.contains c' = true →
      (∀ x, c.testBit x = true → A x ⬝ᵥ u = 0) → (∀ x, c'.testBit x = true → A x ⬝ᵥ v = 0) → False

/-- normal form: the decoder columns are `A U` with `U` invertible (left inverse of `A`, factorisation) -/
theorem col_rep (A B : ℕ → Fin 9 → K) (Al Bl : Matrix (Fin 9) (Fin 104) K)
    (hA : Al * Matrix.of (fun (v : Fin 104) (i : Fin 9) => A v i) = 1)
    (hB : Bl * Matrix.of (fun (v : Fin 104) (i : Fin 9) => B v i) = 1)
    (P Q : Matrix (Fin 104) C9 K) (h : Matrix.of (fun v s : Fin 104 => Mx A B v s) = P * Qᵀ) :
    ∃ U : Matrix (Fin 9) C9 K, ∃ V : Matrix C9 (Fin 9) K, V * U = 1 ∧
      ∀ (t : Fin 104) j, P t j = A t ⬝ᵥ fun i => U i j := by
  set Am := Matrix.of (fun (v : Fin 104) (i : Fin 9) => A v i)
  set Bm := Matrix.of (fun (v : Fin 104) (i : Fin 9) => B v i)
  have hN : Matrix.of (fun v s : Fin 104 => Mx A B v s) = Am * Bmᵀ := by
    ext v s; simp [Mx, Am, Bm, Matrix.mul_apply, dotProduct]
  have hAm : Am = P * (Qᵀ * Blᵀ) := by
    calc Am = Am * (Bl * Bm)ᵀ := by rw [hB, transpose_one, Matrix.mul_one]
      _ = (Am * Bmᵀ) * Blᵀ := by rw [transpose_mul, Matrix.mul_assoc]
      _ = P * (Qᵀ * Blᵀ) := by rw [← hN, h, Matrix.mul_assoc]
  set V := Qᵀ * Blᵀ
  set U := Al * P
  have hUV : U * V = 1 := by rw [Matrix.mul_assoc, ← hAm, hA]
  have hVU : V * U = 1 := (Matrix.mul_eq_one_comm_of_card_eq (Fin 9) C9 K (A := U) (B := V) (by simp)).mp hUV
  refine ⟨U, V, hVU, fun t j => ?_⟩
  have hP : P = Am * U := by
    calc P = P * (V * U) := by rw [hVU, Matrix.mul_one]
      _ = Am * U := by rw [← Matrix.mul_assoc, ← hAm]
  rw [hP]
  simp [Am, Matrix.mul_apply, dotProduct]

theorem col_ne {U : Matrix (Fin 9) C9 K} {V : Matrix C9 (Fin 9) K} (hVU : V * U = 1) (j : C9) :
    (fun i => U i j) ≠ 0 := by
  intro h0
  have := congrFun (congrFun hVU j) j
  rw [Matrix.mul_apply, Matrix.one_apply_eq] at this
  simp only [show ∀ i, U i j = 0 from fun i => congrFun h0 i, mul_zero, Finset.sum_const_zero] at this
  exact zero_ne_one this

theorem col_indep {U : Matrix (Fin 9) C9 K} {V : Matrix C9 (Fin 9) K} (hVU : V * U = 1) {j k : C9} (hjk : j ≠ k) :
    LinearIndependent K ![fun i => U i j, fun i => U i k] := by
  rw [LinearIndependent.pair_iff]
  intro s t hst
  have key : ∀ l, s * (V * U) l j + t * (V * U) l k = 0 := by
    intro l
    simp only [Matrix.mul_apply, Finset.mul_sum, ← Finset.sum_add_distrib]
    refine Finset.sum_eq_zero fun i _ => ?_
    have := congrFun hst i
    simp only [Pi.add_apply, Pi.smul_apply, smul_eq_mul, Pi.zero_apply] at this
    calc s * (V l i * U i j) + t * (V l i * U i k) = V l i * (s * U i j + t * U i k) := by ring
      _ = 0 := by rw [this, mul_zero]
  have h1 := key j; have h2 := key k
  rw [hVU, Matrix.one_apply_eq, Matrix.one_apply_ne hjk] at h1
  rw [hVU, Matrix.one_apply_eq, Matrix.one_apply_ne (Ne.symm hjk)] at h2
  simp only [mul_one, mul_zero, add_zero, zero_add] at h1 h2
  exact ⟨h1, h2⟩

/-- dead rows of a side of span `≤ 7` contain `C(z₁, z₂)` -/
theorem dead_of_span {X : Matrix (Fin 104) C9 K} {j : C9} (z1 z2 : V9)
    (hz : ∀ t ∈ rowSupp X j, labK t ⬝ᵥ z1 = 0 ∧ labK t ⬝ᵥ z2 = 0) :
    ∀ x : Fin 104, (labK x ⬝ᵥ z1 ≠ 0 ∨ labK x ⬝ᵥ z2 ≠ 0) → X x j = 0 := by
  intro x hx
  by_contra hne
  have := hz x (by simp [rowSupp, hne])
  rcases hx with e | e
  · exact e this.1
  · exact e this.2

/-- **One side.** A side of span `≤ 7` gives the floor or a frameless dead set `C ∈ FL`; span `≤ 6` gives the floor. -/
theorem side (hFT : ∀ k < 387, FloorType K k) (hgrp : grpOK = true) (horb : orbOK flData = true)
    (hflf : flNoFrame flData = true) (hfc3 : fc3OK = true)
    (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (Al Bl : Matrix (Fin 9) (Fin 104) K) (hA : Al * Matrix.of (fun (v : Fin 104) (i : Fin 9) => A v i) = 1)
    (hB : Bl * Matrix.of (fun (v : Fin 104) (i : Fin 9) => B v i) = 1)
    (P Q : Matrix (Fin 104) C9 K) (h : Matrix.of (fun v s : Fin 104 => Mx A B v s) = P * Qᵀ)
    (U : Matrix (Fin 9) C9 K) (V : Matrix C9 (Fin 9) K) (hVU : V * U = 1)
    (hP : ∀ (t : Fin 104) j, P t j = A t ⬝ᵥ fun i => U i j) (j : C9) :
    (lspan labK (rowSupp P j) ≤ 6 → 56 ≤ cost labK P Q) ∧
    (lspan labK (rowSupp P j) ≤ 7 → 56 ≤ cost labK P Q ∨
      ∃ c, flData.contains c = true ∧ ∀ x, c.testBit x = true → A x ⬝ᵥ (fun i => U i j) = 0) := by
  have hu := col_ne hVU j
  have dead : ∀ z1 z2 : V9, (∀ t ∈ rowSupp P j, labK t ⬝ᵥ z1 = 0 ∧ labK t ⬝ᵥ z2 = 0) →
      ∀ x : Fin 104, (labK x ⬝ᵥ z1 ≠ 0 ∨ labK x ⬝ᵥ z2 ≠ 0) → A x ⬝ᵥ (fun i => U i j) = 0 := by
    intro z1 z2 hz x hx
    rw [← hP]; exact dead_of_span z1 z2 hz x hx
  constructor
  · intro h6
    obtain ⟨z1, z2, z3, n1, n2, n3, d12, d13, d23, d3, hz⟩ := Red.three_dual labK _ h6
    obtain ⟨y1, y2, g1, g2, g12, hspan, hf⟩ := framed_of_three hfc3 z1 z2 z3 n1 n2 n3 d12 d13 d23 d3
    have hz' : ∀ t ∈ rowSupp P j, labK t ⬝ᵥ y1 = 0 ∧ labK t ⬝ᵥ y2 = 0 := fun t ht =>
      hspan _ (hz t ht).1 (hz t ht).2.1 (hz t ht).2.2
    rcases floor_framed hFT hgrp flData horb A B _ hu y1 y2 g1 g2 g12 (dead y1 y2 hz') hdiag hmask Al Bl hA hB
      P Q h with e | e
    · exact e
    · rw [not_FL hflf hf] at e; exact absurd e (by simp)
  · intro h7
    obtain ⟨z1, z2, n1, n2, d12, hz⟩ := Red.two_dual labK _ h7
    rcases floor_framed hFT hgrp flData horb A B _ hu z1 z2 n1 n2 d12 (dead z1 z2 hz) hdiag hmask Al Bl hA hB
      P Q h with e | e
    · exact Or.inl e
    · refine Or.inr ⟨_, e, fun x hx => ?_⟩
      obtain ⟨hy, hpar⟩ := cmask_bit hx
      refine dead z1 z2 hz ⟨x, hy⟩ ?_
      rcases hpar with p | p
      · exact Or.inl ((lab_dot _ _).mpr p)
      · exact Or.inr ((lab_dot _ _).mpr p)

/-- **Main theorem (rank 9).** Every nine-term decoder of a masked rank-9 matrix on P104 costs at least 56. -/
theorem floor56 (hFT : ∀ k < 387, FloorType K k) (hgrp : grpOK = true) (horb : orbOK flData = true)
    (hflf : flNoFrame flData = true) (hfc3 : fc3OK = true) (hT2 : T2Pair K flData)
    (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (Al Bl : Matrix (Fin 9) (Fin 104) K) (hA : Al * Matrix.of (fun (v : Fin 104) (i : Fin 9) => A v i) = 1)
    (hB : Bl * Matrix.of (fun (v : Fin 104) (i : Fin 9) => B v i) = 1)
    (P Q : Matrix (Fin 104) C9 K) (h : Matrix.of (fun v s : Fin 104 => Mx A B v s) = P * Qᵀ) :
    56 ≤ cost labK P Q := by
  by_contra hlt
  push_neg at hlt
  -- transposed problem
  have hdiag' : ∀ x < 104, B x ⬝ᵥ A x ≠ 0 := fun x hx => by rw [dotProduct_comm]; exact hdiag x hx
  have hmask' : ∀ x < 104, ∀ y < 104, orth x y = true → B x ⬝ᵥ A y = 0 := fun x hx y hy ho => by
    rw [dotProduct_comm]; exact hmask y hy x hx (by rw [orth_comm]; exact ho)
  have h' : Matrix.of (fun v s : Fin 104 => Mx B A v s) = Q * Pᵀ := by
    have := congrArg Matrix.transpose h
    rw [transpose_mul, transpose_transpose] at this
    rw [← this]; ext v s; simp [Mx, dotProduct_comm]
  have hcs : cost labK Q P = cost labK P Q := cost_swap labK P Q
  obtain ⟨U, V, hVU, hP⟩ := col_rep A B Al Bl hA hB P Q h
  obtain ⟨W, X, hXW, hQ⟩ := col_rep B A Bl Al hB hA Q P h'
  have SP := side hFT hgrp horb hflf hfc3 A B hdiag hmask Al Bl hA hB P Q h U V hVU hP
  have SQ := side hFT hgrp horb hflf hfc3 B A hdiag' hmask' Bl Al hB hA Q P h' W X hXW hQ
  -- every side has span ≥ 7
  have g7P : ∀ j, 7 ≤ lspan labK (rowSupp P j) := fun j => by
    by_contra hc; exact absurd ((SP j).1 (by omega)) (by omega)
  have g7Q : ∀ j, 7 ≤ lspan labK (rowSupp Q j) := fun j => by
    by_contra hc; have := (SQ j).1 (by omega); rw [hcs] at this; omega
  rcases Red.count_big labK P Q (by simp) hlt g7P g7Q with ⟨j, k, hjk, hj, hk⟩ | ⟨j, k, hjk, hj, hk⟩
  · rcases (SP j).2 hj.le with e | ⟨c, hc, hdc⟩
    · omega
    rcases (SP k).2 hk.le with e | ⟨c', hc', hdc'⟩
    · omega
    exact hT2 A B hdiag hmask Al Bl hA hB _ _ (col_indep hVU hjk) c c' hc hc' hdc hdc'
  · rcases (SQ j).2 hj.le with e | ⟨c, hc, hdc⟩
    · rw [hcs] at e; omega
    rcases (SQ k).2 hk.le with e | ⟨c', hc', hdc'⟩
    · rw [hcs] at e; omega
    exact hT2 B A hdiag' hmask' Bl Al hB hA _ _ (col_indep hXW hjk) c c' hc hc' hdc hdc'

end RankNine.Main
