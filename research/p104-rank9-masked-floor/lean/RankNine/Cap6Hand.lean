import RankNine.FC3Hand
import BForm.E8.Capacity

set_option linter.unusedSectionVars false

/-!
# Cap6 by hand (CENSUS-PLAN §6): a set of at least 21 ports has label span at least 7

If `lspan R ≤ 6`, three independent `z₁, z₂, z₃` kill every label of `R` (`ker_three`).  For a family of labels
`l`, pointwise over the 3-space `W = ⟨z₁, z₂, z₃⟩`: `4 · [l ⊥ W] + #{z ∈ W ∖ 0 : l · z = 1} = 4` (`pt3`), so
`4 |D(W)| + Σ_{z ∈ W ∖ 0} n(z) = 4 · (number of labels)` (`count7`).  We count the 104 ports and, separately, the 16
removed lines (`rlab`; ports and removed lines together are the 120 vectors of weight 3 or 7).  Finite fact
(`cap6OK`, 512 labels, checked by `decide`; Python `cap6hand/check.py`): `N(z) = n_P(z) + n_rm(z)` is `56` with
`wt z ≡ 1, 2 (mod 4)`, or `≥ 64` (the Gauss sum `N(z) = 60 − 4σ(wt z)` of §6).  By the hand lemma
`no_plane3o 1` not all seven `N(z)` are `56`, so `Σ N ≥ 6 · 56 + 64 = 400`, and
`4 |D_P(W)| = 416 − Σ n_P = 416 − Σ N + Σ n_rm ≤ 416 − 400 + 64 = 80`: `|R| ≤ |D_P(W)| ≤ 20`.
-/

namespace RankNine.Facts

open Matrix Finset Module BForm BForm.E8

attribute [local instance] Classical.propDecidable

/-! ## The 16 removed lines -/

/-- labels of the 16 removed lines (the weight-3/7 vectors of `F₂⁹` that are not port labels) -/
def rmBits : List ℕ := [7, 25, 42, 52, 67, 76, 82, 97, 104, 127, 137, 162, 266, 289, 448, 491]

def rbits (i : ℕ) : List ℕ := (List.range 9).map fun k => if (rmBits.getD i 0).testBit k then 1 else 0

def rlab (i : Fin 16) : V9 := fun k => (((rbits i).getD k 0 : ℕ) : ZMod 2)

def rpar (i : ℕ) (l : List ℕ) : Bool := (List.zipWith (· * ·) (rbits i) l).sum % 2 == 1

def nRm (l : List ℕ) : ℕ := (List.range 16).countP fun i => rpar i l

theorem rbits_len (i : ℕ) : (rbits i).length = 9 := by simp [rbits]

theorem rlab_dot (i : Fin 16) (z : V9) : rlab i ⬝ᵥ z ≠ 0 ↔ rpar i (zl z) = true := by
  have h : rlab i ⬝ᵥ z = (((List.zipWith (· * ·) (rbits i) (zl z)).sum : ℕ) : ZMod 2) := by
    rw [sumNat_eq _ _ 9 (rbits_len i) (zl_len z)]
    simp only [dotProduct, rlab, Nat.cast_sum, Nat.cast_mul, zl_getD, ZMod.natCast_zmod_val]
  rw [h, Ne, ZMod.natCast_eq_zero_iff, rpar]
  simp only [beq_iff_eq]
  omega

theorem nRm_card (z : V9) : (univ.filter fun i : Fin 16 => rlab i ⬝ᵥ z ≠ 0).card = nRm (zl z) := by
  rw [nRm, countP_range]
  congr 1
  ext i
  simp only [mem_filter, mem_univ, true_and, rlab_dot]

/-! ## Counting over a 3-space -/

theorem pt3 (a b c : ZMod 2) : 4 * (if a = 0 ∧ b = 0 ∧ c = 0 then 1 else 0) + (if a ≠ 0 then 1 else 0) +
    (if b ≠ 0 then 1 else 0) + (if c ≠ 0 then 1 else 0) + (if a + b ≠ 0 then 1 else 0) +
    (if a + c ≠ 0 then 1 else 0) + (if b + c ≠ 0 then 1 else 0) + (if a + b + c ≠ 0 then 1 else 0) = (4 : ℕ) := by
  revert a b c; decide

theorem count7 {ι : Type*} [Fintype ι] (lab : ι → V9) (z1 z2 z3 : V9) :
    4 * (univ.filter fun t => lab t ⬝ᵥ z1 = 0 ∧ lab t ⬝ᵥ z2 = 0 ∧ lab t ⬝ᵥ z3 = 0).card +
      (univ.filter fun t => lab t ⬝ᵥ z1 ≠ 0).card + (univ.filter fun t => lab t ⬝ᵥ z2 ≠ 0).card +
      (univ.filter fun t => lab t ⬝ᵥ z3 ≠ 0).card + (univ.filter fun t => lab t ⬝ᵥ (z1 + z2) ≠ 0).card +
      (univ.filter fun t => lab t ⬝ᵥ (z1 + z3) ≠ 0).card + (univ.filter fun t => lab t ⬝ᵥ (z2 + z3) ≠ 0).card +
      (univ.filter fun t => lab t ⬝ᵥ (z1 + z2 + z3) ≠ 0).card = 4 * Fintype.card ι := by
  have key : ∀ t ∈ (univ : Finset ι),
      4 * (if lab t ⬝ᵥ z1 = 0 ∧ lab t ⬝ᵥ z2 = 0 ∧ lab t ⬝ᵥ z3 = 0 then 1 else 0) +
        (if lab t ⬝ᵥ z1 ≠ 0 then 1 else 0) + (if lab t ⬝ᵥ z2 ≠ 0 then 1 else 0) +
        (if lab t ⬝ᵥ z3 ≠ 0 then 1 else 0) + (if lab t ⬝ᵥ (z1 + z2) ≠ 0 then 1 else 0) +
        (if lab t ⬝ᵥ (z1 + z3) ≠ 0 then 1 else 0) + (if lab t ⬝ᵥ (z2 + z3) ≠ 0 then 1 else 0) +
        (if lab t ⬝ᵥ (z1 + z2 + z3) ≠ 0 then 1 else 0) = 4 := by
    intro t _
    have e1 : lab t ⬝ᵥ (z1 + z2) = lab t ⬝ᵥ z1 + lab t ⬝ᵥ z2 := dotProduct_add _ _ _
    have e2 : lab t ⬝ᵥ (z1 + z3) = lab t ⬝ᵥ z1 + lab t ⬝ᵥ z3 := dotProduct_add _ _ _
    have e3 : lab t ⬝ᵥ (z2 + z3) = lab t ⬝ᵥ z2 + lab t ⬝ᵥ z3 := dotProduct_add _ _ _
    have e4 : lab t ⬝ᵥ (z1 + z2 + z3) = lab t ⬝ᵥ z1 + lab t ⬝ᵥ z2 + lab t ⬝ᵥ z3 := by
      rw [dotProduct_add, dotProduct_add]
    rw [e1, e2, e3, e4]
    exact pt3 _ _ _
  rw [Finset.card_filter, Finset.card_filter, Finset.card_filter, Finset.card_filter, Finset.card_filter,
    Finset.card_filter, Finset.card_filter, Finset.card_filter, Finset.mul_sum, ← Finset.sum_add_distrib,
    ← Finset.sum_add_distrib, ← Finset.sum_add_distrib, ← Finset.sum_add_distrib, ← Finset.sum_add_distrib,
    ← Finset.sum_add_distrib, ← Finset.sum_add_distrib, Finset.sum_congr rfl key, Finset.sum_const,
    Finset.card_univ, smul_eq_mul, Nat.mul_comm]

/-- `lspan R ≤ 6`: three independent vectors kill the labels of `R` -/
theorem ker_three (R : Finset (Fin 104)) (h : lspan labK R ≤ 6) :
    ∃ z1 z2 z3 : V9, z1 ≠ 0 ∧ z2 ≠ 0 ∧ z3 ≠ 0 ∧ z1 ≠ z2 ∧ z1 ≠ z3 ∧ z2 ≠ z3 ∧ z3 ≠ z1 + z2 ∧
      ∀ t ∈ R, labK t ⬝ᵥ z1 = 0 ∧ labK t ⬝ᵥ z2 = 0 ∧ labK t ⬝ᵥ z3 = 0 := by
  set f := (labMat labK R).mulVecLin with hf
  have hr : finrank (ZMod 2) (LinearMap.range f) ≤ 6 := h
  have hrn := LinearMap.finrank_range_add_finrank_ker f
  have h9 : finrank (ZMod 2) (Fin 9 → ZMod 2) = 9 := Module.finrank_fin_fun _
  have hk : 3 ≤ finrank (ZMod 2) (LinearMap.ker f) := by omega
  have hc : 8 ≤ Fintype.card (LinearMap.ker f) := by
    rw [Module.card_eq_pow_finrank (K := ZMod 2) (V := LinearMap.ker f), ZMod.card]
    calc 8 = 2 ^ 3 := by norm_num
      _ ≤ 2 ^ finrank (ZMod 2) (LinearMap.ker f) := Nat.pow_le_pow_right (by norm_num) hk
  have h1 : 1 < ((Finset.univ : Finset (LinearMap.ker f)).erase 0).card := by
    rw [Finset.card_erase_of_mem (Finset.mem_univ _), Finset.card_univ]; omega
  obtain ⟨x, hx, y, hy, hxy⟩ := Finset.one_lt_card.mp h1
  simp only [Finset.mem_erase, Finset.mem_univ, and_true] at hx hy
  have h3 : ∃ w : LinearMap.ker f, w ∉ ({0, x, y, x + y} : Finset (LinearMap.ker f)) := by
    by_contra hcon
    push_neg at hcon
    have hsub : (Finset.univ : Finset (LinearMap.ker f)) ⊆ {0, x, y, x + y} := fun w _ => hcon w
    have hle := Finset.card_le_card hsub
    have c1 := Finset.card_insert_le (0 : LinearMap.ker f) ({x, y, x + y} : Finset (LinearMap.ker f))
    have c2 := Finset.card_insert_le x ({y, x + y} : Finset (LinearMap.ker f))
    have c3 := Finset.card_insert_le y ({x + y} : Finset (LinearMap.ker f))
    have c4 := Finset.card_singleton (x + y)
    rw [Finset.card_univ] at hle
    omega
  obtain ⟨w, hw⟩ := h3
  simp only [Finset.mem_insert, Finset.mem_singleton, not_or] at hw
  obtain ⟨hw0, hwx, hwy, hwxy⟩ := hw
  have mem : ∀ v : LinearMap.ker f, ∀ t ∈ R, labK t ⬝ᵥ (v : V9) = 0 := by
    intro v t ht
    have h0 : (labMat labK R).mulVecLin (v : V9) = 0 := LinearMap.mem_ker.mp v.2
    have := congrFun h0 ⟨t, ht⟩
    rw [Matrix.mulVecLin_apply] at this
    exact this
  refine ⟨x, y, w, fun e => hx (Subtype.ext e), fun e => hy (Subtype.ext e), fun e => hw0 (Subtype.ext e),
    fun e => hxy (Subtype.ext e), fun e => hwx (Subtype.ext e).symm, fun e => hwy (Subtype.ext e).symm,
    fun e => hwxy (Subtype.ext e), fun t ht => ⟨mem x t ht, mem y t ht, mem w t ht⟩⟩

/-! ## The finite fact and the bound -/

def cap6At (n : ℕ) : Bool :=
  n == 0 || (nOdd (lz n) + nRm (lz n) == 56 && (wt n % 4 == 1 || wt n % 4 == 2)) ||
    decide (64 ≤ nOdd (lz n) + nRm (lz n))

/-- **finite fact (Gauss sum of §6)**: `N(z) = 56` with `wt z ≡ 1, 2 (mod 4)`, or `N(z) ≥ 64` -/
def cap6OK : Bool := (List.range 512).all cap6At

theorem fact56 (h : cap6OK = true) {n : ℕ} (hn : n < 512) (h0 : n ≠ 0) :
    56 ≤ nOdd (lz n) + nRm (lz n) ∧ (nOdd (lz n) + nRm (lz n) < 64 → PhO 1 n) := by
  have e := List.all_eq_true.mp h n (List.mem_range.mpr hn)
  unfold cap6At at e
  simp only [Bool.or_eq_true, Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq] at e
  rcases e with (e | ⟨e, w⟩) | e
  · exact absurd e h0
  · refine ⟨by omega, fun _ => ?_⟩
    unfold PhO
    omega
  · exact ⟨by omega, fun hl => absurd e (by omega)⟩

/-- **Cap6 for P104, by hand** (with the finite fact `cap6OK`). -/
theorem cap6_hand (hc : cap6OK = true) : ∀ R : Finset (Fin 104), 21 ≤ R.card → 7 ≤ lspan labK R := by
  intro R hR
  by_contra hlt
  obtain ⟨z1, z2, z3, h1, h2, h3, h12, h13, h23, h312, hz⟩ := ker_three R (by omega)
  obtain ⟨a, ha, ea⟩ := exists_lz z1
  obtain ⟨b, hb, eb⟩ := exists_lz z2
  obtain ⟨c, hcc, ec⟩ := exists_lz z3
  have zne : ∀ {n : ℕ} {z : V9}, n < 512 → lz n = zl z → z ≠ 0 → n ≠ 0 := by
    intro n z hn e hz h0; subst h0; rw [lz_zero] at e; exact hz (zl_zero e.symm)
  have xab : lz (a ^^^ b) = zl (z1 + z2) := by rw [lz_xor, ea, eb, zl_add]
  have xac : lz (a ^^^ c) = zl (z1 + z3) := by rw [lz_xor, ea, ec, zl_add]
  have xbc : lz (b ^^^ c) = zl (z2 + z3) := by rw [lz_xor, eb, ec, zl_add]
  have xabc : lz ((a ^^^ b) ^^^ c) = zl (z1 + z2 + z3) := by rw [lz_xor, xab, ec, zl_add]
  have s0 : ∀ {p q : V9}, p ≠ q → p + q ≠ 0 := fun hpq e => hpq (v9_eq_of_add e)
  have n123 : z1 + z2 + z3 ≠ 0 := fun e => h312 (v9_eq_of_add e).symm
  have hsub : R ⊆ univ.filter fun t : Fin 104 => labK t ⬝ᵥ z1 = 0 ∧ labK t ⬝ᵥ z2 = 0 ∧ labK t ⬝ᵥ z3 = 0 := by
    intro t ht
    simp only [mem_filter, mem_univ, true_and]
    exact hz t ht
  have hcard := Finset.card_le_card hsub
  have hP := count7 labK z1 z2 z3
  have hQ := count7 rlab z1 z2 z3
  simp only [nOdd_card, nRm_card, Fintype.card_fin] at hP hQ
  rw [← ea, ← eb, ← ec, ← xab, ← xac, ← xbc, ← xabc] at hP hQ
  obtain ⟨g1, p1⟩ := fact56 hc ha (zne ha ea h1)
  obtain ⟨g2, p2⟩ := fact56 hc hb (zne hb eb h2)
  obtain ⟨g3, p3⟩ := fact56 hc hcc (zne hcc ec h3)
  obtain ⟨g4, p4⟩ := fact56 hc (x512 ha hb) (zne (x512 ha hb) xab (s0 h12))
  obtain ⟨g5, p5⟩ := fact56 hc (x512 ha hcc) (zne (x512 ha hcc) xac (s0 h13))
  obtain ⟨g6, p6⟩ := fact56 hc (x512 hb hcc) (zne (x512 hb hcc) xbc (s0 h23))
  obtain ⟨g7, p7⟩ := fact56 hc (x512 (x512 ha hb) hcc) (zne (x512 (x512 ha hb) hcc) xabc n123)
  have hsum : 400 ≤ nOdd (lz a) + nRm (lz a) + (nOdd (lz b) + nRm (lz b)) + (nOdd (lz c) + nRm (lz c)) +
      (nOdd (lz (a ^^^ b)) + nRm (lz (a ^^^ b))) + (nOdd (lz (a ^^^ c)) + nRm (lz (a ^^^ c))) +
      (nOdd (lz (b ^^^ c)) + nRm (lz (b ^^^ c))) + (nOdd (lz ((a ^^^ b) ^^^ c)) + nRm (lz ((a ^^^ b) ^^^ c))) := by
    by_contra hs
    exact no_plane3o 1 (Or.inl rfl) a b c (p1 (by omega)) (p2 (by omega)) (p3 (by omega)) (p4 (by omega))
      (p5 (by omega)) (p6 (by omega)) (p7 (by omega))
  omega

end RankNine.Facts
