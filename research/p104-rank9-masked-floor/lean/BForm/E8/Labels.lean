import BForm.E8.Bridge
import BForm.Cost

/-! Labels of the ports in `F₂⁹` and the label checks. -/

namespace BForm.E8

open Matrix Finset

/-- the label of port `t` -/
def labK (t : Fin 104) : V9 := fun k => (((pbits t).getD k 0 : ℕ) : ZMod 2)

/-- a label as a 0/1 list -/
def zl (z : V9) : List ℕ := (List.finRange 9).map fun k => (z k).val

theorem pbits_len (t : ℕ) : (pbits t).length = 9 := by simp [pbits]

theorem zl_len (z : V9) : (zl z).length = 9 := by simp [zl]

theorem zl_getD (z : V9) (k : Fin 9) : (zl z).getD k 0 = (z k).val := by
  simp [zl, List.getD_eq_getElem?_getD]

theorem zl_mem (z : V9) : zl z ∈ lists9 := by
  rw [lists9, List.mem_sections, List.forall₂_iff_get]
  refine ⟨by simp [zl], fun i h1 h2 => ?_⟩
  simp only [zl, List.get_eq_getElem, List.getElem_map, List.getElem_finRange, List.getElem_replicate]
  generalize z _ = a
  have : a.val < 2 := ZMod.val_lt _
  simp only [List.mem_cons, List.not_mem_nil, or_false]
  omega

theorem zl_zero {z : V9} (h : zl z = zero9) : z = 0 := by
  funext k
  have := congrArg (fun l => l.getD k 0) h
  simp only [zl_getD] at this
  have h0 : (z k).val = 0 := by
    rw [this]; fin_cases k <;> rfl
  simpa using (ZMod.val_eq_zero (z k)).mp h0

theorem sumNat_eq (a b : List ℕ) (n : ℕ) (ha : a.length = n) (hb : b.length = n) :
    (List.zipWith (· * ·) a b).sum = ∑ k : Fin n, a.getD k 0 * b.getD k 0 := by
  induction a generalizing b n with
  | nil => subst ha; simp
  | cons x a ih =>
    cases b with
    | nil => simp at hb; subst hb; simp at ha
    | cons y b =>
      cases n with
      | zero => simp at ha
      | succ n =>
        simp only [List.length_cons, add_left_inj] at ha hb
        rw [Fin.sum_univ_succ]
        have := ih b n ha hb
        simp only [List.zipWith_cons_cons, List.sum_cons] at this ⊢
        rw [this]; simp

theorem lab_dot (t : Fin 104) (z : V9) : labK t ⬝ᵥ z ≠ 0 ↔ par t (zl z) = true := by
  have h : labK t ⬝ᵥ z = (((List.zipWith (· * ·) (pbits t) (zl z)).sum : ℕ) : ZMod 2) := by
    rw [sumNat_eq _ _ 9 (pbits_len t) (zl_len z)]
    simp only [dotProduct, labK, Nat.cast_sum, Nat.cast_mul, zl_getD, ZMod.natCast_zmod_val]
  rw [h, Ne, ZMod.natCast_eq_zero_iff, par]
  simp only [beq_iff_eq]
  omega

theorem lab_of_pbits {t : Fin 104} {z : V9} (h : pbits t = zl z) : z = labK t := by
  funext k
  simp only [labK, h, zl_getD, ZMod.natCast_zmod_val]

end BForm.E8
