import BForm.E8h.ChecksProof
import BForm.E8h.Cert
import BForm.E8.Bridge

/-!
# Positive roots, simple reflections and the dominant chamber

`lv K j` is positive root `j` over a field `K` of characteristic zero; `sr i` is the reflection in the simple
root `i`.  The main result `dom` (over `ℚ`): a non-zero vector is orthogonal to at most 37 positive roots,
or to at most 42 and it is a multiple of a sum of two orthogonal roots (D7), or it is a multiple of a root (E7).
The proof moves `y` into the dominant chamber by simple reflections, by induction on the number of positive roots
with negative inner product; in the dominant chamber the orthogonal roots form a parabolic subsystem, whose size
is read off the table `paraOK`.
-/

namespace BForm.E8h

set_option linter.unusedSectionVars false

open Matrix Finset BForm.E8

section field

variable {K : Type*} [Field K] [CharZero K]

/-- positive root `j` over `K` -/
def lv (K : Type*) [Field K] (j : ℕ) : Fin 8 → K := fun k => (((pr j).getD k 0 : ℤ) : K)

theorem pr_len (j : ℕ) (hj : j < 120) : (pr j).length = 8 := by
  have h := lenOK_true
  simp only [lenOK, Bool.and_eq_true, beq_iff_eq, List.all_eq_true] at h
  have hm : pr j ∈ posData := getD_mem (by rw [h.1.1.1.1.1.1.1]; exact hj) []
  simpa using h.1.1.1.1.1.1.2 _ hm

theorem lv_dot (i j : ℕ) (hi : i < 120) (hj : j < 120) :
    lv K i ⬝ᵥ lv K j = ((dotZ (pr i) (pr j) : ℤ) : K) := by
  rw [dotZ_eq _ _ 8 (pr_len i hi) (pr_len j hj)]
  simp [lv, dotProduct]

theorem lv_norm (j : ℕ) (hj : j < 120) : lv K j ⬝ᵥ lv K j = 8 := by
  have h := normOK_true
  rw [normOK, all_range] at h
  rw [lv_dot j j hj hj, (beq_iff_eq.mp (h j hj))]; norm_num

/-- reflection in simple root `i` -/
def sr (i : ℕ) (y : Fin 8 → K) : Fin 8 → K := y - ((lv K i ⬝ᵥ y) / 4) • lv K i

theorem sr_dot (i : ℕ) (y v : Fin 8 → K) : sr i y ⬝ᵥ v = y ⬝ᵥ sr i v := by
  simp only [sr, sub_dotProduct, dotProduct_sub, smul_dotProduct, dotProduct_smul, smul_eq_mul]
  rw [dotProduct_comm y (lv K i)]; ring

theorem sr_sr (i : ℕ) (hi : i < 120) (y : Fin 8 → K) : sr i (sr i y) = y := by
  have hn := lv_norm (K := K) i hi
  have h1 : lv K i ⬝ᵥ sr i y = -(lv K i ⬝ᵥ y) := by
    simp only [sr, dotProduct_sub, dotProduct_smul, smul_eq_mul, hn]; ring
  rw [sr, h1, sr]; ext k; simp only [Pi.sub_apply, Pi.smul_apply, smul_eq_mul]; ring

theorem sr_smul (i : ℕ) (c : K) (y : Fin 8 → K) : sr i (c • y) = c • sr i y := by
  ext k; simp only [sr, dotProduct_smul, Pi.sub_apply, Pi.smul_apply, smul_eq_mul]; ring

theorem sr_add (i : ℕ) (y v : Fin 8 → K) : sr i (y + v) = sr i y + sr i v := by
  ext k; simp only [sr, dotProduct_add, Pi.sub_apply, Pi.add_apply, Pi.smul_apply, smul_eq_mul]; ring

theorem sr_iso (i : ℕ) (hi : i < 120) (y v : Fin 8 → K) : sr i y ⬝ᵥ sr i v = y ⬝ᵥ v := by
  rw [sr_dot, sr_sr i hi]

/-- the sign of `s_i (root j)` -/
def sg (i j : ℕ) : K := if j = i then -1 else 1

theorem sg_sq (i j : ℕ) : sg (K := K) i j * sg i j = 1 := by unfold sg; split_ifs <;> norm_num

theorem rf_lt (i j : ℕ) (hi : i < 8) (hj : j < 120) : rf i j < 120 := by
  have h := reflOK_true
  rw [reflOK, all_range] at h
  have h' := all_range.mp (h i hi) j hj
  simp only [Bool.and_eq_true, decide_eq_true_eq] at h'
  exact h'.1.1

theorem rf_rf (i j : ℕ) (hi : i < 8) (hj : j < 120) : rf i (rf i j) = j := by
  have h := reflOK_true
  rw [reflOK, all_range] at h
  have h' := all_range.mp (h i hi) j hj
  simp only [Bool.and_eq_true, beq_iff_eq] at h'
  exact h'.1.2

theorem sr_lv (i j : ℕ) (hi : i < 8) (hj : j < 120) : sr i (lv K j) = sg (K := K) i j • lv K (rf i j) := by
  have h := reflOK_true
  rw [reflOK, all_range] at h
  have h' := all_range.mp (h i hi) j hj
  simp only [Bool.and_eq_true] at h'
  have hk := all_range.mp h'.2
  rw [sr, lv_dot i j (by omega) hj]
  ext k
  have e := beq_iff_eq.mp (hk k k.2)
  have e' : (((4 * (pr j).getD k 0 - dotZ (pr i) (pr j) * (pr i).getD k 0 : ℤ)) : K) =
      (((if j = i then -4 else 4) * (pr (rf i j)).getD k 0 : ℤ) : K) := by rw [e]
  simp only [lv, sg, Pi.sub_apply, Pi.smul_apply, smul_eq_mul]
  split_ifs at e' ⊢ <;> push_cast at e' <;> linear_combination e' / 4

theorem sr_lv_dot (i j : ℕ) (hi : i < 8) (hj : j < 120) (y : Fin 8 → K) :
    lv K j ⬝ᵥ sr i y = sg i j * (lv K (rf i j) ⬝ᵥ y) := by
  rw [dotProduct_comm, sr_dot, sr_lv i j hi hj, dotProduct_smul, smul_eq_mul, dotProduct_comm]

/-- the coefficients of a positive root over the simple roots -/
theorem lv_coef (j : ℕ) (hj : j < 120) : lv K j = ∑ i : Fin 8, (cf j i : K) • lv K i := by
  have h := coefOK_true
  rw [coefOK, all_range] at h
  have hk := all_range.mp (h j hj)
  ext k
  have e := beq_iff_eq.mp (hk k k.2)
  rw [sum_range_fin] at e
  have e' : (((pr j).getD k 0 : ℤ) : K) = ((∑ i : Fin 8, (cf j i : ℤ) * (pr i).getD k 0 : ℤ) : K) := by rw [← e]
  simp only [lv, Finset.sum_apply, Pi.smul_apply, smul_eq_mul]
  rw [e']; push_cast; rfl

theorem lv_dot_coef (j : ℕ) (hj : j < 120) (y : Fin 8 → K) :
    lv K j ⬝ᵥ y = ∑ i : Fin 8, (cf j i : K) * (lv K i ⬝ᵥ y) := by
  rw [lv_coef j hj, sum_dotProduct]; simp [smul_dotProduct]

end field

end BForm.E8h
