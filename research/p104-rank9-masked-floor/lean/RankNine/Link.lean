import RankNine.Packed
import RankNine.Expansion
import RankNine.OrthTab

/-!
# Link: the certificate relations come from the frame expansion (layer L3/L4 link)

`M x y = A x ⬝ᵥ B y` on the 104 lines of P104 (indices `0 … 103`), `M x x ≠ 0`, `M x y = 0` on orthogonal pairs.
One of the nine terms has dual vector `u ≠ 0`, and every row of the dead set `C(W)` (bit mask `m`) is dead:
`A x ⬝ᵥ u = 0`.  For dead `t ⊥ s` and a frame `F` inside the dead set whose lines not orthogonal to both `t` and `s`
are exactly `a, b`, the frame expansions of `M t s = 0` and `M s t = 0` give
`N{t,a} N{s,a} = N{t,b} N{s,b}` with `N{x,y} = M x y M y x / (M x x M y y)` (`rel_core`).  Codes `104 min + max`
index the unordered pairs (`Nc`).  `relOK` is the kernel-checkable origin record of one certificate relation.
-/

namespace RankNine

open Matrix

theorem dotL_comm : ∀ a b : List Int, dotL a b = dotL b a
  | [], [] => rfl
  | [], _ :: _ => rfl
  | _ :: _, [] => rfl
  | x :: xs, y :: ys => by
    show x * y + dotL xs ys = y * x + dotL ys xs
    rw [dotL_comm xs ys, Int.mul_comm]

theorem orth_comm (i j : ℕ) : orth i j = orth j i := by
  unfold orth dot; rw [dotL_comm]

theorem orth_of_orthB {i j : ℕ} (hi : i < 104) (hj : j < 104) (h : orthB i j = true) : orth i j = true := by
  have ht := orthB_table
  simp only [List.all_eq_true, List.mem_range, beq_iff_eq] at ht
  rw [← ht i hi j hj]; exact h

/-- default frame (frame 0), so that `frL f` is a frame for every `f` -/
def frameDefault : List ℕ := [0, 6, 18, 24, 32, 41, 52, 103]

/-- line `k` of frame `f` -/
def frL (f k : ℕ) : ℕ := (frameData.getD f frameDefault).getD k 0

def goodFrame (fr : List ℕ) : Bool :=
  (List.range 8).all fun k => decide (fr.getD k 0 < 104) &&
    (List.range 8).all fun l => k == l || orthB (fr.getD k 0) (fr.getD l 0)

theorem frames_good : (frameDefault :: frameData).all goodFrame = true := by decide +kernel

theorem frL_good (f : ℕ) : goodFrame (frameData.getD f frameDefault) = true := by
  have h := frames_good
  simp only [List.all_cons, Bool.and_eq_true, List.all_eq_true] at h
  exact getD_prop (fun fr => goodFrame fr = true) frameData frameDefault h.1 h.2 f

theorem frame_lt (f : ℕ) {k : ℕ} (hk : k < 8) : frL f k < 104 := by
  have h := frL_good f
  simp only [goodFrame, List.all_eq_true, List.mem_range, Bool.and_eq_true, decide_eq_true_eq] at h
  exact (h k hk).1

theorem frame_orth (f : ℕ) {k l : ℕ} (hk : k < 8) (hl : l < 8) (hkl : k ≠ l) :
    orth (frL f k) (frL f l) = true := by
  have h := frL_good f
  simp only [goodFrame, List.all_eq_true, List.mem_range, Bool.and_eq_true, decide_eq_true_eq,
    Bool.or_eq_true, beq_iff_eq] at h
  rcases (h k hk).2 l hl with h1 | h1
  · exact absurd h1 hkl
  · exact orth_of_orthB (frame_lt f hk) (frame_lt f hl) h1

/-- code of the unordered pair `{a, b}` -/
def pcode (a b : ℕ) : ℕ := 104 * min a b + max a b

variable {K : Type*} [Field K]

def Mx (A B : ℕ → Fin 9 → K) (x y : ℕ) : K := A x ⬝ᵥ B y

/-- `N{x,y} = M x y M y x / (M x x M y y)` -/
def Nq (A B : ℕ → Fin 9 → K) (x y : ℕ) : K := Mx A B x y * Mx A B y x / (Mx A B x x * Mx A B y y)

/-- `N` on pair codes -/
def Nc (A B : ℕ → Fin 9 → K) (c : ℕ) : K := Nq A B (c / 104) (c % 104)

theorem Nq_comm (A B : ℕ → Fin 9 → K) (x y : ℕ) : Nq A B x y = Nq A B y x := by
  unfold Nq; ring

theorem Nc_code (A B : ℕ → Fin 9 → K) {x y : ℕ} (hx : x < 104) (hy : y < 104) :
    Nc A B (pcode x y) = Nq A B x y := by
  unfold Nc pcode
  rcases le_total x y with h | h
  · rw [min_eq_left h, max_eq_right h]
    have h1 : (104 * x + y) / 104 = x := by omega
    have h2 : (104 * x + y) % 104 = y := by omega
    rw [h1, h2]
  · rw [min_eq_right h, max_eq_left h]
    have h1 : (104 * y + x) / 104 = y := by omega
    have h2 : (104 * y + x) % 104 = x := by omega
    rw [h1, h2, Nq_comm]

/-- the algebra of one relation: two two-term expansions of zero -/
theorem rel_alg {Mta Mat Msa Mas Mtb Mbt Msb Mbs Maa Mbb Mtt Mss : K}
    (e1 : 0 = Mta * Mas / Maa + Mtb * Mbs / Mbb) (e2 : 0 = Msa * Mat / Maa + Msb * Mbt / Mbb) :
    (Mta * Mat / (Mtt * Maa)) * (Msa * Mas / (Mss * Maa)) =
      (Mtb * Mbt / (Mtt * Mbb)) * (Msb * Mbs / (Mss * Mbb)) := by
  linear_combination (-(Msa * Mat / Maa) / (Mtt * Mss)) * e1 + (Mtb * Mbs / Mbb / (Mtt * Mss)) * e2

/-- one relation from the frame expansion -/
theorem rel_core (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (t s f ka kb : ℕ) (ht : t < 104) (hs : s < 104) (hka : ka < 8) (hkb : kb < 8) (hab : ka ≠ kb)
    (hZt : m.testBit t = true) (hZs : m.testBit s = true) (hts : orth t s = true)
    (hFZ : ∀ k < 8, m.testBit (frL f k) = true)
    (hoth : ∀ k < 8, k = ka ∨ k = kb ∨ orth t (frL f k) = true ∨ orth s (frL f k) = true) :
    Nq A B t (frL f ka) * Nq A B s (frL f ka) = Nq A B t (frL f kb) * Nq A B s (frL f kb) := by
  have hdead : ∀ k : Fin 8, A (frL f k) ⬝ᵥ u = 0 := fun k => hZ _ (hFZ k k.2)
  have hdF : ∀ k : Fin 8, A (frL f k) ⬝ᵥ B (frL f k) ≠ 0 := fun k => hdiag _ (frame_lt f k.2)
  have hoff : ∀ k l : Fin 8, k ≠ l → A (frL f k) ⬝ᵥ B (frL f l) = 0 := fun k l hkl =>
    hmask _ (frame_lt f k.2) _ (frame_lt f l.2) (frame_orth f k.2 l.2 (fun e => hkl (Fin.ext e)))
  have hst : orth s t = true := by rw [orth_comm]; exact hts
  have e1 : (0 : K) = ∑ k : Fin 8, A t ⬝ᵥ B (frL f k) * (A (frL f k) ⬝ᵥ B s) / (A (frL f k) ⬝ᵥ B (frL f k)) :=
    (hmask t ht s hs hts).symm.trans
      (frame_expansion A B u hu (fun k => frL f k) hdead hdF hoff t (hZ t hZt) s)
  have e2 : (0 : K) = ∑ k : Fin 8, A s ⬝ᵥ B (frL f k) * (A (frL f k) ⬝ᵥ B t) / (A (frL f k) ⬝ᵥ B (frL f k)) :=
    (hmask s hs t ht hst).symm.trans
      (frame_expansion A B u hu (fun k => frL f k) hdead hdF hoff s (hZ s hZs) t)
  have hne : (⟨ka, hka⟩ : Fin 8) ≠ ⟨kb, hkb⟩ := Fin.ne_of_val_ne hab
  have s1 : ∀ x : Fin 8, x ≠ ⟨ka, hka⟩ ∧ x ≠ ⟨kb, hkb⟩ →
      A t ⬝ᵥ B (frL f x) * (A (frL f x) ⬝ᵥ B s) / (A (frL f x) ⬝ᵥ B (frL f x)) = 0 := by
    intro x hx
    rcases hoth x x.2 with h | h | h | h
    · exact (hx.1 (Fin.ext h)).elim
    · exact (hx.2 (Fin.ext h)).elim
    · rw [hmask t ht _ (frame_lt f x.2) h, zero_mul, zero_div]
    · rw [hmask _ (frame_lt f x.2) s hs (by rw [orth_comm]; exact h), mul_zero, zero_div]
  have s2 : ∀ x : Fin 8, x ≠ ⟨ka, hka⟩ ∧ x ≠ ⟨kb, hkb⟩ →
      A s ⬝ᵥ B (frL f x) * (A (frL f x) ⬝ᵥ B t) / (A (frL f x) ⬝ᵥ B (frL f x)) = 0 := by
    intro x hx
    rcases hoth x x.2 with h | h | h | h
    · exact (hx.1 (Fin.ext h)).elim
    · exact (hx.2 (Fin.ext h)).elim
    · rw [hmask _ (frame_lt f x.2) t ht (by rw [orth_comm]; exact h), mul_zero, zero_div]
    · rw [hmask s hs _ (frame_lt f x.2) h, zero_mul, zero_div]
  rw [Fintype.sum_eq_add _ _ hne s1] at e1
  rw [Fintype.sum_eq_add _ _ hne s2] at e2
  exact rel_alg e1 e2

/-- kernel-checkable origin of a relation `r`: dead rows `t ⊥ s`, frame `f` inside the dead set `m`, positions
`ka ≠ kb` of the only frame lines not orthogonal to both `t` and `s`, and `r` is the relation of these codes -/
def relChk (m : ℕ) (r : Rel) (t s f ka kb : ℕ) : Bool :=
  decide (t < 104) && decide (s < 104) && decide (ka < 8) && decide (kb < 8) && decide (ka ≠ kb) &&
    m.testBit t && m.testBit s && orthB t s &&
    (List.range 8).all (fun k => m.testBit (frL f k)) &&
    (List.range 8).all (fun k => decide (k = ka) || decide (k = kb) || orthB t (frL f k) || orthB s (frL f k)) &&
    decide (r = (pcode t (frL f ka), pcode s (frL f ka), pcode t (frL f kb), pcode s (frL f kb)))

/-- origin record `j` of a packed certificate: five fields `t, s, f, ka, kb` of `O` -/
def relOK (m : ℕ) (R O : List ℕ) (j : ℕ) : Bool :=
  relChk m (relAt R j) (fld O (5 * j)) (fld O (5 * j + 1)) (fld O (5 * j + 2)) (fld O (5 * j + 3))
    (fld O (5 * j + 4))

theorem relChk_sound (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (r : Rel) (t s f ka kb : ℕ) (h : relChk m r t s f ka kb = true) : holds (Nc A B) r := by
  simp only [relChk, Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.mem_range,
    Bool.or_eq_true] at h
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨ht, hs⟩, hka⟩, hkb⟩, hab⟩, hZt⟩, hZs⟩, hts⟩, hFZ⟩, hoth⟩, hr⟩ := h
  subst hr
  have hfa := frame_lt f hka
  have hfb := frame_lt f hkb
  simp only [holds]
  rw [Nc_code A B ht hfa, Nc_code A B hs hfa, Nc_code A B ht hfb, Nc_code A B hs hfb]
  refine rel_core A B u hu m hZ hdiag hmask t s f ka kb ht hs hka hkb hab hZt hZs
    (orth_of_orthB ht hs hts) hFZ ?_
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

theorem relOK_sound (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (R O : List ℕ) (j : ℕ) (h : relOK m R O j = true) : holds (Nc A B) (relAt R j) :=
  relChk_sound A B u hu m hZ hdiag hmask _ _ _ _ _ _ h

end RankNine
