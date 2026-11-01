import BForm.E8.BicliqueDefs
import BForm.Main

/-!
# Soundness of the pruned search for BicliqueFact

`go_sound`: if `go (k+1) C L` succeeds, every (k+1)-sublist of `L` has fewer than 13 common non-orthogonal ports
in `C`.  `biclique_of_go` turns the search result `go 5 (range 104) NBL = true` (checked in `BForm.E8.Biclique`
in 104 pieces) into `BForm.BicliqueFact` for P104.
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
    rcases List.sublist_cons_iff.mp hl with h | ⟨l', rfl, h⟩
    · exact ih k C hB l h hlen
    · have hf : (C.filter fun u => (m :: l').all fun m => m.testBit u) =
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

/-- BicliqueFact for P104 from the search result `go 5 (range 104) NBL`. -/
theorem biclique_of_go (hgo5 : go 5 (List.range 104) NBL = true) {K : Type*} [Field K] [CharZero K] :
    BForm.BicliqueFact (rK K) := by
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
    exact List.sublist_of_subperm_of_pairwise (r := (· ≤ ·))
      (List.subperm_of_subset (Finset.sort_nodup _ _) fun x hx => List.mem_range.mpr (hlt x hx))
      (Finset.pairwise_sort _ _) List.pairwise_le_range
  have hb := nbOK_true
  simp only [nbOK, Bool.and_eq_true, beq_iff_eq] at hb
  have hNB : NBL = (List.range 104).map fun i => NBL.getD i 0 := by
    have h := list_eq_map_range NBL 0
    rw [hb.1] at h
    exact h
  have hs' : (l.map fun i => NBL.getD i 0).Sublist NBL := by
    have := hsub.map (fun i => NBL.getD i 0)
    rwa [← hNB] at this
  have hgo := go_sound NBL 4 _ hgo5 _ hs' (by simp [hlen])
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
