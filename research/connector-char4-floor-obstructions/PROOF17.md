# The characteristic-four floor fails at eighteen sources

This is a scoped written proof in the unsigned dirty-connector floor model.
It excludes eighteen sources and, by #4248's deletion lemma, gives N(4) <= 17.
It uses finite controls and exact integer arithmetic, without claiming a
proof-kernel certificate.

## 1. Prefixes and cube intersections

A walk uses each of k sources exactly four times. Set L=4k. Its cyclic
prefixes are q_t in (Z/4)^k, t=0,...,L-1, and u_t=q_t modulo two. Define
A={u_t}, r=L-|A| and n=L-r. Cyclic rotation translates every prefix by the
same vector, preserving four-prefix sums modulo four and preserving r.

For any translated binary cube, let V be its eligible boundary indices and
s=|V|. Write

    S0=min(k,floor(r/2)),
    H(k,r)=k+S0+floor((k-S0)/4).

Then s<=H(k,r). If V is empty this is immediate. Otherwise rotate to start
at an eligible boundary. Working in the translated coordinates, each source has one internal
edge 0->1 and one three-event bad arc 1->2->3->0. The bad arc stays in one
outside path, meaning a maximal path whose endpoints are eligible and whose
interior is outside the cube.

For each outside path, let d count complete source bad arcs and h count
internal 0->1 edges executed while another coordinate is outside. Its length
is 3d+h, with d>=1. Across all outside paths, sum d=k. If R is the number of
paths and I=sum h, the eligible vertices satisfy s=k-I+R.

Call a path small when h=0 and d<=3. It has 3d+1 parity vertices in a
subcube of dimension d, hence at least 3d+1-2^d>=2 local repeated vertices.
Charge each repeat to its later position, never to the path's first endpoint.
Charges from different paths are disjoint even at shared endpoints.

There is no cyclic endpoint loss. The two endpoint parities of a small path
differ, because every one of its d sources occurs three times. If boundary L
is locally repeated, replace its charge by the first earlier parity-zero
vertex in that final path. This vertex is interior, globally repeated from
boundary zero, and locally first, so it was not already charged. Thus all
charges lie among the r repeated cyclic positions, and 2S<=r for S small paths.

Paths with h>=1 contribute 1-h<=0 to R-I. Every other non-small path consumes
at least four bad arcs, while each small path consumes at least one. Hence

    R-I<=S+floor((k-S)/4)<=S0+floor((k-S0)/4),

which proves the bound. The same endpoint repair also preserves the full
local-repeat lower bound for any individual h=0 path with d<=3.

## 2. Free-coordinate slabs

Allow f coordinates to be unrestricted, leaving k-f binary constraints.
The corresponding intersection bound is

    H_f=k+3f+S_f+floor((k-f-S_f)/4),
    S_f=min(k-f,floor(r/2)).

To see this, let G be the unrestricted-coordinate edges occurring in outside
paths; the other 4f-G such edges occur inside. The eligible vertex count is
k+3f+R-I-G. Every path with at least one internal or unrestricted edge has
contribution at most zero to R-I-G. The remaining small paths have the same
repeat charge, and the k-f constrained sources supply their bad arcs.
Consequently H_f<=H(k,r)+3f, using S_f<=S0 and k-f-S_f<=k-S0.

## 3. Unions of cubes with the same parity

Let a length-4k source cycle use every coordinate four times, with prefixes
q_t in (Z/4)^k. Let P be any p distinct binary vectors, p>=1. Then

    #{t: q_t+a is in union_(v in P) ({0,1}^k+2v)}
       <= min(4k, 2k+2(p-1)).

The translates have the same parity and are disjoint as subsets of (Z/4)^k.

### Proof

Write each coordinate of q_t+a as low bit plus twice high bit. A boundary is
eligible exactly when its high-bit pattern is in P. Each coordinate high bit
flips exactly twice in the whole source cycle, at its 1->2 and 3->0 events.

Compress the cyclic sequence of eligible high-bit patterns by removing
consecutive repetitions, including across outside excursions with equal
endpoint patterns. Its number of transitions is zero for one visited region, and otherwise at most 2(p-1). Indeed, a
cyclic alternation A,B,A,B of distinct patterns would force a coordinate in
which A and B differ to flip at least four times, impossible. A cyclic word
on p letters with adjacent letters distinct and no such alternation has at
most 2(p-1) transitions. To prove this by induction, if some letter repeats,
take a shortest arc between consecutive occurrences of a repeated letter.
Every interior letter occurs once globally: another occurrence outside the
arc would alternate with its endpoints, and two inside would give a shorter
arc. Thus some letter occurs once. Remove it, costing at most two transitions,
and apply induction. If no letter repeats the bound is immediate for p>=2.

Let F be the f coordinates on which the patterns in P are not all equal.
Call a source event a budgeted low edge when it flips only the low bit and
its own coordinate high bit occurs among P at that coordinate. There is one
such edge for each of the k-f fixed coordinates and two for each of the f
varying coordinates, for a total k+f. Each such edge has either both endpoints
eligible or both outside. Let I count those outside.

An eligible vertex is entered by a budgeted low edge, a direct high-bit
transition between eligible regions, or an outside path. Classify outside
paths by whether their endpoint high patterns are equal or different.
Let R_same count the former and R_cross count the latter plus direct
high-bit transitions. Then, writing s for eligible vertices,

    s=k+f-I+R_same+R_cross.

The compressed-region argument gives R_cross<=2(p-1).

Consider a same-region outside path containing no budgeted low edge. At
least one high bit flips in the path, and since its endpoint patterns are
equal each coordinate flips either zero or twice. A varying coordinate
cannot flip twice: between its two high flips lies one of its budgeted low
edges, contradicting the assumption. Therefore some fixed coordinate flips
twice. Those two flips and the intervening wrong-high low edge are exactly
that source's three-event bad arc. Each fixed source has only one such arc,
which belongs to one outside path, so at most k-f same-region paths contain
no budgeted low edge. Paths with at least one budgeted low edge contribute
at most zero to R_same-I; budgeted low edges in cross paths only help.
Consequently R_same-I<=k-f.

Substitution gives s<=k+f+(k-f)+2(p-1)=2k+2(p-1).


## 4. Three levels of triple classes

In this section and below, put h=H(k,r). For equal-cardinality index sets,
colex order compares the largest index in their symmetric difference;
the set containing that index is larger.

Let A={u_t} be the set of distinct parity prefixes. Ignore masks in
P={0} union {u_a+u_b:a!=b}; its size is at most 1+C(n,2), n=4k-r.
For every other mask, every four-readout representation has four different
parity-prefix values. Its four three-prefix parity sums are distinct and do
not belong to A.

Consider all three-element boundary-index subsets whose parity sum is not
in A. Let V be the number of their distinct full sums modulo four. Join two
full sums when they differ by 2e_j for some j and both occur. Let X be the
number of connected components of this graph. Finally let Z be the number
of distinct parity sums of these full sums. Each parity class contains some
number t of X-components and v distinct full sums.

An X-component with v_i full sums has all its carry differences supported on
at most v_i-1 coordinate axes, using a spanning tree. The slab bound gives
at most h+3(v_i-1) possible fourth boundaries across that component. Summing
over its t components gives 3v+(h-3)t. Separately, the same-parity
union-cube lemma above gives at most 2v+2k-2 fourth boundaries for the entire
parity class.

Put d=2h-2k-2. When k+1<=h<=2k and t>=2,

    3v+(h-3)t - (2v+2k-2) >= d(t-1),

because v>=t and the remaining difference is (2k-h)(t-2)>=0.
For t=1 no subtraction is needed. Thus the total number of mask/parity-class
incidences is at most

    3V+(2k-h-1)X+(2h-2k-2)Z.

Each non-P mask has at least four different triple-parity-class incidences,
one from each distinct last-prefix parity in its representation. For fixed
triple parity and fixed last-prefix parity the binary target is determined,
so counting possible fourth indices upper-bounds incidences. Therefore

    masks <= 1+C(n,2)
             + floor((3V+(2k-h-1)X+(2h-2k-2)Z)/4).

The coefficients used below are nonnegative. Here h denotes H(k,r).

## 5. Pair graphs bounding V, X and Z

Use events 1,...,L-1, L=4k, so the closing source occurs three times and
others four times. For equal-source events a<b use these pairs:

Y: {a-1,b} -> {a,b-1}, exact full-sum equality.
X: {a,b} -> {a-1,b-1}, changing the full sum by 2e_j.
Z: {b-1,b} -> {a-1,a}, parity equality, taking one earlier a per later b.

Each replacement removes the largest index b. In a three-subset whose
parity is not in A it cannot create a repeated index, since that would make
the parity sum one prefix. Minimum-colex representatives for full values
avoid Y pairs; representatives for X-components avoid X and Y pairs;
representatives for parity classes avoid all three pair types after replacing
duplicate parity-prefix indices by their earliest representatives.

For a graph with m forbidden pairs on N indices, and wedge count
W=sum_v C(deg(v),2), the number of independent triples is at most

    C(N,3)-m(N-2)+W.

This is the first two inclusion-exclusion terms. Ignoring its negative
triangle correction is safe.

The Y graph has exactly mY=6k-3 edges. The XY graph has at least
mX=12k-6-2r edges. The full XYZ graph, after discarding r duplicate parity
vertices, has at least mZ=15k-7-13r edges, clamped below at zero.

For mX: earlier same-source event-endpoint pairs overlap only when two
successive occurrences are consecutive events. Each such adjacency costs
at most two XY pairs. Each adjacency ends at a repeated parity prefix, so
there are at most r. For mZ, the pre-deletion graph has at least15k-7-3r
edges by the following direct count, and its maximum degree is ten, as below.
For a source with q retained events, the later event of rank i>=2 has at most
2i-1 distinct earlier neighbors. Without adjacent equal-source events the
total is q^2-1. Summing q=4 for k-1 sources and q=3 for the closing source
gives 15k-7. A consecutive equal-source pair reduces this total by at most
three, and ends at a repeated parity prefix. There are at most r such pairs.
Deleting r vertices then loses at most 10r further edges.

The maximum degrees for Y,XY,XYZ are respectively 6,9,10. Their wedge counts
are at most respectively 22k,70k,108k before vertex deletion, and at most
(D-1)m by maximum degree. To see the rank bounds, assign a boundary between
an event of occurrence rank i and the next event of occurrence rank j the
following degree upper bounds alpha_i+beta_j:

| graph | alpha_(1..4) | beta_(1..4) |
|---|---|---|
| Y | 0,1,2,3 | 3,2,1,0 |
| XY | 3,4,5,6 | 3,2,1,0 |
| XYZ | 3,5,6,7 | 3,3,2,1 |

The boundary zero may be assigned the omitted closing rank four; its actual
degree is smaller. The missing closing event only decreases the bounds.
Each rank occurs k times in each marginal. Rearranging alpha and beta in
the same order maximizes sum C(alpha+beta,2), giving
22k,70k,108k respectively. Deleting vertices cannot increase wedge count.

Thus, for k=18,L=72 and n=72-r,

    V <= C(72,3)-105*70+min(5*105,22*18),
    X <= C(72,3)-mX*70+min(8*mX,70*18),
    Z <= C(n,3)-mZ*(n-2)+min(9*mZ,108*18),

where mX=max(0,210-2r), mZ=max(0,263-13r). The right sides decrease with
the actual edge count on the ranges used, so substituting its lower bound
is safe.

## 6. Initial eighteen-source cases

At k=18,L=72, the exact arithmetic in axis_obstruction.py evaluates every
r=0,...,20. All rows exclude 2^18 masks except r=2,4,5, whose conservative
upper bounds including zero are 262506,265606,262744. A four-readout multiset reduces to an even subset of at most four of the
n distinct parity prefixes, giving at most 1+C(n,2)+C(n,4) parity masks.
For r>=21, n<=51 and

    1+C(51,2)+C(51,4)=251176<262144=2^18.

It remains to handle the three exceptional rows. Their theoretical cube caps
H are 23,24,24 respectively.

## 7. Closing the exceptional cases

Let q_0,...,q_(L-1) be the cyclic mod-four prefixes, L=72. Call index b
axis-deletable when some a<b has q_b-q_a=2e_j. Every minimum-colex representative
of an X-component in Section 4 avoids b. Indeed, replace b by a in any
three-index subset with parity sum outside the prefix parity set. Its three
parities are distinct, so this does not duplicate another index; the new full
sum is connected to the old by one X edge and the index triple decreases in
colex order. Consequently, a specified number of axis-deletable indices may be discarded
before counting X-components. Representatives are minimized over the
original triples: if a pair rewrite introduces another discarded axis index,
its earlier partner replacement preserves the component and further lowers
colex order.

The XY graph has degree at most9 and at least210-2r edges before deletion.
After q such deletions it has at least m=210-2r-9q edges on N=72-q vertices.
Its wedge count is still at most min(8m,1260), using the same monotonic
substitution. Thus

    X <= C(72-q,3) - (210-2r-9q)(70-q) + min(8(210-2r-9q),1260).

For a literal three-event run j,j,j starting after boundary a, indices a+2 and
a+3 are axis-deletable: their earlier partners are a and a+1 respectively.
Their full sums differ by exactly2e_j, without any condition on the entering
prefix. If the run ends at cyclic boundary L, use L-1 as one deletable index,
partner L-3. Replace the other, omitted index L, by index L-2: q_(L-2)=2e_j,
because the last two events are both j and q_L=0. Its earlier partner is0.
These two indices are distinct. For disjoint outside paths the chosen indices
are distinct, as their first endpoint is never selected. This remains true
when paths share eligible endpoints.

Now branch on whether some translated binary cube attains the maximum H
used in each critical r row. If none does, all cubes have intersection at most
H-1. The general slab cap still uses theoretical H, so use the following
conservative four-per-axis replacement. For an X-component with one full
value, its fourth-boundary cap is H-1. With v_i>=2 full values, the old slab
bound H+3(v_i-1) is at most4v_i+H-5. Thus a parity class with v full values and
t X-components has cap4v+(H-5)t. Combining with the same union cap2v+2k-2,
subtract (2H-2k-4)(t-1) when t>=2. The remaining difference is bounded below
by (2k-H+1)(t-2)>=0 because v>=t. Summing classes gives incidence numerator

    4V+(2k-H-1)X+(2H-2k-4)Z.

All coefficients are nonnegative here. No attained-H geometry is used in this
branch. The corrected counts are255394,259733,257507 for r2,4,5.

If H is attained, let S count small h=0 outside paths, each with d<=3 bad arcs.
Rotate at an eligible boundary of that cube as in the component argument;
the walk still restores at L and the shifted cube is again a translated cube.
The component argument gives R-I <= S + floor((18-S)/4). At r2, S<=1 and
H=23 forces S=1 and at least4 other h=0 paths with d>=4. The small path
therefore has d<=2. A d2,h0 path has7 parity vertices in a two-dimensional
affine subcube, and hence at least3 local repeated vertices. These imply at
least3 global parity repeats. If its final endpoint is L, replace a charged L
by the first earlier parity-zero vertex in that path, just as in Section 1;
the endpoints have different parity, so this earlier occurrence is interior
and locally first. Thus d2 contradicts r2. The small path has d1, and is a
literal triple-equal-source run, giving q=2 axis deletions.

At r4 or r5, S<=2 and H=24 force S=2 and at least4 other h=0 paths of d>=4.
The source budget18 is exhausted by minimum costs1+1+4+4+4+4, so both small
paths have d1. They give q=4 axis-deletable indices. We do not need to control
the fifth repeat at r5.

The registered exact arithmetic in axis_obstruction.py gives the following upper
counts, all below262144. V and Z retain their conservative Section 5 bounds.

| r | H | q | new X upper | H attained | H not attained |
|---|---|---|---|---|---|
| 2 | 23 | 2 | 43216 | 252714 | 255394 |
| 4 | 24 | 4 | 40420 | 248171 | 259733 |
| 5 | 24 | 4 | 40552 | 245287 | 257507 |

Every eighteen-source floor walk is therefore excluded, and deletion gives
N(4)<=17.
The earlier certified lower bound remains9.
