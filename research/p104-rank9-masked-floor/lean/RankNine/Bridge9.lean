import RankNine.T35

set_option linter.unusedSectionVars false

/-!
# Bridge to the E8 coordinates of BForm (#6188 / #6218)

The ports of BForm (`BForm.E8.r8`, doubled D8 coordinates, norm 8) are the lines of RankNine in the same order:
`4 ρ_a·ρ_b = 9 r_a·r_b` for all pairs (`bridgeOK`, kernel check), and the linear map `FK = F9L / 9` (`8 × 9`,
integer `9 F`, computed by `t3scan/bridge_F.py` in Internal) sends `ρ_x` to `r_x` for every line (`fOK`).
These discharge the hypotheses `hr`, `hF` and the frame-sum identities `hPs`, `hcs` of `bform_F1/F2/F3`.
-/

namespace RankNine

open Matrix

variable {K : Type*} [Field K] [CharZero K]

/-- `r8` dot product over the first 8 coordinates -/
def r8dot (a b : ℕ) : ℤ := ((List.range 8).map fun k => (BForm.E8.r8 a).getD k 0 * (BForm.E8.r8 b).getD k 0).sum

def bridgeOK : Bool :=
  (List.range 104).all fun a => (List.range 104).all fun b => 4 * dot a b == 9 * r8dot a b

theorem bridgeOK_true : bridgeOK = true := by decide +kernel

/-- `9 F` -/
def F9L : List (List ℤ) :=
  [[0, -3, 0, 0, -3, 0, 3, 0, 3], [-2, 1, -2, -2, 1, -2, 1, 4, 1], [0, -3, 0, 0, 3, 0, -3, 0, 3],
   [0, 3, 0, 0, -3, 0, -3, 0, 3], [-2, 1, -2, -2, 1, 4, 1, -2, 1], [-2, 1, -2, 4, 1, -2, 1, -2, 1],
   [-2, 1, 4, -2, 1, -2, 1, -2, 1], [-4, -1, 2, 2, -1, 2, -1, 2, -1]]

def fOK : Bool := (List.range 104).all fun x => (List.range 8).all fun k =>
  ((List.range 9).map fun j => (F9L.getD k []).getD j 0 * (root x).getD j 0).sum == 9 * (BForm.E8.r8 x).getD k 0

theorem fOK_true : fOK = true := by decide +kernel

/-- the map `ρ ↦ r` -/
def FK : Matrix (Fin 8) (Fin 9) K := fun k j => (((F9L.getD k []).getD j 0 : ℤ) : K) / 9

theorem rK_dot (a b : Fin 104) : BForm.E8.rK K a ⬝ᵥ BForm.E8.rK K b = ((r8dot a b : ℤ) : K) := by
  unfold r8dot
  rw [BForm.E8.sum_range_fin]
  simp only [dotProduct, BForm.E8.rK, Int.cast_sum, Int.cast_mul]

theorem hr_P104 (a b : Fin 104) : ((dot a b : ℤ) : K) = 9 / 4 * (BForm.E8.rK K a ⬝ᵥ BForm.E8.rK K b) := by
  have h := bridgeOK_true
  simp only [bridgeOK, List.all_eq_true, List.mem_range, beq_iff_eq] at h
  have hz : 4 * dot a b = 9 * r8dot a b := h a a.2 b b.2
  have hK : (4 : K) * ((dot a b : ℤ) : K) = 9 * ((r8dot a b : ℤ) : K) := by exact_mod_cast hz
  rw [rK_dot]
  linear_combination (1 / 4 : K) * hK

theorem hF_P104 (x : Fin 104) : (FK : Matrix (Fin 8) (Fin 9) K) *ᵥ rho K x = BForm.E8.rK K x := by
  funext k
  have h := fOK_true
  simp only [fOK, List.all_eq_true, List.mem_range, beq_iff_eq] at h
  have hz := h x x.2 k k.2
  rw [BForm.E8.sum_range_fin] at hz
  have hK : ∑ j : Fin 9, (((F9L.getD k []).getD j 0 : ℤ) : K) * (((root x).getD j 0 : ℤ) : K) =
      9 * (((BForm.E8.r8 x).getD k 0 : ℤ) : K) := by exact_mod_cast hz
  simp only [mulVec, dotProduct, FK, rho, vK, BForm.E8.rK]
  have e : ∑ j : Fin 9, (((F9L.getD k []).getD j 0 : ℤ) : K) / 9 * (((root x).getD j 0 : ℤ) : K) =
      (1 / 9) * ∑ j : Fin 9, (((F9L.getD k []).getD j 0 : ℤ) : K) * (((root x).getD j 0 : ℤ) : K) := by
    rw [Finset.mul_sum]; exact Finset.sum_congr rfl fun j _ => by ring
  rw [e, hK]; ring

/-- `F_dot` for sums over lines given as naturals -/
theorem F_dotN (r : Fin 104 → Fin 8 → K) (hr : ∀ a b : Fin 104, ((dot a b : ℤ) : K) = 9 / 4 * (r a ⬝ᵥ r b))
    (F : Matrix (Fin 8) (Fin 9) K) (hF : ∀ x : Fin 104, F *ᵥ rho K x = r x) {n : ℕ} (co : Fin n → K)
    (g : Fin n → ℕ) (hg : ∀ k, g k < 104) (s : Fin 104) :
    9 / 4 * (r s ⬝ᵥ (F *ᵥ ∑ k, co k • rho K (g k))) = rho K s ⬝ᵥ ∑ k, co k • rho K (g k) :=
  F_dot r hr F hF co (fun k => ⟨g k, hg k⟩) s

theorem hPs_P104 (A B : ℕ → Fin 9 → K) (g : ℕ → K) (f : ℕ) (v s : Fin 104) :
    9 / 4 * (BForm.E8.rK K s ⬝ᵥ (FK *ᵥ PV A B g f v)) = rho K s ⬝ᵥ PV A B g f v := by
  unfold PV
  exact F_dotN _ hr_P104 FK hF_P104 _ (fun k => frL f k) (fun k => frame_lt f k.2) s

theorem hcs_P104 (A B : ℕ → Fin 9 → K) (g : ℕ → K) (f : ℕ) (v s : Fin 104) :
    9 / 4 * (BForm.E8.rK K v ⬝ᵥ (FK *ᵥ cS A B g f s)) = rho K v ⬝ᵥ cS A B g f s := by
  unfold cS
  exact F_dotN _ hr_P104 FK hF_P104 _ (fun k => frL f k) (fun k => frame_lt f k.2) v

end RankNine
