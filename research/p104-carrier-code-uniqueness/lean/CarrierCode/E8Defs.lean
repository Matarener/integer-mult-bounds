import Mathlib
import CarrierCode.E8Data
import CarrierCode.E8Cert

/-!
# Concrete data layer for the E8 proof

Roots of the ports mod 3 (D8 coordinates), frames, and step-3 certificates are stored as lists of naturals so that
the kernel checks them quickly (`decide +kernel`, no `native_decide`).  This file defines the list functions and
their `ZMod 3` / `Fin` counterparts, and proves the bridge lemmas.
-/

namespace CarrierCode.E8

open Matrix

abbrev ι := Fin 104

def rL (i : ℕ) : List ℕ := rootData.getD i []
def rv (i : ℕ) (k : ℕ) : ℕ := (rL i).getD k 0
def dotW (i : ℕ) (w : List ℕ) : ℕ :=
  rv i 0 * w.getD 0 0 + rv i 1 * w.getD 1 0 + rv i 2 * w.getD 2 0 + rv i 3 * w.getD 3 0 +
  rv i 4 * w.getD 4 0 + rv i 5 * w.getD 5 0 + rv i 6 * w.getD 6 0 + rv i 7 * w.getD 7 0
def dotN (i j : ℕ) : ℕ := dotW i (rL j)
def frL (f : ℕ) : List ℕ := frameData.getD f []
def frN (f k : ℕ) : ℕ := (frL f).getD k 0

/-- a list of naturals as a vector of `F₃⁸` -/
def vec (w : List ℕ) : Fin 8 → ZMod 3 := fun k => ((w.getD k 0 : ℕ) : ZMod 3)
/-- the root of port `i` mod 3 -/
def r (i : ℕ) : Fin 8 → ZMod 3 := vec (rL i)

theorem dotW_cast (i : ℕ) (w : List ℕ) : ((dotW i w : ℕ) : ZMod 3) = r i ⬝ᵥ vec w := by
  simp [dotW, r, vec, rv, dotProduct, Fin.sum_univ_eight]

theorem dotN_cast (i j : ℕ) : ((dotN i j : ℕ) : ZMod 3) = r i ⬝ᵥ r j := dotW_cast i (rL j)

theorem cast_eq_zero_iff (n : ℕ) : ((n : ℕ) : ZMod 3) = 0 ↔ n % 3 = 0 := by
  rw [ZMod.natCast_eq_zero_iff]; exact Nat.dvd_iff_mod_eq_zero

theorem cast_mod (n : ℕ) : ((n % 3 : ℕ) : ZMod 3) = (n : ZMod 3) := ZMod.natCast_mod n 3

/-- ports as elements of `ι` -/
def toι (a : ℕ) : ι := ⟨a % 104, Nat.mod_lt _ (by norm_num)⟩

theorem toι_val {a : ℕ} (h : a < 104) : (toι a).val = a := Nat.mod_eq_of_lt h

/-- frames as maps `Fin 8 → ι` -/
def fr (f : ℕ) (k : Fin 8) : ι := toι (frN f k)

/-- The Gram form mod 3. -/
def Gm (i j : ι) : ZMod 3 := r i ⬝ᵥ r j

theorem Gm_comm (i j : ι) : Gm i j = Gm j i := dotProduct_comm _ _

/-- Sum over a list of length 8 as a sum over `Fin 8`. -/
theorem sum_fin8 (ℓ : List ℕ) (h : ℓ.length = 8) (g : ℕ → ZMod 3) :
    ∑ k : Fin 8, g (ℓ.getD k 0) = (ℓ.map g).sum := by
  match ℓ, h with
  | [a0, a1, a2, a3, a4, a5, a6, a7], _ => simp [Fin.sum_univ_eight]; ring

/-- Counting form of a list sum. -/
theorem sum_count (ℓ : List ℕ) (hl : ∀ a ∈ ℓ, a < 104) (h : ι → ZMod 3) :
    ∑ i : ι, ((ℓ.count i.val : ℕ) : ZMod 3) * h i = (ℓ.map fun a => h (toι a)).sum := by
  induction ℓ with
  | nil => simp
  | cons a ℓ ih =>
    have ha : a < 104 := hl a (by simp)
    have ih' := ih (fun b hb => hl b (by simp [hb]))
    simp only [List.count_cons, List.map_cons, List.sum_cons]
    rw [← ih']
    have : ∑ i : ι, (((if (a == i.val) = true then 1 else 0 : ℕ)) : ZMod 3) * h i = h (toι a) := by
      rw [Finset.sum_eq_single (toι a)]
      · simp [toι_val ha]
      · intro b _ hb
        have : a ≠ b.val := fun e => hb (Fin.ext (by rw [toι_val ha]; exact e.symm))
        simp [this]
      · simp
    rw [← this, ← Finset.sum_add_distrib]
    refine Finset.sum_congr rfl fun i _ => ?_
    push_cast; ring

/-! ## Checks (decided by the kernel in `E8Check*.lean`) -/

def framesOK : Prop := ∀ f : Fin 759, (frL f).length = 8 ∧ ∀ a b : Fin 8, frN f a < 104 ∧
  (a ≠ b → dotN (frN f a) (frN f b) % 3 = 0 ∧ frN f a ≠ frN f b)

instance : Decidable framesOK := by unfold framesOK; infer_instance

def seedL (t : ℕ) : List ℕ := seedData.getD t []
def seedN (t j : ℕ) : ℕ := (seedL t).getD j 0
def wL (t j : ℕ) : List ℕ := (wData.getD t []).getD j []
def combL (t x : ℕ) : List (ℕ × ℕ) := (combData.getD t []).getD x []
def accL (L : List (ℕ × ℕ)) (i : ℕ) : ℕ := (L.map fun p => p.2 * (frL p.1).count i).sum
def eN (t x j : ℕ) : ℕ := dotN t x * dotW x (wL t j)
def tgt (t x i : ℕ) : ℕ := (if i = x then 1 else 0) +
  ((List.range 7).map fun j => if i = seedN t j then 2 * eN t x j else 0).sum

def seedOK (t : ℕ) : Prop := (seedL t).length = 7 ∧ ∀ i j : Fin 7, seedN t i < 104 ∧ seedN t i ≠ t ∧
  (dotN t (seedN t i) * dotW (seedN t i) (wL t j)) % 3 = (if i = j then 1 else 0) ∧ dotW t (wL t j) % 3 = 0

def check3 (t x : ℕ) : Prop :=
  x = t ∨ dotN t x % 3 = 0 ∨ x ∈ seedL t ∨
  ((∀ p ∈ combL t x, p.1 < 759) ∧
   (∀ i : Fin 104, i.val = t ∨ dotN t i % 3 = 0 ∨ accL (combL t x) i % 3 = tgt t x i % 3) ∧
   (((combL t x).map Prod.snd).sum + 2 * accL (combL t x) t) % 3 =
     (1 + ((List.range 7).map fun j => 2 * eN t x j).sum) % 3)

instance (t : ℕ) : Decidable (seedOK t) := by unfold seedOK; infer_instance
instance (t x : ℕ) : Decidable (check3 t x) := by unfold check3; infer_instance

/-- All step-3 checks for the ports `t` with `t / 13 = k`. -/
def step3OK (k : ℕ) : Prop := ∀ t : Fin 104, t.val / 13 = k → seedOK t ∧ ∀ x : Fin 104, check3 t x

instance (k : ℕ) : Decidable (step3OK k) := by unfold step3OK; infer_instance

end CarrierCode.E8
