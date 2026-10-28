import CarrierCode.E8Defs

/-! Kernel check of the step-3 certificates for the ports t with t / 13 = 5 (generated). -/

namespace CarrierCode.E8

theorem step3OK_5 : step3OK 5 := by decide +kernel

end CarrierCode.E8
