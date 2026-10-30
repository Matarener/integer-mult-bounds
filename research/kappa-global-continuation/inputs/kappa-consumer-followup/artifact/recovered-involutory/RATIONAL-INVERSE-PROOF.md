# The rational inverse component and its equal-bill consumer

## Result

There is an exact changed local contract on both authenticated PR3734 words
which deletes all eight rank-eight centers and requires no new recursive
native phase repair:

\[
F(x,y,h)=(Jx,y+Jx,h),\qquad
B(x,y,h)=(x-y,J^{-1}y,h),\qquad J=I-KR.
\]

The independent checker verifies all 632 input columns, including 408
arbitrary helpers and the cleanup of every private buffer. The conditional
local rank mass is 5070, compared with the source mass 5134. Its exact scalar
reference is rational: the backward code introduces division by 13. The
retained Gaussian-dyadic compiler does not already include that primitive.

The literal terminal implementation with 72 full observations, each charged
one H8, spends exactly the 576 rank mass saved by nine such local calls. It
therefore gives no improvement under that invoice. A cheaper complete terminal
implementation remains unconstructed and is not ruled out by this calculation.

## Exact local algebra

The actual modern words independently give

\[
RK=14I_8,\qquad J=I-KR,\qquad JK=-13K.
\]

Consequently

\[
J^{-1}=I-\frac1{13}KR.
\]

The checker verifies both products with this inverse explicitly. Removing the
center phase and applying the paid dirty-helper compensation produces

\[
F_{\rm clean}(x,y,h)=(x,y+Jx,h),\quad
B_{\rm clean}(x,y,h)=(x-Jy,y,h).
\]

Apply J to the source after the complete forward cleanup, where every source
has native gauge FULL. Apply the inverse to Y before the backward entries,
where every Y has gauge I. These are legal common-gauge scalar actions and give
the displayed changed endpoints. Neither action reads through a port-dependent
hole. All original helper wrappers, climbs, native warps, residual adapters and
zero buffers retain their authenticated order.

For each k, the source code forms the scalar query R_k x in one owned
accumulator and scatters -K_k times that query (forward), or divides the query
by 13 before scattering (backward). Because R_i K_k=0 for i different from k,
earlier scatter operations do not change a later completed query. The reference
replay checks this identity through the complete emitted programs.

## Local invoice

The base and extra providers give the same changed local profile and bill:

| Quantity | Forward | Backward |
|---|---:|---:|
| Recursive profile | {1:2440, 2:725, 3:224, 4:102, 5:20} | Same |
| Rank mass | 5070 | 5070 |
| New rank-one native repairs | 0 | 0 |
| Retained dyadic real primitives | 173532 | 173532 |
| New complex divisions by 13 | 0 | 8 |
| New real divisions by 13 | 0 | 16 |

The dyadic bill includes inherited scalar work, the dirty-helper compensation,
and the new source code. It excludes the new division primitive and the global
consumer, routing, hosting, precision and tape/address invoice. It must not be
substituted into the supplier recurrence without those components.

## An explicit constant-divisor arithmetic contract

Binary long division by 13 has 13 remainder states. Given current remainder r
and the next input bit b, use

\[
t=2r+b,\qquad q=[t\ge13],\qquad r'=t-13q.
\]

The complete 26-transition table is emitted and checked. Every transition has
q in {0,1}, 0 <= r' < 13, and t=13q+r'. Induction on the scanned prefix proves
the usual prefix = 13 quotient + remainder invariant. Signed division scans
the absolute value and restores the sign. A fixed number of appended zero bits
provides fixed guard precision. The algorithm takes one finite-state transition
per input bit, hence O(p) work on a p-bit value with fixed guard lengths. The
checker also validates 73 integer fixtures through 2048 bits.

This supplies an algorithm and a local complexity bound. It is not yet a
certificate integrating a new pointwise primitive into the project's retained
multitape compiler. In particular, the exact rational interpreter is labelled
as a reference; it does not bill 1/13 as a dyadic SCALE.

## Incremental rounding and overflow

All bounds in this paragraph use the per-real-component sup norm. Let each
query division have additive error e_k, with |e_k| < delta, and suppose the
surrounding dyadic query and scatter operations are exact for this incremental
calculation. The source error after the backward source code is -Ke. The target
error after its clean core is JKe=-13Ke. The actual matrices have

\[
\|K\|_\infty=1,\quad \|R\|_\infty=56,\quad
\|J\|_\infty=26,\quad \|J^{-1}\|_\infty=38/13.
\]

Thus the new source error is smaller than delta and the new target error is
smaller than 13 delta. Taking delta=2^(-p-4) makes the target contribution less
than (13/16)2^(-p) and the source contribution less than (1/16)2^(-p).

The checker also propagates independent symbolic division errors through every
serial query prefix. For input component radius B, each accumulator prefix is
bounded by 56 B + (9/2) delta; each source prefix by (77/26) B + delta. Completed
queries contain no previous division error. Six integer guard bits suffice for
the accumulator when B >= delta. These claims concern the new source block;
the inherited core's larger scalar prefix is checked separately against its
retained 192-bit scalar/free-monomial cap.

Other rounding, recursive native error, and amplification through the global
controller must be added to a complete precision recurrence. Four new
fractional bits are sufficient for this isolated division contribution, not a
claim that four bits settle the whole supplier error analysis.

## Complete consumer screen

Nine changed local calls delete 9*8=72 H8 centers, of rank mass 576. A literal
72-query terminal implementation charged H8 per full query also costs 576.
Under that particular tariff the recursive saving is zero before any added
scalar, division, storage, routing or precision costs. The baseline's complete
invoice therefore cannot improve through this implementation alone.

The reviewed 69.75-field lower bound on the earlier involution is not asserted
as a universal lower bound on this rational contract, nor is the literal
72-query implementation asserted to be optimal. Endpoint scalar placement in
the paid FULL gauge closes a local source operation; it does not itself pay
for the separately routed terminal observations. A proposed improvement must
construct and verify a complete terminal operator costing strictly less than
the 72-H8 allowance and include the arithmetic and precision contracts above.

## Reproduction and provenance

Run `python -B recovered-involutory/rational_inverse_component.py` from the
conversation workspace. It prints `PASS_RATIONAL_LOCAL_COMPONENT` for base and
extra. Programs, the complete division transition table, norm bounds and bills
are emitted under `rational-inverse-results/`.

The checker imports the independently constructed modern clean core from
`modern_native_component.py` and authenticates the PR3734 native receipt and
both source words. Source pins and reconstruction details are recorded in
`LOCAL-NATIVE-PROOF.md`. This is new research following the attached survey;
it is not a recovered historical script or a full supplier certificate.

Substantial OpenAI Codex assistance under the user's direction. Apache-2.0.
