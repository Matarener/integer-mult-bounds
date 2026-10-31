import RankNine.Signs

/-!
# T1 zero step (RUP certificate on bit-mask clauses)

The moduli step needs `N c ≠ 0` on its cover set (the codes that lie in some frame-sum quadruple).  With
`z c :≡ (N c = 0)` the geometry gives three kinds of clauses:
* a relation `N x N y = N u N v` (frame expansion, `relChk`) gives `z x → z u ∨ z v`, `z y → z u ∨ z v`,
  `z u → z x ∨ z y`, `z v → z x ∨ z y`;
* a frame-sum quadruple (`quad_sum`, sum of its four terms `= 1`) gives "not all four zero";
* the goal clause "some code of the cover set is zero" (the negation of what we want).
A SAT solver (CaDiCaL) shows the conjunction is unsatisfiable and writes an LRAT proof; the generator keeps only
the clauses that the proof uses and every lemma with its unit-propagation hints (RUP).  The checker below works on
clauses given as bit masks `(P, Q)` (positive literals `z i` for bits of `P`, negative literals for bits of `Q`):
unit propagation along the hints is two GMP bit operations per hint.
-/

namespace RankNine

open Matrix

/-- clause `(P, Q)` holds under `z` -/
def CSat (z : ℕ → Prop) (c : ℕ × ℕ) : Prop :=
  ∃ i, (c.1.testBit i = true ∧ z i) ∨ (c.2.testBit i = true ∧ ¬ z i)

/-- partial assignment: bits of `T` true, bits of `F` false -/
def Agree (z : ℕ → Prop) (T F : ℕ) : Prop :=
  (∀ i, T.testBit i = true → z i) ∧ (∀ i, F.testBit i = true → ¬ z i)

/-- positive literals of `c` not yet false -/
def remP (c : ℕ × ℕ) (F : ℕ) : ℕ := c.1 ^^^ (c.1 &&& F)
/-- negative literals of `c` not yet false -/
def remQ (c : ℕ × ℕ) (T : ℕ) : ℕ := c.2 ^^^ (c.2 &&& T)

/-- one hint: `0` conflict, `1` unit (assignment extended), `2` failure -/
def unitStep (T F : ℕ) (c : ℕ × ℕ) : ℕ × ℕ × ℕ :=
  if remP c F = 0 ∧ remQ c T = 0 then (0, T, F)
  else if remQ c T = 0 ∧ remP c F = 2 ^ (remP c F).log2 then (1, T ||| remP c F, F)
  else if remP c F = 0 ∧ remQ c T = 2 ^ (remQ c T).log2 then (1, T, F ||| remQ c T)
  else (2, T, F)

theorem bit_rem (P F i : ℕ) : (P ^^^ (P &&& F)).testBit i = (P.testBit i && !F.testBit i) := by
  first
  | (rw [Nat.testBit_xor, Nat.testBit_and]; cases P.testBit i <;> cases F.testBit i <;> rfl)
  | (simp only [Nat.testBit_xor, Nat.testBit_land]; cases P.testBit i <;> cases F.testBit i <;> rfl)

theorem bit_or (x y i : ℕ) : (x ||| y).testBit i = (x.testBit i || y.testBit i) := by
  first
  | exact Nat.testBit_or x y i
  | exact Nat.testBit_lor x y i
  | simp

theorem bit_pow (k i : ℕ) : (2 ^ k).testBit i = true ↔ i = k := by
  rw [Nat.testBit_two_pow]
  simp only [decide_eq_true_eq]
  exact eq_comm

theorem bit_zero (i : ℕ) : (0 : ℕ).testBit i = false := Nat.zero_testBit i

theorem pow_bit {x i : ℕ} (hx : x = 2 ^ x.log2) (h : x.testBit i = true) : i = x.log2 := by
  rw [hx] at h
  exact (bit_pow _ _).1 h

theorem unit_key {z : ℕ → Prop} {T F : ℕ} {c : ℕ × ℕ} (hA : Agree z T F) (hc : CSat z c) :
    ∃ i, ((remP c F).testBit i = true ∧ z i) ∨ ((remQ c T).testBit i = true ∧ ¬ z i) := by
  obtain ⟨i, hi⟩ := hc
  refine ⟨i, ?_⟩
  simp only [remP, remQ, bit_rem]
  rcases hi with ⟨hp, hz⟩ | ⟨hq, hz⟩
  · left
    refine ⟨?_, hz⟩
    cases hF : F.testBit i
    · simp [hp]
    · exact absurd hz (hA.2 i hF)
  · right
    refine ⟨?_, hz⟩
    cases hT : T.testBit i
    · simp [hq]
    · exact absurd (hA.1 i hT) hz

theorem unitStep_conf {z : ℕ → Prop} {T F : ℕ} {c : ℕ × ℕ} (hA : Agree z T F) (hc : CSat z c)
    {T' F' : ℕ} (h : unitStep T F c = (0, T', F')) : False := by
  obtain ⟨i, hi⟩ := unit_key hA hc
  unfold unitStep at h
  split_ifs at h with h1 h2 h3
  · rw [h1.1, h1.2, bit_zero] at hi
    simp at hi
  · simp at h
  · simp at h
  · simp at h

theorem unitStep_unit {z : ℕ → Prop} {T F : ℕ} {c : ℕ × ℕ} (hA : Agree z T F) (hc : CSat z c)
    {T' F' : ℕ} (h : unitStep T F c = (1, T', F')) : Agree z T' F' := by
  obtain ⟨i, hi⟩ := unit_key hA hc
  unfold unitStep at h
  split_ifs at h with h1 h2 h3
  · simp at h
  · simp only [Prod.mk.injEq] at h
    obtain ⟨-, hT', hF'⟩ := h
    subst hT' hF'
    have hzi : z (remP c F).log2 := by
      rcases hi with ⟨hb, hz⟩ | ⟨hb, hz⟩
      · rw [pow_bit h2.2 hb] at hz; exact hz
      · rw [h2.1, bit_zero] at hb; simp at hb
    refine ⟨fun j hj => ?_, hA.2⟩
    rw [bit_or, Bool.or_eq_true] at hj
    rcases hj with hj | hj
    · exact hA.1 j hj
    · rw [pow_bit h2.2 hj]; exact hzi
  · simp only [Prod.mk.injEq] at h
    obtain ⟨-, hT', hF'⟩ := h
    subst hT' hF'
    have hzi : ¬ z (remQ c T).log2 := by
      rcases hi with ⟨hb, hz⟩ | ⟨hb, hz⟩
      · rw [h3.1, bit_zero] at hb; simp at hb
      · rw [pow_bit h3.2 hb] at hz; exact hz
    refine ⟨hA.1, fun j hj => ?_⟩
    rw [bit_or, Bool.or_eq_true] at hj
    rcases hj with hj | hj
    · exact hA.2 j hj
    · rw [pow_bit h3.2 hj]; exact hzi
  · simp at h

/-- unit propagation along the hint clauses; `true` iff a conflict is reached -/
def rupRun (cl : ℕ → ℕ × ℕ) : List ℕ → ℕ → ℕ → Bool
  | [], _, _ => false
  | h :: hs, T, F =>
    match unitStep T F (cl h) with
    | (0, _, _) => true
    | (1, T', F') => rupRun cl hs T' F'
    | _ => false

theorem rupRun_sound (z : ℕ → Prop) (cl : ℕ → ℕ × ℕ) :
    ∀ (hs : List ℕ) (T F : ℕ), (∀ h ∈ hs, CSat z (cl h)) → Agree z T F → rupRun cl hs T F = true → False := by
  intro hs
  induction hs with
  | nil => intro T F _ _ hr; simp [rupRun] at hr
  | cons h hs ih =>
    intro T F hall hA hr
    have hc : CSat z (cl h) := hall h (by simp)
    have hall' : ∀ g ∈ hs, CSat z (cl g) := fun g hg => hall g (by simp [hg])
    simp only [rupRun] at hr
    rcases hu : unitStep T F (cl h) with ⟨s, T', F'⟩
    rw [hu] at hr
    rcases s with _ | _ | s
    · exact unitStep_conf hA hc hu
    · exact ih T' F' hall' (unitStep_unit hA hc hu) hr
    · simp at hr

theorem agree_neg {z : ℕ → Prop} {c : ℕ × ℕ} (h : ¬ CSat z c) : Agree z c.2 c.1 := by
  refine ⟨fun i hi => ?_, fun i hi hz => h ⟨i, Or.inl ⟨hi, hz⟩⟩⟩
  by_contra hz
  exact h ⟨i, Or.inr ⟨hi, hz⟩⟩

/-- RUP: if every hint clause holds and propagation from the negation of `c` reaches a conflict, `c` holds -/
theorem rup_sound (z : ℕ → Prop) (cl : ℕ → ℕ × ℕ) (c : ℕ × ℕ) (hs : List ℕ) (hall : ∀ h ∈ hs, CSat z (cl h))
    (hr : rupRun cl hs c.2 c.1 = true) : CSat z c := by
  by_contra hn
  exact rupRun_sound z cl hs _ _ hall (agree_neg hn) hr

theorem csat_empty (z : ℕ → Prop) : ¬ CSat z (0, 0) := by
  rintro ⟨i, ⟨h, _⟩ | ⟨h, _⟩⟩ <;> simp [bit_zero] at h

/-! ## Certificate tables

Entry `j` has seven fields of `E`: kind and arguments.
* kind `0`, relation clause: `t, s, f, ka, kb, v` (origin as in `relChk`, `v < 4` which of the four clauses);
* kind `1`, quadruple clause: `t, f, k1, k2, k3, k4`;
* kind `2`, goal clause (the cover set `Cv`);
* kind `3`, lemma: literal offset and count in `Lt` (literal `2 c + 1` is `z c`, `2 c` is `¬ z c`), hint offset
  and count in `Hn` (hints are earlier entries).
-/

def relCl (x y u v w : ℕ) : ℕ × ℕ :=
  if w = 0 then (2 ^ u ||| 2 ^ v, 2 ^ x)
  else if w = 1 then (2 ^ u ||| 2 ^ v, 2 ^ y)
  else if w = 2 then (2 ^ x ||| 2 ^ y, 2 ^ u)
  else (2 ^ x ||| 2 ^ y, 2 ^ v)

def litMask (Lt : List ℕ) (s : ℕ) (a m : ℕ) : ℕ :=
  (List.range' a m).foldl (fun acc i => if fld Lt i % 2 = s then acc ||| 2 ^ (fld Lt i / 2) else acc) 0

def ef (E : List ℕ) (j r : ℕ) : ℕ := fld E (7 * j + r)

def clAt (Cv : ℕ) (E Lt : List ℕ) (j : ℕ) : ℕ × ℕ :=
  if ef E j 0 = 0 then
    relCl (pcode (ef E j 1) (frL (ef E j 3) (ef E j 4))) (pcode (ef E j 2) (frL (ef E j 3) (ef E j 4)))
      (pcode (ef E j 1) (frL (ef E j 3) (ef E j 5))) (pcode (ef E j 2) (frL (ef E j 3) (ef E j 5))) (ef E j 6)
  else if ef E j 0 = 1 then
    (0, 2 ^ pcode (ef E j 1) (frL (ef E j 2) (ef E j 3)) ||| 2 ^ pcode (ef E j 1) (frL (ef E j 2) (ef E j 4)) |||
      2 ^ pcode (ef E j 1) (frL (ef E j 2) (ef E j 5)) ||| 2 ^ pcode (ef E j 1) (frL (ef E j 2) (ef E j 6)))
  else if ef E j 0 = 2 then (Cv, 0)
  else (litMask Lt 1 (ef E j 1) (ef E j 2), litMask Lt 0 (ef E j 1) (ef E j 2))

def qChk (m t f k1 k2 k3 k4 : ℕ) : Bool :=
  decide (t < 104) && m.testBit t && decide (k1 < 8) && decide (k2 < 8) && decide (k3 < 8) && decide (k4 < 8) &&
    decide (k1 ≠ k2) && decide (k1 ≠ k3) && decide (k1 ≠ k4) && decide (k2 ≠ k3) && decide (k2 ≠ k4) &&
    decide (k3 ≠ k4) &&
    (List.range 8).all (fun k => m.testBit (frL f k)) &&
    (List.range 8).all (fun k => decide (k = k1) || decide (k = k2) || decide (k = k3) || decide (k = k4) ||
      orthB t (frL f k))

def hintList (Hn : List ℕ) (a m : ℕ) : List ℕ := (List.range' a m).map (fld Hn)

def entryOK (m Cv : ℕ) (E Lt Hn : List ℕ) (j : ℕ) : Bool :=
  if ef E j 0 = 0 then
    relChk m (pcode (ef E j 1) (frL (ef E j 3) (ef E j 4)), pcode (ef E j 2) (frL (ef E j 3) (ef E j 4)),
      pcode (ef E j 1) (frL (ef E j 3) (ef E j 5)), pcode (ef E j 2) (frL (ef E j 3) (ef E j 5)))
      (ef E j 1) (ef E j 2) (ef E j 3) (ef E j 4) (ef E j 5) && decide (ef E j 6 < 4)
  else if ef E j 0 = 1 then
    qChk m (ef E j 1) (ef E j 2) (ef E j 3) (ef E j 4) (ef E j 5) (ef E j 6)
  else if ef E j 0 = 2 then true
  else
    (hintList Hn (ef E j 3) (ef E j 4)).all (fun h => decide (h < j)) &&
      rupRun (clAt Cv E Lt) (hintList Hn (ef E j 3) (ef E j 4)) (clAt Cv E Lt j).2 (clAt Cv E Lt j).1

variable {K : Type*} [Field K]

theorem relCl_sound (N : ℕ → K) (x y u v w : ℕ) (h : N x * N y = N u * N v) (hw : w < 4) :
    CSat (fun c => N c = 0) (relCl x y u v w) := by
  have pos2 : ∀ a b : ℕ, N a = 0 ∨ N b = 0 → CSat (fun c => N c = 0) (2 ^ a ||| 2 ^ b, 0) := by
    intro a b hab
    rcases hab with ha | hb
    · exact ⟨a, Or.inl ⟨by rw [bit_or, (bit_pow a a).2 rfl]; rfl, ha⟩⟩
    · exact ⟨b, Or.inl ⟨by rw [bit_or, (bit_pow b b).2 rfl]; simp, hb⟩⟩
  have gen : ∀ (P : ℕ) (q : ℕ), CSat (fun c => N c = 0) (P, 0) → CSat (fun c => N c = 0) (P, 2 ^ q) := by
    rintro P q ⟨i, hi⟩
    rcases hi with hi | ⟨hi, _⟩
    · exact ⟨i, Or.inl hi⟩
    · simp [bit_zero] at hi
  have neg1 : ∀ (P q : ℕ), N q ≠ 0 → CSat (fun c => N c = 0) (P, 2 ^ q) := by
    intro P q hq
    exact ⟨q, Or.inr ⟨(bit_pow q q).2 rfl, hq⟩⟩
  unfold relCl
  split_ifs with h0 h1 h2
  · by_cases hx : N x = 0
    · apply gen; apply pos2
      have : N u * N v = 0 := by rw [← h, hx, zero_mul]
      exact mul_eq_zero.1 this
    · exact neg1 _ _ hx
  · by_cases hy : N y = 0
    · apply gen; apply pos2
      have : N u * N v = 0 := by rw [← h, hy, mul_zero]
      exact mul_eq_zero.1 this
    · exact neg1 _ _ hy
  · by_cases hu : N u = 0
    · apply gen; apply pos2
      have : N x * N y = 0 := by rw [h, hu, zero_mul]
      exact mul_eq_zero.1 this
    · exact neg1 _ _ hu
  · by_cases hv : N v = 0
    · apply gen; apply pos2
      have : N x * N y = 0 := by rw [h, hv, mul_zero]
      exact mul_eq_zero.1 this
    · exact neg1 _ _ hv

theorem quadCl_sound (N : ℕ → K) (a b c d : ℕ) (h : N a + N b + N c + N d = 1) :
    CSat (fun e => N e = 0) (0, 2 ^ a ||| 2 ^ b ||| 2 ^ c ||| 2 ^ d) := by
  have bit4 : ∀ e, e = a ∨ e = b ∨ e = c ∨ e = d → (2 ^ a ||| 2 ^ b ||| 2 ^ c ||| 2 ^ d).testBit e = true := by
    intro e he
    simp only [bit_or, Bool.or_eq_true, bit_pow]
    tauto
  by_cases ha : N a = 0
  · by_cases hb : N b = 0
    · by_cases hc : N c = 0
      · by_cases hd : N d = 0
        · rw [ha, hb, hc, hd] at h; norm_num at h
        · exact ⟨d, Or.inr ⟨bit4 d (by tauto), hd⟩⟩
      · exact ⟨c, Or.inr ⟨bit4 c (by tauto), hc⟩⟩
    · exact ⟨b, Or.inr ⟨bit4 b (by tauto), hb⟩⟩
  · exact ⟨a, Or.inr ⟨bit4 a (by tauto), ha⟩⟩

theorem covB_bit {x i : ℕ} (h : covB x i = true) : x.testBit i = true := by
  simp only [covB, beq_iff_eq] at h
  first
  | (rw [Nat.testBit_to_div_mod, ← Nat.shiftRight_eq_div_pow, h]; rfl)
  | (simp only [Nat.testBit_to_div_mod, ← Nat.shiftRight_eq_div_pow, h]; rfl)
  | (simp only [Nat.testBit, Nat.one_and_eq_mod_two, h]; rfl)
  | (simp [Nat.testBit_to_div_mod, Nat.shiftRight_eq_div_pow] at h ⊢; omega)

/-- one entry is a true clause, given the earlier ones -/
theorem entry_sound (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (Cv : ℕ) (E Lt Hn : List ℕ)
    (hgoal : ∃ c, covB Cv c = true ∧ Nc A B c = 0) (j : ℕ) (hok : entryOK m Cv E Lt Hn j = true)
    (hprev : ∀ i < j, CSat (fun c => Nc A B c = 0) (clAt Cv E Lt i)) :
    CSat (fun c => Nc A B c = 0) (clAt Cv E Lt j) := by
  unfold entryOK at hok
  unfold clAt
  split_ifs at hok ⊢ with k0 k1 k2
  · simp only [Bool.and_eq_true, decide_eq_true_eq] at hok
    have hr := relChk_sound A B u hu m hZ hdiag hmask _ _ _ _ _ _ hok.1
    exact relCl_sound (Nc A B) _ _ _ _ _ hr hok.2
  · simp only [qChk, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.mem_range,
      Bool.or_eq_true, and_assoc] at hok
    obtain ⟨ht, hZt, h1, h2, h3, h4, d12, d13, d14, d23, d24, d34, hFZ, hrest⟩ := hok
    have f1 := frame_lt (ef E j 2) h1; have f2 := frame_lt (ef E j 2) h2
    have f3 := frame_lt (ef E j 2) h3; have f4 := frame_lt (ef E j 2) h4
    apply quadCl_sound
    rw [Nc_code A B ht f1, Nc_code A B ht f2, Nc_code A B ht f3, Nc_code A B ht f4]
    refine quad_sum A B u hu m hZ hdiag hmask _ _ _ _ _ _ ht hZt hFZ h1 h2 h3 h4 d12 d13 d14 d23 d24 d34 ?_
    intro k hk
    have hk' := frame_lt (ef E j 2) hk
    have hr := hrest k hk
    by_cases g1 : k = ef E j 3
    · exact Or.inl g1
    by_cases g2 : k = ef E j 4
    · exact Or.inr (Or.inl g2)
    by_cases g3 : k = ef E j 5
    · exact Or.inr (Or.inr (Or.inl g3))
    by_cases g4 : k = ef E j 6
    · exact Or.inr (Or.inr (Or.inr (Or.inl g4)))
    have g5 : orthB (ef E j 1) (frL (ef E j 2) k) = true := by tauto
    exact Or.inr (Or.inr (Or.inr (Or.inr (orth_of_orthB ht hk' g5))))
  · obtain ⟨c, hc, hz⟩ := hgoal
    exact ⟨c, Or.inl ⟨covB_bit hc, hz⟩⟩
  · simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hok
    obtain ⟨hlt, hrup⟩ := hok
    have h := rup_sound (fun c => Nc A B c = 0) (clAt Cv E Lt) (clAt Cv E Lt j) _
      (fun h hh => hprev h (hlt h hh)) hrup
    unfold clAt at h
    rw [if_neg k0, if_neg k1, if_neg k2] at h
    exact h

/-- the zero step: if all entries pass and the last entry is the empty lemma, no code of `Cv` has `N = 0` -/
theorem zero_sound (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (Cv : ℕ) (E Lt Hn : List ℕ) (n : ℕ)
    (hall : ∀ j < n, entryOK m Cv E Lt Hn j = true) (hlast : clAt Cv E Lt (n - 1) = (0, 0)) (hn : 0 < n) :
    ∀ c, covB Cv c = true → Nc A B c ≠ 0 := by
  intro c hc hz
  have hgoal : ∃ c, covB Cv c = true ∧ Nc A B c = 0 := ⟨c, hc, hz⟩
  have key : ∀ j, j < n → CSat (fun c => Nc A B c = 0) (clAt Cv E Lt j) := by
    intro j
    induction j using Nat.strong_induction_on with
    | _ j ih =>
      intro hj
      exact entry_sound A B u hu m hZ hdiag hmask Cv E Lt Hn hgoal j (hall j hj)
        (fun i hi => ih i hi (by omega))
  have := key (n - 1) (by omega)
  rw [hlast] at this
  exact csat_empty _ this

end RankNine
