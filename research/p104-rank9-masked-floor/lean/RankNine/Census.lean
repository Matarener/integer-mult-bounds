import BForm.E8h.FinalH
import RankNine.Reduce

/-!
# CensusFact from finite facts (Internal `CENSUS-PLAN.md`, #6218 PROOF.md §4)

`censusFact_of_facts`: the census hypothesis `BForm.CensusFact labK (rK K)` of the B-form floor follows from
* `Capacity labK` (`f(7) = 36`), `Cap6` (`f(6) = 20`), `Cap4` (`f(4) = 8`): label bounds (fact FK);
* `LPFact` (Lemma P): no four label planes are pairwise compatible (facts FLAT + LP);
and RootFact (`rootFact_h`, proved).  The finite facts are stated without the field: integer roots `rZ`, integer
minors (`IntRk7`), labels over `F₂`.

Proof.  `r_j ≥ lspan R_j − 1` (`block_rank_ge`, `ColCond`).  Two terms `i ≠ j` leave a dead set `T` with
`rootRank (T \ Zr) ≤ 7` (M_J), so a non-zero `y` is orthogonal to `T \ Zr`; RootFact gives `|R_i ∪ R_j| ≥ 45`.
A big term (`lspan ≤ 7`) lives in `L(Z)` for a plane `Z` (`two_dual`); two bigs give compatible planes (witness
`F = y^⊥`, `E = Zr`).  Counting: a term with `lspan ≤ 4` forces all others to `lspan ≥ 8`; otherwise at most one
term has `lspan ≤ 6` and at most three are big (Lemma P), so the cost is `≥ 63 − 3 − 3 = 57`.
-/

namespace RankNine.Census

open Matrix BForm BForm.E8

attribute [local instance] Classical.propDecidable

set_option linter.unusedSectionVars false

/-- integer roots (doubled D8 coordinates) -/
def rZ (p : Fin 104) : Fin 8 → ℤ := fun k => (r8 p).getD k 0

theorem rK_eq {K : Type*} [Field K] (p : Fin 104) (k : Fin 8) : rK K p k = ((rZ p k : ℤ) : K) := rfl

/-- live set of a label plane `span(a, b)` -/
def Lv (a b : V9) : Finset (Fin 104) := Finset.univ.filter fun t => labK t ⬝ᵥ a = 0 ∧ labK t ⬝ᵥ b = 0

/-- integer rank `≤ 7`: every 8×8 integer minor of the roots vanishes -/
def IntRk7 (F : Finset (Fin 104)) : Prop :=
  ∀ g : Fin 8 → Fin 104, (∀ i, g i ∈ F) → (Matrix.of fun i k => rZ (g i) k).det = 0

/-- compatible planes: outside both live sets, all ports but at most 4 pairwise non-orthogonal ones lie in a set
of integer rank `≤ 7` -/
def Compat (a b c d : V9) : Prop :=
  ∃ F E : Finset (Fin 104), IntRk7 F ∧ E.card ≤ 4 ∧ (∀ x ∈ E, ∀ z ∈ E, x ≠ z → rZ x ⬝ᵥ rZ z ≠ 0) ∧
    ∀ t, t ∉ Lv a b → t ∉ Lv c d → t ∈ F ∨ t ∈ E

/-- **Fact LP (Lemma P)**: no four planes are pairwise compatible. -/
def LPFact : Prop :=
  ∀ a b : Fin 4 → V9, (∀ k, a k ≠ 0 ∧ b k ≠ 0 ∧ a k ≠ b k) → ∃ k l, k ≠ l ∧ ¬ Compat (a k) (b k) (a l) (b l)

/-- **Fact FK6**: `f(6) = 20`. -/
def Cap6 : Prop := ∀ R : Finset (Fin 104), 21 ≤ R.card → 7 ≤ lspan labK R

/-- **Fact FK4**: `f(4) = 8`. -/
def Cap4 : Prop := ∀ R : Finset (Fin 104), 9 ≤ R.card → 5 ≤ lspan labK R

theorem perp_of_rank {K : Type*} [Field K] (r : Fin 104 → Fin 8 → K) (S : Finset (Fin 104))
    (h : rootRank r S ≤ 7) : ∃ y : Fin 8 → K, y ≠ 0 ∧ ∀ t ∈ S, r t ⬝ᵥ y = 0 := by
  let f := (Matrix.of fun (t : S) (k : Fin 8) => r t k).mulVecLin
  have hrn := LinearMap.finrank_range_add_finrank_ker f
  have hr : Module.finrank K (LinearMap.range f) ≤ 7 := h
  rw [Module.finrank_fin_fun] at hrn
  have hk : 0 < Module.finrank K (LinearMap.ker f) := by omega
  obtain ⟨⟨y, hy⟩, hy0⟩ := Module.finrank_pos_iff_exists_ne_zero.mp hk
  refine ⟨y, fun e => hy0 (Subtype.ext e), fun t ht => ?_⟩
  rw [LinearMap.mem_ker] at hy
  have := congrFun hy ⟨t, ht⟩
  first
    | exact this
    | simpa [Matrix.mulVec, dotProduct] using this

theorem card_perp {K : Type*} [Field K] [CharZero K] (y : Fin 8 → K) (hy : y ≠ 0) (S : Finset (Fin 104))
    (hS : ∀ t ∈ S, rK K t ⬝ᵥ y = 0) : S.card ≤ 55 := by
  have h49 := BForm.E8h.rootFact_h y hy
  have hd : Disjoint S (nonorth (rK K) y) := by
    rw [Finset.disjoint_left]
    intro t ht ht'
    simp only [nonorth, Finset.mem_filter] at ht'
    exact ht'.2 (hS t ht)
  have h1 := Finset.card_union_of_disjoint hd
  have hu := Finset.card_le_univ (S ∪ nonorth (rK K) y)
  simp only [Fintype.card_fin] at hu
  omega

theorem intRk_of_perp {K : Type*} [Field K] [CharZero K] (y : Fin 8 → K) (hy : y ≠ 0) :
    IntRk7 (Finset.univ.filter fun t => rK K t ⬝ᵥ y = 0) := by
  intro g hg
  let M : Matrix (Fin 8) (Fin 8) ℤ := Matrix.of fun i k => rZ (g i) k
  show M.det = 0
  have h0 : (M.map (Int.castRingHom K)).det = 0 := by
    rw [← Matrix.exists_mulVec_eq_zero_iff]
    refine ⟨y, hy, ?_⟩
    ext i
    have := (Finset.mem_filter.mp (hg i)).2
    simpa [M, Matrix.mulVec, dotProduct, rK_eq] using this
  rw [← RingHom.mapMatrix_apply, ← RingHom.map_det] at h0
  simpa using h0

theorem dot_cast {K : Type*} [Field K] (x z : Fin 104) :
    rK K x ⬝ᵥ rK K z = ((rZ x ⬝ᵥ rZ z : ℤ) : K) := by
  simp [dotProduct, rK_eq, Int.cast_sum, Int.cast_mul]

theorem compat_of {K : Type*} [Field K] [CharZero K] (Zr : Finset (Fin 104)) (hZr : Zr.card ≤ 4)
    (hcl : IsClique (rK K) Zr) (Ri Rj : Finset (Fin 104)) (y : Fin 8 → K) (hy : y ≠ 0)
    (hT : ∀ t, t ∉ Ri → t ∉ Rj → t ∉ Zr → rK K t ⬝ᵥ y = 0)
    (a b c d : V9) (hi : Ri ⊆ Lv a b) (hj : Rj ⊆ Lv c d) : Compat a b c d := by
  refine ⟨Finset.univ.filter fun t => rK K t ⬝ᵥ y = 0, Zr, intRk_of_perp y hy, hZr, ?_, ?_⟩
  · intro x hx z hz hxz e
    apply hcl x hx z hz hxz
    show rK K x ⬝ᵥ rK K z = 0
    rw [dot_cast, e, Int.cast_zero]
  · intro t ha hc
    by_cases hz : t ∈ Zr
    · exact Or.inr hz
    · exact Or.inl (Finset.mem_filter.mpr
        ⟨Finset.mem_univ _, hT t (fun h => ha (hi h)) (fun h => hc (hj h)) hz⟩)

theorem pair_perp {K : Type*} [Field K] (Zr : Finset (Fin 104)) (P : Matrix (Fin 104) C9 K)
    (hM : ∀ (J : Finset C9) (T : Finset (Fin 104)), (∀ t ∈ T, ∀ j ∈ J, P t j = 0) →
      rootRank (rK K) (T \ Zr) + J.card ≤ 9) (i j : C9) (hij : i ≠ j) :
    ∃ y : Fin 8 → K, y ≠ 0 ∧ ∀ t, t ∉ rowSupp P i → t ∉ rowSupp P j → t ∉ Zr → rK K t ⬝ᵥ y = 0 := by
  let T := (rowSupp P i ∪ rowSupp P j)ᶜ
  have hdead : ∀ t ∈ T, ∀ k ∈ ({i, j} : Finset C9), P t k = 0 := by
    intro t ht k hk
    simp only [T, Finset.mem_compl, Finset.mem_union, not_or] at ht
    simp only [Finset.mem_insert, Finset.mem_singleton] at hk
    rcases hk with hk | hk
    · subst hk; simpa [rowSupp] using ht.1
    · subst hk; simpa [rowSupp] using ht.2
  have h := hM {i, j} T hdead
  rw [Finset.card_pair hij] at h
  obtain ⟨y, hy, hS⟩ := perp_of_rank (rK K) (T \ Zr) (by omega)
  refine ⟨y, hy, fun t hi hj hz => hS t ?_⟩
  simp only [T, Finset.mem_sdiff, Finset.mem_compl, Finset.mem_union, not_or]
  exact ⟨⟨hi, hj⟩, hz⟩

theorem union45 {K : Type*} [Field K] [CharZero K] (Zr : Finset (Fin 104)) (hZr : Zr.card ≤ 4)
    (Ri Rj : Finset (Fin 104)) (y : Fin 8 → K) (hy : y ≠ 0)
    (hT : ∀ t, t ∉ Ri → t ∉ Rj → t ∉ Zr → rK K t ⬝ᵥ y = 0) : 45 ≤ (Ri ∪ Rj).card := by
  let T := (Ri ∪ Rj)ᶜ
  have h1 : (T \ Zr).card ≤ 55 := card_perp y hy _ (fun t ht => by
    simp only [T, Finset.mem_sdiff, Finset.mem_compl, Finset.mem_union, not_or] at ht
    exact hT t ht.1.1 ht.1.2 ht.2)
  have h2 : T.card ≤ (T \ Zr).card + Zr.card := by
    calc T.card ≤ ((T \ Zr) ∪ Zr).card := Finset.card_le_card (fun t ht => by
            by_cases h : t ∈ Zr
            · exact Finset.mem_union_right _ h
            · exact Finset.mem_union_left _ (Finset.mem_sdiff.mpr ⟨ht, h⟩))
      _ ≤ _ := Finset.card_union_le _ _
  have h3 : T.card = 104 - (Ri ∪ Rj).card := by
    simp only [T, Finset.card_compl, Fintype.card_fin]
  have h4 := Finset.card_le_univ (Ri ∪ Rj)
  simp only [Fintype.card_fin] at h4
  omega

theorem sum_ind (S : Finset C9) : ∑ j, (if j ∈ S then 1 else 0 : ℕ) = S.card := by
  first
    | rw [Finset.sum_ite_mem, Finset.univ_inter, Finset.sum_const, smul_eq_mul, mul_one]
    | simp [Finset.sum_boole]

/-- **CensusFact for P104** from the label bounds and Lemma P (RootFact proved). -/
theorem censusFact_of_facts {K : Type*} [Field K] [CharZero K] (hcap : Capacity labK) (h6 : Cap6)
    (h4 : Cap4) (hlp : LPFact) : CensusFact labK (rK K) := by
  intro Zr P Q hZr hcl _hpat hM hcol
  have hrk : ∀ j, lspan labK (rowSupp P j) ≤ (block labK (rowSupp P j) (rowSupp Q j)).rank + 1 := by
    intro j
    have := block_rank_ge labK (rowSupp P j) (rowSupp Q j)
    have := (hcol j).1
    omega
  have hun : ∀ i j, i ≠ j → 45 ≤ (rowSupp P i).card + (rowSupp P j).card := by
    intro i j hij
    obtain ⟨y, hy, hT⟩ := pair_perp Zr P hM i j hij
    have := union45 Zr hZr _ _ y hy hT
    have := Finset.card_union_le (rowSupp P i) (rowSupp P j)
    omega
  have s6 : ∀ j, lspan labK (rowSupp P j) ≤ 6 → (rowSupp P j).card ≤ 20 := by
    intro j h
    by_contra hc
    have := h6 (rowSupp P j) (by omega)
    omega
  have s4 : ∀ j, lspan labK (rowSupp P j) ≤ 4 → (rowSupp P j).card ≤ 8 := by
    intro j h
    by_contra hc
    have := h4 (rowSupp P j) (by omega)
    omega
  unfold cost
  by_cases hA : ∃ j0, lspan labK (rowSupp P j0) ≤ 4
  · obtain ⟨j0, hj0⟩ := hA
    have hge : ∀ i ∈ Finset.univ.erase j0, 7 ≤ (block labK (rowSupp P i) (rowSupp Q i)).rank := by
      intro i hi
      have hne := Finset.ne_of_mem_erase hi
      have h1 := hun i j0 hne
      have h2 := s4 j0 hj0
      have h3 : 8 ≤ lspan labK (rowSupp P i) := hcap _ (by omega)
      have := hrk i
      omega
    have hc : (Finset.univ.erase j0).card = 8 := by
      rw [Finset.card_erase_of_mem (Finset.mem_univ _), Finset.card_univ]
      rfl
    have hsum := Finset.card_nsmul_le_sum _ _ 7 hge
    rw [hc, smul_eq_mul] at hsum
    have hsplit := Finset.add_sum_erase (Finset.univ : Finset C9)
      (fun j => (block labK (rowSupp P j) (rowSupp Q j)).rank) (Finset.mem_univ j0)
    try dsimp only at hsplit
    rw [← hsplit]
    omega
  · push_neg at hA
    let S7 := Finset.univ.filter fun j : C9 => lspan labK (rowSupp P j) ≤ 7
    let S6 := Finset.univ.filter fun j : C9 => lspan labK (rowSupp P j) ≤ 6
    have hS6 : S6.card ≤ 1 := by
      rw [Finset.card_le_one]
      intro a ha b hb
      by_contra hab
      simp only [S6, Finset.mem_filter, Finset.mem_univ, true_and] at ha hb
      have := hun a b hab
      have := s6 a ha
      have := s6 b hb
      omega
    have hS7 : S7.card ≤ 3 := by
      by_contra hc
      push_neg at hc
      obtain ⟨s, hs, hsc⟩ := Finset.exists_subset_card_eq (show 4 ≤ S7.card by omega)
      have hpl : ∀ j, lspan labK (rowSupp P j) ≤ 7 → ∃ z1 z2 : V9, z1 ≠ 0 ∧ z2 ≠ 0 ∧ z1 ≠ z2 ∧
          ∀ t ∈ rowSupp P j, labK t ⬝ᵥ z1 = 0 ∧ labK t ⬝ᵥ z2 = 0 :=
        fun j h => RankNine.Red.two_dual labK (rowSupp P j) h
      choose! A B hAB using hpl
      let e : Fin 4 ≃ s := (Fintype.equivFinOfCardEq (by simp [hsc])).symm
      let f : Fin 4 → C9 := fun k => (e k).1
      have hf : ∀ k, lspan labK (rowSupp P (f k)) ≤ 7 := fun k => by
        have := hs (e k).2
        simpa [S7] using this
      have hinj : Function.Injective f := fun k l h => e.injective (Subtype.ext h)
      obtain ⟨k, l, hkl, hnc⟩ := hlp (fun k => A (f k)) (fun k => B (f k))
        (fun k => ⟨(hAB _ (hf k)).1, (hAB _ (hf k)).2.1, (hAB _ (hf k)).2.2.1⟩)
      apply hnc
      obtain ⟨y, hy, hT⟩ := pair_perp Zr P hM (f k) (f l) (fun h => hkl (hinj h))
      refine compat_of Zr hZr hcl _ _ y hy hT _ _ _ _ ?_ ?_
      · intro t ht
        have := (hAB _ (hf k)).2.2.2 t ht
        simp [Lv, this.1, this.2]
      · intro t ht
        have := (hAB _ (hf l)).2.2.2 t ht
        simp [Lv, this.1, this.2]
    have hge : ∀ j ∈ (Finset.univ : Finset C9), 7 ≤ (block labK (rowSupp P j) (rowSupp Q j)).rank
        + 3 * (if j ∈ S6 then 1 else 0) + (if j ∈ S7 then 1 else 0) := by
      intro j _
      have := hrk j
      have := hA j
      by_cases h7 : lspan labK (rowSupp P j) ≤ 7
      · have m7 : j ∈ S7 := by simp [S7, h7]
        by_cases h6' : lspan labK (rowSupp P j) ≤ 6
        · have m6 : j ∈ S6 := by simp [S6, h6']
          simp only [m6, m7, if_true]
          omega
        · have m6 : j ∉ S6 := by simp [S6, h6']
          simp only [m6, m7, if_true, if_false]
          omega
      · have m7 : j ∉ S7 := by simp [S7, h7]
        have m6 : j ∉ S6 := by
          simp only [S6, Finset.mem_filter, Finset.mem_univ, true_and]
          omega
        simp only [m6, m7, if_false]
        omega
    have hsum := Finset.card_nsmul_le_sum _ _ 7 hge
    have e : ∑ j, ((block labK (rowSupp P j) (rowSupp Q j)).rank + 3 * (if j ∈ S6 then 1 else 0) +
        (if j ∈ S7 then 1 else 0)) =
        ∑ j, (block labK (rowSupp P j) (rowSupp Q j)).rank + 3 * S6.card + S7.card := by
      rw [Finset.sum_add_distrib, Finset.sum_add_distrib, ← Finset.mul_sum, sum_ind, sum_ind]
    rw [e, Finset.card_univ, smul_eq_mul] at hsum
    have h9 : Fintype.card C9 = 9 := by first | rfl | simp | decide
    rw [h9] at hsum
    omega

end RankNine.Census
