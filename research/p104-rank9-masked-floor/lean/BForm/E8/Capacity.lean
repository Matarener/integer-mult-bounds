import BForm.E8.Labels

/-!
# Capacity for P104 (`f(7) = 36`): a set of at least 37 ports has label span at least 8

Hand argument.  If `lspan R ≤ 7`, the label matrix of `R` has a kernel of dimension `≥ 2` (rank-nullity over
`F₂`), so two distinct non-zero `z₁, z₂` annihilate every label of `R`.  Pointwise
`2·[a = 0 ∧ b = 0] + [a ≠ 0] + [b ≠ 0] + [a + b ≠ 0] = 2` gives `2 |D| + n(z₁) + n(z₂) + n(z₁ + z₂) = 208`
for `D` = ports killed by both and `n(z)` = number of ports with odd `l_t·z`.  Finite facts (`capOK`, 512 labels):
`n(z) ≥ 44`, `n(z) ≡ 0 (mod 4)`, and `n(z) = 44` only for the 12 vectors of `E44`, no two of which sum to a third
(`e44OK`).  Hence `n₁ + n₂ + n₃ ≥ 136` and `|R| ≤ |D| ≤ 36`.
-/

namespace BForm.E8

open Matrix Finset Module

attribute [local instance] Classical.propDecidable

set_option linter.unusedSectionVars false

/-- number of ports with odd product against the 0/1 list `l` -/
def nOdd (l : List ℕ) : ℕ := (List.range 104).countP fun t => par t l

def E44 : List (List ℕ) :=
  [[1, 1, 1, 0, 1, 0, 1, 0, 0], [0, 0, 1, 1, 1, 1, 1, 0, 0], [1, 0, 1, 1, 1, 0, 0, 1, 0], [0, 1, 1, 0, 1, 1, 0, 1, 0],
   [1, 0, 1, 0, 1, 1, 0, 0, 1], [1, 0, 0, 1, 1, 0, 0, 1, 1], [0, 1, 0, 1, 0, 1, 0, 1, 1], [0, 0, 1, 0, 1, 1, 0, 1, 1],
   [0, 0, 1, 1, 0, 0, 1, 1, 1], [0, 1, 0, 0, 1, 0, 1, 1, 1], [0, 0, 1, 0, 1, 0, 1, 1, 1], [1, 0, 0, 0, 0, 1, 1, 1, 1]]

def xorL (a b : List ℕ) : List ℕ := (List.range 9).map fun k => (a.getD k 0 + b.getD k 0) % 2

def capOK : Bool := lists9.all fun l => l == zero9 ||
  (decide (44 ≤ nOdd l) && nOdd l % 4 == 0 && (nOdd l != 44 || decide (l ∈ E44)))

def e44OK : Bool := E44.all fun a => E44.all fun b => a == b || !decide (xorL a b ∈ E44)

set_option maxRecDepth 100000 in
theorem capOK_true : capOK = true := by decide +kernel

theorem e44OK_true : e44OK = true := by decide +kernel

theorem nOdd_card (z : V9) : (univ.filter fun t : Fin 104 => labK t ⬝ᵥ z ≠ 0).card = nOdd (zl z) := by
  rw [nOdd, countP_range]
  congr 1
  ext t
  simp only [mem_filter, mem_univ, true_and, lab_dot]

theorem zl_inj {a b : V9} (h : zl a = zl b) : a = b := by
  funext k
  have := congrArg (fun l => l.getD k 0) h
  simp only [zl_getD] at this
  exact ZMod.val_injective _ this

theorem zl_add (a b : V9) : zl (a + b) = xorL (zl a) (zl b) := by
  apply List.ext_getElem
  · simp [zl, xorL]
  · intro i h1 h2
    have hi : i < 9 := by simpa [zl] using h1
    have e1 : (zl a).getD i 0 = (a ⟨i, hi⟩).val := zl_getD a ⟨i, hi⟩
    have e2 : (zl b).getD i 0 = (b ⟨i, hi⟩).val := zl_getD b ⟨i, hi⟩
    have e3 : (zl (a + b)).getD i 0 = ((a + b) ⟨i, hi⟩).val := zl_getD (a + b) ⟨i, hi⟩
    rw [← List.getD_eq_getElem _ 0 h1, e3]
    simp only [xorL, List.getElem_map, List.getElem_range]
    rw [e1, e2, Pi.add_apply, ZMod.val_add]

theorem ker_two (R : Finset (Fin 104)) (h : lspan labK R ≤ 7) :
    ∃ z1 z2 : V9, z1 ≠ 0 ∧ z2 ≠ 0 ∧ z1 ≠ z2 ∧ ∀ t ∈ R, labK t ⬝ᵥ z1 = 0 ∧ labK t ⬝ᵥ z2 = 0 := by
  set f := (labMat labK R).mulVecLin with hf
  have hr : finrank (ZMod 2) (LinearMap.range f) ≤ 7 := h
  have hrn := LinearMap.finrank_range_add_finrank_ker f
  have h9 : finrank (ZMod 2) V9 = 9 := by simp
  have hk : 2 ≤ finrank (ZMod 2) (LinearMap.ker f) := by omega
  have hc : 4 ≤ Fintype.card (LinearMap.ker f) := by
    rw [Module.card_eq_pow_finrank (K := ZMod 2) (V := LinearMap.ker f), ZMod.card]
    calc 4 = 2 ^ 2 := by norm_num
      _ ≤ 2 ^ finrank (ZMod 2) (LinearMap.ker f) := Nat.pow_le_pow_right (by norm_num) hk
  have h1 : 1 < ((Finset.univ : Finset (LinearMap.ker f)).erase 0).card := by
    rw [Finset.card_erase_of_mem (Finset.mem_univ _), Finset.card_univ]; omega
  obtain ⟨x, hx, y, hy, hxy⟩ := Finset.one_lt_card.mp h1
  simp only [Finset.mem_erase, Finset.mem_univ, and_true] at hx hy
  have mem : ∀ w : LinearMap.ker f, ∀ t ∈ R, labK t ⬝ᵥ (w : V9) = 0 := by
    intro w t ht
    have := congrFun (LinearMap.mem_ker.mp w.2) ⟨t, ht⟩
    simpa [hf, labMat, Matrix.mulVec] using this
  refine ⟨x, y, fun e => hx (Subtype.ext e), fun e => hy (Subtype.ext e), fun e => hxy (Subtype.ext e),
    fun t ht => ⟨mem x t ht, mem y t ht⟩⟩

theorem pt2 (a b : ZMod 2) : 2 * (if a = 0 ∧ b = 0 then 1 else 0) + (if a ≠ 0 then 1 else 0) +
    (if b ≠ 0 then 1 else 0) + (if a + b ≠ 0 then 1 else 0) = (2 : ℕ) := by
  revert a b; decide

theorem count_id (z1 z2 : V9) :
    2 * (univ.filter fun t : Fin 104 => labK t ⬝ᵥ z1 = 0 ∧ labK t ⬝ᵥ z2 = 0).card +
      (univ.filter fun t : Fin 104 => labK t ⬝ᵥ z1 ≠ 0).card +
      (univ.filter fun t : Fin 104 => labK t ⬝ᵥ z2 ≠ 0).card +
      (univ.filter fun t : Fin 104 => labK t ⬝ᵥ (z1 + z2) ≠ 0).card = 208 := by
  simp only [Finset.card_filter, Finset.mul_sum, ← Finset.sum_add_distrib]
  rw [Finset.sum_congr rfl fun t _ => by rw [dotProduct_add]; exact pt2 _ _]
  simp

theorem fact44 {z : V9} (hz : z ≠ 0) :
    44 ≤ nOdd (zl z) ∧ nOdd (zl z) % 4 = 0 ∧ (nOdd (zl z) = 44 → zl z ∈ E44) := by
  have h := (List.all_eq_true.mp capOK_true) (zl z) (zl_mem z)
  have hne : ¬ zl z = zero9 := fun e => hz (zl_zero e)
  simp only [Bool.or_eq_true, beq_iff_eq, hne, false_or, Bool.and_eq_true, decide_eq_true_eq,
    bne_iff_ne, ne_eq] at h
  obtain ⟨⟨h1, h2⟩, h3⟩ := h
  refine ⟨h1, h2, fun e => ?_⟩
  rcases h3 with h3 | h3
  · exact absurd e h3
  · exact h3

/-- **Capacity for P104.** -/
theorem capacity_P104 : BForm.Capacity labK := by
  intro R hR
  by_contra hlt
  obtain ⟨z1, z2, h1, h2, h12, hz⟩ := ker_two R (by omega)
  have h3 : z1 + z2 ≠ 0 := by
    intro e
    apply h12
    funext k
    have := congrFun e k
    simp only [Pi.add_apply, Pi.zero_apply] at this
    revert this
    generalize z1 k = a
    generalize z2 k = b
    revert a b
    decide
  have hsub : R ⊆ univ.filter fun t : Fin 104 => labK t ⬝ᵥ z1 = 0 ∧ labK t ⬝ᵥ z2 = 0 := by
    intro t ht
    simp only [mem_filter, mem_univ, true_and]
    exact hz t ht
  have hcard := Finset.card_le_card hsub
  have hid := count_id z1 z2
  rw [nOdd_card, nOdd_card, nOdd_card] at hid
  obtain ⟨a1, b1, c1⟩ := fact44 h1
  obtain ⟨a2, b2, c2⟩ := fact44 h2
  obtain ⟨a3, b3, c3⟩ := fact44 h3
  have hnot : ¬ (nOdd (zl z1) = 44 ∧ nOdd (zl z2) = 44 ∧ nOdd (zl (z1 + z2)) = 44) := by
    rintro ⟨e1, e2, e3⟩
    have m1 := c1 e1
    have m2 := c2 e2
    have m3 := c3 e3
    have h := (List.all_eq_true.mp e44OK_true) _ m1
    have h' := (List.all_eq_true.mp h) _ m2
    simp only [Bool.or_eq_true, beq_iff_eq, Bool.not_eq_true', decide_eq_false_iff_not] at h'
    rcases h' with h' | h'
    · exact h12 (zl_inj h')
    · rw [zl_add] at m3; exact h' m3
  omega

end BForm.E8
