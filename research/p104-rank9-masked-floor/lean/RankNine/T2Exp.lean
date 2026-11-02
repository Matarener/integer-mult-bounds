import RankNine.T2Glue

/-!
# T2.3: discharging `ExpOK` from frame non-degeneracy

`ExpOK A B m F` (dead rows expand over the dead lines of the frame `F`) follows from the partial frame expansion
(`PartialFrame.partial_expansion`) as soon as `F` is a frame (8 distinct pairwise orthogonal lines, checked by
`frameOK`), every dead row is orthogonal to the dead vector `u` (`A x ⬝ᵥ u = 0`), and `u, B(F)` are linearly
independent.  The last condition is the branch hypothesis: in branch (a) it is the branch itself (no degenerate
partial frames); for frames lying entirely in the dead set it is automatic once `u ≠ 0` (`indep_of_dead`), which
covers branch (b) (`u = B s₀`, full frames inside `R`).
-/

namespace RankNine.T2

open Matrix RankNine

variable {K : Type*} [Field K] [CharZero K]

/-- 8 distinct lines `< 104`, pairwise orthogonal -/
def frameOK (F : List ℕ) : Bool :=
  decide (F.length = 8) && F.all (· < 104) && decide F.Nodup &&
  (List.range 8).all fun i => (List.range 8).all fun j => i == j || orthB (F.getD i 0) (F.getD j 0)

/-- the `k`-th line of a frame list -/
def fr (F : List ℕ) (k : Fin 8) : ℕ := F.getD k.1 0

theorem fr_eq (F : List ℕ) (hl : F.length = 8) (k : Fin 8) : fr F k = F[k.1]'(by omega) := by
  unfold fr; rw [List.getD_eq_getElem?_getD, List.getElem?_eq_getElem (by omega), Option.getD_some]

theorem fr_mem (F : List ℕ) (hl : F.length = 8) (k : Fin 8) : fr F k ∈ F := by
  rw [fr_eq F hl]; exact List.getElem_mem _

theorem mem_fr (F : List ℕ) (hl : F.length = 8) {f : ℕ} (hf : f ∈ F) : ∃ k, fr F k = f := by
  obtain ⟨i, hi, rfl⟩ := List.getElem_of_mem hf
  exact ⟨⟨i, by omega⟩, by rw [fr_eq F hl]⟩

theorem fr_inj (F : List ℕ) (hl : F.length = 8) (hn : F.Nodup) : Function.Injective (fr F) := by
  intro k l h
  rw [fr_eq F hl, fr_eq F hl] at h
  exact Fin.ext ((List.Nodup.getElem_inj_iff hn).mp h)

theorem frame_facts (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (F : List ℕ) (hF : frameOK F = true) :
    F.length = 8 ∧ F.Nodup ∧ (∀ k, fr F k < 104) ∧ (∀ k, A (fr F k) ⬝ᵥ B (fr F k) ≠ 0) ∧
      ∀ k l : Fin 8, k ≠ l → A (fr F k) ⬝ᵥ B (fr F l) = 0 := by
  unfold frameOK at hF
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.mem_range, Bool.or_eq_true,
    beq_iff_eq] at hF
  obtain ⟨⟨⟨hl, hlt⟩, hn⟩, ho⟩ := hF
  have hlt' : ∀ k, fr F k < 104 := fun k => hlt _ (fr_mem F hl k)
  refine ⟨hl, hn, hlt', fun k => hdiag _ (hlt' k), fun k l hkl => ?_⟩
  rcases ho k.1 k.2 l.1 l.2 with h | h
  · exact absurd (Fin.ext h) hkl
  · exact hmask _ (hlt' k) _ (hlt' l) (orth_of_orthB (hlt' k) (hlt' l) h)

/-- **`ExpOK` from a non-degenerate frame.** -/
theorem expOK_of_indep (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (u : Fin 9 → K) (m : ℕ)
    (hu : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (F : List ℕ) (hF : frameOK F = true)
    (hind : LinearIndependent K (Fin.cons u (fun k => B (fr F k)) : Fin 9 → Fin 9 → K)) :
    ExpOK A B m F := by
  obtain ⟨hl, hn, -, hd, hoff⟩ := frame_facts A B hdiag hmask F hF
  intro t ht hout s
  set D : Finset (Fin 8) := Finset.univ.filter (fun k => m.testBit (fr F k) = true) with hD
  have h := partial_expansion A B u (fr F) D hind (fun k hk => hu _ (Finset.mem_filter.mp hk).2) hd hoff t
    (hu t ht) (fun k hk => hout _ (fr_mem F hl k) (by simpa [hD] using hk)) s
  have himg : F.toFinset.filter (fun f => m.testBit f = true) = D.image (fr F) := by
    ext f
    simp only [Finset.mem_filter, List.mem_toFinset, Finset.mem_image, hD, Finset.mem_univ, true_and]
    constructor
    · rintro ⟨hf, hm⟩
      obtain ⟨k, rfl⟩ := mem_fr F hl hf
      exact ⟨k, hm, rfl⟩
    · rintro ⟨k, hm, rfl⟩
      exact ⟨fr_mem F hl k, hm⟩
  unfold Mx
  rw [h, himg, Finset.sum_image (fun k _ l _ hkl => fr_inj F hl hn hkl)]

/-- a frame lying entirely in the dead set is non-degenerate for any `u ≠ 0` -/
theorem indep_of_dead (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (u : Fin 9 → K) (hu0 : u ≠ 0)
    (F : List ℕ) (hF : frameOK F = true) (hdead : ∀ k, A (fr F k) ⬝ᵥ u = 0) :
    LinearIndependent K (Fin.cons u (fun k => B (fr F k)) : Fin 9 → Fin 9 → K) := by
  obtain ⟨-, -, -, hd, hoff⟩ := frame_facts A B hdiag hmask F hF
  by_contra hdeg
  obtain ⟨c, hc0, hc⟩ := degenerate_repr A B u (fr F) Finset.univ hdeg (fun k _ => hdead k) hd hoff
  apply hu0
  rw [hc]
  exact Finset.sum_eq_zero fun k _ => by rw [hc0 k (Finset.mem_univ _), zero_smul]

/-- **`ExpOK` for frames inside the dead set** (branch (b): `u = B s₀`, full frames inside `R`). -/
theorem expOK_of_dead (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (u : Fin 9 → K) (hu0 : u ≠ 0) (m : ℕ)
    (hu : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (F : List ℕ) (hF : frameOK F = true)
    (hFd : F.all m.testBit = true) : ExpOK A B m F := by
  have hl := (frame_facts A B hdiag hmask F hF).1
  refine expOK_of_indep A B hdiag hmask u m hu F hF (indep_of_dead A B hdiag hmask u hu0 F hF fun k => hu _ ?_)
  exact List.all_eq_true.mp hFd _ (fr_mem F hl k)

/-- a column vector with non-zero diagonal entry is non-zero -/
theorem B_ne_zero (A B : ℕ → Fin 9 → K) {s : ℕ} (h : A s ⬝ᵥ B s ≠ 0) : B s ≠ 0 := by
  intro h0; rw [h0, dotProduct_zero] at h; exact h rfl

/-- every stored descriptor has a frame (`frameOK`); with `full`, a frame inside the dead set -/
def framesOK (DS : BT (List ℕ)) (m : ℕ) (full : Bool) : Bool :=
  (List.range (2 ^ DS.dp)).all fun a =>
    DS.get [] a == [] || (frameOK (dfr (DS.get [] a)) && (!full || (dfr (DS.get [] a)).all m.testBit))

theorem framesOK_get (DS : BT (List ℕ)) (m : ℕ) (full : Bool) (h : framesOK DS m full = true) (a : ℕ)
    (ha : DS.get [] a ≠ []) :
    frameOK (dfr (DS.get [] a)) = true ∧ (full = true → (dfr (DS.get [] a)).all m.testBit = true) := by
  by_cases hlt : a < 2 ^ DS.dp
  · unfold framesOK at h
    have h' := List.all_eq_true.mp h a (List.mem_range.mpr hlt)
    simp only [Bool.or_eq_true, beq_iff_eq, Bool.and_eq_true, Bool.not_eq_true'] at h'
    rcases h' with h1 | ⟨h1, h2⟩
    · exact absurd h1 ha
    · refine ⟨h1, fun hf => ?_⟩
      rcases h2 with h2 | h2
      · rw [hf] at h2; cases h2
      · exact h2
  · exact absurd (BT.get_big _ _ _ (Nat.not_lt.mp hlt)) ha

/-- `ExpOK` for all stored descriptors whose frames lie in the dead set (branch (b)) -/
theorem hExp_dead (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (u : Fin 9 → K) (hu0 : u ≠ 0) (m : ℕ)
    (hu : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (DS : BT (List ℕ)) (h : framesOK DS m true = true) :
    ∀ a, DS.get [] a ≠ [] → ExpOK A B m (dfr (DS.get [] a)) := fun a ha =>
  expOK_of_dead A B hdiag hmask u hu0 m hu _ (framesOK_get DS m true h a ha).1
    ((framesOK_get DS m true h a ha).2 rfl)

/-- `ExpOK` for all stored descriptors from non-degeneracy of their frames (branches (a), (c)) -/
theorem hExp_indep (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0) (u : Fin 9 → K) (m : ℕ)
    (hu : ∀ x, m.testBit x = true → A x ⬝ᵥ u = 0) (DS : BT (List ℕ)) (h : framesOK DS m false = true)
    (hind : ∀ a, DS.get [] a ≠ [] →
      LinearIndependent K (Fin.cons u (fun k => B (fr (dfr (DS.get [] a)) k)) : Fin 9 → Fin 9 → K)) :
    ∀ a, DS.get [] a ≠ [] → ExpOK A B m (dfr (DS.get [] a)) := fun a ha =>
  expOK_of_indep A B hdiag hmask u m hu _ (framesOK_get DS m false h a ha).1 (hind a ha)

end RankNine.T2
