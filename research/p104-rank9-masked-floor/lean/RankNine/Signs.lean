import RankNine.Link

/-!
# T1 sign step (frame sums and an F2 certificate)

For a dead row `t` and a frame `F` inside the dead set, the frame expansion of `M t t` gives the frame sum
`Σ_k N{t, F k} = 1`; the four lines of `F` not orthogonal to `t` carry the whole sum (`quad_sum`).  If the four
values have equal squares `c²` (moduli step), then over a field of characteristic 0 either `c² = 1/16` and all four
are `1/4`, or `c² = 1/4` and exactly an odd number are negative (`quad_val`).  All values are then in
`{±1/4, ±1/2}`, and a relation `a b = c d` between such values has an even number of negative factors (`rel_sgn`).
These are linear equations over F2 for the sign bits `sgnN` and the magnitude bits `magN`; an XOR certificate per
class forces every magnitude bit to 0, hence `N = 1/4` on every quadruple.  The F2 bookkeeping is done with bit masks
(`par`, `par_xor`).
-/

namespace RankNine

open Matrix

variable {K : Type*} [Field K]

theorem frame_sum (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (t f : ℕ) (ht : t < 104) (hZt : m.testBit t = true) (hFZ : ∀ k < 8, m.testBit (frL f k) = true) :
    ∑ k : Fin 8, Nq A B t (frL f k) = 1 := by
  have hdead : ∀ k : Fin 8, A (frL f k) ⬝ᵥ u = 0 := fun k => hZ _ (hFZ k k.2)
  have hdF : ∀ k : Fin 8, A (frL f k) ⬝ᵥ B (frL f k) ≠ 0 := fun k => hdiag _ (frame_lt f k.2)
  have hoff : ∀ k l : Fin 8, k ≠ l → A (frL f k) ⬝ᵥ B (frL f l) = 0 := fun k l hkl =>
    hmask _ (frame_lt f k.2) _ (frame_lt f l.2) (frame_orth f k.2 l.2 (fun e => hkl (Fin.ext e)))
  have e : A t ⬝ᵥ B t = ∑ k : Fin 8, A t ⬝ᵥ B (frL f k) * (A (frL f k) ⬝ᵥ B t) / (A (frL f k) ⬝ᵥ B (frL f k)) :=
    frame_expansion A B u hu (fun k => frL f k) hdead hdF hoff t (hZ t hZt) t
  have h2 : ∑ k : Fin 8, Nq A B t (frL f k) =
      (∑ k : Fin 8, A t ⬝ᵥ B (frL f k) * (A (frL f k) ⬝ᵥ B t) / (A (frL f k) ⬝ᵥ B (frL f k))) / (A t ⬝ᵥ B t) := by
    rw [Finset.sum_div]
    refine Finset.sum_congr rfl fun k _ => ?_
    unfold Nq Mx
    ring
  rw [h2, ← e, div_self (hdiag t ht)]

theorem quad_sum (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (t f k1 k2 k3 k4 : ℕ) (ht : t < 104) (hZt : m.testBit t = true) (hFZ : ∀ k < 8, m.testBit (frL f k) = true)
    (h1 : k1 < 8) (h2 : k2 < 8) (h3 : k3 < 8) (h4 : k4 < 8)
    (d12 : k1 ≠ k2) (d13 : k1 ≠ k3) (d14 : k1 ≠ k4) (d23 : k2 ≠ k3) (d24 : k2 ≠ k4) (d34 : k3 ≠ k4)
    (hrest : ∀ k < 8, k = k1 ∨ k = k2 ∨ k = k3 ∨ k = k4 ∨ orth t (frL f k) = true) :
    Nq A B t (frL f k1) + Nq A B t (frL f k2) + Nq A B t (frL f k3) + Nq A B t (frL f k4) = 1 := by
  have hsum := frame_sum A B u hu m hZ hdiag hmask t f ht hZt hFZ
  have n1 : (⟨k1, h1⟩ : Fin 8) ∉ ({⟨k2, h2⟩, ⟨k3, h3⟩, ⟨k4, h4⟩} : Finset (Fin 8)) := by
    simp only [Finset.mem_insert, Finset.mem_singleton, not_or]
    exact ⟨Fin.ne_of_val_ne d12, Fin.ne_of_val_ne d13, Fin.ne_of_val_ne d14⟩
  have n2 : (⟨k2, h2⟩ : Fin 8) ∉ ({⟨k3, h3⟩, ⟨k4, h4⟩} : Finset (Fin 8)) := by
    simp only [Finset.mem_insert, Finset.mem_singleton, not_or]
    exact ⟨Fin.ne_of_val_ne d23, Fin.ne_of_val_ne d24⟩
  have n3 : (⟨k3, h3⟩ : Fin 8) ∉ ({⟨k4, h4⟩} : Finset (Fin 8)) := by
    simp only [Finset.mem_singleton]
    exact Fin.ne_of_val_ne d34
  have hz : ∀ x ∈ (Finset.univ : Finset (Fin 8)),
      x ∉ ({⟨k1, h1⟩, ⟨k2, h2⟩, ⟨k3, h3⟩, ⟨k4, h4⟩} : Finset (Fin 8)) → Nq A B t (frL f x) = 0 := by
    intro x _ hx
    simp only [Finset.mem_insert, Finset.mem_singleton, not_or] at hx
    rcases hrest x x.2 with h | h | h | h | h
    · exact (hx.1 (Fin.ext h)).elim
    · exact (hx.2.1 (Fin.ext h)).elim
    · exact (hx.2.2.1 (Fin.ext h)).elim
    · exact (hx.2.2.2 (Fin.ext h)).elim
    · unfold Nq Mx
      rw [hmask t ht _ (frame_lt f x.2) h, zero_mul, zero_div]
  have hs : Nq A B t (frL f k1) + (Nq A B t (frL f k2) + (Nq A B t (frL f k3) + Nq A B t (frL f k4))) =
      ∑ k : Fin 8, Nq A B t (frL f k) := by
    (rw [← Finset.sum_subset (Finset.subset_univ _) hz, Finset.sum_insert n1, Finset.sum_insert n2,
      Finset.sum_insert n3, Finset.sum_singleton]) <;> rfl
  linear_combination hs + hsum

section values

variable [CharZero K]

open Classical in
/-- sign bit of a value in `{±1/4, ±1/2}` -/
noncomputable def sgnN (x : K) : ℕ := if x = -1/4 ∨ x = -1/2 then 1 else 0

open Classical in
/-- magnitude bit: `1` iff `x² = 1/4` -/
noncomputable def magN (x : K) : ℕ := if x ^ 2 = 1/4 then 1 else 0

theorem magN_le (x : K) : magN x ≤ 1 := by unfold magN; split_ifs <;> omega

theorem magN_of_sq {x c : K} (h : x ^ 2 = c ^ 2) : magN x = magN c := by unfold magN; rw [h]

theorem quad_val {c x1 x2 x3 x4 : K} (h1 : x1 ^ 2 = c ^ 2) (h2 : x2 ^ 2 = c ^ 2) (h3 : x3 ^ 2 = c ^ 2)
    (h4 : x4 ^ 2 = c ^ 2) (hs : x1 + x2 + x3 + x4 = 1) :
    (sgnN x1 + sgnN x2 + sgnN x3 + sgnN x4 + magN c) % 2 = 0 ∧ (c ^ 2 = 1/16 ∨ c ^ 2 = 1/4) ∧
      (magN c = 0 → x1 = 1/4 ∧ x2 = 1/4 ∧ x3 = 1/4 ∧ x4 = 1/4) := by
  rcases sq_eq_sq_iff_eq_or_eq_neg.mp h1 with e1 | e1 <;>
  rcases sq_eq_sq_iff_eq_or_eq_neg.mp h2 with e2 | e2 <;>
  rcases sq_eq_sq_iff_eq_or_eq_neg.mp h3 with e3 | e3 <;>
  rcases sq_eq_sq_iff_eq_or_eq_neg.mp h4 with e4 | e4 <;>
  simp only [e1, e2, e3, e4] at hs ⊢ <;>
  first
  | ((suffices h0 : (0 : K) = 1 by exact absurd h0 zero_ne_one); linear_combination hs)
  | ((suffices hc : c = 1/4 by subst hc; norm_num [sgnN, magN]); linear_combination hs / 4)
  | ((suffices hc : c = -1/4 by subst hc; norm_num [sgnN, magN]); linear_combination -hs / 4)
  | ((suffices hc : c = 1/2 by subst hc; norm_num [sgnN, magN]); linear_combination hs / 2)
  | ((suffices hc : c = -1/2 by subst hc; norm_num [sgnN, magN]); linear_combination -hs / 2)

theorem inS_of_sq {x c : K} (h : x ^ 2 = c ^ 2) (hc : c ^ 2 = 1/16 ∨ c ^ 2 = 1/4) :
    x = 1/4 ∨ x = -1/4 ∨ x = 1/2 ∨ x = -1/2 := by
  rcases hc with hc | hc
  · have h' : x ^ 2 = (1/4) ^ 2 := by rw [h, hc]; norm_num
    rcases sq_eq_sq_iff_eq_or_eq_neg.mp h' with h'' | h''
    · exact Or.inl h''
    · exact Or.inr (Or.inl (by linear_combination h''))
  · have h' : x ^ 2 = (1/2) ^ 2 := by rw [h, hc]; norm_num
    rcases sq_eq_sq_iff_eq_or_eq_neg.mp h' with h'' | h''
    · exact Or.inr (Or.inr (Or.inl h''))
    · exact Or.inr (Or.inr (Or.inr (by linear_combination h'')))

theorem rel_sgn {a b c d : K} (ha : a = 1/4 ∨ a = -1/4 ∨ a = 1/2 ∨ a = -1/2)
    (hb : b = 1/4 ∨ b = -1/4 ∨ b = 1/2 ∨ b = -1/2) (hc : c = 1/4 ∨ c = -1/4 ∨ c = 1/2 ∨ c = -1/2)
    (hd : d = 1/4 ∨ d = -1/4 ∨ d = 1/2 ∨ d = -1/2) (h : a * b = c * d) :
    (sgnN a + sgnN b + sgnN c + sgnN d) % 2 = 0 := by
  rcases ha with rfl | rfl | rfl | rfl <;> rcases hb with rfl | rfl | rfl | rfl <;>
  rcases hc with rfl | rfl | rfl | rfl <;> rcases hd with rfl | rfl | rfl | rfl <;>
  revert h <;> norm_num [sgnN]

end values

/-! ## F2 bookkeeping with bit masks -/

def bitv (i : ℕ) : ℕ := 2 ^ i

/-- first bit of the class magnitude variables (codes are `< 104 * 104`) -/
def TAG : ℕ := 10816

/-- parity of the variables in the mask `v` under the 0/1 assignment `w` -/
noncomputable def par (w : ℕ → ℕ) (v : ℕ) : ℕ := (∑ i ∈ Finset.range 16384, if v.testBit i then w i else 0) % 2

theorem par_mod (w : ℕ → ℕ) (v : ℕ) : par w v % 2 = par w v := by unfold par; exact Nat.mod_mod _ _

theorem par_zero (w : ℕ → ℕ) : par w 0 = 0 := by unfold par; simp

theorem par_xor (w : ℕ → ℕ) (a b : ℕ) : par w (a ^^^ b) = (par w a + par w b) % 2 := by
  unfold par
  rw [← Nat.add_mod, ← Finset.sum_add_distrib]
  conv_lhs => rw [Finset.sum_nat_mod]
  conv_rhs => rw [Finset.sum_nat_mod]
  congr 1
  refine Finset.sum_congr rfl fun i _ => ?_
  rw [Nat.testBit_xor]
  cases a.testBit i <;> cases b.testBit i <;> simp <;> omega

theorem par_bit (w : ℕ → ℕ) {i : ℕ} (hi : i < 16384) : par w (bitv i) = w i % 2 := by
  unfold par bitv
  rw [Finset.sum_eq_single i]
  · simp [Nat.testBit_two_pow_self]
  · intro j _ hj
    simp [Nat.testBit_two_pow, Ne.symm hj]
  · intro h; exact absurd (Finset.mem_range.mpr hi) h

theorem par_foldl (w : ℕ → ℕ) (g : ℕ → ℕ) :
    ∀ (l : List ℕ) (acc : ℕ), (∀ i ∈ l, par w (g i) = 0) → par w (l.foldl (fun a i => a ^^^ g i) acc) = par w acc
  | [], _, _ => rfl
  | i :: l, acc, h => by
    rw [List.foldl_cons, par_foldl w g l _ (fun j hj => h j (List.mem_cons_of_mem _ hj)), par_xor,
      h i (by simp), add_zero, par_mod]

theorem pcode_lt {x y : ℕ} (hx : x < 104) (hy : y < 104) : pcode x y < TAG := by
  unfold pcode TAG
  rcases le_total x y with h | h
  · rw [min_eq_left h, max_eq_right h]; omega
  · rw [min_eq_right h, max_eq_left h]; omega

/-! ## Rows -/

/-- quadruple row: dead `t`, frame `f` inside the dead set, positions `k1 … k4` of the frame lines not orthogonal
to `t`, code-table entries `e1 … e4` of the four codes, all with class root `CR[K]` -/
def quadChk (m nQ nK : ℕ) (T CR : List ℕ) (t f k1 k2 k3 k4 e1 e2 e3 e4 K : ℕ) : Bool :=
  decide (t < 104) && m.testBit t && decide (k1 < 8) && decide (k2 < 8) && decide (k3 < 8) && decide (k4 < 8) &&
    decide (k1 ≠ k2) && decide (k1 ≠ k3) && decide (k1 ≠ k4) && decide (k2 ≠ k3) && decide (k2 ≠ k4) &&
    decide (k3 ≠ k4) &&
    (List.range 8).all (fun k => m.testBit (frL f k)) &&
    (List.range 8).all (fun k => decide (k = k1) || decide (k = k2) || decide (k = k3) || decide (k = k4) ||
      orthB t (frL f k)) &&
    decide (e1 < nQ) && decide (e2 < nQ) && decide (e3 < nQ) && decide (e4 < nQ) && decide (K < nK) &&
    decide (nK ≤ 5000) &&
    (fld T (3 * e1) == pcode t (frL f k1)) && (fld T (3 * e2) == pcode t (frL f k2)) &&
    (fld T (3 * e3) == pcode t (frL f k3)) && (fld T (3 * e4) == pcode t (frL f k4)) &&
    (fld T (3 * e1 + 1) == fld CR K) && (fld T (3 * e2 + 1) == fld CR K) &&
    (fld T (3 * e3 + 1) == fld CR K) && (fld T (3 * e4 + 1) == fld CR K)

/-- what a checked quadruple row gives -/
theorem quadChk_sound (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (nQ nK : ℕ) (T CR : List ℕ)
    (hT : ∀ e < nQ, Nc A B (fld T (3 * e)) ^ 2 = Nc A B (fld T (3 * e + 1)) ^ 2)
    (t f k1 k2 k3 k4 e1 e2 e3 e4 c : ℕ) (h : quadChk m nQ nK T CR t f k1 k2 k3 k4 e1 e2 e3 e4 c = true) :
    c < nK ∧ nK ≤ 5000 ∧ pcode t (frL f k1) < TAG ∧ pcode t (frL f k2) < TAG ∧ pcode t (frL f k3) < TAG ∧
      pcode t (frL f k4) < TAG ∧
      Nc A B (pcode t (frL f k1)) ^ 2 = Nc A B (fld CR c) ^ 2 ∧
      Nc A B (pcode t (frL f k2)) ^ 2 = Nc A B (fld CR c) ^ 2 ∧
      Nc A B (pcode t (frL f k3)) ^ 2 = Nc A B (fld CR c) ^ 2 ∧
      Nc A B (pcode t (frL f k4)) ^ 2 = Nc A B (fld CR c) ^ 2 ∧
      Nc A B (pcode t (frL f k1)) + Nc A B (pcode t (frL f k2)) + Nc A B (pcode t (frL f k3)) +
        Nc A B (pcode t (frL f k4)) = 1 := by
  simp only [quadChk, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq, List.all_eq_true, List.mem_range,
    Bool.or_eq_true, and_assoc] at h
  obtain ⟨ht, hZt, h1, h2, h3, h4, d12, d13, d14, d23, d24, d34, hFZ, hrest, he1, he2, he3, he4, hK, hnK,
    c1, c2, c3, c4, r1, r2, r3, r4⟩ := h
  have f1 := frame_lt f h1; have f2 := frame_lt f h2; have f3 := frame_lt f h3; have f4 := frame_lt f h4
  refine ⟨hK, hnK, pcode_lt ht f1, pcode_lt ht f2, pcode_lt ht f3, pcode_lt ht f4, ?_, ?_, ?_, ?_, ?_⟩
  · rw [← c1, ← r1]; exact hT e1 he1
  · rw [← c2, ← r2]; exact hT e2 he2
  · rw [← c3, ← r3]; exact hT e3 he3
  · rw [← c4, ← r4]; exact hT e4 he4
  · rw [Nc_code A B ht f1, Nc_code A B ht f2, Nc_code A B ht f3, Nc_code A B ht f4]
    refine quad_sum A B u hu m hZ hdiag hmask t f k1 k2 k3 k4 ht hZt hFZ h1 h2 h3 h4 d12 d13 d14 d23 d24 d34 ?_
    intro k hk
    have hk' := frame_lt f hk
    have hr := hrest k hk
    by_cases g1 : k = k1
    · exact Or.inl g1
    by_cases g2 : k = k2
    · exact Or.inr (Or.inl g2)
    by_cases g3 : k = k3
    · exact Or.inr (Or.inr (Or.inl g3))
    by_cases g4 : k = k4
    · exact Or.inr (Or.inr (Or.inr (Or.inl g4)))
    have g5 : orthB t (frL f k) = true := by tauto
    exact Or.inr (Or.inr (Or.inr (Or.inr (orth_of_orthB ht hk' g5))))

/-- relation row: origin `(t, s, f, ka, kb)` as in `relChk`, code-table entries `e1 … e4` of the relation codes,
classes `K1 … K4` of the codes -/
def relRowChk (m nQ nK : ℕ) (T CR : List ℕ) (t s f ka kb e1 e2 e3 e4 c1 c2 c3 c4 : ℕ) : Bool :=
  relChk m (fld T (3 * e1), fld T (3 * e2), fld T (3 * e3), fld T (3 * e4)) t s f ka kb &&
    decide (e1 < nQ) && decide (e2 < nQ) && decide (e3 < nQ) && decide (e4 < nQ) &&
    decide (c1 < nK) && decide (c2 < nK) && decide (c3 < nK) && decide (c4 < nK) &&
    decide (fld T (3 * e1) < TAG) && decide (fld T (3 * e2) < TAG) && decide (fld T (3 * e3) < TAG) &&
    decide (fld T (3 * e4) < TAG) &&
    (fld T (3 * e1 + 1) == fld CR c1) && (fld T (3 * e2 + 1) == fld CR c2) &&
    (fld T (3 * e3 + 1) == fld CR c3) && (fld T (3 * e4 + 1) == fld CR c4)

/-- the 0/1 assignment: sign bits on codes, magnitude bits of the class roots above `TAG` -/
noncomputable def wv [CharZero K] (A B : ℕ → Fin 9 → K) (CR : List ℕ) (i : ℕ) : ℕ :=
  if i < TAG then sgnN (Nc A B i) else magN (Nc A B (fld CR (i - TAG)))

theorem wv_code [CharZero K] (A B : ℕ → Fin 9 → K) (CR : List ℕ) {i : ℕ} (hi : i < TAG) :
    wv A B CR i = sgnN (Nc A B i) := by unfold wv; rw [if_pos hi]

theorem wv_tag [CharZero K] (A B : ℕ → Fin 9 → K) (CR : List ℕ) (c : ℕ) :
    wv A B CR (TAG + c) = magN (Nc A B (fld CR c)) := by
  unfold wv; rw [if_neg (by omega), Nat.add_sub_cancel_left]

theorem par4 (w : ℕ → ℕ) {a b c d : ℕ} (ha : a < 16384) (hb : b < 16384) (hc : c < 16384) (hd : d < 16384) :
    par w (bitv a ^^^ bitv b ^^^ bitv c ^^^ bitv d) = (w a + w b + w c + w d) % 2 := by
  rw [par_xor, par_xor, par_xor, par_bit w ha, par_bit w hb, par_bit w hc, par_bit w hd]; omega

theorem par5 (w : ℕ → ℕ) {a b c d e : ℕ} (ha : a < 16384) (hb : b < 16384) (hc : c < 16384) (hd : d < 16384)
    (he : e < 16384) :
    par w (bitv a ^^^ bitv b ^^^ bitv c ^^^ bitv d ^^^ bitv e) = (w a + w b + w c + w d + w e) % 2 := by
  rw [par_xor, par4 w ha hb hc hd, par_bit w he]; omega

def qMask (t f k1 k2 k3 k4 c : ℕ) : ℕ :=
  bitv (pcode t (frL f k1)) ^^^ bitv (pcode t (frL f k2)) ^^^ bitv (pcode t (frL f k3)) ^^^
    bitv (pcode t (frL f k4)) ^^^ bitv (TAG + c)

def rMask (T : List ℕ) (e1 e2 e3 e4 : ℕ) : ℕ :=
  bitv (fld T (3 * e1)) ^^^ bitv (fld T (3 * e2)) ^^^ bitv (fld T (3 * e3)) ^^^ bitv (fld T (3 * e4))

section rows

variable [CharZero K]

theorem quadRow_par (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (nQ nK : ℕ) (T CR : List ℕ)
    (hT : ∀ e < nQ, Nc A B (fld T (3 * e)) ^ 2 = Nc A B (fld T (3 * e + 1)) ^ 2)
    (t f k1 k2 k3 k4 e1 e2 e3 e4 c : ℕ) (h : quadChk m nQ nK T CR t f k1 k2 k3 k4 e1 e2 e3 e4 c = true) :
    par (wv A B CR) (qMask t f k1 k2 k3 k4 c) = 0 ∧
      (Nc A B (fld CR c) ^ 2 = 1/16 ∨ Nc A B (fld CR c) ^ 2 = 1/4) ∧
      (magN (Nc A B (fld CR c)) = 0 → Nc A B (pcode t (frL f k1)) = 1/4 ∧ Nc A B (pcode t (frL f k2)) = 1/4 ∧
        Nc A B (pcode t (frL f k3)) = 1/4 ∧ Nc A B (pcode t (frL f k4)) = 1/4) := by
  obtain ⟨hc, hnK, l1, l2, l3, l4, s1, s2, s3, s4, hs⟩ :=
    quadChk_sound A B u hu m hZ hdiag hmask nQ nK T CR hT t f k1 k2 k3 k4 e1 e2 e3 e4 c h
  obtain ⟨hp, hsq, hq⟩ := quad_val s1 s2 s3 s4 hs
  refine ⟨?_, hsq, hq⟩
  have b1 : pcode t (frL f k1) < 16384 := by unfold TAG at l1; omega
  have b2 : pcode t (frL f k2) < 16384 := by unfold TAG at l2; omega
  have b3 : pcode t (frL f k3) < 16384 := by unfold TAG at l3; omega
  have b4 : pcode t (frL f k4) < 16384 := by unfold TAG at l4; omega
  have b5 : TAG + c < 16384 := by unfold TAG; omega
  unfold qMask
  rw [par5 _ b1 b2 b3 b4 b5, wv_code A B CR l1, wv_code A B CR l2, wv_code A B CR l3, wv_code A B CR l4,
    wv_tag A B CR c]
  exact hp

theorem relRow_par (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (nQ nK : ℕ) (T CR : List ℕ)
    (hT : ∀ e < nQ, Nc A B (fld T (3 * e)) ^ 2 = Nc A B (fld T (3 * e + 1)) ^ 2)
    (hcls : ∀ c < nK, Nc A B (fld CR c) ^ 2 = 1/16 ∨ Nc A B (fld CR c) ^ 2 = 1/4)
    (t s f ka kb e1 e2 e3 e4 c1 c2 c3 c4 : ℕ)
    (h : relRowChk m nQ nK T CR t s f ka kb e1 e2 e3 e4 c1 c2 c3 c4 = true) :
    par (wv A B CR) (rMask T e1 e2 e3 e4) = 0 := by
  simp only [relRowChk, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq, and_assoc] at h
  obtain ⟨hr, he1, he2, he3, he4, hc1, hc2, hc3, hc4, l1, l2, l3, l4, r1, r2, r3, r4⟩ := h
  have hrel := relChk_sound A B u hu m hZ hdiag hmask _ t s f ka kb hr
  simp only [holds] at hrel
  have q1 : Nc A B (fld T (3 * e1)) ^ 2 = Nc A B (fld CR c1) ^ 2 := by rw [← r1]; exact hT e1 he1
  have q2 : Nc A B (fld T (3 * e2)) ^ 2 = Nc A B (fld CR c2) ^ 2 := by rw [← r2]; exact hT e2 he2
  have q3 : Nc A B (fld T (3 * e3)) ^ 2 = Nc A B (fld CR c3) ^ 2 := by rw [← r3]; exact hT e3 he3
  have q4 : Nc A B (fld T (3 * e4)) ^ 2 = Nc A B (fld CR c4) ^ 2 := by rw [← r4]; exact hT e4 he4
  have v1 := inS_of_sq q1 (hcls c1 hc1)
  have v2 := inS_of_sq q2 (hcls c2 hc2)
  have v3 := inS_of_sq q3 (hcls c3 hc3)
  have v4 := inS_of_sq q4 (hcls c4 hc4)
  have b1 : fld T (3 * e1) < 16384 := by unfold TAG at l1; omega
  have b2 : fld T (3 * e2) < 16384 := by unfold TAG at l2; omega
  have b3 : fld T (3 * e3) < 16384 := by unfold TAG at l3; omega
  have b4 : fld T (3 * e4) < 16384 := by unfold TAG at l4; omega
  unfold rMask
  rw [par4 _ b1 b2 b3 b4, wv_code A B CR l1, wv_code A B CR l2, wv_code A B CR l3, wv_code A B CR l4]
  exact rel_sgn v1 v2 v3 v4 hrel

end rows

/-! ## Packed sign certificates -/

def qRow (QS : List ℕ) (j i : ℕ) : ℕ := fld QS (11 * j + i)

def rRow (RS : List ℕ) (j i : ℕ) : ℕ := fld RS (13 * j + i)

def qRowOK (m nQ nK : ℕ) (T CR QS : List ℕ) (j : ℕ) : Bool :=
  quadChk m nQ nK T CR (qRow QS j 0) (qRow QS j 1) (qRow QS j 2) (qRow QS j 3) (qRow QS j 4) (qRow QS j 5)
    (qRow QS j 6) (qRow QS j 7) (qRow QS j 8) (qRow QS j 9) (qRow QS j 10)

def qRowMask (QS : List ℕ) (j : ℕ) : ℕ :=
  qMask (qRow QS j 0) (qRow QS j 1) (qRow QS j 2) (qRow QS j 3) (qRow QS j 4) (qRow QS j 5) (qRow QS j 10)

def rRowOK (m nQ nK : ℕ) (T CR RS : List ℕ) (j : ℕ) : Bool :=
  relRowChk m nQ nK T CR (rRow RS j 0) (rRow RS j 1) (rRow RS j 2) (rRow RS j 3) (rRow RS j 4) (rRow RS j 5)
    (rRow RS j 6) (rRow RS j 7) (rRow RS j 8) (rRow RS j 9) (rRow RS j 10) (rRow RS j 11) (rRow RS j 12)

def rRowMask (T RS : List ℕ) (j : ℕ) : ℕ := rMask T (rRow RS j 5) (rRow RS j 6) (rRow RS j 7) (rRow RS j 8)

/-- rows `0 … nq-1` are quadruples, the rest relations -/
def rowMask (T QS RS : List ℕ) (nq j : ℕ) : ℕ := if j < nq then qRowMask QS j else rRowMask T RS (j - nq)

def rowOK (m nQ nK : ℕ) (T CR QS RS : List ℕ) (nq j : ℕ) : Bool :=
  if j < nq then qRowOK m nQ nK T CR QS j else rRowOK m nQ nK T CR RS (j - nq)

/-- class `c` has a quadruple row `CQ[c]` (so its square is `1/16` or `1/4`) -/
def classOK (QS CQ : List ℕ) (nq c : ℕ) : Bool := decide (fld CQ c < nq) && qRow QS (fld CQ c) 10 == c

/-- the rows `CB[CO[2c] … CO[2c] + CO[2c+1] - 1]` XOR to the single magnitude bit of class `c` -/
def comboOK (T QS RS : List ℕ) (nq nrows : ℕ) (CB CO : List ℕ) (c : ℕ) : Bool :=
  ((List.range' (fld CO (2 * c)) (fld CO (2 * c + 1))).all fun i => decide (fld CB i < nrows)) &&
    ((List.range' (fld CO (2 * c)) (fld CO (2 * c + 1))).foldl (fun a i => a ^^^ rowMask T QS RS nq (fld CB i)) 0
      == bitv (TAG + c))

section assemble

variable [CharZero K]

theorem signs_sound (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (nQ nK nq nrows : ℕ)
    (T CR QS RS CQ CB CO : List ℕ)
    (hT : ∀ e < nQ, Nc A B (fld T (3 * e)) ^ 2 = Nc A B (fld T (3 * e + 1)) ^ 2)
    (hrows : ∀ j < nrows, rowOK m nQ nK T CR QS RS nq j = true) (hq : nq ≤ nrows)
    (hcl : ∀ c < nK, classOK QS CQ nq c = true)
    (hcb : ∀ c < nK, comboOK T QS RS nq nrows CB CO c = true) :
    ∀ c < nK, magN (Nc A B (fld CR c)) = 0 := by
  -- every class row is a checked quadruple
  have hclq : ∀ c < nK, fld CQ c < nq ∧ qRow QS (fld CQ c) 10 = c ∧ qRowOK m nQ nK T CR QS (fld CQ c) = true := by
    intro c hc
    have h := hcl c hc
    simp only [classOK, Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at h
    have hr := hrows _ (lt_of_lt_of_le h.1 hq)
    unfold rowOK at hr
    rw [if_pos h.1] at hr
    exact ⟨h.1, h.2, hr⟩
  have hcls : ∀ c < nK, Nc A B (fld CR c) ^ 2 = 1/16 ∨ Nc A B (fld CR c) ^ 2 = 1/4 := by
    intro c hc
    obtain ⟨_, h10, hr⟩ := hclq c hc
    have := (quadRow_par A B u hu m hZ hdiag hmask nQ nK T CR hT _ _ _ _ _ _ _ _ _ _ _ hr).2.1
    rw [h10] at this
    exact this
  have hpar : ∀ j < nrows, par (wv A B CR) (rowMask T QS RS nq j) = 0 := by
    intro j hj
    have hr := hrows j hj
    unfold rowOK at hr
    unfold rowMask
    split_ifs at hr ⊢ with h
    · exact (quadRow_par A B u hu m hZ hdiag hmask nQ nK T CR hT _ _ _ _ _ _ _ _ _ _ _ hr).1
    · exact relRow_par A B u hu m hZ hdiag hmask nQ nK T CR hT hcls _ _ _ _ _ _ _ _ _ _ _ _ _ hr
  intro c hc
  have hnK : nK ≤ 5000 := by
    obtain ⟨_, _, hr⟩ := hclq c hc
    exact (quadChk_sound A B u hu m hZ hdiag hmask nQ nK T CR hT _ _ _ _ _ _ _ _ _ _ _ hr).2.1
  have h := hcb c hc
  simp only [comboOK, Bool.and_eq_true, List.all_eq_true, decide_eq_true_eq, beq_iff_eq] at h
  obtain ⟨hall, hfold⟩ := h
  have key : par (wv A B CR) ((List.range' (fld CO (2 * c)) (fld CO (2 * c + 1))).foldl
      (fun a i => a ^^^ rowMask T QS RS nq (fld CB i)) 0) = par (wv A B CR) 0 :=
    par_foldl (wv A B CR) (fun i => rowMask T QS RS nq (fld CB i)) _ 0 (fun i hi => hpar _ (hall i hi))
  rw [hfold, par_zero, par_bit _ (by unfold TAG; omega), wv_tag] at key
  have := magN_le (Nc A B (fld CR c))
  omega

/-- consumer form: a checked quadruple row of a class with magnitude bit 0 has all four values `1/4` -/
theorem quad_quarter (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (nQ nK : ℕ) (T CR : List ℕ)
    (hT : ∀ e < nQ, Nc A B (fld T (3 * e)) ^ 2 = Nc A B (fld T (3 * e + 1)) ^ 2)
    (hmag : ∀ c < nK, magN (Nc A B (fld CR c)) = 0)
    (t f k1 k2 k3 k4 e1 e2 e3 e4 c : ℕ) (h : quadChk m nQ nK T CR t f k1 k2 k3 k4 e1 e2 e3 e4 c = true) :
    Nc A B (pcode t (frL f k1)) = 1/4 ∧ Nc A B (pcode t (frL f k2)) = 1/4 ∧
      Nc A B (pcode t (frL f k3)) = 1/4 ∧ Nc A B (pcode t (frL f k4)) = 1/4 :=
  (quadRow_par A B u hu m hZ hdiag hmask nQ nK T CR hT t f k1 k2 k3 k4 e1 e2 e3 e4 c h).2.2
    (hmag c (quadChk_sound A B u hu m hZ hdiag hmask nQ nK T CR hT t f k1 k2 k3 k4 e1 e2 e3 e4 c h).1)

end assemble

end RankNine
