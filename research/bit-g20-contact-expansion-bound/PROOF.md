# A source-bound limit for every catalogue expansion

Use the exact PR5512 G20 word, frames, invoice and CALLS.json pinned in
INPUTS.json. Keep its scalar order, productive targets, original input and
output frames, and owned instructions. In each of its 18 full local calls,
choose any one catalogue frame alpha. Move any subset of the 17060
public/public ADD contacts to alpha. Keep the other contacts at their source
frames. Each call can choose a different alpha and a different subset.

Allow every public field interval to use its cheapest finite sequence of
proper nested QUERYs through any of the 645 source frames. All new ordinary
work and all nonrecursive fees can be free. This is a favorable relaxation
of the physical words in the stated family. It includes changes that move
contacts from many old frames at once; it is not a one-ADD or one-block test.

At C=37/10000, the largest possible local paid-moment saving is at most
2862/1000000. Thus every such complete caller has target-minus-paid moment
at most -46255824/1000000. The retained ordinary admission cannot reach
C=0.0037 through this family. No new kappa is claimed.

## 1. Proper native paths and contact graph

The exact rational row spaces of B define the source projectors. Their A
spaces are their orthogonal complements. All 645 physical projector spaces
are distinct. There are 26312 undirected proper nested pairs. An edge from
U to V has rank r=abs(dim U-dim V), where 1<=r<=7. The pinned native frame
induction permits the corresponding QUERY. No rank8 child is granted.

For every required rank r, the checker proves with integer powers that

    w_r / S <= r^(9963/10000) < (w_r+1) / S,  S=1000000.

Decimal arithmetic only proposes w_r. The proof is the exact comparison
of w_r^10000, S^10000*r^9963 and (w_r+1)^10000.

Let d(U,V) be the shortest path distance for the integer edge costs w_r.
Nonnegative distance potentials are checked on every native edge, so every
finite physical path costs at least d(U,V)/S. Distances are symmetric and
satisfy the metric triangle inequality. The native catalogue is finite;
projectors outside it are not covered.

A vertex is an ADD contact or a fixed public entrance/exit. Two consecutive
contacts on one public field give one graph edge, with multiplicity if two
fields give the same edge. The graph has 37299 field intervals. All owned
contacts and original boundaries are fixed. Exactly 17060 contacts can move.
The source has 2862 paid public QUERYs. Every public normalized row stays
nonzero, so a free whole-zero public path is not omitted. Exact replay checks
all 660 RAW/DIRTY columns and the final scalar endpoint.

The actual source public cost is at most the sum of its upper edge tariffs.
That sum exceeds the integer-distance contact cost by exactly 2862/S.
This accounts for every path and every rounding error, including unchanged
field intervals. Owned queries are unchanged.

## 2. A flow bounds every subset at once

For a fixed alpha, a movable vertex chooses its old label a (state 0) or
alpha (state 1). For an edge with old labels a,b, its four integer costs are

    E00=d(a,b), E01=d(a,alpha), E10=d(alpha,b), E11=0.

Their submodular difference E01+E10-E00 is nonnegative by the triangle
inequality. Use a directed arc from the first vertex to the second with
that capacity. Add E10-E00 to the first vertex's unary change and -E10 to
the second. Relative to the old cost E00, these terms give all four costs
exactly. A fixed endpoint gives only a unary term. Parallel edges retain
their multiplicity.

For a unary change delta, use a source arc of capacity delta when delta>0,
or a sink arc of capacity -delta when delta<0. Add min(0,delta) to the
constant. State 0 lies on the source side of a cut. Thus every subset's
integer cost change is exactly its cut capacity plus that constant.

FLOWS.bin.gz supplies a nonnegative integer flow for each of the 645
choices of alpha. The checker reconstructs the whole graph and verifies
every arc capacity, every internal conservation equation and the source
and sink totals. In every case, flow value plus constant equals zero.
Every cut has capacity at least this feasible flow. Hence every subset's
integer lower-cost change is nonnegative. The proof does not trust a solver
status, a floating-point optimum or a reported minimum-cut value.

Together with Section 1, this proves that the actual paid-moment reduction
is at most 2862/S per local call. Each of the 18 calls can be changed
independently, so the complete gain is at most 18*2862/S. Integer tariff
bounds give source complete moment at most -46307340/S, which proves the
claimed complete upper bound -46255824/S.

## 3. Higher working exponents do not evade the gate

Write t=1-C and divide the complete moment by 8^t. All changed paid ranks
are at most seven. Each retained high paid job of rank r>=14 has a matching
target of rank r+1 with the same multiplicity. The other targets are 72
rank4 jobs, 7614 rank8 jobs and 222 rank127 jobs. The checker verifies this
structure directly from the exact invoice.

For 0<=t<=1, each negative paid term -p*(r/8)^t with r<8 has nonnegative
t derivative. Each matched high pair ((r+1)/8)^t-(r/8)^t has positive
t derivative, because z^t log z increases for z>1. The rank8 target term
is constant. The only negative target derivative is from 72*(1/2)^t,
whose magnitude is at most 72 log 2. The rank127 derivative is at least
222 log(127/8), which exceeds 72 log 2. Thus the normalized complete
moment strictly increases with t for every nonnegative proper-query
histogram in this family. It strictly decreases with C. Failure at 0.0037
therefore excludes every larger working C through 1, not just one sample.

## 4. Certificate and limits

The binary file starts with ASCII G20FLOW1. For each sorted frame ID, two
little-endian unsigned 32-bit words give the frame ID and entry count.
Each following pair gives an arc index and its positive integer flow.
Arc order is the deterministic order emitted by network(). Missing arcs
have zero flow. Duplicate, missing, extra and invalid records are rejected.
A changed flow value is a required negative control.

SciPy 1.15.3 first supplied the search, with every resulting integer flow
checked. OR-Tools 9.14.6206 exported the compact certificate through a
separate solver. The standard-library verifier needs neither solver.
Optional generation is separate from registered replay. The certificate
is author checked, not independently accepted or formally kernel checked.

New projector frames, several new labels in the same move, changed scalar
order, address-dependent recoders, changed owned contacts, changed targets
and a new producer remain open. A sequence of neutral or small moves can
reach a different source word; this theorem is pinned to the source word
and does not classify such sequences. The native frame induction and
caller wiring are credited source premises, not newly admitted theorems.
