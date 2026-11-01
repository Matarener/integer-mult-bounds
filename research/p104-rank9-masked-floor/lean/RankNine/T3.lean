import RankNine.Assemble

set_option linter.unusedSectionVars false

/-!
# T3 per type: from the T1 gauge to rows and columns along roots

`t3_type` combines `rows_rep` (T3.2, along a frame `f` inside `Z`) with `assemble`.  All per-type facts are Boolean
checks (`decide`) on lists and masks, and the per-type certificates enter as `LineH` (line certificates on `OL`),
`GlueH` (gluing on `OG` over the mask `sm`) and the special data for the bad line `U` (`U = 104` if none).
-/

namespace RankNine

open Matrix

variable {K : Type*} [Field K] [CharZero K]

theorem PV_ones (A B : ℕ → Fin 9 → K) (g : ℕ → K) (f v : ℕ) : PV A B g f v ⬝ᵥ vK K ones9L = 0 := by
  unfold PV
  rw [sum_dotProduct]
  exact Finset.sum_eq_zero fun k _ => by rw [smul_dotProduct, rho_ones (frame_lt f k.2), smul_zero]

theorem cS_ones (A B : ℕ → Fin 9 → K) (g : ℕ → K) (f s : ℕ) : cS A B g f s ⬝ᵥ vK K ones9L = 0 := by
  unfold cS
  rw [sum_dotProduct]
  exact Finset.sum_eq_zero fun k _ => by rw [smul_dotProduct, rho_ones (frame_lt f k.2), smul_zero]

/-- the frame `f` lies in the dead set and in `Z` -/
def frInOK (m zm f : ℕ) : Bool := (List.range 8).all fun k => m.testBit (frL f k) && zm.testBit (frL f k)

/-- special data for the bad line `U` -/
def SpecialH (zm U : ℕ) (OL : List ℕ) : Prop :=
  U < 104 → ∃ s t k0 k1 : ℕ, ∃ Cs Ct : RCert, s < 104 ∧ t < 104 ∧ dot s t = 0 ∧ dot U s = 0 ∧ dot U t = 0 ∧
    s ∈ OL ∧ t ∈ OL ∧ lcxOK zm s U k0 Cs = true ∧ lcxOK zm t U k1 Ct = true

/-- **T3 for one framed type.** -/
theorem t3_type (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) {m zm sm U f : ℕ} {OL OG : List ℕ}
    (hZ : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (g : ℕ → K) (hg : ∀ x, g x ≠ 0)
    (hG : ∀ x < 104, ∀ y < 104, zm.testBit x = true → zm.testBit y = true → GramP A B g x y)
    (hfin : frInOK m zm f = true) (hfv : fvecOK f = true) (hz : zm < 2 ^ 104)
    (hzm : (List.range 104).all (fun x => !zm.testBit x || m.testBit x) = true)
    (hOL : OL.all (· < 104) = true) (hOGl : OG.all (· < 104) = true)
    (hcov : (List.range 104).all (fun v => zm.testBit v || decide (v ∈ OL) || v == U) = true)
    (hOG : (List.range 104).all (fun v => zm.testBit v || decide (v ∈ OG) || m.testBit v) = true)
    (hsm : (List.range 104).all (fun s => !sm.testBit s || zm.testBit s || decide (s ∈ OL)) = true)
    (hsmlt : sm < 2 ^ 104) (HL : LineH K zm OL) (HG : GlueH K sm OG) (HS : SpecialH zm U OL) :
    ∃ lam eta : ℕ → K, (∀ v s, Mx A B v s = PV A B g f v ⬝ᵥ cS A B g f s + lam v * eta s) ∧
      (∀ x, m.testBit x = true → lam x = 0) ∧ (∀ v < 104, lam v ≠ 0 → v ∈ OG) ∧
      (∀ s < 104, s ≠ U → ∃ b : K, cS A B g f s = b • rho K s) ∧
      (∀ v < 104, lam v = 0 → ∃ a : K, PV A B g f v = a • rho K v) ∧
      ((∃ Λ : Fin 9 → K, ∀ v < 104, ∃ a : K, PV A B g f v = a • rho K v + lam v • Λ) ∨
        ¬ ∃ x1 x2 x3 x4 x5, (x1 ∈ OG ∧ lam x1 ≠ 0) ∧ (x2 ∈ OG ∧ lam x2 ≠ 0) ∧ (x3 ∈ OG ∧ lam x3 ≠ 0) ∧
          (x4 ∈ OG ∧ lam x4 ≠ 0) ∧ (x5 ∈ OG ∧ lam x5 ≠ 0) ∧ dist5B x1 x2 x3 x4 x5 = true) ∧
      (U < 104 → ∀ s < 104, lam s = 0 → dot s U = 0 → ∀ (k0 : ℕ) (C : RCert), lcxOK zm s U k0 C = true →
        ∃ b : K, cS A B g f U = b • rho K U) := by
  have hf : ∀ k < 8, m.testBit (frL f k) = true ∧ zm.testBit (frL f k) = true := by
    intro k hk
    have := (List.all_eq_true.mp hfin) k (List.mem_range.mpr hk)
    simpa only [Bool.and_eq_true] using this
  obtain ⟨lam, eta, hrep, hlam, hPZ, hcZ⟩ := rows_rep A B u hu m hZ hdiag hmask g hg zm hG f hf hfv
  have hzm' : ∀ x, zm.testBit x = true → m.testBit x = true := by
    intro x hx
    have := (List.all_eq_true.mp hzm) x (List.mem_range.mpr (zm_lt hz hx))
    simp only [Bool.or_eq_true, Bool.not_eq_true'] at this
    rcases this with e | e
    · rw [hx] at e; exact absurd e (by simp)
    · exact e
  have R : Rep (Mx A B) (PV A B g f) (cS A B g f) lam eta zm (dS A B g) g :=
    { rep := hrep
      lamZ := fun x hx => hlam x (hzm' x hx)
      PZ := hPZ
      cZ := hcZ
      dne := fun x hx => dS_ne A B g hg hdiag hx
      gne := hg
      P1 := PV_ones A B g f
      c1 := cS_ones A B g f
      diag := hdiag
      mask := hmask }
  have hOL' : ∀ v ∈ OL, v < 104 := fun v hv => by simpa using (List.all_eq_true.mp hOL) v hv
  have hOG' : ∀ v ∈ OG, v < 104 := fun v hv => by simpa using (List.all_eq_true.mp hOGl) v hv
  have hcov' : ∀ v < 104, zm.testBit v = true ∨ v ∈ OL ∨ v = U := by
    intro v hv
    have := (List.all_eq_true.mp hcov) v (List.mem_range.mpr hv)
    simp only [Bool.or_eq_true, decide_eq_true_eq, beq_iff_eq] at this
    rcases this with (e | e) | e
    · exact Or.inl e
    · exact Or.inr (Or.inl e)
    · exact Or.inr (Or.inr e)
  have hlive : ∀ v < 104, zm.testBit v = false → v ∉ OG → lam v = 0 := by
    intro v hv h1 h2
    have := (List.all_eq_true.mp hOG) v (List.mem_range.mpr hv)
    simp only [Bool.or_eq_true, decide_eq_true_eq] at this
    rcases this with (e | e) | e
    · rw [h1] at e; exact absurd e (by simp)
    · exact absurd e h2
    · exact hlam v e
  have hS : ∀ s, sm.testBit s = true → zm.testBit s = true ∨ s ∈ OL := by
    intro s hs
    have := (List.all_eq_true.mp hsm) s (List.mem_range.mpr (zm_lt hsmlt hs))
    simp only [Bool.or_eq_true, Bool.not_eq_true', decide_eq_true_eq] at this
    rcases this with (e | e) | e
    · rw [hs] at e; exact absurd e (by simp)
    · exact Or.inl e
    · exact Or.inr e
  have hU : U < 104 → lam U = 0 → ∃ a : K, PV A B g f U = a • rho K U := by
    intro hU hl
    obtain ⟨s, t, k0, k1, Cs, Ct, hs, ht, hst, hUs, hUt, hsO, htO, hCs, hCt⟩ := HS hU
    exact dead_special R hz hU hs ht hl hst hUs hUt (col_gramm R hz HL hsO hs) (col_gramm R hz HL htO ht) hCs hCt
  have hin : ∀ v < 104, lam v ≠ 0 → v ∈ OG := by
    intro v hv hl
    by_contra hn
    cases hz' : zm.testBit v
    · exact hl (hlive v hv hz' hn)
    · exact hl (hlam v (hzm' v hz'))
  obtain ⟨hc, hd, hgl⟩ := assemble R hz hOL' hOG' hcov' hlive hS HL HG hU
  exact ⟨lam, eta, hrep, hlam, hin, hc, hd, hgl,
    fun hU' s hs hl hsU _ _ hC => col_pin R hz hU' hs hl hsU (hd s hs hl) hC⟩

end RankNine
