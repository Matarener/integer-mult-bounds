# Global loss-space bound for an unchanged owned producer

Let the ambient binary label space be E. Every original independent public
input x_i has entry frame A_i <= E. At any scalar-program instant, a live
register r has current frame F_r and row sum_i m_ri x_i. Define its source
support space L_r = sum_{i:m_ri != 0} A_i. Coefficients may be arbitrary elements
of a characteristic-zero field; cancellation can remove support but cannot
introduce a new input symbol.

The model allows common-frame linear ADD/COPY/SCALE, public inclusion-ascent,
zero owned INIT, owned erasure, and owned inclusion-descent. It excludes hidden
nonascending public transports or native actions that change the literal row
semantics. Every owned descent of rank r is charged by r^t, 0<t<=1.

## Invariant

There exists a global subspace V such that

    L_r <= F_r + V

for every live register. Initially V=0. Common-frame linear operations preserve
the assertion because new support is contained in the union of the operands'
supports. Public ascent preserves it by inclusion. INIT and CLEAR set a row to
zero or remove the field, so cannot violate it.

For an owned descent A -> B with B <= A, choose any vector-space complement W
such that A=B direct-sum W. Replace V by V+W. For the moved field,

    L_r <= A+V = B+W+V.

Other fields' bounds only become weaker. Since dim W = dim A-dim B, after all
owned descents to a chosen cut,

    dim V <= sum_j r_j,

where r_j are their paid ranks. V may be shared by every register and persists
after owned erasures; erasing a register does not erase the global accounting.

If a required output row v appears at frame F, with initial support space L,
then L<=F+V. Projecting to E/F gives

    sum_j r_j >= dim V >= dim(L+F)-dim F.

Thus the total owned-transport moment up to that cut obeys

    sum_j r_j^t >= (sum_j r_j)^t >= [dim(L+F)-dim F]^t,

using subadditivity of x^t for 0<t<=1. Additional ordinary or public transport
costs cannot reduce this owned-only floor.

## Source application

`check_producers.py` pulls the eight exact COPY-source covectors backward
through the source's purely public prefix. Each has 52 nonzero-chart original
inputs spanning rank8; that span is exactly its original eight-dimensional
COPY frame. The copied values are already present before the first owned INIT,
and none of the eight source rows is modified by preceding owned lifetimes.

For owned735, v is source row173 (118 nonzero input coefficients), delivered
up to a nonzero factor at frame593=span(7), which lies in frame559=span(supp v).
Hence dim(L+F)-dim F = 8-1=7. The source uses a single owned MOVE559->593 of
rank7, so it attains the owned-transport floor H7. The total owned-preparation moment for this retained value cannot fall below
H7 by moving COPY earlier, by arbitrary changed ascending public scalar
preparation, or by adding any number of owned preparations/erasures that still
deliver the same value at frame593 and have no offsetting new productive credit.

All eight values individually have the same rank-mass lower bound7 at their
retained final one-dimensional delivery frames. This does not permit summing
the eight separate bounds: V is global, so a redesigned shared protocol could
amortize paid descents across different values. Owned738's source already splits
its rank7 descent to serve intermediate reads, so the scalar H7 floor is not a
claim of optimality for that complete multi-read itinerary.

## Scope

This is a floor for delivering one unchanged scalar value at one fixed frame,
not a bound on the final multiplication exponent. It does not exclude eliminating
that intermediate value, changing its payload, changing delivery frames, reusing
a descent paid for another target, adding productive credits, or a native-bearing
protocol outside the stated row/frame model. The theorem needs no search cutoff
and no fixed original scalar-contact windows.

Prepared with OpenAI Codex assistance; no proof-kernel or independent human
acceptance is claimed.
