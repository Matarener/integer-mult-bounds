import RankNine.FactsC3

set_option linter.unusedSectionVars false

/-!
# FC3 by hand (NOTE §13.27, restated with weights mod 4)

Replaces the `512³` loop `fc3OK`.  For a label `n < 512` (a vector of `F₂⁹`) let `wt n` be its weight.  The single
dead set `S(n) = {t : lab t · n = 1}` (`sm n`) contains a P104 frame unless `wt n ≡ 2, 3 (mod 4)` (this is
NOTE §13.26 step 2: the frameless `O(z)` are the 136 values of `Φ`, and `Φ` lies in the 240 labels of weight `2, 3`
mod 4).  The frame is given by a **witness table** `FW` (`fwOK`, a table hypothesis: `#eval` + Python
`fc3hand/check.py`).

**Hand lemma** (`no_plane3`): no 3-dim subspace `⟨a, b, c⟩` has all 7 non-zero points of weight `2, 3 (mod 4)`.
With `wt (x + y) + 2 wt (x ∧ y) = wt x + wt y` (`wt_xor`) and `(x + y) ∧ z = (x ∧ z) + (y ∧ z)` (`land_xor`):
* all points even (weight `≡ 2`): `wt (x ∧ y)` is odd for any two of them, but
  `wt ((a + b) ∧ c) ≡ wt (a ∧ c) + wt (b ∧ c) ≡ 0` (`plane_even`);
* otherwise exactly four points are odd (weight `≡ 3`), an affine plane `p, q, r, p + q + r` over three even points
  `p + q, p + r, q + r` (weight `≡ 2`): then `wt (p ∧ r)`, `wt (q ∧ r)` are even, so
  `wt (p + q + r) ≡ 2 + 3 - 2 · 0 ≡ 1 (mod 4)`, not `3` (`plane_odd`).

So one of the 7 points `x` has a frame inside `S(x) ⊆ C(x, y)` for every `y`: `framed_of_three_h`, the statement of
`framed_of_three` with `fwOK` in place of `fc3OK`.
-/

namespace RankNine.Facts

open Matrix BForm BForm.E8

/-! ## Weights -/

def wl (l : List ℕ) (n : ℕ) : ℕ := (l.map fun k => (n.testBit k).toNat).sum

/-- the weight of a label (bits `0..8`) -/
def wt (n : ℕ) : ℕ := wl (List.range 9) n

theorem wl_xor (l : List ℕ) (a b : ℕ) : wl l (a ^^^ b) + 2 * wl l (a &&& b) = wl l a + wl l b := by
  induction l with
  | nil => simp [wl]
  | cons k l ih =>
    have hk : ((a ^^^ b).testBit k).toNat + 2 * ((a &&& b).testBit k).toNat =
        (a.testBit k).toNat + (b.testBit k).toNat := by
      rw [Nat.testBit_xor, Nat.testBit_land]
      cases a.testBit k <;> cases b.testBit k <;> rfl
    simp only [wl, List.map_cons, List.sum_cons] at ih ⊢
    omega

theorem wt_xor (a b : ℕ) : wt (a ^^^ b) + 2 * wt (a &&& b) = wt a + wt b := wl_xor _ a b

theorem land_xor (x y z : ℕ) : (x ^^^ y) &&& z = (x &&& z) ^^^ (y &&& z) := by
  apply Nat.eq_of_testBit_eq
  intro i
  simp only [Nat.testBit_land, Nat.testBit_xor]
  cases x.testBit i <;> cases y.testBit i <;> cases z.testBit i <;> rfl

/-- weight `2` or `3` mod 4 (the 240 labels containing the 136 frameless `Φ`) -/
def Ph (n : ℕ) : Prop := wt n % 4 = 2 ∨ wt n % 4 = 3

/-! ## The hand lemma -/

theorem plane_even {x y z : ℕ} (hx : wt x % 4 = 2) (hy : wt y % 4 = 2) (hz : wt z % 4 = 2)
    (hxy : wt (x ^^^ y) % 4 = 2) (hxz : wt (x ^^^ z) % 4 = 2) (hyz : wt (y ^^^ z) % 4 = 2)
    (hxyz : wt ((x ^^^ y) ^^^ z) % 4 = 2) : False := by
  have e1 := wt_xor x z
  have e2 := wt_xor y z
  have e3 := wt_xor (x ^^^ y) z
  have e4 := wt_xor (x &&& z) (y &&& z)
  rw [← land_xor x y z] at e4
  omega

theorem plane_odd {o p q r s t u v : ℕ} (ho : o % 2 = 1) (hs : p ^^^ q = s) (ht : p ^^^ r = t) (hu : q ^^^ r = u)
    (hv : s ^^^ r = v) (hp : wt p % 4 = o) (hq : wt q % 4 = o) (hr : wt r % 4 = o) (hs2 : wt s % 4 = 2)
    (ht2 : wt t % 4 = 2) (hu2 : wt u % 4 = 2) (hv3 : wt v % 4 = o) : False := by
  subst hs ht hu hv
  have e2 := wt_xor p r
  have e3 := wt_xor q r
  have e4 := wt_xor (p ^^^ q) r
  have e5 := wt_xor (p &&& r) (q &&& r)
  rw [← land_xor p q r] at e5
  omega

/-- labels of weight `2` or `o` mod 4 -/
def PhO (o n : ℕ) : Prop := wt n % 4 = 2 ∨ wt n % 4 = o

set_option maxHeartbeats 800000 in
/-- **No 3-space of labels of weight `2, o (mod 4)`**, `o = 1` or `3` (NOTE §13.27, CENSUS-PLAN §6). -/
theorem no_plane3o (o : ℕ) (ho : o = 1 ∨ o = 3) (a b c : ℕ) (ha : PhO o a) (hb : PhO o b) (hc : PhO o c)
    (hab : PhO o (a ^^^ b)) (hac : PhO o (a ^^^ c)) (hbc : PhO o (b ^^^ c)) (habc : PhO o ((a ^^^ b) ^^^ c)) :
    False := by
  -- write `o = 3 - 2 e`; then `PhO o w` is the single linear fact `(wt w + e) % 4 ≥ 2` (no case splits for `omega`)
  obtain ⟨e, he, rfl⟩ : ∃ e, e ≤ 1 ∧ o = 3 - 2 * e := by
    rcases ho with rfl | rfl
    exacts [⟨1, le_rfl, rfl⟩, ⟨0, Nat.zero_le _, rfl⟩]
  have L : ∀ w, PhO (3 - 2 * e) w → (wt w + e) % 4 ≥ 2 := by intro w h; unfold PhO at h; omega
  replace ha := L _ ha
  replace hb := L _ hb
  replace hc := L _ hc
  replace hab := L _ hab
  replace hac := L _ hac
  replace hbc := L _ hbc
  replace habc := L _ habc
  clear L ho
  have ho2 : (3 - 2 * e) % 2 = 1 := by omega
  have pab := wt_xor a b
  have pac := wt_xor a c
  have pbc := wt_xor b c
  have pabc := wt_xor (a ^^^ b) c
  have i1 : a ^^^ (a ^^^ b) = b := Nat.eq_of_testBit_eq fun i => by
    simp only [Nat.testBit_xor]; cases a.testBit i <;> cases b.testBit i <;> rfl
  have i2 : a ^^^ (a ^^^ c) = c := Nat.eq_of_testBit_eq fun i => by
    simp only [Nat.testBit_xor]; cases a.testBit i <;> cases c.testBit i <;> rfl
  have i3 : b ^^^ (b ^^^ c) = c := Nat.eq_of_testBit_eq fun i => by
    simp only [Nat.testBit_xor]; cases b.testBit i <;> cases c.testBit i <;> rfl
  have j1 : b ^^^ (a ^^^ b) = a := Nat.eq_of_testBit_eq fun i => by
    simp only [Nat.testBit_xor]; cases a.testBit i <;> cases b.testBit i <;> rfl
  have j2 : c ^^^ (a ^^^ c) = a := Nat.eq_of_testBit_eq fun i => by
    simp only [Nat.testBit_xor]; cases a.testBit i <;> cases c.testBit i <;> rfl
  have j3 : c ^^^ (b ^^^ c) = b := Nat.eq_of_testBit_eq fun i => by
    simp only [Nat.testBit_xor]; cases b.testBit i <;> cases c.testBit i <;> rfl
  have k1 : (a ^^^ b) ^^^ (a ^^^ c) = b ^^^ c := Nat.eq_of_testBit_eq fun i => by
    simp only [Nat.testBit_xor]; cases a.testBit i <;> cases b.testBit i <;> cases c.testBit i <;> rfl
  have k2 : (a ^^^ b) ^^^ (b ^^^ c) = a ^^^ c := Nat.eq_of_testBit_eq fun i => by
    simp only [Nat.testBit_xor]; cases a.testBit i <;> cases b.testBit i <;> cases c.testBit i <;> rfl
  have k3 : (a ^^^ c) ^^^ (b ^^^ c) = a ^^^ b := Nat.eq_of_testBit_eq fun i => by
    simp only [Nat.testBit_xor]; cases a.testBit i <;> cases b.testBit i <;> cases c.testBit i <;> rfl
  have l1 : b ^^^ (a ^^^ c) = (a ^^^ b) ^^^ c := Nat.eq_of_testBit_eq fun i => by
    simp only [Nat.testBit_xor]; cases a.testBit i <;> cases b.testBit i <;> cases c.testBit i <;> rfl
  have l2 : a ^^^ (b ^^^ c) = (a ^^^ b) ^^^ c := Nat.eq_of_testBit_eq fun i => by
    simp only [Nat.testBit_xor]; cases a.testBit i <;> cases b.testBit i <;> cases c.testBit i <;> rfl
  have l3 : c ^^^ (a ^^^ b) = (a ^^^ b) ^^^ c := Nat.eq_of_testBit_eq fun i => by
    simp only [Nat.testBit_xor]; cases a.testBit i <;> cases b.testBit i <;> cases c.testBit i <;> rfl
  have m1 : (a ^^^ c) ^^^ (a ^^^ b) = b ^^^ c := Nat.eq_of_testBit_eq fun i => by
    simp only [Nat.testBit_xor]; cases a.testBit i <;> cases b.testBit i <;> cases c.testBit i <;> rfl
  have m2 : (b ^^^ c) ^^^ (a ^^^ b) = a ^^^ c := Nat.eq_of_testBit_eq fun i => by
    simp only [Nat.testBit_xor]; cases a.testBit i <;> cases b.testBit i <;> cases c.testBit i <;> rfl
  rcases Nat.mod_two_eq_zero_or_one (wt a) with ea | ea <;>
  rcases Nat.mod_two_eq_zero_or_one (wt b) with eb | eb <;>
  rcases Nat.mod_two_eq_zero_or_one (wt c) with ec | ec
  · -- even, even, even
    exact plane_even (x := a) (y := b) (z := c) (by omega) (by omega) (by omega) (by omega) (by omega) (by omega)
      (by omega)
  · -- odd points c, a + c, b + c, a + b + c
    exact plane_odd ho2 (p := c) (q := a ^^^ c) (r := b ^^^ c) j2 j3 k3 l2 (by omega) (by omega) (by omega)
      (by omega) (by omega) (by omega) (by omega)
  · -- odd points b, a + b, b + c, a + b + c
    exact plane_odd ho2 (p := b) (q := a ^^^ b) (r := b ^^^ c) j1 i3 k2 l2 (by omega) (by omega) (by omega)
      (by omega) (by omega) (by omega) (by omega)
  · -- odd points b, c, a + b, a + c
    exact plane_odd ho2 (p := b) (q := c) (r := a ^^^ b) rfl j1 l3 m2 (by omega) (by omega) (by omega)
      (by omega) (by omega) (by omega) (by omega)
  · -- odd points a, a + b, a + c, a + b + c
    exact plane_odd ho2 (p := a) (q := a ^^^ b) (r := a ^^^ c) i1 i2 k1 l1 (by omega) (by omega) (by omega)
      (by omega) (by omega) (by omega) (by omega)
  · -- odd points a, c, a + b, b + c
    exact plane_odd ho2 (p := a) (q := c) (r := a ^^^ b) rfl i1 l3 m1 (by omega) (by omega) (by omega)
      (by omega) (by omega) (by omega) (by omega)
  · -- odd points a, b, a + c, b + c
    exact plane_odd ho2 (p := a) (q := b) (r := a ^^^ c) rfl i2 l1 k1 (by omega) (by omega) (by omega)
      (by omega) (by omega) (by omega) (by omega)
  · -- odd, odd, odd
    exact plane_odd ho2 (p := a) (q := b) (r := c) rfl rfl rfl rfl (by omega) (by omega) (by omega)
      (by omega) (by omega) (by omega) (by omega)

/-- **No 3-space of labels of weight `2, 3 (mod 4)`** (NOTE §13.27). -/
theorem no_plane3 (a b c : ℕ) (ha : Ph a) (hb : Ph b) (hc : Ph c) (hab : Ph (a ^^^ b)) (hac : Ph (a ^^^ c))
    (hbc : Ph (b ^^^ c)) (habc : Ph ((a ^^^ b) ^^^ c)) : False :=
  no_plane3o 3 (Or.inr rfl) a b c ha hb hc hab hac hbc habc

/-! ## The witness table -/

def phB (n : ℕ) : Bool := wt n % 4 == 2 || wt n % 4 == 3

def fwAt (FW : List ℕ) (n : ℕ) : Bool :=
  n == 0 || phB n || (decide (FW.getD n 0 < 759) && frm (FW.getD n 0) &&& sm n == frm (FW.getD n 0))

/-- **table hypothesis FW**: every non-zero label of weight `0, 1 (mod 4)` has a P104 frame inside `S(n)` -/
def fwOK (FW : List ℕ) : Bool := (List.range 512).all (fwAt FW)

theorem hasFr_of_fw {FW : List ℕ} (h : fwOK FW = true) {n : ℕ} (hn : n < 512) (h0 : n ≠ 0) (hp : ¬ Ph n)
    (m : ℕ) : hasFr (sm n ||| m) = true := by
  have e := List.all_eq_true.mp h n (List.mem_range.mpr hn)
  unfold fwAt at e
  simp only [Bool.or_eq_true, Bool.and_eq_true, beq_iff_eq, decide_eq_true_eq] at e
  rcases e with (e | e) | ⟨hf, e⟩
  · exact absurd e h0
  · exfalso; apply hp
    unfold phB at e
    simp only [Bool.or_eq_true, beq_iff_eq] at e
    exact e
  · apply List.any_eq_true.mpr
    refine ⟨FW.getD n 0, List.mem_range.mpr hf, ?_⟩
    show (frm (FW.getD n 0) &&& (sm n ||| m) == frm (FW.getD n 0)) = true
    rw [beq_iff_eq]
    apply Nat.eq_of_testBit_eq
    intro i
    have ei := congrArg (fun x => Nat.testBit x i) e
    simp only [Nat.testBit_land, Nat.testBit_or] at ei ⊢
    revert ei
    cases (frm (FW.getD n 0)).testBit i <;> cases (sm n).testBit i <;> cases m.testBit i <;> decide

theorem x512 {a b : ℕ} (ha : a < 512) (hb : b < 512) : a ^^^ b < 512 := by
  have h9 : (512 : ℕ) = 2 ^ 9 := by norm_num
  rw [h9] at ha hb ⊢
  exact Nat.xor_lt_two_pow ha hb

/-- **FC3 applied, by hand.** Three independent vectors give a framed pair in their span. -/
theorem framed_of_three_h {FW : List ℕ} (hfw : fwOK FW = true) (z1 z2 z3 : V9) (h1 : z1 ≠ 0) (h2 : z2 ≠ 0)
    (h3 : z3 ≠ 0) (h12 : z1 ≠ z2) (h13 : z1 ≠ z3) (h23 : z2 ≠ z3) (h312 : z3 ≠ z1 + z2) :
    ∃ y1 y2 : V9, Good z1 z2 z3 y1 y2 := by
  obtain ⟨a, ha, ea⟩ := exists_lz z1
  obtain ⟨b, hb, eb⟩ := exists_lz z2
  obtain ⟨c, hc, ec⟩ := exists_lz z3
  have zne : ∀ {n : ℕ} {z : V9}, n < 512 → lz n = zl z → z ≠ 0 → n ≠ 0 := by
    intro n z hn e hz h0; subst h0; rw [lz_zero] at e; exact hz (zl_zero e.symm)
  have dne : ∀ {n m : ℕ} {y z : V9}, lz n = zl y → lz m = zl z → y ≠ z → n ≠ m := by
    intro n m y z e1 e2 hyz h0; subst h0; exact hyz (zl_inj (e1.symm.trans e2))
  have xab : lz (a ^^^ b) = zl (z1 + z2) := by rw [lz_xor, ea, eb, zl_add]
  have xac : lz (a ^^^ c) = zl (z1 + z3) := by rw [lz_xor, ea, ec, zl_add]
  have xbc : lz (b ^^^ c) = zl (z2 + z3) := by rw [lz_xor, eb, ec, zl_add]
  have xabc : lz ((a ^^^ b) ^^^ c) = zl (z1 + z2 + z3) := by rw [lz_xor, xab, ec, ← zl_add]
  -- the seven points are non-zero, and each differs from the partner chosen below
  have s0 : ∀ {p q : V9}, p ≠ q → p + q ≠ 0 := fun hpq e => hpq (v9_eq_of_add e)
  have s1 : ∀ {p q : V9}, q ≠ 0 → p + q ≠ p := fun hq e => hq (add_left_cancel (e.trans (add_zero _).symm))
  have n12 : z1 + z2 ≠ 0 := s0 h12
  have n13 : z1 + z3 ≠ 0 := s0 h13
  have n23 : z2 + z3 ≠ 0 := s0 h23
  have n123 : z1 + z2 + z3 ≠ 0 := fun e => h312 (v9_eq_of_add e).symm
  have d123 : z1 + z2 + z3 ≠ z1 := by
    intro e
    apply h23
    apply v9_eq_of_add
    apply add_left_cancel (a := z1)
    rw [add_zero, ← add_assoc]
    exact e
  have pr : ∀ {x y : ℕ} {p q : V9}, lz x = zl p → lz y = zl q → p ≠ 0 → q ≠ 0 → p ≠ q → x < 512 → y < 512 →
      ¬ Ph x → (∀ w : V9, w ⬝ᵥ z1 = 0 → w ⬝ᵥ z2 = 0 → w ⬝ᵥ z3 = 0 → w ⬝ᵥ p = 0 ∧ w ⬝ᵥ q = 0) →
      Good z1 z2 z3 p q := by
    intro x y p q ex ey hp hq hpq hx hy hPh hsp
    apply good_of ex.symm ey.symm hsp
    simp only [gpair, Bool.and_eq_true, decide_eq_true_eq, bne_iff_ne, ne_eq]
    exact ⟨⟨⟨⟨⟨hx, hy⟩, zne hx ex hp⟩, zne hy ey hq⟩, dne ex ey hpq⟩, hasFr_of_fw hfw hx (zne hx ex hp) hPh (sm y)⟩
  have dz : ∀ w : V9, w ⬝ᵥ z1 = 0 → w ⬝ᵥ z2 = 0 → w ⬝ᵥ z3 = 0 →
      w ⬝ᵥ (z1 + z2) = 0 ∧ w ⬝ᵥ (z1 + z3) = 0 ∧ w ⬝ᵥ (z2 + z3) = 0 ∧ w ⬝ᵥ (z1 + z2 + z3) = 0 := by
    intro w p1 p2 p3
    simp [dotProduct_add, p1, p2, p3]
  by_cases pa : Ph a
  swap
  · exact ⟨z1, z2, pr ea eb h1 h2 h12 ha hb pa (fun w p1 p2 _ => ⟨p1, p2⟩)⟩
  by_cases pb : Ph b
  swap
  · exact ⟨z2, z1, pr eb ea h2 h1 (Ne.symm h12) hb ha pb (fun w p1 p2 _ => ⟨p2, p1⟩)⟩
  by_cases pc : Ph c
  swap
  · exact ⟨z3, z1, pr ec ea h3 h1 (Ne.symm h13) hc ha pc (fun w p1 _ p3 => ⟨p3, p1⟩)⟩
  by_cases pab : Ph (a ^^^ b)
  swap
  · exact ⟨z1 + z2, z1, pr xab ea n12 h1 (s1 h2) (x512 ha hb) ha pab
      (fun w p1 p2 p3 => ⟨(dz w p1 p2 p3).1, p1⟩)⟩
  by_cases pac : Ph (a ^^^ c)
  swap
  · exact ⟨z1 + z3, z1, pr xac ea n13 h1 (s1 h3) (x512 ha hc) ha pac
      (fun w p1 p2 p3 => ⟨(dz w p1 p2 p3).2.1, p1⟩)⟩
  by_cases pbc : Ph (b ^^^ c)
  swap
  · exact ⟨z2 + z3, z2, pr xbc eb n23 h2 (s1 h3) (x512 hb hc) hb pbc
      (fun w p1 p2 p3 => ⟨(dz w p1 p2 p3).2.2.1, p2⟩)⟩
  by_cases pabc : Ph ((a ^^^ b) ^^^ c)
  swap
  · exact ⟨z1 + z2 + z3, z1, pr xabc ea n123 h1 d123 (x512 (x512 ha hb) hc) ha pabc
      (fun w p1 p2 p3 => ⟨(dz w p1 p2 p3).2.2.2, p1⟩)⟩
  exact (no_plane3 a b c pa pb pc pab pac pbc pabc).elim

end RankNine.Facts
