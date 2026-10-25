-- SPDX-License-Identifier: Apache-2.0
import CompilerAudit.SourceBridge
open CompilerAudit.SourceBridge
-- Negative probe: without wrapper freshness, retained count is not the segment count.
example : (srcRetained (emitSrc ([⟨0, 7, 0⟩, ⟨0, 7, 0⟩] : List (Seg Nat)) 0)).card = 2 := by decide
