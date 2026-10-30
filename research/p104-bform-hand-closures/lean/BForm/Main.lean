import BForm.CaseII

/-!
# The B-form floor on P104

**Theorem** (`bform_floor`).  Let `M = D₁ G D₂ + c βᵀ = X Yᵀ` be a rank-9 B-form realisation of the P104 masked
pattern (`X = [c, D₁R]`, `Y = [β, D₂R]` with left inverses), with `c_u β_s = 0` on orthogonal pairs and
`α_t α'_t ≠ 0` off `supp c ∩ supp β`.  Every nine-term decoder `P Qᵀ = M` costs at least 56.

Hypotheses not proved in Lean, each checked by computation:
* `Capacity` (S0, `f(7) = 36`), `RootFact` (S1, `|N(x)| ≥ 49`), `SpanFact` (BFORM2 span lemma: S0, S1, S2 and the
  E8 hyperplane classification), `BicliqueFact` (S3, `bicliques.py`);
* `CensusFact` (BFORM3/BFORM4 census on top of the repo's case-(b) census and #2338).
-/

namespace BForm

open Matrix

attribute [local instance] Classical.propDecidable

set_option linter.unusedSectionVars false

variable {K : Type*} [Field K] {L : Type*} [Fintype L] [DecidableEq L]

theorem block_swap (lab : L → V9) (R S : Finset L) : block lab S R = (block lab R S)ᵀ := by
  ext a b; simp [block, dotProduct_comm]

theorem cost_swap (lab : L → V9) (P Q : Matrix L C9 K) : cost lab Q P = cost lab P Q := by
  unfold cost
  exact Finset.sum_congr rfl (fun j _ => by rw [block_swap, Matrix.rank_transpose])

theorem orth_symm (r : L → Fin 8 → K) {u s : L} : Orth r u s ↔ Orth r s u := by
  simp [Orth, dotProduct_comm]

/-- S3: a pairwise non-orthogonal rectangle with at least 13 rows has at most 4 columns. -/
def BicliqueFact (r : L → Fin 8 → K) : Prop :=
  ∀ A B : Finset L, (∀ u ∈ A, ∀ s ∈ B, u ≠ s → ¬ Orth r u s) → 13 ≤ A.card → B.card ≤ 4

theorem pattern_transpose (r : L → Fin 8 → K) (N : Matrix L L K) (h : Pattern r N) : Pattern r Nᵀ :=
  ⟨fun t => by simpa using h.1 t, fun u s hus ho => by
    simpa using h.2 s u (Ne.symm hus) ((orth_symm r).mp ho)⟩

/-- **Case III** (`|A| ≤ 4`): the transpose of Case II. -/
theorem caseIII (lab : L → V9) (hcap : Capacity lab) (r : L → Fin 8 → K) (hroot : RootFact r)
    (hspan : SpanFact lab r) (hcensus : CensusFact lab r)
    (α α' c β : L → K) (hdiag : ∀ t, (c t = 0 ∨ β t = 0) → α t ≠ 0 ∧ α' t ≠ 0)
    (hbi : ∀ u s, c u ≠ 0 → β s ≠ 0 → u ≠ s → ¬ Orth r u s)
    (hA : (Finset.univ.filter fun t => c t ≠ 0).card ≤ 4)
    (hpat : Pattern r (bX r α c * (bX r α' β)ᵀ))
    (Xl Yl : Matrix C9 L K) (hX : Xl * bX r α c = 1) (hY : Yl * bX r α' β = 1)
    (P Q : Matrix L C9 K) (h : bX r α c * (bX r α' β)ᵀ = P * Qᵀ) : 56 ≤ cost lab P Q := by
  rw [← cost_swap]
  refine caseII lab hcap r hroot hspan hcensus α' α β c (fun t ht => (hdiag t ht.symm).symm)
    (fun u s hu hs hus ho => hbi s u hs hu (Ne.symm hus) ((orth_symm r).mp ho)) hA ?_ Yl Xl hY hX Q P ?_
  · have := pattern_transpose r _ hpat
    simpa [Matrix.transpose_mul] using this
  · have := congrArg Matrix.transpose h
    simpa [Matrix.transpose_mul] using this

/-- **The B-form floor.** -/
theorem bform_floor (lab : L → V9) (hcap : Capacity lab) (r : L → Fin 8 → K) (hroot : RootFact r)
    (hspan : SpanFact lab r) (hbic : BicliqueFact r) (hcensus : CensusFact lab r)
    (α α' c β : L → K) (hdiag : ∀ t, (c t = 0 ∨ β t = 0) → α t ≠ 0 ∧ α' t ≠ 0)
    (hbi : ∀ u s, c u ≠ 0 → β s ≠ 0 → u ≠ s → ¬ Orth r u s)
    (hpat : Pattern r (bX r α c * (bX r α' β)ᵀ))
    (Xl Yl : Matrix C9 L K) (hX : Xl * bX r α c = 1) (hY : Yl * bX r α' β = 1)
    (P Q : Matrix L C9 K) (h : bX r α c * (bX r α' β)ᵀ = P * Qᵀ) : 56 ≤ cost lab P Q := by
  set As := Finset.univ.filter fun t => c t ≠ 0
  set Bs := Finset.univ.filter fun t => β t ≠ 0
  have hAB : ∀ u ∈ As, ∀ s ∈ Bs, u ≠ s → ¬ Orth r u s := by
    intro u hu s hs; simp only [As, Bs, Finset.mem_filter, Finset.mem_univ, true_and] at hu hs
    exact hbi u s hu hs
  by_cases hA : As.card ≤ 12
  · by_cases hB : Bs.card ≤ 12
    · exact caseI lab hcap r hroot α α' c β (fun t ht => (hdiag t (Or.inl ht)).1)
        (fun t ht => (hdiag t (Or.inr ht)).2) hA hB Xl Yl hX hY P Q h
    · have : As.card ≤ 4 := hbic Bs As (fun s hs u hu hsu ho => hAB u hu s hs (Ne.symm hsu)
        ((orth_symm r).mp ho)) (by omega)
      exact caseIII lab hcap r hroot hspan hcensus α α' c β hdiag hbi this hpat Xl Yl hX hY P Q h
  · exact caseII lab hcap r hroot hspan hcensus α α' c β hdiag hbi (hbic As Bs hAB (by omega)) hpat
      Xl Yl hX hY P Q h

end BForm
