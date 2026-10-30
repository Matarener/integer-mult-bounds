# The G20 split and its complete bill

## 1. Exact source and cut

Use the PR5671 word at31bd16e74c3833a9fb25dca17a0f00fa9046325c.
All normalized values are linear over F2. QUERY changes the physical
frame and leaves the normalized row unchanged. ADD uses one actual
common frame. Each owned ERASE removes its arbitrary input column.

Immediately after event14875, fields19,465,466 and665 have frame508.
This frame has dimension4. Let A be the complete scalar prefix and B
its suffix, with all684 entry and output columns. Define

    a = e19^T + e465^T,       b = e465 + e466 + e665,
    c = e465^T,              d = e297 + e465.

The executable check proves aA=c, Bb=d and ab=cd=1. Both boundary
vectors use retained helpers with entrance frame1 of dimension8 and
exit frame0. No main or owned input occurs in c. No main or owned
output occurs in d. These are exact row identities, not point samples.

The helper basis G is the single ADD297,465. Its row465 is c and
Gd=e465. The cut basis J is

    ADD465,19; ADD466,465; ADD665,465.

Its row465 is a and Jb=e465. Each operation is its own inverse over F2;
the inverse program uses reverse order. All basis operations use one
physical frame. Their exact matrices need no recursive call.

Apply G inverse at the input. Run the source prefix and apply J.
Field465 now contains the independent old helper coordinate. Keep it
as an early output at frame508. New independent input684 starts at
frame508. Substitute it for role465 in J inverse, the full source
suffix and the final G. Give field684 final frame0. Every other output
has its source endpoint. The new program has eight more ADDs.

For helper vector h and successor input z, the suffix state changes
by b(z-c h). Its helper output is h+d(z-c h). The final basis gives
G h+e465(z-c h). Thus the old independent coordinate has already
returned at frame508, and the successor independently returns at0.
No helper is assumed zero. The early output stays public and live.
No new owned field, COPY or CLEAR is needed.

## 2. Physical action and target normalization

For each actual frame U, let D_U denote its source bit coframe operator.
The physical value of a normalized row is the corresponding D_U image.
Every common-frame ADD commutes with D_U. Nested source query frames
satisfy the exact rational projector identities. This induction applies
to arbitrary functions and every positive tensor width under the
retained native contract. It is not restricted to the two finite address
moduli used as controls.

The new targets are D_508 D_1 and D_0 D_508. Their residual ranks are4
and4. The first uses the complement of frame508; the second uses
frame508 itself. `MATCHER.json` contains the actual rational forward
basis and inverse. Both matrix products are the identity, and the
frame and complement are orthogonal. The complete fee includes both
directions and both paired address halves:5,472 new coefficient terms
and72 new route passes over all36 targets. Their positive fixed fees
enter the finite ordinary bound.

All685 independent local columns are checked in forward and separate
adjoint replays. Each includes arbitrary dirty owned inputs. A dynamic
bit iterator covers the new public column684; the inherited iterator
was bounded by the old field count. The complete frame induction and
source formulas, rather than finite point samples alone, supply the
all-function claim.

## 3. How far the cut strategy was taken

At every cut and physical common-frame bank, group helpers by their
entrance and exit frames. The cut frame must lie strictly between both
boundary frames. The current domain requires a helper in that group
as the physical pivot. Other public fields and existing owned fields
may occur in the cut bank.

For each group, remove its input columns from A's bank rows and its
output rows from B's bank columns. Compute the two exact kernels.
Their vectors give a and b with aA=c and Bb=d supported on the group.
A candidate needs both ab=1 and cd=1. The second test excludes empty
owned coordinates that carry no independent helper input.

The search tests each left kernel basis vector and each sum of two
basis vectors. This suffices for existence of a left vector for which
both right-side linear functionals are nonzero: if no basis vector
works, choose one on which the first functional is nonzero and one
on which the second is nonzero. Each other's functional is then zero,
so their sum works. For two nonzero right linear functionals, either
they agree or their pair is surjective onto F2 squared. The code
constructs a right vector with both values one in each case.

Every touched bank is checked after each event; unchanged banks have
unchanged matrices. Exact tuples remove duplicate contexts. The source
has7,412 distinct contexts and six basis witnesses at the two frames.
The4+4 split gives more concave credit than7+1 for0<t<1. It also gives
the largest two-part split credit of rank8, by strict concavity.
After its full installation,7,869 contexts contain no next split.
This does not exclude a different first basis that changes future
opportunities, a pivot outside the helper group, a changed scalar word,
or a different physical role assignment.

## 4. Caller and ordinary admission

All18 local calls use the emitted word. The controller, main physical
polynomial proof, thin queries, whole idles and boundary programs stay
literal source inputs. Each successor has its own public owner.
The complete source ledger gives11,022 originals,48 owned fields,
56,223 paid queries,443,238 events and2,529 owned payload episodes.
No owned output receives target credit.

The paid histogram is unchanged. The target change is36H4-18H8.
Its rank mass is zero, and its moment gain is

    18 * (2 * 4^t - 8^t) > 0,   0<t<1.

The complete rank surplus is753. The ordinary fee uses the new public
field count in parent parking, completion tails and stock. The raw
stream, all scalar operations, all owned entry and exit clears, zero
headers, source descriptors, routes, target normalizers and recursive
backend costs have positive charges. The precision majorant has517
bits. The coarse primitive bound is952,838,566,869, below2^64.

Two rational interval engines give raw crossing
(.00350741073845,.00350741073849). Test at.00350741073843, use uniform
saving.00350741073842, reserve2^-48, tensor degree2048 and cover gap
10^-14. The fresh strict thresholds are

    H0 = 748357344491618305,
    H1 = 524959317249823813072659373926.

Five finite backend levels from the completed PR5671 component give
ordinary BIT saving.003507410738409. Fresh rank-mass tails and uniform
compiler-tail guards also validate the retained strict-margin theorem:
every saving strictly below this fixed invoice crossing is attainable
with new finite parameters. The crossing itself is not admitted.
A stronger Gaussian caller and the full outer assembly remain separate.

## 5. Verification boundary

The wrapper rebuilds outputs in a fresh directory in normal and optimized
Python. The second global implementation checks every source descriptor
and all input columns. Invalid cut vectors, missing boundary bases,
stale source epochs and an extra H8 target reject. Frozen files and
published artifacts must remain byte-identical after replay; gzip
container bytes and measured CPU time are excluded only when comparing
rebuilt scientific outputs.

The retained framework assumptions remain. The uniform compiler word,
its enormous stock and the rounded multiplication algorithm are not
executed. These checks are not independent human acceptance or a
proof-kernel theorem. No selected-frontier change is made.
