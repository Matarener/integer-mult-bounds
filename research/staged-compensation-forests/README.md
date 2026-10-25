# Restored compensation forests for the staged 644/660 words

This finite construction replaces the frame-zero compensation in the two
PR3605 words. It reduces **5,736 additions to 2,288**, including preparation
and restoration of both the target and helper bases. Under the stated
cleared-work binary-Horner price, the saving is **41,162 real-component
primitives per orientation**. Every arbitrary target and helper input is
included.

| Compensation on the same source matrix | Additions | Primitives per real component |
| --- | ---: | ---: |
| Original PR3605 | 5,736 | 31,214 |
| Earlier unpublished rank-basis construction | 3,214 | 17,334 |
| Signed-unit target forest | 2,834 | 13,716 |
| Target forest with disjoint helper pairs | 2,288 | 10,633 |

The target forest has 17 roots and 95 signed edges. Its fully paid cost is
minimal within the single-parent signed-unit target-forest class on this
matrix. The second step selects 88 disjoint helper pairs from one fully
specified sorted greedy pass. **The two-sided circuit has no claimed global
or matching optimality.** The 1,922 remaining injections, 95 target preparations,
88 helper preparations, and both sets of restorations are all charged.

The construction uses established forest and two-sided basis methods. Its
contribution is the explicit circuit for these exact staged words, the
comparison with the superseded unpublished circuit, and the accompanying
source-bound checks. [RELATED-WORK.md](RELATED-WORK.md) separates the input
matrices and prior recipes.

## Exact interface

Let `y` be the 112 arbitrary targets and `h` the arbitrary helper coordinates
at the compensation boundary. The source response is `(y,h) -> (y+C h,h)`.
Prepare the signed target forest `T` deepest-first, prepare the disjoint helper
shears `H`, inject `T C H^-1`, restore `H`, and restore `T`. The endpoint is
exactly the original response over the dyadic rationals. The helpers are
temporarily changed and then restored.

All 207 active helper columns have the required zero-frame entrance and FULL
terminal frame in the pinned word. No removed register, private zero buffer,
wrapped entrance or early-ended helper is used as a new donor. Only the
compensation field changes. Sources, centers, warps, helper roles, ordered
widths, cleanup and the paid recursive profile are retained.

The literal inverse reverses and negates the additions. The same-chronology
inverse transpose swaps source and target and negates each coefficient. Its
compensation endpoint changes helpers by `-C^T y`; unchanged-helper language
applies to the forward boundary.

## Complete scalar comparison

The independent logical-word replay retains ordered formal warp letters and
checks 632 arbitrary live inputs and 91 initially zero private buffers in
both orientations and their literal reverse inverses. A separate replay lowers
both emitted programs to scalar primitives. In that projection, nonscalar
events act as identity and CLEAR is a zero assignment. The original transport
and emitter produce these streams; they are not counted as a second
independent mathematical implementation.

| Complete scalar-program quantity, per provider | Original | New |
| --- | ---: | ---: |
| Forward primitives per real component | 79,072 | 58,491 |
| Backward primitives per real component | 79,096 | 58,515 |
| Forward maximum exact coefficient row sum | 302 | 302 |
| Backward maximum exact coefficient row sum | 169 | 181 |
| Forward positive-envelope bits | 89 | 89 |
| Backward positive-envelope bits | 95 | 97 |

Both conservative positive envelopes increase; the forward bit ceiling stays
at 89, while the backward ceiling rises to 97. The backward exact row sum also
increases. The earlier supplier's precision allowance is not reused. Exact prefix denominator
depths remain 4 forward and 5 backward. These are finite scalar/free-warp
calculations, not native phase or rounding certificates.

## Reproduce

With CPython 3.12 and its standard library, from the repository root:

```sh
python3 -I -B scripts/research_package.py --package research/staged-compensation-forests
```

The registered commands authenticate the frozen inputs, regenerate the circuit
and its complete records, check the independent mathematical receipts, and
exercise acceptance controls. Generated output goes to temporary directories.
The package also works from a Git-free source export. The source transport and
emitter run with their assertions enabled.

## Scope and limits

The recursive profile remains
`{1:2439,2:726,3:224,4:102,5:20,8:8}`. The 408 helper roles, 91 private cleanup
buffers and ordered helper-width inventory are unchanged. Consequently this
scalar substitution gives **no improved recursive moment or kappa**.

All coefficient work uses the declared component price
`p(a/2^d)=3+floor(log2|a|)+popcount(|a|)+d` for reduced nonzero dyadics,
with `p(0)=0`. This is a specified finite lowering model, not a measured runtime
claim. Scalar projection checks do not establish native phases, physical
strict-zero erasures, rounded cleanup, hosted owner allocations or an all-size
supplier. No existing whole-supplier precision allowance is admitted by this
package.

The historical C01 factory and cold-tail screens are retained as provenance
in [the original note](frozen/history/C01-PROOF.md). They are not rerun or
promoted to new claims here.

## Open next questions

1. Can this exact compensation be admitted into a complete hosted native
   supplier with its actual rounding, source-access and physical cleanup
   costs? Start from the frozen two-sided words and regenerate that full
   invoice and precision argument.
2. Can a different local contract improve the paid recursive profile?
   Further scalar savings alone do not resolve that obligation. A new claim
   must name the changed frame or child call and include all restoration.

## Sources and credit

PR3605 is pinned at `3efbb5de06a49ffeea6684482f2d3fe48cdca3fb`.
Its PR3133 word lineage, Jeremy Kothe's routing/preload work, Yiyang Lu's
compensation work and the retained native implementation notices remain
credited in [NOTICE.md](NOTICE.md). Forest and two-sided predecessors are
credited separately in [RELATED-WORK.md](RELATED-WORK.md).

Prepared by Ross Richardson with substantial OpenAI Codex assistance in
construction, mathematical checking, verification and publication. Separate
AI contexts are not independent human review or formal-kernel evidence.
Apache-2.0.
