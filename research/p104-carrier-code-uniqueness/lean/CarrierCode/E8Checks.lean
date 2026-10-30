import CarrierCode.E8CheckFrames
import CarrierCode.E8Check3_0
import CarrierCode.E8Check3_1
import CarrierCode.E8Check3_2
import CarrierCode.E8Check3_3
import CarrierCode.E8Check3_4
import CarrierCode.E8Check3_5
import CarrierCode.E8Check3_6
import CarrierCode.E8Check3_7
import CarrierCode.E8Step3

/-! All kernel checks of steps 1–3 combined, and step 3 for every decoding matrix. -/

namespace CarrierCode.E8

open Matrix

theorem step3_checks : ∀ t : ι, seedOK t.val ∧ ∀ x : ι, check3 t.val x.val := by
  intro t
  have ht := t.isLt
  rcases (show t.val / 13 = 0 ∨ t.val / 13 = 1 ∨ t.val / 13 = 2 ∨ t.val / 13 = 3 ∨ t.val / 13 = 4 ∨
      t.val / 13 = 5 ∨ t.val / 13 = 6 ∨ t.val / 13 = 7 by omega) with h | h | h | h | h | h | h | h
  · exact (fun ⟨a, b⟩ => ⟨a, fun x => b x⟩) (step3OK_0 t h)
  · exact (fun ⟨a, b⟩ => ⟨a, fun x => b x⟩) (step3OK_1 t h)
  · exact (fun ⟨a, b⟩ => ⟨a, fun x => b x⟩) (step3OK_2 t h)
  · exact (fun ⟨a, b⟩ => ⟨a, fun x => b x⟩) (step3OK_3 t h)
  · exact (fun ⟨a, b⟩ => ⟨a, fun x => b x⟩) (step3OK_4 t h)
  · exact (fun ⟨a, b⟩ => ⟨a, fun x => b x⟩) (step3OK_5 t h)
  · exact (fun ⟨a, b⟩ => ⟨a, fun x => b x⟩) (step3OK_6 t h)
  · exact (fun ⟨a, b⟩ => ⟨a, fun x => b x⟩) (step3OK_7 t h)

/-- Step 3 for every matrix satisfying the decoding hypotheses: `N t x = 1 + (r_t·r_x)(r_x·v_t)`. -/
theorem step3_all {M : Matrix ι ι (ZMod 3)} {A : Matrix ι (Fin 8) (ZMod 3)} {B : Matrix (Fin 8) ι (ZMod 3)}
    (h : Hyp M A B) (t x : ι) (hnz : dotN t x % 3 ≠ 0) :
    Nm M t x = 1 + Gm t x * (r x ⬝ᵥ vv M t) :=
  step3 h framesOK_true step3_checks t x hnz

end CarrierCode.E8
