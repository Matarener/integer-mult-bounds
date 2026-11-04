import RankNine.T1Tab
import RankNine.Floor

set_option linter.unusedSectionVars false

/-!
# T3 per type from a table, and the floor for one framed type from two records (hand route)

`T3D` holds the T3 data of one framed type (frame `f` inside `zm`, outer lines `OL` with rank-7 line
certificates, glued rows `O` with pair certificates over the mask `sm`), exactly the data of the old generated
files `Cert/Glue<k>.lean`, but checked by one Boolean `T3D.ok` instead of `decide`.  `floor_of_records` is the old
`Cert/Fl<k>.floor` proved once for all types: T1 from the record `T1D` (`T1D.sound`), T3 (`t3_type`) and the
B-form floor (`floor_noU`).  This file covers the types without a special line (`U = 104`).
-/

namespace RankNine

open Matrix

/-- the T3 data of one framed type -/
structure T3D where
  f : ℕ
  zm : ℕ
  sm : ℕ
  OL : List ℕ
  O : List ℕ
  bad : List (ℕ × ℕ)
  T : List PCert
  LT : List (ℕ × ℕ × RCert)

/-- **the check of one T3 record** for the dead mask `m` -/
def T3D.ok (d : T3D) (m : ℕ) : Bool :=
  frInOK m d.zm d.f && fvecOK d.f &&
  (List.range 104).all (fun x => !d.zm.testBit x || m.testBit x) &&
  (List.range 104).all (fun v => d.zm.testBit v || decide (v ∈ d.O) || m.testBit v) &&
  d.O.all (· < 104) && d.T.all (pcOK d.sm) && coverOK d.O d.bad d.T && matchOK d.O d.bad && fiveOK d.O d.bad &&
  lineOK d.zm d.OL d.LT && decide (d.zm < 2 ^ 104) &&
  (List.range 104).all (fun s => !d.sm.testBit s || d.zm.testBit s || decide (s ∈ d.OL)) &&
  decide (d.sm < 2 ^ 104) && d.OL.all (· < 104) &&
  (List.range 104).all (fun v => d.zm.testBit v || decide (v ∈ d.OL) || v == 104)

/-- **C(P104) ≥ 56 for one framed type from its two records** (no special line). -/
theorem floor_of_records {K : Type*} [Field K] [CharZero K] (hcap : BForm.Capacity BForm.E8.labK)
    (hbic : BForm.BicliqueFact (BForm.E8.rK K)) (hcensus : BForm.CensusFact BForm.E8.labK (BForm.E8.rK K))
    (k : ℕ) (d1 : T2.T1D) (d3 : T3D) (h1 : d1.ok = true) (h3 : d3.ok (typeMask.getD k 0) = true)
    (hm : d1.m = typeMask.getD k 0) (hz : d3.zm = d1.zm)
    (A B : ℕ → Fin 9 → K) (u : Fin 9 → K) (hu : u ≠ 0)
    (hZ : ∀ x, (typeMask.getD k 0).testBit x = true → A x ⬝ᵥ u = 0)
    (hdiag : ∀ x < 104, A x ⬝ᵥ B x ≠ 0) (hmask : ∀ x < 104, ∀ y < 104, orth x y = true → A x ⬝ᵥ B y = 0)
    (Al Bl : Matrix (Fin 9) (Fin 104) K) (hA : Al * Matrix.of (fun (v : Fin 104) (i : Fin 9) => A v i) = 1)
    (hB : Bl * Matrix.of (fun (v : Fin 104) (i : Fin 9) => B v i) = 1)
    (P' Q' : Matrix (Fin 104) BForm.C9 K) (h : Matrix.of (fun v s : Fin 104 => Mx A B v s) = P' * Q'ᵀ) :
    56 ≤ BForm.cost BForm.E8.labK P' Q' := by
  obtain ⟨g, hg, hG⟩ := d1.sound h1 A B hdiag hmask u hu (by rw [hm]; exact hZ)
  rw [← hz] at hG
  unfold T3D.ok at h3
  simp only [Bool.and_eq_true] at h3
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨hfin, hfv⟩, hzm⟩, hOG⟩, hO⟩, hT⟩, hc⟩, hmt⟩, hf⟩, hL⟩, hzlt⟩, hsm⟩, hsmlt⟩, hOL⟩, hcov⟩ := h3
  obtain ⟨lam, eta, hrep, -, hin, hcolU, hrowd, hglue, -⟩ := t3_type A B u hu hZ hdiag hmask g hg hG hfin hfv
    (of_decide_eq_true hzlt) hzm hOL hO hcov hOG hsm (of_decide_eq_true hsmlt)
    (fun v hv d h1 hd => line_of_data hL hv d h1 hd) (fun h τ L R five => glue_of_data hO hT hc hmt hf R five)
    (fun h => absurd h (lt_irrefl _))
  exact floor_noU hcap hbic hcensus _ _ _ lam eta (fun v s => by rw [Matrix.of_apply]; exact hrep v s)
    (fun s hs => hcolU s hs (by omega)) hrowd (hPs_P104 A B _ d3.f)
    (hglue.imp_right (live_le_four lam _ hin)) (fun t => by rw [Matrix.of_apply]; exact hdiag t t.2)
    (fun x y hd => by rw [Matrix.of_apply]; exact hmask x x.2 y y.2 (by simp [orth, hd]))
    _ _ Al Bl hA hB (by ext v s; simp [Matrix.mul_apply, Mx, dotProduct]) P' Q' h

end RankNine
