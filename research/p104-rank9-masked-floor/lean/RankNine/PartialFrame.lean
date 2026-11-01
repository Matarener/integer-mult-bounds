import RankNine.Expansion

/-!
# Partial frame expansion (T2, step T2.0)

`M x y = A x ⬝ᵥ B y`, dead rows `{t : A t ⬝ᵥ u = 0}` of one term (`u ≠ 0`).  An 8-frame `F` (non-zero diagonal,
zero off-diagonal) of which only the lines `k ∈ D` are dead.  The frame is *non-degenerate* for `u` when `u`
together with the eight frame columns `B (F k)` is linearly independent.  Then every dead row `t` orthogonal to the
outside lines `F k`, `k ∉ D`, expands along the inside lines:
`M t s = Σ_{k ∈ D} M t (F k) * M (F k) s / M (F k) (F k)`.
If the frame is degenerate, `u` is a combination of the outside frame columns only (`degenerate_repr`).
-/

namespace RankNine

open Matrix

variable {K : Type*} [Field K] {ι : Type*}

/-- The eight frame columns are linearly independent. -/
theorem frame_B_indep (A B : ι → Fin 9 → K) (F : Fin 8 → ι) (hdiag : ∀ k, A (F k) ⬝ᵥ B (F k) ≠ 0)
    (hoff : ∀ k l, k ≠ l → A (F k) ⬝ᵥ B (F l) = 0) :
    LinearIndependent K (fun l => B (F l)) := by
  rw [Fintype.linearIndependent_iff]
  intro g hg k
  have := congrArg (fun v => A (F k) ⬝ᵥ v) hg
  simp only [dotProduct_zero, dotProduct_sum, dotProduct_smul, smul_eq_mul] at this
  rw [Finset.sum_eq_single k (fun l _ hl => by rw [hoff k l (Ne.symm hl), mul_zero]) (by simp)] at this
  exact (mul_eq_zero.mp this).resolve_right (hdiag k)

/-- A vector orthogonal to `u` and to all frame columns is zero, once `u` and the columns are independent. -/
theorem orth_basis_eq_zero (B' : Fin 9 → Fin 9 → K) (hli : LinearIndependent K B') (w : Fin 9 → K)
    (hw : ∀ i, w ⬝ᵥ B' i = 0) : w = 0 := by
  let b := basisOfLinearIndependentOfCardEqFinrank hli (by simp)
  have hb : ∀ i, w ⬝ᵥ b i = 0 := by
    intro i; simpa [b, coe_basisOfLinearIndependentOfCardEqFinrank] using hw i
  funext j
  have hx := b.sum_repr (Pi.single j 1)
  have : w ⬝ᵥ Pi.single j 1 = 0 := by
    rw [← hx, dotProduct_sum]
    exact Finset.sum_eq_zero fun i _ => by rw [dotProduct_smul, hb i, smul_zero]
  simpa [dotProduct_single] using this

/-- **Partial frame expansion.** -/
theorem partial_expansion (A B : ι → Fin 9 → K) (u : Fin 9 → K) (F : Fin 8 → ι) (D : Finset (Fin 8))
    (hnd : LinearIndependent K (Fin.cons u (fun l => B (F l)) : Fin 9 → Fin 9 → K))
    (hdead : ∀ k ∈ D, A (F k) ⬝ᵥ u = 0) (hdiag : ∀ k, A (F k) ⬝ᵥ B (F k) ≠ 0)
    (hoff : ∀ k l, k ≠ l → A (F k) ⬝ᵥ B (F l) = 0) (t : ι) (ht : A t ⬝ᵥ u = 0)
    (hout : ∀ k, k ∉ D → A t ⬝ᵥ B (F k) = 0) (s : ι) :
    A t ⬝ᵥ B s = ∑ k ∈ D, (A t ⬝ᵥ B (F k)) * (A (F k) ⬝ᵥ B s) / (A (F k) ⬝ᵥ B (F k)) := by
  set c : Fin 8 → K := fun k => (A t ⬝ᵥ B (F k)) / (A (F k) ⬝ᵥ B (F k)) with hc
  have hw : A t - ∑ k ∈ D, c k • A (F k) = 0 := by
    apply orth_basis_eq_zero _ hnd
    intro i
    refine Fin.cases ?_ (fun l => ?_) i
    · simp only [Fin.cons_zero]
      rw [sub_dotProduct, sum_dotProduct, ht, zero_sub, neg_eq_zero]
      exact Finset.sum_eq_zero fun k hk => by rw [smul_dotProduct, hdead k hk, smul_zero]
    · simp only [Fin.cons_succ]
      rw [sub_dotProduct, sum_dotProduct]
      by_cases hl : l ∈ D
      · rw [Finset.sum_eq_single l]
        · rw [smul_dotProduct, smul_eq_mul, hc]
          field_simp [hdiag l]
          ring
        · intro k _ hk; rw [smul_dotProduct, hoff k l hk, smul_zero]
        · intro h; exact absurd hl h
      · rw [hout l hl, zero_sub, neg_eq_zero]
        exact Finset.sum_eq_zero fun k hk => by
          rw [smul_dotProduct, hoff k l (fun e => hl (e ▸ hk)), smul_zero]
  have ht' : A t = ∑ k ∈ D, c k • A (F k) := sub_eq_zero.mp hw
  calc A t ⬝ᵥ B s = (∑ k ∈ D, c k • A (F k)) ⬝ᵥ B s := by rw [← ht']
    _ = ∑ k ∈ D, c k * (A (F k) ⬝ᵥ B s) := by
      rw [sum_dotProduct]; simp only [smul_dotProduct, smul_eq_mul]
    _ = ∑ k ∈ D, (A t ⬝ᵥ B (F k)) * (A (F k) ⬝ᵥ B s) / (A (F k) ⬝ᵥ B (F k)) := by
      refine Finset.sum_congr rfl fun k _ => ?_
      simp only [hc]
      ring

/-- **Degenerate frame.** If `u` and the frame columns are dependent, `u` is a combination of the columns of the
frame lines that are not dead. -/
theorem degenerate_repr (A B : ι → Fin 9 → K) (u : Fin 9 → K) (F : Fin 8 → ι) (D : Finset (Fin 8))
    (hdeg : ¬ LinearIndependent K (Fin.cons u (fun l => B (F l)) : Fin 9 → Fin 9 → K))
    (hdead : ∀ k ∈ D, A (F k) ⬝ᵥ u = 0) (hdiag : ∀ k, A (F k) ⬝ᵥ B (F k) ≠ 0)
    (hoff : ∀ k l, k ≠ l → A (F k) ⬝ᵥ B (F l) = 0) :
    ∃ c : Fin 8 → K, (∀ k ∈ D, c k = 0) ∧ u = ∑ k, c k • B (F k) := by
  have hB := frame_B_indep A B F hdiag hoff
  have hmem : u ∈ Submodule.span K (Set.range fun l => B (F l)) := by
    by_contra hn
    exact hdeg (linearIndependent_fin_cons.mpr ⟨hB, hn⟩)
  obtain ⟨c, hc⟩ := (Submodule.mem_span_range_iff_exists_fun K).mp hmem
  refine ⟨c, fun k hk => ?_, hc.symm⟩
  have h0 := hdead k hk
  rw [← hc, dotProduct_sum] at h0
  simp only [dotProduct_smul, smul_eq_mul] at h0
  rw [Finset.sum_eq_single k (fun l _ hl => by rw [hoff k l (Ne.symm hl), mul_zero]) (by simp)] at h0
  exact (mul_eq_zero.mp h0).resolve_right (hdiag k)

end RankNine
