-- SPDX-License-Identifier: Apache-2.0
import CompilerAudit.SourceBridge
open CompilerAudit.SourceBridge

-- Positive contract probe: hypotheses are satisfiable and the op-stream model counts as stated.

-- LOW enumeration/inverse hypotheses hold for the identity ranking.
example (N : Nat) : List.range N = (List.range N).map id ∧ ∀ o, o < N → id (id o) = o :=
  ⟨(List.map_id _).symm, fun _ _ => rfl⟩

-- Two residual segments (2 and 0 blocks), one wrapper-free prefix op and a tail of 3.
example : (srcRefs (emitSrc ([⟨1, 7, 2⟩, ⟨0, 8, 0⟩] : List (Seg Nat)) 3)).length = 6 := by decide
example : (srcRetained (emitSrc ([⟨1, 7, 2⟩, ⟨0, 8, 0⟩] : List (Seg Nat)) 3)).card = 2 := by decide
example : (srcRefs (emitSrc ([⟨1, 7, 2⟩, ⟨0, 8, 0⟩] : List (Seg Nat)) 3)).length = 6 :=
  (refs_length ([⟨1, 7, 2⟩, ⟨0, 8, 0⟩] : List (Seg Nat)) 3).trans (by decide)

-- Freshness is load-bearing: duplicate wrappers collapse the retained count.
example : (srcRetained (emitSrc ([⟨0, 7, 0⟩, ⟨0, 7, 0⟩] : List (Seg Nat)) 0)).card = 1 := by decide
