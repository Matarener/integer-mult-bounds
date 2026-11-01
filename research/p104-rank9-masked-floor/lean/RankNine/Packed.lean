import RankNine.Moduli

/-!
# Bit-packed moduli certificates

All certificate data are lists of natural numbers (blocks of 256 fields of 16 bits), so that the kernel reads a
field with a short list walk and two GMP operations on a 4096-bit block (`>>>`, `%`).  The certificate lists every derived fact explicitly (`F`, two fields per fact), and each
step is checked locally against earlier facts (`stepOK`).  The local checks can be split into chunks.

Step `i` (five fields of `S`): tag `0` seed `(a, b, oa, ob)`, `1` prop `(a, o, k)`, `2` trans `(k, l)`, `3` symm `k`.
-/

namespace RankNine

variable {K : Type*} [Field K]

def fld (B : List ℕ) (k : ℕ) : ℕ := ((B.getD (k / 256) 0) >>> (16 * (k % 256))) % 65536

def relAt (R : List ℕ) (j : ℕ) : Rel := (fld R (4 * j), fld R (4 * j + 1), fld R (4 * j + 2), fld R (4 * j + 3))

def factAt (F : List ℕ) (i : ℕ) : ℕ × ℕ := (fld F (2 * i), fld F (2 * i + 1))

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


/-! ### Lattice seeds (step tag `4`)

A lattice seed derives `N u ^ 2 = N v ^ 2` from an integer combination of relations: the exponent vectors
`e_x + e_p - e_y - e_q` of the relations (all four codes covered, so `N ≠ 0` on them) with coefficients `c_i`
sum to `2 e_u - 2 e_v`.  The kernel compares the exponent sums code by code (`esum`); the proof multiplies the
relations (`mval`) and regroups the product by codes (`mval_group`).  Term `i` of `Lx` is two fields: relation
index and coefficient `+ 32768`. -/

/-- monomial `∏ w c ^ e` of a list of (code, exponent) -/
def mval (w : ℕ → K) : List (ℕ × ℤ) → K
  | [] => 1
  | t :: l => w t.1 ^ t.2 * mval w l

def esum (l : List (ℕ × ℤ)) (c : ℕ) : ℤ := (l.map fun t => if t.1 = c then t.2 else 0).sum

def relMono (r : Rel) : List (ℕ × ℤ) := [(r.1, 1), (r.2.1, 1), (r.2.2.1, -1), (r.2.2.2, -1)]

def tcoef (Lx : List ℕ) (i : ℕ) : ℤ := (fld Lx (2 * i + 1) : ℤ) - 32768

def latL (R Lx : List ℕ) (a m : ℕ) : List (ℕ × ℤ) :=
  (List.range' a m).flatMap fun i => (relMono (relAt R (fld Lx (2 * i)))).map fun t => (t.1, tcoef Lx i * t.2)

def latTermsOK (nR : ℕ) (R Lx : List ℕ) (Cv a m : ℕ) : Bool :=
  (List.range' a m).all fun i => decide (fld Lx (2 * i) < nR) &&
    (relMono (relAt R (fld Lx (2 * i)))).all fun t => covB Cv t.1

/-- insert a term into a sorted list of (code, exponent), merging equal codes and dropping zero exponents -/
def insT (t : ℕ × ℤ) : List (ℕ × ℤ) → List (ℕ × ℤ)
  | [] => if t.2 = 0 then [] else [t]
  | d :: r => if t.1 = d.1 then (if t.2 + d.2 = 0 then r else (d.1, t.2 + d.2) :: r)
      else if t.1 < d.1 then t :: d :: r else d :: insT t r

/-- normal form of a monomial (sorted, merged, no zero exponents) -/
def normL : List (ℕ × ℤ) → List (ℕ × ℤ)
  | [] => []
  | t :: l => insT t (normL l)

def latOK (nR : ℕ) (R Lx : List ℕ) (Cv a m u v : ℕ) : Bool :=
  latTermsOK nR R Lx Cv a m && covB Cv u && covB Cv v &&
    (normL (latL R Lx a m ++ [(u, -2), (v, 2)])).isEmpty

open Classical in
noncomputable def wN (N : ℕ → K) (c : ℕ) : K := if N c = 0 then 1 else N c

theorem wN_ne (N : ℕ → K) (c : ℕ) : wN N c ≠ 0 := by
  unfold wN; split_ifs with h
  · exact one_ne_zero
  · exact h

theorem wN_eq (N : ℕ → K) {c : ℕ} (h : N c ≠ 0) : wN N c = N c := by
  unfold wN; rw [if_neg h]

theorem mval_append (w : ℕ → K) (l1 l2 : List (ℕ × ℤ)) : mval w (l1 ++ l2) = mval w l1 * mval w l2 := by
  induction l1 with
  | nil => simp [mval]
  | cons t l ih => simp only [List.cons_append, mval, ih]; ring

theorem mval_insT (w : ℕ → K) (hw : ∀ c, w c ≠ 0) (t : ℕ × ℤ) :
    ∀ l, mval w (insT t l) = w t.1 ^ t.2 * mval w l
  | [] => by
    unfold insT
    by_cases h : t.2 = 0
    · rw [if_pos h, h, zpow_zero, one_mul]
    · rw [if_neg h]; simp [mval]
  | d :: r => by
    unfold insT
    by_cases h1 : t.1 = d.1
    · rw [if_pos h1]
      by_cases h2 : t.2 + d.2 = 0
      · rw [if_pos h2]
        simp only [mval]
        rw [← mul_assoc, h1, ← zpow_add₀ (hw _), h2, zpow_zero, one_mul]
      · rw [if_neg h2]
        simp only [mval]
        rw [h1, zpow_add₀ (hw _)]; ring
    · rw [if_neg h1]
      by_cases h3 : t.1 < d.1
      · rw [if_pos h3]; simp only [mval]
      · rw [if_neg h3]
        simp only [mval]
        rw [mval_insT w hw t r]; ring

theorem mval_normL (w : ℕ → K) (hw : ∀ c, w c ≠ 0) : ∀ l, mval w (normL l) = mval w l
  | [] => rfl
  | t :: l => by
    rw [normL, mval_insT w hw, mval_normL w hw l]
    rfl

theorem mval_of_norm (w : ℕ → K) (hw : ∀ c, w c ≠ 0) (l : List (ℕ × ℤ)) (h : (normL l).isEmpty = true) :
    mval w l = 1 := by
  rw [← mval_normL w hw l, List.isEmpty_iff.1 h]; rfl

theorem mval_scale (w : ℕ → K) (n : ℤ) (l : List (ℕ × ℤ)) :
    mval w (l.map fun t => (t.1, n * t.2)) = mval w l ^ n := by
  induction l with
  | nil => simp [mval]
  | cons t l ih =>
    simp only [List.map_cons, mval, ih]
    rw [mul_zpow, ← zpow_mul, mul_comm t.2 n]

theorem esum_cons (t : ℕ × ℤ) (l : List (ℕ × ℤ)) (c : ℕ) :
    esum (t :: l) c = (if t.1 = c then t.2 else 0) + esum l c := by
  simp [esum]

theorem mval_group (w : ℕ → K) (hw : ∀ c, w c ≠ 0) (l : List (ℕ × ℤ)) (S : Finset ℕ) (hS : ∀ t ∈ l, t.1 ∈ S) :
    mval w l = ∏ c ∈ S, w c ^ esum l c := by
  induction l with
  | nil => simp [mval, esum]
  | cons t l ih =>
    rw [mval, ih (fun t' ht' => hS t' (List.mem_cons_of_mem _ ht'))]
    have h1 : ∏ c ∈ S, w c ^ esum (t :: l) c =
        (∏ c ∈ S, w c ^ (if t.1 = c then t.2 else 0)) * ∏ c ∈ S, w c ^ esum l c := by
      rw [← Finset.prod_mul_distrib]
      refine Finset.prod_congr rfl (fun c _ => ?_)
      rw [esum_cons, zpow_add₀ (hw c)]
    rw [h1]
    congr 1
    rw [Finset.prod_eq_single t.1]
    · simp
    · intro b _ hb
      simp [Ne.symm hb]
    · intro h
      exact absurd (hS t List.mem_cons_self) h

theorem mval_rel (N : ℕ → K) (x p y q : ℕ) (h : N x * N p = N y * N q)
    (hx : N x ≠ 0) (hp : N p ≠ 0) (hy : N y ≠ 0) (hq : N q ≠ 0) :
    mval (wN N) (relMono (x, p, y, q)) = 1 := by
  simp only [relMono, mval, wN_eq N hx, wN_eq N hp, wN_eq N hy, wN_eq N hq, zpow_one, zpow_neg_one, mul_one]
  have hyq : N y * N q ≠ 0 := mul_ne_zero hy hq
  calc N x * (N p * ((N y)⁻¹ * (N q)⁻¹)) = (N x * N p) * (N y * N q)⁻¹ := by rw [mul_inv]; ring
    _ = 1 := by rw [h]; exact mul_inv_cancel₀ hyq

theorem latL_val (N : ℕ → K) (nR : ℕ) (R Lx : List ℕ) (Cv : ℕ) (hrel : ∀ j < nR, holds N (relAt R j))
    (hcov : ∀ c, covB Cv c = true → N c ≠ 0) :
    ∀ (m a : ℕ), latTermsOK nR R Lx Cv a m = true → mval (wN N) (latL R Lx a m) = 1 := by
  intro m
  induction m with
  | zero => intro a _; simp [latL, mval]
  | succ m ih =>
    intro a h
    unfold latTermsOK at h
    rw [List.range'_succ, List.all_cons, Bool.and_eq_true] at h
    obtain ⟨ha, h'⟩ := h
    have e : latL R Lx a (m + 1) = ((relMono (relAt R (fld Lx (2 * a)))).map fun t => (t.1, tcoef Lx a * t.2)) ++
        latL R Lx (a + 1) m := by
      simp only [latL, List.range'_succ, List.flatMap_cons]
    rw [e, mval_append, mval_scale, ih (a + 1) h', mul_one]
    rw [Bool.and_eq_true, decide_eq_true_eq] at ha
    obtain ⟨hj, hC⟩ := ha
    have hR := hrel _ hj
    generalize relAt R (fld Lx (2 * a)) = r at hR hC ⊢
    obtain ⟨x, p, y, q⟩ := r
    simp only [relMono, List.all_cons, List.all_nil, Bool.and_true, Bool.and_eq_true] at hC
    obtain ⟨cx, cp, cy, cq⟩ := hC
    rw [mval_rel N x p y q hR (hcov _ cx) (hcov _ cp) (hcov _ cy) (hcov _ cq), one_zpow]

theorem mval_tgt (N : ℕ → K) (u v : ℕ) (hu : N u ≠ 0) (hv : N v ≠ 0)
    (h : mval (wN N) [(u, 2), (v, -2)] = 1) : N u ^ 2 = N v ^ 2 := by
  simp only [mval, wN_eq N hu, wN_eq N hv, mul_one] at h
  have hv2 : N v ^ (2 : ℤ) ≠ 0 := zpow_ne_zero _ hv
  have h2 : N u ^ (2 : ℤ) = N v ^ (2 : ℤ) := by
    rw [zpow_neg, ← div_eq_mul_inv, div_eq_one_iff_eq hv2] at h
    exact h
  have c2 : ∀ a : K, a ^ (2 : ℤ) = a ^ (2 : ℕ) := fun a => by
    first
    | exact zpow_ofNat a 2
    | exact zpow_natCast a 2
    | norm_cast
  rw [c2, c2] at h2
  exact h2

theorem mval_tgt' (N : ℕ → K) (u v : ℕ) (hu : N u ≠ 0) (hv : N v ≠ 0)
    (h : mval (wN N) [(u, -2), (v, 2)] = 1) : N u ^ 2 = N v ^ 2 := by
  simp only [mval, wN_eq N hu, wN_eq N hv, mul_one] at h
  have h2 : N v ^ (2 : ℤ) = N u ^ (2 : ℤ) := by
    calc N v ^ (2 : ℤ) = N u ^ (2 : ℤ) * (N u ^ (-2 : ℤ) * N v ^ (2 : ℤ)) := by
          rw [← mul_assoc, ← zpow_add₀ hu]; norm_num
      _ = N u ^ (2 : ℤ) := by rw [h, mul_one]
  have c2 : ∀ a : K, a ^ (2 : ℤ) = a ^ (2 : ℕ) := fun a => by
    first
    | exact zpow_ofNat a 2
    | exact zpow_natCast a 2
    | norm_cast
  rw [c2, c2] at h2
  exact h2.symm

theorem latOK_sound (N : ℕ → K) (nR : ℕ) (R Lx : List ℕ) (Cv a m u v : ℕ) (hrel : ∀ j < nR, holds N (relAt R j))
    (hcov : ∀ c, covB Cv c = true → N c ≠ 0) (h : latOK nR R Lx Cv a m u v = true) : Fact N (u, v) := by
  unfold latOK at h
  rw [Bool.and_eq_true, Bool.and_eq_true, Bool.and_eq_true] at h
  obtain ⟨⟨⟨h1, hu⟩, hv⟩, h2⟩ := h
  have hval := latL_val N nR R Lx Cv hrel hcov m a h1
  have hT := mval_of_norm (wN N) (wN_ne N) _ h2
  rw [mval_append, hval, one_mul] at hT
  exact mval_tgt' N u v (hcov u hu) (hcov v hv) hT

def stepOK (nR : ℕ) (R S F Lx : List ℕ) (Cv i : ℕ) : Bool :=
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
  else if fld S (5 * i) = 3 then
    fld S (5 * i + 1) < i && symmOK (factAt F (fld S (5 * i + 1))) (factAt F i)
  else
    latOK nR R Lx Cv (fld S (5 * i + 1) + 65536 * fld S (5 * i + 2)) (fld S (5 * i + 3)) (factAt F i).1 (factAt F i).2

theorem stepOK_sound (N : ℕ → K) (nR : ℕ) (R S F Lx : List ℕ) (Cv : ℕ) (hrel : ∀ j < nR, holds N (relAt R j))
    (hcov : ∀ c, covB Cv c = true → N c ≠ 0) (i : ℕ) (hprev : ∀ k < i, Fact N (factAt F k))
    (h : stepOK nR R S F Lx Cv i = true) : Fact N (factAt F i) := by
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
  · exact latOK_sound N nR R Lx Cv _ _ _ _ hrel hcov h

/-- all steps below `n` pass the local check ⇒ all facts below `n` are true -/
theorem steps_sound (N : ℕ → K) (nR : ℕ) (R S F Lx : List ℕ) (Cv n : ℕ) (hrel : ∀ j < nR, holds N (relAt R j))
    (hcov : ∀ c, covB Cv c = true → N c ≠ 0) (h : ∀ i < n, stepOK nR R S F Lx Cv i = true) :
    ∀ i < n, Fact N (factAt F i) := by
  intro i
  induction i using Nat.strong_induction_on with
  | _ i ih =>
    intro hi
    exact stepOK_sound N nR R S F Lx Cv hrel hcov i (fun k hk => ih k hk (lt_trans hk hi)) (h i hi)

/-- chunked form: `(List.range' a m).all` checks, proved separately by `decide +kernel` -/
theorem all_range'_iff (P : ℕ → Bool) (a m : ℕ) :
    (List.range' a m).all P = true ↔ ∀ i, a ≤ i → i < a + m → P i = true := by
  simp only [List.all_eq_true, List.mem_range'_1]
  constructor
  · intro h i h1 h2; exact h i ⟨by omega, by omega⟩
  · rintro h i ⟨h1, h2⟩; exact h i h1 (by omega)

/-- code table entry `e` (3 fields of `T`): code `c`, class root `r`, fact pointer `f` (0 means `c = r`) -/
def tEntryOK (n : ℕ) (F T : List ℕ) (e : ℕ) : Bool :=
  if fld T (3 * e + 2) = 0 then fld T (3 * e) == fld T (3 * e + 1)
  else fld T (3 * e + 2) - 1 < n && factAt F (fld T (3 * e + 2) - 1) == (fld T (3 * e + 1), fld T (3 * e))

theorem tEntryOK_sound (N : ℕ → K) (n : ℕ) (F T : List ℕ) (e : ℕ) (hF : ∀ i < n, Fact N (factAt F i))
    (h : tEntryOK n F T e = true) : N (fld T (3 * e)) ^ 2 = N (fld T (3 * e + 1)) ^ 2 := by
  unfold tEntryOK at h
  split_ifs at h
  · simp only [beq_iff_eq] at h; rw [h]
  · simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at h
    obtain ⟨hl, he⟩ := h
    have := hF _ hl
    rw [he] at this
    exact this.symm

end RankNine
