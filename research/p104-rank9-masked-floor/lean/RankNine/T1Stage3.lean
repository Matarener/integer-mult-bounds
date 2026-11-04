import RankNine.T1Tab
import RankNine.T2PairStep
import RankNine.T1Pin

set_option linter.unusedSectionVars false

/-!
# T1 stage 3: degenerate frames, support rounds (hand route, NOTE §13.25 stage 3, T2-LOGIC §1)

For the hard types the closure needs relations from frames that leave the dead set `Z`.  Such a frame `E` gives a
valid expansion when `u ∉ span B(E)` (`expOK_of_indep`).  Otherwise (D1) `u = Σ_{s ∈ σ} c_s B_s` with all `c_s ≠ 0`
for a non-empty `σ ⊆ E ∖ Z`: `σ` is a **support** of `u` (`mT`).  Then
* the dead set grows to `Z ∪ σ^⊥` (`mT_dead`);
* (D2) two different supports `σ, τ` with `σ ∪ τ` orthogonal do not exist (`mT_D2`);
* (ZKILL) if 8 dead rows orthogonal to `s ∈ σ` have a Gram block with non-zero integer minor, then `u ∥ B_s`, so
  `{s}` is a support too (`zkill`, from `pair_minor`).

The data of one type (`St3`) is a branch-(a) record (all frames of `BIG` valid) and a list of support branches
`Br`, checked in order: in branch `σ_i` the supports `σ_j`, `j < i`, are false (`brs_sound`, by induction on the
list), so a frame all of whose possible supports are earlier, or orthogonal-disjoint from `σ_i`, is valid.  Each
branch ends with Gram on the target `zm` (record `T1D` with extra valid frames, `T1D.soundX`) or with ZKILL.  The
records are data; `St3.ok = true` is the table hypothesis, checked by `#eval`.
-/

namespace RankNine.T2

open Matrix RankNine

variable {K : Type*} [Field K] [CharZero K]

/-! ## Masks -/

/-- the mask of a list of lines -/
def lmask (l : List ℕ) : ℕ := l.foldr (fun s a => a ||| 2 ^ s) 0

theorem lmask_bit (l : List ℕ) (s : ℕ) : (lmask l).testBit s = true ↔ s ∈ l := by
  induction l with
  | nil => simp [lmask]
  | cons a l ih =>
    show (lmask l ||| 2 ^ a).testBit s = true ↔ s ∈ a :: l
    rw [Nat.testBit_or, Bool.or_eq_true, ih, Nat.testBit_two_pow, decide_eq_true_eq, List.mem_cons]
    exact ⟨fun h => h.elim Or.inr (fun h => Or.inl h.symm), fun h => h.elim (fun h => Or.inr h.symm) Or.inl⟩

/-- the lines of a mask -/
def msk (σ : ℕ) : Finset ℕ := (Finset.range 104).filter (fun s => σ.testBit s = true)

theorem mem_msk {σ s : ℕ} : s ∈ msk σ ↔ s < 104 ∧ σ.testBit s = true := by
  simp [msk]

/-- the lines of a mask, as a list -/
def bitsL (σ : ℕ) : List ℕ := (List.range 104).filter (fun s => σ.testBit s)

theorem mem_bitsL {σ s : ℕ} : s ∈ bitsL σ ↔ s ∈ msk σ := by
  simp [bitsL, msk]

theorem bitsL_of_msk {σ τ : ℕ} (h : msk σ = msk τ) : bitsL σ = bitsL τ := by
  unfold bitsL
  apply List.filter_congr
  intro s hs
  have := congrArg (fun S => s ∈ S) h
  simp only [mem_msk, List.mem_range.mp hs, true_and, eq_iff_iff] at this
  revert this
  show (σ.testBit s = true ↔ τ.testBit s = true) → σ.testBit s = τ.testBit s
  cases σ.testBit s <;> cases τ.testBit s <;> simp

/-- a mask of pairwise orthogonal lines -/
def orthM (σ : ℕ) : Bool := (bitsL σ).all fun x => (bitsL σ).all fun y => x == y || orthB x y

theorem orthB_eq {x y : ℕ} (hx : x < 104) (hy : y < 104) : orthB x y = orth x y := by
  have h := List.all_eq_true.mp (List.all_eq_true.mp orthB_table x (List.mem_range.mpr hx)) y
    (List.mem_range.mpr hy)
  exact beq_iff_eq.mp h

theorem orthM_sound {σ : ℕ} (h : orthM σ = true) {x y : ℕ} (hx : x ∈ msk σ) (hy : y ∈ msk σ) (hxy : x ≠ y) :
    orth x y = true := by
  have h1 := List.all_eq_true.mp (List.all_eq_true.mp h x (mem_bitsL.mpr hx)) y (mem_bitsL.mpr hy)
  simp only [Bool.or_eq_true, beq_iff_eq] at h1
  rcases h1 with e | e
  · exact absurd e hxy
  · rw [← orthB_eq (mem_msk.mp hx).1 (mem_msk.mp hy).1]; exact e

/-- `a ⊆ b` on the 104 lines -/
def subset104 (a b : ℕ) : Bool := (List.range 104).all fun x => !a.testBit x || b.testBit x

theorem subset104_sound {a b : ℕ} (h : subset104 a b = true) {x : ℕ} (hx : x < 104) (ha : a.testBit x = true) :
    b.testBit x = true := by
  have h1 := List.all_eq_true.mp h x (List.mem_range.mpr hx)
  rw [ha] at h1
  simpa using h1

theorem testBit_big {a x : ℕ} (ha : a < 2 ^ 104) (hx : ¬ x < 104) : a.testBit x = false :=
  Nat.testBit_eq_false_of_lt (lt_of_lt_of_le ha (Nat.pow_le_pow_right (by norm_num) (by omega)))

/-! ## Supports -/

/-- `σ` is a support of `u`: `u = Σ_{s ∈ σ} c_s B_s` with all `c_s ≠ 0` -/
def mT (B : ℕ → Fin 9 → K) (u : Fin 9 → K) (σ : ℕ) : Prop :=
  ∃ c : ℕ → K, (∀ s ∈ msk σ, c s ≠ 0) ∧ u = ∑ s ∈ msk σ, c s • B s

theorem mT_zero {B : ℕ → Fin 9 → K} {u : Fin 9 → K} (h : mT B u 0) : u = 0 := by
  obtain ⟨c, -, hc⟩ := h
  rw [hc]
  exact Finset.sum_eq_zero fun s hs => absurd (mem_msk.mp hs).2 (by simp)

/-- the possible supports of a frame `E` for the dead mask `m`: masks of the sublists of `E ∖ m` -/
def subM (E : List ℕ) (m : ℕ) : List ℕ := (E.filter (fun e => !m.testBit e)).sublists.map lmask

section
variable (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
  (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
include hmask

/-- a support makes its orthogonal lines dead -/
theorem mT_dead {u : Fin 9 → K} {σ : ℕ} (h : mT B u σ) {t : ℕ} (ht : t < 104)
    (hor : ∀ s ∈ msk σ, orth t s = true) : A t ⬝ᵥ u = 0 := by
  obtain ⟨c, -, rfl⟩ := h
  rw [dotProduct_sum]
  exact Finset.sum_eq_zero fun s hs => by
    rw [dotProduct_smul, hmask t ht s (mem_msk.mp hs).1 (hor s hs), smul_zero]

theorem mT_at {u : Fin 9 → K} {σ : ℕ} {c : ℕ → K} (hc : u = ∑ s ∈ msk σ, c s • B s) {x : ℕ} (hx : x < 104)
    (hor : ∀ s ∈ msk σ, s ≠ x → orth x s = true) :
    A x ⬝ᵥ u = if x ∈ msk σ then c x * (A x ⬝ᵥ B x) else 0 := by
  rw [hc, dotProduct_sum]
  split_ifs with hxm
  · rw [Finset.sum_eq_single x (fun s hs hsx => by
      rw [dotProduct_smul, hmask x hx s (mem_msk.mp hs).1 (hor s hs hsx), smul_zero]) (fun h => absurd hxm h),
      dotProduct_smul, smul_eq_mul]
  · exact Finset.sum_eq_zero fun s hs => by
      rw [dotProduct_smul, hmask x hx s (mem_msk.mp hs).1 (hor s hs (fun e => hxm (e ▸ hs))), smul_zero]

include hdiag

/-- **D2.** Two different supports with orthogonal union do not exist. -/
theorem mT_D2 {u : Fin 9 → K} {σ τ : ℕ} (hσ : mT B u σ) (hτ : mT B u τ) (hne : bitsL σ ≠ bitsL τ)
    (ho : orthM (σ ||| τ) = true) : False := by
  obtain ⟨c, hc0, hc⟩ := hσ
  obtain ⟨d, hd0, hd⟩ := hτ
  have hsub : ∀ {s}, s ∈ msk σ ∨ s ∈ msk τ → s ∈ msk (σ ||| τ) := by
    intro s hs
    rw [mem_msk, Nat.testBit_or, Bool.or_eq_true]
    rcases hs with hs | hs
    · exact ⟨(mem_msk.mp hs).1, Or.inl (mem_msk.mp hs).2⟩
    · exact ⟨(mem_msk.mp hs).1, Or.inr (mem_msk.mp hs).2⟩
  have key : ∀ x, x ∈ msk σ ∨ x ∈ msk τ → (x ∈ msk σ ↔ x ∈ msk τ) := by
    intro x hx
    have hx104 : x < 104 := by rcases hx with h | h <;> exact (mem_msk.mp h).1
    have hor : ∀ ρ : ℕ, (∀ s ∈ msk ρ, s ∈ msk σ ∨ s ∈ msk τ) → ∀ s ∈ msk ρ, s ≠ x → orth x s = true :=
      fun ρ hρ s hs hsx => orthM_sound ho (hsub hx) (hsub (hρ s hs)) (Ne.symm hsx)
    have e1 := mT_at A B hmask hc hx104 (hor σ fun s hs => Or.inl hs)
    have e2 := mT_at A B hmask hd hx104 (hor τ fun s hs => Or.inr hs)
    have hxx := hdiag x hx104
    constructor
    · intro h1
      by_contra h2
      rw [if_pos h1] at e1
      rw [if_neg h2] at e2
      exact mul_ne_zero (hc0 x h1) hxx (e1.symm.trans e2)
    · intro h2
      by_contra h1
      rw [if_neg h1] at e1
      rw [if_pos h2] at e2
      exact mul_ne_zero (hd0 x h2) hxx (e2.symm.trans e1)
  apply hne
  apply bitsL_of_msk
  ext x
  constructor
  · intro h; exact (key x (Or.inl h)).mp h
  · intro h; exact (key x (Or.inr h)).mpr h

/-- **D1.** A degenerate frame has a support inside `E ∖ m`. -/
theorem deg_support (u : Fin 9 → K) (m : ℕ) (hu : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (F : List ℕ)
    (hF : frameOK F = true)
    (hdeg : ¬ LinearIndependent K (Fin.cons u (fun k => B (fr F k)) : Fin 9 → Fin 9 → K)) :
    ∃ σ ∈ subM F m, mT B u σ := by
  classical
  obtain ⟨hl, hn, hlt, hd, hoff⟩ := frame_facts A B hdiag hmask F hF
  obtain ⟨c, hc0, hc⟩ := degenerate_repr A B u (fr F) (Finset.univ.filter fun k => m.testBit (fr F k) = true)
    hdeg (fun k hk => hu _ (Finset.mem_filter.mp hk).2) hd hoff
  let c' : ℕ → K := fun s => if h : ∃ k, fr F k = s then c h.choose else 0
  have hc' : ∀ k, c' (fr F k) = c k := by
    intro k
    have h : ∃ k', fr F k' = fr F k := ⟨k, rfl⟩
    show (if h : ∃ k', fr F k' = fr F k then c h.choose else 0) = c k
    rw [dif_pos h]
    exact congrArg c (fr_inj F hl hn h.choose_spec)
  let L := (F.filter (fun e => !m.testBit e)).filter (fun e => decide (c' e ≠ 0))
  have hmemL : ∀ s, s ∈ L ↔ (s ∈ F ∧ m.testBit s = false) ∧ c' s ≠ 0 := by
    intro s
    simp [L, List.mem_filter]
    tauto
  refine ⟨lmask L, List.mem_map.mpr ⟨L, List.mem_sublists.mpr (List.filter_sublist ..), rfl⟩, c', ?_, ?_⟩
  · intro s hs
    exact ((hmemL s).mp ((lmask_bit L s).mp (mem_msk.mp hs).2)).2
  · have h1 : u = ∑ s ∈ Finset.univ.image (fr F), c' s • B s := by
      rw [Finset.sum_image (fun k _ l _ h => fr_inj F hl hn h), hc]
      exact Finset.sum_congr rfl fun k _ => by rw [hc']
    rw [h1]
    symm
    apply Finset.sum_subset
    · intro s hs
      have hL := (hmemL s).mp ((lmask_bit L s).mp (mem_msk.mp hs).2)
      obtain ⟨k, rfl⟩ := mem_fr F hl hL.1.1
      exact Finset.mem_image_of_mem _ (Finset.mem_univ k)
    · intro s hs hns
      obtain ⟨k, -, rfl⟩ := Finset.mem_image.mp hs
      have h0 : c' (fr F k) = 0 := by
        by_contra hne
        apply hns
        rw [mem_msk]
        refine ⟨hlt k, (lmask_bit L _).mpr ((hmemL _).mpr ⟨⟨fr_mem F hl k, ?_⟩, hne⟩)⟩
        cases hb : m.testBit (fr F k)
        · rfl
        · exact (hne (by rw [hc']; exact hc0 k (Finset.mem_filter.mpr ⟨Finset.mem_univ _, hb⟩))).elim
      rw [h0, zero_smul]

/-- a frame without a possible support gives a valid expansion -/
theorem expOK_of_nosupp (u : Fin 9 → K) (m : ℕ) (hu : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (F : List ℕ)
    (hF : frameOK F = true) (hno : ∀ σ ∈ subM F m, ¬ mT B u σ) : ExpOK A B m F :=
  expOK_of_indep A B hdiag hmask u m hu F hF (by
    by_contra hdeg
    obtain ⟨σ, hσ, h⟩ := deg_support A B hdiag hmask u m hu F hF hdeg
    exact hno σ hσ h)

/-- **ZKILL.** Rows dead for `u` and orthogonal to `s`, with a Gram block of non-zero integer minor, force
`u ∥ B_s`. -/
theorem zkill {u : Fin 9 → K} (hu0 : u ≠ 0) (g : ℕ → K) (hg : ∀ x, g x ≠ 0) (s : ℕ) (hs : s < 104)
    (X Y : Fin 8 → ℕ) (hX : ∀ i, X i < 104) (hXu : ∀ i, A (X i) ⬝ᵥ u = 0) (hXs : ∀ i, orth (X i) s = true)
    (hG : ∀ i k, GramP A B g (X i) (Y k)) (D : Matrix (Fin 8) (Fin 8) ℤ) (hD : D.det ≠ 0)
    (hDd : ∀ i k, D i k = dot (X i) (Y k)) : mT B u (2 ^ s) := by
  classical
  by_cases hind : LinearIndependent K ![u, B s]
  · exfalso
    refine pair_minor A B u (B s) hind X Y hXu (fun i => hmask _ (hX i) s hs (hXs i))
      (fun x => if dS A B g x = 0 then 1 else 18 / dS A B g x) (fun y => (g y)⁻¹) ?_
      (fun y => inv_ne_zero (hg y)) D hD ?_
    · intro x
      split_ifs with h
      · exact one_ne_zero
      · exact div_ne_zero (by norm_num) h
    · intro i k
      have hdx : dS A B g (X i) ≠ 0 := div_ne_zero (hdiag _ (hX i)) (hg _)
      have hGik := hG i k
      unfold GramP gam at hGik
      rw [if_neg hdx, hGik, hDd i k]
      have hgk := hg (Y k)
      first | (field_simp; done) | (field_simp; ring)
  · rw [LinearIndependent.pair_iff] at hind
    push_neg at hind
    obtain ⟨a, b, hab, hne⟩ := hind
    have hBs : B s ≠ 0 := fun h0 => hdiag s hs (by rw [h0, dotProduct_zero])
    have ha : a ≠ 0 := by
      intro ha0
      rw [ha0, zero_smul, zero_add] at hab
      exact hne ha0 ((smul_eq_zero.mp hab).resolve_right hBs)
    have hu' : u = (-b / a) • B s := by
      have e : a • u = -(b • B s) := eq_neg_of_add_eq_zero_left hab
      calc u = a⁻¹ • (a • u) := by rw [smul_smul, inv_mul_cancel₀ ha, one_smul]
        _ = (-b / a) • B s := by
          rw [e, smul_neg, smul_smul, ← neg_smul]
          congr 1
          rw [neg_div, div_eq_inv_mul]
    have hmsk : msk (2 ^ s) = {s} := by
      ext x
      rw [mem_msk, Nat.testBit_two_pow, decide_eq_true_eq, Finset.mem_singleton]
      constructor
      · rintro ⟨-, h⟩; exact h.symm
      · rintro rfl; exact ⟨hs, rfl⟩
    refine ⟨fun _ => -b / a, fun x _ h0 => hu0 (by rw [hu', show -b / a = 0 from h0, zero_smul]), ?_⟩
    rw [hmsk, Finset.sum_singleton]
    exact hu'

end

/-! ## T1 records with extra valid frames -/

/-- a frame inside `m`, or one of the extra frames `XF` -/
def frInX (m : ℕ) (XF : List (List ℕ)) (F : List ℕ) : Bool := frameOK F && (F.all m.testBit || decide (F ∈ XF))

def t1FramesOKX (DS : BT (List ℕ)) (m : ℕ) (XF : List (List ℕ)) : Bool :=
  (List.range (2 ^ DS.dp)).all fun a =>
    if (DS.get [] a).length = 29 then (List.range 3).all fun i => frInX m XF (fr3 (DS.get [] a) i)
    else if (DS.get [] a).length = 21 then (List.range 2).all fun i => frInX m XF (fr3 (DS.get [] a) i)
    else DS.get [] a == [] || frInX m XF (dfr (DS.get [] a))

def zFramesOKX (FT : BT (List ℕ)) (m : ℕ) (XF : List (List ℕ)) : Bool :=
  (List.range (2 ^ FT.dp)).all fun fi => FT.get [] fi == [] || frInX m XF (FT.get [] fi)

/-- **the check of one T1 record with extra frames `XF`** (same as `T1D.ok` otherwise) -/
def T1D.okX (d : T1D) (XF : List (List ℕ)) : Bool :=
  check d.C && glue1OK d.C d.EI d.ER d.EC d.DS d.nE d.m d.T d.r0 && cov1OK d.EI d.ER d.EC d.nE d.zm d.C.NE &&
  t1FramesOKX d.DS d.m XF && zFramesOKX d.zFT d.m XF &&
  (List.range d.zn).all (entryOK d.m 104 d.zG d.zVT d.zFT d.zEN) &&
  decide (clOf d.zG (d.zEN.get [] (d.zn - 1)) = (0, 0)) && decide (0 < d.zn) && zEdges d

section
variable (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
  (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (u : Fin 9 → K) (hu0 : u ≠ 0) (m : ℕ)
  (hu : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (XF : List (List ℕ))
  (hX : ∀ F ∈ XF, frameOK F = true → ExpOK A B m F)
include hdiag hmask hu0 hu hX

theorem expOK_frInX {F : List ℕ} (h : frInX m XF F = true) : ExpOK A B m F := by
  unfold frInX at h
  simp only [Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq] at h
  obtain ⟨hF, h | h⟩ := h
  · exact expOK_of_dead A B hdiag hmask u hu0 m hu F hF h
  · exact hX F h hF

theorem t1FramesX_get {DS : BT (List ℕ)} (h : t1FramesOKX DS m XF = true) {a : ℕ} (ha : DS.get [] a ≠ []) :
    (if (DS.get [] a).length = 29 then (List.range 3).all fun i => frInX m XF (fr3 (DS.get [] a) i)
      else if (DS.get [] a).length = 21 then (List.range 2).all fun i => frInX m XF (fr3 (DS.get [] a) i)
      else DS.get [] a == [] || frInX m XF (dfr (DS.get [] a))) = true := by
  by_cases hlt : a < 2 ^ DS.dp
  · exact List.all_eq_true.mp h a (List.mem_range.mpr hlt)
  · exact absurd (BT.get_big _ _ _ (Nat.not_lt.mp hlt)) ha

theorem t1X_hExp {DS : BT (List ℕ)} (h : t1FramesOKX DS m XF = true) :
    ∀ a, (DS.get [] a).length ≠ 29 → (DS.get [] a).length ≠ 21 → DS.get [] a ≠ [] →
      ExpOK A B m (dfr (DS.get [] a)) := by
  intro a h29 h21 ha
  have hg := t1FramesX_get A B hdiag hmask u hu0 m hu XF hX h ha
  rw [if_neg h29, if_neg h21] at hg
  simp only [Bool.or_eq_true, beq_iff_eq] at hg
  rcases hg with h0 | hf
  · exact absurd h0 ha
  · exact expOK_frInX A B hdiag hmask u hu0 m hu XF hX hf

theorem t1X_hExp3 {DS : BT (List ℕ)} (h : t1FramesOKX DS m XF = true) :
    ∀ a, (DS.get [] a).length = 29 → ∀ i < 3, ExpOK A B m (fr3 (DS.get [] a) i) := by
  intro a h29 i hi
  have ha : DS.get [] a ≠ [] := fun h0 => by rw [h0] at h29; simp at h29
  have hg := t1FramesX_get A B hdiag hmask u hu0 m hu XF hX h ha
  rw [if_pos h29] at hg
  exact expOK_frInX A B hdiag hmask u hu0 m hu XF hX (List.all_eq_true.mp hg i (List.mem_range.mpr hi))

theorem t1X_hExp2 {DS : BT (List ℕ)} (h : t1FramesOKX DS m XF = true) :
    ∀ a, (DS.get [] a).length = 21 → ∀ i < 2, ExpOK A B m (fr3 (DS.get [] a) i) := by
  intro a h21 i hi
  have ha : DS.get [] a ≠ [] := fun h0 => by rw [h0] at h21; simp at h21
  have h29 : (DS.get [] a).length ≠ 29 := by omega
  have hg := t1FramesX_get A B hdiag hmask u hu0 m hu XF hX h ha
  rw [if_neg h29, if_pos h21] at hg
  exact expOK_frInX A B hdiag hmask u hu0 m hu XF hX (List.all_eq_true.mp hg i (List.mem_range.mpr hi))

theorem zX_hFT {FT : BT (List ℕ)} (h : zFramesOKX FT m XF = true) :
    ∀ fi, FT.get [] fi ≠ [] → ExpOK A B m (FT.get [] fi) := by
  intro fi hf
  by_cases hlt : fi < 2 ^ FT.dp
  · have hg := List.all_eq_true.mp h fi (List.mem_range.mpr hlt)
    simp only [Bool.or_eq_true, beq_iff_eq] at hg
    rcases hg with h0 | hF
    · exact absurd h0 hf
    · exact expOK_frInX A B hdiag hmask u hu0 m hu XF hX hF
  · exact absurd (BT.get_big _ _ _ (Nat.not_lt.mp hlt)) hf

end

/-- **T1 for one record with extra valid frames.** -/
theorem T1D.soundX (d : T1D) (XF : List (List ℕ)) (h : d.okX XF = true) (A B : ℕ → Fin 9 → K)
    (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (u : Fin 9 → K) (hu0 : u ≠ 0)
    (hu : ∀ x, d.m.testBit x = true → A x ⬝ᵥ u = 0) (hX : ∀ F ∈ XF, frameOK F = true → ExpOK A B d.m F) :
    ∃ g : ℕ → K, (∀ x, g x ≠ 0) ∧
      ∀ x < 104, ∀ y < 104, d.zm.testBit x = true → d.zm.testBit y = true → GramP A B g x y := by
  unfold T1D.okX at h
  simp only [Bool.and_eq_true] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨hc, hg⟩, hcov⟩, hfr⟩, hzfr⟩, hall⟩, hlast⟩, hn⟩, hze⟩ := h
  have hMnz := t2_zero A B hdiag hmask d.m 104 d.zG (fun h => absurd h (lt_irrefl _)) d.zVT d.zFT d.zEN
    (zX_hFT A B hdiag hmask u hu0 d.m hu XF hX hzfr) d.zn
    (fun j hj => List.all_eq_true.mp hall j (List.mem_range.mpr hj)) (of_decide_eq_true hlast)
    (of_decide_eq_true hn) d.ER d.EC d.zGV d.nE hze
  exact t1_gram A B hdiag hmask d.C d.EI d.ER d.EC d.DS d.nE d.m d.zm d.T d.r0 hc hg hcov
    (t1X_hExp A B hdiag hmask u hu0 d.m hu XF hX hfr) (t1X_hExp3 A B hdiag hmask u hu0 d.m hu XF hX hfr)
    (t1X_hExp2 A B hdiag hmask u hu0 d.m hu XF hX hfr) hMnz

/-! ## Pins after a record -/

/-- rank-7 pins after a record (frame `f` inside its Gram set, needed by `rows_rep` when there are pins) -/
def pinsOK (d : T1D) (f : ℕ) (PL : List (ℕ × ℕ × RCert)) : Bool :=
  pinOK d.m d.zm PL &&
    (PL.isEmpty || (frInOK d.m d.zm f && fvecOK f && subset104 d.zm d.m && decide (d.zm < 2 ^ 104)))

theorem pins_sound (d : T1D) (f : ℕ) (PL : List (ℕ × ℕ × RCert)) (h : pinsOK d f PL = true)
    (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (u : Fin 9 → K) (hu0 : u ≠ 0)
    (hu : ∀ x, d.m.testBit x = true → A x ⬝ᵥ u = 0) (g : ℕ → K) (hg : ∀ x, g x ≠ 0)
    (hG : ∀ x < 104, ∀ y < 104, d.zm.testBit x = true → d.zm.testBit y = true → GramP A B g x y) :
    ∃ g' : ℕ → K, (∀ x, g' x ≠ 0) ∧
      ∀ x < 104, ∀ y < 104, (pinZ d.zm PL).testBit x = true → (pinZ d.zm PL).testBit y = true → GramP A B g' x y := by
  unfold pinsOK at h
  simp only [Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq] at h
  obtain ⟨hp, he | ⟨⟨⟨hfin, hfv⟩, hsub⟩, hz⟩⟩ := h
  · rw [List.isEmpty_iff.mp he]
    exact ⟨g, hg, hG⟩
  · have hf : ∀ k < 8, d.m.testBit (frL f k) = true ∧ d.zm.testBit (frL f k) = true := by
      intro k hk
      have := (List.all_eq_true.mp hfin) k (List.mem_range.mpr hk)
      simpa only [Bool.and_eq_true] using this
    have hzm : ∀ x, d.zm.testBit x = true → d.m.testBit x = true := by
      intro x hx
      by_cases hx104 : x < 104
      · exact subset104_sound hsub hx104 hx
      · rw [testBit_big hz hx104] at hx; exact absurd hx (by simp)
    exact pin_all A B u hu0 d.m hu hdiag hmask f hfv PL d.zm g hg hz hzm hf hp hG

/-! ## Support branches -/

/-- one support branch: support `σ`, a record on the dead mask `d.m ⊆ Z ∪ σ^⊥` with extra frames `XF`; it ends
with Gram on the target (`s = 104`) or with ZKILL at the line `s ∈ σ` (rows `X`, columns `Y`, adjugate `J`, `dd`) -/
structure Br where
  σ : ℕ
  d : T1D
  XF : List (List ℕ)
  s : ℕ
  X : List ℕ
  Y : List ℕ
  J : List (List ℤ)
  dd : ℤ
  f : ℕ
  PL : List (ℕ × ℕ × RCert)

/-- the integer block `dot X Y` -/
def dotM (X Y : List ℕ) : Matrix (Fin 8) (Fin 8) ℤ := Matrix.of fun i k => dot (X.getD i 0) (Y.getD k 0)

def jM (J : List (List ℤ)) : Matrix (Fin 8) (Fin 8) ℤ := Matrix.of fun i k => (J.getD i []).getD k 0

/-- the extra frames of a branch are valid: every possible support is excluded (earlier, or D2) -/
def xfOK (XF : List (List ℕ)) (m σ : ℕ) (prev : List ℕ) : Bool :=
  XF.all fun E => frameOK E && (subM E m).all fun τ =>
    τ == 0 || decide (τ ∈ prev) || (bitsL τ != bitsL σ && orthM (σ ||| τ))

/-- the ZKILL part of a branch (`zP` the Gram set after the pins) -/
def zkOK (b : Br) (prev : List ℕ) (zP : ℕ) : Bool :=
  decide (b.s < 104) && b.σ.testBit b.s && decide (b.X.length = 8) && decide (b.Y.length = 8) &&
  b.X.all (fun x => decide (x < 104) && b.d.m.testBit x && zP.testBit x && orthB x b.s) &&
  b.Y.all (fun y => decide (y < 104) && zP.testBit y) &&
  b.dd != 0 && decide (dotM b.X b.Y * jM b.J = b.dd • (1 : Matrix (Fin 8) (Fin 8) ℤ)) &&
  (decide (2 ^ b.s ∈ prev) || (bitsL (2 ^ b.s) != bitsL b.σ && orthM (b.σ ||| 2 ^ b.s)))

/-- **the check of one branch** (`m0` the type mask, `zm` the target, `prev` the earlier supports) -/
def Br.ok (b : Br) (m0 zm : ℕ) (prev : List ℕ) : Bool :=
  b.d.okX b.XF && decide (b.d.m < 2 ^ 104) &&
  (List.range 104).all (fun x => !b.d.m.testBit x || m0.testBit x || (bitsL b.σ).all (fun s => orthB x s)) &&
  xfOK b.XF b.d.m b.σ prev && pinsOK b.d b.f b.PL &&
  (if b.s = 104 then subset104 zm (pinZ b.d.zm b.PL) else zkOK b prev (pinZ b.d.zm b.PL))

/-- the branches in order: each with the supports before it -/
def brsOK (m0 zm : ℕ) : List ℕ → List Br → Bool
  | _, [] => true
  | prev, b :: r => b.ok m0 zm prev && brsOK m0 zm (prev ++ [b.σ]) r

theorem getD_mem8 {l : List ℕ} (hl : l.length = 8) (i : Fin 8) : l.getD i 0 ∈ l := by
  rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem (by omega), Option.getD_some]
  exact List.getElem_mem _

theorem det_of_adj (D J : Matrix (Fin 8) (Fin 8) ℤ) (d : ℤ) (hd : d ≠ 0)
    (hDJ : D * J = d • (1 : Matrix (Fin 8) (Fin 8) ℤ)) : D.det ≠ 0 := by
  have hZ : D.det * J.det = d ^ 8 := by
    rw [← Matrix.det_mul, hDJ, Matrix.det_smul, Matrix.det_one, mul_one, Fintype.card_fin]
  intro h0
  rw [h0, zero_mul] at hZ
  exact pow_ne_zero 8 hd hZ.symm

section
variable (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
  (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (u : Fin 9 → K) (hu0 : u ≠ 0) (m0 zm : ℕ)
  (hu : ∀ x, m0.testBit x = true → A x ⬝ᵥ u = 0)
include hdiag hmask hu0 hu

/-- **one branch**: if `σ` is a support and no earlier support is, the target is Gram -/
theorem br_sound (b : Br) (prev : List ℕ) (h : b.ok m0 zm prev = true) (hσ : mT B u b.σ)
    (hprev : ∀ τ ∈ prev, ¬ mT B u τ) :
    ∃ g : ℕ → K, (∀ x, g x ≠ 0) ∧
      ∀ x < 104, ∀ y < 104, zm.testBit x = true → zm.testBit y = true → GramP A B g x y := by
  unfold Br.ok at h
  simp only [Bool.and_eq_true] at h
  obtain ⟨⟨⟨⟨⟨hd, hmlt⟩, hdead⟩, hxf⟩, hpins⟩, hend⟩ := h
  have hmlt' := of_decide_eq_true hmlt
  -- the dead rows of the branch
  have hu' : ∀ x, b.d.m.testBit x = true → A x ⬝ᵥ u = 0 := by
    intro x hx
    by_cases hx104 : x < 104
    · have h1 := List.all_eq_true.mp hdead x (List.mem_range.mpr hx104)
      simp only [hx, Bool.not_true, Bool.false_or, Bool.or_eq_true] at h1
      rcases h1 with h1 | h1
      · exact hu x h1
      · refine mT_dead A B hmask hσ hx104 fun s hs => ?_
        have h2 := List.all_eq_true.mp h1 s (mem_bitsL.mpr hs)
        rwa [orthB_eq hx104 (mem_msk.mp hs).1] at h2
    · rw [testBit_big hmlt' hx104] at hx
      exact absurd hx (by simp)
  -- the extra frames are valid
  have hX : ∀ F ∈ b.XF, frameOK F = true → ExpOK A B b.d.m F := by
    intro F hF hFo
    have h1 := List.all_eq_true.mp hxf F hF
    simp only [Bool.and_eq_true] at h1
    refine expOK_of_nosupp A B hdiag hmask u b.d.m hu' F hFo fun τ hτ hmT => ?_
    have h2 := List.all_eq_true.mp h1.2 τ hτ
    simp only [Bool.or_eq_true, beq_iff_eq, decide_eq_true_eq, Bool.and_eq_true, bne_iff_ne] at h2
    rcases h2 with (h2 | h2) | ⟨h2, h3⟩
    · subst h2; exact hu0 (mT_zero hmT)
    · exact hprev τ h2 hmT
    · exact mT_D2 A B hdiag hmask hσ hmT (Ne.symm h2) h3
  obtain ⟨g0, hg0, hG0⟩ := b.d.soundX b.XF hd A B hdiag hmask u hu0 hu' hX
  obtain ⟨g, hg, hG⟩ := pins_sound b.d b.f b.PL hpins A B hdiag hmask u hu0 hu' g0 hg0 hG0
  by_cases hs : b.s = 104
  · rw [if_pos hs] at hend
    exact ⟨g, hg, fun x hx y hy hzx hzy =>
      hG x hx y hy (subset104_sound hend hx hzx) (subset104_sound hend hy hzy)⟩
  · rw [if_neg hs] at hend
    exfalso
    unfold zkOK at hend
    simp only [Bool.and_eq_true, decide_eq_true_eq, bne_iff_ne, Bool.or_eq_true] at hend
    obtain ⟨⟨⟨⟨⟨⟨⟨⟨hs104, hsσ⟩, hXl⟩, hYl⟩, hXc⟩, hYc⟩, hdd⟩, hDJ⟩, hlast⟩ := hend
    have hXi : ∀ i : Fin 8, b.X.getD i 0 < 104 ∧ b.d.m.testBit (b.X.getD i 0) = true ∧
        (pinZ b.d.zm b.PL).testBit (b.X.getD i 0) = true ∧ orthB (b.X.getD i 0) b.s = true := by
      intro i
      have h1 := List.all_eq_true.mp hXc _ (getD_mem8 hXl i)
      simp only [Bool.and_eq_true, decide_eq_true_eq] at h1
      exact ⟨h1.1.1.1, h1.1.1.2, h1.1.2, h1.2⟩
    have hYi : ∀ k : Fin 8, b.Y.getD k 0 < 104 ∧ (pinZ b.d.zm b.PL).testBit (b.Y.getD k 0) = true := by
      intro k
      have h1 := List.all_eq_true.mp hYc _ (getD_mem8 hYl k)
      simp only [Bool.and_eq_true, decide_eq_true_eq] at h1
      exact h1
    have hmTs := zkill A B hdiag hmask hu0 g hg b.s hs104 (fun i => b.X.getD i 0) (fun k => b.Y.getD k 0)
      (fun i => (hXi i).1) (fun i => hu' _ (hXi i).2.1)
      (fun i => by have h0 := (hXi i).2.2.2; rw [orthB_eq (hXi i).1 hs104] at h0; exact h0)
      (fun i k => hG _ (hXi i).1 _ (hYi k).1 (hXi i).2.2.1 (hYi k).2) (dotM b.X b.Y)
      (det_of_adj _ _ _ hdd hDJ) (fun i k => rfl)
    rcases hlast with h1 | ⟨h1, h2⟩
    · exact hprev _ h1 hmTs
    · exact mT_D2 A B hdiag hmask hσ hmTs (Ne.symm h1) h2

/-- **the branches in order**: if some branch support is a support, the target is Gram -/
theorem brs_sound : ∀ (bs : List Br) (prev : List ℕ), brsOK m0 zm prev bs = true → (∀ τ ∈ prev, ¬ mT B u τ) →
    (∃ b ∈ bs, mT B u b.σ) →
    ∃ g : ℕ → K, (∀ x, g x ≠ 0) ∧
      ∀ x < 104, ∀ y < 104, zm.testBit x = true → zm.testBit y = true → GramP A B g x y
  | [], _, _, _, hex => by obtain ⟨b, hb, -⟩ := hex; simp at hb
  | b :: r, prev, h, hprev, hex => by
    unfold brsOK at h
    simp only [Bool.and_eq_true] at h
    by_cases hb : mT B u b.σ
    · exact br_sound A B hdiag hmask u hu0 m0 zm hu b prev h.1 hb hprev
    · refine brs_sound r (prev ++ [b.σ]) h.2 (fun τ hτ => ?_) ?_
      · rcases List.mem_append.mp hτ with h1 | h1
        · exact hprev τ h1
        · rw [List.mem_singleton.mp h1]; exact hb
      · obtain ⟨c, hc, hcm⟩ := hex
        rcases List.mem_cons.mp hc with e | e
        · subst e; exact absurd hcm hb
        · exact ⟨c, e, hcm⟩

end

/-! ## One stage-3 type -/

/-- the stage-3 data of one type: type mask `m0`, target `zm`, frames `BIG` (all their possible supports are among
the branches), branch (a) record `d0` (all of `BIG` valid), the support branches `B` -/
structure St3 where
  m0 : ℕ
  zm : ℕ
  BIG : List (List ℕ)
  d0 : T1D
  f0 : ℕ
  PL0 : List (ℕ × ℕ × RCert)
  B : List Br

/-- **the check of one stage-3 type** -/
def St3.ok (st : St3) : Bool :=
  st.d0.okX st.BIG && st.d0.m == st.m0 && pinsOK st.d0 st.f0 st.PL0 && subset104 st.zm (pinZ st.d0.zm st.PL0) &&
  st.BIG.all (fun E => frameOK E && (subM E st.m0).all fun τ => τ == 0 || decide (τ ∈ st.B.map Br.σ)) &&
  brsOK st.m0 st.zm [] st.B

/-- **T1 for one stage-3 type**: Gram on the target `zm`. -/
theorem St3.sound (st : St3) (h : st.ok = true) (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (u : Fin 9 → K) (hu0 : u ≠ 0)
    (hu : ∀ x, st.m0.testBit x = true → A x ⬝ᵥ u = 0) :
    ∃ g : ℕ → K, (∀ x, g x ≠ 0) ∧
      ∀ x < 104, ∀ y < 104, st.zm.testBit x = true → st.zm.testBit y = true → GramP A B g x y := by
  unfold St3.ok at h
  simp only [Bool.and_eq_true, beq_iff_eq] at h
  obtain ⟨⟨⟨⟨⟨hd0, hm0⟩, hpins⟩, hzm⟩, hbig⟩, hbrs⟩ := h
  by_cases hex : ∃ b ∈ st.B, mT B u b.σ
  · exact brs_sound A B hdiag hmask u hu0 st.m0 st.zm hu st.B [] hbrs (fun τ h => by simp at h) hex
  · push_neg at hex
    have hu' : ∀ x, st.d0.m.testBit x = true → A x ⬝ᵥ u = 0 := by rw [hm0]; exact hu
    have hX : ∀ F ∈ st.BIG, frameOK F = true → ExpOK A B st.d0.m F := by
      intro F hF hFo
      rw [hm0]
      refine expOK_of_nosupp A B hdiag hmask u st.m0 hu F hFo fun τ hτ hmT => ?_
      have h1 := List.all_eq_true.mp hbig F hF
      simp only [Bool.and_eq_true] at h1
      have h2 := List.all_eq_true.mp h1.2 τ hτ
      simp only [Bool.or_eq_true, beq_iff_eq, decide_eq_true_eq] at h2
      rcases h2 with h2 | h2
      · subst h2; exact hu0 (mT_zero hmT)
      · obtain ⟨b, hb, rfl⟩ := List.mem_map.mp h2
        exact hex b hb hmT
    obtain ⟨g0, hg0, hG0⟩ := st.d0.soundX st.BIG hd0 A B hdiag hmask u hu0 hu' hX
    obtain ⟨g, hg, hG⟩ := pins_sound st.d0 st.f0 st.PL0 hpins A B hdiag hmask u hu0 hu' g0 hg0 hG0
    exact ⟨g, hg, fun x hx y hy hzx hzy => hG x hx y hy (subset104_sound hzm hx hzx) (subset104_sound hzm hy hzy)⟩

end RankNine.T2
