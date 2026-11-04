import RankNine.T1Glue
import RankNine.T2Zero
import RankNine.T2Exp

/-!
# T1 per type from a table (hand route, SCHEME §3.2, NOTE §13.25 stages 1–2)

One record `T1D` per framed type: the closure certificate (`T2Close.Cert`, rules (a), (b), (c) from frames inside
`Z`, gauge tree with no diagonal scale) and the zero step (contagion chains as a RUP certificate, `T2Zero`), on one
edge table `ER`, `EC`.  `T1D.ok` is one Boolean check; `T1D.sound` proves once, for every record:

  `d.ok = true` ⇒ `M` is Gram (`GramP`) on `d.zm × d.zm`,

for every masked matrix whose rows in the dead mask `d.m` are orthogonal to one `u ≠ 0` (R3: `D_j = Z_E`).
The records themselves are data; `d.ok = true` for the 387 records is the named table hypothesis (checked by the
same `ok` with `#eval`, and by an independent Python checker).
-/

namespace RankNine.T2

open Matrix RankNine

variable {K : Type*} [Field K] [CharZero K]

/-- a frame inside the mask `m` -/
def frIn (m : ℕ) (F : List ℕ) : Bool := frameOK F && F.all m.testBit

/-- the frames of all stored T1 descriptors lie inside `m` -/
def t1FramesOK (DS : BT (List ℕ)) (m : ℕ) : Bool :=
  (List.range (2 ^ DS.dp)).all fun a =>
    if (DS.get [] a).length = 29 then (List.range 3).all fun i => frIn m (fr3 (DS.get [] a) i)
    else if (DS.get [] a).length = 21 then (List.range 2).all fun i => frIn m (fr3 (DS.get [] a) i)
    else DS.get [] a == [] || frIn m (dfr (DS.get [] a))

/-- the frames of the zero certificate lie inside `m` -/
def zFramesOK (FT : BT (List ℕ)) (m : ℕ) : Bool :=
  (List.range (2 ^ FT.dp)).all fun fi => FT.get [] fi == [] || frIn m (FT.get [] fi)

section

variable (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
  (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (u : Fin 9 → K) (hu0 : u ≠ 0) (m : ℕ)
  (hu : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0)
include hdiag hmask hu0 hu

theorem expOK_frIn {F : List ℕ} (h : frIn m F = true) : ExpOK A B m F := by
  unfold frIn at h
  simp only [Bool.and_eq_true] at h
  exact expOK_of_dead A B hdiag hmask u hu0 m hu F h.1 h.2

theorem t1Frames_get {DS : BT (List ℕ)} (h : t1FramesOK DS m = true) {a : ℕ} (ha : DS.get [] a ≠ []) :
    (if (DS.get [] a).length = 29 then (List.range 3).all fun i => frIn m (fr3 (DS.get [] a) i)
      else if (DS.get [] a).length = 21 then (List.range 2).all fun i => frIn m (fr3 (DS.get [] a) i)
      else DS.get [] a == [] || frIn m (dfr (DS.get [] a))) = true := by
  by_cases hlt : a < 2 ^ DS.dp
  · exact List.all_eq_true.mp h a (List.mem_range.mpr hlt)
  · exact absurd (BT.get_big _ _ _ (Nat.not_lt.mp hlt)) ha

theorem t1_hExp {DS : BT (List ℕ)} (h : t1FramesOK DS m = true) :
    ∀ a, (DS.get [] a).length ≠ 29 → (DS.get [] a).length ≠ 21 → DS.get [] a ≠ [] →
      ExpOK A B m (dfr (DS.get [] a)) := by
  intro a h29 h21 ha
  have hg := t1Frames_get A B hdiag hmask u hu0 m hu h ha
  rw [if_neg h29, if_neg h21] at hg
  simp only [Bool.or_eq_true, beq_iff_eq] at hg
  rcases hg with h0 | hf
  · exact absurd h0 ha
  · exact expOK_frIn A B hdiag hmask u hu0 m hu hf

theorem t1_hExp3 {DS : BT (List ℕ)} (h : t1FramesOK DS m = true) :
    ∀ a, (DS.get [] a).length = 29 → ∀ i < 3, ExpOK A B m (fr3 (DS.get [] a) i) := by
  intro a h29 i hi
  have ha : DS.get [] a ≠ [] := fun h0 => by rw [h0] at h29; simp at h29
  have hg := t1Frames_get A B hdiag hmask u hu0 m hu h ha
  rw [if_pos h29] at hg
  exact expOK_frIn A B hdiag hmask u hu0 m hu (List.all_eq_true.mp hg i (List.mem_range.mpr hi))

theorem t1_hExp2 {DS : BT (List ℕ)} (h : t1FramesOK DS m = true) :
    ∀ a, (DS.get [] a).length = 21 → ∀ i < 2, ExpOK A B m (fr3 (DS.get [] a) i) := by
  intro a h21 i hi
  have ha : DS.get [] a ≠ [] := fun h0 => by rw [h0] at h21; simp at h21
  have h29 : (DS.get [] a).length ≠ 29 := by omega
  have hg := t1Frames_get A B hdiag hmask u hu0 m hu h ha
  rw [if_neg h29, if_pos h21] at hg
  exact expOK_frIn A B hdiag hmask u hu0 m hu (List.all_eq_true.mp hg i (List.mem_range.mpr hi))

theorem z_hFT {FT : BT (List ℕ)} (h : zFramesOK FT m = true) :
    ∀ fi, FT.get [] fi ≠ [] → ExpOK A B m (FT.get [] fi) := by
  intro fi hf
  by_cases hlt : fi < 2 ^ FT.dp
  · have hg := List.all_eq_true.mp h fi (List.mem_range.mpr hlt)
    simp only [Bool.or_eq_true, beq_iff_eq] at hg
    rcases hg with h0 | hF
    · exact absurd h0 hf
    · exact expOK_frIn A B hdiag hmask u hu0 m hu hF
  · exact absurd (BT.get_big _ _ _ (Nat.not_lt.mp hlt)) hf

end

/-- one T1 record: closure certificate + zero certificate on one edge table -/
structure T1D where
  C : Cert
  EI : BT ℕ
  ER : BT ℕ
  EC : BT ℕ
  DS : BT (List ℕ)
  nE : ℕ
  m : ℕ
  zm : ℕ
  T : List (ℕ × Bool)
  r0 : ℕ
  zG : ℕ
  zVT : BT (List ℕ)
  zFT : BT (List ℕ)
  zEN : BT (List ℕ)
  zn : ℕ
  zGV : BT ℕ

/-- zero-edge coverage, exactly the hypothesis of `t2_zero` -/
def zEdges (d : T1D) : Bool :=
  (List.range d.nE).all (fun e => decide (d.ER.get 0 e < 104) && (decide (d.ER.get 0 e = d.EC.get 0 e) ||
    (d.zG.testBit (d.zGV.get 0 e) && d.zVT.get [] (d.zGV.get 0 e) == [0, d.ER.get 0 e, d.EC.get 0 e])))

/-- **the check of one T1 record** -/
def T1D.ok (d : T1D) : Bool :=
  check d.C && glue1OK d.C d.EI d.ER d.EC d.DS d.nE d.m d.T d.r0 && cov1OK d.EI d.ER d.EC d.nE d.zm d.C.NE &&
  t1FramesOK d.DS d.m && zFramesOK d.zFT d.m &&
  (List.range d.zn).all (entryOK d.m 104 d.zG d.zVT d.zFT d.zEN) &&
  decide (clOf d.zG (d.zEN.get [] (d.zn - 1)) = (0, 0)) && decide (0 < d.zn) && zEdges d

/-- **T1 for one record.**  A checked record gives Gram on `zm × zm`. -/
theorem T1D.sound (d : T1D) (h : d.ok = true) (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (u : Fin 9 → K) (hu0 : u ≠ 0)
    (hu : ∀ x, d.m.testBit x = true → A x ⬝ᵥ u = 0) :
    ∃ g : ℕ → K, (∀ x, g x ≠ 0) ∧
      ∀ x < 104, ∀ y < 104, d.zm.testBit x = true → d.zm.testBit y = true → GramP A B g x y := by
  unfold T1D.ok at h
  simp only [Bool.and_eq_true] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨hc, hg⟩, hcov⟩, hfr⟩, hzfr⟩, hall⟩, hlast⟩, hn⟩, hze⟩ := h
  have hMnz := t2_zero A B hdiag hmask d.m 104 d.zG (fun h => absurd h (lt_irrefl _)) d.zVT d.zFT d.zEN
    (z_hFT A B hdiag hmask u hu0 d.m hu hzfr) d.zn
    (fun j hj => List.all_eq_true.mp hall j (List.mem_range.mpr hj)) (of_decide_eq_true hlast)
    (of_decide_eq_true hn) d.ER d.EC d.zGV d.nE hze
  exact t1_gram A B hdiag hmask d.C d.EI d.ER d.EC d.DS d.nE d.m d.zm d.T d.r0 hc hg hcov
    (t1_hExp A B hdiag hmask u hu0 d.m hu hfr) (t1_hExp3 A B hdiag hmask u hu0 d.m hu hfr)
    (t1_hExp2 A B hdiag hmask u hu0 d.m hu hfr) hMnz

end RankNine.T2
