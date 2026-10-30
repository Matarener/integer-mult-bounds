# Exact finite map and complete historical charges

For ordered ground points P, let D_(a,b)(P) send each a-subset input to the
sum of inputs disjoint from each b-subset target. Splitting P into L and R,
the channel with source-left cardinality i and target-left cardinality j
is `D_(i,j)(L) tensor D_(a-i,b-j)(R)`. Applying these two tensor factors in
either order gives the same integer map. This equality holds on arbitrary
inputs and needs no cancellation or approximation.

The constructor changes only subproblems of shape `(n,a,b)=(11,2,2)`.
The pinned planner splits them into five and six ground points. In channel
`(i,j)=(1,1)`, the left-first and right-first unshared costs are both 146;
the constructor checks this equality explicitly. It takes the opposite order
from the planner. All other channels and all root choices stay as in #981.
The argument above proves that every changed subproblem still computes
D_(2,2)(11), and hence the full circuit computes D_(3,3)(22).

Every addition combines disjoint source families. Retaining the first
binary decomposition of an already existing support leaves its integer
coefficient vector unchanged. Pruning unreachable nodes also leaves all
output vectors unchanged. Different factor orders can expose different
previously interned supports, so their equal unshared costs need not give
equal final DAG sizes. The finite checker derives the 30,676 retained
additions from this new DAG. It derives every output vector independently
from the set-theoretic predicate `S intersect T is empty`. This establishes
all 1,540 by 1,540 coefficients, with both zero and nonzero coefficients
included. The count is a certificate of this construction, not a lower bound
on other possible circuits.

The retained compiler gives c+v roles for c additions and v outputs. Here
c=30,676 and v=1,540, giving 32,216 roles. Every compiled operation first adds
its other input roles into its pivot, then adds the pivot into its distinct
fanout roles. It is an invertible integer linear map. Subtract the pivot
from the fanout roles first, then subtract the other input roles from the
pivot to invert it. The slot-alias checks ensure these instructions have
the stated meaning. Thus arbitrary dirty values are permitted in the mixer
and returned by its literal inverse. The clean source-to-output block is
checked separately by full symbolic support replay. The retained twelve-step
signed invocation can therefore reuse this block while cancelling every
initial side value, exactly under its existing boundary contract.

For any active node, let A be the union of ground points of ancestor source
triples, and B the union of reachable target triples. Every such source
triple is disjoint from every such target triple, since coefficients are
positive and every output row has exactly the required support. Thus A and
B are disjoint. The phase enclosure in the pinned
`notes/disjoint-tensor-compression.tex` applies to any such DAG, rather than
only its original factor choices. Source lines, coordinate spaces and target
complements remain nested with the same norm-one residual witnesses.
The retained checker traverses both actual physical orientations of the new
compiled circuit. It checks the case conditions for every transition; it
does not explicitly construct the 104,897 residual bases.

For the complete historical invoice, retain h=22, v=binomial(h,3)=1,540,
intersection-two roles `R2=binomial(h,2)*(4*(h-2)-6)=17094` and h+1 centres.
The source proof gives

```text
R0 = c+v
M = 2c+2*binomial(h,2)*(3*(h-2)-6)
C = J = 4v
S_inv = 4M+2C+4J+18v
S_all = 3v^2*S_inv
W = 2v^3+2v^2*(R0+R2+h+1)
m = h^3
L = 3v^2*h*(h+1)
s = W*m-2v^3+2L
E = 64*(W+m+1)^3
```

These formulas keep every mixer or inverse, source access, injection,
restoration, centre, intersection-two role, join and recursive child in the
same historical contract. The checker evaluates them at the new c, obtaining
`S_inv=409880`, `S_all=2916214224000`, `W=241300813600` and
`s=2569370958862400`. It also checks `2<=s<m^5` and
`4*S_all+8*s+8*W+8*m<E`. Against #981's cited c=30,698, the 22 fewer additions
save 22 roles, 176 steps per signed invocation and
`24*v^2*22=1252204800` steps in the full scalar bound. No new fee is introduced
because the boundary map, frame-enclosure rule and number of calls are the
same. This statement does not transfer the old contract into the selected
P104 supplier or prove its all-size assumptions.
