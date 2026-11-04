import RankNine.T1Tab
import RankNine.Floor

set_option linter.unusedSectionVars false

/-!
# T3 per type from a table, and the floor for one framed type from two records (hand route)

`T3D` holds the T3 data of one framed type (frame `f` inside `zm`, outer lines `OL` with rank-7 line
certificates, glued rows `O` with pair certificates over the mask `sm`), exactly the data of the old generated
files `Cert/Glue<k>.lean`, but checked by one Boolean `T3D.ok` instead of `decide`.  `floor_of_records` is the old
`Cert/Fl<k>.floor` proved once for all types: T1 from the record `T1D` (`T1D.sound`), T3 (`t3_type`) and the
B-form floor (`floor_noU`).  Types with a special line `U < 104` use `floor_U` with the pinning data `GC`, `BsL`.
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
  /-- the special line (`104`: none) and its data: two orthogonal pinning columns, pinning lines `GC`, `BsL` -/
  U : ℕ
  s1 : ℕ
  s2 : ℕ
  ks : ℕ
  kt : ℕ
  Cs : RCert
  Ct : RCert
  GC : List (ℕ × ℕ × RCert)
  BsL : List ℕ

/-- **the check of one T3 record** for the dead mask `m` -/
def T3D.ok (d : T3D) (m : ℕ) : Bool :=
  frInOK m d.zm d.f && fvecOK d.f &&
  (List.range 104).all (fun x => !d.zm.testBit x || m.testBit x) &&
  (List.range 104).all (fun v => d.zm.testBit v || decide (v ∈ d.O) || m.testBit v) &&
  d.O.all (· < 104) && d.T.all (pcOK d.sm) && coverOK d.O d.bad d.T && matchOK d.O d.bad && fiveOK d.O d.bad &&
  lineOK d.zm d.OL d.LT && decide (d.zm < 2 ^ 104) &&
  (List.range 104).all (fun s => !d.sm.testBit s || d.zm.testBit s || decide (s ∈ d.OL)) &&
  decide (d.sm < 2 ^ 104) && d.OL.all (· < 104) &&
  (List.range 104).all (fun v => d.zm.testBit v || decide (v ∈ d.OL) || v == d.U) &&
  (d.U == 104 || (decide (d.U < 104) && decide (d.s1 < 104) && decide (d.s2 < 104) && decide (dot d.s1 d.s2 = 0) &&
    decide (dot d.U d.s1 = 0) && decide (dot d.U d.s2 = 0) && decide (d.s1 ∈ d.OL) && decide (d.s2 ∈ d.OL) &&
    lcxOK d.zm d.s1 d.U d.ks d.Cs && lcxOK d.zm d.s2 d.U d.kt d.Ct &&
    d.GC.all (fun e => decide (e.1 < 104) && dot e.1 d.U == 0 && lcxOK d.zm e.1 d.U e.2.1 e.2.2) &&
    decide (5 ≤ (Finset.univ.filter fun v : Fin 104 => (v : ℕ) ∈ d.GC.map (fun e => e.1)).card) &&
    decide (d.U ∈ d.BsL) && decide ((Finset.univ.filter fun v : Fin 104 => (v : ℕ) ∈ d.BsL).card ≤ 4) &&
    (List.range 104).all (fun s => decide (s ∈ d.BsL) || (d.GC.map (fun e => e.1)).any (fun v => dot v s == 0))))

/-- **C(P104) ≥ 56 for one framed type from its two records.** -/
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
  obtain ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨hfin, hfv⟩, hzm⟩, hOG⟩, hO⟩, hT⟩, hc⟩, hmt⟩, hf⟩, hL⟩, hzlt⟩, hsm⟩, hsmlt⟩, hOL⟩, hcov⟩,
    hspec⟩ := h3
  simp only [Bool.or_eq_true, beq_iff_eq, Bool.and_eq_true, decide_eq_true_eq] at hspec
  have hSP : SpecialH d3.zm d3.U d3.OL := by
    intro hU
    rcases hspec with e | ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨-, h1⟩, h2⟩, h12⟩, hu1⟩, hu2⟩, hm1⟩, hm2⟩, hc1⟩, hc2⟩, -⟩, -⟩, -⟩, -⟩, -⟩
    · omega
    · exact ⟨d3.s1, d3.s2, d3.ks, d3.kt, d3.Cs, d3.Ct, h1, h2, h12, hu1, hu2, hm1, hm2, hc1, hc2⟩
  obtain ⟨lam, eta, hrep, -, hin, hcolU, hrowd, hglue, hpinT⟩ := t3_type A B u hu hZ hdiag hmask g hg hG hfin hfv
    (of_decide_eq_true hzlt) hzm hOL hO hcov hOG hsm (of_decide_eq_true hsmlt)
    (fun v hv d h1 hd => line_of_data hL hv d h1 hd) (fun h τ L R five => glue_of_data hO hT hc hmt hf R five) hSP
  have hdg : ∀ t, Matrix.of (fun v s : Fin 104 => Mx A B v s) t t ≠ 0 := fun t => by
    rw [Matrix.of_apply]; exact hdiag t t.2
  have hmk : ∀ x y : Fin 104, dot x y = 0 → Matrix.of (fun v s : Fin 104 => Mx A B v s) x y = 0 := fun x y hd => by
    rw [Matrix.of_apply]; exact hmask x x.2 y y.2 (by simp [orth, hd])
  have hAB : Matrix.of (fun v s : Fin 104 => Mx A B v s) = Matrix.of (fun (v : Fin 104) (i : Fin 9) => A v i) *
      (Matrix.of (fun (v : Fin 104) (i : Fin 9) => B v i))ᵀ := by
    ext v s; simp [Matrix.mul_apply, Mx, dotProduct]
  rcases hspec with hU | ⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨⟨hU, -⟩, -⟩, -⟩, -⟩, -⟩, -⟩, -⟩, -⟩, -⟩, hGC⟩, hG5⟩, hUB⟩, hBs⟩, hcovB⟩
  · exact floor_noU hcap hbic hcensus _ _ _ lam eta (fun v s => by rw [Matrix.of_apply]; exact hrep v s)
      (fun s hs => hcolU s hs (by omega)) hrowd (hPs_P104 A B _ d3.f)
      (hglue.imp_right (live_le_four lam _ hin)) hdg hmk _ _ Al Bl hA hB hAB P' Q' h
  · have hGl : ∀ s ∈ d3.GC.map (fun e => e.1), s < 104 := by
      intro s hs
      obtain ⟨e, hme, rfl⟩ := List.mem_map.mp hs
      have hce := (List.all_eq_true.mp hGC) e hme
      simp only [Bool.and_eq_true, decide_eq_true_eq] at hce
      exact hce.1.1
    have hpin : ∀ s ∈ d3.GC.map (fun e => e.1), lam s = 0 →
        ∃ b : K, cS A B g d3.f d3.U = b • rho K d3.U := by
      intro s hs hl
      obtain ⟨e, hme, rfl⟩ := List.mem_map.mp hs
      have hce := (List.all_eq_true.mp hGC) e hme
      simp only [Bool.and_eq_true, decide_eq_true_eq, beq_iff_eq] at hce
      exact hpinT hU e.1 hce.1.1 hl hce.1.2 e.2.1 e.2.2 hce.2
    exact floor_U hcap hbic hcensus _ _ _ lam eta (fun v s => by rw [Matrix.of_apply]; exact hrep v s) d3.U
      hcolU hrowd (hPs_P104 A B _ d3.f) (hcs_P104 A B _ d3.f) (hglue.imp_right (live_le_four lam _ hin))
      _ d3.BsL hGl hpin hG5 hUB hBs hcovB hdg hmk _ _ Al Bl hA hB hAB P' Q' h

end RankNine
