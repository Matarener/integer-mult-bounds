# Completion of the newly supplied three-stage E caller

Scope: a source-bound mathematical composition with the local physical contracts
of PR #5464 at 56ba6d7d609124d71c067d6a380caed573963f8f. Its PROOF, MODES and
PRECISION-SCOPE are retained unchanged. This package does not rerun that
41-file native verifier or claim an independently rebuilt physical E provider.

Let P = E_3 E_2⁻¹ E_1. The source's actual F_1, B_2, F_3 word, followed by its
ordinary signed swap, has endpoints Q⁻¹ P D_123 and P D_123 Q. The source supplies
ordinary E and E⁻¹ recoders, including their owned cleanup and rational costs.
The source positive decoder P⁻¹ already gives one independent R73 output.

**Sufficient completion.** On the negative output alone execute, chronologically,

    Q, E_3⁻¹, E_2, E_1⁻¹, Q.

Theorem 1 of PROOF.md gives the other independent R73 output on its original
input. No commutation with Q or between E stages is inserted. Every stage
recoder is the source's supplied ordinary routine. The addition is exactly
2v H1 jobs and three E/E⁻¹ evaluations, with v = 112³. The existing reusable
512-field recoding scratch suffices after the caller's owned cleanup. Gaussian
child workspace remains part of the inherited service contract.

Counting the three local modules and both output decoders gives twelve total
E/E⁻¹ evaluations, three modal-query upper bills and three native/boundary upper
bills. `check_invoice.py` sums their actual MODES.json fields, retaining COPY,
CLEAR, OWN_ZERO, SCALE, SWAP and monomial work. Owned peak is bounded by the
source's v + 20,480 + 512 fields. This is a field-level upper bill, not a newly
proved TM running time or fixed-precision implementation.

The complete Gaussian profile is

    targets: 2v H73,
    paid: 3v (H8 + H9 + H15 + H16) + 61,440 H25 + 2v H1.

Its rank-mass surplus is −1,536,000, or −375/343 per owner. The repaired exact
moment is negative at κ = 0.003027288235. Thus the composition supplies positive
Gaussian endpoints under the pinned local contracts but no profitable supplier.
The source's positive conditional screen was computed before paying this repair.

## An explicit inverse polynomial and the correct norm bound

The source C is real symmetric with spectrum {0, 98, −1078}, K² = I, KC = −C,
and E = K(I−C)⁻¹. Its spectral minimal-polynomial relation implies

    C³ + 980C² − 105644C = 0,
    (I−C)⁻¹ = I − (981C + C²)/104663,
    E = K + (981C + C²)/104663,
    E⁻¹ = K + C,
    104663 = 97 · 1079.

Multiplying (I−C) by the displayed polynomial gives I plus the displayed
zero polynomial divided by 104663. Multiplying by K and using KC = −C gives
the E formula. These are identities of the actual physical similarity too;
scalar coefficients are applied once, not tensor-powered. The checker verifies
the polynomial coefficients exactly and its values at every source eigenvalue.
No cheaper evaluation cost than the source recoder is claimed from this formula.

Because K is a commuting orthogonal involution, the singular values of E are
1, 1/97 and 1/1079. Consequently ‖E‖₂ = 1 and ‖E⁻¹‖₂ = 1079. The full negative
decoder has operator norm at most 1079² = 1,164,241. Unlike the K decoder, it is
not unitary. Its incoming-error bound must include that amplification.

For a schedule that evaluates each complete rational E code exactly before one
coordinatewise rounding, and rounds after each central bit butterfly, a sufficient
additional-error bound is

    1079² (2f + 3) √N · 2⁻ᴮ,

where N counts complex scalar cells. Add 1079² times incoming Euclidean error.
The proof is the same suffix-error telescoping argument: every suffix contains
at most two expanding E⁻¹ factors, one nonexpanding E factor and unitary Q layers.
Exact rational accumulators can be implemented with fixed common denominators
for this finite owner program; they have real storage and integer-arithmetic
cost. This statement does not validate intermediate rounding inside a cheaper
recoder, invoke the K-only dyadic grid, or omit the √N coordinate-to-field factor.
It supplies a sufficient decoder precision schedule, not the missing full-caller
precision/stock/TM admission.

Credit the complete E construction and all source contracts to THU New Media
Research Center / PR #5464 and its retained Ali Romman, Dugongue, Dillon Amburgey,
native, Clifford and compiler predecessors. The conjugation completion and
spectral-polynomial calculation are elementary; this note claims their specific
source-bound application, with substantial OpenAI Codex assistance by one solo
worker, not literature priority or independent physical-provider verification.
