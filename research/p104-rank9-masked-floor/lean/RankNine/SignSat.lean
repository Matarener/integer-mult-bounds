import RankNine.Zero

/-!
# T1 sign step by a RUP certificate (types where the F2 elimination does not force the magnitude bits)

Atoms: bit `c < TAG` is "the sign of `N` at code `c` is minus", bit `TAG + K` is "the magnitude bit of class `K`
is 1" (assignment `wv`, as in `RankNine.Signs`).  Every original clause forbids one 0/1 pattern on the atoms of a
checked row:
* quadruple row (codes `c1 … c4`, class `K`): the values `(s1, …, s4, m)` are `m = 0` with no minus or `m = 1`
  with exactly one minus (`quad_allowed`);
* relation row: the sign parity is even (`rel_sgn`), and the magnitude bits satisfy `m1 + m2 = m3 + m4`
  (`rel_mag`);
* goal clause: some class has magnitude bit 1.
A CaDiCaL LRAT proof (trimmed, with unit variables per hint) shows that these clauses are unsatisfiable, so every
class has magnitude bit 0, i.e. `N = 1/4` on its quadruples (`RankNine.quad_quarter`).
-/

namespace RankNine

open Matrix

variable {K : Type*} [Field K]

/-! ## Pattern clauses -/

/-- clause "some atom differs from the pattern `p`" (bit `i` of `p` for atom `i`) -/
def patCl : List ℕ → ℕ → ℕ × ℕ
  | [], _ => (0, 0)
  | a :: as, p =>
    if p % 2 = 0 then ((patCl as (p / 2)).1 ||| 2 ^ a, (patCl as (p / 2)).2)
    else ((patCl as (p / 2)).1, (patCl as (p / 2)).2 ||| 2 ^ a)

/-- the values `vs` match the pattern `p` -/
def patMatch : List ℕ → ℕ → Bool
  | [], _ => true
  | v :: vs, p => (v == p % 2) && patMatch vs (p / 2)

theorem csat_or1 {z : ℕ → Prop} {P Q : ℕ} (X : ℕ) (h : CSat z (P, Q)) : CSat z (P ||| X, Q) := by
  obtain ⟨i, hi⟩ := h
  refine ⟨i, ?_⟩
  rcases hi with ⟨h1, h2⟩ | ⟨h1, h2⟩
  · left; refine ⟨?_, h2⟩; simp only at h1 ⊢; rw [bit_or, h1]; rfl
  · right; exact ⟨h1, h2⟩

theorem csat_or2 {z : ℕ → Prop} {P Q : ℕ} (X : ℕ) (h : CSat z (P, Q)) : CSat z (P, Q ||| X) := by
  obtain ⟨i, hi⟩ := h
  refine ⟨i, ?_⟩
  rcases hi with ⟨h1, h2⟩ | ⟨h1, h2⟩
  · left; exact ⟨h1, h2⟩
  · right; refine ⟨?_, h2⟩; simp only at h1 ⊢; rw [bit_or, h1]; rfl

theorem patCl_sound (z : ℕ → Prop) :
    ∀ (l : List (ℕ × ℕ)) (p : ℕ), (∀ t ∈ l, t.2 ≤ 1 ∧ (z t.1 ↔ t.2 = 1)) →
      patMatch (l.map Prod.snd) p = false → CSat z (patCl (l.map Prod.fst) p) := by
  intro l
  induction l with
  | nil => intro p _ h; simp [patMatch] at h
  | cons t l ih =>
    intro p hl h
    have ht := hl t (by simp)
    have hl' : ∀ t' ∈ l, t'.2 ≤ 1 ∧ (z t'.1 ↔ t'.2 = 1) := fun t' h' => hl t' (by simp [h'])
    simp only [List.map_cons, patMatch, Bool.and_eq_false_iff, beq_eq_false_iff_ne, ne_eq] at h
    simp only [List.map_cons, patCl]
    by_cases hrest : patMatch (l.map Prod.snd) (p / 2) = false
    · have hr := ih (p / 2) hl' hrest
      split_ifs
      · exact csat_or1 _ hr
      · exact csat_or2 _ hr
    · have hv : t.2 ≠ p % 2 := by
        rcases h with h | h
        · exact h
        · exact absurd h hrest
      have hp := Nat.mod_two_eq_zero_or_one p
      split_ifs with h0
      · -- pattern bit 0, value 1: positive literal
        have h1 : t.2 = 1 := by omega
        exact ⟨t.1, Or.inl ⟨by rw [bit_or, (bit_pow _ _).2 rfl, Bool.or_true], ht.2.2 h1⟩⟩
      · -- pattern bit 1, value 0: negative literal
        have h1 : t.2 = 0 := by omega
        refine ⟨t.1, Or.inr ⟨by rw [bit_or, (bit_pow _ _).2 rfl, Bool.or_true], fun hz => ?_⟩⟩
        have := ht.2.1 hz
        omega

/-! ## Allowed values -/

def allowedQ (s1 s2 s3 s4 m : ℕ) : Bool :=
  (m == 0 && s1 + s2 + s3 + s4 == 0) || (m == 1 && s1 + s2 + s3 + s4 == 1)

section values

variable [CharZero K]

theorem sgnN_le (x : K) : sgnN x ≤ 1 := by unfold sgnN; split_ifs <;> omega

theorem quad_allowed {c x1 x2 x3 x4 : K} (h1 : x1 ^ 2 = c ^ 2) (h2 : x2 ^ 2 = c ^ 2) (h3 : x3 ^ 2 = c ^ 2)
    (h4 : x4 ^ 2 = c ^ 2) (hs : x1 + x2 + x3 + x4 = 1) :
    allowedQ (sgnN x1) (sgnN x2) (sgnN x3) (sgnN x4) (magN c) = true := by
  rcases sq_eq_sq_iff_eq_or_eq_neg.mp h1 with e1 | e1 <;>
  rcases sq_eq_sq_iff_eq_or_eq_neg.mp h2 with e2 | e2 <;>
  rcases sq_eq_sq_iff_eq_or_eq_neg.mp h3 with e3 | e3 <;>
  rcases sq_eq_sq_iff_eq_or_eq_neg.mp h4 with e4 | e4 <;>
  simp only [e1, e2, e3, e4] at hs ⊢ <;>
  first
  | ((suffices h0 : (0 : K) = 1 by exact absurd h0 zero_ne_one); linear_combination hs)
  | ((suffices hc : c = 1/4 by subst hc; norm_num [sgnN, magN, allowedQ]); linear_combination hs / 4)
  | ((suffices hc : c = -1/4 by subst hc; norm_num [sgnN, magN, allowedQ]); linear_combination -hs / 4)
  | ((suffices hc : c = 1/2 by subst hc; norm_num [sgnN, magN, allowedQ]); linear_combination hs / 2)
  | ((suffices hc : c = -1/2 by subst hc; norm_num [sgnN, magN, allowedQ]); linear_combination -hs / 2)

theorem rel_mag {a b c d : K} (ha : a = 1/4 ∨ a = -1/4 ∨ a = 1/2 ∨ a = -1/2)
    (hb : b = 1/4 ∨ b = -1/4 ∨ b = 1/2 ∨ b = -1/2) (hc : c = 1/4 ∨ c = -1/4 ∨ c = 1/2 ∨ c = -1/2)
    (hd : d = 1/4 ∨ d = -1/4 ∨ d = 1/2 ∨ d = -1/2) (h : a * b = c * d) :
    magN a + magN b = magN c + magN d := by
  rcases ha with rfl | rfl | rfl | rfl <;> rcases hb with rfl | rfl | rfl | rfl <;>
  rcases hc with rfl | rfl | rfl | rfl <;> rcases hd with rfl | rfl | rfl | rfl <;>
  revert h <;> norm_num [magN]

end values

/-! ## Certificate tables

Entry `j` has five fields of `E`: kind and arguments.
* kind `0`: quadruple clause, row `r` of `QS`, pattern `p < 32` not allowed;
* kind `1`: relation sign clause, row `r` of `RS`, pattern `p < 16` of odd weight on the four codes;
* kind `2`: relation magnitude clause, row `r` of `RS`, pattern `p < 16` with `p0 + p1 ≠ p2 + p3` on the four
  class bits;
* kind `3`: goal clause (all class bits);
* kind `4`: lemma: literal offset and count in `Lt`, hint offset and count in `Hn` (as in `RankNine.Zero`).
-/

def gMask : ℕ → ℕ
  | 0 => 0
  | n + 1 => gMask n ||| 2 ^ (TAG + n)

theorem gMask_bit : ∀ (n c : ℕ), c < n → (gMask n).testBit (TAG + c) = true := by
  intro n
  induction n with
  | zero => intro c h; omega
  | succ n ih =>
    intro c h
    simp only [gMask]
    rw [bit_or]
    rcases Nat.lt_succ_iff_lt_or_eq.1 h with h' | h'
    · rw [ih c h']; rfl
    · subst h'; rw [(bit_pow _ _).2 rfl, Bool.or_true]

def sf (E : List ℕ) (j r : ℕ) : ℕ := fld E (7 * j + r)

/-- hints `(clause, unit variable)`, three fields each (clause index split in two 16-bit fields) -/
def hint3 (Hn : List ℕ) (a m : ℕ) : List (ℕ × ℕ) :=
  (List.range' a m).map (fun i => (fld Hn (3 * i) + 65536 * fld Hn (3 * i + 1), fld Hn (3 * i + 2)))

def qAtoms (QS : List ℕ) (r : ℕ) : List ℕ :=
  [pcode (qRow QS r 0) (frL (qRow QS r 1) (qRow QS r 2)), pcode (qRow QS r 0) (frL (qRow QS r 1) (qRow QS r 3)),
    pcode (qRow QS r 0) (frL (qRow QS r 1) (qRow QS r 4)), pcode (qRow QS r 0) (frL (qRow QS r 1) (qRow QS r 5)),
    TAG + qRow QS r 10]

def rSAtoms (T RS : List ℕ) (r : ℕ) : List ℕ :=
  [fld T (3 * rRow RS r 5), fld T (3 * rRow RS r 6), fld T (3 * rRow RS r 7), fld T (3 * rRow RS r 8)]

def rMAtoms (RS : List ℕ) (r : ℕ) : List ℕ :=
  [TAG + rRow RS r 9, TAG + rRow RS r 10, TAG + rRow RS r 11, TAG + rRow RS r 12]

def sClAt (nK : ℕ) (T QS RS E Lt : List ℕ) (j : ℕ) : ℕ × ℕ :=
  if sf E j 0 = 0 then patCl (qAtoms QS (sf E j 1)) (sf E j 2)
  else if sf E j 0 = 1 then patCl (rSAtoms T RS (sf E j 1)) (sf E j 2)
  else if sf E j 0 = 2 then patCl (rMAtoms RS (sf E j 1)) (sf E j 2)
  else if sf E j 0 = 3 then (gMask nK, 0)
  else (litMask Lt 1 (sf E j 1 + 65536 * sf E j 2) (sf E j 3), litMask Lt 0 (sf E j 1 + 65536 * sf E j 2) (sf E j 3))

def sEntryOK (m nQ nK nq nr : ℕ) (T CR QS RS E Lt Hn : List ℕ) (j : ℕ) : Bool :=
  if sf E j 0 = 0 then
    decide (sf E j 1 < nq) && qRowOK m nQ nK T CR QS (sf E j 1) && decide (sf E j 2 < 32) &&
      !allowedQ (sf E j 2 % 2) (sf E j 2 / 2 % 2) (sf E j 2 / 4 % 2) (sf E j 2 / 8 % 2) (sf E j 2 / 16 % 2)
  else if sf E j 0 = 1 then
    decide (sf E j 1 < nr) && rRowOK m nQ nK T CR RS (sf E j 1) && decide (sf E j 2 < 16) &&
      decide ((sf E j 2 % 2 + sf E j 2 / 2 % 2 + sf E j 2 / 4 % 2 + sf E j 2 / 8 % 2) % 2 = 1)
  else if sf E j 0 = 2 then
    decide (sf E j 1 < nr) && rRowOK m nQ nK T CR RS (sf E j 1) && decide (sf E j 2 < 16) &&
      decide (sf E j 2 % 2 + sf E j 2 / 2 % 2 ≠ sf E j 2 / 4 % 2 + sf E j 2 / 8 % 2)
  else if sf E j 0 = 3 then true
  else
    (hint3 Hn (sf E j 4 + 65536 * sf E j 5) (sf E j 6)).all (fun h => decide (h.1 < j)) &&
      rupRun (sClAt nK T QS RS E Lt) (hint3 Hn (sf E j 4 + 65536 * sf E j 5) (sf E j 6))
        (sClAt nK T QS RS E Lt j).2 (sClAt nK T QS RS E Lt j).1

theorem patMatch5 {v0 v1 v2 v3 v4 p : ℕ} (h : patMatch [v0, v1, v2, v3, v4] p = true) :
    v0 = p % 2 ∧ v1 = p / 2 % 2 ∧ v2 = p / 4 % 2 ∧ v3 = p / 8 % 2 ∧ v4 = p / 16 % 2 := by
  simp only [patMatch, Bool.and_eq_true, beq_iff_eq, Bool.and_true] at h
  obtain ⟨h0, h1, h2, h3, h4, -⟩ := h
  refine ⟨h0, h1, ?_, ?_, ?_⟩
  · rw [h2, Nat.div_div_eq_div_mul]
  · rw [h3, Nat.div_div_eq_div_mul, Nat.div_div_eq_div_mul]
  · rw [h4, Nat.div_div_eq_div_mul, Nat.div_div_eq_div_mul, Nat.div_div_eq_div_mul]

theorem patMatch4 {v0 v1 v2 v3 p : ℕ} (h : patMatch [v0, v1, v2, v3] p = true) :
    v0 = p % 2 ∧ v1 = p / 2 % 2 ∧ v2 = p / 4 % 2 ∧ v3 = p / 8 % 2 := by
  simp only [patMatch, Bool.and_eq_true, beq_iff_eq, Bool.and_true] at h
  obtain ⟨h0, h1, h2, h3, -⟩ := h
  refine ⟨h0, h1, ?_, ?_⟩
  · rw [h2, Nat.div_div_eq_div_mul]
  · rw [h3, Nat.div_div_eq_div_mul, Nat.div_div_eq_div_mul]

section sound

variable [CharZero K]

/-- the assignment: `wv = 1` -/
def zS (A B : ℕ → Fin 9 → K) (CR : List ℕ) (i : ℕ) : Prop := wv A B CR i = 1

theorem zS_code (A B : ℕ → Fin 9 → K) (CR : List ℕ) {c : ℕ} (hc : c < TAG) :
    (zS A B CR c ↔ sgnN (Nc A B c) = 1) := by
  unfold zS; rw [wv_code A B CR hc]

theorem zS_tag (A B : ℕ → Fin 9 → K) (CR : List ℕ) (c : ℕ) :
    (zS A B CR (TAG + c) ↔ magN (Nc A B (fld CR c)) = 1) := by
  unfold zS; rw [wv_tag]

theorem sentry_sound (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (nQ nK nq nr : ℕ)
    (T CR QS RS E Lt Hn : List ℕ)
    (hT : ∀ e < nQ, Nc A B (fld T (3 * e)) ^ 2 = Nc A B (fld T (3 * e + 1)) ^ 2)
    (hcls : ∀ c < nK, Nc A B (fld CR c) ^ 2 = 1/16 ∨ Nc A B (fld CR c) ^ 2 = 1/4)
    (hgoal : ∃ c < nK, magN (Nc A B (fld CR c)) ≠ 0) (j : ℕ)
    (hok : sEntryOK m nQ nK nq nr T CR QS RS E Lt Hn j = true)
    (hprev : ∀ i < j, CSat (zS A B CR) (sClAt nK T QS RS E Lt i)) :
    CSat (zS A B CR) (sClAt nK T QS RS E Lt j) := by
  unfold sEntryOK at hok
  unfold sClAt
  split_ifs at hok ⊢ with k0 k1 k2 k3
  · -- quadruple clause
    simp only [Bool.and_eq_true, decide_eq_true_eq, Bool.not_eq_true'] at hok
    obtain ⟨⟨⟨_, hr⟩, _⟩, hna⟩ := hok
    unfold qRowOK at hr
    obtain ⟨_, _, l1, l2, l3, l4, s1, s2, s3, s4, hs⟩ := quadChk_sound A B u hu m hZ hdiag hmask nQ nK T CR hT _ _ _ _ _ _ _ _ _ _ _ hr
    have hal := quad_allowed s1 s2 s3 s4 hs
    let r := sf E j 1
    let l : List (ℕ × ℕ) :=
      [(pcode (qRow QS r 0) (frL (qRow QS r 1) (qRow QS r 2)),
          sgnN (Nc A B (pcode (qRow QS r 0) (frL (qRow QS r 1) (qRow QS r 2))))),
        (pcode (qRow QS r 0) (frL (qRow QS r 1) (qRow QS r 3)),
          sgnN (Nc A B (pcode (qRow QS r 0) (frL (qRow QS r 1) (qRow QS r 3))))),
        (pcode (qRow QS r 0) (frL (qRow QS r 1) (qRow QS r 4)),
          sgnN (Nc A B (pcode (qRow QS r 0) (frL (qRow QS r 1) (qRow QS r 4))))),
        (pcode (qRow QS r 0) (frL (qRow QS r 1) (qRow QS r 5)),
          sgnN (Nc A B (pcode (qRow QS r 0) (frL (qRow QS r 1) (qRow QS r 5))))),
        (TAG + qRow QS r 10, magN (Nc A B (fld CR (qRow QS r 10))))]
    have hatoms : l.map Prod.fst = qAtoms QS r := rfl
    rw [← hatoms]
    refine patCl_sound (zS A B CR) l _ ?_ ?_
    · intro t ht
      simp only [l, List.mem_cons, List.not_mem_nil, or_false] at ht
      rcases ht with rfl | rfl | rfl | rfl | rfl
      · exact ⟨sgnN_le _, zS_code A B CR l1⟩
      · exact ⟨sgnN_le _, zS_code A B CR l2⟩
      · exact ⟨sgnN_le _, zS_code A B CR l3⟩
      · exact ⟨sgnN_le _, zS_code A B CR l4⟩
      · exact ⟨magN_le _, zS_tag A B CR _⟩
    · by_contra hm
      rw [Bool.not_eq_false] at hm
      obtain ⟨e0, e1, e2, e3, e4⟩ := patMatch5 hm
      rw [e0, e1, e2, e3, e4] at hal
      exact absurd hal (by simpa using hna)
  · -- relation sign clause
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hok
    obtain ⟨⟨⟨_, hr⟩, _⟩, hodd⟩ := hok
    unfold rRowOK at hr
    simp only [relRowChk, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq, and_assoc] at hr
    obtain ⟨hrc, he1, he2, he3, he4, hc1, hc2, hc3, hc4, l1, l2, l3, l4, r1, r2, r3, r4⟩ := hr
    have hrel := relChk_sound A B u hu m hZ hdiag hmask _ _ _ _ _ _ hrc
    simp only [holds] at hrel
    let r := sf E j 1
    have q1 : Nc A B (fld T (3 * rRow RS r 5)) ^ 2 = Nc A B (fld CR (rRow RS r 9)) ^ 2 := by
      rw [← r1]; exact hT _ he1
    have q2 : Nc A B (fld T (3 * rRow RS r 6)) ^ 2 = Nc A B (fld CR (rRow RS r 10)) ^ 2 := by
      rw [← r2]; exact hT _ he2
    have q3 : Nc A B (fld T (3 * rRow RS r 7)) ^ 2 = Nc A B (fld CR (rRow RS r 11)) ^ 2 := by
      rw [← r3]; exact hT _ he3
    have q4 : Nc A B (fld T (3 * rRow RS r 8)) ^ 2 = Nc A B (fld CR (rRow RS r 12)) ^ 2 := by
      rw [← r4]; exact hT _ he4
    have hpar := rel_sgn (inS_of_sq q1 (hcls _ hc1)) (inS_of_sq q2 (hcls _ hc2)) (inS_of_sq q3 (hcls _ hc3))
      (inS_of_sq q4 (hcls _ hc4)) hrel
    let l : List (ℕ × ℕ) :=
      [(fld T (3 * rRow RS r 5), sgnN (Nc A B (fld T (3 * rRow RS r 5)))),
        (fld T (3 * rRow RS r 6), sgnN (Nc A B (fld T (3 * rRow RS r 6)))),
        (fld T (3 * rRow RS r 7), sgnN (Nc A B (fld T (3 * rRow RS r 7)))),
        (fld T (3 * rRow RS r 8), sgnN (Nc A B (fld T (3 * rRow RS r 8))))]
    have hatoms : l.map Prod.fst = rSAtoms T RS r := rfl
    rw [← hatoms]
    refine patCl_sound (zS A B CR) l _ ?_ ?_
    · intro t ht
      simp only [l, List.mem_cons, List.not_mem_nil, or_false] at ht
      rcases ht with rfl | rfl | rfl | rfl
      · exact ⟨sgnN_le _, zS_code A B CR l1⟩
      · exact ⟨sgnN_le _, zS_code A B CR l2⟩
      · exact ⟨sgnN_le _, zS_code A B CR l3⟩
      · exact ⟨sgnN_le _, zS_code A B CR l4⟩
    · by_contra hm
      rw [Bool.not_eq_false] at hm
      obtain ⟨e0, e1, e2, e3⟩ := patMatch4 hm
      rw [e0, e1, e2, e3] at hpar
      omega
  · -- relation magnitude clause
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hok
    obtain ⟨⟨⟨_, hr⟩, _⟩, hne⟩ := hok
    unfold rRowOK at hr
    simp only [relRowChk, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq, and_assoc] at hr
    obtain ⟨hrc, he1, he2, he3, he4, hc1, hc2, hc3, hc4, l1, l2, l3, l4, r1, r2, r3, r4⟩ := hr
    have hrel := relChk_sound A B u hu m hZ hdiag hmask _ _ _ _ _ _ hrc
    simp only [holds] at hrel
    let r := sf E j 1
    have q1 : Nc A B (fld T (3 * rRow RS r 5)) ^ 2 = Nc A B (fld CR (rRow RS r 9)) ^ 2 := by
      rw [← r1]; exact hT _ he1
    have q2 : Nc A B (fld T (3 * rRow RS r 6)) ^ 2 = Nc A B (fld CR (rRow RS r 10)) ^ 2 := by
      rw [← r2]; exact hT _ he2
    have q3 : Nc A B (fld T (3 * rRow RS r 7)) ^ 2 = Nc A B (fld CR (rRow RS r 11)) ^ 2 := by
      rw [← r3]; exact hT _ he3
    have q4 : Nc A B (fld T (3 * rRow RS r 8)) ^ 2 = Nc A B (fld CR (rRow RS r 12)) ^ 2 := by
      rw [← r4]; exact hT _ he4
    have hmag := rel_mag (inS_of_sq q1 (hcls _ hc1)) (inS_of_sq q2 (hcls _ hc2)) (inS_of_sq q3 (hcls _ hc3))
      (inS_of_sq q4 (hcls _ hc4)) hrel
    rw [magN_of_sq q1, magN_of_sq q2, magN_of_sq q3, magN_of_sq q4] at hmag
    let l : List (ℕ × ℕ) :=
      [(TAG + rRow RS r 9, magN (Nc A B (fld CR (rRow RS r 9)))),
        (TAG + rRow RS r 10, magN (Nc A B (fld CR (rRow RS r 10)))),
        (TAG + rRow RS r 11, magN (Nc A B (fld CR (rRow RS r 11)))),
        (TAG + rRow RS r 12, magN (Nc A B (fld CR (rRow RS r 12))))]
    have hatoms : l.map Prod.fst = rMAtoms RS r := rfl
    rw [← hatoms]
    refine patCl_sound (zS A B CR) l _ ?_ ?_
    · intro t ht
      simp only [l, List.mem_cons, List.not_mem_nil, or_false] at ht
      rcases ht with rfl | rfl | rfl | rfl <;> exact ⟨magN_le _, zS_tag A B CR _⟩
    · by_contra hm
      rw [Bool.not_eq_false] at hm
      obtain ⟨e0, e1, e2, e3⟩ := patMatch4 hm
      rw [e0, e1, e2, e3] at hmag
      exact hne hmag
  · -- goal clause
    obtain ⟨c, hc, hne⟩ := hgoal
    have h1 : magN (Nc A B (fld CR c)) = 1 := by have := magN_le (Nc A B (fld CR c)); omega
    exact ⟨TAG + c, Or.inl ⟨gMask_bit nK c hc, (zS_tag A B CR c).2 h1⟩⟩
  · -- lemma
    simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hok
    obtain ⟨hlt, hrup⟩ := hok
    have h := rup_sound (zS A B CR) (sClAt nK T QS RS E Lt) (sClAt nK T QS RS E Lt j) _
      (fun h hh => hprev h.1 (hlt h hh)) hrup
    unfold sClAt at h
    rw [if_neg k0, if_neg k1, if_neg k2, if_neg k3] at h
    exact h

/-- every class with a checked quadruple row has square `1/16` or `1/4` -/
def cqOK (m nQ nK : ℕ) (T CR QS CQ : List ℕ) (nq c : ℕ) : Bool :=
  classOK QS CQ nq c && qRowOK m nQ nK T CR QS (fld CQ c)

theorem signsat_sound (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (nQ nK nq nr : ℕ)
    (T CR QS RS CQ E Lt Hn : List ℕ) (n : ℕ)
    (hT : ∀ e < nQ, Nc A B (fld T (3 * e)) ^ 2 = Nc A B (fld T (3 * e + 1)) ^ 2)
    (hcq : ∀ c < nK, cqOK m nQ nK T CR QS CQ nq c = true)
    (hall : ∀ j < n, sEntryOK m nQ nK nq nr T CR QS RS E Lt Hn j = true)
    (hlast : sClAt nK T QS RS E Lt (n - 1) = (0, 0)) (hn : 0 < n) :
    ∀ c < nK, magN (Nc A B (fld CR c)) = 0 := by
  have hcls : ∀ c < nK, Nc A B (fld CR c) ^ 2 = 1/16 ∨ Nc A B (fld CR c) ^ 2 = 1/4 := by
    intro c hc
    have h := hcq c hc
    simp only [cqOK, classOK, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at h
    obtain ⟨⟨_, h10⟩, hr⟩ := h
    unfold qRowOK at hr
    have := (quadRow_par A B u hu m hZ hdiag hmask nQ nK T CR hT _ _ _ _ _ _ _ _ _ _ _ hr).2.1
    rw [h10] at this
    exact this
  by_contra hne
  push_neg at hne
  obtain ⟨c, hc, hz⟩ := hne
  have hgoal : ∃ c < nK, magN (Nc A B (fld CR c)) ≠ 0 := ⟨c, hc, hz⟩
  have key : ∀ j, j < n → CSat (zS A B CR) (sClAt nK T QS RS E Lt j) := by
    intro j
    induction j using Nat.strong_induction_on with
    | _ j ih =>
      intro hj
      exact sentry_sound A B u hu m hZ hdiag hmask nQ nK nq nr T CR QS RS E Lt Hn hT hcls hgoal j (hall j hj)
        (fun i hi => ih i hi (by omega))
  have := key (n - 1) (by omega)
  rw [hlast] at this
  exact csat_empty _ this

end sound

end RankNine
