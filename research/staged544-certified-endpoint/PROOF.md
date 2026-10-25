# Exact finite admission and conditional endpoint transfer

Let m = 73, T = 360, W = 896T, and let nᵣ be the seven positive counts in
CLAIM.json. The paid moment is

    M(b) = Σᵣ nᵣ r (73/r)^b / (73W).

Its rank mass is 65,088T. Thus M(0) < 1, and M is continuous and strictly
increasing because every paid rank is positive and below 73. The exact
interval witnesses prove M(C) < 1 < M(C + 10⁻⁶⁰). Consequently its unique
root lies between these adjacent grid points. Strict positivity of the lower
and upper margins is recorded in RESULT.json, not inferred from printed digits.

## Independently implemented dyadic enclosures

An integer interval (a,z) at scale S = 2⁵¹² means [a/S,z/S]. For nonnegative
intervals, floor(ab/S) and ceil(zw/S) bound products. Addition and multiplication
by a positive exact rational preserve enclosures under outward rounding.

For 1 ≤ y ≤ 2, put t = (y−1)/(y+1), so 0 ≤ t ≤ 1/3. The identity

    log y = 2 Σⱼ≥0 t^(2j+1)/(2j+1)

has a positive tail after N terms bounded above by

    2 t^(2N+1) / ((2N+1)(1−t²)) ≤ 9 t^(2N+1)/(4(2N+1)).

The program propagates intervals for t, t² and each odd power, rounding every
term outward. At loop exit its upper power bounds t^(2N+1); the stated tail
is rounded upward and added. Here N = 256. Exact binary range reduction
x = 2ᵏy gives log x = k log 2 + log y without a floating-point operation.

Multiplying the logarithm interval by exact b bounds each exponential argument.
For 0 ≤ x ≤ 1/2, the exponential Taylor terms are positive. After degree 96,
the first omitted upper term T bounds the whole omitted tail by 2T because
all subsequent term ratios are at most 1/2. Directed recurrence rounding
therefore encloses exp x. Every actual argument is checked in this domain.
Positive weighted addition gives the moment interval. An ambiguous sign in
bisection fails; it is never accepted by a heuristic.

The retained current-source engine uses log(r), outward decimal quantization
and alternating partial sums for exp(−b log r), with the signed r = 73 live
term. Its representation and exponential-tail argument differ from the new
positive ratio/exponential evaluator. It independently proves the new signs
without changing its precision parameters. The separate test oracle sums
exact Fractions with geometric atanh and exponential remainders and rounds
only at the logarithm/final reporting boundaries.

## Sufficient formal assembly from MathProof

The existing MathProof theorem `rational_upper_certificate` proves:
nonnegative rational coefficients cᵢ, real weights wᵢ ≤ uᵢ, and an exact
rational inequality Σ cᵢuᵢ < B imply Σ cᵢwᵢ < B. Its unchanged proof bodies
are extracted in CapCertificate.lean and specialized to cᵢ = nᵣr and
B = 73 × 896 × 360. The exact 512-bit rational certificate is checked with
ordinary `norm_num`, without `native_decide`.

The stronger analytic route uses only sufficient Taylor inequalities from
Mathlib. FORMAL-DATA.json contains outward 80-digit logarithm bounds Lᵣ,
90-digit eighth-root bounds zᵣ and 70-digit upper weights uᵣ. The sufficient
checks are

    73/r ≤ zᵣ⁸,
    zᵣ ≤ Σⱼ<60 (Lᵣ/8)^j/j!,
    Σⱼ<26 (CLᵣ)^j/j! + (CLᵣ)^26·27/(26!·26) ≤ uᵣ,
    Σᵣ nᵣr uᵣ < 73W.

All are finite rational inequalities. Positivity and Mathlib's
`Real.sum_le_exp_of_nonneg` give zᵣ ≤ exp(Lᵣ/8), hence log(73/r) ≤ Lᵣ.
Mathlib's `Real.exp_bound'` gives exp(CLᵣ) ≤ uᵣ because 0 ≤ CLᵣ ≤ 1.
Monotonicity then bounds the actual exp(C log(73/r)). The MathProof
certificate-transfer theorem proves M(C) < 1. The real-power form follows
from `Real.rpow_def_of_pos`; it does not assume any real-weight upper bound
as an unresolved hypothesis. The complete analytic route passed source compilation, the separate
target-module kernel replay and the transitive-axiom audit, with only
propext, Classical.choice and Quot.sound. The separate all-imports fresh replay
exceeded its 300-second budget and is not counted as a pass; VALIDATION.json
retains that limit.
These are standard analytic methods, not a priority claim for Taylor bounds.

## Actual finite source and unchanged physical invoice

PR #3815's exact current clock and fill are replayed with PR #3734's unchanged
owner auditor. Every helper identity, strict lower/closed upper source window,
same-call physical family, compact chronological prefix and bin capacity is
checked. The complete idle bill, zero data/helper alias count and rank mass
are rederived, with actual corrupted inputs rejected by production gates.
The exact dual checks all 2,551 patterns and the original six semantic controls.

Both current words are rechecked by the retained arbitrary-dirty interpreter:
632 live columns and 91 independent buffer columns, both orientations, reverse
pull-back and cleanup boundary. Widths and paid local frames are recomputed;
no new local interpreter or native-chain rebuild is claimed. Retained native
receipts bind these exact word hashes and canonical native-frame hashes.
Full native-cache bytes are outside this bounded check; the optional immutable
source archive is explicitly identified. Its inherited correctness/admission
premises remain conditional.

The root grid changes a proof parameter, not any instruction or coefficient.
No gate, owner, COPY, restoration, routing or physical stock charge disappears.
Physical stock remains 323,069, including 91 private buffers, and the charged
2,048-bit reserve is retained. All-size and implementation obligations do not
follow merely from a source/receipt hash.

## Fresh complete outer arithmetic

The unchanged carried-bootstrap function is extracted from its authenticated
assembly source. The same exact 47-row engine runs 12 carried stages, including
the carried-constant cutoff rule and four original controls, at the new C.
Its legacy balanced endpoint is auxiliary, not the final modern κ.

The current admitted modern checker and independent balance checker are copied
unchanged into fresh scratch space. At endpoint_digits = 60 their existing
formulas give

    r₀ = 10⁻¹⁴⁰, δ = (1025/1024)r₀,
    ε = 1−δ, β = 1−3δ,
    b = C−r₀, q = C−2r₀,
    FLOOR = 10¹⁰⁶, BACKOFF = 10⁻⁸².

The checker derives 0 < C−εq < 1/FLOOR and that C·FLOOR is integral. Therefore
floor(FLOOR·εq)/FLOOR = C−1/FLOOR, yielding

    κ = C − 10⁻¹⁰⁶ − 10⁻⁸².

The candidate is derived by the checker; it is not supplied as its comparison
point. The comparison field is the previous PR #3815 endpoint. All 63 strict
rows and 17 original rejection controls run, and the independent derivation
agrees. Exact rational subtraction proves the gain in CLAIM.json. The retained
BIT endpoint remains above C. The general mathematical/physical premises of
this outer transfer are inherited; this finite proof does not admit an
unconditional integer-multiplication theorem or change the selected frontier.
