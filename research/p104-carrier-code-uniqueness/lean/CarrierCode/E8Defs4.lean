import CarrierCode.E8Defs
import CarrierCode.E8Data4

/-!
# Data layer for step 4

For each port `t`, seven A2 triangles `(x, y, a, b)` with `r_y = a r_t + b r_x` (mod 3) and the inverse `C` of the
matrix with rows `r_t, r_x₁, …, r_x₇`.
-/

namespace CarrierCode.E8

def a2L (t : ℕ) : List ℕ := a2Data.getD t []
def ax (t i : ℕ) : ℕ := (a2L t).getD (4 * i) 0
def ay (t i : ℕ) : ℕ := (a2L t).getD (4 * i + 1) 0
def aa (t i : ℕ) : ℕ := (a2L t).getD (4 * i + 2) 0
def ab (t i : ℕ) : ℕ := (a2L t).getD (4 * i + 3) 0
def cL (t k i : ℕ) : ℕ := ((invData.getD t []).getD k []).getD i 0
/-- rows `r_t, r_x₁, …, r_x₇` -/
def rowL (t i : ℕ) : List ℕ := if i = 0 then rL t else rL (ax t (i - 1))

def tri4 (t i : ℕ) : Prop :=
  ax t i < 104 ∧ ay t i < 104 ∧ dotN t (ax t i) % 3 ≠ 0 ∧ dotN t (ay t i) % 3 ≠ 0 ∧
  dotN (ax t i) (ay t i) % 3 ≠ 0 ∧ (aa t i = 1 ∨ aa t i = 2) ∧ (ab t i = 1 ∨ ab t i = 2) ∧
  ∀ k : Fin 8, (rv (ay t i) k + 2 * aa t i * rv t k + 2 * ab t i * rv (ax t i) k) % 3 = 0

def check4 (t : ℕ) : Prop :=
  (∀ i : Fin 7, tri4 t i) ∧
  ∀ k l : Fin 8, ((List.range 8).map fun i => cL t k i * (rowL t i).getD l 0).sum % 3 = if k = l then 1 else 0

instance (t i : ℕ) : Decidable (tri4 t i) := by unfold tri4; infer_instance
instance (t : ℕ) : Decidable (check4 t) := by unfold check4; infer_instance

def step4OK : Prop := ∀ t : Fin 104, check4 t

instance : Decidable step4OK := by unfold step4OK; infer_instance

end CarrierCode.E8
