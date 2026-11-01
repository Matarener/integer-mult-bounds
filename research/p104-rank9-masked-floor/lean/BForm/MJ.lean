import BForm.Rank

/-!
# C. The M_J bound

Rows `w t` (here `w t = (p₀(t), c_t)`) and an invertible `U`; the decoder rows are `P = w * U`.  If every row of a set
`T` is dead for every term of `J` (`P t j = 0`), then the rows `w t, t ∈ T` span at most `card r - card J` dimensions.
In the B-form `card r = 9`, so `rank p₀(M_J) ≤ rank w(M_J) ≤ 9 - |J|` (BFORM3 step 2; the repo's case-(b) bound).
-/

namespace BForm

open Matrix

variable {F : Type*} [Field F] {T r J : Type*} [Fintype T] [Fintype r] [Fintype J] [DecidableEq r] [DecidableEq J]

/-- The selection matrix of an embedding `J ↪ r`. -/
def selMat (e : J ↪ r) : Matrix r J F := fun i j => if i = e j then 1 else 0

set_option linter.unusedSectionVars false

theorem mul_selMat (A : Matrix T r F) (e : J ↪ r) (t : T) (j : J) :
    (A * selMat (F := F) e) t j = A t (e j) := by
  simp [Matrix.mul_apply, selMat]

theorem selMat_t_mul (e : J ↪ r) : (selMat (F := F) e)ᵀ * selMat (F := F) e = 1 := by
  ext a b
  rw [Matrix.mul_apply]
  simp only [Matrix.transpose_apply, selMat, ite_mul, one_mul, zero_mul, Finset.sum_ite_eq', Finset.mem_univ,
    if_true, Matrix.one_apply, e.injective.eq_iff]

theorem mj_bound (w : Matrix T r F) (U : Matrix r r F) (hU : IsUnit U.det) (e : J ↪ r)
    (hdead : ∀ t j, (w * U) t (e j) = 0) : w.rank + Fintype.card J ≤ Fintype.card r := by
  have hzero : w * (U * selMat (F := F) e) = 0 := by
    ext t j
    rw [← Matrix.mul_assoc, mul_selMat, hdead, Matrix.zero_apply]
  have h1 := rank_add_rank_le_of_mul_eq_zero w (U * selMat (F := F) e) hzero
  have hS : (U * (selMat (F := F) e)).rank = Fintype.card J := by
    rw [Matrix.rank_mul_eq_right_of_isUnit_det U _ hU]
    apply le_antisymm (Matrix.rank_le_card_width _)
    have := Matrix.rank_mul_le_right (selMat (F := F) e)ᵀ (selMat (F := F) e)
    rw [selMat_t_mul, Matrix.rank_one] at this
    exact this
  omega

end BForm
