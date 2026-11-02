import BForm.Cost

/-!
# Reduction (NOTE §1, Lemmas 1–2)

`two_cheap`: a nine-term decoder of cost `< 56` has two distinct terms of rank `≤ 6`.
`cheap_side`: a term of rank `≤ 6` has a side whose live labels span at most `F₂⁷` (rank formula `block_rank_ge`).
`two_dual`: labels spanning at most `F₂⁷` are killed by two distinct non-zero `z₁, z₂ ∈ F₂⁹`, so the dead set of that
side contains `C(z₁, z₂) = {t : lab t ⬝ z₁ ≠ 0 ∨ lab t ⬝ z₂ ≠ 0}`.
`reduce`: cost `< 56` ⇒ two distinct terms, each with a big dead side `⊇ C(z₁, z₂)`.
-/

namespace RankNine.Red

open Matrix Module BForm

attribute [local instance] Classical.propDecidable

set_option linter.unusedSectionVars false

variable {L : Type*} [Fintype L] [DecidableEq L] (lab : L → V9)
variable {K : Type*} [Field K] {ι : Type*} [Fintype ι]

/-- Lemma 1: cost `< 56` with nine terms ⇒ two distinct terms of rank `≤ 6`. -/
theorem two_cheap (P Q : Matrix L ι K) (hι : Fintype.card ι = 9) (h : cost lab P Q < 56) :
    ∃ j k, j ≠ k ∧ (block lab (rowSupp P j) (rowSupp Q j)).rank ≤ 6 ∧
      (block lab (rowSupp P k) (rowSupp Q k)).rank ≤ 6 := by
  let p : ι → Prop := fun j => 7 ≤ (block lab (rowSupp P j) (rowSupp Q j)).rank
  have hJ : (Finset.univ.filter p).card ≤ 7 := by
    by_contra hc
    have := cost_ge_56 lab P Q (Finset.univ.filter p) (by omega) (fun j hj => (Finset.mem_filter.mp hj).2)
    omega
  have hsum := Finset.filter_card_add_filter_neg_card_eq_card (s := (Finset.univ : Finset ι)) p
  rw [Finset.card_univ, hι] at hsum
  obtain ⟨j, hj, k, hk, hjk⟩ := Finset.one_lt_card.mp (by omega : 1 < (Finset.univ.filter fun j => ¬ p j).card)
  simp only [Finset.mem_filter, Finset.mem_univ, true_and, p, not_le] at hj hk
  exact ⟨j, k, hjk, by omega, by omega⟩

/-- Lemma 2, rank part: a term of rank `≤ 6` has a side of label span `≤ 7`. -/
theorem cheap_side (R S : Finset L) (h : (block lab R S).rank ≤ 6) : lspan lab R ≤ 7 ∨ lspan lab S ≤ 7 := by
  have := block_rank_ge lab R S
  omega

/-- Lemma 2, dual part: label span `≤ 7` ⇒ two distinct non-zero `z₁, z₂` orthogonal to every live label. -/
theorem two_dual (R : Finset L) (h : lspan lab R ≤ 7) :
    ∃ z1 z2 : V9, z1 ≠ 0 ∧ z2 ≠ 0 ∧ z1 ≠ z2 ∧ ∀ t ∈ R, lab t ⬝ᵥ z1 = 0 ∧ lab t ⬝ᵥ z2 = 0 := by
  let f := (labMat lab R).mulVecLin
  have hrn := LinearMap.finrank_range_add_finrank_ker f
  have hr : finrank (ZMod 2) (LinearMap.range f) ≤ 7 := h
  rw [Module.finrank_fin_fun] at hrn
  have hk : 2 ≤ finrank (ZMod 2) (LinearMap.ker f) := by omega
  let b := Module.finBasis (ZMod 2) (LinearMap.ker f)
  let i0 : Fin (finrank (ZMod 2) (LinearMap.ker f)) := ⟨0, by omega⟩
  let i1 : Fin (finrank (ZMod 2) (LinearMap.ker f)) := ⟨1, by omega⟩
  have hne : ∀ i, ((b i : LinearMap.ker f) : V9) ≠ 0 := fun i h0 => b.ne_zero i (Subtype.ext h0)
  have hd : ((b i0 : LinearMap.ker f) : V9) ≠ b i1 := fun e => by
    have := b.injective (Subtype.ext e)
    simp [i0, i1, Fin.ext_iff] at this
  have hz : ∀ i, ∀ t ∈ R, lab t ⬝ᵥ ((b i : LinearMap.ker f) : V9) = 0 := by
    intro i t ht
    have hm := (b i).2
    rw [LinearMap.mem_ker] at hm
    have := congrFun hm ⟨t, ht⟩
    simpa [f, labMat, Matrix.mulVecLin_apply, Matrix.mulVec] using this
  exact ⟨_, _, hne i0, hne i1, hd, fun t ht => ⟨hz i0 t ht, hz i1 t ht⟩⟩

/-- label span `≤ 6` ⇒ three independent `z₁, z₂, z₃` (distinct, non-zero, `z₃ ≠ z₁ + z₂`) orthogonal to every
live label; with the codim-3 fact FC3 one of the 7 codim-2 supersets has a framed dead set (T1). -/
theorem three_dual (R : Finset L) (h : lspan lab R ≤ 6) :
    ∃ z1 z2 z3 : V9, z1 ≠ 0 ∧ z2 ≠ 0 ∧ z3 ≠ 0 ∧ z1 ≠ z2 ∧ z1 ≠ z3 ∧ z2 ≠ z3 ∧ z3 ≠ z1 + z2 ∧
      ∀ t ∈ R, lab t ⬝ᵥ z1 = 0 ∧ lab t ⬝ᵥ z2 = 0 ∧ lab t ⬝ᵥ z3 = 0 := by
  let f := (labMat lab R).mulVecLin
  have hrn := LinearMap.finrank_range_add_finrank_ker f
  have hr : finrank (ZMod 2) (LinearMap.range f) ≤ 6 := h
  rw [Module.finrank_fin_fun] at hrn
  have hk : 3 ≤ finrank (ZMod 2) (LinearMap.ker f) := by omega
  let b := Module.finBasis (ZMod 2) (LinearMap.ker f)
  let i0 : Fin (finrank (ZMod 2) (LinearMap.ker f)) := ⟨0, by omega⟩
  let i1 : Fin (finrank (ZMod 2) (LinearMap.ker f)) := ⟨1, by omega⟩
  let i2 : Fin (finrank (ZMod 2) (LinearMap.ker f)) := ⟨2, by omega⟩
  have hne : ∀ i, ((b i : LinearMap.ker f) : V9) ≠ 0 := fun i h0 => b.ne_zero i (Subtype.ext h0)
  have hd : ∀ i j, i ≠ j → ((b i : LinearMap.ker f) : V9) ≠ b j := fun i j hij e => hij (b.injective (Subtype.ext e))
  have hz : ∀ i, ∀ t ∈ R, lab t ⬝ᵥ ((b i : LinearMap.ker f) : V9) = 0 := by
    intro i t ht
    have hm := (b i).2
    rw [LinearMap.mem_ker] at hm
    have := congrFun hm ⟨t, ht⟩
    simpa [f, labMat, Matrix.mulVecLin_apply, Matrix.mulVec] using this
  have h3 : ((b i2 : LinearMap.ker f) : V9) ≠ (b i0 : V9) + (b i1 : V9) := by
    intro e
    have e' : b i2 = b i0 + b i1 := Subtype.ext (by rw [Submodule.coe_add]; exact e)
    have := congrArg (fun x => b.repr x i2) e'
    simp only [map_add, Basis.repr_self, Finsupp.add_apply, Finsupp.single_apply] at this
    simp [i0, i1, i2, Fin.ext_iff] at this
  have n01 : i0 ≠ i1 := by simp [i0, i1, Fin.ext_iff]
  have n02 : i0 ≠ i2 := by simp [i0, i2, Fin.ext_iff]
  have n12 : i1 ≠ i2 := by simp [i1, i2, Fin.ext_iff]
  exact ⟨_, _, _, hne i0, hne i1, hne i2, hd _ _ n01, hd _ _ n02, hd _ _ n12, h3,
    fun t ht => ⟨hz i0 t ht, hz i1 t ht, hz i2 t ht⟩⟩

/-- the side `X` (column `j`) is dead on `C(z₁, z₂)` for two distinct non-zero `z₁, z₂` -/
def BigDead (X : Matrix L ι K) (j : ι) : Prop :=
  ∃ z1 z2 : V9, z1 ≠ 0 ∧ z2 ≠ 0 ∧ z1 ≠ z2 ∧ ∀ t, (lab t ⬝ᵥ z1 ≠ 0 ∨ lab t ⬝ᵥ z2 ≠ 0) → X t j = 0

theorem bigDead_of (X : Matrix L ι K) (j : ι) (h : lspan lab (rowSupp X j) ≤ 7) : BigDead lab X j := by
  obtain ⟨z1, z2, h1, h2, h12, hz⟩ := two_dual lab _ h
  refine ⟨z1, z2, h1, h2, h12, fun t ht => ?_⟩
  by_contra hx
  have := hz t (by simp [rowSupp, hx])
  rcases ht with e | e
  · exact e this.1
  · exact e this.2

/-- **Reduction.** A nine-term decoder of cost `< 56` has two distinct terms, each with a big dead side. -/
theorem reduce (P Q : Matrix L ι K) (hι : Fintype.card ι = 9) (h : cost lab P Q < 56) :
    ∃ j k, j ≠ k ∧ (BigDead lab P j ∨ BigDead lab Q j) ∧ (BigDead lab P k ∨ BigDead lab Q k) := by
  obtain ⟨j, k, hjk, hj, hk⟩ := two_cheap lab P Q hι h
  have side : ∀ i, (block lab (rowSupp P i) (rowSupp Q i)).rank ≤ 6 → BigDead lab P i ∨ BigDead lab Q i :=
    fun i hi => (cheap_side lab _ _ hi).imp (bigDead_of lab P i) (bigDead_of lab Q i)
  exact ⟨j, k, hjk, side j hj, side k hk⟩

/-- **T2.1 counting.** If every side has label span `≥ 7` (a side of span `≤ 6` has a framed dead set, T1), then
cost `< 56` forces two distinct terms whose row sides both have span `7`, or two whose column sides do. -/
theorem count_big (P Q : Matrix L ι K) (hι : Fintype.card ι = 9) (h : cost lab P Q < 56)
    (hP : ∀ j, 7 ≤ lspan lab (rowSupp P j)) (hQ : ∀ j, 7 ≤ lspan lab (rowSupp Q j)) :
    (∃ j k, j ≠ k ∧ lspan lab (rowSupp P j) = 7 ∧ lspan lab (rowSupp P k) = 7) ∨
      (∃ j k, j ≠ k ∧ lspan lab (rowSupp Q j) = 7 ∧ lspan lab (rowSupp Q k) = 7) := by
  let a : ι → ℕ := fun j => if lspan lab (rowSupp P j) ≤ 7 then 1 else 0
  let b : ι → ℕ := fun j => if lspan lab (rowSupp Q j) ≤ 7 then 1 else 0
  have hj : ∀ j, 7 ≤ (block lab (rowSupp P j) (rowSupp Q j)).rank + a j + b j := by
    intro j
    have h1 := block_rank_ge lab (rowSupp P j) (rowSupp Q j)
    have h2 := hP j; have h3 := hQ j
    simp only [a, b]
    split_ifs <;> omega
  have hs : ∑ _j : ι, 7 ≤ ∑ j, ((block lab (rowSupp P j) (rowSupp Q j)).rank + a j + b j) :=
    Finset.sum_le_sum fun j _ => hj j
  rw [Finset.sum_add_distrib, Finset.sum_add_distrib, Finset.sum_const, Finset.card_univ, hι, smul_eq_mul] at hs
  have ha : ∑ j, a j = (Finset.univ.filter fun j => lspan lab (rowSupp P j) ≤ 7).card := by
    simp only [a]; rw [Finset.sum_boole]; simp
  have hb : ∑ j, b j = (Finset.univ.filter fun j => lspan lab (rowSupp Q j) ≤ 7).card := by
    simp only [b]; rw [Finset.sum_boole]; simp
  have hc : ∑ j, (block lab (rowSupp P j) (rowSupp Q j)).rank = cost lab P Q := rfl
  rw [ha, hb, hc] at hs
  by_cases hA : 4 ≤ (Finset.univ.filter fun j => lspan lab (rowSupp P j) ≤ 7).card
  · left
    obtain ⟨j, hj1, k, hk1, hjk⟩ := Finset.one_lt_card.mp (by omega : 1 < (Finset.univ.filter
      fun j => lspan lab (rowSupp P j) ≤ 7).card)
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hj1 hk1
    exact ⟨j, k, hjk, le_antisymm hj1 (hP j), le_antisymm hk1 (hP k)⟩
  · right
    obtain ⟨j, hj1, k, hk1, hjk⟩ := Finset.one_lt_card.mp (by omega : 1 < (Finset.univ.filter
      fun j => lspan lab (rowSupp Q j) ≤ 7).card)
    simp only [Finset.mem_filter, Finset.mem_univ, true_and] at hj1 hk1
    exact ⟨j, k, hjk, le_antisymm hj1 (hQ j), le_antisymm hk1 (hQ k)⟩

end RankNine.Red
