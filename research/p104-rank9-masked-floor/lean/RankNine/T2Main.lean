import RankNine.T2Hand
import RankNine.Main

set_option linter.unusedSectionVars false

/-!
# T2 for all frameless pairs (`Main.T2Pair`) from the 9 representative records

Every frameless set `c ∈ FL` contains the image `g(r_k)` of one of the 9 representatives `r_k` under a group element
`g` (witness table `W`, checked by `t2wOK`).  The transported decoder `A ∘ g` has the rows of `r_k` dead for `u`,
and the rows of the preimage `g⁻¹(c')` dead for `v`; that preimage is again in `FL` (`flClosed`: for every `g`, the
preimage map permutes `FL`, checked by comparing sorted lists).  `T2R.sound` for `r_k` and the partner `g⁻¹(c')`
gives the contradiction.

Table hypotheses (checked by `#eval`, Python cross-check): existence of 9 records with `T2R.ok`, `t2wOK`, `flClosed`.
-/

namespace RankNine.T2M

open Matrix RankNine RankNine.Facts

/-- preimage of the mask `c` under the group element `g` -/
def pre (g c : ℕ) : ℕ := T2.lmask ((List.range 104).filter fun x => c.testBit (gl g x))

theorem pre_bit {g c x : ℕ} (h : (pre g c).testBit x = true) : x < 104 ∧ c.testBit (gl g x) = true := by
  rw [pre, T2.lmask_bit, List.mem_filter, List.mem_range] at h
  exact h

/-- **finite fact FLC**: for every group element the preimage map permutes `FL` -/
def flClosed (FL : List ℕ) : Bool :=
  (List.range 384).all fun g => (FL.map (pre g)).mergeSort (fun a b => decide (a ≤ b)) == FL.mergeSort (fun a b => decide (a ≤ b))

theorem pre_mem {FL : List ℕ} (h : flClosed FL = true) {g : ℕ} (hg : g < 384) {c : ℕ} (hc : c ∈ FL) :
    pre g c ∈ FL := by
  have e := List.all_eq_true.mp h g (List.mem_range.mpr hg)
  rw [beq_iff_eq] at e
  have h1 := List.mergeSort_perm (FL.map (pre g)) (fun a b => decide (a ≤ b))
  have h2 := List.mergeSort_perm FL (fun a b => decide (a ≤ b))
  rw [e] at h1
  exact (h1.symm.trans h2).mem_iff.mp (List.mem_map.mpr ⟨c, hc, rfl⟩)

/-- representative `k` maps into `c` under `g` -/
def imgOK2 (R : List ℕ) (g k c : ℕ) : Bool :=
  decide (g < 384) && decide (k < R.length) && decide (R.getD k 0 < 2 ^ 104) &&
  (List.range 104).all fun x => !(R.getD k 0).testBit x || c.testBit (gl g x)

/-- **finite fact W**: every frameless set has a witness `(c, g, k)` -/
def t2wOK (R : List ℕ) (FL : List ℕ) (W : List (ℕ × ℕ × ℕ)) : Bool :=
  FL.all fun c => W.any fun e => e.1 == c && imgOK2 R e.2.1 e.2.2 c

/-- **T2 for all pairs** from the representative records. -/
theorem t2Pair_of_records (K : Type) [Field K] [CharZero K] (hgrp : grpOK = true) (FL R : List ℕ)
    (W : List (ℕ × ℕ × ℕ)) (hw : t2wOK R FL W = true) (hcl : flClosed FL = true)
    (hT : ∀ k < R.length, ∃ r : T2.T2R, r.ok (R.getD k 0) FL = true) :
    Main.T2Pair K FL := by
  intro A B hdiag hmask Al Bl _ _ u v huv c c' hc hc' hu hv
  have hc : c ∈ FL := by simpa using hc
  have hc' : c' ∈ FL := by simpa using hc'
  obtain ⟨e, -, he⟩ := List.any_eq_true.mp (List.all_eq_true.mp hw c hc)
  rw [Bool.and_eq_true] at he
  replace he := he.2
  unfold imgOK2 at he
  simp only [Bool.and_eq_true, decide_eq_true_eq, List.all_eq_true, List.mem_range, Bool.or_eq_true,
    Bool.not_eq_true'] at he
  obtain ⟨⟨⟨hg, hk⟩, hRlt⟩, himg⟩ := he
  set g := e.2.1
  set k := e.2.2
  set π := permOf hgrp hg
  have hu' : ∀ x, (R.getD k 0).testBit x = true → (fun y => A (Tr.pn π y)) x ⬝ᵥ u = 0 := by
    intro x hx
    have hx104 : x < 104 := by
      by_contra hcn
      rw [testBit_big hRlt (by omega)] at hx; exact absurd hx (by simp)
    have hcx := (himg x hx104).resolve_left (by rw [hx]; simp)
    show A (Tr.pn π x) ⬝ᵥ u = 0
    rw [pn_permOf hgrp hg hx104]
    exact hu _ hcx
  have hv' : ∀ x, (pre g c').testBit x = true → (fun y => A (Tr.pn π y)) x ⬝ᵥ v = 0 := by
    intro x hx
    obtain ⟨hx104, hcx⟩ := pre_bit hx
    show A (Tr.pn π x) ⬝ᵥ v = 0
    rw [pn_permOf hgrp hg hx104]
    exact hv _ hcx
  obtain ⟨r, hr⟩ := hT k hk
  exact T2.T2R.sound r _ FL hr (fun x => A (Tr.pn π x)) (fun x => B (Tr.pn π x))
    (Tr.diag_perm π A B hdiag) (Tr.mask_perm π (orth_perm hgrp hg) A B hmask) u v huv (pre g c')
    (pre_mem hcl hg hc') hu' hv'

/-- **T2 as existence of data** (the table hypothesis): representatives, witnesses and 9 checked records. -/
theorem t2Pair_of_ex (K : Type) [Field K] [CharZero K] (hgrp : grpOK = true)
    (hex : ∃ R : List ℕ, ∃ W : List (ℕ × ℕ × ℕ), t2wOK R flData W = true ∧ flClosed flData = true ∧
      ∀ k < R.length, ∃ r : T2.T2R, r.ok (R.getD k 0) flData = true) :
    Main.T2Pair K flData := by
  obtain ⟨R, W, hw, hcl, hT⟩ := hex
  exact t2Pair_of_records K hgrp flData R W hw hcl hT

end RankNine.T2M
