# Dirty connector restoration with overlapping write windows

This is a written exact theorem for a specified query interface. It is not a
proof-assistant theorem or a selected-supplier implementation.

## Contract

Work over F2 with distinct rows x, z, y_1,...,y_k and arbitrary initial data.
The source x is immutable. B and A_i are arbitrary compatible linear maps;
singular and noncommuting maps are allowed. We require

    x' = x, z' = z, y_i' = y_i + A_i B x.

There are m ordered slots numbered 0,...,m-1. These are **logical permission
intervals**, not wall-clock deadlines or capacity-constrained time slots. A
slot may contain any finite sequential word. Output i may be written only
in its nonempty inclusive interval I_i=[l_i,r_i], must be correct at the end
of slot r_i, and is not externally observed before that end. Its delivered
value must remain fixed. Windows may coincide, nest, or partially overlap.
All windows and prices are fixed when compiling the straight-line schedule.

The only data operations are complete calls

    B at slot t: z += B x,       cost b_t > 0;
    A_i in I_i:  y_i += A_i z,   cost a_i > 0.

Each price includes that call's source access, arithmetic, fixed-port
frame/routing work, private scratch restoration, head return and dispatch.
These charges are indivisible and identical on repeated occurrences at the
same slot. No extra connector, clean copy of Bx, output feedback, source
mutation, nonlinear/data-dependent control, combined query or free map is
allowed. Caller-wide setup, lifetime and storage costs are additional, as
specified below. The word must be valid for **every** choice of maps and
data, rather than exploit a particular zero map.

## Theorem: even interval multiset price

Let c_t be the number of B calls in slot t. The exact minimum complete-query
price is

    Q = 2 sum_i a_i + min_c sum_t b_t c_t,                 (1)

where the minimization is over

    c_t in {0,1,2},  sum_t c_t even,
    sum_(t in I_i) c_t >= 1 for every i.                  (2)

For k=0, Q=0. Otherwise feasibility is immediate by placing two B calls in
each required slot. The theorem permits arbitrarily many calls in the
original alphabet; the {0,1,2} bound is a proved optimization reduction.

**Lower bound.** Specialize all maps to the scalar identity and take x,z0
and all output dirt as independent bits. An output needs an even number of
A_i calls to cancel z0, and cannot have zero calls because its x coefficient
must change. Thus it pays at least 2a_i. If no B call occurs in I_i, the
coefficient of x in z stays constant throughout that window. An even number
of A_i calls cannot give x coefficient one, a contradiction. Therefore
every window contains a B call. Restoring z at the final endpoint requires
an even total number of B calls. This proves the unrestricted integer
version of (1)-(2). For any c_t>=3, subtracting two at that slot preserves
positivity of its support and total parity and reduces positive cost.
Repeat to obtain c_t in {0,1,2} without weakening the lower bound.

**Attainment for arbitrary maps.** Choose any feasible multiset. Assign
each output to a slot in its window containing a B call. Immediately before
the first B call in a slot, read every assigned output once; immediately
after it, read each once again. These output updates commute because the
output rows are distinct and are not sources. Their combined contribution
to i is

    A_i z_before + A_i(z_before + Bx) = A_i Bx.

No earlier carried dirt or Bx term survives in that output. Emit any second
B call in that slot afterward. Every output is complete inside its own
window and unchanged later. Even total B parity restores arbitrary z0.
Linearity proves the construction at every row dimension; invertibility
and commutation are unnecessary. Exactly two A_i calls are used. This
attains (1), including each deadline, not merely the final matrix.

## Exact weighted recurrence

Let d_t=max{l_i:r_i=t}, with max(empty)=-1. After processing slots before t,
store F_t(s,p), the cheapest source-call bill, where s is the latest slot
containing a B call (-1 if none) and p is total B parity. Initially
F_0(-1,0)=0 and all other entries are infinity.

For c in {0,1,2}, put s'=t if c>0 and s'=s otherwise. If s'>=d_t, update

    F_(t+1)(s', p XOR (c mod 2))
        = min(current, F_t(s,p) + c b_t).                 (3)

Reject the transition if s'<d_t. Previous deadlines were checked when they
occurred; for windows ending at t, the latest occupied slot is at most t,
so the single test s'>=d_t is equivalent to hitting every such window.
The source-call answer is min_s F_m(s,0). Add 2 sum_i a_i to obtain Q.
There are O(m^2) state transitions after O(k+m) deadline preparation.
The reference implementation copies path tuples for deterministic ties;
that adds overhead and is not claimed to attain the optimal implementation
time/space bound. Rational arithmetic is exact; arithmetic bit complexity
is distinct from the transition count.

## Uniform tariffs and the actual permission that buys a saving

If b_t=b, let tau be the minimum number of slots hitting all intervals.
The standard earliest-right-endpoint greedy rule computes tau; equivalently,
tau is the maximum size of a pairwise-disjoint interval subfamily. The
usual proof chooses the earliest right endpoint, deletes every interval it
hits, and repeats: the chosen witness intervals are disjoint and force one
point each, while the selected endpoints attain that number.

The source-call count is exactly 2 ceil(tau/2): the lower bound is tau
rounded to even; if tau is odd, add one B call at any existing selected
slot. Thus

    Q_uniform = 2 sum_i a_i + 2b ceil(tau/2).             (4)

With disjoint windows tau=k, reproducing the one-source case of woklerx's
PR1442. If every window shares a slot, tau=1 and two B calls suffice. Merely
forming a connected chain of overlaps does not imply tau=1: our six
length-two windows have tau=3 and need four B calls. Ordinary interval
stabbing alone is insufficient because it forgets final dirty restoration.

For the equal-price comparison with disjoint requests, overlap saves

    2b [ceil(k/2) - ceil(tau/2)].                        (5)

This is a boundary-permission result. It gives no permission to prewrite an
actual caller's output. Weighted greedy need not be optimal: I_1=[0,1],
I_2=[1,2], b=(1,9,1), a=(1,1) cost six using B at 0 and 2. Choosing their
common point 1 costs at least fourteen including a cheapest outside close,
or twenty-two if both B calls occur there. Equation (3) finds the minimum.

## Complete cost recurrence and stopping rule

For a path c and input size n, write its actual caller cost as

    C(n,c) = P(n,c) + 2 sum_i C_Ai(n)
                      + sum_t c_t C_B,t(n).             (6)

P includes coefficient/program preparation, request descriptions, scheduling,
the connector and output lifetimes, root-level moves/frames, precision and
storage not already included in the complete child tariffs. Equations
(1)-(3) minimize (6) only when P is independent of the path. Otherwise
price P for the chosen path; a new path-aware optimization would be needed
to claim global physical optimality. We do not silently set P to zero.

When a complete child itself recursively expands, substitute its full cost
recurrence into C_Ai or C_B,t; every occurrence and its restoration is still
present in (6). No call rank is divided by the number of outputs. A family
of recursive callers would additionally have to establish contraction and
the correct types/sizes at each node. This package gives the exact boundary
scheduling recurrence, **not** such a contracting supplier recurrence.

Under a common complete B price, overlap helps against the PR1442 disjoint
interface only if its extra caller bill DeltaP is strictly less than (5).
For the six-output scalar fixture, the threshold is two complete B calls:
fourteen XORs, 28 reads, fourteen writes, 116 head steps, fourteen latch
resets and fourteen instruction dispatches (182 bits of fixed program).
These are separate tariff components, not quantities silently priced as
one XOR. All matrices are compiled into scalar gates; no
dynamic coefficient multiplication is free. No actual selected caller with
these permissions and a favorable DeltaP is supplied. Stop before supplier
adoption rather than assign an exponent to this abstract saving.

The selected complex and bit suppliers, their balance constraints, and all
uniform/native/hosting/precision/tape/analytic assumptions remain unchanged.

## Attribution

The dirty connector, scalar specialization, and sequential-delivery lower
bound are credited to Ross Richardson's PR934/943 lineage and woklerx's
PR1442. Woklerx's PR1439 supplies the concrete B matrix used in our pilot;
Ross Richardson's PR1780 solves the distinct mutable-source sequential
contract. Interval stabbing, parity and dynamic programming are standard
methods. The contribution here is their exact restoration-aware connection
to overlapping write windows, the attaining complete-query word, weighted
recurrence, and source-pinned evidence. Yuzhou Wang with substantial OpenAI
Codex assistance; Apache-2.0. No independent human proof review is claimed.
