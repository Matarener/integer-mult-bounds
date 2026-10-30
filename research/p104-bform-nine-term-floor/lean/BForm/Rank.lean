import Mathlib

/-!
# A. Sylvester's inequality and the rank formula for label blocks

`rank (A * B) ≥ rank A + rank B - card k` for `A : m × k`, `B : k × n` over a field.  For the label table
`B[t,s] = l_t ⬝ l_s` over `F₂` this gives `rank B[R, A] ≥ dim span l(R) + dim span l(A) - 9`.
-/

namespace BForm

open Matrix Module

variable {F : Type*} [Field F]

/-- Restricting a linear map to a subspace loses at most the kernel. -/
theorem finrank_le_map_add_ker {V W : Type*} [AddCommGroup V] [Module F V] [FiniteDimensional F V]
    [AddCommGroup W] [Module F W] (f : V →ₗ[F] W) (S : Submodule F V) :
    finrank F S ≤ finrank F (S.map f) + finrank F (LinearMap.ker f) := by
  have h := LinearMap.finrank_range_add_finrank_ker (f.domRestrict S)
  rw [LinearMap.range_domRestrict] at h
  have hk : finrank F (LinearMap.ker (f.domRestrict S)) ≤ finrank F (LinearMap.ker f) := by
    let g : LinearMap.ker (f.domRestrict S) →ₗ[F] LinearMap.ker f :=
      { toFun := fun x => ⟨(x.1 : V), LinearMap.mem_ker.mpr (LinearMap.mem_ker.mp x.2)⟩
        map_add' := fun x y => rfl
        map_smul' := fun c x => rfl }
    apply LinearMap.finrank_le_finrank_of_injective (f := g)
    intro x y hxy
    apply Subtype.ext; apply Subtype.ext
    exact congrArg (fun z : LinearMap.ker f => (z : V)) hxy
  omega

variable {m n k : Type*} [Fintype n] [Fintype k]

/-- Sylvester's rank inequality. -/
theorem rank_mul_ge (A : Matrix m k F) (B : Matrix k n F) :
    A.rank + B.rank ≤ (A * B).rank + Fintype.card k := by
  have hA := LinearMap.finrank_range_add_finrank_ker A.mulVecLin
  have hmap := finrank_le_map_add_ker A.mulVecLin (LinearMap.range B.mulVecLin)
  have hr : (LinearMap.range B.mulVecLin).map A.mulVecLin = LinearMap.range (A * B).mulVecLin := by
    rw [Matrix.mulVecLin_mul, LinearMap.range_comp]
  rw [hr] at hmap
  simp only [Matrix.rank, Module.finrank_fintype_fun_eq_card] at *
  omega

/-- If `A * B = 0` then `rank A + rank B ≤ card k`. -/
theorem rank_add_rank_le_of_mul_eq_zero (A : Matrix m k F) (B : Matrix k n F) (h : A * B = 0) :
    A.rank + B.rank ≤ Fintype.card k := by
  have := rank_mul_ge A B
  rw [h, Matrix.rank_zero] at this
  omega

end BForm
