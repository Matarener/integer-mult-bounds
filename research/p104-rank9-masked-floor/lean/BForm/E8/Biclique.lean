import BForm.E8.BicliqueDefs
import BForm.Main
import BForm.E8.BicliqueC0
import BForm.E8.BicliqueC1
import BForm.E8.BicliqueC2
import BForm.E8.BicliqueC3

/-!
# BicliqueFact for P104: no 13 ports are non-orthogonal to 5 ports

A depth-first search with pruning (`go`) over 5-subsets of the ports in increasing order, keeping the list of
ports non-orthogonal to all chosen ones and cutting a branch as soon as fewer than 13 remain (about 1.1 million
calls, 18 million filter steps; the same search in Python: Internal rank9-p104-2026-10-29/t3scan).  The fact holds
for all 120 lines of E8 (at most 11 common lines), so no frame of P104 is special; no hand proof is known.
-/

namespace BForm.E8

open Matrix Finset

set_option linter.unusedSectionVars false

theorem go_succ_iff (k : ℕ) (C : List ℕ) : ∀ L : List ℕ,
    go (k + 1) C L = true ↔ ∀ i ≤ L.length, top k C (L.drop i) = true := by
  intro L
  induction L with
  | nil => simp [go, top]
  | cons m ms ih =>
    rw [show go (k + 1) C (m :: ms) = (top k C (m :: ms) && go (k + 1) C ms) by simp only [go, top],
      Bool.and_eq_true, ih]
    constructor
    · rintro ⟨h0, h⟩ i hi
      cases i with
      | zero => simpa using h0
      | succ j => simpa using h j (by simp at hi; omega)
    · intro h
      exact ⟨by simpa using h 0 (by simp), fun j hj => by simpa using h (j + 1) (by simp; omega)⟩

theorem go_sound : ∀ (L : List ℕ) (k : ℕ) (C : List ℕ), go (k + 1) C L = true → ∀ l : List ℕ, l.Sublist L →
    l.length = k + 1 → (C.filter fun u => l.all fun m => m.testBit u).length < 13 := by
  intro L
  induction L with
  | nil =>
    intro k C _ l hl hlen
    rw [List.sublist_nil.mp hl] at hlen
    simp at hlen
  | cons m ms ih =>
    intro k C hg l hl hlen
    simp only [go, Bool.and_eq_true, Bool.or_eq_true, decide_eq_true_eq, bne_iff_ne, ne_eq] at hg
    obtain ⟨hA, hB⟩ := hg
    cases hl with
    | cons _ h => exact ih k C hB l h hlen
    | cons₂ _ h =>
      rename_i l'
      have hf : (C.filter fun u => (m :: l').all fun m => m.testBit u) =
          (C.filter fun u => m.testBit u).filter fun u => l'.all fun m => m.testBit u := by
        rw [List.filter_filter]
        congr 1
        funext u
        simp only [List.all_cons, Bool.and_comm]
      rw [hf]
      simp only [List.length_cons, add_left_inj] at hlen
      rcases hA with hA | ⟨hk, hA⟩
      · exact lt_of_le_of_lt (List.length_filter_le _ _) hA
      · obtain ⟨k', rfl⟩ : ∃ k', k = k' + 1 := ⟨k - 1, by omega⟩
        exact ih k' _ hA l' h hlen

theorem bic_true : go 5 (List.range 104) NBL = true := by
  have hb := nbOK_true
  simp only [nbOK, Bool.and_eq_true, beq_iff_eq] at hb
  rw [go_succ_iff]
  intro i hi
  rw [hb.1] at hi
  interval_cases i
  exacts [bic_0, bic_1, bic_2, bic_3, bic_4, bic_5, bic_6, bic_7, bic_8, bic_9, bic_10, bic_11, bic_12, bic_13, bic_14, bic_15, bic_16, bic_17, bic_18, bic_19, bic_20, bic_21, bic_22, bic_23, bic_24, bic_25, bic_26, bic_27, bic_28, bic_29, bic_30, bic_31, bic_32, bic_33, bic_34, bic_35, bic_36, bic_37, bic_38, bic_39, bic_40, bic_41, bic_42, bic_43, bic_44, bic_45, bic_46, bic_47, bic_48, bic_49, bic_50, bic_51, bic_52, bic_53, bic_54, bic_55, bic_56, bic_57, bic_58, bic_59, bic_60, bic_61, bic_62, bic_63, bic_64, bic_65, bic_66, bic_67, bic_68, bic_69, bic_70, bic_71, bic_72, bic_73, bic_74, bic_75, bic_76, bic_77, bic_78, bic_79, bic_80, bic_81, bic_82, bic_83, bic_84, bic_85, bic_86, bic_87, bic_88, bic_89, bic_90, bic_91, bic_92, bic_93, bic_94, bic_95, bic_96, bic_97, bic_98, bic_99, bic_100, bic_101, bic_102, bic_103, by rw [List.drop_eq_nil_of_le (by rw [hb.1])]; rfl]

theorem rK_d8 {K : Type*} [Field K] (a b : Fin 104) : rK K a ⬝ᵥ rK K b = ((d8 a b : ℤ) : K) := by
  unfold d8
  rw [sum_range_fin]
  simp only [dotProduct, rK, Int.cast_sum, Int.cast_mul]

theorem nb_bit {K : Type*} [Field K] [CharZero K] {u s : Fin 104} (h : ¬ BForm.Orth (rK K) u s) :
    (NBL.getD s 0).testBit u = true := by
  have hb := nbOK_true
  simp only [nbOK, Bool.and_eq_true, all_range, beq_iff_eq] at hb
  rw [hb.2 s s.2 u u.2]
  have hne : rK K u ⬝ᵥ rK K s ≠ 0 := h
  rw [dotProduct_comm, rK_d8] at hne
  have : d8 s u ≠ 0 := fun e => hne (by rw [e]; simp)
  simpa using this

theorem self_nonorth {K : Type*} [Field K] [CharZero K] (s : Fin 104) : ¬ BForm.Orth (rK K) s s := by
  have hb := nbOK_true
  simp only [nbOK, Bool.and_eq_true, all_range, beq_iff_eq] at hb
  intro h
  have e : rK K s ⬝ᵥ rK K s = 0 := h
  rw [rK_d8] at e
  have hd : d8 s s = 0 := by exact_mod_cast e
  have : d8 s s ≠ 0 := by
    have := (List.all_eq_true.mp (show (List.range 104).all (fun s => d8 s s != 0) = true by decide +kernel)) s
      (List.mem_range.mpr s.2)
    simpa using this
  exact this hd

/-- **BicliqueFact for P104.** -/
theorem biclique_P104 {K : Type*} [Field K] [CharZero K] : BForm.BicliqueFact (rK K) := by
  intro A B hAB hA
  by_contra hB
  rw [not_le] at hB
  obtain ⟨T, hTB, hT⟩ := Finset.exists_subset_card_eq (show 5 ≤ B.card by omega)
  set l : List ℕ := (T.map Fin.valEmbedding).sort (· ≤ ·) with hl
  have hlen : l.length = 5 := by rw [hl, Finset.length_sort, Finset.card_map, hT]
  have hlt : ∀ x ∈ l, x < 104 := by
    intro x hx
    rw [hl, Finset.mem_sort, Finset.mem_map] at hx
    obtain ⟨y, -, rfl⟩ := hx
    exact y.2
  have hsub : l.Sublist (List.range 104) := by
    apply List.sublist_of_subperm_of_sorted (r := (· ≤ ·)) _ (Finset.sort_sorted _ _)
      ((List.pairwise_lt_range 104).imp le_of_lt)
    exact List.subperm_of_subset (Finset.sort_nodup _ _) fun x hx => List.mem_range.mpr (hlt x hx)
  have hb := nbOK_true
  simp only [nbOK, Bool.and_eq_true, beq_iff_eq] at hb
  have hNB : NBL = (List.range 104).map fun i => NBL.getD i 0 := by
    have h := list_eq_map_range NBL 0
    rw [hb.1] at h
    exact h
  have hs' : (l.map fun i => NBL.getD i 0).Sublist NBL := by
    have := hsub.map (fun i => NBL.getD i 0)
    rwa [← hNB] at this
  have hgo := go_sound NBL 4 _ bic_true _ hs' (by simp [hlen])
  apply absurd hgo
  rw [not_lt]
  calc 13 ≤ A.card := hA
    _ = (A.map Fin.valEmbedding).card := (Finset.card_map _).symm
    _ ≤ ((List.range 104).filter fun u => (l.map fun i => NBL.getD i 0).all fun m => m.testBit u).toFinset.card := by
        apply Finset.card_le_card
        intro x hx
        rw [Finset.mem_map] at hx
        obtain ⟨a, ha, rfl⟩ := hx
        rw [List.mem_toFinset, List.mem_filter]
        refine ⟨List.mem_range.mpr a.2, ?_⟩
        rw [List.all_eq_true]
        intro m hm
        rw [List.mem_map] at hm
        obtain ⟨x, hx, rfl⟩ := hm
        rw [hl, Finset.mem_sort, Finset.mem_map] at hx
        obtain ⟨s, hs, rfl⟩ := hx
        show (NBL.getD (s : ℕ) 0).testBit (a : ℕ) = true
        by_cases e : a = s
        · subst e; exact nb_bit (K := K) (self_nonorth a)
        · exact nb_bit (K := K) (hAB a ha s (hTB hs) e)
    _ ≤ _ := List.toFinset_card_le _

end BForm.E8
