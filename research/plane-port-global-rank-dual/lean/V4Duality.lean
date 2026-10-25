import Mathlib

/-!
# V4: the abstract half of the clique-dual lower bound on plane-port decoders

A plane-port decoder is a matrix `M = ∑ₖ uₖ vₖᵀ` over any field `F` (e.g. ℚ with arbitrary, also even, denominators) on a finite port set `ι`.

* `identity_block_needs_terms`: if `M` restricted to a port set `S` is the identity, then at least `|S|`
  terms `k` touch `S` on both sides (`uₖ` nonzero somewhere on `S` and `vₖ` nonzero somewhere on `S`).
  For a clique of pairwise non-orthogonal planes the mask forces exactly this identity block.
* `weak_duality`: if every column `x` (a clique) is touched by at least `r x` terms and the weights `lam ≥ 0`
  satisfy `∑_{x touched by k} lam x ≤ cost k` for every term `k`, then `∑ₓ lam x * r x ≤ ∑ₖ cost k`.

Together: any feasible weight vector `lam` on cliques gives `total tariff ≥ ∑_Q lam_Q · 2|Q|`.
The finite feasibility check of a concrete `lam` is a separate, data-dependent step.
-/

open Finset

namespace V4

/-- Weak duality for covering bounds. -/
theorem weak_duality {K X : Type*} [Fintype K] [Fintype X]
    (touch : K → X → Prop) [∀ k x, Decidable (touch k x)]
    (cost : K → ℝ) (lam r : X → ℝ) (hlam : ∀ x, 0 ≤ lam x)
    (hcover : ∀ x, r x ≤ ((univ.filter fun k => touch k x).card : ℝ))
    (hfeas : ∀ k, ∑ x ∈ univ.filter (fun x => touch k x), lam x ≤ cost k) :
    ∑ x, lam x * r x ≤ ∑ k, cost k := by
  have h1 : ∀ x, lam x * ((univ.filter fun k => touch k x).card : ℝ)
      = ∑ k, if touch k x then lam x else 0 := by
    intro x
    rw [Finset.card_filter]
    push_cast
    rw [Finset.mul_sum]
    apply Finset.sum_congr rfl
    intro k _
    split_ifs <;> simp
  calc ∑ x, lam x * r x
      ≤ ∑ x, lam x * ((univ.filter fun k => touch k x).card : ℝ) :=
        Finset.sum_le_sum fun x _ => mul_le_mul_of_nonneg_left (hcover x) (hlam x)
    _ = ∑ x, ∑ k, if touch k x then lam x else 0 := Finset.sum_congr rfl fun x _ => h1 x
    _ = ∑ k, ∑ x, if touch k x then lam x else 0 := Finset.sum_comm
    _ = ∑ k, ∑ x ∈ univ.filter (fun x => touch k x), lam x := by
        apply Finset.sum_congr rfl
        intro k _
        rw [Finset.sum_filter]
    _ ≤ ∑ k, cost k := Finset.sum_le_sum fun k _ => hfeas k

/-- An identity block on a port set `S` needs at least `|S|` rank-one terms touching `S` on both sides. -/
theorem identity_block_needs_terms {F ι K : Type*} [Field F] [DecidableEq F] [Fintype ι] [DecidableEq ι] [Fintype K] [DecidableEq K]
    (u v : K → ι → F) (S : Finset ι)
    (hM : ∀ p ∈ S, ∀ q ∈ S, ∑ k, u k p * v k q = if p = q then 1 else 0) :
    S.card ≤ (univ.filter fun k => (∃ p ∈ S, u k p ≠ 0) ∧ (∃ q ∈ S, v k q ≠ 0)).card := by
  classical
  set T := univ.filter fun k => (∃ p ∈ S, u k p ≠ 0) ∧ (∃ q ∈ S, v k q ≠ 0) with hT
  let w : K → (S → F) := fun k p => u k p
  let W : Submodule (F) (S → F) :=
    Submodule.span (F) ((T.image w : Finset (S → F)) : Set (S → F))
  have key : ∀ q : S, (Pi.single q 1 : S → F) ∈ W := by
    intro q
    have hsum : (Pi.single q 1 : S → F) = ∑ k ∈ T, v k q • w k := by
      funext p
      simp only [Finset.sum_apply, Pi.smul_apply, smul_eq_mul, w]
      have hz : ∀ k ∈ (univ : Finset K), k ∉ T → v k q * u k p = 0 := by
        intro k _ hk
        rw [hT, Finset.mem_filter] at hk
        simp only [Finset.mem_univ, true_and] at hk
        by_cases h : ∃ p ∈ S, u k p ≠ 0
        · have hv : ∀ q ∈ S, v k q = 0 := by
            intro q' hq'
            by_contra hne
            exact hk ⟨h, q', hq', hne⟩
          rw [hv q q.2, zero_mul]
        · push_neg at h
          rw [h p p.2, mul_zero]
      rw [Finset.sum_subset (Finset.subset_univ T) hz]
      have h := hM p p.2 q q.2
      simp_rw [mul_comm (v _ (q : ι))]
      rw [h, Pi.single_apply]
      by_cases hpq : p = q
      · simp [hpq]
      · have : (p : ι) ≠ q := fun e => hpq (Subtype.ext e)
        simp [hpq, this]
    rw [hsum]
    refine Submodule.sum_mem _ fun k hk => Submodule.smul_mem _ _ ?_
    exact Submodule.subset_span (Finset.mem_coe.mpr (Finset.mem_image_of_mem w hk))
  have htop : W = ⊤ := by
    rw [eq_top_iff, ← (Pi.basisFun (F) S).span_eq, Submodule.span_le]
    rintro _ ⟨q, rfl⟩
    simpa [Pi.basisFun_apply] using key q
  calc S.card = Fintype.card S := (Fintype.card_coe S).symm
    _ = Module.finrank (F) (S → F) := (Module.finrank_fintype_fun_eq_card (F)).symm
    _ = Module.finrank (F) W := by rw [htop, finrank_top]
    _ ≤ (T.image w).card := finrank_span_finset_le_card _
    _ ≤ T.card := Finset.card_image_le

end V4

#print axioms V4.weak_duality
#print axioms V4.identity_block_needs_terms
