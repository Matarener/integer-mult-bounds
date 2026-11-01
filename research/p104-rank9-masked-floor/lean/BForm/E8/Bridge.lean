import BForm.E8.Defs
import BForm.E8.Normal

/-! Bridge lemmas: from the Boolean checks to statements over a field of characteristic zero. -/

namespace BForm.E8

open Matrix Finset

theorem all_range {n : ℕ} {f : ℕ → Bool} : (List.range n).all f = true ↔ ∀ i < n, f i = true := by
  simp [List.all_eq_true, List.mem_range]

theorem countP_range (n : ℕ) (f : ℕ → Bool) :
    (List.range n).countP f = (univ.filter fun i : Fin n => f i = true).card := by
  rw [← List.map_coe_finRange_eq_range, List.countP_map, List.countP_eq_length_filter]
  rw [← List.toFinset_card_of_nodup ((List.nodup_finRange n).filter _)]
  congr 1; ext i; simp

theorem sum_range_fin {M : Type*} [AddCommMonoid M] (n : ℕ) (g : ℕ → M) :
    ((List.range n).map g).sum = ∑ i : Fin n, g i := by
  induction n with
  | zero => simp
  | succ n ih => rw [List.range_succ, List.map_append, List.sum_append, ih, Fin.sum_univ_castSucc]; simp

variable {K : Type*} [Field K] [CharZero K]

/-- ports as vectors over `K` -/
def rK (K : Type*) [Field K] (p : Fin 104) : Fin 8 → K := fun k => (((r8 p).getD k 0 : ℤ) : K)

theorem dotZ_eq (a b : List ℤ) (n : ℕ) (ha : a.length = n) (hb : b.length = n) :
    dotZ a b = ∑ k : Fin n, a.getD k 0 * b.getD k 0 := by
  induction a generalizing b n with
  | nil => subst ha; simp [dotZ]
  | cons x a ih =>
    cases b with
    | nil => simp at hb; subst hb; simp at ha
    | cons y b =>
      cases n with
      | zero => simp at ha
      | succ n =>
        simp only [List.length_cons, add_left_inj] at ha hb
        rw [Fin.sum_univ_succ]
        have := ih b n ha hb
        simp only [dotZ, List.zipWith_cons_cons, List.sum_cons] at this ⊢
        rw [this]; simp

/-- frame line `t` of frame `fi` as a port -/
def frP (fi : ℕ) (t : Fin 8) : Fin 104 := ⟨fr fi t % 104, Nat.mod_lt _ (by norm_num)⟩

theorem partOK_spec (h : partOK = true) :
    (∀ p < 104, frameOf.getD p 0 < 13 ∧ posOf.getD p 0 < 8 ∧ fr (frameOf.getD p 0) (posOf.getD p 0) = p) ∧
    (∀ fi < 13, ∀ t < 8, fr fi t < 104 ∧ frameOf.getD (fr fi t) 0 = fi ∧ posOf.getD (fr fi t) 0 = t) := by
  simp only [partOK, Bool.and_eq_true, all_range, beq_iff_eq, decide_eq_true_eq] at h
  exact ⟨fun p hp => by have := h.1 p hp; tauto, fun fi hfi t ht => by have := h.2 fi hfi t ht; tauto⟩

theorem frP_val (h : partOK = true) {fi : ℕ} (hfi : fi < 13) (t : Fin 8) : (frP fi t).val = fr fi t :=
  Nat.mod_eq_of_lt ((partOK_spec h).2 fi hfi t t.2).1

theorem frameId_spec (h : frameIdOK = true) {fi : ℕ} (hfi : fi < 13) {p : ℕ} (hp : p < 104) {k : ℕ} (hk : k < 8) :
    2 * (r8 p).getD k 0 = ∑ t : Fin 8, uu p (fr fi t) * (r8 (fr fi t)).getD k 0 := by
  simp only [frameIdOK, all_range, beq_iff_eq] at h
  rw [h fi hfi p hp k hk, sum_range_fin]

theorem frame_id (h1 : frameIdOK = true) (hp : partOK = true) {fi : ℕ} (hfi : fi < 13) (p : Fin 104)
    (x : Fin 8 → K) :
    2 * (rK K p ⬝ᵥ x) = ∑ t : Fin 8, ((uu p (fr fi t) : ℤ) : K) * (rK K (frP fi t) ⬝ᵥ x) := by
  have hk : ∀ k : Fin 8, (2 : K) * rK K p k = ∑ t : Fin 8, ((uu p (fr fi t) : ℤ) : K) * rK K (frP fi t) k := by
    intro k
    have := congrArg (fun z : ℤ => (z : K)) (frameId_spec h1 hfi p.2 k.2)
    simp only [Int.cast_mul, Int.cast_ofNat, Int.cast_sum] at this
    simp only [rK, frP_val hp hfi]; exact this
  simp only [dotProduct, Finset.mul_sum]
  rw [Finset.sum_comm]
  refine Finset.sum_congr rfl fun k _ => ?_
  rw [← mul_assoc, hk k, Finset.sum_mul]
  refine Finset.sum_congr rfl fun t _ => by ring

theorem frameOrtho_spec (h : frameOrthoOK = true) {fi : ℕ} (hfi : fi < 13) {k l : ℕ} (hk : k < 8) (hl : l < 8) :
    ∑ t : Fin 8, (r8 (fr fi t)).getD k 0 * (r8 (fr fi t)).getD l 0 = if k = l then 8 else 0 := by
  simp only [frameOrthoOK, all_range, beq_iff_eq] at h
  have := h fi hfi k hk l hl
  rw [sum_range_fin] at this; rw [this]

/-- a frame spans: `x` orthogonal to all its lines vanishes -/
theorem frame_span (h : frameOrthoOK = true) (hp : partOK = true) {fi : ℕ} (hfi : fi < 13) (x : Fin 8 → K)
    (hx : ∀ t : Fin 8, rK K (frP fi t) ⬝ᵥ x = 0) : x = 0 := by
  funext l
  have hc : ∀ k : Fin 8, ∑ t : Fin 8, rK K (frP fi t) l * rK K (frP fi t) k = if l = k then 8 else 0 := by
    intro k
    have := congrArg (fun z : ℤ => (z : K)) (frameOrtho_spec h hfi l.2 k.2)
    simp only [Int.cast_sum, Int.cast_mul] at this
    simp only [rK, frP_val hp hfi]; rw [this]; by_cases hlk : l = k <;> simp [hlk, Fin.val_inj]
  have key : (8 : K) * x l = ∑ t : Fin 8, rK K (frP fi t) l * (rK K (frP fi t) ⬝ᵥ x) := by
    simp only [dotProduct, Finset.mul_sum]
    rw [Finset.sum_comm]
    have : ∀ k : Fin 8, ∑ t : Fin 8, rK K (frP fi t) l * (rK K (frP fi t) k * x k) =
        (if l = k then 8 else 0) * x k := by
      intro k; rw [← hc k, Finset.sum_mul]; exact Finset.sum_congr rfl fun t _ => by ring
    rw [Finset.sum_congr rfl fun k _ => this k]; simp
  have h8 : (8 : K) ≠ 0 := by norm_num
  have : (8 : K) * x l = 0 := by rw [key]; simp [hx]
  simpa [h8] using this

/-- the 13 frames as a bijection `Fin 13 × Fin 8 ≃ Fin 104` -/
def frameEquiv (hp : partOK = true) : Fin 13 × Fin 8 ≃ Fin 104 where
  toFun ft := frP ft.1 ft.2
  invFun p := (⟨frameOf.getD p 0, ((partOK_spec hp).1 p p.2).1⟩, ⟨posOf.getD p 0, ((partOK_spec hp).1 p p.2).2.1⟩)
  left_inv ft := by
    obtain ⟨fi, t⟩ := ft
    have h := (partOK_spec hp).2 fi fi.2 t t.2
    refine Prod.ext (Fin.ext ?_) (Fin.ext ?_)
    · show frameOf.getD (frP fi t).val 0 = fi; rw [frP_val hp fi.2]; exact h.2.1
    · show posOf.getD (frP fi t).val 0 = t; rw [frP_val hp fi.2]; exact h.2.2
  right_inv p := by
    have h := (partOK_spec hp).1 p p.2
    apply Fin.ext
    show (frP (frameOf.getD p 0) ⟨posOf.getD p 0, _⟩).val = p
    rw [frP_val hp h.1]; exact h.2.2

theorem card_frames (hp : partOK = true) (Q : Fin 104 → Prop) [DecidablePred Q] :
    (univ.filter Q).card = ∑ fi : Fin 13, (univ.filter fun t : Fin 8 => Q (frP fi t)).card := by
  simp only [Finset.card_filter]
  rw [← (frameEquiv hp).sum_comp, Fintype.sum_prod_type]
  rfl

/-! List helpers. -/

theorem getD_mem {α : Type*} {l : List α} {i : ℕ} (hi : i < l.length) (d : α) : l.getD i d ∈ l := by
  rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hi]; exact List.getElem_mem hi

theorem list_eq_map_range {α : Type*} (l : List α) (d : α) : l = (List.range l.length).map fun i => l.getD i d := by
  apply List.ext_getElem (by simp)
  intro i h1 h2
  simp [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem h1]

theorem countP_list {α : Type*} (l : List α) (d : α) (h : α → Bool) :
    l.countP h = (univ.filter fun i : Fin l.length => h (l.getD i d) = true).card := by
  conv_lhs => rw [list_eq_map_range l d]
  rw [List.countP_map, countP_range]; rfl

theorem zipIdx_all {α : Type*} (l : List α) (d : α) (h : α × ℕ → Bool) (H : l.zipIdx.all h = true) :
    ∀ i < l.length, h (l.getD i d, i) = true := by
  rw [List.all_eq_true] at H
  intro i hi
  apply H
  rw [List.mem_zipIdx_iff_getElem?]
  simp [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hi]

theorem r8Len_spec (h : r8Len = true) :
    r8Data.length = 104 ∧ fmaskData.length = 680 ∧ maskData.length = 128 ∧ ∀ p < 104, (r8 p).length = 8 := by
  simp only [r8Len, Bool.and_eq_true, beq_iff_eq, all_range] at h
  exact ⟨h.1.1.1, h.1.1.2, h.1.2, h.2⟩

/-! Blocks. -/

def blkL (fi b : ℕ) : List ℕ := (blkData.getD fi []).getD b []

theorem blkOK_spec (h : blkOK = true) {fi : ℕ} (hfi : fi < 13) :
    (∀ b < 14, (blkL fi b).length = 4) ∧ (∀ b < 14, ∀ q < 4, blk fi b q < 8 ∧ (q = 3 ∨ blk fi b q < blk fi b (q + 1))) ∧
    (∀ t1 < 8, ∀ t2 < 8, ∀ t3 < 8, ∃ b < 14, t1 ∈ blkL fi b ∧ t2 ∈ blkL fi b ∧ t3 ∈ blkL fi b) := by
  simp only [blkOK, all_range, Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq, Bool.or_eq_true,
    List.any_eq_true, List.mem_range, List.contains_iff_mem] at h
  have h := h fi hfi
  refine ⟨h.1.1, h.1.2, fun t1 h1 t2 h2 t3 h3 => ?_⟩
  obtain ⟨b, hb, hm⟩ := h.2 t1 h1 t2 h2 t3 h3
  exact ⟨b, hb, hm.1.1, hm.1.2, hm.2⟩

/-- block `b` of frame `fi` as a map `Fin 4 → Fin 8` -/
def blkF (fi b : ℕ) (q : Fin 4) : Fin 8 := ⟨blk fi b q % 8, Nat.mod_lt _ (by norm_num)⟩

theorem blkF_val (h : blkOK = true) {fi b : ℕ} (hfi : fi < 13) (hb : b < 14) (q : Fin 4) :
    (blkF fi b q).val = blk fi b q := Nat.mod_eq_of_lt ((blkOK_spec h hfi).2.1 b hb q q.2).1

theorem blk_mono (h : blkOK = true) {fi b : ℕ} (hfi : fi < 13) (hb : b < 14) :
    StrictMono fun q : Fin 4 => blk fi b q := by
  have H := (blkOK_spec h hfi).2.1 b hb
  have h01 := (H 0 (by norm_num)).2; have h12 := (H 1 (by norm_num)).2; have h23 := (H 2 (by norm_num)).2
  simp only [show (0 : ℕ) ≠ 3 by norm_num, show (1 : ℕ) ≠ 3 by norm_num, show (2 : ℕ) ≠ 3 by norm_num,
    false_or] at h01 h12 h23
  intro a c hac
  fin_cases a <;> fin_cases c <;> simp_all <;> omega

theorem blkF_inj (h : blkOK = true) {fi b : ℕ} (hfi : fi < 13) (hb : b < 14) : Function.Injective (blkF fi b) := by
  intro a c hac
  have := congrArg Fin.val hac
  rw [blkF_val h hfi hb, blkF_val h hfi hb] at this
  exact (blk_mono h hfi hb).injective this

theorem mem_blkL (h : blkOK = true) {fi b : ℕ} (hfi : fi < 13) (hb : b < 14) (t : Fin 8) :
    (t : ℕ) ∈ blkL fi b → ∃ q : Fin 4, blkF fi b q = t := by
  intro ht
  obtain ⟨i, hi, he⟩ := List.getElem_of_mem ht
  have hl := (blkOK_spec h hfi).1 b hb
  refine ⟨⟨i, by omega⟩, Fin.ext ?_⟩
  rw [blkF_val h hfi hb]
  simp only [blk, ← he]
  have : (blkL fi b).getD i 0 = (blkL fi b)[i] := by
    rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hi]; rfl
  exact this

/-- a support of at most three positions lies in a block -/
theorem small_in_block (h : blkOK = true) {fi : ℕ} (hfi : fi < 13) (S : Finset (Fin 8)) (hS : S.card ≤ 3) :
    ∃ b < 14, ∀ t ∈ S, (t : ℕ) ∈ blkL fi b := by
  have : ∃ t1 t2 t3 : Fin 8, S ⊆ {t1, t2, t3} := by
    rcases Nat.lt_or_ge S.card 1 with h0 | h1
    · exact ⟨0, 0, 0, by rw [Finset.card_eq_zero.mp (show S.card = 0 by omega)]; simp⟩
    rcases Nat.lt_or_ge S.card 2 with h1' | h2
    · obtain ⟨a, ha⟩ := Finset.card_eq_one.mp (show S.card = 1 by omega); exact ⟨a, a, a, by rw [ha]; simp⟩
    rcases Nat.lt_or_ge S.card 3 with h2' | h3
    · obtain ⟨a, c, -, ha⟩ := Finset.card_eq_two.mp (show S.card = 2 by omega); exact ⟨a, c, c, by rw [ha]; intro x; simp⟩
    · obtain ⟨a, c, d, -, -, -, ha⟩ := Finset.card_eq_three.mp (show S.card = 3 by omega); exact ⟨a, c, d, by rw [ha]⟩
  obtain ⟨t1, t2, t3, hsub⟩ := this
  obtain ⟨b, hb, m1, m2, m3⟩ := (blkOK_spec h hfi).2.2 t1 t1.2 t2 t2.2 t3 t3.2
  refine ⟨b, hb, fun t ht => ?_⟩
  have := hsub ht; simp only [Finset.mem_insert, Finset.mem_singleton] at this
  rcases this with rfl | rfl | rfl <;> assumption

/-- a sum over a frame supported in a block -/
theorem sum_block {M : Type*} [AddCommMonoid M] (h : blkOK = true) {fi b : ℕ} (hfi : fi < 13) (hb : b < 14)
    (g : Fin 8 → M) (hg : ∀ t, g t ≠ 0 → ∃ q, blkF fi b q = t) :
    ∑ t : Fin 8, g t = ∑ q : Fin 4, g (blkF fi b q) := by
  rw [← Finset.sum_image (fun a _ c _ hac => blkF_inj h hfi hb hac)]
  symm
  apply Finset.sum_subset (Finset.subset_univ _)
  intro t _ ht
  by_contra hne
  obtain ⟨q, rfl⟩ := hg t hne
  exact ht (Finset.mem_image_of_mem _ (Finset.mem_univ q))

/-! Points, normals, classes. -/

def ptK (K : Type*) [Field K] (c : ℕ) : Fin 4 → K := fun q => (((pt c).getD q 0 : ℤ) : K)
def nK (K : Type*) [Field K] (m : ℕ) : Fin 4 → K := fun q => (((nv m).getD q 0 : ℤ) : K)
def clsF (fi b : ℕ) (p : ℕ) : ℕ := (clsOf (uvec fi b (r8 p))).1

theorem ptOK_spec (h : ptOK = true) :
    (∀ c < 40, (pt c).length = 4) ∧ ∀ e ∈ [[1, 0, 0, 0], [0, 1, 0, 0], [0, 0, 1, 0], [0, 0, 0, 1]],
      ∃ c < 40, pt c = (e : List ℤ) := by
  simp only [ptOK, Bool.and_eq_true, all_range, beq_iff_eq, List.all_eq_true, List.any_eq_true,
    List.mem_range] at h
  exact ⟨h.1, fun e he => by obtain ⟨c, hc, he'⟩ := h.2 e he; exact ⟨c, hc, he'⟩⟩

theorem dotK_cast (a b : List ℤ) (ha : a.length = 4) (hb : b.length = 4) :
    ((dotZ a b : ℤ) : K) = (fun q : Fin 4 => ((a.getD q 0 : ℤ) : K)) ⬝ᵥ (fun q : Fin 4 => ((b.getD q 0 : ℤ) : K)) := by
  rw [dotZ_eq a b 4 ha hb]; simp [dotProduct]

theorem pt_span (h : ptOK = true) : Submodule.span K (Set.range fun c : Fin 40 => ptK K c) = ⊤ := by
  rw [eq_top_iff]
  intro x _
  have hunit : ∀ i : Fin 4, Pi.single i (1 : K) ∈ Submodule.span K (Set.range fun c : Fin 40 => ptK K c) := by
    intro i
    apply Submodule.subset_span
    have H := (ptOK_spec h).2
    fin_cases i
    · obtain ⟨c, hc, he⟩ := H [1, 0, 0, 0] (by simp); refine ⟨⟨c, hc⟩, ?_⟩
      funext q; fin_cases q <;> simp [ptK, he]
    · obtain ⟨c, hc, he⟩ := H [0, 1, 0, 0] (by simp); refine ⟨⟨c, hc⟩, ?_⟩
      funext q; fin_cases q <;> simp [ptK, he]
    · obtain ⟨c, hc, he⟩ := H [0, 0, 1, 0] (by simp); refine ⟨⟨c, hc⟩, ?_⟩
      funext q; fin_cases q <;> simp [ptK, he]
    · obtain ⟨c, hc, he⟩ := H [0, 0, 0, 1] (by simp); refine ⟨⟨c, hc⟩, ?_⟩
      funext q; fin_cases q <;> simp [ptK, he]
  have hx : x = ∑ i : Fin 4, x i • Pi.single i (1 : K) := by
    funext q; simp [Finset.sum_apply, Pi.single_apply]
  rw [hx]
  exact Submodule.sum_mem _ fun i _ => Submodule.smul_mem _ _ (hunit i)

theorem nOK_spec [CharZero K] (h : nOK = true) (hp : ptOK = true) {m : ℕ} (hm : m < 680) :
    nK K m ≠ 0 ∧ ∀ c < 40, ((fmask m).testBit c = true ↔ ptK K c ⬝ᵥ nK K m = 0) := by
  simp only [nOK, all_range, Bool.and_eq_true, beq_iff_eq, List.any_eq_true, bne_iff_ne, ne_eq] at h
  obtain ⟨⟨hl, a, ha, ha0⟩, hc⟩ := h m hm
  refine ⟨fun h0 => ?_, fun c hc' => ?_⟩
  · obtain ⟨i, hi, rfl⟩ := List.getElem_of_mem ha
    have := congrFun h0 ⟨i, by omega⟩
    simp only [nK, Pi.zero_apply, Int.cast_eq_zero] at this
    apply ha0; rw [← this, List.getD_eq_getElem?_getD, List.getElem?_eq_getElem hi]; rfl
  · have := hc c hc'
    have hd := dotK_cast (K := K) (pt c) (nv m) ((ptOK_spec hp).1 c hc') hl
    rw [this]; unfold ptK nK; rw [← hd]; simp

theorem pfOK_spec (h : pfOK = true) {i j k : ℕ} (hi : i < 40) (hj : j < 40) (hk : k < 40) :
    ∃ m < 680, (fmask m).testBit i = true ∧ (fmask m).testBit j = true ∧ (fmask m).testBit k = true := by
  simp only [pfOK, Bool.and_eq_true, List.all_eq_true, List.any_eq_true, decide_eq_true_eq,
    beq_iff_eq] at h
  obtain ⟨h1, h2⟩ := h i (List.mem_range.mpr hi) j (List.mem_range.mpr hj)
  obtain ⟨⟨m, msk⟩, hmem, hb⟩ := h2 k (List.mem_range.mpr hk)
  obtain ⟨hm, he⟩ := h1 (m, msk) hmem
  simp only at hm he hb
  rw [he] at hb
  exact ⟨m, hm, hb.1.1, hb.1.2, hb.2⟩

theorem clsSpec_spec {u : List ℤ} (h : clsSpec u = true) :
    ((clsOf u).1 = 40 ∧ ∀ a ∈ u, a = 0) ∨
      ((clsOf u).1 < 40 ∧ (clsOf u).2 ≠ 0 ∧ u = (pt (clsOf u).1).map ((clsOf u).2 * ·)) := by
  rcases hc : clsOf u with ⟨c, l⟩
  simp only [clsSpec, hc, Bool.or_eq_true, Bool.and_eq_true, beq_iff_eq, List.all_eq_true, decide_eq_true_eq,
    bne_iff_ne, ne_eq] at h
  rcases h with ⟨h1, h2⟩ | ⟨⟨h1, h2⟩, h3⟩
  · exact Or.inl ⟨h1, h2⟩
  · exact Or.inr ⟨h1, h2, h3⟩

/-- the class decides orthogonality: `Σ u_q A_q = 0 ↔ class 40 or the point is orthogonal to A` -/
theorem cls_dot [CharZero K] (hp : ptOK = true) {u : List ℤ} (hs : clsSpec u = true) (hu : u.length = 4)
    (A : Fin 4 → K) :
    (∑ q : Fin 4, ((u.getD q 0 : ℤ) : K) * A q = 0) ↔ ((clsOf u).1 = 40 ∨ ptK K (clsOf u).1 ⬝ᵥ A = 0) := by
  rcases clsSpec_spec hs with ⟨h40, h0⟩ | ⟨hlt, hl, hmap⟩
  · have : ∀ q : Fin 4, u.getD q 0 = 0 := fun q => by
      rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem (by omega)]; exact h0 _ (List.getElem_mem _)
    rw [Finset.sum_eq_zero (fun q _ => by rw [this q]; simp)]; simp [h40]
  · generalize hcl : clsOf u = cl at hlt hl hmap ⊢
    have hne : cl.1 ≠ 40 := by omega
    have hq : ∀ q : Fin 4, u.getD q 0 = cl.2 * (pt cl.1).getD q 0 := fun q => by
      rw [hmap]; have := List.getD_map (f := (cl.2 * ·)) (l := pt cl.1) (n := q) (d := 0)
      simpa using this
    have hlK : ((cl.2 : ℤ) : K) ≠ 0 := by exact_mod_cast hl
    simp only [hq, Int.cast_mul, mul_assoc, ← Finset.mul_sum, mul_eq_zero, hlK, false_or, hne]
    simp [dotProduct, ptK]

end BForm.E8
