# No cheaper direct cycle on the PR3359 map

## Statement and fixed boundary

Fix PR3359 at `3bdc260e996fd3a94dcb7560b68f2c61d2253d80`, with complete owner
payload SHA256 `31d39e4d91f92cf174f8cccfbbb33d742d9872462b37456bed775072ce111764`.
Consider a permutation of selected original whole helpers between occupied bins,
with exactly one original helper leaving and exactly one arriving at each
selected bin. Keep each helper's original call and width, the 144-call order,
and all other assignments fixed. Every arrival must be inside its destination's
actual source-event window and fit its capacity after the departure.

For every concave function on the integer ranks `0,...,48`, this permutation
cannot reduce the sum over the affected bins, including rank-zero bins.
For the usual idle-child cost, the rank-zero value is zero.
In particular, no direct four-helper
rotation across four distinct bins can lower the recursive moment for any
`0<a<1`, whose idle child cost is `r^(1-a)` and whose rank-zero cost is zero.
This is an exact finite-certificate theorem, followed by an elementary analytic
argument. It is not a formal-kernel proof or a multiplication theorem.

We prove the statement in a favorable relaxation that drops family occupancy,
active-pair restrictions and all remaining physical admission conditions. Thus
repeated physical families and same-call interactions do not escape this
particular obstruction. Multiple original departures or arrivals at one bin
are outside the theorem.

## Complete source reconstruction

The verifier applies the authenticated 217-row checked-preimage delta to the
canonical PR2169 owner file. It checks the complete reconstructed canonical
payload against the retained PR3359 `RESULT.json` and `SOURCE-EXPORT.json`.
The independent Josie Elliston auditor checks all 69,120 roles, original widths,
144 calls, physical families, prefix slices, 288 source-event windows and the
complete idle profile. It rebuilds the windows from the source chronology and
compares them with PLAN. Rank mass is 1,041,408 and deficit is 5,120.

These are checks of the starting owner map. We neither propose a changed
supplier nor rerun the complete eleven-stage admission for this negative result.
All seven canonical runtime inputs are byte-pinned before importing the auditor.
No pending PR commit object is needed in a cold checkout.

## A graph that contains every allowed direct permutation

For original helper `j`, write its call as `t_j`, width as `w_j`, bin as `b_j`,
and that bin's original free capacity as `f_j`. The five widths are
`{4,5,7,8,9}`. A vertex is `(t,w)` for one of the 144 calls and one of these
widths. There are 720 vertices.

For every original helper `j`, every incoming call `t` strictly inside `b_j`'s
reconstructed event window, and every incoming width `w`, include the edge

`(t,w) -> (t_j,w_j)`

when `f_j+w_j-w >= 0`. Its destination-bin residual would become
`f_j+w_j-w`. The upper capacity bound follows because the original outgoing
helper occupies `w_j` cells and the incoming width is positive. The graph
allows same-bin moves and ignores family conflicts, so it is a supergraph
of the actual allowed moves.

A permutation of one helper per selected bin decomposes into cycles of the
selected helpers. Its sequence of call/width states is a closed walk in this
graph, even when states repeat. The edge from helper `i` to helper `j` charges
exactly the residual change at `b_j`. Thus every bin in such a cycle is
charged once.

## Exact compression and potential inequalities

For `k=1,...,47`, define the convex hinge `h_k(r)=max(r-k,0)`. An edge with
width difference `delta=w_j-w` has hinge gain

`h_k(f_j+delta)-h_k(f_j)`.

For fixed endpoints, `delta` is fixed. If `delta>0`, this gain is nondecreasing
in `f_j`. If `delta<0`, it is nonincreasing in `f_j`. This follows by summing
first differences of a convex integer sequence. For `delta=0` it is zero.
Consequently the largest gain for every hinge is attained at the same extreme
residual: the largest feasible `f_j` when `delta>0`, the smallest when
`delta<0`, and any when `delta=0`.

The verifier enumerates every original helper, allowed incoming call and width,
then keeps precisely that extreme for each pair of vertices. The resulting
197,545 edges preserve an upper bound for every omitted parallel edge,
simultaneously for every hinge. The independent synthetic control compares this
compression with all uncompressed hinge maxima, including both signs of delta.

`POTENTIALS.json` supplies integer vertex values `p_k`, all between 0 and 5.
The verifier checks all 47 x 197,545 = 9,284,615 inequalities

`h_k(f_j+delta)-h_k(f_j) <= p_k(t_j,w_j)-p_k(t,w)`.

All hold using integer arithmetic. Summing along any closed walk telescopes
the potentials to zero. Hence the total change in each convex hinge sum is
nonpositive, for cycles of every length. The verification does not use a
floating tolerance, a search cutoff, or a claim that no candidate was found.

## From hinges to every concave rank cost

Let `phi` be concave on the integer ranks `0,...,48`. Put

`c_k = 2*phi(k)-phi(k-1)-phi(k+1) >= 0`, for `k=1,...,47`.

The finite identity

`phi(r) = phi(0)+r*(phi(1)-phi(0))-sum_k c_k*h_k(r)`

holds for every integer `0<=r<=48`, by comparing successive first differences.
A direct permutation leaves the number of affected bins and their total idle
rank unchanged. Its constant and linear contributions therefore cancel.
Every hinge sum has nonpositive change, so its total cost change is
`-sum_k c_k*Delta(sum h_k) >= 0`. This proves the claim.

For `phi(r)=r^(1-a)` and `0<a<1`, concavity gives the same conclusion. The paid
local children and every fixed additional charge are unchanged in the stated
model. This direct permutation cannot supply a better moment, and hence cannot
supply a better exponent through that unchanged invoice. This conclusion does
not certify the invoice, either supplier, or their inherited assumptions.

## A real control outside the boundary

[PR3366](https://github.com/CrocSwap/integer-mult-bounds/pull/3366), commit
`3f59a00257b3e29ad54e349f826d5ffdc59f7cfb`, supplies a neutral transposition `(34864,43904)` followed by
the triple `(37210,30301,31680)`. The retained tests independently apply these
fixed nominations to the reconstructed PR3359 map. The first move preserves the
idle profile. Together they give `-2 H1 + H2`, preserve rank mass and deficit,
and match canonical payload
`96f0dc4e3b8f08cdfd385992e8675f033ed83bcd61bb14f8f6b9671b8c125fe3`.

Five original helpers relocate, but bin `(11,14,1)` loses TWO width-8 helpers
and gains width 7 and width 9. Thus the resulting change is not a permutation
with one original departure and arrival per bin. Its lower concave cost is
consistent with this theorem. We do not repeat its search, pricing or physical
admission. This control prevents interpreting our direct-cycle statement as a
barrier to interacting rearrangements or to all PR3359 improvements.

## Credit and limits

Pierre/hexapode's PR3359 supplies the exact map and its six composed cycles,
retaining Nick Petalas's PR3354 and PR3338 gains. The reconstruction starts from
Philippe Van Velzen's PR2169 source. Josie Elliston supplies the independent
owner/window audit, and Hao Yan the underlying T16 controller lineage. Credit
also Gonzalo Mier, George Lydakis, Rohan Arun, Jeremy Kothe and the retained
selected geometry, word, native and pricing authors. Original predecessor prose
and notices are retained byte-for-byte.

The theorem fixes the original map, calls, widths and windows. Moving several
original helpers out of or into a bin, using previously empty bins, changing
words or widths, splitting/reusing helpers, and changing chronology are outside
its scope. A new starting map needs a new certificate. No packing optimum,
new kappa, supplier admission, full native/cold replay, independent human review
or selected-frontier update is claimed.
