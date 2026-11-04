import RankNine.Facts

/-!
# Finite facts FC3 and FLF (codim-3 sides; the frameless list has no frame)

Labels of `F₂⁹` are numbered `n < 512` by `lz n` (bit `k` of `n` = coordinate `k`); `lists9 = map lz (range 512)`.
`sm n` caches the single dead set `S(n) = {t : par t (lz n)}`; `C(a, b) = S(a) ∪ S(b)` (`cmask_eq`).

* `flNoFrame FL`: no listed frameless set contains a frame (so a set with a frame is not in `FL`).
* `fc3OK`: for independent `a, b, c` one of the 7 codim-2 supersets `C(x₁, x₂)` (pairs from `span{a, b, c}`)
  contains a frame (`gpair` carries the non-degeneracy guards).

`framed_of_three`: three independent `z₁, z₂, z₃` killing all live labels give a pair `y₁, y₂` in their span with
a frame inside `C(y₁, y₂)`; `not_FL`: such a set is not in `FL`.
-/

namespace RankNine.Facts

open Matrix BForm BForm.E8

set_option linter.unusedSectionVars false

def lz (n : ℕ) : List ℕ := (List.range 9).map fun k => if n.testBit k then 1 else 0

def smask (l : List ℕ) : ℕ := lmask ((List.range 104).filter fun t => BForm.E8.par t l)

def smT : Array ℕ := ((List.range 512).map fun n => smask (lz n)).toArray

def sm (n : ℕ) : ℕ := smT.getD n 0

theorem sm_eq {n : ℕ} (hn : n < 512) : sm n = smask (lz n) := by
  unfold sm smT
  first
  | simp [Array.getD, hn]
  | simp [hn]

theorem cmask_eq (l1 l2 : List ℕ) : cmask l1 l2 = smask l1 ||| smask l2 := by
  apply Nat.eq_of_testBit_eq
  intro i
  rw [bit_or]
  apply Bool.eq_iff_iff.mpr
  rw [Bool.or_eq_true, cmask, smask, smask, lmask_bit, lmask_bit, lmask_bit]
  simp only [List.mem_filter, List.mem_range, Bool.or_eq_true]
  tauto

theorem lists9_eq : lists9 = (List.range 512).map lz := by decide +kernel

theorem lz_zero : lz 0 = zero9 := by decide

theorem lz_xor (a b : ℕ) : lz (a ^^^ b) = xorL (lz a) (lz b) := by
  apply List.ext_getElem (by simp [lz, xorL])
  intro k h1 h2
  simp only [lz, List.length_map, List.length_range] at h1
  simp only [lz, xorL, List.getElem_map, List.getElem_range, List.getD_eq_getElem?_getD, List.getElem?_map,
    List.getElem?_range h1, Option.map_some, Option.getD_some, Nat.testBit_xor]
  cases a.testBit k <;> cases b.testBit k <;> rfl

theorem exists_lz (z : V9) : ∃ n < 512, lz n = zl z := by
  have := zl_mem z
  rw [lists9_eq, List.mem_map] at this
  obtain ⟨n, hn, e⟩ := this
  exact ⟨n, List.mem_range.mp hn, e⟩

theorem lz_inj {x y : ℕ} (hx : x < 512) (hy : y < 512) (h : lz x = lz y) : x = y := by
  apply Nat.eq_of_testBit_eq
  intro k
  by_cases hk : k < 9
  · have := congrArg (fun l => l.getD k 0) h
    simp only [lz, List.getD_eq_getElem?_getD, List.getElem?_map, List.getElem?_range hk, Option.map_some,
      Option.getD_some] at this
    cases hxk : x.testBit k <;> cases hyk : y.testBit k <;> simp_all
  · have h9 : ∀ n < 512, n.testBit k = false := fun n hn =>
      Nat.testBit_eq_false_of_lt (lt_of_lt_of_le hn (by
        calc 512 = 2 ^ 9 := by norm_num
          _ ≤ 2 ^ k := Nat.pow_le_pow_right (by norm_num) (by omega)))
    rw [h9 x hx, h9 y hy]

def frm (f : ℕ) : ℕ := lmask (frameData.getD f [])

def hasFr (c : ℕ) : Bool := (List.range 759).any fun f => frm f &&& c == frm f

/-- **finite fact FLF** -/
def flNoFrame (FL : List ℕ) : Bool := FL.all fun c => (List.range 759).all fun f => !(frm f &&& c == frm f)

theorem not_FL {FL : List ℕ} (hF : flNoFrame FL = true) {c : ℕ} (hc : hasFr c = true) : FL.contains c = false := by
  by_contra hcon
  simp only [Bool.not_eq_false, List.contains_iff_mem] at hcon
  have h1 := List.all_eq_true.mp hF c hcon
  obtain ⟨f, hf, e⟩ := List.any_eq_true.mp hc
  have := List.all_eq_true.mp h1 f hf
  rw [e] at this
  exact absurd this (by decide)

def c2 (a b : ℕ) : ℕ := sm a ||| sm b

def gpair (x1 x2 : ℕ) : Bool :=
  decide (x1 < 512) && decide (x2 < 512) && x1 != 0 && x2 != 0 && x1 != x2 && hasFr (c2 x1 x2)

/-- **finite fact FC3** -/
def fc3OK : Bool :=
  (List.range 512).all fun a => (List.range 512).all fun b =>
    a == 0 || b == 0 || a == b || gpair a b ||
    (List.range 512).all fun c => c == 0 || c == a || c == b || c == (a ^^^ b) ||
      gpair a c || gpair b c || gpair a (b ^^^ c) || gpair b (a ^^^ c) || gpair c (a ^^^ b) ||
      gpair (a ^^^ b) (a ^^^ c)

theorem v9_eq_of_add {a b : V9} (h : a + b = 0) : a = b := by
  funext k
  have := congrFun h k
  simp only [Pi.add_apply, Pi.zero_apply] at this
  generalize a k = x at this ⊢
  generalize b k = y at this ⊢
  revert x y; decide

/-- output of FC3 for one pair -/
def Good (z1 z2 z3 : V9) (y1 y2 : V9) : Prop :=
  y1 ≠ 0 ∧ y2 ≠ 0 ∧ y1 ≠ y2 ∧
    (∀ w : V9, w ⬝ᵥ z1 = 0 → w ⬝ᵥ z2 = 0 → w ⬝ᵥ z3 = 0 → w ⬝ᵥ y1 = 0 ∧ w ⬝ᵥ y2 = 0) ∧
    hasFr (cmask (zl y1) (zl y2)) = true

theorem good_of {z1 z2 z3 y1 y2 : V9} {x1 x2 : ℕ} (e1 : zl y1 = lz x1) (e2 : zl y2 = lz x2)
    (hspan : ∀ w : V9, w ⬝ᵥ z1 = 0 → w ⬝ᵥ z2 = 0 → w ⬝ᵥ z3 = 0 → w ⬝ᵥ y1 = 0 ∧ w ⬝ᵥ y2 = 0)
    (hg : gpair x1 x2 = true) : Good z1 z2 z3 y1 y2 := by
  simp only [gpair, Bool.and_eq_true, decide_eq_true_eq, bne_iff_ne, ne_eq] at hg
  obtain ⟨⟨⟨⟨⟨h1, h2⟩, n1⟩, n2⟩, n12⟩, hf⟩ := hg
  refine ⟨fun h0 => n1 ?_, fun h0 => n2 ?_, fun e => n12 ?_, hspan, ?_⟩
  · apply lz_inj h1 (by norm_num); rw [← e1, h0, lz_zero]; first | rfl | decide | simp [zl, zero9]
  · apply lz_inj h2 (by norm_num); rw [← e2, h0, lz_zero]; first | rfl | decide | simp [zl, zero9]
  · exact lz_inj h1 h2 (by rw [← e1, ← e2, e])
  · rw [cmask_eq, e1, e2, ← sm_eq h1, ← sm_eq h2]; exact hf

/-- **FC3 applied.** Three independent vectors killing the live labels give a framed pair in their span. -/
theorem framed_of_three (h : fc3OK = true) (z1 z2 z3 : V9) (h1 : z1 ≠ 0) (h2 : z2 ≠ 0) (h3 : z3 ≠ 0)
    (h12 : z1 ≠ z2) (h13 : z1 ≠ z3) (h23 : z2 ≠ z3) (h312 : z3 ≠ z1 + z2) :
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
  have dz : ∀ w : V9, w ⬝ᵥ z1 = 0 → w ⬝ᵥ z2 = 0 → w ⬝ᵥ z3 = 0 →
      w ⬝ᵥ z1 = 0 ∧ w ⬝ᵥ z2 = 0 ∧ w ⬝ᵥ z3 = 0 ∧ w ⬝ᵥ (z1 + z2) = 0 ∧ w ⬝ᵥ (z1 + z3) = 0 ∧
        w ⬝ᵥ (z2 + z3) = 0 := by
    intro w p1 p2 p3
    simp [dotProduct_add, p1, p2, p3]
  have hab := List.all_eq_true.mp (List.all_eq_true.mp h a (List.mem_range.mpr ha)) b (List.mem_range.mpr hb)
  simp only [Bool.or_eq_true, beq_iff_eq] at hab
  rcases hab with (((e | e) | e) | e) | hin
  · exact absurd e (zne ha ea h1)
  · exact absurd e (zne hb eb h2)
  · exact absurd e (dne ea eb h12)
  · exact ⟨z1, z2, good_of ea.symm eb.symm (fun w p1 p2 p3 => ⟨p1, p2⟩) e⟩
  have hcc := List.all_eq_true.mp hin c (List.mem_range.mpr hc)
  simp only [Bool.or_eq_true, beq_iff_eq] at hcc
  rcases hcc with (((((((((e | e) | e) | e) | e) | e) | e) | e) | e) | e)
  · exact absurd e (zne hc ec h3)
  · exact absurd e (dne ec ea (Ne.symm h13))
  · exact absurd e (dne ec eb (Ne.symm h23))
  · exact absurd e (dne ec xab h312)
  · exact ⟨z1, z3, good_of ea.symm ec.symm (fun w p1 p2 p3 => ⟨p1, p3⟩) e⟩
  · exact ⟨z2, z3, good_of eb.symm ec.symm (fun w p1 p2 p3 => ⟨p2, p3⟩) e⟩
  · exact ⟨z1, z2 + z3, good_of ea.symm xbc.symm (fun w p1 p2 p3 => ⟨p1, (dz w p1 p2 p3).2.2.2.2.2⟩) e⟩
  · exact ⟨z2, z1 + z3, good_of eb.symm xac.symm (fun w p1 p2 p3 => ⟨p2, (dz w p1 p2 p3).2.2.2.2.1⟩) e⟩
  · exact ⟨z3, z1 + z2, good_of ec.symm xab.symm (fun w p1 p2 p3 => ⟨p3, (dz w p1 p2 p3).2.2.2.1⟩) e⟩
  · exact ⟨z1 + z2, z1 + z3, good_of xab.symm xac.symm
      (fun w p1 p2 p3 => ⟨(dz w p1 p2 p3).2.2.2.1, (dz w p1 p2 p3).2.2.2.2.1⟩) e⟩

end RankNine.Facts
