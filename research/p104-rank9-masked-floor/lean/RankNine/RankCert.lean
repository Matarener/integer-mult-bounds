import RankNine.Rows

set_option linter.unusedSectionVars false

/-!
# T3.3/T3.4: rank certificates for root sets

A vector `d ∈ K⁹` orthogonal to the roots of the lines `X` and to the all-ones vector and zero on the pivot
coordinates (bits of `pm`) is zero, if for every non-pivot `j` an integer combination
`Σ_t N j t ρ_{X t} + No j 𝟙` equals `D e_j` on the non-pivot coordinates (`certOK`, `D ≠ 0`).  With one pivot this
says `rank ρ(X) = 7` (solutions = the line through the orthogonal root), with two pivots `rank ρ(X) = 6`.
-/

namespace RankNine

open Matrix

theorem sum_range_fin {M : Type*} [AddCommMonoid M] (n : ℕ) (g : ℕ → M) :
    ((List.range n).map g).sum = ∑ i : Fin n, g i := by
  induction n with
  | zero => simp
  | succ n ih => rw [List.range_succ, List.map_append, List.sum_append, ih, Fin.sum_univ_castSucc]; simp

def ones9L : List ℤ := [1, 1, 1, 1, 1, 1, 1, 1, 1]

def rootSumOK : Bool := (List.range 104).all fun x => dotL (root x) ones9L == 0

theorem rootSum_ok : rootSumOK = true := by decide +kernel

variable {K : Type*} [Field K]

theorem ones_apply (i : Fin 9) : vK K ones9L i = 1 := by
  fin_cases i <;> simp [vK, ones9L]

theorem rho_ones {x : ℕ} (hx : x < 104) : rho K x ⬝ᵥ vK K ones9L = 0 := by
  have h := rootSum_ok
  simp only [rootSumOK, List.all_eq_true, List.mem_range, beq_iff_eq] at h
  rw [rho, vK_dot _ _ (root_length x) rfl, h x hx, Int.cast_zero]

/-- certificate: lines `X`, combination rows `N j` (over `X`) and `No j` (over `𝟙`), scale `D`, pivots `pm` -/
def combZ (X : List ℕ) (N : List (List ℤ)) (No : List ℤ) (j i : ℕ) : ℤ :=
  ((List.range X.length).map fun t => (N.getD j []).getD t 0 * (root (X.getD t 0)).getD i 0).sum + No.getD j 0

def certOK (X : List ℕ) (N : List (List ℤ)) (No : List ℤ) (D : ℤ) (pm : ℕ) : Bool :=
  D != 0 && (List.range 9).all fun j => pm.testBit j ||
    (List.range 9).all fun i => pm.testBit i || combZ X N No j i == if i = j then D else 0

theorem cert_zero (X : List ℕ) (N : List (List ℤ)) (No : List ℤ) (D : ℤ) (pm : ℕ) (h : certOK X N No D pm = true)
    (d : Fin 9 → K) [CharZero K] (hW : ∀ t < X.length, d ⬝ᵥ rho K (X.getD t 0) = 0) (h1 : d ⬝ᵥ vK K ones9L = 0)
    (hp : ∀ i : Fin 9, pm.testBit i = true → d i = 0) : d = 0 := by
  simp only [certOK, Bool.and_eq_true, bne_iff_ne, ne_eq, List.all_eq_true, List.mem_range, Bool.or_eq_true,
    beq_iff_eq] at h
  obtain ⟨hD, hc⟩ := h
  funext j
  by_cases hj : pm.testBit j = true
  · exact hp j hj
  set v : Fin 9 → K := ∑ t : Fin X.length, (((N.getD j []).getD t 0 : ℤ) : K) • rho K (X.getD t 0) +
    ((No.getD j 0 : ℤ) : K) • vK K ones9L with hv
  have hdv : d ⬝ᵥ v = 0 := by
    rw [hv, dotProduct_add, dotProduct_sum, dotProduct_smul, h1, smul_zero, add_zero]
    exact Finset.sum_eq_zero fun t _ => by rw [dotProduct_smul, hW t t.2, smul_zero]
  have hvi : ∀ i : Fin 9, v i = ((combZ X N No j i : ℤ) : K) := by
    intro i
    rw [hv, combZ, sum_range_fin]
    simp only [Pi.add_apply, Finset.sum_apply, Pi.smul_apply, smul_eq_mul, ones_apply, mul_one, Int.cast_add,
      Int.cast_sum, Int.cast_mul]
    rfl
  have hcj := (hc j j.2).resolve_left hj
  have hdj : d ⬝ᵥ v = d j * (D : K) := by
    rw [dotProduct, Finset.sum_eq_single j]
    · rw [hvi j, (hcj j j.2).resolve_left hj, if_pos rfl]
    · intro i _ hij
      by_cases hpi : pm.testBit i = true
      · rw [hp i hpi, zero_mul]
      · have e := (hcj i i.2).resolve_left hpi
        rw [hvi i, e, if_neg (fun h => hij (Fin.ext h)), Int.cast_zero, mul_zero]
    · simp
  rw [hdv] at hdj
  have hDK : (D : K) ≠ 0 := Int.cast_ne_zero.mpr hD
  exact ((mul_eq_zero.mp hdj.symm).resolve_right hDK)

end RankNine
