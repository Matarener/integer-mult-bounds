import CarrierCode.E8Defs
import CarrierCode.E8Data5

/-!
# Data layer for step 5 (signs)

`T s` are the ports of the frame `fT`; `En j s = 2 (r_j ⬝ r_{T s}) mod 3` is the frame coordinate of port `j`.
For every ordered pair `(s, s')` a tree (parent, depth) connects the ports meeting both `T s` and `T s'` by edges
`j - k` that are orthogonal, share only `s, s'` and have opposite sign products.
-/

namespace CarrierCode.E8

def Tn (s : ℕ) : ℕ := frN fT s
def En (j s : ℕ) : ℕ := (2 * dotN j (Tn s)) % 3
def trP (s s' j : ℕ) : ℕ := ((treeData.getD (8 * s + s') []).getD j []).getD 0 0
def trD (s s' j : ℕ) : ℕ := ((treeData.getD (8 * s + s') []).getD j []).getD 1 0
def rt5 (s s' : ℕ) : ℕ := rootData5.getD (8 * s + s') 0
def triW (s s' : ℕ) : ℕ := triData.getD (8 * s + s') 0
def sup0 (j : ℕ) : ℕ := sup0Data.getD j 0

def treeOK (s s' j : ℕ) : Prop :=
  (trD s s' j = 0 → j = rt5 s s') ∧
  (trD s s' j ≠ 0 → trP s s' j < 104 ∧ trD s s' (trP s s' j) + 1 = trD s s' j ∧
    En (trP s s' j) s ≠ 0 ∧ En (trP s s' j) s' ≠ 0 ∧ trP s s' j ≠ j ∧ dotN j (trP s s' j) % 3 = 0 ∧
    (∀ u : Fin 8, u.val ≠ s → u.val ≠ s' → (En j u * En (trP s s' j) u) % 3 = 0) ∧
    (En j s * En j s' + En (trP s s' j) s * En (trP s s' j) s') % 3 = 0)

def c5diag : Prop := ∀ t : Fin 104, dotN t t % 3 = 2
def c5root : Prop := ∀ s s' : Fin 8, s ≠ s' → rt5 s s' < 104 ∧ En (rt5 s s') s ≠ 0 ∧ En (rt5 s s') s' ≠ 0
def c5tree : Prop := ∀ s s' : Fin 8, s ≠ s' → ∀ j : Fin 104, En j s ≠ 0 → En j s' ≠ 0 → treeOK s s' j
def c5tri : Prop := ∀ s s' : Fin 8, s.val ≠ 0 → s'.val ≠ 0 → s ≠ s' →
  triW s s' < 104 ∧ En (triW s s') 0 ≠ 0 ∧ En (triW s s') s ≠ 0 ∧ En (triW s s') s' ≠ 0
def c5sup : Prop := ∀ j : Fin 104, sup0 j < 8 ∧ En j (sup0 j) ≠ 0
def c5gram : Prop := ∀ j k : Fin 104, ((List.range 8).map fun s => En j s * En k s).sum % 3 = (2 * dotN j k) % 3

def check5 : Prop := c5diag ∧ c5root ∧ c5tree ∧ c5tri ∧ c5sup ∧ c5gram

instance (s s' j : ℕ) : Decidable (treeOK s s' j) := by unfold treeOK; infer_instance
instance : Decidable c5diag := by unfold c5diag; infer_instance
instance : Decidable c5root := by unfold c5root; infer_instance
instance : Decidable c5tree := by unfold c5tree; infer_instance
instance : Decidable c5tri := by unfold c5tri; infer_instance
instance : Decidable c5sup := by unfold c5sup; infer_instance
instance : Decidable c5gram := by unfold c5gram; infer_instance
instance : Decidable check5 := by unfold check5; infer_instance

end CarrierCode.E8
