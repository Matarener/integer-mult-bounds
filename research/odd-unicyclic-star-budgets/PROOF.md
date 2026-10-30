# Exact budgets for prescribed targets with one odd cycle

This scoped theorem was produced by Nick Petalas. It extends Sam Sung's
[graph-target note](../asymmetric-hypercube-decoder/GRAPH-TARGETS.md), from
PR #669. That note supplies the observation model, the unit-row criterion,
the general nonzero-constant lower bound, and the triangle specialization.
The new contribution is attainment for every prescribed target set with
exactly one cycle in total, provided that cycle is odd. The lower-bound
argument is included to make the extension readable on its own.

## Statement

Let p >= 3, and let G be the complete graph on n = 2p vertices with a
perfect matching removed. Its E = 2p(p-1) edges are the signed two-ports.
All vector spaces in this note are over F2.

For a retained edge set F, the available observations are the vertex sums

    star_v(F) = sum_{e in F, v in e} x_e

and the empty star `sum_{e in F} x_e`. This is the source's C+ code. At k=2,
the permitted overlap correction for target uv is star_u + star_v and
therefore adds no observation. Every retained input x_e is arbitrary and
independent.

Let T be a prescribed target edge set. Assume the spanning graph with edges
T has exactly one cycle in total, of odd length. It may also have trees
attached to that cycle, other tree components and isolated vertices.
Write r = |T| and s = n-r+1, the number of components of T, including
isolated vertices. Then the minimum number of deleted edges disjoint from
T that makes every x_t, t in T, individually recoverable is

    delta_+(T) = 2p(p-1) - r - floor((2p-r+1)^2 / 4).          (1)

In particular, the optimum depends only on p and r within this class.
Formula (1) applies to every p, with no upper bound imposed by the finite
checker. Without the empty star such a cyclic target set is infeasible,
as already proved in the source's feasibility criterion.

## The inherited lower bound

Combine r individual unit decoders into a vector decoder. It assigns each
vertex v a coefficient a_v in F2^r and the empty star a coefficient b.
At a retained edge uv the coefficient is a_u + a_v + b. It must be the
corresponding standard basis vector e_t for t in T and zero on every
retained nontarget edge. If recovery uses arbitrary exact postprocessing of
these linear observations, the same criterion still applies: an input
coordinate recoverable on every input vanishes on the observation kernel,
and hence belongs to its row space.

Summing the target equations around the unique odd cycle gives

    b = sum_{t on the cycle} e_t != 0.                       (2)

Let H be the retained nontarget graph, with h components including isolated
vertices. On every edge of H, a_u + a_v = b. Thus H is bipartite. In each
component choose a root with coefficient c_i and write
a_v = c_i + sigma_v b, where sigma_v is the path parity from that root.
The target coefficients all lie in the span of b and the vectors c_i+c_j.
This span has dimension at most h, because the latter vectors are spanned
by c_i+c_1 for 2 <= i <= h. The r target coefficients are independent, so
h >= r.

A bipartite component with v vertices has at most f(v)=floor(v^2/4) edges.
Put g(t)=f(t+1) for integers t >= 0. Then g(0)=0, and the successive
increments of g are 1,1,2,2,3,3,... . They are nondecreasing, so
g(a)+g(b) <= g(a+b) for a,b >= 0. Consequently, for component sizes v_i,

    |H| <= sum_i g(v_i-1)
         <= g(n-h)
         <= g(n-r) = floor(s^2/4).                          (3)

At most r+floor(s^2/4) edges can remain. Subtracting from E proves the
lower bound in (1). This is the source's nonzero-constant bound applied
to a target set that forces b != 0, rather than a new lower-bound method.

## Choosing a balanced root set despite the missing matching

Choose one root from each component of T. We need a choice R of s roots
and a partition R=A disjoint-union B with

    |A|=floor(s/2), |B|=ceil(s/2),

such that no removed matching edge has one endpoint in each part.

For any root set, group its complete matched pairs into atoms of size two,
and its unmatched root vertices into atoms of size one. Keeping each atom
in one part prevents every forbidden crossing.

If there is at least one singleton atom, every integer size from zero to s
is a sum of atom sizes. Indeed, if there are a double atoms and b >= 1
singletons, the intervals [2j,2j+b], for 0 <= j <= a, cover all integers
from zero to 2a+b. Thus the balanced partition exists. If every atom has
size two and s is divisible by four, it also exists.

The only remaining case is a root set made entirely of complete matched
pairs, with s congruent to 2 modulo 4. There is a nontrivial target
component, since T contains an odd cycle. Replace its chosen root v by
another vertex w in that component. Initially R is a union of complete
matched pairs. Since w was not a root, neither was its mate. Since v was
a root, its mate was a root in another component. After the replacement,
w and the mate of v are singleton atoms. The preceding argument applies.
The replacement preserves one root per target component.

This proves the required root-selection statement for all s >= 1. When
s=1, A is empty and B consists of the sole root.

## Attaining the bound with literal decoder coefficients

Take R,A,B as above, and let H contain every edge between A and B. All
these edges exist in G. They are nontarget edges because distinct roots
belong to distinct target components. Therefore

    |H|=|A||B|=floor(s^2/4),   F=T disjoint-union H.

Here is a direct construction of the unit decoders, including their empty
star coefficients. Define b by (2). Set a_v=b at every root in A and
a_v=0 at every root in B. Remove one edge t_0 of the target cycle, leaving
a spanning tree in each target component. Traverse those trees outward
from the selected roots. For a tree edge t=uv, with u already assigned, set

    a_v = a_u + b + e_t.                                   (4)

All retained tree edges now have their desired coefficient. Along the
path replacing t_0 there are an even number of edges, because the removed
cycle is odd. Summing (4) along that path gives

    a_u + a_v + b = sum_{t on cycle, t != t_0} e_t + b
                  = e_(t_0).

So the omitted cycle edge also has its unit coefficient. At any edge of
H, one root has label b and the other zero, giving coefficient b+0+b=0.
Each coordinate of this vector identity is an actual decoder for one
prescribed target using the allowed observations on F. Every retained
nontarget input has coefficient zero, without an input restriction.

Exactly r+floor(s^2/4) edges remain. Together with (3), this proves (1).

## A first case beyond the source's triangle formula

At p=3 let T be the five-cycle 0,2,1,4,3,0, with vertex 5 isolated. All
five target edges are allowed. Here r=5, s=2 and E=12. Take roots 0 and 5,
so H consists of the single edge 05. The construction retains six edges
and deletes six. Bound (3) proves that fewer than six deletions cannot
suffice. No triangle is present in this target graph.

For a triangle with all other vertices isolated, r=3 gives
delta_+=p^2-4, recovering the source's already proved result with credit.
The added scope includes longer odd cycles and arbitrary tree additions.

## Scope

This is a uniform algebraic proof with finite corroboration. The code
constructs coefficients; it does not implement the observations as paid
native operations. Physical frames, helper acquisition, dirty restoration,
tape movement, precision, recursive prices and the complete multiplication
theorem remain separate obligations. No new kappa is claimed.

New proof and checker are Apache-2.0. The source credits the graph-incidence
bridge to Martinez-Bernal, Valencia-Bucio and Villarreal, and retains Joel
Pulikkan / GamingPuzzled, icekylinx and eumemic's paired-cube lineage.
