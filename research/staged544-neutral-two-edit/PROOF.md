# Neutral-first two-edit domains and exact coverage

This is an informal scoped proof with executable finite certificates. It is
not a formal-kernel proof, a supplier admission, or a universal retiming barrier.
The frozen inputs are the literal PR3734 providers retained by PR3886 at
`359fe0fe77d29544972fd22ee674085ed5a3b4d0`. Both are checked separately.

## 1. Interfaces and scalar meaning

Keep all entrances, target and centre cuts, helper exits, roles, wrappers,
native maps and native cut positions fixed. Retimings stay after the A prelude
and within one original A, B-warp segment, or restore phase. Every first and
second edit moves one existing ADD and may change its common binary frame.
All other frames remain fixed, except the frame changed by the first edit.
Inverse cleanup is rederived from the actual edited instruction sequence.

For ADDs `g = I+c E_ds` and `h = I+b E_uv`, require
`d != v` and `u != s`. These sufficient conditions give `gh=hg` on arbitrary
register contents, including independent dirty values. Crossing a nonzero
SCALE conjugates the moved coefficient exactly, as in PR3886. The verifier
also compares exact rational block matrices for every admitted first edit.
There is no assumption that helper inputs vanish.

The full free-operator interpreter and adapter are reused unchanged from Sagar
Thakrar and roger-sato, with their Arham Tahir frame-contract attribution.
They are not newly independent implementations in this contribution. The full
word replay checks all 632 live inputs and 91 arbitrary dirty buffers, both
orientations, reverse pull-back and the cleanup boundary. New small block
matrix checks supply an additional exact check of the first-edit algebra.

## 2. Frame-changing first moves at displacement at most two

Enumerate every original single-ADD insertion cut with final displacement at
most two positions, including the original position. Price every possible
dimension between the join L of the two preceding frames and the intersection
H of the two following constraints. The complete local price depends only on
that dimension, exactly as in PR3886. Fixed boundary checks are relaxed to
virtual climbs for pricing; every actual witness is checked by the full frame
auditor and its real boundary equalities.

Keep the zero signed histograms and require the chosen subspace to differ from
the moved gate's original frame. Every neutral dimension in this finite domain
is an endpoint `dim L` or `dim H`, as checked during replay. Therefore its
subspace is uniquely L or H: no unsampled same-dimension first-frame choice is
discarded. The exact enumeration supplies 122 legal first edits per provider.

For each such literal first word, price every permissible second ADD retiming
whose ADD touches at least one of the first ADD's two registers. There is no
distance bound on this second edit. Other phases are included when the second
gate touches one of those registers. The other gates and frames of the neutral
descendant remain fixed while this second move is priced.

A second ADD touching neither first register has a baseline counterpart of
identical price: its two projected register-frame sequences are unchanged;
the first gate always commutes with it, both before and after its coefficient
conjugation. Inserting/removing that disjoint first gate only duplicates cuts
on those projected sequences. Its admissible second-frame interval and its
crossed scalar factors therefore already occur in the baseline census.
Replaying the baseline obstruction covers these disjoint second moves.

## 3. Adjacent frame-preserving neutral starts

For every consecutive pair of commuting ADDs within one original scalar
segment, swap the pair while retaining both original frames. A shared register
must see both frame orders legally. Baseline monotonicity gives F_g <= F_h;
swapped monotonicity gives F_h <= F_g, so the two frames must agree if the pair
shares any register. If their touched registers are disjoint, each projected
frame sequence is unchanged. These conditions are also sufficient for all
unchanged boundary equalities, so the swap is neutral and legal exactly when
the shared frames agree. Identical gates would give the unchanged word and
are excluded if present.

The incremental trace implements this argument exactly: shared-register event
addresses and frames stay unchanged; an exclusive register's one event is
renamed from i to i+1 or conversely. Its before/after masks do not change.
The verifier cross-checks this construction against fresh chronological traces
and the independent retained frame auditor on representative cases, including
rejected pairs. The rational two-gate matrix identity is checked for every
legal first pair.

After every legal swap, enumerate all retimings of either swapped ADD,
including all second-frame dimensions. For a third ADD, it is enough to add the
new middle cut, by the following reduction.

### New-middle-cut reduction

Let g,h be the adjacent original ADDs at i,i+1 and k a different ADD. If the
second insertion cut is outside their middle, deleting k and inserting it at
that cut sees exactly the baseline projected frame masks on k's two registers.
If both g and h touch one such register their common frame masks are equal;
if only one touches it, its position in the projected sequence is unchanged.
The scalar corridor crosses both g,h or neither, since k did not originally
lie between them. Thus the sufficient commutation checks and all SCALE
conjugation factors agree with a baseline retiming. The signed invoice is the
same baseline invoice, including any relaxed boundary charges.

Only insertion into the new middle cut i+1 can expose a different combination
of the two registers' preceding/following frames. Enumerate that cut for every
third ADD that can reach it. If k was before the pair, its original upper cut
must reach i and it must commute with h, now first. If k was after the pair,
its original lower cut must reach i+2 and it must commute with g, now last.
These conditions are necessary and sufficient because all intervening gates
outside the pair are unchanged. Native segment restrictions are retained.

Moves in other phases or segments have unchanged projected constraints and
scalar corridors and are covered by their baseline counterparts. The separate
swapped-gate census, new-middle-cut census and replayed baseline certificate
therefore cover every second move in the original single-ADD class after each
of these adjacent neutral starts. No global word-search claim follows.

## 4. All-exponent sign certificates

For a signed new-minus-old child histogram d of zero rank mass, define

    C_k = sum_r d_r min(r,k),     S_j = sum_{k=1}^j C_k.

PR3886's credited discrete-curvature argument gives

    sum_r d_r r^(1-a) = sum_j S_j (theta_j-theta_{j+1}),
    theta_j = 2 j^(1-a) - (j-1)^(1-a) - (j+1)^(1-a).

For 0<a<1 the theta_j are positive and strictly decreasing. The last theta is
set to zero only for this finite summation identity. Hence nonnegative S_j
certify non-improvement for the whole interval, without floating-point sign
sampling. Every enumerated delta is checked exactly; zero deltas are neutral.
The second-frame dimension enumeration covers every price, even when several
different subspaces have the same dimension.

## 5. Positive control and limits

The positive fixture rolls back the already-retained Jeremy Kothe PR2957 swap
at A[4043:4045]. Its two ADDs then share the earlier rank-seven frame. Swapping
them while retaining both frames is a neutral first step. Raising the now-second
ADD to its retained rank-eight frame is a strictly improving second step:
`2+3 -> 1+4`. With cleanup and basis spelling restored, the result is the pinned
source word. Full arbitrary-dirty replay checks the rollback, neutral middle
and recovered word in each provider. This detects a real two-step gain but is
not a new improvement over the current source.

The two declared domains do not cover arbitrary nonadjacent neutral starts,
frame-changing starts beyond displacement two, non-neutral intermediate words,
simultaneous incompatible intermediate frames, SCALE moves, commutator
corrections, warp crossings, changed phases or interfaces. Unknown physical,
native realization and complete supplier costs are recorded as unknown, not
zero. No current supplier improvement, new kappa or selected-frontier change
is inferred from a failed finite search.
