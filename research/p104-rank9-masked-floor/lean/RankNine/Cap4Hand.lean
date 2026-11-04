import RankNine.Cap6Hand

set_option linter.unusedSectionVars false

/-!
# Cap4 by hand (CENSUS-PLAN §6, parity): a set of at least 9 ports has label span at least 5

The labels of `R` lie in `U = span lab(R)`, `|U| = 2^{lspan R} ≤ 16`.  Every port label has odd weight
(`l · j = 1`, `j` the all-ones vector; checked on the 104 labels), labels are distinct.  The odd part `O` of `U`
injects into the even part by `x ↦ x + l₀` (`l₀` a label of `R`), so `|R| ≤ |O| ≤ |U| / 2 ≤ 8`.
-/

namespace RankNine.Facts

open Matrix Finset Module BForm BForm.E8

def jv : V9 := fun _ => 1

theorem pbits_inj : ∀ s t : Fin 104, pbits s = pbits t → s = t := by decide +kernel

theorem par_ones : ∀ t : Fin 104, par t (zl jv) = true := by decide +kernel

attribute [local instance] Classical.propDecidable

theorem labK_inj : Function.Injective labK := by
  intro s t h
  apply pbits_inj
  rw [← zl_labK, ← zl_labK, h]

theorem labK_odd (t : Fin 104) : labK t ⬝ᵥ jv ≠ 0 := (lab_dot t jv).mpr (par_ones t)

theorem odd_add {a b : ZMod 2} (ha : a ≠ 0) (hb : b ≠ 0) : a + b = 0 := by
  revert a b; decide

/-- **Cap4 for P104, by hand.** -/
theorem cap4_hand : ∀ R : Finset (Fin 104), 9 ≤ R.card → 5 ≤ lspan labK R := by
  intro R hR
  by_contra hlt
  set U : Submodule (ZMod 2) V9 := Submodule.span (ZMod 2) (Set.range (labMat labK R)) with hU
  have hfr : finrank (ZMod 2) U ≤ 4 := by
    have := Matrix.rank_eq_finrank_span_row (labMat labK R)
    rw [← hU] at this
    unfold lspan at hlt
    omega
  have hcU : Fintype.card U ≤ 16 := by
    rw [Module.card_eq_pow_finrank (K := ZMod 2) (V := U), ZMod.card]
    calc 2 ^ finrank (ZMod 2) U ≤ 2 ^ 4 := Nat.pow_le_pow_right (by norm_num) hfr
      _ = 16 := by norm_num
  have hmem : ∀ t ∈ R, labK t ∈ U := by
    intro t ht
    apply Submodule.subset_span
    exact ⟨⟨t, ht⟩, rfl⟩
  set Uf : Finset V9 := univ.filter fun x => x ∈ U with hUf
  have hUf16 : Uf.card ≤ 16 := by
    rw [hUf, ← Fintype.card_subtype]
    convert hcU
  set O := Uf.filter fun x => x ⬝ᵥ jv ≠ 0 with hO
  set Ev := Uf.filter fun x => ¬ (x ⬝ᵥ jv ≠ 0) with hEv
  have hsplit : O.card + Ev.card = Uf.card := Finset.filter_card_add_filter_neg_card_eq_card _
  have hRO : R.card ≤ O.card := by
    rw [← Finset.card_image_of_injective R labK_inj]
    apply Finset.card_le_card
    intro x hx
    obtain ⟨t, ht, rfl⟩ := Finset.mem_image.mp hx
    simp only [hO, hUf, mem_filter, mem_univ, true_and]
    exact ⟨hmem t ht, labK_odd t⟩
  obtain ⟨t0, ht0⟩ : R.Nonempty := Finset.card_pos.mp (by omega)
  have hOE : O.card ≤ Ev.card := by
    have hinj : Function.Injective fun x : V9 => x + labK t0 := fun x y h => add_right_cancel h
    rw [← Finset.card_image_of_injective O hinj]
    apply Finset.card_le_card
    intro y hy
    obtain ⟨x, hx, rfl⟩ := Finset.mem_image.mp hy
    simp only [hO, hEv, hUf, mem_filter, mem_univ, true_and] at hx ⊢
    refine ⟨U.add_mem hx.1 (hmem t0 ht0), ?_⟩
    rw [add_dotProduct]
    exact not_not.mpr (odd_add hx.2 (labK_odd t0))
  omega

end RankNine.Facts
