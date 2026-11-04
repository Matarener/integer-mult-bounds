import RankNine.Cap6Hand

/-! The finite fact `cap6OK` (512 labels × 120 lines of weight 3 or 7), by `decide`, as `capOK_true`. -/

namespace RankNine.Facts

set_option maxRecDepth 100000 in
theorem cap6OK_true : cap6OK = true := by decide +kernel

/-- **Cap6 for P104.** -/
theorem cap6_P104 : ∀ R : Finset (Fin 104), 21 ≤ R.card → 7 ≤ BForm.lspan BForm.E8.labK R :=
  cap6_hand cap6OK_true

end RankNine.Facts
