# Exact tariffs for two reusable resources

This is a scoped written proof. The finite verifier corroborates it; it is
not a formal proof-kernel certificate or a physical implementation theorem.

## Model

There are n>=1 labelled consumers. Consumer i is live on a nonempty half-open
interval [s_i,t_i), has a fixed nonempty eligibility list L_i contained in
{0,1}, and pays w_i>=0 each time it moves between the two resources while
remaining live. Initial placement and release are free. Simultaneously live
consumers occupy distinct resources. There is no reserved initial or final
placement. The lists do not change during a lifetime.

Partition time at the distinct endpoints. A schedule gives a legal injection
on every elementary time interval, including intervals with no live consumers.
At a boundary its charge is the sum of w_i over consumers present on both
sides whose resource changes. Atomic exchanges are allowed. This is an
optimistic transfer model: a physical realization may need extra storage,
movement, restoration and time. We prove no zero-cost physical migration.

Pointwise Hall feasibility means every active set has an injective eligible
placement. In this two-resource model this says that at most two consumers
are live and, when two are live, their lists have union {0,1}. It guarantees a
schedule when migrations are allowed, since independent legal placements can
be chosen at every elementary interval.

## Theorem 1: exact weighted optimum and a checkable certificate

For each elementary interval k let S_k be its set of legal placements.
Pointwise feasibility implies 1<=|S_k|<=2. For consecutive placements a,b set

    c(a,b) = sum_{i live in both, a(i)!=b(i)} w_i.

Then the exact minimum charge is the shortest layered-path cost with every
initial placement free and every terminal placement accepted. In particular,

    D_0(a) = 0,
    D_k(b) = min_{a in S_{k-1}} [D_{k-1}(a)+c(a,b)],
    optimum = min_{b in S_last} D_last(b).

Every schedule is one such path with exactly that charge, and every path is
an allowed atomic schedule. Induction on the layer proves the recurrence.
There are at most 2n-1 layers and four arcs per layer boundary. After endpoints
are sorted, a sweep constructs the states and optimum in O(n) steps. Sorting
costs O(n log n). These bounds count exact arithmetic operations.

The implementation emits a path and integer potentials p_k(a). A separate
checker tests the path's cost M, p_0(a)<=0 for every initial state,

    p_k(b)-p_{k-1}(a) <= c(a,b) on every arc,
    p_last(b) >= M for every terminal state.

Along every competing path these inequalities telescope to charge>=M.
The supplied path attains M. Thus the checker does not need to repeat the
minimization. The optimizer's distances satisfy these certificate conditions.
Integer weights are the executable interface; the mathematical recurrence
also holds for arbitrary nonnegative real weights with exact comparisons.

Allowing extra changes inside an elementary interval cannot defeat the lower
bound. Sample the placement once in each interval. A consumer whose sampled
resources differ across a boundary must move at least once between samples.
For a fixed consumer these sampling windows are disjoint, and its lifetime
contains each such window. Nonnegative charges therefore dominate the sampled
path's charge. The event model already attains its own optimum.

## Theorem 2: the sharp worst-case migration count is max(0,n-2)

Set every weight to one. Every pointwise-feasible instance admits a schedule
with at most max(0,n-2) migrations. For every n>=1 there is an instance whose
minimum is exactly this number.

For the upper bound, separate the connected components of the interval
overlap graph, using positive-length overlap. Isolated consumers cost zero.
In a component with k>=2 consumers, process starts in time order, with endings
before starts at the same time. At most two consumers can be live.

Choose the initial placement of the first consumer to accommodate the first
consumer overlapping it. Such a choice exists by pointwise feasibility, and
no intervening consumer belongs to that component. If both begin together,
choose any feasible placement of the pair. This first pair costs no migration.

At every later start there is at most one continuing consumer. If its current
resource permits the new consumer's placement, do nothing. Otherwise the new
consumer must have a singleton list equal to that occupied resource. Hall
feasibility forces the continuing consumer to be eligible for the other
resource; move it once and start the new consumer. With no continuing consumer,
the new placement is free. Two simultaneous new starts also need no migration.
Thus each start after the first pair incurs at most one migration. The component
cost is at most k-2. Summing components is at most n-2 whenever n>=2 and there
is a nontrivial component. With only isolated consumers it is zero. This proves
the stated bound, including n=1.

For sharpness at n>=2, use one flexible consumer on [0,2n-1) with list {0,1}.
For i=1,...,n-1 put a blocker on [2i-1,2i), whose singleton resource is
(i-1) modulo 2. Blockers are disjoint and the instance is pointwise feasible.
During consecutive blockers the long consumer must occupy opposite resources.
It therefore moves at least n-2 times. It can move once in each intervening
gap, attaining the bound. At n=1 a single consumer attains zero.

Giving the long consumer weight W yields exact optimum W(n-2), since no
blocker can move. Consequently pointwise compatibility leaves an unbounded
additive migration bill even at concurrency two. At n=3 the family is the
smallest pointwise-feasible instance without a constant-per-lifetime eligible
assignment. One or two consumers always admit a fixed assignment: assign
disjoint consumers independently, or use their common feasible placement if
they overlap.

## Research consequence and limits

Ali Romman's [PR #5781](https://github.com/CrocSwap/integer-mult-bounds/pull/5781)
explicitly excludes temporal reuse from its static assignment model. The new
step solves this particular temporal extension and quantifies an obligation
that a per-time matching relaxation omits. This does not exhibit an error in
that predecessor, nor was its matcher run to establish this result. Hall's
theorem and layered shortest paths are classical; the scoped tariff, sharp
family and independently checked implementation are the contribution here.

The two-resource assumption, fixed lists, free initial/final placement and
atomic migration contract matter. This is no theorem about arbitrary coupled
native consumers or three or more resources. No actual helper lifetime export,
physical transfer word, selected supplier invoice, new kappa, uniform compiler,
stock/precision/tape proof or complete multiplication theorem is supplied.
