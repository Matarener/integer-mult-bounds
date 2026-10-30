import BForm.E8h.SpanH
import BForm.Main

/-!
# The B-form floor for P104 with RootFact and SpanFact proved

`rootFact_h` and `spanFact_h` come from the dominant chamber argument (hand proofs `HAND-ROOTFACT.md`,
`HAND-SPANFACT.md`); their finite checks are small kernel computations.
-/

namespace BForm.E8h

open Matrix BForm.E8

variable {K : Type*} [Field K] [CharZero K]

/-- `BForm.bform_floor` for P104 with `RootFact` and `SpanFact` discharged. -/
theorem bform_floor_P104_h (hcap : BForm.Capacity labK) (hbic : BForm.BicliqueFact (rK K))
    (hcensus : BForm.CensusFact labK (rK K))
    (α α' c β : Fin 104 → K) (hdiag : ∀ t, (c t = 0 ∨ β t = 0) → α t ≠ 0 ∧ α' t ≠ 0)
    (hbi : ∀ u s, c u ≠ 0 → β s ≠ 0 → u ≠ s → ¬ BForm.Orth (rK K) u s)
    (hpat : BForm.Pattern (rK K) (BForm.bX (rK K) α c * (BForm.bX (rK K) α' β)ᵀ))
    (Xl Yl : Matrix BForm.C9 (Fin 104) K) (hX : Xl * BForm.bX (rK K) α c = 1) (hY : Yl * BForm.bX (rK K) α' β = 1)
    (P Q : Matrix (Fin 104) BForm.C9 K) (h : BForm.bX (rK K) α c * (BForm.bX (rK K) α' β)ᵀ = P * Qᵀ) :
    56 ≤ BForm.cost labK P Q :=
  BForm.bform_floor labK hcap (rK K) rootFact_h spanFact_h hbic hcensus α α' c β hdiag hbi hpat Xl Yl hX hY P Q h

end BForm.E8h
