import BForm.Main

/-!
# Generalized B-form (rank-9 masked floor, T3.5)

`M = X Yᵀ` with `X = bX r α c` (every row a multiple of its root plus a lift coordinate) and `Y` arbitrary on a set
`Bs` of at most 4 ports, `Y t = (0, α' t • r t)` with `α' t ≠ 0` off `Bs`.  The proof of case II (`caseII`) uses
the rows of `Y` only through the normal form (any `Y` with a left inverse) and through the support of the column
vectors off `Bs`; here it is repeated with those two places generalized (`supp_gen`, `yzero_gen`, `caseII_gen`).
The rows of `X` with `α = 0` must form a clique of at most 4 ports (in the ordinary B-form this followed from
`hdiag` and `hbi`).
-/

namespace BForm

open Matrix

attribute [local instance] Classical.propDecidable

set_option linter.unusedSectionVars false

variable {K : Type*} [Field K] {L : Type*} [Fintype L] [DecidableEq L]

/-- rows off `Bs` are pure root rows -/
def GenRows (r : L → Fin 8 → K) (Y : Matrix L C9 K) (Bs : Finset L) (α' : L → K) : Prop :=
  ∀ t, t ∉ Bs → α' t ≠ 0 ∧ ∀ i, Y t i = bX r α' (fun _ => 0) t i

theorem supp_gen (r : L → Fin 8 → K) (Y : Matrix L C9 K) (Bs : Finset L) (α' : L → K) (hY : GenRows r Y Bs α')
    (W : Matrix C9 C9 K) (j : C9) :
    nonorth r (fun k => W (some k) j) \ Bs ⊆ rowSupp (Y * W) j := by
  intro t ht
  simp only [Finset.mem_sdiff, nonorth, Finset.mem_filter, Finset.mem_univ, true_and] at ht
  obtain ⟨hα, hrow⟩ := hY t ht.2
  have e : (Y * W) t j = (bX r α' (fun _ => 0) * W) t j := by
    simp only [Matrix.mul_apply, hrow]
  simp only [rowSupp, Finset.mem_filter, Finset.mem_univ, true_and]
  rw [e, bX_mul_apply, zero_mul, zero_add]
  exact mul_ne_zero hα ht.1

theorem yzero_gen (lab : L → V9) (hcap : Capacity lab) (r : L → Fin 8 → K) (hroot : RootFact r)
    (α c : L → K) (Y : Matrix L C9 K) (Bs : Finset L) (α' : L → K) (hY : GenRows r Y Bs α')
    (hZr : (Finset.univ.filter fun t => α t = 0).card ≤ 4) (hB : Bs.card ≤ 4)
    (U W : Matrix C9 C9 K) (hUW : U * Wᵀ = 1) (j₀ : C9) (hy : (fun k => W (some k) j₀) = 0)
    (P Q : Matrix L C9 K) (hP : P = bX r α c * U) (hQ : Q = Y * W) : 56 ≤ cost lab P Q := by
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
  · have hsub := supp_gen r Y Bs α' hY W j
    rw [← hQ] at hsub
    have h49 : 49 ≤ (nonorth r fun k => W (some k) j).card := hroot _ (hyn ⟨j, hj⟩)
    have := Finset.card_le_card hsub
    have := Finset.le_card_sdiff Bs (nonorth r fun k => W (some k) j)
    omega

/-- **Generalized case II.** -/
theorem caseII_gen (lab : L → V9) (hcap : Capacity lab) (r : L → Fin 8 → K) (hroot : RootFact r)
    (hspan : SpanFact lab r) (hcensus : CensusFact lab r)
    (α c : L → K) (Y : Matrix L C9 K) (Bs : Finset L) (α' : L → K) (hY : GenRows r Y Bs α') (hB : Bs.card ≤ 4)
    (hZr : (Finset.univ.filter fun t => α t = 0).card ≤ 4) (hcl : IsClique r (Finset.univ.filter fun t => α t = 0))
    (hpat : Pattern r (bX r α c * Yᵀ))
    (Xl Yl : Matrix C9 L K) (hX : Xl * bX r α c = 1) (hYl : Yl * Y = 1)
    (P Q : Matrix L C9 K) (h : bX r α c * Yᵀ = P * Qᵀ) : 56 ≤ cost lab P Q := by
  obtain ⟨hUW, hP, hQ⟩ := normal_form _ _ P Q Xl Yl hX hYl h
  set U := Xl * P; set W := Yl * Q
  set Zr := Finset.univ.filter fun t => α t = 0
  by_cases hy0 : ∃ j, (fun k => W (some k) j) = 0
  · obtain ⟨j₀, hj₀⟩ := hy0
    exact yzero_gen lab hcap r hroot α c Y Bs α' hY hZr hB U W hUW j₀ hj₀ P Q hP hQ
  push Not at hy0
  apply hcensus Zr P Q hZr hcl
  · rw [← h]; exact hpat
  · intro J T hdead
    let w : Matrix T C9 K := Matrix.of fun (t : T) (i : C9) => bX r α c t i
    have hU : IsUnit U.det := Matrix.isUnit_det_of_right_inverse hUW
    have hd : ∀ (t : T) (j : J), (w * U) t ((Function.Embedding.subtype (· ∈ J)) j) = 0 := by
      intro t j
      have := hdead t.1 t.2 j.1 j.2
      rw [hP] at this
      simpa [w, Matrix.mul_apply] using this
    have hmj := mj_bound w U hU (Function.Embedding.subtype (· ∈ J)) hd
    have hle : rootRank r (T \ Zr) ≤ w.rank := rootRank_le r α c T Zr (fun t ht => by
      simpa [Zr] using ht)
    simp only [Fintype.card_coe, Fintype.card_option, Fintype.card_fin] at hmj
    omega
  · intro j
    have hsub := supp_gen r Y Bs α' hY W j
    rw [← hQ] at hsub
    have h49 : 49 ≤ (nonorth r fun k => W (some k) j).card := hroot _ (hy0 j)
    have hcard : 45 ≤ (rowSupp Q j).card := by
      have := Finset.card_le_card hsub
      have := Finset.le_card_sdiff Bs (nonorth r fun k => W (some k) j)
      omega
    refine ⟨hcap _ (by omega), ?_⟩
    intro z hz hzero
    rcases hspan _ (hy0 j) Bs hB z hz (fun t ht => hzero t (hsub ht)) with h1 | ⟨w, -, hw⟩
    · left
      apply rank_le_seven _ (fun k => W (some k) j) (hy0 j)
      funext t
      have ht := t.2
      simp only [labO, Finset.mem_filter, Finset.mem_univ, true_and] at ht
      have : (t : L) ∉ nonorth r (fun k => W (some k) j) := fun hn => ht (h1 t hn)
      simp only [nonorth, Finset.mem_filter, Finset.mem_univ, true_and, not_not] at this
      simpa [Matrix.mulVec, dotProduct] using this
    · exact Or.inr ⟨w, hw⟩

end BForm
