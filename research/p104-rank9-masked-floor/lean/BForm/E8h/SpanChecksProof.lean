import BForm.E8h.SpanChecks

namespace BForm.E8h

set_option maxRecDepth 100000

theorem oOK_true : oOK = true := by decide +kernel
theorem maskOK_true : maskOK = true := by decide +kernel
theorem o44OK_true : o44OK = true := by decide +kernel

end BForm.E8h
