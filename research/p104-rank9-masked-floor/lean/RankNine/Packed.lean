import RankNine.Moduli

/-!
# Bit-packed moduli certificates

All certificate data are single natural numbers with 16-bit fields, so that the kernel reads a field with two
GMP operations (`>>>`, `%`).  The certificate lists every derived fact explicitly (`F`, two fields per fact), and each
step is checked locally against earlier facts (`stepOK`).  The local checks can be split into chunks.

Step `i` (five fields of `S`): tag `0` seed `(a, b, oa, ob)`, `1` prop `(a, o, k)`, `2` trans `(k, l)`, `3` symm `k`.
-/

namespace RankNine

variable {K : Type*} [Field K]

def fld (B k : ℕ) : ℕ := (B >>> (16 * k)) % 65536

def relAt (R j : ℕ) : Rel := (fld R (4 * j), fld R (4 * j + 1), fld R (4 * j + 2), fld R (4 * j + 3))

def factAt (F i : ℕ) : ℕ × ℕ := (fld F (2 * i), fld F (2 * i + 1))

def covB (Cv c : ℕ) : Bool := (Cv >>> c) % 2 == 1

def seedOK (Cv : ℕ) (r1 r2 : Rel) (f : ℕ × ℕ) : Bool :=
  r2 == (r1.1, r1.2.2.2, r1.2.2.1, r1.2.1) && covB Cv r1.2.1 && covB Cv r1.2.2.2 && f == (r1.1, r1.2.2.1)

def propOK (Cv : ℕ) (r1 : Rel) (g f : ℕ × ℕ) : Bool :=
  g == (r1.1, r1.2.2.1) && covB Cv r1.1 && f == (r1.2.1, r1.2.2.2)

def transOK (g h f : ℕ × ℕ) : Bool := h.1 == g.2 && f == (g.1, h.2)

def symmOK (g f : ℕ × ℕ) : Bool := f == (g.2, g.1)

theorem seed_core {x p y q : K} (hp : p ≠ 0) (hq : q ≠ 0) (h1 : x * p = y * q) (h2 : x * q = y * p) :
    x ^ 2 = y ^ 2 := by
  have : x ^ 2 * (p * q) = y ^ 2 * (p * q) := by
    calc x ^ 2 * (p * q) = (x * p) * (x * q) := by ring
      _ = (y * q) * (y * p) := by rw [h1, h2]
      _ = y ^ 2 * (p * q) := by ring
  exact mul_right_cancel₀ (mul_ne_zero hp hq) this

theorem seedOK_sound (N : ℕ → K) (Cv : ℕ) (hcov : ∀ c, covB Cv c = true → N c ≠ 0) (r1 r2 : Rel) (f : ℕ × ℕ)
    (H1 : holds N r1) (H2 : holds N r2) (h : seedOK Cv r1 r2 f = true) : Fact N f := by
  obtain ⟨x, p, y, q⟩ := r1
  obtain ⟨x', q', y', p'⟩ := r2
  simp only [seedOK, Bool.and_eq_true, beq_iff_eq, Prod.mk.injEq] at h
  obtain ⟨⟨⟨⟨e1, e2, e3, e4⟩, cp⟩, cq⟩, ef⟩ := h
  subst ef
  simp only [holds] at H1 H2
  rw [e1, e2, e3, e4] at H2
  exact seed_core (hcov _ cp) (hcov _ cq) H1 H2

theorem propOK_sound (N : ℕ → K) (Cv : ℕ) (hcov : ∀ c, covB Cv c = true → N c ≠ 0) (r1 : Rel) (g f : ℕ × ℕ)
    (H1 : holds N r1) (hg : Fact N g) (h : propOK Cv r1 g f = true) : Fact N f := by
  obtain ⟨x, p, y, q⟩ := r1
  simp only [propOK, Bool.and_eq_true, beq_iff_eq] at h
  obtain ⟨⟨eg, cx⟩, ef⟩ := h
  subst eg; subst ef
  simp only [holds] at H1
  simp only [Fact] at hg ⊢
  exact propagate (hcov _ cx) hg H1

theorem transOK_sound (N : ℕ → K) (g h f : ℕ × ℕ) (hg : Fact N g) (hh : Fact N h)
    (hc : transOK g h f = true) : Fact N f := by
  obtain ⟨u, v⟩ := g; obtain ⟨v', w⟩ := h
  simp only [transOK, Bool.and_eq_true, beq_iff_eq] at hc
  obtain ⟨e, ef⟩ := hc
  subst ef
  simp only [Fact] at hg hh ⊢
  rw [e] at hh
  exact hg.trans hh

theorem symmOK_sound (N : ℕ → K) (g f : ℕ × ℕ) (hg : Fact N g) (hc : symmOK g f = true) : Fact N f := by
  obtain ⟨u, v⟩ := g
  simp only [symmOK, beq_iff_eq] at hc
  subst hc
  simp only [Fact] at hg ⊢
  exact hg.symm

def stepOK (nR R S F Cv i : ℕ) : Bool :=
  if fld S (5 * i) = 0 then
    fld S (5 * i + 1) < nR && fld S (5 * i + 2) < nR &&
      seedOK Cv (orient (fld S (5 * i + 3)) (relAt R (fld S (5 * i + 1))))
        (orient (fld S (5 * i + 4)) (relAt R (fld S (5 * i + 2)))) (factAt F i)
  else if fld S (5 * i) = 1 then
    fld S (5 * i + 1) < nR && fld S (5 * i + 3) < i &&
      propOK Cv (orient (fld S (5 * i + 2)) (relAt R (fld S (5 * i + 1)))) (factAt F (fld S (5 * i + 3))) (factAt F i)
  else if fld S (5 * i) = 2 then
    fld S (5 * i + 1) < i && fld S (5 * i + 2) < i &&
      transOK (factAt F (fld S (5 * i + 1))) (factAt F (fld S (5 * i + 2))) (factAt F i)
  else
    fld S (5 * i + 1) < i && symmOK (factAt F (fld S (5 * i + 1))) (factAt F i)

theorem stepOK_sound (N : ℕ → K) (nR R S F Cv : ℕ) (hrel : ∀ j < nR, holds N (relAt R j))
    (hcov : ∀ c, covB Cv c = true → N c ≠ 0) (i : ℕ) (hprev : ∀ k < i, Fact N (factAt F k))
    (h : stepOK nR R S F Cv i = true) : Fact N (factAt F i) := by
  unfold stepOK at h
  split_ifs at h
  · simp only [Bool.and_eq_true, decide_eq_true_eq] at h
    obtain ⟨⟨ha, hb⟩, hs⟩ := h
    exact seedOK_sound N Cv hcov _ _ _ (orient_holds N _ _ (hrel _ ha)) (orient_holds N _ _ (hrel _ hb)) hs
  · simp only [Bool.and_eq_true, decide_eq_true_eq] at h
    obtain ⟨⟨ha, hk⟩, hs⟩ := h
    exact propOK_sound N Cv hcov _ _ _ (orient_holds N _ _ (hrel _ ha)) (hprev _ hk) hs
  · simp only [Bool.and_eq_true, decide_eq_true_eq] at h
    obtain ⟨⟨hk, hl⟩, hs⟩ := h
    exact transOK_sound N _ _ _ (hprev _ hk) (hprev _ hl) hs
  · simp only [Bool.and_eq_true, decide_eq_true_eq] at h
    obtain ⟨hk, hs⟩ := h
    exact symmOK_sound N _ _ (hprev _ hk) hs

/-- all steps below `n` pass the local check ⇒ all facts below `n` are true -/
theorem steps_sound (N : ℕ → K) (nR R S F Cv n : ℕ) (hrel : ∀ j < nR, holds N (relAt R j))
    (hcov : ∀ c, covB Cv c = true → N c ≠ 0) (h : ∀ i < n, stepOK nR R S F Cv i = true) :
    ∀ i < n, Fact N (factAt F i) := by
  intro i
  induction i using Nat.strong_induction_on with
  | _ i ih =>
    intro hi
    exact stepOK_sound N nR R S F Cv hrel hcov i (fun k hk => ih k hk (lt_trans hk hi)) (h i hi)

/-- chunked form: `(List.range' a m).all` checks, proved separately by `decide +kernel` -/
theorem all_range'_iff (P : ℕ → Bool) (a m : ℕ) :
    (List.range' a m).all P = true ↔ ∀ i, a ≤ i → i < a + m → P i = true := by
  simp only [List.all_eq_true, List.mem_range'_1]
  constructor
  · intro h i h1 h2; exact h i ⟨by omega, by omega⟩
  · rintro h i ⟨h1, h2⟩; exact h i h1 (by omega)

/-- quadruple `q` (9 fields of `Q`): root `r`, then four (code, fact pointer); pointer 0 means the code is `r` -/
def qEntryOK (n F Q q j : ℕ) : Bool :=
  if fld Q (9 * q + 2 + 2 * j) = 0 then fld Q (9 * q + 1 + 2 * j) == fld Q (9 * q)
  else fld Q (9 * q + 2 + 2 * j) - 1 < n &&
    factAt F (fld Q (9 * q + 2 + 2 * j) - 1) == (fld Q (9 * q), fld Q (9 * q + 1 + 2 * j))

theorem qEntryOK_sound (N : ℕ → K) (n F Q q j : ℕ) (hF : ∀ i < n, Fact N (factAt F i))
    (h : qEntryOK n F Q q j = true) : N (fld Q (9 * q + 1 + 2 * j)) ^ 2 = N (fld Q (9 * q)) ^ 2 := by
  unfold qEntryOK at h
  split_ifs at h
  · simp only [beq_iff_eq] at h; rw [h]
  · simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at h
    obtain ⟨hl, he⟩ := h
    have := hF _ hl
    rw [he] at this
    exact this.symm

end RankNine
