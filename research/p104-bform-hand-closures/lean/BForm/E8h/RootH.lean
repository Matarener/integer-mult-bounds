import BForm.E8h.Dom
import BForm.CaseI

/-!
# RootFact for P104 from the dominant chamber argument

`dom`: every non-zero rational vector has `Shape`.  `rootQ`: a non-zero rational vector is non-orthogonal to at
least 49 ports.  `reduce`: a non-zero vector over a field of characteristic zero has a non-zero rational partner
orthogonal to (at least) the same roots.  `rootFact_h`: `BForm.RootFact` for the ports of P104.
-/

namespace BForm.E8h

set_option linter.unusedSectionVars false

open Matrix Finset BForm.E8

theorem Zc_dom (y : V) (hd : ∀ i < 8, 0 ≤ lv ℚ i ⬝ᵥ y) (b : ℕ → Bool)
    (hb : ∀ i < 8, b i = decide (lv ℚ i ⬝ᵥ y = 0)) : Zc y = cnt b := by
  unfold Zc cnt
  rw [countP_range]
  congr 1
  apply Finset.filter_congr
  intro j _
  rw [all_range, lv_dot_coef j j.2,
    Finset.sum_eq_zero_iff_of_nonneg (fun (i : Fin 8) _ => mul_nonneg (Nat.cast_nonneg _) (hd i i.2))]
  constructor
  · intro h i hi
    rcases mul_eq_zero.mp (h ⟨i, hi⟩ (mem_univ _)) with h0 | h0
    · simp only [Bool.or_eq_true, beq_iff_eq]; left; exact_mod_cast h0
    · simp only [Bool.or_eq_true, beq_iff_eq, hb i hi, decide_eq_true_eq]; right; exact h0
  · intro h i _
    have := h i i.2
    simp only [Bool.or_eq_true, beq_iff_eq, hb i i.2, decide_eq_true_eq] at this
    rcases this with h0 | h0
    · simp [h0]
    · simp [h0]

theorem shape_dom (y : V) (hd : ∀ i < 8, 0 ≤ lv ℚ i ⬝ᵥ y) : Shape y := by
  have hb : ∀ i < 8, bv (decide (lv ℚ 0 ⬝ᵥ y = 0)) (decide (lv ℚ 1 ⬝ᵥ y = 0)) (decide (lv ℚ 2 ⬝ᵥ y = 0))
      (decide (lv ℚ 3 ⬝ᵥ y = 0)) (decide (lv ℚ 4 ⬝ᵥ y = 0)) (decide (lv ℚ 5 ⬝ᵥ y = 0))
      (decide (lv ℚ 6 ⬝ᵥ y = 0)) (decide (lv ℚ 7 ⬝ᵥ y = 0)) i = decide (lv ℚ i ⬝ᵥ y = 0) := by
    intro i hi; interval_cases i <;> rfl
  have hZ := Zc_dom y hd _ hb
  have hp := paraP_true (decide (lv ℚ 0 ⬝ᵥ y = 0)) (decide (lv ℚ 1 ⬝ᵥ y = 0)) (decide (lv ℚ 2 ⬝ᵥ y = 0))
      (decide (lv ℚ 3 ⬝ᵥ y = 0)) (decide (lv ℚ 4 ⬝ᵥ y = 0)) (decide (lv ℚ 5 ⬝ᵥ y = 0))
      (decide (lv ℚ 6 ⬝ᵥ y = 0)) (decide (lv ℚ 7 ⬝ᵥ y = 0))
  rw [paraP] at hp
  simp only [Bool.or_eq_true, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at hp
  rw [← hZ] at hp
  rcases hp with (h | ⟨⟨⟨⟨⟨⟨h0, h1⟩, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩) | ⟨⟨⟨⟨⟨⟨⟨h1, h2⟩, h3⟩, h4⟩, h5⟩, h6⟩, h7⟩, h42⟩
  · left; exact h
  · right; right
    rw [lv_eq_0] at h0; rw [lv_eq_1] at h1; rw [lv_eq_2] at h2; rw [lv_eq_3] at h3
    rw [lv_eq_4] at h4; rw [lv_eq_5] at h5; rw [lv_eq_6] at h6
    refine ⟨119, by norm_num, ((![0, 0, 0, 0, 0, 0, 2, 2] : Fin 8 → ℚ) ⬝ᵥ y) / 8, ?_⟩
    rw [lv_eq_119]
    exact e7_cert y h0 h1 h2 h3 h4 h5 h6
  · right; left
    refine ⟨by omega, 99, 119, by norm_num, by norm_num, ?_, ((![0, 0, 0, 0, 0, 0, 0, 4] : Fin 8 → ℚ) ⬝ᵥ y) / 16, 1,
      Or.inl rfl, ?_⟩
    · rw [lv_eq_99, lv_eq_119]; simp [dotProduct, Fin.sum_univ_eight]
    rw [lv_eq_1] at h1; rw [lv_eq_2] at h2; rw [lv_eq_3] at h3; rw [lv_eq_4] at h4
    rw [lv_eq_5] at h5; rw [lv_eq_6] at h6; rw [lv_eq_7] at h7
    have e : (lv ℚ 99 + (1 : ℚ) • lv ℚ 119) = (![0, 0, 0, 0, 0, 0, 0, 4] : Fin 8 → ℚ) := by
      rw [lv_eq_99, lv_eq_119]; ext k; fin_cases k <;> simp <;> norm_num
    rw [e]
    exact d7_cert y h1 h2 h3 h4 h5 h6 h7

/-- every non-zero rational vector has `Shape` -/
theorem dom (y : V) (hy : y ≠ 0) : Shape y := by
  induction h : nNeg y using Nat.strong_induction_on generalizing y with
  | _ n ih =>
    by_cases hd : ∃ i < 8, lv ℚ i ⬝ᵥ y < 0
    · obtain ⟨i, hi, hneg⟩ := hd
      have h1 := nNeg_sr i hi y hneg
      exact shape_of_sr i hi y (ih (nNeg (sr i y)) (by omega) (sr i y) (sr_ne_zero i hi y hy) rfl)
    · push Not at hd; exact shape_dom y hd

/-! ## Ports -/

theorem port_spec (t : ℕ) (ht : t < 104) : pl t < 120 ∧ (ps t = 1 ∨ ps t = -1) ∧
    ∀ k < 8, (r8 t).getD k 0 = ps t * (pr (pl t)).getD k 0 := by
  have h := portOK_true
  simp only [portOK, Bool.and_eq_true] at h
  have h' := all_range.mp h.1 t ht
  simp only [Bool.and_eq_true, decide_eq_true_eq, Bool.or_eq_true, beq_iff_eq] at h'
  exact ⟨h'.1.1, h'.1.2, fun k hk => beq_iff_eq.mp (all_range.mp h'.2 k hk)⟩

theorem pl_inj (t s : ℕ) (ht : t < 104) (hs : s < 104) (h : pl t = pl s) : t = s := by
  have h0 := portOK_true
  simp only [portOK, Bool.and_eq_true, decide_eq_true_eq] at h0
  have hl : portLine.length = 104 := by
    have := lenOK_true; simp only [lenOK, Bool.and_eq_true, beq_iff_eq] at this; exact this.1.2
  have := (List.Nodup.getElem_inj_iff h0.2 (i := t) (j := s) (hi := by omega) (hj := by omega)).mp
  apply this
  simpa [pl, List.getD_eq_getElem?_getD, List.getElem?_eq_getElem (show t < portLine.length by omega),
    List.getElem?_eq_getElem (show s < portLine.length by omega)] using h

def plF (t : Fin 104) : Fin 120 := ⟨pl t, (port_spec t t.2).1⟩

theorem rK_eq {K : Type*} [Field K] [CharZero K] (t : Fin 104) : rK K t = (ps t : K) • lv K (pl t) := by
  ext k
  simp only [rK, lv, Pi.smul_apply, smul_eq_mul]
  rw [(port_spec t t.2).2.2 k k.2]; push_cast; ring

/-! ## RootFact over `ℚ` -/

theorem rootQ (y : V) (hy : y ≠ 0) : 49 ≤ (univ.filter fun t : Fin 104 => lv ℚ (pl t) ⬝ᵥ y ≠ 0).card := by
  have hsplit := Finset.card_filter_add_card_filter_not (s := (univ : Finset (Fin 104)))
    (fun t => lv ℚ (pl t) ⬝ᵥ y = 0)
  simp only [card_univ, Fintype.card_fin] at hsplit
  have hne : (univ.filter fun t : Fin 104 => lv ℚ (pl t) ⬝ᵥ y ≠ 0).card =
      (univ.filter fun t : Fin 104 => ¬ lv ℚ (pl t) ⬝ᵥ y = 0).card := rfl
  have hZ : (univ.filter fun t : Fin 104 => lv ℚ (pl t) ⬝ᵥ y = 0).card ≤ Zc y := by
    unfold Zc
    apply Finset.card_le_card_of_injOn plF
    · intro t ht; simpa [plF] using ht
    · intro t _ s _ h
      exact Fin.ext (pl_inj t s t.2 s.2 (congrArg Fin.val h))
  rcases dom y hy with h | ⟨h, _⟩ | ⟨j, hj, μ, he⟩
  · omega
  · omega
  · have hμ : μ ≠ 0 := by rintro rfl; apply hy; rw [he, zero_smul]
    have h := rootOK_true
    rw [rootOK, all_range] at h
    have h49 := of_decide_eq_true (h j hj)
    rw [countP_range] at h49
    refine le_trans h49 (le_of_eq (congrArg _ (Finset.filter_congr ?_)))
    intro t _
    rw [he, dotProduct_smul, smul_eq_mul, lv_dot (pl t) j (port_spec t t.2).1 hj]
    simp [hμ]

/-! ## Reduction from a field of characteristic zero to `ℚ` -/

theorem reduce {K : Type*} [Field K] [CharZero K] (x : Fin 8 → K) (hx : x ≠ 0) :
    ∃ y : V, y ≠ 0 ∧ ∀ j : ℕ, j < 120 → lv K j ⬝ᵥ x = 0 → lv ℚ j ⬝ᵥ y = 0 := by
  let T : Set V := {v | ∃ j < 120, lv K j ⬝ᵥ x = 0 ∧ v = lv ℚ j}
  have key : ∀ v ∈ Submodule.span ℚ T, (fun k => ((v k : ℚ) : K)) ⬝ᵥ x = 0 := by
    intro v hv
    induction hv using Submodule.span_induction with
    | mem v hv =>
      obtain ⟨j, _, h0, rfl⟩ := hv
      convert h0 using 2
      ext k; simp [lv]
    | zero => simp
    | add u v _ _ hu hv =>
      have : (fun k => (((u + v) k : ℚ) : K)) = (fun k => ((u k : ℚ) : K)) + (fun k => ((v k : ℚ) : K)) := by
        ext; simp
      rw [this, add_dotProduct, hu, hv, add_zero]
    | smul c v _ hv =>
      have : (fun k => (((c • v) k : ℚ) : K)) = (c : K) • (fun k => ((v k : ℚ) : K)) := by
        ext; simp
      rw [this, smul_dotProduct, hv, smul_zero]
  have hlt : Submodule.span ℚ T < ⊤ := by
    rw [lt_top_iff_ne_top]
    intro htop
    apply hx
    ext c
    have h := key (fun j => if c = j then 1 else 0) (htop ▸ Submodule.mem_top)
    simpa [dotProduct, apply_ite] using h
  obtain ⟨f, hf0, hle⟩ := Submodule.exists_le_ker_of_lt_top _ hlt
  have hf : ∀ v : V, f v = v ⬝ᵥ fun c => f fun j => if c = j then 1 else 0 := by
    intro v; rw [LinearMap.pi_apply_eq_sum_univ f v]; simp [dotProduct]
  refine ⟨fun c => f fun j => if c = j then 1 else 0, ?_, ?_⟩
  · intro h0
    apply hf0
    apply LinearMap.ext
    intro v
    rw [hf v, h0, dotProduct_zero]; rfl
  · intro j hj h0
    have hv : lv ℚ j ∈ LinearMap.ker f := hle (Submodule.subset_span ⟨j, hj, h0, rfl⟩)
    rw [LinearMap.mem_ker, hf] at hv
    exact hv

/-- **RootFact for P104**, proved from the dominant chamber argument. -/
theorem rootFact_h {K : Type*} [Field K] [CharZero K] : BForm.RootFact (rK K) := by
  intro x hx
  obtain ⟨y, hy, hZ⟩ := reduce x hx
  refine le_trans (rootQ y hy) (Finset.card_le_card ?_)
  intro t ht
  simp only [mem_filter, mem_univ, true_and] at ht
  simp only [nonorth, mem_filter, mem_univ, true_and]
  intro h0
  apply ht
  apply hZ (pl t) (port_spec t t.2).1
  rw [rK_eq, smul_dotProduct, smul_eq_mul] at h0
  have hs : (ps t : K) ≠ 0 := by
    rcases (port_spec t t.2).2.1 with h | h <;> rw [h] <;> norm_num
  exact (mul_eq_zero.mp h0).resolve_left hs

end BForm.E8h
