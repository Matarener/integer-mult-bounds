import BForm.CaseI

/-!
# The case of a term with zero root part in its column vector (`y_{j₀} = 0`)

Then the other eight terms carry dual bases `(x_j)`, `(y_j)` of `K⁸`, their lift coordinates `a_j`, `b_j` vanish, and
each of them is a pure Gram term: rows `N(x_j) \ Z_r`, columns `N(y_j) \ Z_c`, where `Z_r = {α = 0}`, `Z_c = {α' = 0}`
hold at most 4 ports.  So each costs `≥ 7` (BFORM3 step 1 / BFORM4).
-/

namespace BForm

open Matrix

attribute [local instance] Classical.propDecidable

set_option linter.unusedSectionVars false

variable {K : Type*} [Field K] {L : Type*} [Fintype L] [DecidableEq L]

/-- Rows of a term `X * U` with zero lift coordinate: the support contains `N(x) \ {α = 0}`. -/
theorem supp_pure (r : L → Fin 8 → K) (α c : L → K) (U : Matrix C9 C9 K) (j : C9) (ha : U none j = 0) :
    nonorth r (fun k => U (some k) j) \ Finset.univ.filter (fun t => α t = 0) ⊆ rowSupp (bX r α c * U) j := by
  intro t ht
  simp only [Finset.mem_sdiff, nonorth, Finset.mem_filter, Finset.mem_univ, true_and] at ht
  simp only [rowSupp, Finset.mem_filter, Finset.mem_univ, true_and, bX_mul_apply, ha, mul_zero, zero_add]
  exact mul_ne_zero ht.2 ht.1

theorem yzero (lab : L → V9) (hcap : Capacity lab) (r : L → Fin 8 → K) (hroot : RootFact r)
    (α α' c β : L → K) (hα' : ∀ t, β t = 0 → α' t ≠ 0)
    (hZr : (Finset.univ.filter fun t => α t = 0).card ≤ 4) (hB : (Finset.univ.filter fun t => β t ≠ 0).card ≤ 4)
    (U W : Matrix C9 C9 K) (hUW : U * Wᵀ = 1) (j₀ : C9) (hy : (fun k => W (some k) j₀) = 0)
    (P Q : Matrix L C9 K) (hP : P = bX r α c * U) (hQ : Q = bX r α' β * W) : 56 ≤ cost lab P Q := by
  set J0 : Finset C9 := Finset.univ.erase j₀
  have hJ0 : J0.card = 8 := by simp [J0, Finset.card_erase_of_mem]
  let Xm : Matrix (Fin 8) J0 K := fun k j => U (some k) j
  let Ym : Matrix (Fin 8) J0 K := fun k j => W (some k) j
  have hsum : ∀ (f : C9 → K), f j₀ = 0 → ∑ j : J0, f j = ∑ j, f j := by
    intro f hf
    rw [Finset.sum_coe_sort J0 f]
    exact Finset.sum_subset (Finset.subset_univ _) (fun j _ hj => by
      simp only [J0, Finset.mem_erase, Finset.mem_univ, and_true, not_not] at hj; subst hj; exact hf)
  have hy0 : ∀ k, W (some k) j₀ = 0 := fun k => congrFun hy k
  have hxy : Xm * Ymᵀ = 1 := by
    ext a b
    have hab := congrFun (congrFun hUW (some a)) (some b)
    simp only [Matrix.mul_apply, Matrix.transpose_apply, Matrix.one_apply, Option.some.injEq] at hab ⊢
    rw [← hab, hsum (fun j => U (some a) j * W (some b) j) (by simp [hy0])]
  have hyx : Ymᵀ * Xm = 1 := (Matrix.mul_eq_one_comm_of_card_eq (Fin 8) J0 K (A := Xm) (B := Ymᵀ) (by simp [hJ0])).mp hxy
  have hxy' : Xmᵀ * Ym = 1 := by simpa [Matrix.transpose_mul] using congrArg Matrix.transpose hyx
  -- the lift coordinates `a_j` vanish on J0 (`Σ_j a_j y_j = 0` and the `y_j` are a basis)
  have ha : ∀ j : J0, U none j = 0 := by
    let av : J0 → K := fun j => U none j
    have h0 : Ym *ᵥ av = 0 := by
      funext k
      have := congrFun (congrFun hUW none) (some k)
      simp only [Matrix.mul_apply, Matrix.transpose_apply, Matrix.one_apply, reduceCtorEq, if_false] at this
      simp only [Matrix.mulVec, dotProduct, Pi.zero_apply, Ym, av]
      rw [← this, ← hsum (fun j => U none j * W (some k) j) (by simp [hy0])]
      exact Finset.sum_congr rfl (fun j _ => mul_comm _ _)
    intro j
    have : av = 0 := by
      calc av = (Xmᵀ * Ym) *ᵥ av := by rw [hxy', Matrix.one_mulVec]
        _ = Xmᵀ *ᵥ (Ym *ᵥ av) := (Matrix.mulVec_mulVec _ _ _).symm
        _ = 0 := by rw [h0, Matrix.mulVec_zero]
    exact congrFun this j
  -- root parts are non-zero on J0
  have hx : ∀ j : J0, (fun k => U (some k) j) ≠ 0 := by
    intro j h
    have := congrFun (congrFun hyx j) j
    simp only [Matrix.mul_apply, Matrix.transpose_apply, Matrix.one_apply_eq] at this
    have h' : ∀ k, Xm k j = 0 := fun k => congrFun h k
    simp [h'] at this
  have hyn : ∀ j : J0, (fun k => W (some k) j) ≠ 0 := by
    intro j h
    have := congrFun (congrFun hyx j) j
    simp only [Matrix.mul_apply, Matrix.transpose_apply, Matrix.one_apply_eq] at this
    have h' : ∀ k, Ym k j = 0 := fun k => congrFun h k
    simp [h'] at this
  refine cost_ge_56 lab P Q J0 (by omega) ?_
  intro j hj
  apply term_ge_seven lab hcap
  · have hsub := supp_pure r α c U j (ha ⟨j, hj⟩)
    rw [← hP] at hsub
    have h49 : 49 ≤ (nonorth r fun k => U (some k) j).card := hroot _ (hx ⟨j, hj⟩)
    have := Finset.card_le_card hsub
    have := Finset.le_card_sdiff (Finset.univ.filter fun t => α t = 0) (nonorth r fun k => U (some k) j)
    omega
  · have hsub := supp_off_lift r α' β hα' W j
    rw [← hQ] at hsub
    have h49 : 49 ≤ (nonorth r fun k => W (some k) j).card := hroot _ (hyn ⟨j, hj⟩)
    have := Finset.card_le_card hsub
    have := Finset.le_card_sdiff (Finset.univ.filter fun t => β t ≠ 0) (nonorth r fun k => W (some k) j)
    omega

end BForm
