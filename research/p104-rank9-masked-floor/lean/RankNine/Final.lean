import RankNine.Main
import RankNine.T2Sym
import RankNine.T3St3
import RankNine.LPHand
import RankNine.FC3Hand

set_option linter.unusedSectionVars false

/-!
# The rank-9 floor `C(P104) ≥ 56`, hand route (assembly)

All BForm facts are Lean theorems here: `Capacity` (`capacity_P104`), `BicliqueFact` (`biclique_P104`),
`CensusFact` (`LP.censusFact_P104`, Lemma P "no six" by hand from the type-1 table `t1xOK`), FC3
(`framed_of_three_h`, witness table `fwOK`).  The remaining hypotheses are **finite tables**, each checked by `#eval`
and by an independent Python checker with a log (Internal `rank9-p104-2026-10-29`):
* `hrec`: for each of the 387 framed types, a T1 record + T3 record (ordinary types) or a stage-3 record + T3 record
  (hard types);
* `grpOK`, `orbOK flData`, `flNoFrame flData` (the group of order 384, the frameless orbit list);
* `fwOK FW` (frames inside the single dead sets), `t1xOK` (type 1 of Lemma P);
* `hT2`: the T2 orbit records of the 9 frameless representatives with their pair certificates.
-/

namespace RankNine.Final

open Matrix BForm BForm.E8 RankNine.Facts

/-- the records of one framed type `k` -/
def RecOK (k : ℕ) : Prop :=
  (∃ d1 : T2.T1D, ∃ d3 : T3D, d1.ok = true ∧ d3.ok (typeMask.getD k 0) = true ∧
      d1.m = typeMask.getD k 0 ∧ d3.zm = d1.zm) ∨
  (∃ st : T2.St3, ∃ d3 : T3D, st.ok = true ∧ d3.ok (typeMask.getD k 0) = true ∧
      st.m0 = typeMask.getD k 0 ∧ d3.zm = st.zm)

theorem floorType_of_rec {K : Type} [Field K] [CharZero K] (hcensus : CensusFact labK (rK K)) {k : ℕ}
    (h : RecOK k) : FloorType K k := by
  intro A B u hu hZ hdiag hmask Al Bl hA hB P Q hPQ
  rcases h with ⟨d1, d3, h1, h3, hm, hz⟩ | hst
  · exact floor_of_records capacity_P104 biclique_P104 hcensus k d1 d3 h1 h3 hm hz A B u hu hZ hdiag hmask
      Al Bl hA hB P Q hPQ
  · exact floor_of_st3_ex capacity_P104 biclique_P104 hcensus k hst A B u hu hZ hdiag hmask Al Bl hA hB P Q hPQ

/-- **Main theorem (rank 9, hand route).** Every nine-term decoder of a masked rank-9 matrix on P104 costs at
least 56. -/
theorem floor56_hand {K : Type} [Field K] [CharZero K]
    (hrec : ∀ k < 387, RecOK k) (hgrp : grpOK = true) (horb : orbOK flData = true)
    (hflf : flNoFrame flData = true) (FW : List ℕ) (hfw : fwOK FW = true) (ht1x : LP.t1xOK = true)
    (hT2 : ∃ R : List ℕ, ∃ W : List (ℕ × ℕ × ℕ), T2M.t2wOK R flData W = true ∧ T2M.flClosed flData = true ∧
      ∀ k < R.length, ∃ r : T2S.T2SR, r.ok (R.getD k 0) flData = true)
    (A B : ℕ → Fin 9 → K) (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0)
    (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (Al Bl : Matrix (Fin 9) (Fin 104) K) (hA : Al * Matrix.of (fun (v : Fin 104) (i : Fin 9) => A v i) = 1)
    (hB : Bl * Matrix.of (fun (v : Fin 104) (i : Fin 9) => B v i) = 1)
    (P Q : Matrix (Fin 104) C9 K) (h : Matrix.of (fun v s : Fin 104 => Mx A B v s) = P * Qᵀ) :
    56 ≤ cost labK P Q :=
  Main.floor56 (fun k hk => floorType_of_rec (LP.censusFact_P104 ht1x) (hrec k hk)) hgrp horb hflf
    (framed_of_three_h hfw) (T2S.t2Pair_of_exS hgrp hT2) A B hdiag hmask Al Bl hA hB P Q h

end RankNine.Final
