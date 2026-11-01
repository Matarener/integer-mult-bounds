import BForm.E8h.Checks

namespace BForm.E8h

set_option maxRecDepth 100000

theorem lenOK_true : lenOK = true := by decide +kernel
theorem normOK_true : normOK = true := by decide +kernel
theorem reflOK_true : reflOK = true := by decide +kernel
theorem coefOK_true : coefOK = true := by decide +kernel
theorem portOK_true : portOK = true := by decide +kernel
theorem paraP_true : ∀ b0 b1 b2 b3 b4 b5 b6 b7 : Bool, paraP b0 b1 b2 b3 b4 b5 b6 b7 = true := by
  decide +kernel
theorem rfiOK_true : rfiOK = true := by decide +kernel
theorem rootOK_true : rootOK = true := by decide +kernel
theorem d7OK_true : d7OK = true := by decide +kernel

end BForm.E8h
