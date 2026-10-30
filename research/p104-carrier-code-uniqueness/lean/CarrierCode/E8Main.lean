import CarrierCode.E8Checks
import CarrierCode.E8Check4
import CarrierCode.E8Check5
import CarrierCode.E8Step5

/-!
# Search-free uniqueness of the length-8 decoding code (E8-PROOF.md)

Let `M` be the 104 × 104 matrix of decoding vectors over `F₃`: `M = A * B` with inner dimension 8 (the code has
dimension at most 8), unit diagonal, and `M i j = 0` whenever ports `i ≠ j` conflict (their E8 roots are
orthogonal).  Then `M = D (2 Gm) D` for a diagonal `±1` matrix `D`, where `Gm` is the Gram form of the roots mod 3.
So the decoding vectors, and the code they span, are unique up to signs.

All finite inputs are checked by the kernel (`decide +kernel`), with no `native_decide`.
-/

namespace CarrierCode.E8

theorem checks3_true : Checks3 := ⟨framesOK_true, step3_checks⟩

theorem decoding_unique (M : Matrix ι ι (ZMod 3)) (A : Matrix ι (Fin 8) (ZMod 3)) (B : Matrix (Fin 8) ι (ZMod 3))
    (h : Hyp M A B) :
    ∃ D : ι → ZMod 3, (∀ j, D j * D j = 1) ∧ ∀ j k, M j k = D j * D k * (2 * Gm j k) :=
  signs h checks3_true step4OK_true check5_true

end CarrierCode.E8
