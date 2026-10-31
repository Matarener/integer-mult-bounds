import Mathlib

/-!
# Frame expansion (layer L3)

`M x y = A x ⬝ᵥ B y` with `A x, B y ∈ K⁹` (a rank-≤9 factorisation).  Rows in the hyperplane `{v : v ⬝ᵥ u = 0}`
(`u ≠ 0`, the dual vector of one term: its dead rows).  If eight dead rows `F` have a diagonal `M[F, F]` with nonzero
diagonal (an 8-frame inside the dead set), every dead row `t` expands along `F`:
`M t s = Σ_k M t (F k) * M (F k) s / M (F k) (F k)` for every column `s`.
-/

namespace RankNine

open Matrix

variable {K : Type*} [Field K] {ι : Type*}

/-- `u` together with the frame columns `B (F l)` is linearly independent. -/
theorem frame_cols_indep (A B : ι → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (F : Fin 8 → ι)
    (hdead : ∀ k, A (F k) ⬝ᵥ u = 0) (hdiag : ∀ k, A (F k) ⬝ᵥ B (F k) ≠ 0)
    (hoff : ∀ k l, k ≠ l → A (F k) ⬝ᵥ B (F l) = 0) :
    LinearIndependent K (Fin.cons u (fun l => B (F l)) : Fin 9 → Fin 9 → K) := by
  rw [Fintype.linearIndependent_iff]
  intro g hg
  have hdot : ∀ k : Fin 8, g k.succ * (A (F k) ⬝ᵥ B (F k)) = 0 := by
    intro k
    have := congrArg (fun v => A (F k) ⬝ᵥ v) hg
    simp only at this
    rw [Fin.sum_univ_succ, dotProduct_zero, dotProduct_add, dotProduct_sum] at this
    simp only [Fin.cons_zero, Fin.cons_succ, dotProduct_smul, hdead, smul_eq_mul, mul_zero,
      zero_add] at this
    rw [Finset.sum_eq_single k] at this
    · rw [mul_comm] at this; rw [mul_comm]; exact this
    · intro l _ hl; rw [hoff k l (Ne.symm hl), mul_zero]
    · simp
  have hs : ∀ k : Fin 8, g k.succ = 0 := fun k =>
    (mul_eq_zero.mp (hdot k)).resolve_right (hdiag k)
  intro i
  refine Fin.cases ?_ (fun k => hs k) i
  have : g 0 • u = 0 := by
    have h2 := hg
    rw [Fin.sum_univ_succ] at h2
    simp only [Fin.cons_zero, Fin.cons_succ, hs, zero_smul, Finset.sum_const_zero, add_zero] at h2
    exact h2
  exact (smul_eq_zero.mp this).resolve_right hu

/-- A vector orthogonal to `u` and to all frame columns is zero. -/
theorem orth_frame_eq_zero (A B : ι → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (F : Fin 8 → ι)
    (hdead : ∀ k, A (F k) ⬝ᵥ u = 0) (hdiag : ∀ k, A (F k) ⬝ᵥ B (F k) ≠ 0)
    (hoff : ∀ k l, k ≠ l → A (F k) ⬝ᵥ B (F l) = 0) (w : Fin 9 → K) (hwu : w ⬝ᵥ u = 0)
    (hwB : ∀ l, w ⬝ᵥ B (F l) = 0) : w = 0 := by
  have hli := frame_cols_indep A B u hu F hdead hdiag hoff
  let b := basisOfLinearIndependentOfCardEqFinrank hli (by simp)
  have hb0 : ∀ i, w ⬝ᵥ (Fin.cons u (fun l => B (F l)) : Fin 9 → Fin 9 → K) i = 0 := by
    intro i
    refine Fin.cases ?_ ?_ i
    · simpa using hwu
    · intro l; simpa using hwB l
  have hb : ∀ i, w ⬝ᵥ b i = 0 := by
    intro i; simpa [b, coe_basisOfLinearIndependentOfCardEqFinrank] using hb0 i
  funext j
  have hx := b.sum_repr (Pi.single j 1)
  have : w ⬝ᵥ Pi.single j 1 = 0 := by
    rw [← hx, dotProduct_sum]
    exact Finset.sum_eq_zero fun i _ => by rw [dotProduct_smul, hb i, smul_zero]
  simpa [dotProduct_single] using this

/-- Frame expansion of a dead row. -/
theorem frame_expansion (A B : ι → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0) (F : Fin 8 → ι)
    (hdead : ∀ k, A (F k) ⬝ᵥ u = 0) (hdiag : ∀ k, A (F k) ⬝ᵥ B (F k) ≠ 0)
    (hoff : ∀ k l, k ≠ l → A (F k) ⬝ᵥ B (F l) = 0) (t : ι) (ht : A t ⬝ᵥ u = 0) (s : ι) :
    A t ⬝ᵥ B s = ∑ k, (A t ⬝ᵥ B (F k)) * (A (F k) ⬝ᵥ B s) / (A (F k) ⬝ᵥ B (F k)) := by
  set c : Fin 8 → K := fun k => (A t ⬝ᵥ B (F k)) / (A (F k) ⬝ᵥ B (F k)) with hc
  have hw : A t - ∑ k, c k • A (F k) = 0 := by
    apply orth_frame_eq_zero A B u hu F hdead hdiag hoff
    · rw [sub_dotProduct, sum_dotProduct]
      simp [smul_dotProduct, hdead, ht]
    · intro l
      rw [sub_dotProduct, sum_dotProduct, Finset.sum_eq_single l]
      · rw [smul_dotProduct, smul_eq_mul, hc]
        field_simp [hdiag l]
        ring
      · intro k _ hk; rw [smul_dotProduct, hoff k l hk, smul_zero]
      · simp
  have ht' : A t = ∑ k, c k • A (F k) := sub_eq_zero.mp hw
  rw [ht', sum_dotProduct]
  refine Finset.sum_congr rfl fun k _ => ?_
  rw [smul_dotProduct, smul_eq_mul]
  simp only [hc]
  ring

end RankNine
