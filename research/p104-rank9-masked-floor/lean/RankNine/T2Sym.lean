import RankNine.T2Main

set_option linter.unusedSectionVars false

/-!
# T2 by support orbits (stabiliser transport, joint kills)

For a frameless representative `c` the support branches of `T2Hand` are replaced by **items**, one per support orbit
(and per joint pair `(S, S')`, NOTE §13.24), in closing order.  Item `j = (σ, ctx)` (`ctx = 0`: plain) assumes
`Hyp j`: `σ` is a support of `u`, and so is `ctx` if `ctx ≠ 0`.  The statement proved for every item, by induction
on `j`, is

  `P j`: for every decoder with `c` dead for `u` and an independent `v` dead on some `c' ∈ FL` (`Bad`), `¬ Hyp j`.

It is invariant under the stabiliser `G` of `c` (`bad_perm`, `mT_img`), so in item `j` every image `g(item i)`,
`i < j`, is excluded too: a possible support `τ` of a frame is excluded by a witness `(τ, i, g, kind)`
(`exclB`, `excl_sound`).  Item `j` then gives Gram on the target (`it_sound`, as `br_sound`), and the pair
certificates give the contradiction (`gram_false`).  Branch (a) (no support): all frames valid, Gram, contradiction.
-/

namespace RankNine.T2S

open Matrix RankNine RankNine.T2 RankNine.Facts

variable {K : Type} [Field K] [CharZero K]

/-! ## Images of masks -/

/-- the image of the mask `σ` under the group element `g` -/
def imgM (g σ : ℕ) : ℕ := T2.lmask ((bitsL σ).map (gl g))

theorem mem_msk_img (hgrp : grpOK = true) {g : ℕ} (hg : g < 384) {σ t : ℕ} :
    t ∈ msk (imgM g σ) ↔ ∃ s ∈ msk σ, gl g s = t := by
  rw [mem_msk, imgM, T2.lmask_bit, List.mem_map]
  constructor
  · rintro ⟨-, s, hs, e⟩; exact ⟨s, mem_bitsL.mp hs, e⟩
  · rintro ⟨s, hs, e⟩
    exact ⟨e ▸ (grp_facts hgrp hg (mem_msk.mp hs).1).1, s, mem_bitsL.mpr hs, e⟩

theorem imgM_zero (g : ℕ) : imgM g 0 = 0 := by
  simp [imgM, bitsL, T2.lmask]

/-- supports transport: a support `g(σ)` of `u` for `B` is the support `σ` of `u` for `B ∘ g` -/
theorem mT_img (hgrp : grpOK = true) {g : ℕ} (hg : g < 384) {B : ℕ → Fin 9 → K} {u : Fin 9 → K} {σ : ℕ}
    (h : mT B u (imgM g σ)) : mT (fun x => B (Tr.pn (permOf hgrp hg) x)) u σ := by
  classical
  obtain ⟨c, hc0, hc⟩ := h
  have himg : msk (imgM g σ) = (msk σ).image (gl g) := by
    ext t
    rw [mem_msk_img hgrp hg, Finset.mem_image]
  have hinj : ∀ x ∈ msk σ, ∀ y ∈ msk σ, gl g x = gl g y → x = y := by
    intro x hx y hy e
    have hx' := (grp_facts hgrp hg (mem_msk.mp hx).1).2.2.1
    have hy' := (grp_facts hgrp hg (mem_msk.mp hy).1).2.2.1
    rw [← hx', ← hy', e]
  refine ⟨fun s => c (gl g s), fun s hs => hc0 _ ((mem_msk_img hgrp hg).mpr ⟨s, hs, rfl⟩), ?_⟩
  rw [hc, himg, Finset.sum_image hinj]
  refine Finset.sum_congr rfl fun s hs => ?_
  rw [pn_permOf hgrp hg (mem_msk.mp hs).1]

/-! ## The invariant statement -/

/-- the hypothesis of item `p = (σ, ctx)` -/
def Hyp (B : ℕ → Fin 9 → K) (u : Fin 9 → K) (p : ℕ × ℕ) : Prop := mT B u p.1 ∧ (p.2 = 0 ∨ mT B u p.2)

/-- a T2 configuration on the frameless set `c`: dead rows on `c` for `u`, an independent `v` dead on some `c' ∈ FL` -/
def Bad (c : ℕ) (FL : List ℕ) (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) : Prop :=
  (∀ x < 104, A x ⬝ᵥ B x ≠ 0) ∧ (∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) ∧
    (∀ x, c.testBit x = true → A x ⬝ᵥ u = 0) ∧
    ∃ v : Fin 9 → K, LinearIndependent K ![u, v] ∧ ∃ c' ∈ FL, ∀ x, c'.testBit x = true → A x ⬝ᵥ v = 0

/-- the stabiliser list `G` maps `c` into itself -/
def stabOK (c : ℕ) (G : List ℕ) : Bool :=
  decide (c < 2 ^ 104) && G.all fun g => decide (g < 384) && (List.range 104).all fun x => !c.testBit x || c.testBit (gl g x)

theorem bad_perm (hgrp : grpOK = true) {c : ℕ} {FL G : List ℕ} (hst : stabOK c G = true) (hcl : T2M.flClosed FL = true)
    {g : ℕ} (hgG : g ∈ G) {A B : ℕ → Fin 9 → K} {u : Fin 9 → K} (h : Bad c FL A B u) :
    ∃ hg : g < 384, Bad c FL (fun x => A (Tr.pn (permOf hgrp hg) x)) (fun x => B (Tr.pn (permOf hgrp hg) x)) u := by
  unfold stabOK at hst
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.mem_range, Bool.or_eq_true,
    Bool.not_eq_true'] at hst
  obtain ⟨hc, hG⟩ := hst
  obtain ⟨hg, hgx⟩ := hG g hgG
  obtain ⟨hdiag, hmask, hu, v, huv, c', hc', hv⟩ := h
  refine ⟨hg, Tr.diag_perm _ A B hdiag, Tr.mask_perm _ (orth_perm hgrp hg) A B hmask, ?_, v, huv, T2M.pre g c',
    T2M.pre_mem hcl hg hc', ?_⟩
  · intro x hx
    have hx104 : x < 104 := by
      by_contra hcn
      rw [Facts.testBit_big hc (by omega)] at hx; exact absurd hx (by simp)
    show A (Tr.pn _ x) ⬝ᵥ u = 0
    rw [pn_permOf hgrp hg hx104]
    exact hu _ ((hgx x hx104).resolve_left (by rw [hx]; simp))
  · intro x hx
    obtain ⟨hx104, hcx⟩ := T2M.pre_bit hx
    show A (Tr.pn _ x) ⬝ᵥ v = 0
    rw [pn_permOf hgrp hg hx104]
    exact hv _ hcx

/-! ## Exclusion witnesses -/

/-- witness `w = (τ, i, g, kind)` that `τ` is not a support, in item `j = (a, b)`: kind 0: `τ = g(σ_i)` with item `i`
plain; kind ≠ 0: item `i` joint with `{g σ_i, g ctx_i} = {a, τ}` or `{b, τ}` (`b ≠ 0`) -/
def wOK (HP : List (ℕ × ℕ)) (G : List ℕ) (j a b τ : ℕ) (w : ℕ × ℕ × ℕ × ℕ) : Bool :=
  w.1 == τ && decide (w.2.1 < j) && G.contains w.2.2.1 &&
    (if w.2.2.2 = 0 then (HP.getD w.2.1 (0, 0)).2 == 0 && imgM w.2.2.1 (HP.getD w.2.1 (0, 0)).1 == τ
     else (HP.getD w.2.1 (0, 0)).2 != 0 &&
      ((imgM w.2.2.1 (HP.getD w.2.1 (0, 0)).1 == a && imgM w.2.2.1 (HP.getD w.2.1 (0, 0)).2 == τ) ||
       (imgM w.2.2.1 (HP.getD w.2.1 (0, 0)).1 == τ && imgM w.2.2.1 (HP.getD w.2.1 (0, 0)).2 == a) ||
       (b != 0 && ((imgM w.2.2.1 (HP.getD w.2.1 (0, 0)).1 == b && imgM w.2.2.1 (HP.getD w.2.1 (0, 0)).2 == τ) ||
         (imgM w.2.2.1 (HP.getD w.2.1 (0, 0)).1 == τ && imgM w.2.2.1 (HP.getD w.2.1 (0, 0)).2 == b)))))

/-- `τ` is excluded in item `(a, b)`: zero, D2 with `a` or `b`, or a witness -/
def exclB (HP : List (ℕ × ℕ)) (G : List ℕ) (j a b : ℕ) (EW : List (ℕ × ℕ × ℕ × ℕ)) (τ : ℕ) : Bool :=
  τ == 0 || (bitsL τ != bitsL a && orthM (a ||| τ)) || (b != 0 && bitsL τ != bitsL b && orthM (b ||| τ)) ||
    EW.any (wOK HP G j a b τ)

/-- the invariant of item `i` -/
def PI (c : ℕ) (FL : List ℕ) (HP : List (ℕ × ℕ)) (i : ℕ) : Prop :=
  ∀ (A B : ℕ → Fin 9 → K) (u : Fin 9 → K), Bad c FL A B u → ¬ Hyp B u (HP.getD i (0, 0))

theorem excl_sound (hgrp : grpOK = true) {c : ℕ} {FL G : List ℕ} (hst : stabOK c G = true)
    (hcl : T2M.flClosed FL = true) {HP : List (ℕ × ℕ)} {j : ℕ} (hP : ∀ i < j, PI (K := K) c FL HP i)
    {A B : ℕ → Fin 9 → K} {u : Fin 9 → K} (hbad : Bad c FL A B u) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (hu0 : u ≠ 0) {a b : ℕ}
    (ha : mT B u a) (hb : b = 0 ∨ mT B u b) {EW : List (ℕ × ℕ × ℕ × ℕ)} {τ : ℕ}
    (h : exclB HP G j a b EW τ = true) : ¬ mT B u τ := by
  intro hτ
  unfold exclB at h
  simp only [Bool.or_eq_true, beq_iff_eq, Bool.and_eq_true, bne_iff_ne, ne_eq, List.any_eq_true] at h
  rcases h with ((h | ⟨h1, h2⟩) | ⟨⟨h0, h1⟩, h2⟩) | ⟨w, -, hw⟩
  · subst h; exact hu0 (mT_zero hτ)
  · exact mT_D2 A B hdiag hmask ha hτ (Ne.symm h1) h2
  · exact mT_D2 A B hdiag hmask (hb.resolve_left h0) hτ (Ne.symm h1) h2
  · unfold wOK at hw
    simp only [Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq, List.contains_iff_mem] at hw
    obtain ⟨⟨⟨hw1, hwi⟩, hwG⟩, hw⟩ := hw
    obtain ⟨hg, hbad'⟩ := bad_perm hgrp hst hcl (List.mem_of_elem_eq_true hwG) hbad
    refine hP _ hwi _ _ u hbad' ?_
    set p := HP.getD w.2.1 (0, 0)
    set g := w.2.2.1
    split_ifs at hw with hk
    · simp only [Bool.and_eq_true, beq_iff_eq] at hw
      exact ⟨mT_img hgrp hg (hw.2 ▸ hτ), Or.inl hw.1⟩
    · simp only [Bool.and_eq_true, beq_iff_eq, bne_iff_ne, ne_eq, Bool.or_eq_true] at hw
      obtain ⟨hp2, hw⟩ := hw
      have hb' : b ≠ 0 → mT B u b := fun hb0 => hb.resolve_left hb0
      have key : mT B u (imgM g p.1) ∧ mT B u (imgM g p.2) := by
        rcases hw with ((⟨e1, e2⟩ | ⟨e1, e2⟩) | ⟨hb0, ⟨e1, e2⟩ | ⟨e1, e2⟩⟩)
        · exact ⟨e1 ▸ ha, e2 ▸ hτ⟩
        · exact ⟨e1 ▸ hτ, e2 ▸ ha⟩
        · exact ⟨e1 ▸ hb' hb0, e2 ▸ hτ⟩
        · exact ⟨e1 ▸ hτ, e2 ▸ hb' hb0⟩
      exact ⟨mT_img hgrp hg key.1, Or.inr (mT_img hgrp hg key.2)⟩

/-! ## Items -/

/-- one item: a branch record `b` (support `b.σ`), the joint support `ctx` (0: none), exclusion witnesses -/
structure It where
  b : Br
  ctx : ℕ
  EW : List (ℕ × ℕ × ℕ × ℕ)

/-- extra frames valid: every possible support excluded -/
def xfOKS (XF : List (List ℕ)) (m : ℕ) (ex : ℕ → Bool) : Bool :=
  XF.all fun E => frameOK E && (subM E m).all ex

/-- ZKILL closing of an item: `{s}` would be a support (`zkill`), and it is excluded -/
def zkOKS (b : Br) (ex : ℕ → Bool) (zP : ℕ) : Bool :=
  decide (b.s < 104) && decide (b.X.length = 8) && decide (b.Y.length = 8) &&
  b.X.all (fun x => decide (x < 104) && b.d.m.testBit x && zP.testBit x && orthB x b.s) &&
  b.Y.all (fun y => decide (y < 104) && zP.testBit y) &&
  b.dd != 0 && decide (dotM b.X b.Y * jM b.J = b.dd • (1 : Matrix (Fin 8) (Fin 8) ℤ)) && ex (2 ^ b.s)

/-- **the check of item `j`** (`m0 = c`, target `zm`) -/
def It.ok (it : It) (m0 zm : ℕ) (HP : List (ℕ × ℕ)) (G : List ℕ) (j : ℕ) : Bool :=
  it.b.d.okX it.b.XF && decide (it.b.d.m < 2 ^ 104) &&
  (List.range 104).all (fun x => !it.b.d.m.testBit x || m0.testBit x || (bitsL it.b.σ).all (fun s => orthB x s) ||
    (it.ctx != 0 && (bitsL it.ctx).all (fun s => orthB x s))) &&
  xfOKS it.b.XF it.b.d.m (exclB HP G j it.b.σ it.ctx it.EW) && pinsOK it.b.d it.b.f it.b.PL &&
  (if it.b.s = 104 then subset104 zm (pinZ it.b.d.zm it.b.PL)
   else zkOKS it.b (exclB HP G j it.b.σ it.ctx it.EW) (pinZ it.b.d.zm it.b.PL))

/-- **one item**: under its hypothesis and the exclusions, Gram on the target -/
theorem it_sound (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (u : Fin 9 → K) (hu0 : u ≠ 0) (m0 zm : ℕ)
    (hu : ∀ x, m0.testBit x = true → A x ⬝ᵥ u = 0) (it : It) (HP : List (ℕ × ℕ)) (G : List ℕ) (j : ℕ)
    (h : it.ok m0 zm HP G j = true) (hσ : mT B u it.b.σ) (hc : it.ctx = 0 ∨ mT B u it.ctx)
    (hex : ∀ τ, exclB HP G j it.b.σ it.ctx it.EW τ = true → ¬ mT B u τ) :
    ∃ g : ℕ → K, (∀ x, g x ≠ 0) ∧
      ∀ x < 104, ∀ y < 104, zm.testBit x = true → zm.testBit y = true → GramP A B g x y := by
  unfold It.ok at h
  simp only [Bool.and_eq_true] at h
  obtain ⟨⟨⟨⟨⟨hd, hmlt⟩, hdead⟩, hxf⟩, hpins⟩, hend⟩ := h
  have hmlt' := of_decide_eq_true hmlt
  have hu' : ∀ x, it.b.d.m.testBit x = true → A x ⬝ᵥ u = 0 := by
    intro x hx
    by_cases hx104 : x < 104
    · have h1 := List.all_eq_true.mp hdead x (List.mem_range.mpr hx104)
      simp only [hx, Bool.not_true, Bool.false_or, Bool.or_eq_true, Bool.and_eq_true, bne_iff_ne, ne_eq] at h1
      rcases h1 with (h1 | h1) | ⟨h0, h1⟩
      · exact hu x h1
      · refine mT_dead A B hmask hσ hx104 fun s hs => ?_
        have h2 := List.all_eq_true.mp h1 s (mem_bitsL.mpr hs)
        rwa [orthB_eq hx104 (mem_msk.mp hs).1] at h2
      · refine mT_dead A B hmask (hc.resolve_left h0) hx104 fun s hs => ?_
        have h2 := List.all_eq_true.mp h1 s (mem_bitsL.mpr hs)
        rwa [orthB_eq hx104 (mem_msk.mp hs).1] at h2
    · rw [testBit_big hmlt' hx104] at hx
      exact absurd hx (by simp)
  have hX : ∀ F ∈ it.b.XF, frameOK F = true → ExpOK A B it.b.d.m F := by
    intro F hF hFo
    have h1 := List.all_eq_true.mp hxf F hF
    simp only [Bool.and_eq_true] at h1
    exact expOK_of_nosupp A B hdiag hmask u it.b.d.m hu' F hFo fun τ hτ => hex τ (List.all_eq_true.mp h1.2 τ hτ)
  obtain ⟨g0, hg0, hG0⟩ := it.b.d.soundX it.b.XF hd A B hdiag hmask u hu0 hu' hX
  obtain ⟨g, hg, hG⟩ := pins_sound it.b.d it.b.f it.b.PL hpins A B hdiag hmask u hu0 hu' g0 hg0 hG0
  by_cases hs : it.b.s = 104
  · rw [if_pos hs] at hend
    exact ⟨g, hg, fun x hx y hy hzx hzy =>
      hG x hx y hy (subset104_sound hend hx hzx) (subset104_sound hend hy hzy)⟩
  · rw [if_neg hs] at hend
    exfalso
    unfold zkOKS at hend
    simp only [Bool.and_eq_true, decide_eq_true_eq, bne_iff_ne] at hend
    obtain ⟨⟨⟨⟨⟨⟨⟨⟨hs104, hXl⟩, hYl⟩, hXc⟩, hYc⟩, hdd⟩, hDJ⟩, hlast⟩ := hend
    have hXi : ∀ i : Fin 8, it.b.X.getD i 0 < 104 ∧ it.b.d.m.testBit (it.b.X.getD i 0) = true ∧
        (pinZ it.b.d.zm it.b.PL).testBit (it.b.X.getD i 0) = true ∧ orthB (it.b.X.getD i 0) it.b.s = true := by
      intro i
      have h1 := List.all_eq_true.mp hXc _ (getD_mem8 hXl i)
      simp only [Bool.and_eq_true, decide_eq_true_eq] at h1
      exact ⟨h1.1.1.1, h1.1.1.2, h1.1.2, h1.2⟩
    have hYi : ∀ k : Fin 8, it.b.Y.getD k 0 < 104 ∧ (pinZ it.b.d.zm it.b.PL).testBit (it.b.Y.getD k 0) = true := by
      intro k
      have h1 := List.all_eq_true.mp hYc _ (getD_mem8 hYl k)
      simp only [Bool.and_eq_true, decide_eq_true_eq] at h1
      exact h1
    have hmTs := zkill A B hdiag hmask hu0 g hg it.b.s hs104 (fun i => it.b.X.getD i 0) (fun k => it.b.Y.getD k 0)
      (fun i => (hXi i).1) (fun i => hu' _ (hXi i).2.1)
      (fun i => by have h0 := (hXi i).2.2.2; rw [orthB_eq (hXi i).1 hs104] at h0; exact h0)
      (fun i k => hG _ (hXi i).1 _ (hYi k).1 (hXi i).2.2.1 (hYi k).2) (dotM it.b.X it.b.Y)
      (det_of_adj _ _ _ hdd hDJ) (fun i k => rfl)
    exact hex _ hlast hmTs

/-! ## One representative -/

/-- the T2 record of one frameless representative, by orbits -/
structure T2SR where
  zm : ℕ
  BIG : List (List ℕ)
  d0 : T1D
  f0 : ℕ
  PL0 : List (ℕ × ℕ × RCert)
  EW0 : List (ℕ × ℕ × ℕ × ℕ)
  G : List ℕ
  its : List It
  Y : List ℕ
  P : List (ℕ × List ℕ × List (List ℤ) × ℤ)

def HPof (its : List It) : List (ℕ × ℕ) := its.map fun it => (it.b.σ, it.ctx)

/-- the items in order, item `j` with index `j` -/
def itsOK (m0 zm : ℕ) (HP : List (ℕ × ℕ)) (G : List ℕ) : ℕ → List It → Bool
  | _, [] => true
  | j, it :: r => it.ok m0 zm HP G j && itsOK m0 zm HP G (j + 1) r

/-- the pair certificates for the Gram set `zm` -/
def pairsOK (zm c : ℕ) (FL : List ℕ) (Y : List ℕ) (P : List (ℕ × List ℕ × List (List ℤ) × ℤ)) : Bool :=
  FL.all fun c' => P.any fun p => p.1 == c' && pcOK2 zm c c' Y p.2.1 p.2.2.1 p.2.2.2

/-- **the check of a T2 record by orbits** for the representative `c` and the partner list `FL` -/
def T2SR.ok (r : T2SR) (c : ℕ) (FL : List ℕ) : Bool :=
  r.d0.m == c && stabOK c r.G && T2M.flClosed FL && r.d0.okX r.BIG && pinsOK r.d0 r.f0 r.PL0 &&
  subset104 r.zm (pinZ r.d0.zm r.PL0) &&
  r.BIG.all (fun E => frameOK E && (subM E c).all fun τ =>
    τ == 0 || r.EW0.any fun w => w.2.2.2 == 0 && wOK (HPof r.its) r.G r.its.length 0 0 τ w) &&
  itsOK c r.zm (HPof r.its) r.G 0 r.its && pairsOK r.zm c FL r.Y r.P

/-- Gram on the target and the pair certificates contradict `Bad` -/
theorem gram_false {c zm : ℕ} {FL Y : List ℕ} {P : List (ℕ × List ℕ × List (List ℤ) × ℤ)} (hp : pairsOK zm c FL Y P = true)
    {A B : ℕ → Fin 9 → K} {u : Fin 9 → K} (hbad : Bad c FL A B u) (g : ℕ → K) (hg : ∀ x, g x ≠ 0)
    (hG : ∀ x < 104, ∀ y < 104, zm.testBit x = true → zm.testBit y = true → GramP A B g x y) : False := by
  obtain ⟨hdiag, -, hu, v, huv, c', hc', hv⟩ := hbad
  unfold pairsOK at hp
  simp only [List.all_eq_true, List.any_eq_true, Bool.and_eq_true] at hp
  obtain ⟨p, -, -, hpp⟩ := hp c' hc'
  exact pair_false A B hdiag u v huv g hg zm c c' hG hu hv Y _ _ _ hpp

theorem u_ne {c : ℕ} {FL : List ℕ} {A B : ℕ → Fin 9 → K} {u : Fin 9 → K} (hbad : Bad c FL A B u) : u ≠ 0 := by
  obtain ⟨-, -, -, v, huv, -⟩ := hbad
  intro h0
  have := huv.ne_zero 0
  simp [h0] at this

theorem its_sound (hgrp : grpOK = true) {c zm : ℕ} {FL G : List ℕ} (hst : stabOK c G = true)
    (hcl : T2M.flClosed FL = true) {Y : List ℕ} {P : List (ℕ × List ℕ × List (List ℤ) × ℤ)}
    (hp : pairsOK zm c FL Y P = true) (HP : List (ℕ × ℕ)) :
    ∀ (l : List It) (j : ℕ), itsOK c zm HP G j l = true → HP.drop j = HPof l →
      (∀ i < j, PI (K := K) c FL HP i) → ∀ i < j + l.length, PI (K := K) c FL HP i
  | [], j, _, _, hP => fun i hi => hP i (by simpa using hi)
  | it :: r, j, h, hd, hP => by
    unfold itsOK at h
    simp only [Bool.and_eq_true] at h
    have hj : HP.getD j (0, 0) = (it.b.σ, it.ctx) := by
      have e := congrArg (fun l => l.getD 0 (0, 0)) hd
      simp only [HPof, List.map_cons, List.getD_cons_zero] at e
      rw [← e, List.getD_eq_getElem?_getD, List.getD_eq_getElem?_getD, List.getElem?_drop, Nat.add_zero]
    have hPj : PI (K := K) c FL HP j := by
      intro A B u hbad hhyp
      rw [hj] at hhyp
      obtain ⟨hσ, hctx⟩ := hhyp
      have hb := hbad
      obtain ⟨hdiag, hmask, hu, -⟩ := hb
      have hu0 := u_ne hbad
      obtain ⟨g, hg, hG⟩ := it_sound A B hdiag hmask u hu0 c zm hu it HP G j h.1 hσ hctx
        fun τ hτ => excl_sound hgrp hst hcl hP hbad hdiag hmask hu0 hσ hctx hτ
      exact gram_false hp hbad g hg hG
    have hrest := its_sound hgrp hst hcl hp HP r (j + 1) h.2
      (by rw [← List.drop_drop, hd]; simp [HPof])
      (fun i hi => by
        rcases Nat.lt_succ_iff_lt_or_eq.mp hi with h1 | h1
        · exact hP i h1
        · rw [h1]; exact hPj)
    intro i hi
    exact hrest i (by simp at hi ⊢; omega)

/-- **T2 for one frameless representative, by orbits.** -/
theorem T2SR.sound (hgrp : grpOK = true) (r : T2SR) (c : ℕ) (FL : List ℕ) (h : r.ok c FL = true)
    (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hbad : Bad c FL A B u) : False := by
  unfold T2SR.ok at h
  simp only [Bool.and_eq_true, beq_iff_eq] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨hm, hst⟩, hcl⟩, hd0⟩, hpins⟩, hzm⟩, hbig⟩, hits⟩, hp⟩ := h
  have hall := its_sound hgrp hst hcl hp (HPof r.its) r.its 0 hits (by simp) (fun i hi => absurd hi (by omega))
  obtain ⟨hdiag, hmask, hu, -⟩ := hbad
  have hu0 := u_ne hbad
  have hu' : ∀ x, r.d0.m.testBit x = true → A x ⬝ᵥ u = 0 := by rw [hm]; exact hu
  have hX : ∀ F ∈ r.BIG, frameOK F = true → ExpOK A B r.d0.m F := by
    intro F hF hFo
    rw [hm]
    refine expOK_of_nosupp A B hdiag hmask u c hu F hFo fun τ hτ hmT => ?_
    have h1 := List.all_eq_true.mp hbig F hF
    simp only [Bool.and_eq_true] at h1
    have h2 := List.all_eq_true.mp h1.2 τ hτ
    simp only [Bool.or_eq_true, beq_iff_eq, List.any_eq_true, Bool.and_eq_true] at h2
    rcases h2 with h2 | ⟨w, -, hk, hw⟩
    · subst h2; exact hu0 (mT_zero hmT)
    · unfold wOK at hw
      simp only [Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq, List.contains_iff_mem] at hw
      obtain ⟨⟨⟨hw1, hwi⟩, hwG⟩, hw⟩ := hw
      rw [if_pos hk] at hw
      simp only [Bool.and_eq_true, beq_iff_eq] at hw
      obtain ⟨hg, hbad'⟩ := bad_perm hgrp hst hcl (List.mem_of_elem_eq_true hwG) hbad
      exact hall _ (by simpa using hwi) _ _ u hbad' ⟨mT_img hgrp hg (hw.2 ▸ hmT), Or.inl hw.1⟩
  obtain ⟨g0, hg0, hG0⟩ := r.d0.soundX r.BIG hd0 A B hdiag hmask u hu0 hu' hX
  obtain ⟨g, hg, hG⟩ := pins_sound r.d0 r.f0 r.PL0 hpins A B hdiag hmask u hu0 hu' g0 hg0 hG0
  exact gram_false hp hbad g hg fun x hx y hy hzx hzy => hG x hx y hy (subset104_sound hzm hx hzx) (subset104_sound hzm hy hzy)

/-! ## All pairs -/

/-- **T2 for all frameless pairs, by orbits** (table hypothesis: existence of the data). -/
theorem t2Pair_of_exS (hgrp : grpOK = true)
    (hex : ∃ R : List ℕ, ∃ W : List (ℕ × ℕ × ℕ), T2M.t2wOK R flData W = true ∧ T2M.flClosed flData = true ∧
      ∀ k < R.length, ∃ r : T2SR, r.ok (R.getD k 0) flData = true) :
    Main.T2Pair K flData := by
  obtain ⟨R, W, hw, hcl, hT⟩ := hex
  intro A B hdiag hmask Al Bl _ _ u v huv c c' hc hc' hu hv
  have hc : c ∈ flData := by simpa using hc
  have hc' : c' ∈ flData := by simpa using hc'
  obtain ⟨e, -, he⟩ := List.any_eq_true.mp (List.all_eq_true.mp hw c hc)
  rw [Bool.and_eq_true] at he
  replace he := he.2
  unfold T2M.imgOK2 at he
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.mem_range, Bool.or_eq_true,
    Bool.not_eq_true'] at he
  obtain ⟨⟨⟨hg, hk⟩, hRlt⟩, himg⟩ := he
  set g := e.2.1
  set k := e.2.2
  set π := permOf hgrp hg
  obtain ⟨r, hr⟩ := hT k hk
  refine T2SR.sound hgrp r (R.getD k 0) flData hr (fun x => A (Tr.pn π x)) (fun x => B (Tr.pn π x)) u
    ⟨Tr.diag_perm π A B hdiag, Tr.mask_perm π (orth_perm hgrp hg) A B hmask, ?_, v, huv, T2M.pre g c',
      T2M.pre_mem hcl hg hc', ?_⟩
  · intro x hx
    have hx104 : x < 104 := by
      by_contra hcn
      rw [Facts.testBit_big hRlt (by omega)] at hx; exact absurd hx (by simp)
    have hcx := (himg x hx104).resolve_left (by rw [hx]; simp)
    show A (Tr.pn π x) ⬝ᵥ u = 0
    rw [pn_permOf hgrp hg hx104]
    exact hu _ hcx
  · intro x hx
    obtain ⟨hx104, hcx⟩ := T2M.pre_bit hx
    show A (Tr.pn π x) ⬝ᵥ v = 0
    rw [pn_permOf hgrp hg hx104]
    exact hv _ hcx

end RankNine.T2S
