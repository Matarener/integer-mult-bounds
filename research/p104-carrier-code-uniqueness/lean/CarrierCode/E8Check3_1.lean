import CarrierCode.E8Defs

/-! Kernel check of the step-3 certificates for the ports t with t / 13 = 1 (generated). -/

namespace CarrierCode.E8

theorem step3OK_1 : step3OK 1 := by decide +kernel

end CarrierCode.E8
