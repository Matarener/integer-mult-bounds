import CarrierCode.E8Defs4

/-! Kernel check of the step-4 data (A2 triangles and inverse matrices). -/

namespace CarrierCode.E8

theorem step4OK_true : step4OK := by decide +kernel

end CarrierCode.E8
