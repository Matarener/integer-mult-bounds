# Coupled contacts and complete conditional price

The endpoint is `kappa = 304153/100000000 = .00304153`, improving Ali
Romman's PR5545 endpoint `.00304117` by `9/25000000 = .00000036`.
Source head: `18968423711fd902aaee1099979497d55603e1dc`.
The selected record is unchanged. All five framework premises remain:
native all-column implementation, owned erasure, uniform compiler,
precision and tape costs, and analytic recovery. This proves an ideal
operator change and a complete conditional price; the enormous uniform
word and rounded integer multiplier are not materialized.

## Literal change and all-width implication

`construct.py` pins these six zero-based source events:

| Event | Unchanged scalar operation | Old frame | New frame |
| --- | --- | --- | --- |
| 10461 | `297 += 303` | 335 | 17 |
| 10462 | `303 -= 297/2` | 335 | 17 |
| 13970 | `152 -= 297/2` | 335 | 17 |
| 15479 | `198 += 319` | 915 | 207 |
| 15639 | `205 += 198` | 915 | 207 |
| 15640 | `198 -= 205/2` | 915 | 207 |

Frame 335 has dimension two. Frame 17 is `span(145)`, dimension one.
Frame 915 has dimension seven. Frame 207 has dimension eight and basis
`[2,5,8,17,33,65,129,257]`. All are existing source canonical charts.
No new coordinate transformation is granted for free.

The emitter issues every nested MOVE needed to place both operands at
the declared common frame. SCALE occurs at its operand's current frame;
terminal public MOVEs finish at the original exits. Fifteen SCALE chart
annotations change; every scalar coefficient and its order is retained.
INIT/COPY/CLEAR lifetimes are unchanged. Every actual intervening source
read and write is included in the complete replay. The word has 25,310 events.

The separate [peer proof](peer/PROOF.md) and
[role histories](peer/RECEIPT.json) bind the actual field versions. In the
first group, role 297 coalesces two rank-one rises into rank two; role 303
splits rank two into two rank-one rises; role 152 replaces two rank-two
rises by ranks one and three. Their net delta is `H1 - 2H2 + H3`.
In the second group, role 198 replaces ranks four plus one by rank five;
role 319 exchanges the order of ranks one and two with zero profile delta;
role 205 splits rank two into two rank-one rises. The net delta is
`H1 - H2 - H4 + H5`.

Let Phi_F be the exact canonical source chart. At field width f, a role
stores Phi_F tensor-power f applied to its logical value. A MOVE F to G
applies `Phi_G Phi_F^{-1}` tensor-power f, preserving that logical value.
Same-chart ADD/COPY acts on logical values with its scalar applied once,
outside tensor powers. SCALE commutes with transport by linearity. Thus
the unchanged scalar/owned word and fixed endpoint charts imply exactly
the same complete physical operator at every positive f. This is a
compositional induction: no sum is tensor-powered and no width-one
linear-independence claim is used.

Three exact endpoint checks cover all 743 rows and 552,049 coefficients:
sparse rational forward rows, dense integer reverse columns with binary
denominators, and an independently written integer/dyadic peer interpreter
that imports neither constructor nor native checker. All 735 public inputs
remain arbitrary. All 527 productive helpers retain their targets. Eight
owned lifetimes retain peak occupancy one and the original erasure premise.

The source native compiler freshly lowers every MOVE, helper boundary and
main adapter. Its separate Gaussian interpreter compares every signed Pauli
image and absolute global phase: 2,979 distinct maps, 1,054 helper normalizers
and 208 main adapters. Wrong phase is rejected. These exact base identities
tensor to every positive f. The unchanged complete caller is freshly checked
through its Laurent identity, 265-axis phase polynomial, 104 ports, both
orientations and actual orthogonal routes. This algebraic check is distinct
from materializing exponential-size all-column matrices.

The added independent dense audit checks all 512 columns of each of the
four new MOVE maps: `17 -> 720` (rank 2), `17 -> 782` (rank 3),
`615 -> 207` (rank 5), and `775 -> 207` (rank 2). It compares
1,048,576 exact complex entries, including
absolute phase, column norm and support. The unchanged credited PR5548
arithmetic engine executes the literal source charts and lowered recipes;
the source/vendor tableau is not used for matrix equality. Phase-only
faults invisible to signed Pauli images are rejected. The exact base
equalities tensor factorwise, with phase i^theta lifted as i^(f theta).
This checks the new map interfaces only, and retains the old native and
uniform implementation premises.

## Complete moment and transfer

The new local paid profile is

```text
{1:2430, 2:554, 3:390, 4:111, 5:108, 6:17, 7:13, 9:1}.
```

Its delta from PR5545 is

```text
local:     +2H1 -3H2 +H3 -H4 +H5
complete: +36H1 -54H2 +18H3 -18H4 +18H5
target:    zero at every rank.
```

For `H_r=r^t`, `0<t<1`, strict concavity gives
`H3-H2 < H2-H1` and `H5-H4 < H2-H1`. Summing shows the paid delta is
strictly negative throughout this interval. Call count and rank mass are
unchanged. This is different from repeating PR5545's `H1+H5 -> H6` edit
and lies outside PR5548's narrow repetition ceiling.

Each invocation retains helper targets `{4:51,5:36,7:24,8:122,9:294}`.
The full bill includes 18 forward invocations, 15 genuine queries, 15 whole
idles and 32 main banks: 69,912 paid calls, 12,814 productive fields and rank
surplus 760. Maximum paid/target ranks remain 72/145. No helper is omitted.

`pricing.py` retains PR5544/5545's funding argument. New mathematical
parameters are claimed/tested saving and comparison endpoint; its input
histogram comes from the freshly replayed word. Two independent full
invoice counts and both inherited rational moment engines must agree.
The strict raw crossing enclosure is

```text
.00304153116714 < raw crossing < .00304153116715.
```

The separate funding peer implements a third rational interval engine:
50-term atanh logarithms with rigorous tails and 128-bit outward grids,
followed by alternating exponential bounds of degrees 15/14. It imports
neither retained moment engine. Its four sign enclosures and full invoice
recount agree. The wrapper binds the audited word, source and complete
receipt to this publication.

Tested saving is `.0030415305`. Cutoff 17, floor 18, tail offset 1/5,
power 1024, reserve `10^-10` and logarithm power 1000 fund completion,
splitting and rounding. Compiler gap is `1/14000000000`, integer height
`H=690116000000000`, test exponent 49,294; the preceding integer point
fails. Ordinary/admitted BIT stock checks and all 54 strict plus four
functional outer predicates pass. `RESULT.json` records exact rationals.
The endpoint gain is not claimed to equal the raw-crossing difference,
which has different safety margins. No global optimum is claimed.

Scalar coefficients and counts are unchanged. The 26,000-event bound,
per-event scalar growth below `2^16`, total local Gaussian rank 5,894 and
owned peak one still bound reordered prefixes. Local native ranks stay
at most nine. Routing, normalization, COPY, caller and erasure allowances
are recomputed; no precision/tape cost is set to zero. The same five
framework premises remain necessary.

## Controls, source retention and credit

The verifier rejects an old-chart contact, wrong butterfly coefficient,
changed source event and uncharged recursive call. The peer also rejects
missing owned CLEAR. Inherited checks reject missing central translation,
wrong native phase, adverse completion cutoff and inadequate BIT saving.
All 33 dependency files are authenticated before imports. The closed
official export retains the exact PR5545 bytes and source attribution.

Prepared for thu-nmrc with substantial OpenAI Codex assistance, Apache-2.0.
These are author-side checks, not independent human/proof-kernel acceptance.
Credit Ali Romman for PR5544/5545's caller and price; Gareth Davidson for
PR2305; David Arias for PR2152; Cinna Davis for PR2219/controller; Jacob
Alan Sussman for productive recursion; zxv for compiler/outer machinery;
Cao Yifan for pricing; and all geometry, common-chart, dual-ADD, native,
COPY, precision and analytic predecessors in the retained proofs. The
new contribution is this coupled literal itinerary and conditional gain.
