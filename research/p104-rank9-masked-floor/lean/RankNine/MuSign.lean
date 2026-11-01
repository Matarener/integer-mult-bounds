import RankNine.SignSat

/-!
# T1 sign step with ordered (`μ`) parity facts

For the five framed types where the unordered sign model (`RankNine.SignSat`) is satisfiable, the sign step uses
the arc values `μ(x→y) = M x y / M x x` (arc code `104 x + y`).  For dead rows `t ⊥ s` and a frame inside the dead
set whose only lines not orthogonal to both are `a, b`, the frame expansion of `A t ⬝ B s = 0` gives the ordered
relation `μ(t→a) μ(a→s) = - μ(t→b) μ(b→s)` (`ord_core`), and `μ(x→y) μ(y→x) = N{x,y}`.  A parity fact is an
integer combination `∑ aᵢ rᵢ + ∑ cₑ symₑ` (ordered relations `rᵢ`, `symₑ = (x→y) + (y→x)`) whose exponent vanishes
on every arc; then `(-1)^(∑ aᵢ) ∏ Nₑ^cₑ = 1`, and since every `Nₑ` is `±1/4` or `±1/2` this gives
`∑_{cₑ odd} σₑ ≡ ∑ aᵢ (mod 2)` (`fact_parity`).  Each such fact enters the RUP certificate as the clauses that forbid
the sign patterns of the wrong parity (entry kind `5`).
-/

namespace RankNine

open Matrix

variable {K : Type*} [Field K]

/-! ## Arc values -/

/-- `μ(x→y) = M x y / M x x` on the arc code `104 x + y` -/
def muA (A B : ℕ → Fin 9 → K) (a : ℕ) : K := Mx A B (a / 104) (a % 104) / Mx A B (a / 104) (a / 104)

theorem muA_arc (A B : ℕ → Fin 9 → K) (x y : ℕ) (hy : y < 104) :
    muA A B (104 * x + y) = Mx A B x y / Mx A B x x := by
  have h1 : (104 * x + y) / 104 = x := by omega
  have h2 : (104 * x + y) % 104 = y := by omega
  unfold muA; rw [h1, h2]

theorem Mx_ne_of_Nq (A B : ℕ → Fin 9 → K) {x y : ℕ} (h : Nq A B x y ≠ 0) :
    Mx A B x y ≠ 0 ∧ Mx A B y x ≠ 0 := by
  unfold Nq at h
  constructor
  · intro h0; apply h; rw [h0, zero_mul, zero_div]
  · intro h0; apply h; rw [h0, mul_zero, zero_div]

theorem muA_ne (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0) {x y : ℕ} (hx : x < 104) (hy : y < 104)
    (h : Mx A B x y ≠ 0) : muA A B (104 * x + y) ≠ 0 := by
  rw [muA_arc A B x y hy]; exact div_ne_zero h (hdiag x hx)

/-- the ordered relation from the frame expansion -/
theorem ord_core (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (t s f ka kb : ℕ) (ht : t < 104) (hs : s < 104) (hka : ka < 8) (hkb : kb < 8) (hab : ka ≠ kb)
    (hZt : m.testBit t = true) (hts : orth t s = true)
    (hFZ : ∀ k < 8, m.testBit (frL f k) = true)
    (hoth : ∀ k < 8, k = ka ∨ k = kb ∨ orth t (frL f k) = true ∨ orth s (frL f k) = true) :
    muA A B (104 * t + frL f ka) * muA A B (104 * frL f ka + s) +
      muA A B (104 * t + frL f kb) * muA A B (104 * frL f kb + s) = 0 := by
  have hdead : ∀ k : Fin 8, A (frL f k) ⬝ᵥ u = 0 := fun k => hZ _ (hFZ k k.2)
  have hdF : ∀ k : Fin 8, A (frL f k) ⬝ᵥ B (frL f k) ≠ 0 := fun k => hdiag _ (frame_lt f k.2)
  have hoff : ∀ k l : Fin 8, k ≠ l → A (frL f k) ⬝ᵥ B (frL f l) = 0 := fun k l hkl =>
    hmask _ (frame_lt f k.2) _ (frame_lt f l.2) (frame_orth f k.2 l.2 (fun e => hkl (Fin.ext e)))
  have e1 : (0 : K) = ∑ k : Fin 8, A t ⬝ᵥ B (frL f k) * (A (frL f k) ⬝ᵥ B s) / (A (frL f k) ⬝ᵥ B (frL f k)) :=
    (hmask t ht s hs hts).symm.trans
      (frame_expansion A B u hu (fun k => frL f k) hdead hdF hoff t (hZ t hZt) s)
  have hne : (⟨ka, hka⟩ : Fin 8) ≠ ⟨kb, hkb⟩ := Fin.ne_of_val_ne hab
  have s1 : ∀ x : Fin 8, x ≠ ⟨ka, hka⟩ ∧ x ≠ ⟨kb, hkb⟩ →
      A t ⬝ᵥ B (frL f x) * (A (frL f x) ⬝ᵥ B s) / (A (frL f x) ⬝ᵥ B (frL f x)) = 0 := by
    intro x hx
    rcases hoth x x.2 with h | h | h | h
    · exact (hx.1 (Fin.ext h)).elim
    · exact (hx.2 (Fin.ext h)).elim
    · rw [hmask t ht _ (frame_lt f x.2) h, zero_mul, zero_div]
    · rw [hmask _ (frame_lt f x.2) s hs (by rw [orth_comm]; exact h), mul_zero, zero_div]
  rw [Fintype.sum_eq_add _ _ hne s1] at e1
  have e1' : (0 : K) = A t ⬝ᵥ B (frL f ka) * (A (frL f ka) ⬝ᵥ B s) / (A (frL f ka) ⬝ᵥ B (frL f ka)) +
      A t ⬝ᵥ B (frL f kb) * (A (frL f kb) ⬝ᵥ B s) / (A (frL f kb) ⬝ᵥ B (frL f kb)) := e1
  rw [muA_arc A B _ _ (frame_lt f hka), muA_arc A B _ _ hs, muA_arc A B _ _ (frame_lt f hkb), muA_arc A B _ _ hs]
  have key : Mx A B t (frL f ka) / Mx A B t t * (Mx A B (frL f ka) s / Mx A B (frL f ka) (frL f ka)) +
      Mx A B t (frL f kb) / Mx A B t t * (Mx A B (frL f kb) s / Mx A B (frL f kb) (frL f kb)) =
      (A t ⬝ᵥ B (frL f ka) * (A (frL f ka) ⬝ᵥ B s) / (A (frL f ka) ⬝ᵥ B (frL f ka)) +
        A t ⬝ᵥ B (frL f kb) * (A (frL f kb) ⬝ᵥ B s) / (A (frL f kb) ⬝ᵥ B (frL f kb))) / (A t ⬝ᵥ B t) := by
    unfold Mx; ring
  rw [key, ← e1', zero_div]

theorem mval_ord (f : ℕ → K) (p q r s : ℕ) (h : f p * f q + f r * f s = 0)
    (hp : f p ≠ 0) (hq : f q ≠ 0) (hr : f r ≠ 0) (hs : f s ≠ 0) :
    mval (wN f) [(p, 1), (q, 1), (r, -1), (s, -1)] = -1 := by
  simp only [mval, wN_eq f hp, wN_eq f hq, wN_eq f hr, wN_eq f hs, zpow_one, _root_.zpow_neg_one, mul_one]
  have hrs : f r * f s ≠ 0 := mul_ne_zero hr hs
  have h' : f p * f q = -(f r * f s) := by linear_combination h
  calc f p * (f q * ((f r)⁻¹ * (f s)⁻¹)) = (f p * f q) * (f r * f s)⁻¹ := by rw [mul_inv]; ring
    _ = -1 := by rw [h', neg_mul, mul_inv_cancel₀ hrs]

theorem mval_sym (f : ℕ → K) (p q : ℕ) (hp : f p ≠ 0) (hq : f q ≠ 0) :
    mval (wN f) [(p, 1), (q, 1)] = f p * f q := by
  simp only [mval, wN_eq f hp, wN_eq f hq, zpow_one, mul_one]

/-! ## Certificate tables

`OR`: ordered relation rows `t, s, f, ka, kb` (five fields).  `XO`: ordered terms (row, coefficient `+ 32768`).
`XS`: symmetric terms (moduli table entry `e` of the pair code, class `K`, coefficient `+ 32768`).  `XF`: facts,
seven fields `oa, oa', on, sa, sa', sn, L` (ordered terms `XO[oa + 65536 oa' …]`, symmetric terms
`XS[sa + 65536 sa' …]`, the first `L` symmetric terms have odd coefficients, the others even). -/

def orw (OR : List ℕ) (r k : ℕ) : ℕ := fld OR (5 * r + k)

def oArcs (OR : List ℕ) (r : ℕ) : List (ℕ × ℤ) :=
  [(104 * orw OR r 0 + frL (orw OR r 2) (orw OR r 3), 1), (104 * frL (orw OR r 2) (orw OR r 3) + orw OR r 1, 1),
    (104 * orw OR r 0 + frL (orw OR r 2) (orw OR r 4), -1), (104 * frL (orw OR r 2) (orw OR r 4) + orw OR r 1, -1)]

def sArcs (c : ℕ) : List (ℕ × ℤ) := [(c, 1), (104 * (c % 104) + c / 104, 1)]

def ocoef (XO : List ℕ) (i : ℕ) : ℤ := (fld XO (2 * i + 1) : ℤ) - 32768

def scoef (XS : List ℕ) (i : ℕ) : ℤ := (fld XS (3 * i + 2) : ℤ) - 32768

def scode (T XS : List ℕ) (i : ℕ) : ℕ := fld T (3 * fld XS (3 * i))

def xoL (OR XO : List ℕ) (a m : ℕ) : List (ℕ × ℤ) :=
  (List.range' a m).flatMap fun i => (oArcs OR (fld XO (2 * i))).map fun t => (t.1, ocoef XO i * t.2)

def xsL (T XS : List ℕ) (a m : ℕ) : List (ℕ × ℤ) :=
  (List.range' a m).flatMap fun i => (sArcs (scode T XS i)).map fun t => (t.1, scoef XS i * t.2)

def osum (XO : List ℕ) (a m : ℕ) : ℤ := ((List.range' a m).map (ocoef XO)).sum

def oTermOK (m Cv nO : ℕ) (OR XO : List ℕ) (i : ℕ) : Bool :=
  decide (fld XO (2 * i) < nO) &&
    relChk m (pcode (orw OR (fld XO (2 * i)) 0) (frL (orw OR (fld XO (2 * i)) 2) (orw OR (fld XO (2 * i)) 3)),
      pcode (orw OR (fld XO (2 * i)) 1) (frL (orw OR (fld XO (2 * i)) 2) (orw OR (fld XO (2 * i)) 3)),
      pcode (orw OR (fld XO (2 * i)) 0) (frL (orw OR (fld XO (2 * i)) 2) (orw OR (fld XO (2 * i)) 4)),
      pcode (orw OR (fld XO (2 * i)) 1) (frL (orw OR (fld XO (2 * i)) 2) (orw OR (fld XO (2 * i)) 4)))
      (orw OR (fld XO (2 * i)) 0) (orw OR (fld XO (2 * i)) 1) (orw OR (fld XO (2 * i)) 2)
      (orw OR (fld XO (2 * i)) 3) (orw OR (fld XO (2 * i)) 4) &&
    covB Cv (pcode (orw OR (fld XO (2 * i)) 0) (frL (orw OR (fld XO (2 * i)) 2) (orw OR (fld XO (2 * i)) 3))) &&
    covB Cv (pcode (orw OR (fld XO (2 * i)) 1) (frL (orw OR (fld XO (2 * i)) 2) (orw OR (fld XO (2 * i)) 3))) &&
    covB Cv (pcode (orw OR (fld XO (2 * i)) 0) (frL (orw OR (fld XO (2 * i)) 2) (orw OR (fld XO (2 * i)) 4))) &&
    covB Cv (pcode (orw OR (fld XO (2 * i)) 1) (frL (orw OR (fld XO (2 * i)) 2) (orw OR (fld XO (2 * i)) 4)))

def sTermOK (nQ nK Cv : ℕ) (T CR XS : List ℕ) (i : ℕ) : Bool :=
  decide (fld XS (3 * i) < nQ) && decide (fld XS (3 * i + 1) < nK) &&
    (fld T (3 * fld XS (3 * i) + 1) == fld CR (fld XS (3 * i + 1))) && decide (scode T XS i < TAG) &&
    covB Cv (scode T XS i)

def xfa (XF : List ℕ) (x k : ℕ) : ℕ := fld XF (7 * x + k)
def xOa (XF : List ℕ) (x : ℕ) : ℕ := xfa XF x 0 + 65536 * xfa XF x 1
def xSa (XF : List ℕ) (x : ℕ) : ℕ := xfa XF x 3 + 65536 * xfa XF x 4

def factOK (m nQ nK Cv nO : ℕ) (T CR OR XO XS XF : List ℕ) (x : ℕ) : Bool :=
  (List.range' (xOa XF x) (xfa XF x 2)).all (oTermOK m Cv nO OR XO) &&
    (List.range' (xSa XF x) (xfa XF x 5)).all (sTermOK nQ nK Cv T CR XS) &&
    decide (xfa XF x 6 ≤ xfa XF x 5) &&
    (List.range' (xSa XF x) (xfa XF x 6)).all (fun i => scoef XS i % 2 == 1) &&
    (List.range' (xSa XF x + xfa XF x 6) (xfa XF x 5 - xfa XF x 6)).all (fun i => scoef XS i % 2 == 0) &&
    (normL (xoL OR XO (xOa XF x) (xfa XF x 2) ++ xsL T XS (xSa XF x) (xfa XF x 5))).isEmpty

/-- the sign atoms of fact `x` (the pair codes with odd coefficient) -/
def xAtoms (T XS XF : List ℕ) (x : ℕ) : List ℕ := (List.range' (xSa XF x) (xfa XF x 6)).map (scode T XS)

def bsum (p : ℕ) : ℕ → ℕ
  | 0 => 0
  | n + 1 => p % 2 + bsum (p / 2) n

/-! ## Soundness of a parity fact -/

theorem range'_split (s m n : ℕ) : List.range' s (m + n) = List.range' s m ++ List.range' (s + m) n := by
  induction m generalizing s with
  | zero => simp
  | succ m ih =>
    rw [show m + 1 + n = (m + n) + 1 by omega, List.range'_succ, List.range'_succ, ih (s + 1),
      show s + 1 + m = s + (m + 1) by omega]
    rfl

theorem relChk_parts {m : ℕ} {r : Rel} {t s f ka kb : ℕ} (h : relChk m r t s f ka kb = true) :
    t < 104 ∧ s < 104 ∧ ka < 8 ∧ kb < 8 ∧ ka ≠ kb ∧ m.testBit t = true ∧ orth t s = true ∧
      (∀ k < 8, m.testBit (frL f k) = true) ∧
      (∀ k < 8, k = ka ∨ k = kb ∨ orth t (frL f k) = true ∨ orth s (frL f k) = true) := by
  simp only [relChk, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.mem_range,
    Bool.or_eq_true] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨ht, hs⟩, hka⟩, hkb⟩, hab⟩, hZt⟩, _⟩, hts⟩, hFZ⟩, hoth⟩, _⟩ := h
  refine ⟨ht, hs, hka, hkb, hab, hZt, orth_of_orthB ht hs hts, hFZ, ?_⟩
  intro k hk
  have hk' := frame_lt f hk
  have hk2 := hoth k hk
  by_cases e1 : k = ka
  · exact Or.inl e1
  by_cases e2 : k = kb
  · exact Or.inr (Or.inl e2)
  by_cases e3 : orthB t (frL f k) = true
  · exact Or.inr (Or.inr (Or.inl (orth_of_orthB ht hk' e3)))
  have e4 : orthB s (frL f k) = true := by tauto
  exact Or.inr (Or.inr (Or.inr (orth_of_orthB hs hk' e4)))

section sound

variable (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)

include hu hZ hdiag hmask in
theorem mval_oArcs (Cv nO : ℕ) (OR XO : List ℕ) (hcov : ∀ c, covB Cv c = true → Nc A B c ≠ 0) (i : ℕ)
    (h : oTermOK m Cv nO OR XO i = true) : mval (wN (muA A B)) (oArcs OR (fld XO (2 * i))) = -1 := by
  unfold oTermOK at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨⟨⟨⟨_, hrc⟩, c1⟩, c2⟩, c3⟩, c4⟩ := h
  generalize fld XO (2 * i) = r at hrc c1 c2 c3 c4 ⊢
  unfold oArcs
  generalize orw OR r 0 = t at hrc c1 c2 c3 c4 ⊢
  generalize orw OR r 1 = s at hrc c1 c2 c3 c4 ⊢
  generalize orw OR r 2 = f at hrc c1 c2 c3 c4 ⊢
  generalize orw OR r 3 = ka at hrc c1 c2 c3 c4 ⊢
  generalize orw OR r 4 = kb at hrc c1 c2 c3 c4 ⊢
  obtain ⟨ht, hs, hka, hkb, hab, hZt, hts, hFZ, hoth⟩ := relChk_parts hrc
  have hfa := frame_lt f hka
  have hfb := frame_lt f hkb
  have n1 := hcov _ c1; rw [Nc_code A B ht hfa] at n1
  have n2 := hcov _ c2; rw [Nc_code A B hs hfa] at n2
  have n3 := hcov _ c3; rw [Nc_code A B ht hfb] at n3
  have n4 := hcov _ c4; rw [Nc_code A B hs hfb] at n4
  exact mval_ord (muA A B) _ _ _ _
    (ord_core A B u hu m hZ hmask hdiag t s f ka kb ht hs hka hkb hab hZt hts hFZ hoth)
    (muA_ne A B hdiag ht hfa (Mx_ne_of_Nq A B n1).1) (muA_ne A B hdiag hfa hs (Mx_ne_of_Nq A B n2).2)
    (muA_ne A B hdiag ht hfb (Mx_ne_of_Nq A B n3).1) (muA_ne A B hdiag hfb hs (Mx_ne_of_Nq A B n4).2)

include hu hZ hdiag hmask in
theorem mval_xoL (Cv nO : ℕ) (OR XO : List ℕ) (hcov : ∀ c, covB Cv c = true → Nc A B c ≠ 0) :
    ∀ (n a : ℕ), (List.range' a n).all (oTermOK m Cv nO OR XO) = true →
      mval (wN (muA A B)) (xoL OR XO a n) = (-1 : K) ^ osum XO a n := by
  intro n
  induction n with
  | zero => intro a _; simp [xoL, osum, mval]
  | succ n ih =>
    intro a h
    rw [List.range'_succ, List.all_cons, Bool.and_eq_true] at h
    obtain ⟨ha, h'⟩ := h
    have e : xoL OR XO a (n + 1) = ((oArcs OR (fld XO (2 * a))).map fun t => (t.1, ocoef XO a * t.2)) ++
        xoL OR XO (a + 1) n := by
      simp only [xoL, List.range'_succ, List.flatMap_cons]
    have eo : osum XO a (n + 1) = ocoef XO a + osum XO (a + 1) n := by
      simp only [osum, List.range'_succ, List.map_cons, List.sum_cons]
    rw [e, mval_append, mval_scale, ih (a + 1) h', eo, zpow_add₀ (neg_ne_zero.2 one_ne_zero),
      mval_oArcs A B u hu m hZ hdiag hmask Cv nO OR XO hcov a ha]

/-- value of a symmetric term: `μ(x→y) μ(y→x) = N{x,y}` -/
theorem mval_sArcs (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0) (c : ℕ) (hc : c < TAG) (hN : Nc A B c ≠ 0) :
    mval (wN (muA A B)) (sArcs c) = Nc A B c := by
  have hx : c / 104 < 104 := by unfold TAG at hc; omega
  have hy : c % 104 < 104 := Nat.mod_lt _ (by norm_num)
  have hN' : Nq A B (c / 104) (c % 104) ≠ 0 := hN
  obtain ⟨m1, m2⟩ := Mx_ne_of_Nq A B hN'
  have hc' : 104 * (c / 104) + c % 104 = c := Nat.div_add_mod c 104
  have a1 : muA A B c ≠ 0 := by rw [← hc']; exact muA_ne A B hdiag hx hy m1
  have a2 : muA A B (104 * (c % 104) + c / 104) ≠ 0 := muA_ne A B hdiag hy hx m2
  unfold sArcs
  rw [mval_sym _ _ _ a1 a2, muA_arc A B _ _ hx]
  show Mx A B (c / 104) (c % 104) / Mx A B (c / 104) (c / 104) *
    (Mx A B (c % 104) (c / 104) / Mx A B (c % 104) (c % 104)) = Nq A B (c / 104) (c % 104)
  unfold Nq; ring

theorem mval_xsL (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0) (nQ nK Cv : ℕ) (T CR XS : List ℕ)
    (hcov : ∀ c, covB Cv c = true → Nc A B c ≠ 0) :
    ∀ (n a : ℕ), (List.range' a n).all (sTermOK nQ nK Cv T CR XS) = true →
      mval (wN (muA A B)) (xsL T XS a n) = ((List.range' a n).map fun i => Nc A B (scode T XS i) ^ scoef XS i).prod := by
  intro n
  induction n with
  | zero => intro a _; simp [xsL, mval]
  | succ n ih =>
    intro a h
    rw [List.range'_succ, List.all_cons, Bool.and_eq_true] at h
    obtain ⟨ha, h'⟩ := h
    have e : xsL T XS a (n + 1) = ((sArcs (scode T XS a)).map fun t => (t.1, scoef XS a * t.2)) ++
        xsL T XS (a + 1) n := by
      simp only [xsL, List.range'_succ, List.flatMap_cons]
    unfold sTermOK at ha
    simp only [Bool.and_eq_true, decide_eq_true_eq] at ha
    obtain ⟨⟨_, hT⟩, hc⟩ := ha
    rw [e, mval_append, mval_scale, ih (a + 1) h', mval_sArcs A B hdiag _ hT (hcov _ hc), List.range'_succ,
      List.map_cons, List.prod_cons]

end sound

/-! ## From the product to the sign parity (characteristic zero) -/

section parity

variable [CharZero K]

theorem neg_one_zpow_ne : ∀ n : ℤ, (-1 : K) ^ n ≠ 0 := fun n => zpow_ne_zero _ (neg_ne_zero.2 one_ne_zero)

/-- `x = ± q` with `q ∈ {1/4, 1/2}` -/
theorem sgn_split (x : K) (h : x ^ 2 = 1/16 ∨ x ^ 2 = 1/4) :
    ∃ q : ℚ, 0 < q ∧ x = (-1 : K) ^ (sgnN x : ℤ) * (q : K) := by
  have c1 : (1/4 : K) ≠ -1/4 := by norm_num
  have c2 : (1/4 : K) ≠ -1/2 := by norm_num
  have c3 : (1/2 : K) ≠ -1/4 := by norm_num
  have c4 : (1/2 : K) ≠ -1/2 := by norm_num
  rcases h with h | h
  · have hf : (x - 1/4) * (x + 1/4) = 0 := by linear_combination h
    rcases mul_eq_zero.1 hf with h1 | h1
    · have hx : x = 1/4 := by linear_combination h1
      refine ⟨1/4, by norm_num, ?_⟩
      have : sgnN x = 0 := by unfold sgnN; rw [if_neg]; rw [hx]; exact fun e => e.elim c1 c2
      rw [this, hx]; norm_num
    · have hx : x = -1/4 := by linear_combination h1
      refine ⟨1/4, by norm_num, ?_⟩
      have : sgnN x = 1 := by unfold sgnN; rw [if_pos (Or.inl hx)]
      rw [this, hx]; norm_num
  · have hf : (x - 1/2) * (x + 1/2) = 0 := by linear_combination h
    rcases mul_eq_zero.1 hf with h1 | h1
    · have hx : x = 1/2 := by linear_combination h1
      refine ⟨1/2, by norm_num, ?_⟩
      have : sgnN x = 0 := by unfold sgnN; rw [if_neg]; rw [hx]; exact fun e => e.elim c3 c4
      rw [this, hx]; norm_num
    · have hx : x = -1/2 := by linear_combination h1
      refine ⟨1/2, by norm_num, ?_⟩
      have : sgnN x = 1 := by unfold sgnN; rw [if_pos (Or.inr hx)]
      rw [this, hx]; norm_num

theorem sign_extract (g : ℕ → K) (kk : ℕ → ℤ) : ∀ L : List ℕ, (∀ i ∈ L, g i ^ 2 = 1/16 ∨ g i ^ 2 = 1/4) →
    ∃ Q : ℚ, 0 < Q ∧ (L.map fun i => g i ^ kk i).prod =
      (-1 : K) ^ ((L.map fun i => kk i * (sgnN (g i) : ℤ)).sum) * (Q : K) := by
  intro L
  induction L with
  | nil => intro _; exact ⟨1, one_pos, by simp⟩
  | cons i L ih =>
    intro hL
    obtain ⟨Q, hQ, e⟩ := ih (fun j hj => hL j (List.mem_cons_of_mem _ hj))
    obtain ⟨q, hq, ex⟩ := sgn_split (g i) (hL i List.mem_cons_self)
    refine ⟨q ^ kk i * Q, mul_pos (zpow_pos hq _) hQ, ?_⟩
    rw [List.map_cons, List.prod_cons, e, List.map_cons, List.sum_cons,
      zpow_add₀ (neg_ne_zero.2 one_ne_zero), Rat.cast_mul, Rat.cast_zpow]
    conv_lhs => rw [ex]
    rw [mul_zpow, ← _root_.zpow_mul, mul_comm ((sgnN (g i) : ℕ) : ℤ) (kk i)]
    ring

theorem even_of_prod (S : ℤ) (Q : ℚ) (hQ : 0 < Q) (h : (-1 : K) ^ S * (Q : K) = 1) : S % 2 = 0 := by
  rcases Int.even_or_odd S with he | ho
  · obtain ⟨r, hr⟩ := he; omega
  · exfalso
    rw [Odd.neg_one_zpow ho, neg_one_mul] at h
    have h2 : ((Q : ℚ) : K) = ((-1 : ℚ) : K) := by push_cast; linear_combination -h
    have h3 : Q = -1 := Rat.cast_injective h2
    rw [h3] at hQ; norm_num at hQ

theorem odd_coef_sum (kk : ℕ → ℤ) (σ : ℕ → ℕ) (hσ : ∀ i, σ i ≤ 1) :
    ∀ L : List ℕ, (∀ i ∈ L, kk i % 2 = 1) →
      ((L.map fun i => kk i * (σ i : ℤ)).sum - (((L.map σ).sum : ℕ) : ℤ)) % 2 = 0 := by
  intro L
  induction L with
  | nil => intro _; simp
  | cons i L ih =>
    intro hL
    have h1 := ih (fun j hj => hL j (List.mem_cons_of_mem _ hj))
    have h2 := hL i List.mem_cons_self
    simp only [List.map_cons, List.sum_cons, Nat.cast_add]
    rcases Nat.le_one_iff_eq_zero_or_eq_one.1 (hσ i) with e | e <;> rw [e] <;>
      simp only [Nat.cast_zero, Nat.cast_one, mul_zero, mul_one] <;> omega

theorem even_coef_sum (kk : ℕ → ℤ) (σ : ℕ → ℕ) (hσ : ∀ i, σ i ≤ 1) :
    ∀ L : List ℕ, (∀ i ∈ L, kk i % 2 = 0) → ((L.map fun i => kk i * (σ i : ℤ)).sum) % 2 = 0 := by
  intro L
  induction L with
  | nil => intro _; simp
  | cons i L ih =>
    intro hL
    have h1 := ih (fun j hj => hL j (List.mem_cons_of_mem _ hj))
    have h2 := hL i List.mem_cons_self
    simp only [List.map_cons, List.sum_cons]
    rcases Nat.le_one_iff_eq_zero_or_eq_one.1 (hσ i) with e | e <;> rw [e] <;>
      simp only [Nat.cast_zero, Nat.cast_one, mul_zero, mul_one] <;> omega

theorem patMatch_sum : ∀ (vs : List ℕ) (p : ℕ), patMatch vs p = true → vs.sum = bsum p vs.length := by
  intro vs
  induction vs with
  | nil => intro p _; rfl
  | cons v vs ih =>
    intro p h
    simp only [patMatch, Bool.and_eq_true, beq_iff_eq] at h
    simp only [List.sum_cons, List.length_cons, bsum]
    rw [ih _ h.2, h.1]

/-- a checked fact: the odd-coefficient signs have the parity of the ordered coefficients -/
theorem fact_parity (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (nQ nK Cv nO : ℕ)
    (T CR OR XO XS XF : List ℕ) (hcov : ∀ c, covB Cv c = true → Nc A B c ≠ 0)
    (hT : ∀ e < nQ, Nc A B (fld T (3 * e)) ^ 2 = Nc A B (fld T (3 * e + 1)) ^ 2)
    (hcls : ∀ c < nK, Nc A B (fld CR c) ^ 2 = 1/16 ∨ Nc A B (fld CR c) ^ 2 = 1/4) (x : ℕ)
    (h : factOK m nQ nK Cv nO T CR OR XO XS XF x = true) :
    (osum XO (xOa XF x) (xfa XF x 2) +
      ((((xAtoms T XS XF x).map fun c => sgnN (Nc A B c)).sum : ℕ) : ℤ)) % 2 = 0 := by
  unfold factOK at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨⟨⟨⟨ho, hs⟩, hL⟩, hodd⟩, hev⟩, hz⟩ := h
  set oa := xOa XF x
  set on := xfa XF x 2
  set sa := xSa XF x
  set sn := xfa XF x 5
  set L := xfa XF x 6
  set l := xoL OR XO oa on ++ xsL T XS sa sn
  -- the whole monomial is 1
  have h1 : mval (wN (muA A B)) l = 1 := mval_of_norm _ (wN_ne _) l hz
  rw [mval_append, mval_xoL A B u hu m hZ hdiag hmask Cv nO OR XO hcov on oa ho,
    mval_xsL A B hdiag nQ nK Cv T CR XS hcov sn sa hs] at h1
  -- every symmetric term has square 1/16 or 1/4
  have hsq : ∀ i ∈ List.range' sa sn, Nc A B (scode T XS i) ^ 2 = 1/16 ∨ Nc A B (scode T XS i) ^ 2 = 1/4 := by
    intro i hi
    rw [List.all_eq_true] at hs
    have := hs i hi
    unfold sTermOK at this
    simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at this
    obtain ⟨⟨⟨⟨he, hk⟩, hr⟩, _⟩, _⟩ := this
    unfold scode
    rw [hT _ he, hr]
    exact hcls _ hk
  obtain ⟨Q, hQ, eQ⟩ := sign_extract (fun i => Nc A B (scode T XS i)) (scoef XS) _ hsq
  beta_reduce at eQ
  rw [eQ, ← mul_assoc, ← zpow_add₀ (neg_ne_zero.2 one_ne_zero)] at h1
  have hp := even_of_prod _ Q hQ h1
  -- split the symmetric terms into the odd ones and the even ones
  have hsplit := range'_split sa L (sn - L)
  rw [show L + (sn - L) = sn by omega] at hsplit
  rw [hsplit, List.map_append, List.sum_append] at hp
  have hσ : ∀ i, (fun i => sgnN (Nc A B (scode T XS i))) i ≤ 1 := fun i => sgnN_le _
  have ho' := odd_coef_sum (scoef XS) (fun i => sgnN (Nc A B (scode T XS i))) hσ (List.range' sa L) (fun i hi => by
    rw [List.all_eq_true] at hodd
    have := hodd i hi
    rw [beq_iff_eq] at this
    exact this)
  have he' := even_coef_sum (scoef XS) (fun i => sgnN (Nc A B (scode T XS i))) hσ (List.range' (sa + L) (sn - L))
    (fun i hi => by
      rw [List.all_eq_true] at hev
      have := hev i hi
      rw [beq_iff_eq] at this
      exact this)
  have hat : (xAtoms T XS XF x).map (fun c => sgnN (Nc A B c)) =
      (List.range' sa L).map (fun i => sgnN (Nc A B (scode T XS i))) := by
    unfold xAtoms; rw [List.map_map]; rfl
  rw [hat]
  beta_reduce at ho' he'
  omega

end parity

/-! ## Certificate entries with parity facts (kind `5`) -/

/-- clause of entry `j`: kind `5` forbids the sign pattern `p` on the atoms of fact `x` -/
def mClAt (nK : ℕ) (T QS RS E Lt XS XF : List ℕ) (j : ℕ) : ℕ × ℕ :=
  if sf E j 0 = 5 then patCl (xAtoms T XS XF (sf E j 1)) (sf E j 2) else sClAt nK T QS RS E Lt j

def mEntryOK (m nQ nK nq nr Cv nO nX : ℕ) (T CR QS RS E Lt Hn OR XO XS XF : List ℕ) (j : ℕ) : Bool :=
  if sf E j 0 = 5 then
    decide (sf E j 1 < nX) &&
      decide (((bsum (sf E j 2) (xfa XF (sf E j 1) 6) : ℕ) + osum XO (xOa XF (sf E j 1)) (xfa XF (sf E j 1) 2)) % 2 = 1)
  else if sf E j 0 = 0 ∨ sf E j 0 = 1 ∨ sf E j 0 = 2 ∨ sf E j 0 = 3 then
    sEntryOK m nQ nK nq nr T CR QS RS E Lt Hn j
  else
    (hint3 Hn (sf E j 4 + 65536 * sf E j 5) (sf E j 6)).all (fun h => decide (h.1 < j)) &&
      rupRun (mClAt nK T QS RS E Lt XS XF) (hint3 Hn (sf E j 4 + 65536 * sf E j 5) (sf E j 6))
        (mClAt nK T QS RS E Lt XS XF j).2 (mClAt nK T QS RS E Lt XS XF j).1

section msound

variable [CharZero K]

theorem mentry_sound (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (nQ nK nq nr Cv nO nX : ℕ)
    (T CR QS RS E Lt Hn OR XO XS XF : List ℕ) (hcov : ∀ c, covB Cv c = true → Nc A B c ≠ 0)
    (hT : ∀ e < nQ, Nc A B (fld T (3 * e)) ^ 2 = Nc A B (fld T (3 * e + 1)) ^ 2)
    (hcls : ∀ c < nK, Nc A B (fld CR c) ^ 2 = 1/16 ∨ Nc A B (fld CR c) ^ 2 = 1/4)
    (hfact : ∀ x < nX, factOK m nQ nK Cv nO T CR OR XO XS XF x = true)
    (hgoal : ∃ c < nK, magN (Nc A B (fld CR c)) ≠ 0) (j : ℕ)
    (hok : mEntryOK m nQ nK nq nr Cv nO nX T CR QS RS E Lt Hn OR XO XS XF j = true)
    (hprev : ∀ i < j, CSat (zS A B CR) (mClAt nK T QS RS E Lt XS XF i)) :
    CSat (zS A B CR) (mClAt nK T QS RS E Lt XS XF j) := by
  unfold mEntryOK at hok
  by_cases k5 : sf E j 0 = 5
  · rw [if_pos k5] at hok
    unfold mClAt; rw [if_pos k5]
    simp only [Bool.and_eq_true, decide_eq_true_eq] at hok
    obtain ⟨hx, hpar⟩ := hok
    have hf := hfact _ hx
    have hfp := fact_parity A B u hu m hZ hdiag hmask nQ nK Cv nO T CR OR XO XS XF hcov hT hcls _ hf
    have hlt : ∀ c ∈ xAtoms T XS XF (sf E j 1), c < TAG := by
      intro c hc
      unfold xAtoms at hc
      obtain ⟨i, hi, rfl⟩ := List.mem_map.1 hc
      unfold factOK at hf
      simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true] at hf
      obtain ⟨⟨⟨⟨⟨_, hs⟩, hL⟩, _⟩, _⟩, _⟩ := hf
      have hi' : i ∈ List.range' (xSa XF (sf E j 1)) (xfa XF (sf E j 1) 5) := by
        rw [List.mem_range'_1] at hi ⊢; omega
      have := hs i hi'
      unfold sTermOK at this
      simp only [Bool.and_eq_true, decide_eq_true_eq] at this
      exact this.1.2
    let l : List (ℕ × ℕ) := (xAtoms T XS XF (sf E j 1)).map fun c => (c, sgnN (Nc A B c))
    have hfst : l.map Prod.fst = xAtoms T XS XF (sf E j 1) := by
      simp only [l, List.map_map]; exact List.map_id _
    rw [← hfst]
    refine patCl_sound (zS A B CR) l _ ?_ ?_
    · intro t ht
      obtain ⟨c, hc, rfl⟩ := List.mem_map.1 ht
      exact ⟨sgnN_le _, zS_code A B CR (hlt c hc)⟩
    · by_contra hm
      rw [Bool.not_eq_false] at hm
      have hs := patMatch_sum _ _ hm
      have hlen : (l.map Prod.snd).length = xfa XF (sf E j 1) 6 := by
        simp [l, xAtoms, List.length_map, List.length_range']
      rw [hlen] at hs
      have hsnd : l.map Prod.snd = (xAtoms T XS XF (sf E j 1)).map fun c => sgnN (Nc A B c) := by
        simp [l, List.map_map]
      rw [hsnd] at hs
      rw [hs] at hfp
      omega
  · rw [if_neg k5] at hok
    unfold mClAt; rw [if_neg k5]
    by_cases kb : sf E j 0 = 0 ∨ sf E j 0 = 1 ∨ sf E j 0 = 2 ∨ sf E j 0 = 3
    · rw [if_pos kb] at hok
      refine sentry_sound A B u hu m hZ hdiag hmask nQ nK nq nr T CR QS RS E Lt Hn hT hcls hgoal j hok ?_
      intro hn
      exfalso
      rcases kb with e | e | e | e
      · exact hn.1 e
      · exact hn.2.1 e
      · exact hn.2.2.1 e
      · exact hn.2.2.2 e
    · rw [if_neg kb] at hok
      simp only [Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq] at hok
      obtain ⟨hlt, hrup⟩ := hok
      have h := rup_sound (zS A B CR) (mClAt nK T QS RS E Lt XS XF) (mClAt nK T QS RS E Lt XS XF j) _
        (fun h hh => hprev h.1 (hlt h hh)) hrup
      unfold mClAt at h
      rw [if_neg k5] at h
      exact h

theorem mu_sound (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (nQ nK nq nr Cv nO nX : ℕ)
    (T CR QS RS CQ E Lt Hn OR XO XS XF : List ℕ) (n : ℕ) (hcov : ∀ c, covB Cv c = true → Nc A B c ≠ 0)
    (hT : ∀ e < nQ, Nc A B (fld T (3 * e)) ^ 2 = Nc A B (fld T (3 * e + 1)) ^ 2)
    (hcq : ∀ c < nK, cqOK m nQ nK T CR QS CQ nq c = true)
    (hfact : ∀ x < nX, factOK m nQ nK Cv nO T CR OR XO XS XF x = true)
    (hall : ∀ j < n, mEntryOK m nQ nK nq nr Cv nO nX T CR QS RS E Lt Hn OR XO XS XF j = true)
    (hlast : mClAt nK T QS RS E Lt XS XF (n - 1) = (0, 0)) (hn : 0 < n) :
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
  have key : ∀ j, j < n → CSat (zS A B CR) (mClAt nK T QS RS E Lt XS XF j) := by
    intro j
    induction j using Nat.strong_induction_on with
    | _ j ih =>
      intro hj
      exact mentry_sound A B u hu m hZ hdiag hmask nQ nK nq nr Cv nO nX T CR QS RS E Lt Hn OR XO XS XF hcov hT hcls
        hfact hgoal j (hall j hj) (fun i hi => ih i hi (by omega))
  have := key (n - 1) (by omega)
  rw [hlast] at this
  exact csat_empty _ this

end msound

end RankNine
