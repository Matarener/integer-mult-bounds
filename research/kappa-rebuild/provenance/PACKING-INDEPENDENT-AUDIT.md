# Independent audit: productive helper packing and paired query swaps

**Outcome: the conditional packing and recursive invoices pass. Native
admission remains open.** This audit read the three stable source/receipt
pairs without importing their construction routines. It independently
recounted the improved p=1 and p=2 inventories and rank bills, reviewed the
rational interval proof, and checked all twelve reported invoices with
110-digit Decimal evaluation. Every independent value lies inside its
reported outward interval. No predecessor native source was reconstructed.

## Improved p=2: 213 added productive fields

There are448 main fields and213 new productive helper fields, for661
productive fields of ambient rank41. At each of the four outside stages the
original idle bins supply

`90×9, 44×8, 56×7, 18×6, 16×5`.

The new fields independently supply

`123×9, 49×8, 12×5`.

Their sum is exactly the required per-call inventory
`213×9, 93×8, 56×7, 18×6, 28×5`. At the middle stage, original fields supply
all195 roles of widths5 through8, and new fields supply all213 width9 roles.

The48 new hosts with outside pattern `(9,9,9,5)` and middle9 use all41 ranks.
The116 with outside pattern `(9,9,9,0)` use36 and leave5. The49 with outside
pattern `(8,8,8,8)` use41. The original two-stage bins leave
`72H1+64H2`; their middle-stage bins leave `56H1+18H2+28H3+29H8`.
Thus the complete remainder is exactly

\[
128H_1+82H_2+28H_3+116H_5+29H_8.
\]

Its rank mass is1188. Five pruned THREE calls have rank mass25465, so

\[
661\cdot41-(25465+1188)=448.
\]

The40 rank-one children of the five H completions are then explicitly
subtracted. With `H_r=r^(1-C)`, the remaining allowances are:

| C | Remaining allowance after H completions |
|---:|---:|
|0.001745|257.8060663457233916759|
|0.004|65.3169531797331110453|

The213-host minimum is valid **for the stated middle window**:213 simultaneous
width9 roles cannot fit in any of its rank8 original idle bins, and a field
cannot serve two simultaneous native helper roles. This is not a global
minimum over changed schedules, interfaces, or split roles. The earlier219
bound held the old original-bin allocation fixed; changing that allocation
does not contradict it.

## Improved p=1: concentrated residual

The six independently checked cyclic patterns have counts
`18,1,28,54,168,139`, totaling408 fields per controller. Across three replicas,
each stage has precisely three times the required helper inventory. Their
remainder is

\[
54H_1+28H_2+H_7+18H_{10},
\]

of rank mass297. All residual children are strictly smaller than the ambient
rank25. The rank identity is `632×25−3×5093−297=224`. After the24 rank-one H
completion children, the allowances are125.5333563352732444235 at C=0.001745
and29.9957695582853966376 at C=0.004. This pattern is an exact feasible
construction in the width model; the MILP discovery is not promoted to a
rational optimality proof.

## Interval verification

The source uses the positive series
`log(x)=2 sum z^(2j+1)/(2j+1)`, with `z=(x−1)/(x+1)`. Its displayed geometric
tail bounds the omitted terms. Range reduction keeps z at most1/3. The
positive exponential series uses an upper geometric ratio for its remaining
terms; the largest exponent used here is below1. Reciprocal interval
directions, subtraction of positive cost coefficients, and45-place outward
rounding are correct. Independent Decimal evaluation is an additional
numerical backstop, not the source of the exact interval claim.

## Why the whole-block helper lemma is sufficient, and what it assumes

If a fully checked physical word is
`diag(DataOp,T1,...,T408)`, multiplying it on the input and output by block
diagonal operators acting only on individual helper registers leaves
`DataOp` and every zero data/helper cross block unchanged. Therefore free
monomial normal forms of the complete `T_i` can replace canonical helper
entrances with ordinary productive Fourier jobs without changing internal
ADDs. The371-rank synchronous-entrance objection does not apply to this
whole-block construction.

This conclusion requires the following actual native facts:

- Arbitrary-input restoration must make every physical helper block diagonal,
  including zero helper-to-helper cross terms.
- Each actual relative transform must have the claimed Fourier rank, with
  **allowed free monomial** input/output factors and correct absolute phase.
  An arbitrary Clifford factorization is insufficient. Backward conjugate
  conventions must be checked explicitly.
- Successive normalized jobs on one field must act on disjoint unfinished
  axes. Original host windows must correspond to actual named registers
  disjoint from that call's active main ports. The packing checks nominal
  capacities and stage assignments; it does not emit this physical owner
  schedule.
- Every credited productive field must finally compute a complete rank25 or
  rank41 Fourier transform of its own arbitrary original input. A cache
  containing another source function does not automatically earn that credit.
- The main-data controller still needs complete endpoint closure. Its credit
  is conditional in these invoices. The inherited H owned C0 is an additional
  reusable, uncredited scratch resource; no full Fourier job is credited to
  it. Any outer simultaneous-storage requirement must allow that resource.
- Boundary scalar work, coefficient growth and precision obligations must be
  integrated before an asymptotic admission. The reported leading allowance
  does not itself perform those checks.

No hidden additional recursive-rank debit was found **under these stated
premises**. The complete historical identity supplier remains over budget in
the reported favorable screens, so helper packing alone does not close the
research objective.

## Same-future-query paired swaps

The paired-swap identity is valid over a noncommuting operator ring. Let
`Q E=I`, `T=I−E Q`, and

\[
S(Y,P)=(TY+EP,QY).
\]

Then `T²=T`, `TE=0`, `QT=0`, so `S²=I`. An intervening backward shear that
changes X but preserves Y and P does not prevent the second exchange from
restoring the bank. For arbitrary H0,H1,H2 the full equations are

\[
Y_0=Y+H_0X,\quad Y_1=TY_0+Ed,\quad X_1=X-H_1Y_1,
\]

followed by `Y2=Y0, P=d` and terminal outputs
`Xout=Y0+H2 X1, Yout=−X1`. This is not an identity main-data endpoint.

Choosing the same future Q at both pre-Y contacts is a useful changed premise,
but cheap evaluation of Q **does not imply** a cheap right inverse E. A right
inverse can require non-dyadic coefficients, unavailable frame changes, or
expensive scattering. The two physical bank transports must also intertwine
the chosen Q and E; equality of untransported symbolic labels is insufficient.

There is a concrete candidate for the frozen selected-port query. If the
recovered physical formula is `Q_t=(R_A^T R/4) D_t` and
`R_A^T R_A=4I`, its selected-column restriction is `diag(D_t,a)`. Then
`E_t=P_A diag(D_t,a^-1)`, where `P_A` injects into the eight selected ports,
is an explicit right inverse. It is a cheap candidate only if those inverse
owner maps are allowed monomials preserving both contact frames, with the
required phases. This is the next finite native test, not an admitted free
scatter.

## Audited source pins

| File | SHA256 |
|---|---|
|productive_helper_forest.py|fc8ce7bd7ec4803d2cff816af54feee9ebb5198afe6e58bd33f8f85fde1014f4|
|productive_helper_refinement.py|d70e2feb935f93e9c9ce30340ce099dbefdc3ffe9ef54b3b338333efe815df71|
|productive_helper_p1_refinement.py|2982ef4fab8e7844a460579640ad13bf9eb0381b0e7b66fb805c21f73cea1b8d|
|PRODUCTIVE-HELPER-FOREST.json|63a4197062a6ea4a96555b4136210efc716317c1251d88c40a47a22b9926b89d|
|PRODUCTIVE-HELPER-REFINEMENT.json|8ae18b7b972d216a31dba54514925ee244824323eba452049b02ebce746b53d1|
|PRODUCTIVE-HELPER-P1-REFINEMENT.json|3437b3179af26bdde44278bfeb07247735eed3c6c7b8e2a2275057caf7ad4dbc|

No new kappa is established by this audit.
