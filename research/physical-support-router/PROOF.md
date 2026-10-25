# Complete physical support router

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.

I implement the support router from Vlado Vojdanovski's PR1673 around the
encoded sparse XOR batch in PR3608. I retain the arbitrary-coordinate routing
lineage of RaD/hipotures's PR20, recorded by Zhihao Chen in PR23. I claim a
source-relative executable composition and its complete invoice. I retain the
universal ordinary-callee, source and machine-refinement arguments as premises.

## Contract and quantified conclusion

Supply canonical Count tapes for address width n>=1, precision p>=2, listed
support size 0<=k<=n, position width w=max(1,ceil(log2 n)), positive record
width R and arbitrary positive outer-row count C. Supply exactly k pairs of
w-bit unsigned positions, least-significant bit first within each field.
List the source positions in increasing order. Require distinct image positions
and equality of the source and image sets. I extend the listed map by the
identity outside that set; listed fixed points are permitted. I number address
coordinates from the least significant end and use

    output_coordinate[pi(i)] = input_coordinate[i].

Supply the complete C by 2^n rectangle of opaque R-bit records. Its volume is
V=C*2^n*R. The caller supplies distinct borrowed payload/descriptor ports and
canonical parameter ports at their origins. I return a distinct protected
output, preserve those inputs and erase owned work on successful return.
The caller consumes the output before reuse. I retain the predecessors'
successful-input contract, without interruption recovery.

For correctness I need the retained exact B1 and sparse-batch endpoints.
For the faster rate I additionally fix c,C0,A0>0 and require

    c*p <= n <= C0*p,
    k <= 2*p^(997/1000),
    log2(R+1) <= A0*p.

Assume the retained completed binary B1 bound, uniform over arbitrary complete
spectator cardinalities,

    T_B1(v,h) <= B_q*v*(1+h^tau),
    tau=332353/332929,

and its linear workspace bound plus fixed compilation F_q. In PR3562 I give the
retuned exponent argument for PR3608's actual ordinary cohort. I also retain
PR3608's sparse guard, repair, refinement and complete cost arguments. I prove

    T_router = O_(q,c,C0,A0)(V*(k+1)^tau*(log2 p)^(1+tau)),
    S_router = O_(q,c,C0,A0)(V) + F_q.

The functional program accepts valid inputs outside this rate domain. I retain
their literal or unabsorbed physical invoice instead of claiming the displayed
rate there. I do not derive a multiplication theorem or change the selected
frontier.

## Two involutions and the literal route

I validate the descriptor with repeated scans. I then traverse each cycle from
each listed vertex, keeping one cycle on a reusable tape. I emit edges only
when the starting vertex is the least coordinate of that cycle. For a cycle
with pi(c_i)=c_(i+1 mod m), define

    J0(c_i)=c_(-i mod m),
    J1(c_i)=c_(1-i mod m).

I execute J0 first and J1 second. Then J1(J0(c_i))=c_(i+1 mod m).
For each involution I emit an edge only when i is smaller than its partner
index. I obtain disjoint transpositions, at most floor(k/2) in each matching.
I handle identity before constructing any positive reservoir width.

On the literal branch I execute these at most k single-coordinate swaps
through completed B1 with h=1. I charge O_q(V*(k+1)) plus metadata setup.
I preserve the same cycle orientation on both routing branches.

## Actual record preparation

Set l=ceil(log2 p), ell=l^2, G=4*l+6, K=64*G and
H=floor(k/2)*G for a nonidentity permutation. I first require n>ell and
N=n-ell>=10H. I search for a contiguous ell-bit interval U outside the
listed support and disjoint from the actual suffix E=[0,ell).
I search from ell upward through the sorted support, advancing a candidate
past any coordinate that intersects it. If either test fails, I use the
literal route.

On the fast branch I physically exchange U and E using completed B1; call
this coordinate exchange W. I conjugate each listed edge by W and subtract
ell. Since pi fixes U pointwise, W*pi*W fixes E pointwise. I can therefore
group the actual suffix into opaque records of width

    R'=2^ell*R,   N=n-ell,   C*2^N*R'=V.

I route the conjugated permutation on the remaining prefix. At the end I
restore the original record interpretation and execute W again. The full
coordinate map is W*(W*pi*W)*W=pi. I do not manufacture record width by
declaring a longer scalar or fixing a coarse label.

For any disjoint blocks [a,a+h),[b,b+h) with a+h<=b and b+h<=n, I call B1 with

    width=h,
    prefixes=C*2^(n-b-h),
    gap=2^(b-a-h),
    suffix=R*2^a.

These are actual complete extents. The preceding and intervening cardinalities
may equal one. The inherited B1 contract already pays its binary padding,
restriction and cleanup and does not require long records. Thus I can use it
for the two width-ell preparation/restoration swaps before invoking the
long-record sparse-batch bound.

## Reservoir placement, recoloring and complete matching execution

In most-significant order on the N-bit prefix, choose three reservoirs
[0,3H),[3H,6H),[6H,9H). An edge has two endpoints, so it avoids at least one
reservoir. I assign it to the first reservoir it avoids. Within each matching
I process the three resulting cohorts in order.

For one cohort, place the reservoir's three H-bit chunks at u=[0,H),
t=[H,2H),b=[N-H,N). Since N>=10H, b starts at or after 9H. For reservoir 0,
the first two chunks already occupy their destinations; I omit those identity
swaps. For reservoirs 1 and 2, the three source chunks and destinations are
disjoint. I execute at most three H-bit swaps and undo them in reverse order.

An edge avoiding the chosen reservoir lands entirely in y=[2H,N-H) in
most-significant order. In the code's least-significant convention this is
[H,N-2H). I apply the actual block-exchange map to both endpoints after each
placement, then subtract H. I recompute the canonical position width for
Y=N-3H. I color these new target coordinates, not their earlier positions.

I execute each transposition with three XOR stages: a^=b, b^=a, a^=b.
Within a stage the sources are distinct and disjoint from the target set.
For targets j with j+K<=Y, I group by j modulo K and sort only the pair
metadata by target. Equal-color target guards are disjoint. Every batch has
at most floor(k/2) pairs and therefore requires at most H compact bits.
In PR3608 I implement exactly these encoded sparse XOR endpoints, including their
full exceptional-record repair. I keep the actual full H in its bill.

For a target without a complete guard, I execute an exact CNOT. There are
fewer than K such target positions per stage. I avoid an unsigned subtraction
Y-K by testing j+K<=Y. The CNOT uses the retained four-bucket complete-row
permutation; I iterate arbitrary C outer rows with an encoded counter. I
convert its two positions from least-significant to left-numbered coordinates.

I process distinct edges in any cohort/color order because the complete XOR
stage has disjoint source and target sets. Within a matching, disjoint
transpositions commute. The prefix operations do not touch the grouped
suffix; the inverse placements restore the surrounding address interpretation.

## Encoded execution and fixed physical ownership

I compile the plan onto one binary tape with six fixed three-bit opcodes.
I encode numerical fields with the validated position width; batch pairs use
the recomputed y width. Counts of nonempty batch pairs, positions and block
widths fit these fields. I keep variable cycles, matchings, cohorts and sorted
metadata on a fixed number of tapes, not in size-dependent host collections.
The interpreter checks the exact instruction ending and executes the complete
prepared/restored packet.

I construct one SparseEngine and retain its existing Binary and native cohort.
The router owns 256 scratch roles and one protected output. I suspend only the
router scope before a Binary or SparseEngine call. I pass borrowed physical
views, copy the protected child return into router-owned scratch, erase that
child output and then consume the previous owned packet. I call neither child
until its predecessor output has been consumed and its work has closed.

For a conservative fixed-role proof, I allow 24 leases for persistent plan,
instruction and matching fields; 32 for nested scans, two pair contexts,
cycle/reflection and reindex frames; 32 for arithmetic intermediates; and
24 for the packet interpreter, row layout and exact-gate buckets. The sum is
112, below 128 and the allocated 256. Planning and physical execution do not
overlap their deepest frames. I count child pools separately through their
retained bounds. The measured peaks are only finite controls for this count.

Each metadata stream has O((k+1)w) cells: each matching edge occurs in at most
three XOR stages, and I emit only nonempty batches. I reuse color buckets.
I bound physical payload streams by V and the inherited linear child bounds.
Global cardinality fields occupy O(p+log(C+1)) cells in the rate domain.
For simulator reuse I charge each role's largest preceding visited extent;
erasing a body does not shrink its retained backing array.

## Complete time invoice

Let D=2kw and A=2+p+n+D+ceil(log2(R+1)). I obtain D=O(p) from the support
cap and n<=C0*p: p^(-.003)*log p has a finite supremum. Thus A=O(p).
One repeated pair read, including rewind, skip, arithmetic and disposal, costs
O(A^2). I use O(k^2) lookups for validation, O(k^3) for rediscovering cycles
and O(K*k^2) for cohort/color scans. Metadata radix sorting adds a polynomial
in D and w. A conservative O(p^6) allowance covers the actual planner.

Before grouping, V>=2^(c*p). For each fixed j>0,

    p^j / 2^(c*p) <= (j/(c*e*log 2))^j.

I can therefore pay that planner allowance with O_c(V). I handle arbitrary
C separately: for L_C=ceil(log2(C+1)), L_C^j/C<=2^(j+1)*j!. Any fixed-degree
global setup polynomial in p+L_C also has a uniform O_c(V) charge. In the
actual code, only global extents and outer counters involve C. The retained
counter traversal costs O(C+L_C); the sparse offsets and repair keys use local
row addresses, so their repeated per-record arithmetic does not contain L_C.

On the fast branch I have at most 18K sparse batches, 216K internal H-bit B1
swaps, 36 placement/restoration H-bit swaps, 18K exact tail CNOTs and two
ell-bit preparation/restoration swaps. I include output copies and disposal.
The sparse source invoice uses M=C*2^N, R', and local A'=O(p):

    12*sum_rows T_B1(2^N*R',H)
      + O(V + M*(A')^6 + delta*M*A'*(R'+A')),
    delta <= min(1, r*(2/2^G + 8*2^(G-K))),

where r is the actual batch size. With G=4l+6 and K=64G, I retain PR3608's bound
delta=O(p^-3). Since R'>=2^(l^2),

    p^j/R' <= 2^(j^2/4).

I pay the remaining per-record and exceptional terms with O(V) per batch.
I obtain the full fast invoice

    O_q(V*((216K+36)*(1+H^tau) + 2*(1+ell^tau) + K+1))
      + O(poly(p+L_C)).

Substitute H<=kG/2 and K=64G=Theta(log p). Also 2tau<=1+tau because tau<=1.
I obtain the stated fast-rate expression, including actual record preparation.

## Uniform literal fallback

I give an explicit cutoff so that a geometry failure does not hide a second
asymptotic regime. Put

    c1=min(c,1),
    L=ceil(log2(672/c1)),
    X=1024*(L+11),
    P*=2^X.

Here L>=10. For x=log2 p>=X, use .003>1/512 and
2^(x/512)>2^L*(x+1)^2. At X, the latter inequality follows from
2^(L+22)>(1024*(L+11)+1)^2 for L>=10; the logarithmic difference increases
afterward. Hence

    p^.003 > (672/c1)*(log2 p+1)^2.

Since k<=2p^.997 and ell<=(log2 p+1)^2, I get
n>2(k+1)ell. Among the free intervals after E, at most k+1 gaps remain;
if each had fewer than ell coordinates, their total together with E and k
listed positions would be below 2(k+1)ell. Thus an admissible U exists.
The same inequality gives ell<n/672 and, using G<=10(log2 p+1),
12kG<n/2. In particular N=n-ell>12kG>=10H.

Consequently a geometric failure implies p<P*. On that bounded range,

    k^(1-tau) <= 2^((1-tau)*(1+.997*X)) <= 2^(2L+23).

I pay literal O(V*(k+1)) routing with the same target expression, using a
constant depending on c. The identity branch costs O(V) plus its already-paid
metadata validation. I branch on the actual geometry; I do not construct the
cutoff at runtime.

## Remaining obligations

I retain the source-relative B1/sparse universal premises and their scientific
review status. The physical fixtures use q=2's elementary B1 branch and the
explicit compiled G=1,K=5 fixture policy. I check the standard policy through
encoded planning and the written inequalities; I do not execute its enormous
full physical rectangles in those fixtures.

The lower bound n>=c*p matters. A generic actual-width T74 interface gives no
such lower bound by itself. A future enclosing caller must bind its full
address rectangle and online precision, preserve the global coarse ranges,
and pay its root, restoration, error and packing ledger. The offline setup
precision cannot replace the online p in this argument. I leave that combined
caller and the multiplication theorem open.
