import BForm.Rank

/-!
# Supports, label blocks and the cost of a decoder

Ports `L`, labels `lab : L → F₂⁹`, the table `B[t,s] = lab t ⬝ lab s`.  A decoder with terms `j : ι` has row supports
`R j = {t | P t j ≠ 0}` and column supports `A j = {s | Q s j ≠ 0}`, and costs `Σ_j rank_F₂ B[R j, A j]`.
-/

namespace BForm

open Matrix Module

attribute [local instance] Classical.propDecidable

set_option linter.unusedSectionVars false

abbrev V9 := Fin 9 → ZMod 2

variable {L : Type*} [Fintype L] [DecidableEq L] (lab : L → V9)

/-- The label table restricted to rows `R` and columns `S`. -/
def block (R S : Finset L) : Matrix R S (ZMod 2) := fun t s => lab t ⬝ᵥ lab s

/-- The matrix whose rows are the labels of `R`. -/
def labMat (R : Finset L) : Matrix R (Fin 9) (ZMod 2) := fun t => lab t

theorem block_eq (R S : Finset L) : block lab R S = labMat lab R * (labMat lab S)ᵀ := by
  ext t s; simp [block, labMat, Matrix.mul_apply, dotProduct]

/-- Label span dimension of a set of ports. -/
noncomputable def lspan (R : Finset L) : ℕ := (labMat lab R).rank

/-- Rank formula, lower bound: `rank B[R,S] ≥ dim span l(R) + dim span l(S) - 9`. -/
theorem block_rank_ge (R S : Finset L) : lspan lab R + lspan lab S ≤ (block lab R S).rank + 9 := by
  have := rank_mul_ge (labMat lab R) (labMat lab S)ᵀ
  rw [Matrix.rank_transpose, ← block_eq] at this
  simpa [lspan] using this

variable {K : Type*} [Field K] {ι : Type*} [Fintype ι]

/-- Row and column supports of the term `j`. -/
noncomputable def rowSupp (P : Matrix L ι K) (j : ι) : Finset L := Finset.univ.filter fun t => P t j ≠ 0

/-- The cost of a decoder `(P, Q)`. -/
noncomputable def cost (P Q : Matrix L ι K) : ℕ :=
  ∑ j, (block lab (rowSupp P j) (rowSupp Q j)).rank

/-- Capacity (finite fact S0, `f(7) = 36`): a set of at least 37 ports has label span of dimension at least 8. -/
def Capacity : Prop := ∀ R : Finset L, 37 ≤ R.card → 8 ≤ lspan lab R

/-- A term whose row and column supports both hold at least 37 ports costs at least 7. -/
theorem term_ge_seven (hcap : Capacity lab) (R S : Finset L) (hR : 37 ≤ R.card) (hS : 37 ≤ S.card) :
    7 ≤ (block lab R S).rank := by
  have := block_rank_ge lab R S
  have := hcap R hR; have := hcap S hS
  omega

/-- Eight terms of cost at least 7 give cost at least 56. -/
theorem cost_ge_56 (P Q : Matrix L ι K) (J : Finset ι) (hJ : 8 ≤ J.card)
    (h7 : ∀ j ∈ J, 7 ≤ (block lab (rowSupp P j) (rowSupp Q j)).rank) : 56 ≤ cost lab P Q := by
  calc 56 ≤ 7 * J.card := by omega
    _ = ∑ j ∈ J, 7 := by simp [mul_comm]
    _ ≤ ∑ j ∈ J, (block lab (rowSupp P j) (rowSupp Q j)).rank := Finset.sum_le_sum h7
    _ ≤ cost lab P Q := Finset.sum_le_sum_of_subset_of_nonneg (Finset.subset_univ _) (by intros; omega)

end BForm
