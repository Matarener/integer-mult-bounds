import BForm.E8h.RootH
import BForm.E8h.SpanChecksProof
import BForm.E8h.SpanAll
import BForm.E8.Labels
import BForm.CaseII

/-!
# SpanFact for P104 from the dominant chamber argument

`reduceExact`: a non-zero vector over a field of characteristic zero has a non-zero rational partner orthogonal
to exactly the same roots.  For a rational `y` and a non-zero label `z`, let `S` be the ports that are
non-orthogonal to `y` and odd for `z`.  By `dom`, either `y` is orthogonal to at most 37 roots (then
`|S| ≥ 44 - 37`), or it is a D7 normal (at most 42 roots; labels with at least 47 odd ports give `|S| ≥ 5`, the
twelve others are checked), or it is a root (checked).  In all cases `S` is empty, has at least 5 ports, or is a
single port whose label is `z`.
-/

namespace BForm.E8h

set_option linter.unusedSectionVars false

open Matrix Finset BForm.E8

/-! ## Bit masks as port sets -/

/-- the ports in a mask -/
def bset (s : ℕ) : Finset (Fin 104) := univ.filter fun t => s.testBit t = true

theorem bset_card_eq_bitsN (s : ℕ) : (bset s).card = bitsN s := by
  rw [bitsN, countP_range]; rfl

theorem hbStep_spec (m w s : ℕ) (h1 : 2 ^ m ≤ s) (h2 : s < 2 ^ (m + 2 * w)) :
    2 ^ hbStep m w s ≤ s ∧ s < 2 ^ (hbStep m w s + w) := by
  unfold hbStep
  split_ifs with h
  · exact ⟨h, by rw [show m + w + w = m + 2 * w by ring]; exact h2⟩
  · exact ⟨h1, by omega⟩

theorem hb_eq (s : ℕ) (h0 : s ≠ 0) (h : s < 2 ^ 128) : hb s = s.log2 := by
  have e1 := hbStep_spec 0 64 s (by simpa using Nat.one_le_iff_ne_zero.mpr h0) (by simpa using h)
  have e2 := hbStep_spec _ 32 s e1.1 (by simpa using e1.2)
  have e3 := hbStep_spec _ 16 s e2.1 (by simpa using e2.2)
  have e4 := hbStep_spec _ 8 s e3.1 (by simpa using e3.2)
  have e5 := hbStep_spec _ 4 s e4.1 (by simpa using e4.2)
  have e6 := hbStep_spec _ 2 s e5.1 (by simpa using e5.2)
  have e7 := hbStep_spec _ 1 s e6.1 (by simpa using e6.2)
  apply le_antisymm
  · exact (Nat.le_log2 h0).mpr e7.1
  · exact Nat.lt_succ_iff.mp ((Nat.log2_lt h0).mpr e7.2)

theorem bset_clr (s : ℕ) (hs : s ≠ 0) (hlt : s < 2 ^ 104) :
    (bset (clr s)).card + 1 = (bset s).card ∧ clr s < 2 ^ 104 := by
  have hl : s.log2 < 104 := (Nat.log2_lt hs).mpr hlt
  have hb : s.testBit s.log2 = true := Nat.testBit_log2 hs
  have hc : clr s = s ^^^ 2 ^ s.log2 := by
    rw [clr, hb_eq s hs (lt_of_lt_of_le hlt (Nat.pow_le_pow_right (by norm_num) (by norm_num)))]
  rw [hc]
  constructor
  · have : bset (s ^^^ 2 ^ s.log2) = (bset s).erase ⟨s.log2, hl⟩ := by
      ext t
      simp only [bset, mem_filter, mem_univ, true_and, mem_erase, Nat.testBit_xor, Nat.testBit_two_pow]
      by_cases h : (t : ℕ) = s.log2
      · have ht : t = ⟨s.log2, hl⟩ := Fin.ext h
        subst ht; simp [hb]
      · have ht : t ≠ ⟨s.log2, hl⟩ := fun e => h (congrArg Fin.val e)
        have h' : ¬ s.log2 = (t : ℕ) := fun e => h e.symm
        simp [ht, h']
    rw [this, card_erase_add_one]; simp [bset, hb]
  · exact Nat.xor_lt_two_pow hlt (Nat.pow_lt_pow_right (by norm_num) hl)

theorem bset_pos (s : ℕ) (hs : s ≠ 0) (hlt : s < 2 ^ 104) : 1 ≤ (bset s).card := by
  have h := bset_clr s hs hlt; omega

theorem atLeast5_spec (s : ℕ) (h : atLeast5 s = true) (hlt : s < 2 ^ 104) : 5 ≤ (bset s).card := by
  simp only [atLeast5, Bool.and_eq_true, bne_iff_ne, ne_eq] at h
  obtain ⟨⟨⟨⟨h0, h1⟩, h2⟩, h3⟩, h4⟩ := h
  obtain ⟨c0, l0⟩ := bset_clr s h0 hlt
  obtain ⟨c1, l1⟩ := bset_clr _ h1 l0
  obtain ⟨c2, l2⟩ := bset_clr _ h2 l1
  obtain ⟨c3, l3⟩ := bset_clr _ h3 l2
  have := bset_pos _ h4 l3
  omega

theorem bset_zero : bset 0 = ∅ := by ext t; simp [bset]

theorem bset_pow (w : ℕ) (hw : w < 104) : bset (2 ^ w) = {⟨w, hw⟩} := by
  ext t; simp only [bset, mem_filter, mem_univ, true_and, Nat.testBit_two_pow, decide_eq_true_eq, mem_singleton]
  constructor
  · intro h; exact Fin.ext h.symm
  · intro h; rw [h]

/-! ## Exact reduction to `ℚ` -/

def Wsub {K : Type*} [Field K] (x : Fin 8 → K) : Submodule ℚ V where
  carrier := {y | ∀ j < 120, lv K j ⬝ᵥ x = 0 → lv ℚ j ⬝ᵥ y = 0}
  add_mem' := by
    intro a b ha hb j hj h0; rw [dotProduct_add, ha j hj h0, hb j hj h0, add_zero]
  zero_mem' := by intro j _ _; simp
  smul_mem' := by intro c a ha j hj h0; rw [dotProduct_smul, ha j hj h0, smul_zero]

def dotL (v : V) : Module.Dual ℚ V where
  toFun y := v ⬝ᵥ y
  map_add' a b := dotProduct_add v a b
  map_smul' c a := by simp [dotProduct_smul]

theorem reduceExact {K : Type*} [Field K] [CharZero K] (x : Fin 8 → K) (hx : x ≠ 0) :
    ∃ y : V, y ≠ 0 ∧ ∀ j : ℕ, j < 120 → (lv K j ⬝ᵥ x = 0 ↔ lv ℚ j ⬝ᵥ y = 0) := by
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
  obtain ⟨y0, hy0, hW0⟩ := reduce x hx
  obtain ⟨c, hc⟩ : ∃ c, y0 c ≠ 0 := by
    by_contra h; push Not at h; exact hy0 (funext h)
  let ι := Option {j : Fin 120 // lv K j ⬝ᵥ x ≠ 0}
  let f : ι → Module.Dual ℚ V := fun i => match i with
    | none => LinearMap.proj c
    | some j => dotL (lv ℚ j)
  have hex : ∀ i, ∃ y ∈ Wsub x, f i y ≠ 0 := by
    intro i
    match i with
    | none => exact ⟨y0, hW0, hc⟩
    | some ⟨j, hj⟩ =>
      have hnot : lv ℚ j ∉ Submodule.span ℚ T := by
        intro hm; apply hj
        have := key _ hm
        convert this using 2
        ext k; simp [lv]
      obtain ⟨g, hg, hle⟩ := Submodule.exists_le_ker_of_notMem hnot
      have hgv : ∀ v : V, g v = v ⬝ᵥ fun c => g fun j => if c = j then 1 else 0 := by
        intro v; rw [LinearMap.pi_apply_eq_sum_univ g v]; simp [dotProduct]
      refine ⟨fun c => g fun j => if c = j then 1 else 0, ?_, ?_⟩
      · intro i hi h0
        have := hle (Submodule.subset_span ⟨i, hi, h0, rfl⟩)
        rw [LinearMap.mem_ker, hgv] at this
        exact this
      · change dotL (lv ℚ j) _ ≠ 0
        simp only [dotL, LinearMap.coe_mk, AddHom.coe_mk]
        rw [← hgv]; exact hg
  obtain ⟨y, hyW, hy⟩ := Module.Dual.exists_forall_mem_ne_zero_of_forall_exists (Wsub x) f hex
  refine ⟨y, fun h => hy none (by rw [h]; rfl), fun j hj => ⟨hyW j hj, fun h0 => ?_⟩⟩
  by_contra hne
  exact hy (some ⟨⟨j, hj⟩, hne⟩) h0

/-! ## Ports, labels and masks -/

theorem oData_spec (l : List ℕ) (hl : l ∈ lists9) : ∃ M, (l, M) ∈ oData ∧ M < 2 ^ 104 ∧
    ∀ t < 104, M.testBit t = par t l := by
  have h := oOK_true
  simp only [oOK, Bool.and_eq_true, beq_iff_eq, List.all_eq_true, decide_eq_true_eq] at h
  rw [← h.1] at hl
  obtain ⟨⟨l', M⟩, hm, rfl⟩ := List.mem_map.mp hl
  have h2 := h.2 _ hm
  exact ⟨M, hm, h2.1, fun t ht => h2.2 t (List.mem_range.mpr ht)⟩

theorem dp_cast (t j : ℕ) (ht : t < 104) (hj : j < 120) :
    rK ℚ ⟨t, ht⟩ ⬝ᵥ lv ℚ j = (dp t j : ℚ) := by
  rw [rK_eq, smul_dotProduct, smul_eq_mul, lv_dot _ _ (port_spec t ht).1 hj, dp]; push_cast; rfl

theorem mask_spec (j t : ℕ) (hj : j < 120) (ht : t < 104) :
    nm j < 2 ^ 104 ∧ ((nm j).testBit t = true ↔ dp t j ≠ 0) ∧ ((pm j).testBit t = true ↔ 0 < dp t j) ∧
    ((mm j).testBit t = true ↔ dp t j < 0) ∧ (pl t = j ∨ dp t j = 0 ∨ dp t j = 4 ∨ dp t j = -4) := by
  have h := maskOK_true
  simp only [maskOK, Bool.and_eq_true] at h
  have h1 := all_range.mp h.2 j hj
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h1
  have h2 := all_range.mp h1.2 t ht
  simp only [Bool.and_eq_true, beq_iff_eq, Bool.or_eq_true, bne_iff_ne, ne_eq] at h2
  refine ⟨h1.1, ?_, ?_, ?_, ?_⟩
  · rw [h2.1.1.1]; simp
  · rw [h2.1.1.2]; simp
  · rw [h2.1.2]; simp
  · rcases h2.2 with ((h | h) | h) | h <;> simp [h]

theorem nm_mem (j : ℕ) (hj : j < 120) : nm j ∈ nMask := by
  have h := maskOK_true
  simp only [maskOK, Bool.and_eq_true, beq_iff_eq] at h
  exact getD_mem (by rw [h.1.1.1]; exact hj) 0

theorem dp_vals (t j : ℕ) (ht : t < 104) (hj : j < 120) :
    (pl t = j ∧ (dp t j = 8 ∨ dp t j = -8)) ∨ dp t j = 0 ∨ dp t j = 4 ∨ dp t j = -4 := by
  rcases (mask_spec j t hj ht).2.2.2.2 with h | h
  · left; refine ⟨h, ?_⟩
    have hn := normOK_true
    rw [normOK, all_range] at hn
    rw [dp, h, beq_iff_eq.mp (hn j hj)]
    rcases (port_spec t ht).2.1 with h' | h' <;> rw [h'] <;> norm_num
  · right; exact h

theorem dp_orth (t a b : ℕ) (ha : a < 120) (hb : b < 120) (hab : dotZ (pr a) (pr b) = 0) (h : pl t = a) :
    dp t b = 0 := by rw [dp, h, hab, mul_zero]

theorem tb_iff {s : ℕ} {t : ℕ} {p : Prop} [Decidable p] (h : s.testBit t = true ↔ p) : s.testBit t = decide p := by
  rw [Bool.eq_iff_iff, decide_eq_true_iff]; exact h

theorem nv_spec (a b t : ℕ) (ha : a < 120) (hb : b < 120) (ht : t < 104) (hab : dotZ (pr a) (pr b) = 0)
    (e : Bool) : (nv a b e).testBit t = true ↔ dp t a + (if e then 1 else -1) * dp t b ≠ 0 := by
  have hba : dotZ (pr b) (pr a) = 0 := by
    have : lv ℚ b ⬝ᵥ lv ℚ a = 0 := by
      rw [dotProduct_comm, lv_dot a b ha hb, hab]; simp
    rw [lv_dot b a hb ha] at this; exact_mod_cast this
  obtain ⟨_, hNa, hPa, hMa, _⟩ := mask_spec a t ha ht
  obtain ⟨_, hNb, hPb, hMb, _⟩ := mask_spec b t hb ht
  unfold nv
  have va := dp_vals t a ht ha
  have vb := dp_vals t b ht hb
  have xa := fun h => dp_orth t a b ha hb hab h
  have xb := fun h => dp_orth t b a hb ha hba h
  cases e <;>
  · simp only [Bool.false_eq_true, if_false, if_true, Nat.testBit_or, Nat.testBit_xor, Nat.testBit_and,
      tb_iff hNa, tb_iff hPa, tb_iff hMa, tb_iff hNb, tb_iff hPb, tb_iff hMb]
    generalize dp t a = da at *
    generalize dp t b = db at *
    rcases va with ⟨h1, h2 | h2⟩ | h2 | h2 | h2 <;> rcases vb with ⟨h3, h4 | h4⟩ | h4 | h4 | h4 <;>
      subst h2 <;> subst h4 <;> simp_all

/-! ## The core statement over `ℚ` -/

/-- non-orthogonal ports of a rational vector -/
noncomputable def NP (y : V) : Finset (Fin 104) := univ.filter fun t => rK ℚ t ⬝ᵥ y ≠ 0

theorem NP_eq (y : V) : NP y = univ.filter fun t : Fin 104 => lv ℚ (pl t) ⬝ᵥ y ≠ 0 := by
  unfold NP; apply Finset.filter_congr; intro t _
  rw [rK_eq, smul_dotProduct, smul_eq_mul]
  have hs : (ps t : ℚ) ≠ 0 := by rcases (port_spec t t.2).2.1 with h | h <;> rw [h] <;> norm_num
  simp [hs]

/-- `S` for a rational normal and an odd-port mask `M` -/
theorem core (y : V) (hy : y ≠ 0) (l : List ℕ) (hl0 : l ≠ zero9) (M : ℕ) (hlM : (l, M) ∈ oData)
    (hM : M < 2 ^ 104) (S : Finset (Fin 104)) (hS : S = (NP y).filter fun t : Fin 104 => M.testBit t = true)
    (h4 : S.card ≤ 4) : S = ∅ ∨ ∃ w ∈ S, pbits w = l := by
  have h44 := o44OK_true
  simp only [o44OK, List.all_eq_true] at h44
  have hO := h44 _ hlM
  simp only [Bool.or_eq_true, beq_iff_eq, hl0, false_or, Bool.and_eq_true, decide_eq_true_eq] at hO
  -- `|S| ≥ |O| - |ports orthogonal to y|`
  have hsplit : (bset M).card ≤ S.card + (univ.filter fun t : Fin 104 => lv ℚ (pl t) ⬝ᵥ y = 0).card := by
    have hsum := Finset.card_filter_add_card_filter_not (s := bset M) (fun t : Fin 104 => lv ℚ (pl t) ⬝ᵥ y ≠ 0)
    have e1 : (bset M).filter (fun t : Fin 104 => lv ℚ (pl t) ⬝ᵥ y ≠ 0) = S := by
      rw [hS, NP_eq]; ext t; simp [bset, and_comm]
    have e2 : ((bset M).filter fun t : Fin 104 => ¬ lv ℚ (pl t) ⬝ᵥ y ≠ 0) ⊆
        univ.filter fun t : Fin 104 => lv ℚ (pl t) ⬝ᵥ y = 0 := by
      intro t ht; simp only [mem_filter, mem_univ, true_and, not_not] at ht ⊢; exact ht.2
    have hle := Finset.card_le_card e2
    rw [e1] at hsum
    omega
  have hZ : (univ.filter fun t : Fin 104 => lv ℚ (pl t) ⬝ᵥ y = 0).card ≤ Zc y := by
    unfold Zc
    apply Finset.card_le_card_of_injOn plF
    · intro t ht; simpa [plF] using ht
    · intro t _ s _ h
      exact Fin.ext (pl_inj t s t.2 s.2 (congrArg Fin.val h))
  rw [bset_card_eq_bitsN] at hsplit
  rcases dom y hy with h | ⟨h, a, b, ha, hb, hab, μ, ε, hε, he⟩ | ⟨j, hj, μ, he⟩
  · omega
  · -- D7
    rcases hO with ⟨_, h47 | hbad⟩
    · omega
    left
    have hμ : μ ≠ 0 := by rintro rfl; apply hy; rw [he, zero_smul]
    have hd := d7Span_all a ha
    rw [d7SpanA, all_range] at hd
    have hd2 := hd b hb
    have habZ : dotZ (pr a) (pr b) = 0 := by
      have := hab; rw [lv_dot a b ha hb] at this; exact_mod_cast this
    simp only [Bool.or_eq_true, bne_iff_ne, ne_eq, habZ, not_true_eq_false, false_or, Bool.and_eq_true,
      List.all_eq_true] at hd2
    have hbad' : (l, M) ∈ oBad := by simpa using hbad
    let e : Bool := decide (ε = 1)
    have hεe : ε = if e then 1 else -1 := by
      rcases hε with rfl | rfl <;> simp [e]
    have hcase : M &&& nv a b e = 0 ∨ atLeast5 (M &&& nv a b e) = true := by
      have hc := hd2 _ hbad'
      have hc' : d7Cond (M &&& nv a b e) = true := by cases e <;> simp_all
      simpa [d7Cond] using hc'
    have hSb : S = bset (M &&& nv a b e) := by
      rw [hS]; ext t
      simp only [NP, mem_filter, mem_univ, true_and, bset, Nat.testBit_and, Bool.and_eq_true]
      rw [he, dotProduct_smul, dotProduct_add, dotProduct_smul, smul_eq_mul, smul_eq_mul,
        dp_cast t a t.2 ha, dp_cast t b t.2 hb, nv_spec a b t ha hb t.2 habZ e, hεe]
      have key : ((dp t a : ℚ) + (if e then 1 else -1) * (dp t b : ℚ)) =
          ((dp t a + (if e then 1 else -1) * dp t b : ℤ) : ℚ) := by split_ifs <;> push_cast <;> ring
      rw [key]
      simp only [ne_eq, mul_eq_zero, hμ, false_or, Int.cast_eq_zero]
      constructor <;> intro h <;> exact ⟨h.2, h.1⟩
    rw [hSb] at h4 ⊢
    rcases hcase with h0 | h5
    · rw [h0, bset_zero]
    · have := atLeast5_spec _ h5 (by rw [Nat.land_comm]; exact Nat.and_lt_two_pow _ hM)
      omega
  · -- root
    have hμ : μ ≠ 0 := by rintro rfl; apply hy; rw [he, zero_smul]
    have hr := rootSpan_all j hj
    simp only [rootSpanJ, List.all_eq_true] at hr
    have hr2 := hr _ hlM
    have hSb : S = bset (M &&& nm j) := by
      rw [hS]; ext t
      simp only [NP, mem_filter, mem_univ, true_and, bset, Nat.testBit_and, Bool.and_eq_true]
      rw [he, dotProduct_smul, smul_eq_mul, dp_cast t j t.2 hj, (mask_spec j t hj t.2).2.1]
      simp [hμ, and_comm]
    simp only [rootCond, Bool.or_eq_true, beq_iff_eq, hl0, false_or, Bool.and_eq_true, decide_eq_true_eq] at hr2
    rw [hSb] at h4 ⊢
    rcases hr2 with (h0 | h5) | ⟨⟨hp, hw⟩, hpb⟩
    · left; rw [h0, bset_zero]
    · have := atLeast5_spec _ h5 (by rw [Nat.land_comm]; exact Nat.and_lt_two_pow _ hM)
      omega
    · right
      have hs : bset (M &&& nm j) = {⟨hb (M &&& nm j), hw⟩} := by
        conv_lhs => rw [hp]
        exact bset_pow _ hw
      rw [hs]
      refine ⟨⟨hb (M &&& nm j), hw⟩, mem_singleton_self _, ?_⟩
      rw [Fin.val_mk]; exact hpb

/-! ## SpanFact -/

/-- **SpanFact for P104**, proved from the dominant chamber argument. -/
theorem spanFact_h {K : Type*} [Field K] [CharZero K] : BForm.SpanFact labK (rK K) := by
  intro x hx B hB z hz hyp
  obtain ⟨y, hy, hZ⟩ := reduceExact x hx
  have hl0 : zl z ≠ zero9 := fun h => hz (zl_zero h)
  obtain ⟨M, hlM, hM, hMbit⟩ := oData_spec (zl z) (zl_mem z)
  have hN : ∀ t : Fin 104, t ∈ nonorth (rK K) x ↔ t ∈ NP y := by
    intro t
    simp only [nonorth, NP, mem_filter, mem_univ, true_and]
    rw [rK_eq, rK_eq, smul_dotProduct, smul_dotProduct, smul_eq_mul, smul_eq_mul]
    have hs : ps t = 1 ∨ ps t = -1 := (port_spec t t.2).2.1
    have hsK : (ps t : K) ≠ 0 := by rcases hs with h | h <;> rw [h] <;> norm_num
    have hsQ : (ps t : ℚ) ≠ 0 := by rcases hs with h | h <;> rw [h] <;> norm_num
    simp only [ne_eq, mul_eq_zero, hsK, hsQ, false_or]
    exact not_congr (hZ (pl t) (port_spec t t.2).1)
  have hodd : ∀ t : Fin 104, labK t ⬝ᵥ z ≠ 0 ↔ M.testBit t = true := by
    intro t; rw [lab_dot, hMbit t t.2]
  have hSB : (NP y).filter (fun t : Fin 104 => M.testBit t = true) ⊆ B := by
    intro t ht
    rw [mem_filter] at ht
    by_contra hB'
    exact (hodd t).mpr ht.2 (hyp t (mem_sdiff.mpr ⟨(hN t).mpr ht.1, hB'⟩))
  have h4 := (card_le_card hSB).trans hB
  rcases core y hy (zl z) hl0 M hlM hM _ rfl h4 with h0 | ⟨w, hw, hpw⟩
  · left
    intro t ht
    by_contra hne
    have : t ∈ (NP y).filter (fun t : Fin 104 => M.testBit t = true) := mem_filter.mpr ⟨(hN t).mp ht, (hodd t).mp hne⟩
    rw [h0] at this; simp at this
  · right
    exact ⟨w, hSB hw, lab_of_pbits hpw⟩

end BForm.E8h
