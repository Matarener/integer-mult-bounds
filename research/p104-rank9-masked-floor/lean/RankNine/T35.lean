import RankNine.T3
import BForm

set_option linter.unusedSectionVars false

/-!
# T3.5: the T3 output as a B-form

Ports `Fin 104`; BForm roots `r : Fin 104 → Fin 8 → K` with `ρ_a·ρ_b = (9/4) r_a·r_b` (`hr`; for `r = rK`, the
E8 coordinates of #6188, this is a finite check).  If every row is `P v = a_v ρ_v + λ_v Λ` and every column is
`c s = b_s ρ_s`, then `M v s = α_v α'_s r_v·r_s + λ_v β_s` with `α = (9/4) a`, `α' = b`,
`β_s = b_s Λ·ρ_s + η_s`: the ordinary B-form, with the diagonal and biclique conditions of `bform_floor`
(`bform_F1`).
-/

namespace RankNine

open Matrix

variable {K : Type*} [Field K] [CharZero K]

theorem bX_bX_apply (r : Fin 104 → Fin 8 → K) (α c α' β : Fin 104 → K) (t s : Fin 104) :
    (BForm.bX r α c * (BForm.bX r α' β)ᵀ) t s = c t * β s + α t * α' s * (r t ⬝ᵥ r s) := by
  simp only [Matrix.mul_apply, Matrix.transpose_apply, BForm.bX, Fintype.sum_option, Option.elim, dotProduct,
    Finset.mul_sum]
  congr 1
  refine Finset.sum_congr rfl fun k _ => ?_
  ring

/-- **(F1)** the ordinary B-form from glued rows and gramm columns -/
theorem bform_F1 (r : Fin 104 → Fin 8 → K) (hr : ∀ a b : Fin 104, ((dot a b : ℤ) : K) = 9 / 4 * (r a ⬝ᵥ r b))
    (N : Matrix (Fin 104) (Fin 104) K) (P c : ℕ → Fin 9 → K) (lam eta : ℕ → K) (Λ : Fin 9 → K)
    (hN : ∀ v s : Fin 104, N v s = P v ⬝ᵥ c s + lam v * eta s)
    (hrow : ∀ v < 104, ∃ a : K, P v = a • rho K v + lam v • Λ) (hcol : ∀ s < 104, ∃ b : K, c s = b • rho K s)
    (hdiag : ∀ t, N t t ≠ 0) (hmask : ∀ u s : Fin 104, dot u s = 0 → N u s = 0) :
    ∃ α α' cc β : Fin 104 → K, (∀ t, (cc t = 0 ∨ β t = 0) → α t ≠ 0 ∧ α' t ≠ 0) ∧
      (∀ u s, cc u ≠ 0 → β s ≠ 0 → u ≠ s → ¬ BForm.Orth r u s) ∧
      BForm.Pattern r (BForm.bX r α cc * (BForm.bX r α' β)ᵀ) ∧ N = BForm.bX r α cc * (BForm.bX r α' β)ᵀ := by
  choose! a ha using hrow
  choose! b hb using hcol
  set α : Fin 104 → K := fun t => 9 / 4 * a t
  set α' : Fin 104 → K := fun t => b t
  set cc : Fin 104 → K := fun t => lam t
  set β : Fin 104 → K := fun t => b t * (Λ ⬝ᵥ rho K t) + eta t
  have hform : N = BForm.bX r α cc * (BForm.bX r α' β)ᵀ := by
    ext t s
    rw [bX_bX_apply, hN, ha t t.2, hb s s.2]
    simp only [add_dotProduct, smul_dotProduct, dotProduct_smul, smul_eq_mul, rho_dot, hr, α, α', cc, β]
    ring
  have hent : ∀ t s : Fin 104, N t s = cc t * β s + α t * α' s * (r t ⬝ᵥ r s) := by
    intro t s; rw [hform, bX_bX_apply]
  have hrr : ∀ t : Fin 104, r t ⬝ᵥ r t = 8 := by
    intro t
    have h := hr t t
    rw [dot_self t.2] at h
    have : (9 / 4 : K) * (r t ⬝ᵥ r t) = 18 := by rw [← h]; norm_num
    linear_combination (4 / 9 : K) * this
  refine ⟨α, α', cc, β, fun t ht => ?_, fun u s hu hs hus ho => ?_, ⟨fun t => ?_, fun u s hus ho => ?_⟩, hform⟩
  · have e := hdiag t
    rw [hent, hrr] at e
    rcases ht with h0 | h0 <;> rw [h0] at e <;> simp only [zero_mul, mul_zero, zero_add] at e <;>
      exact ⟨left_ne_zero_of_mul (left_ne_zero_of_mul e), right_ne_zero_of_mul (left_ne_zero_of_mul e)⟩
  · have hd : dot u s = 0 := by
      have h := hr u s
      unfold BForm.Orth at ho
      rw [ho, mul_zero] at h
      exact_mod_cast h
    have e := hmask u s hd
    rw [hent] at e
    unfold BForm.Orth at ho
    rw [ho, mul_zero, add_zero] at e
    exact mul_ne_zero hu hs e
  · rw [← hform]; exact hdiag t
  · rw [← hform]
    apply hmask
    have h := hr u s
    unfold BForm.Orth at ho
    rw [ho, mul_zero] at h
    exact_mod_cast h

end RankNine
