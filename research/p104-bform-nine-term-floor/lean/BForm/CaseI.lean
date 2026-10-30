import BForm.Cost
import BForm.NormalForm

/-!
# D. Case I of the B-form floor (BFORM2): `|A|, |B| ≤ 12` gives cost `≥ 56`

B-form realisation `M = D₁ G D₂ + c βᵀ` with `G = R Rᵀ` (roots `r t ∈ K⁸`), written `M = X Yᵀ` with
`X t = (c t, α t • r t)`, `Y t = (β t, α' t • r t)`; columns indexed by `Option (Fin 8)` (`none` = the lift).
A nine-term decoder is `P, Q : L × Option (Fin 8)` with `P Qᵀ = M`.
Inputs used as hypotheses (finite facts, checked by enumeration in `spanlemma.py` / Kaggle `p104-bform-floor`):
`RootFact` (S1: every `x ≠ 0` is non-orthogonal to at least 49 ports) and `Capacity` (S0: `f(7) = 36`).
-/

namespace BForm

open Matrix

attribute [local instance] Classical.propDecidable

set_option linter.unusedSectionVars false
set_option linter.unusedSimpArgs false

variable {K : Type*} [Field K] {L : Type*} [Fintype L] [DecidableEq L]

abbrev C9 := Option (Fin 8)

/-- `X t = (c t, α t • r t)`. -/
def bX (r : L → Fin 8 → K) (α c : L → K) : Matrix L C9 K := fun t i => Option.elim i (c t) (fun k => α t * r t k)

/-- Ports non-orthogonal to `x`. -/
noncomputable def nonorth (r : L → Fin 8 → K) (x : Fin 8 → K) : Finset L := Finset.univ.filter fun t => r t ⬝ᵥ x ≠ 0

/-- Finite fact S1. -/
def RootFact (r : L → Fin 8 → K) : Prop := ∀ x : Fin 8 → K, x ≠ 0 → 49 ≤ (nonorth r x).card

theorem bX_mul_apply (r : L → Fin 8 → K) (α c : L → K) (U : Matrix C9 C9 K) (t : L) (j : C9) :
    (bX r α c * U) t j = c t * U none j + α t * (r t ⬝ᵥ fun k => U (some k) j) := by
  simp [bX, Matrix.mul_apply, Fintype.sum_option, dotProduct, Finset.mul_sum, mul_assoc]

/-- Off the lift support, the support of a term `X * u` is exactly the non-orthogonal set of its root part. -/
theorem supp_off_lift (r : L → Fin 8 → K) (α c : L → K) (hα : ∀ t, c t = 0 → α t ≠ 0)
    (U : Matrix C9 C9 K) (j : C9) :
    nonorth r (fun k => U (some k) j) \ Finset.univ.filter (fun t => c t ≠ 0) ⊆ rowSupp (bX r α c * U) j := by
  intro t ht
  simp only [Finset.mem_sdiff, nonorth, Finset.mem_filter, Finset.mem_univ, true_and, not_not] at ht
  simp only [rowSupp, Finset.mem_filter, Finset.mem_univ, true_and, bX_mul_apply, ht.2, zero_mul, zero_add]
  exact mul_ne_zero (hα t ht.2) ht.1

/-- At least 8 of the nine terms have both root parts non-zero (`Σ_j x_j y_jᵀ = I₈`). -/
theorem eight_live (U W : Matrix C9 C9 K) (h : U * Wᵀ = 1) :
    8 ≤ (Finset.univ.filter fun j : C9 =>
      (fun k => U (some k) j) ≠ 0 ∧ (fun k => W (some k) j) ≠ 0).card := by
  classical
  set J := Finset.univ.filter fun j : C9 => (fun k => U (some k) j) ≠ 0 ∧ (fun k => W (some k) j) ≠ 0
  let Xm : Matrix (Fin 8) J K := fun k j => U (some k) j
  let Ym : Matrix (Fin 8) J K := fun k j => W (some k) j
  have hxy : Xm * Ymᵀ = 1 := by
    ext a b
    have hab := congrFun (congrFun h (some a)) (some b)
    simp only [Matrix.mul_apply, Matrix.transpose_apply, Matrix.one_apply, Option.some.injEq] at hab ⊢
    rw [← hab]
    symm
    rw [← Finset.sum_subset (Finset.subset_univ J) ?_]
    · exact (Finset.sum_coe_sort J (fun j => U (some a) j * W (some b) j)).symm
    · intro j _ hj
      simp only [J, Finset.mem_filter, Finset.mem_univ, true_and, not_and_or, not_not] at hj
      rcases hj with hj | hj
      · have := congrFun hj a; simp only [Pi.zero_apply] at this; simp [this]
      · have := congrFun hj b; simp only [Pi.zero_apply] at this; simp [this]
  have h1 : (Xm * Ymᵀ).rank ≤ Xm.rank := Matrix.rank_mul_le_left _ _
  rw [hxy, Matrix.rank_one, Fintype.card_fin] at h1
  have h2 := Matrix.rank_le_card_width Xm
  simp only [Fintype.card_coe] at h2
  omega

/-- **Case I.** -/
theorem caseI (lab : L → V9) (hcap : Capacity lab) (r : L → Fin 8 → K) (hroot : RootFact r)
    (α α' c β : L → K) (hα : ∀ t, c t = 0 → α t ≠ 0) (hα' : ∀ t, β t = 0 → α' t ≠ 0)
    (hA : (Finset.univ.filter fun t => c t ≠ 0).card ≤ 12) (hB : (Finset.univ.filter fun t => β t ≠ 0).card ≤ 12)
    (Xl Yl : Matrix C9 L K) (hX : Xl * bX r α c = 1) (hY : Yl * bX r α' β = 1)
    (P Q : Matrix L C9 K) (h : bX r α c * (bX r α' β)ᵀ = P * Qᵀ) : 56 ≤ cost lab P Q := by
  obtain ⟨hUW, hP, hQ⟩ := normal_form _ _ P Q Xl Yl hX hY h
  set U := Xl * P; set W := Yl * Q
  refine cost_ge_56 lab P Q _ (eight_live U W hUW) ?_
  intro j hj
  simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hj
  apply term_ge_seven lab hcap
  · have hsub := supp_off_lift r α c hα U j
    rw [← hP] at hsub
    have h49 := hroot _ hj.1
    have := Finset.card_le_card hsub
    have := Finset.le_card_sdiff (Finset.univ.filter fun t => c t ≠ 0) (nonorth r fun k => U (some k) j)
    omega
  · have hsub := supp_off_lift r α' β hα' W j
    rw [← hQ] at hsub
    have h49 := hroot _ hj.2
    have := Finset.card_le_card hsub
    have := Finset.le_card_sdiff (Finset.univ.filter fun t => β t ≠ 0) (nonorth r fun k => W (some k) j)
    omega

end BForm
