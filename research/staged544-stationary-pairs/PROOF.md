# Stationary two-frame compatibility on the pinned staged544 words

This is a source-bound finite theorem, not a general property of framed circuits.
On each immutable PR3734 provider, hold all scalar operators and their order,
all native maps and frames, every other scalar frame, cuts, entrance/terminal
frames, helper identities, and the caller fixed. Choose at most two distinct
ADD addresses, and simultaneously replace their common binary frames. Require
the resulting whole framed word to be legal. Then at least one of the two
single-frame replacements gives a legal intermediate word. The complete local
recursive moment cannot decrease for any real `0<a<1`.

The compatibility statement is the added result. PR3942 already treats legal
sequential first-frame changes followed by a second edit in its declared
scalar corridors. This work resolves the stationary portion of its omitted
illegal-intermediate question. Its independent price rows corroborate that
consequence and also explicitly check the complete stationary address domain.
No gate displacement, new native boundary, new helper or supplier is included.

## 1. Exact reduction to adjacent events on a register

The credited PR3886 trace records every scalar common frame on every touched
register, every exact native/centre/target check, each native map, and the
terminal climb. In each register's chronological sequence, a scalar event
changes a frame `P` to `F` with `P⊆F`. Its positive dimension increase costs
`H_(dim F-dim P)`. Checks require equality; maps have fixed entry and exit.

Changing one ADD changes at most two frame nodes. Two distinct ADDs interact
only if they are consecutive events on at least one shared register. If a fixed
event intervenes on every shared register, all affected consecutive edges are
disjoint. The final legality constraints and the profile delta then factor into
two single-edit systems. Each final frame is individually legal, so either order
is legal; the two individually nonnegative moments add. A shared register alone
is not enough to call a pair coupled. A fixed check/map between them also breaks
the interaction.

The checker constructs the coupled graph by consecutive trace events, then
independently verifies that definition with direct address-position scans. There
are 5,549 ADD addresses and `5549*5548/2 = 15,392,926` unordered pairs per provider.
Exactly 8,923 are coupled; the other 15,384,003 use this factorization. The latter
number counts factored address pairs, not explicitly priced circuits.

## 2. Final simultaneous legality, without an intermediate assumption

For a coupled pair with chronological frames `F` then `G`, delete both frame
nodes while retaining all neighbouring fixed frames. On each affected register,
partition selected nodes into consecutive runs. A run has fixed exterior `P,Q`.
Its exact bill is the sum of positive consecutive dimension differences in
`P,F,Q`, `P,G,Q`, or `P,F,G,Q`; subtract the original run bill. Every run must be
nested. If `Q` is a fixed check, its preceding selected frame must equal `Q`.
The implementation enforces that equality as both an upper and lower bound.

Joining all exterior lower bounds and intersecting all exterior upper bounds
gives `L_F⊆F⊆U_F`, `L_G⊆G⊆U_G`, plus `F⊆G`. Propagate this relation by replacing
`U_F` with `U_F∩U_G` and `L_G` with `L_G+L_F`. No old opposite frame is imposed.
Consequently this domain includes a final pair even when both direct one-edit
intermediates would fail.

Every subspace of each resulting quotient is enumerated by adjoining vectors.
The largest actual quotient dimension is three; the guard rejects dimensions
above four rather than silently sampling. Every nested pair is checked against
all original affected runs, including fixed checks. There are 10,591 such frame
assignments and 9,883 distinct pair/dimension cells per provider. Multiple frame
orientations with the same dimensions have the same recursive invoice.

For each assignment the first replacement alone is legal precisely when
`F_new⊆G_old`; the second alone is legal precisely when `F_old⊆G_new`. All fixed
exterior constraints already hold. The checker finds at least one true predicate
in every case and recomputes all affected runs for each claimed legal order.
First-earlier is legal in 10,307 assignments; first-later in 10,545. These counts
overlap. The source-bound number with neither order legal is zero.

This zero is not assumed or a general theorem: the controls use old
`F=G=span(e1)` and new `F=G=span(e2)` between `0` and `span(e1,e2)`.
The final pair is legal and neutral; neither direct intermediate is legal.
The production detector reports both orders false and both intermediate
boundary checks reject. That synthetic pair is not an occurrence in staged544.

## 3. Independent subspace and dimension checks

For each distinct actual interval, the control chooses quotient representatives
and enumerates every subset of all quotient vectors, taking its XOR span. This
independent algorithm agrees with the production adjoin-one-vector enumeration
on all 1,345 distinct intervals across the two providers.

A second exact feasibility test checks every dimension cell. With propagated
bounds `L⊆F⊆H`, `M⊆G⊆K`, `F⊆G` and `L⊆M`, the smallest possible `dim(F+M)` for
`dim F=d` is

`dim M + max(0, d - dim(L + (H∩M)))`.

Indeed one can choose at most `dim(L+(H∩M))` dimensions of `F` inside the span
already paid by `M`; extend `L` through that subspace first, then outside it in
`H`. Each outside dimension increases the join by one. Such an `F` can be
extended to `G` of dimension `e` inside `K` exactly when this minimum is at most
`e`, with the separate individual dimension bounds. The checker compares this
formula with the exhaustive nested subspaces for every coupled pair.

Merely imposing individual dimension intervals and `d≤e` admits 100 false cells
per provider. At actual B addresses 362 and 366, `(d,e)=(4,4)` satisfies those
naive inequalities but requires `dim(F+M)≥5`. No compatible 4,4 pair exists.
This is why a dimension-only apparent gain is not a literal rank exchange.

## 4. Complete local prices and the paid exchange target

All 5,931 single-frame assignments and all 10,591 coupled assignments are
priced from every changed register edge, including final returns. Their signed
rank histograms have zero rank mass. There are 19 single and 42 coupled signed
profile types. The retained exact min-basis certificate checks every row:
`C_j = sum_r delta_r min(r,j)`, `sum_{j≤k} C_j≥0` for `1≤k≤8`, and `C_9=0`.
This sufficient criterion, proved and credited in PR3886, implies
`sum_r delta_r r^a≥0` for every `0<a<1`. Independent controls reconstruct all
coefficients. For completeness, write `f(r)=r^a` on ranks0..9 as
`f(r)=sum_(j=1)^8 c_j min(r,j) + (f(9)-f(8))*r`, where
`c_j=2f(j)-f(j-1)-f(j+1)`. Concavity makes these coefficients positive,
and decreasing curvature magnitude makes `c_1≥...≥c_8` for `0<a<1`.
Summation by parts expresses `sum c_j C_j` as nonnegative differences
`c_j-c_(j+1)` times prefix sums of the C's, plus `c_8` times their final
prefix sum. The rank-mass term vanishes. This proves the stated sign criterion.
No floating-point price decides a sign.

Thus the favorable `H1-2H2+H3` exchange of PR3863 cannot be realized by this
stationary two-ADD frame contract. The control distinguishes that favorable
exchange from its non-improving reverse. PR3863's 1,775-exchange overhead budget
belongs to its separate complete supplier calibration; this local census does
not multiply its own address counts into that budget or claim a new supplier.

## 5. Arbitrary dirty states and remaining costs

A frame-only edit changes no ADD opcode, operands or rational coefficient; no
SCALE, native operator, precondition, compensation, central update or cleanup
operator changes. Therefore the complete ordered free-operator product is
literally identical on every independent input symbol, including arbitrary
dirty helpers and the dual representation. This is a universal algebraic
identity, not an inference from clean-input tests. Inverse cleanup is identical.
Frame legality supplies a legal framed realization of that unchanged program.

The retained Thakrar/roger-sato interpreter additionally replays both full
baselines and four edited whole words per provider, including a cross-A/B pair,
an A/A pair, a B/B pair and restore/restore. All 632 live inputs and 91 dirty
buffers are retained, with both orientations and reverse cleanup. These are
whole-word controls, not a claim to execute all 21,182 variants in that
interpreter. The exhaustive exact local legality/invoice calculation and the
identical semantic program give universal coverage of the declared family.

CHECKS files include every baseline primitive count and helper width, the full
local profile (3,519 children, rank mass 5,134), 408 helper roles, 91 dirty buffers,
72 B native warps, 36 initial corrections and unchanged scalar coefficient
bounds. Every changed profile is reconstructible from RESULT signed rows.
No gates, helpers or buffers are added. Fresh native Gaussian/Clifford phases,
physical hosting/owner chronology, uniform stock/precision/tape tariffs,
all-size compiler, outer/supplier, analytic and BIT obligations remain inherited
or unknown, never zero. No physical or selected-frontier improvement follows.
