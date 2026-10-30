import BForm.YZero
import BForm.MJ

/-!
# E. Cases II/III (one side of the rank-one lift has at most 4 ports), including singular `D`

The finite census (repo `research/nine-term-outside-colspace` case-(b) census, extended in BFORM3/BFORM4: port
classes as extra column classes, survivors and port classes may repeat, the propagation bound replaced by the exact
root rank after removing a non-orthogonal set of at most 4 ports; Kaggle `p104-bform-census`, `p104-bform-singular`:
0 configurations alive), together with #2338's floor for decoders with at most 8 paid terms, is used ONLY through
`CensusFact`: a purely combinatorial statement about the supports of an exact masked decoder.  Here we prove that
every B-form decoder with `|B| ≤ 4` either falls under `yzero` or satisfies all premises of `CensusFact`.
The geometric span lemma (BFORM2, from S0, S1, S2 and the E8 hyperplane classification) enters as `SpanFact`.
-/

namespace BForm

open Matrix

attribute [local instance] Classical.propDecidable

set_option linter.unusedSectionVars false

variable {K : Type*} [Field K] {L : Type*} [Fintype L] [DecidableEq L]

/-- Rank of the roots of a set of ports. -/
noncomputable def rootRank (r : L → Fin 8 → K) (T : Finset L) : ℕ := (Matrix.of fun (t : T) (k : Fin 8) => r t k).rank

def Orth (r : L → Fin 8 → K) (u s : L) : Prop := r u ⬝ᵥ r s = 0

/-- Pairwise non-orthogonal set. -/
def IsClique (r : L → Fin 8 → K) (Z : Finset L) : Prop := ∀ u ∈ Z, ∀ s ∈ Z, u ≠ s → ¬ Orth r u s

/-- The label class `O(z) = {t : l_t ⬝ z = 1}`. -/
noncomputable def labO (lab : L → V9) (z : V9) : Finset L := Finset.univ.filter fun t => lab t ⬝ᵥ z ≠ 0

/-- Exact survivor class: the roots of `O(z)` do not span. (The census used the repo's survivors `lb < 8`, a
superset.) -/
def Survivor (r : L → Fin 8 → K) (lab : L → V9) (z : V9) : Prop := rootRank r (labO lab z) ≤ 7

/-- The P104 masked pattern: non-zero diagonal, zero on orthogonal pairs. -/
def Pattern (r : L → Fin 8 → K) (N : Matrix L L K) : Prop :=
  (∀ t, N t t ≠ 0) ∧ ∀ u s, u ≠ s → Orth r u s → N u s = 0

/-- Column condition used by the census: label span `≥ 8`, and a missing class is a survivor or a port class. -/
def ColCond (lab : L → V9) (r : L → Fin 8 → K) (S : Finset L) : Prop :=
  8 ≤ lspan lab S ∧ ∀ z : V9, z ≠ 0 → (∀ s ∈ S, lab s ⬝ᵥ z = 0) → Survivor r lab z ∨ ∃ w, z = lab w

/-- **The census statement** (checked by `cnt9c.py` V3 and `cnt9z.py` V3 on top of the repo's case-(b) census and
#2338; not proved in Lean). -/
def CensusFact (lab : L → V9) (r : L → Fin 8 → K) : Prop :=
  ∀ (Zr : Finset L) (P Q : Matrix L C9 K), Zr.card ≤ 4 → IsClique r Zr → Pattern r (P * Qᵀ) →
    (∀ (J : Finset C9) (T : Finset L), (∀ t ∈ T, ∀ j ∈ J, P t j = 0) → rootRank r (T \ Zr) + J.card ≤ 9) →
    (∀ j, ColCond lab r (rowSupp Q j)) → 56 ≤ cost lab P Q

/-- **Span lemma** (BFORM2, corrected after the Kaggle S2 check). -/
def SpanFact (lab : L → V9) (r : L → Fin 8 → K) : Prop :=
  ∀ y : Fin 8 → K, y ≠ 0 → ∀ B : Finset L, B.card ≤ 4 → ∀ z : V9, z ≠ 0 →
    (∀ t ∈ nonorth r y \ B, lab t ⬝ᵥ z = 0) → (∀ t ∈ nonorth r y, lab t ⬝ᵥ z = 0) ∨ ∃ w ∈ B, z = lab w

/-- A non-zero vector killed by all rows bounds the rank by 7. -/
theorem rank_le_seven {T : Type*} [Fintype T] (A : Matrix T (Fin 8) K) (y : Fin 8 → K) (hy : y ≠ 0)
    (h : A *ᵥ y = 0) : A.rank ≤ 7 := by
  have hrk := LinearMap.finrank_range_add_finrank_ker A.mulVecLin
  have hk : 0 < Module.finrank K (LinearMap.ker A.mulVecLin) :=
    Module.finrank_pos_iff_exists_ne_zero.mpr ⟨⟨y, by simpa using h⟩, fun h0 => hy (by simpa using h0)⟩
  simp only [Module.finrank_fin_fun] at hrk
  unfold Matrix.rank
  omega

/-- Roots outside `Zr` have rank at most the rank of the corresponding rows of `X = [c, α r]`. -/
theorem rootRank_le (r : L → Fin 8 → K) (α c : L → K) (T Zr : Finset L) (hα : ∀ t, t ∉ Zr → α t ≠ 0) :
    rootRank r (T \ Zr) ≤ (Matrix.of fun (t : T) (i : C9) => bX r α c t i).rank := by
  let ι : (T \ Zr : Finset L) → T := fun t => ⟨t.1, (Finset.mem_sdiff.mp t.2).1⟩
  let S := (Matrix.of fun (t : T) (i : C9) => bX r α c t i).submatrix ι some
  have hS := Matrix.rank_submatrix_le (Matrix.of fun (t : T) (i : C9) => bX r α c t i) ι some
  have heq : (Matrix.of fun (t : (T \ Zr : Finset L)) (k : Fin 8) => r t k) =
      Matrix.diagonal (fun t : (T \ Zr : Finset L) => (α t)⁻¹) * S := by
    ext t k
    have ht : α t ≠ 0 := hα t (Finset.mem_sdiff.mp t.2).2
    simp [S, ι, bX, Matrix.diagonal_mul, ht]
  unfold rootRank
  rw [heq]
  exact le_trans (Matrix.rank_mul_le_right _ _) hS

/-- **Case II** (`|B| ≤ 4`), any `D` (singular or not). -/
theorem caseII (lab : L → V9) (hcap : Capacity lab) (r : L → Fin 8 → K) (hroot : RootFact r)
    (hspan : SpanFact lab r) (hcensus : CensusFact lab r)
    (α α' c β : L → K) (hdiag : ∀ t, (c t = 0 ∨ β t = 0) → α t ≠ 0 ∧ α' t ≠ 0)
    (hbi : ∀ u s, c u ≠ 0 → β s ≠ 0 → u ≠ s → ¬ Orth r u s)
    (hB : (Finset.univ.filter fun t => β t ≠ 0).card ≤ 4)
    (hpat : Pattern r (bX r α c * (bX r α' β)ᵀ))
    (Xl Yl : Matrix C9 L K) (hX : Xl * bX r α c = 1) (hY : Yl * bX r α' β = 1)
    (P Q : Matrix L C9 K) (h : bX r α c * (bX r α' β)ᵀ = P * Qᵀ) : 56 ≤ cost lab P Q := by
  obtain ⟨hUW, hP, hQ⟩ := normal_form _ _ P Q Xl Yl hX hY h
  set U := Xl * P; set W := Yl * Q
  set Bs := Finset.univ.filter fun t => β t ≠ 0
  set Zr := Finset.univ.filter fun t => α t = 0
  have hα' : ∀ t, β t = 0 → α' t ≠ 0 := fun t ht => (hdiag t (Or.inr ht)).2
  have hZrB : Zr ⊆ Bs := by
    intro t ht
    simp only [Zr, Bs, Finset.mem_filter, Finset.mem_univ, true_and] at ht ⊢
    intro hb; exact (hdiag t (Or.inr hb)).1 ht
  have hZr : Zr.card ≤ 4 := le_trans (Finset.card_le_card hZrB) hB
  by_cases hy0 : ∃ j, (fun k => W (some k) j) = 0
  · obtain ⟨j₀, hj₀⟩ := hy0
    exact yzero lab hcap r hroot α α' c β hα' hZr hB U W hUW j₀ hj₀ P Q hP hQ
  push Not at hy0
  apply hcensus Zr P Q hZr
  · intro u hu s hs hus
    simp only [Zr, Finset.mem_filter, Finset.mem_univ, true_and] at hu hs
    have hcu : c u ≠ 0 := fun hc => (hdiag u (Or.inl hc)).1 hu
    have hbs : β s ≠ 0 := fun hb => (hdiag s (Or.inr hb)).1 hs
    exact hbi u s hcu hbs hus
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
    have hsub := supp_off_lift r α' β hα' W j
    rw [← hQ] at hsub
    have h49 : 49 ≤ (nonorth r fun k => W (some k) j).card := hroot _ (hy0 j)
    have hcard : 45 ≤ (rowSupp Q j).card := by
      have := Finset.card_le_card hsub
      have := Finset.le_card_sdiff (Finset.univ.filter fun t => β t ≠ 0) (nonorth r fun k => W (some k) j)
      have hB' : (Finset.univ.filter fun t => β t ≠ 0).card ≤ 4 := hB
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
