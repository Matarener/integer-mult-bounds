# Late FULL delivery removes the eight private descents

## Contract and changed premise

The object is the exact 4,058-event witness frozen in the main-branch native
P104 package, followed by the actual PR3882 correction builder at scientific
head `9d56eeedbed5e3e9bbbc8c189d66f14cf15b6067` (publication
`d76586303e7036baa74f8deb2155038290174ffd`). Inputs are 104 source rows,
104 target rows, and 72 independent arbitrary dirty Q/G/D rows. Coefficients
are dyadic; no query or delivery helper is initialized to zero.

PR3965 establishes that deleting the eight copy intervals with their original
consumers unchanged is wrong, and that replacing each private descent by a
same-query descent/return pays another56. Here we change the consumers and
cleanup jointly. We retain every public native transport and the original
Q producers, initial compensations, and Q source cleanup. We replace the
32 early copy deliveries **and** their32 paired D cleanup reads by416 late
FULL reads. The104 target lifts already present in PR3882 are retimed, once.
This is a different chronological contract, not a counterexample to3965's
fixed-consumer result or the earlier fixed-boundary COPY56 results.

## Actual cones and causal identity

For each query j the verifier extracts the literal interval
`zero C; copy C,Qj; transport C; Dk += C ...; erase C`, its D consumers,
their later Y reads, and their FULL cleanup `Dk -= Qj`.
The eight query records in RESULT.json contain every original zero-based
index, all416 real Y reads, all32 cleanup indices, and all query source
coefficients. Each query at copy time is exactly

    q_j = h_j + a_j^t x,

with coefficient1 on its own arbitrary dirty input h_j and no other dirty
input. The actual producer a_j is extracted from the whole word; it is not
postulated. It stays untouched, apart from native frame changes, until cut
3641. Each Y response u_ij is the sum of actual post-injection reads of
that query's D helpers. There are52 nonzero u_ij per query, all ±1/4.

Each D helper's initial dirty contribution to Y already has its compensating
initial read. Removing both its q_j injection and its final subtraction
therefore restores its original dirty row while omitting exactly u_ij q_j
from each Y row. The inherited initial Q/Y compensation remains. Adding
u_ij q_j directly at FULL restores the exact old Y row, including cancellation
of h_j; the existing subsequent Q source cleanup restores q_j to h_j.
No dirty erasure, missing copy owner, or changed source preparation occurs.

This identity is verified on all280 independent input columns by exact
Fraction arithmetic. It preserves every final row, including the residual
encoding, rather than only the104 sum outputs. For a bounded pilot, just
Q0's five D helpers and52 reads give combined mass2569 and exact equivalence;
the same verified extraction extends to all8 queries.

## Chronology and native physical operators

Delete the eight complete C intervals and32 D/Q cleanup additions. Retain
all other witness events. Immediately after original event3641, lift every
Y from its literal final hyperplane to FULL. All104 X and72 Q/G/D are already
FULL, all Y have finished their terminal transports, and the remaining416
original events are only Q/X source-cleanup additions at FULL. For each Qj:
halve twice, perform its52 signed unit Y additions, then double twice.
Thus the donor is restored before any Q cleanup. Complete the old Q cleanup.
Finally execute the old PR3882 tail with its104 initial lifts removed.

The physical row invariant is the native package's
`physical_r = Gamma_(frame_r) * logical_row_r`. The retained public native
subsequence is checked literally equal to the inherited sequence. The only
removed positive children are the eight private rank7 descents. The104
inserted lifts are implemented in LIFT-RECIPES.json, each as actual Gaussian
monomials around one rank1 positive child, not admitted by a rank count.
Their old frame is bound to the **exact ordered canonical basis** in the
certificate for the corresponding last Y transport; equality of spans alone
would not fix its chart operator. Their target is the same F9 used by Q/X.
The independent native interpreter checks signed Pauli actions and exact
phase for all104 complete operators. These determine the full Clifford;
512 Gaussian columns are also compared for the first lift. A changed global
phase rejects. No new direct read is allowed outside the common FULL chart.

The remaining historical native operators and endpoint adapters are inherited
from PR1991. We do not claim a fresh replay of that entire native certificate.
The raw changed module now has104 source and target FULL endpoints,72 restored
dirty FULL helpers, and no private allocation or discard. It implements the
same Gram row map. Its monotone boundary progress and native mass are both
2416 (=2312+104). This changed raw boundary is not the old partially transformed
channel boundary. It does not by itself implement I or admit a global supplier.

The saving is also available to the source-preserving PR3894 continuation
(head `13b397e36d43f2a91b9e6d42b3ca67f0ec50cea7`). Its104 Y lifts can be
grouped first, since each target's later correction reads only unchanged X
rows and its lowering touches only that target. Our raw FULL endpoint equals
the original raw channel followed by those grouped lifts on all280 columns.
Thus its remaining4,992 target additions and104 target returns compose with
the identical input interface, giving the same2576→2520 native saving without
consuming X. This is a compositional transfer using PR3894's stated schedule;
we do not claim a fresh replay of its frozen correction here. In particular,
56 saved native mass is not an advantage exclusive to role exchange.

The final104 drops/role-exchange interface of PR3882 retains that predecessor's
physical/global admission qualifications. This package establishes exact
normalized endpoint equality and a new native implementation of the retimed
prefix; it does not fill the unproved all-size or global-owner implications.

## Complete local accounting and conditional caller gate

| Item | Original channel +3882 tail | Changed module +remaining tail |
|---|---:|---:|
| Native channel rank mass |2368|2312|
| Y lifts |104|104|
| Final drops |104|104|
| Total positive-child mass |2576|2520|
| Private zero/copy/erase |8 each|0|
| Raw channel weighted ADDs |2624|2976|
| Explicit new half/double |0|16 each|

Original channel profile is
`{1:1074,2:58,3:86,4:104,5:48,6:24,7:8,8:8}`.
Changed raw module including lifts is
`{1:1178,2:58,3:86,4:104,5:48,6:24,8:8}` (mass2416).
Add104 rank1 final drops to obtain combined mass2520. The correction's
remaining1248 unit ADDs and104 each half/double are unchanged.

For a reproducible complete scalar tariff, lower each old coefficient p/2^s
separately as s donor halves, |p| signed unit ADDs, s donor doubles. This is a
valid deliberately unoptimized implementation, not a scalar lower bound.
Old channel:3872 unit ADDs and2496 each half/double. New module:4224 unit ADDs
and2512 each half/double. Including the unchanged tail gives5472 unit ADDs
and2616 each half/double, versus5120 and2600. There are no unpriced nonunit
coefficients in the new416 deliveries. All old widths/precision obligations
remain; rank mass does not erase this finite scalar overhead.

Under precisely PR3954's optimistic two-axis hosting/coverage assumptions,
there are208 calls and10816 anchors. Corrected local endpoint progress remains
2312. The old complete excess44096 decreases by208*56=11648 to32448:

    208*(2520-2312) - 10816 = 32448 > 0.

The complete bill is2997696 over denominator2965248. Its zero-exponent moment
is therefore greater than1; with all widths at most81, the same monotonicity
argument excludes the retained favorable gate throughout 0<=a<1. No further
construction round follows from this gate. The raw all-FULL module's changed
progress2416 requires a new caller/entrance/coverage invoice; substituting
2416 into the old formula would silently change the contract. We make no
such global claim and do not change the selected frontier.

## Verification and remaining work

Four semantic controls remove delivery, move delivery after Q cleanup, omit
one real target, or fail to restore the quartered dirty donor. Each fails
exact row equality. Separate optimized CLI processes reject Boolean/float
receipt types, duplicate keys, false savings, changed/missing source bytes,
and changed frozen tail bytes, after first validating each private fixture.
All checks use exceptions, not optimization-removable assertions.

Next genuinely different questions are an actual caller for the new all-FULL
Gram boundary and a complete jointly redesigned correction with owner/coverage
and all-size accounting. Combining this change with PR3943's earlier tail and
compressed Q cleanup requires a new chronology proof; the scalar savings from
that PR are not credited here. No universal copy or native-rank lower bound,
new source-preserving cost optimum, or improved kappa is claimed.
