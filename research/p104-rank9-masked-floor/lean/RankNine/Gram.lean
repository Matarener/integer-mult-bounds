import RankNine.Step5

/-!
# T3.1: the Gram identity on the whole dead set

From the T1 step-5 facts `μ x y g x = γ x y g y` (directed covered pairs) we get, for every ordered pair `(x, y)`
of the (reduced) dead set `Z`,
  `M x y = d x * γ x y * g y`  with  `d x = M x x / g x`  (`GramP`).
Each pair is certified by one of
* diagonal (`γ x x = 1`), orthogonal (`M x y = 0 = γ x y`), a step-5 fact (basic codes, `bOK`);
* a frame `F` inside the dead set with every `(x, f)` and `(f, y)` basic: the frame expansion of `M x y` and the
  integer identity `Σ_f (ρ_x·ρ_f)(ρ_f·ρ_y) = 18 ρ_x·ρ_y` (checked per entry).
-/

namespace RankNine

open Matrix

variable {K : Type*} [Field K]

/-- the row scale `d x = M x x / g x` -/
def dS (A B : ℕ → Fin 9 → K) (g : ℕ → K) (x : ℕ) : K := Mx A B x x / g x

/-- the Gram identity for the ordered pair `(x, y)` -/
def GramP (A B : ℕ → Fin 9 → K) (g : ℕ → K) (x y : ℕ) : Prop := Mx A B x y = dS A B g x * gam x y * g y

/-- basic code `c` for `(x, y)`: 65534 diagonal, 65535 orthogonal, else a step-5 fact index -/
def bOK (nF : ℕ) (FS : List ℕ) (x y c : ℕ) : Bool :=
  if c = 65534 then x == y && dot x x == 18
  else if c = 65535 then orthB x y
  else decide (c < nF) && fct FS c == (x, y)

/-- eight-term sum (frame lines `0 … 7`) -/
def s8 (F : ℕ → ℤ) : ℤ := F 0 + F 1 + F 2 + F 3 + F 4 + F 5 + F 6 + F 7

theorem s8_eq (F : ℕ → ℤ) : ∑ k : Fin 8, F k = s8 F := by
  rw [Fin.sum_univ_eight]; rfl

/-- frame entry `j` (19 fields): `x y f`, then the basic codes of `(x, frL f k)` and of `(frL f k, y)` -/
def ge (GE : List ℕ) (j i : ℕ) : ℕ := fld GE (19 * j + i)

def frOK (m nF : ℕ) (FS GE : List ℕ) (j : ℕ) : Bool :=
  decide (ge GE j 0 < 104) && decide (ge GE j 1 < 104) && m.testBit (ge GE j 0) &&
    (List.range 8).all (fun k => m.testBit (frL (ge GE j 2) k) &&
      bOK nF FS (ge GE j 0) (frL (ge GE j 2) k) (ge GE j (3 + k)) &&
      bOK nF FS (frL (ge GE j 2) k) (ge GE j 1) (ge GE j (11 + k))) &&
    s8 (fun k => dot (ge GE j 0) (frL (ge GE j 2) k) * dot (frL (ge GE j 2) k) (ge GE j 1)) ==
      18 * dot (ge GE j 0) (ge GE j 1)

/-- pair `(x, y)` with table value `v`: frame entry `v - 50000` if `50000 ≤ v < 65534`, else a basic code -/
def pairOK (m zm nF nG : ℕ) (FS GE : List ℕ) (x y v : ℕ) : Bool :=
  if zm.testBit x && zm.testBit y then
    decide (x < 104) && decide (y < 104) &&
      (if 50000 ≤ v ∧ v < 65534 then
        decide (v - 50000 < nG) && ge GE (v - 50000) 0 == x && ge GE (v - 50000) 1 == y &&
          frOK m nF FS GE (v - 50000)
      else bOK nF FS x y v)
  else true

section sound

variable [CharZero K]

theorem basic_sound (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (nF : ℕ) (FS : List ℕ) (g : ℕ → K)
    (hg : ∀ x, g x ≠ 0) (hGf : ∀ i < nF, Gf A B g (fct FS i).1 (fct FS i).2)
    {x y c : ℕ} (hx : x < 104) (hy : y < 104) (h : bOK nF FS x y c = true) : GramP A B g x y := by
  unfold bOK at h
  split_ifs at h with h1 h2
  · simp only [Bool.and_eq_true, beq_iff_eq] at h
    obtain ⟨e, hd⟩ := h
    subst e
    unfold GramP dS gam
    rw [hd]
    push_cast
    rw [div_self (by norm_num : (18 : K) ≠ 0), mul_one, div_mul_cancel₀ _ (hg x)]
  · have ho := orth_of_orthB hx hy h
    have hM : Mx A B x y = 0 := hmask x hx y hy ho
    have hdz : dot x y = 0 := by simpa [orth] using ho
    unfold GramP gam
    rw [hM, hdz]
    simp
  · simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at h
    have G := hGf c h.1
    rw [h.2] at G
    dsimp only at G
    unfold Gf mu at G
    have hxx : Mx A B x x ≠ 0 := hdiag x hx
    rw [div_mul_eq_mul_div, div_eq_iff hxx] at G
    unfold GramP
    rw [show dS A B g x * gam x y * g y = gam x y * g y * Mx A B x x / g x by unfold dS; ring,
      eq_div_iff (hg x)]
    exact G

theorem frame_sound (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (nF : ℕ) (FS GE : List ℕ) (g : ℕ → K)
    (hg : ∀ x, g x ≠ 0) (hGf : ∀ i < nF, Gf A B g (fct FS i).1 (fct FS i).2) (j : ℕ)
    (h : frOK m nF FS GE j = true) : GramP A B g (ge GE j 0) (ge GE j 1) := by
  unfold frOK at h
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.mem_range, beq_iff_eq] at h
  obtain ⟨⟨⟨⟨hx, hy⟩, hZx⟩, hk⟩, hs⟩ := h
  set x := ge GE j 0 with hxd
  set y := ge GE j 1 with hyd
  set f := ge GE j 2 with hfd
  have hdead : ∀ k : Fin 8, A (frL f k) ⬝ᵥ u = 0 := fun k => hZ _ (hk k k.2).1.1
  have hdF : ∀ k : Fin 8, A (frL f k) ⬝ᵥ B (frL f k) ≠ 0 := fun k => hdiag _ (frame_lt f k.2)
  have hoff : ∀ k l : Fin 8, k ≠ l → A (frL f k) ⬝ᵥ B (frL f l) = 0 := fun k l hkl =>
    hmask _ (frame_lt f k.2) _ (frame_lt f l.2) (frame_orth f k.2 l.2 (fun e => hkl (Fin.ext e)))
  have e1 : A x ⬝ᵥ B y = ∑ k : Fin 8, A x ⬝ᵥ B (frL f k) * (A (frL f k) ⬝ᵥ B y) / (A (frL f k) ⬝ᵥ B (frL f k)) :=
    frame_expansion A B u hu (fun k => frL f k) hdead hdF hoff x (hZ x hZx) y
  have hT : ∀ k : Fin 8, A x ⬝ᵥ B (frL f k) * (A (frL f k) ⬝ᵥ B y) / (A (frL f k) ⬝ᵥ B (frL f k)) =
      dS A B g x * g y * (((dot x (frL f k) * dot (frL f k) y : ℤ) : K) / 324) := by
    intro k
    have hfk := frame_lt f k.2
    have b1 : GramP A B g x (frL f k) := basic_sound A B hdiag hmask nF FS g hg hGf hx hfk (hk k k.2).1.2
    have b2 : GramP A B g (frL f k) y := basic_sound A B hdiag hmask nF FS g hg hGf hfk hy (hk k k.2).2
    unfold GramP at b1 b2
    have hff : Mx A B (frL f k) (frL f k) ≠ 0 := hdF k
    have hc : dS A B g (frL f k) * g (frL f k) = Mx A B (frL f k) (frL f k) := div_mul_cancel₀ _ (hg _)
    show Mx A B x (frL f k) * Mx A B (frL f k) y / Mx A B (frL f k) (frL f k) = _
    rw [b1, b2, div_eq_iff hff]
    unfold gam
    push_cast
    linear_combination (dS A B g x * g y * (dot x (frL f k) : K) * (dot (frL f k) y : K) / 324) * hc
  rw [Finset.sum_congr rfl (fun k _ => hT k), ← Finset.mul_sum, ← Finset.sum_div] at e1
  have hsK : ∑ k : Fin 8, (((dot x (frL f k) * dot (frL f k) y : ℤ)) : K) = 18 * (dot x y : K) := by
    rw [← Int.cast_sum, s8_eq (fun k => dot x (frL f k) * dot (frL f k) y), hs]
    simp only [Int.cast_mul, Int.cast_ofNat]
  rw [hsK] at e1
  unfold GramP gam
  show A x ⬝ᵥ B y = _
  rw [e1]
  ring

theorem pair_sound (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (zm nF nG : ℕ) (FS GE : List ℕ)
    (g : ℕ → K) (hg : ∀ x, g x ≠ 0) (hGf : ∀ i < nF, Gf A B g (fct FS i).1 (fct FS i).2) {x y v : ℕ}
    (h : pairOK m zm nF nG FS GE x y v = true) (hzx : zm.testBit x = true) (hzy : zm.testBit y = true) :
    GramP A B g x y := by
  unfold pairOK at h
  rw [if_pos (by simp [hzx, hzy])] at h
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h
  obtain ⟨⟨hx, hy⟩, h⟩ := h
  split_ifs at h with hv
  · simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at h
    obtain ⟨⟨⟨_, h0⟩, h1⟩, hf⟩ := h
    have F := frame_sound A B u hu m hZ hdiag hmask nF FS GE g hg hGf _ hf
    rwa [h0, h1] at F
  · exact basic_sound A B hdiag hmask nF FS g hg hGf hx hy h

/-- T3.1: the Gram identity on `Z × Z` (`Z` = bits of `zm`) from a checked pair table `PI` (index `104 x + y`) -/
theorem gram_sound (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (m : ℕ)
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (zm nF nG : ℕ) (FS GE PI : List ℕ)
    (g : ℕ → K) (hg : ∀ x, g x ≠ 0) (hGf : ∀ i < nF, Gf A B g (fct FS i).1 (fct FS i).2)
    (hall : ∀ c < 10816, pairOK m zm nF nG FS GE (c / 104) (c % 104) (fld PI c) = true) :
    ∀ x < 104, ∀ y < 104, zm.testBit x = true → zm.testBit y = true → GramP A B g x y := by
  intro x hx y hy hzx hzy
  have h := hall (104 * x + y) (by omega)
  rw [show (104 * x + y) / 104 = x by omega, show (104 * x + y) % 104 = y by omega] at h
  exact pair_sound A B u hu m hZ hdiag hmask zm nF nG FS GE g hg hGf h hzx hzy

end sound

end RankNine
