# Physical T74 on an arbitrary selected support

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.

I compose PR3619's complete physical coordinate router with PR3599's
actual-width normalized T74 root. I retain both exact source exports and their
universal source, native, hosting, refinement and cost premises. I add the
encoded exposure, persistent actual records, complete physical invocation and
literal fallback. I leave scientific admission of the inherited premises open.

## Contract

Fix c,C0,B>0. Supply canonical Count parameters p>=2, n>=1, g>=0, r>=1 and C>=1,
with

    c*p <= n <= C0*p,
    g <= min(n,floor(p^.997)),
    log2(r+1) <= B*p.

Supply exactly g sorted distinct selected coordinates S in a borrowed tape,
each with w=max(1,ceil(log2 n)) bits, least-significant bit first. I number
address positions from the least significant end. The payload contains the
complete C by 2^n rectangle, with r complete p-grid Gaussian coefficients
per address and p+2 bits per signed component. Every coefficient lies in the
unit disk. Its original bit volume is

    V=2(p+2)*C*2^n*r.

I return Q_p(H0_S x), where H0=[[1,1],[1,-1]]/2 acts on the selected
coordinates and Q_p truncates each component toward zero to the p-grid.
I obtain error below sqrt(2)*2^-p per Gaussian coefficient.
I preserve the borrowed payload and descriptors and return a distinct protected
p-grid output. I restore each child's inherited owned-work baseline and erase
my wrapper's scratch bodies and markers. The caller consumes output before
reuse. I retain the predecessors' successful-input contract.

Under the two retained source contracts, put

    alpha=99827101/100000000,
    tau=332353/332929.

For g>=1 I obtain

    O_(q,c,C0,B)(V*(g^alpha*log2 p + (g+1)^tau*(log2 p)^(1+tau))) time,
    O_(q,c,C0,B)(V)+F_q space.

For g=0 I copy the complete packet and validate the empty descriptor. I use
the same upper bound after interpreting its first term as zero. I do not
absorb the extra logarithm uniformly into the actual-g root term. I do not
infer a multiplication exponent from this local composition.

## One authenticated class cohort

I open PR3599's active T74 context as the sole runtime owner. I authenticate
PR3619's official export, then its retained PR3608 export and both nested
Compact/ordinary-rate exports. I invoke authentication/extraction hooks only;
I do not open another cold runtime inside the active T74 namespace.

I compare all 21 Compact package files and all 15 external Compact inputs
with the active T74 cohort. These include the two Compact predecessor archives.
I compare all 23 ordinary backend files with the retained rate source. I check
the actual imported module paths and Count, Tape, CompactEngine and SparseEngine
class identities. I register a separate sparse/router context containing the
active runtime modules. The T74 context's `source` field is a path; the sparse
context's `source` field is the backend module. I preserve that distinction.

I compile two fresh retuned native instances in this cohort, one for each
unchanged owner. Both use Profile(1,577). Their constructors retain exclusive
ownership of their Binary/native work. I include both fixed inventories in F_q;
I do not pass an already-owned native into a constructor that requires freshness.

## Encode the exposure

For g>0, set

    ell=ceil(log2 p)^2,
    K=floor(g^(1/500)),
    E=[0,ell),
    T={ell+jK: 0<=j<g}.

I require the complete span [ell,ell+gK) inside the address rectangle. I map
the ordered S list to T, then map sorted T outside S to sorted S outside T.
I fix the complement. The resulting permutation Pi acts within S union T,
whose size m is at most 2g. Its listed support includes fixed points, as the
router permits. I construct its sorted source/image table by scanning address
coordinates, not payload addresses. Repeated encoded membership scans and
complement ranks use fixed tapes and Count arithmetic.

I choose a complete ell-bit block U disjoint from S union T union E. I use
the retained sorted gap search on Pi's entire listed union. If the complete
target span or such a block does not exist, I execute the literal branch below.

On the composed branch I physically exchange U and E through the router's
existing B1 engine. Call that exchange W. Since W fixes T and Pi fixes U,
the conjugate Pi'=W*Pi*W fixes E and sends W(S) to T. I encode Pi' on the
remaining prefix after subtracting ell from both coordinate fields. I sort
this forward table by source, then swap its columns and sort again for the
inverse table. Swapping columns alone would not preserve the required source
order.

The disjoint blocks U,E imply n>=2ell. Therefore N=n-ell>=n/2>=c*p/2 on every
accepted composed branch, including finite sizes below the eventual cutoff.

## Keep actual records throughout the root

After the physical W swap, I group the complete suffix E into coefficients:

    N=n-ell,
    r_eff=2^ell*r,
    R_eff=2(p+2)*r_eff,
    C*2^N*r_eff=C*2^n*r.

I expose the prefix by Pi', call the actual root with

    precision=p, selected=g, left=N-gK, right=0,
    coefficients=r_eff, outer_rows=C, residue=0,

then route the prefix by the inverse table. I undo the record grouping and
execute W again. The root fixes the unselected prefix coordinates. Conjugation
therefore gives H0 on the original S coordinates and fixes the others.

I keep r_eff unchanged across the root call and its descendants. It satisfies

    r_eff >= 2^((log2 p)^2),
    log2 r_eff <= (B+13)*p,

using ell<=(1+log2 p)^2<=13p. Thus I supply PR3599's actual coefficient
multiplicity premise. I do not replace it with a declared length or a fixed
coarse-label slice. I preserve the full complete address ranges.

Both router calls receive only the N-bit prefix and opaque R_eff-bit records.
Their own temporary suffix preparations occur inside that prefix and end before
return. They never divide or reinterpret the persistent external E coefficients.
The root returns the original p-grid component format, so inverse routing
receives the same record boundaries as forward routing.

## Literal fallback with one effective truncation

I cannot truncate to the original p-grid after each single-bit root: the
successive errors can change the final p-grid answer. Instead I first expand
every component to precision P=p+g by inserting g actual low zero bits, keeping
signed width P+2. For each original selected position s I call the unchanged
actual-width root with

    precision=P, selected=1, left=n-s-1, right=s,
    coefficients=r, outer_rows=C, residue=0.

Each call is direct: d=K=1 and Q0=3G>1. I retain its exact
phase/C/phase/normalizer endpoint before final grid conversion. The Gaussian
leaf rejects inexact halving and the normalizer rejects nonzero discarded
normalization bits. Their signed-headroom conditions remain inherited premises.

After t exact H0 axes the coefficients lie on the 2^(-(p+t)) grid and remain
inside the unit disk. For t<=g this is a subgrid of the P-grid. Hence each
one-bit root's final grid conversion discards only zeros. Its return is exact
on the P-grid. This proves the induction from exact arithmetic and grid
divisibility, not from the weaker Euclidean approximation estimate.

After the g calls I truncate once from P to p, toward zero componentwise.
Each component changes by less than 2^-p, so the Gaussian error is below
sqrt(2)*2^-p. This final truncation preserves the unit disk. The composed
branch inherits the retained common-grid height induction and exact root
endpoint before its final truncation. Componentwise Q_p commutes with its
surrounding record permutations. I therefore obtain Q_p(H0_S x) on both
branches, with no additional error or amplification. In particular, if the
ideal selected transform already lies on the p-grid, I return it exactly.
I use the predecessor's exact-half/final-only truncation argument, not merely
its Euclidean error estimate, for this subgrid conclusion.

## Complete cost and the geometry cutoff

On the composed branch the two external ell-bit B1 swaps cost
O_q(V*(1+ell^tau)). Each router receives a prefix between c*p/2 and C0*p,
listed support m<=2g<=2p^.997 and record length with logarithm O(p).
PR3619 therefore charges each complete router call by
O(V*(g+1)^tau*(log p)^(1+tau)). PR3599 charges the actual root by
O(V*g^alpha*log p). Since 2tau<=1+tau, the router term also pays the external
suffix swaps. I include returned-output copying and disposal.

The encoded planner scans at most n coordinates and uses nested scans of
O(g log n) metadata. Its support extension, validation and metadata-only radix
sorts have a fixed polynomial cost, conservatively O(p^8), in this domain.
I pay this with the original complete volume V>=2^{c*p}. I keep arbitrary C:
global extents and counter initialization may cost a fixed polynomial in
p+ceil(log2(C+1)), which V also absorbs. I keep that quantity outside repeated
per-record phase and repair work. Those computations use local row addresses;
the retained ripple counters have their amortized traversal bounds.

For uniform fallback payment, set

    c1=min(c,1),
    L=ceil(log2(672/c1)),
    P*=2^(1024(L+11)).

PR3619's gap estimate gives n>2(m+1)ell for p>=P*, since m<=2p^.997.
It supplies U disjoint from the support union and E. Also

    gK <= p^(499497/500000),
    1-499497/500000 = 503/500000 > 1/1024.

For x=log2 p>=1024(L+11), this gives
gK<=p/2^(x/1024)<c1*p/4. The same gap estimate gives ell<c1*p/672.
Therefore ell+gK<n. Every failure of the external geometry has p<P*.

On that bounded range, P=p+g<=2p. I retain a literal invoice
O_q(V*g*poly(p)) for the g direct one-bit roots, including their generic
phase/address scans, grid lifting, descriptor setup and final truncation.
I do not invoke the long-record root rate for these short-record calls.
Since p and g are bounded by source-dependent constants on this branch,
I obtain the displayed complete wrapper bound with a constant depending on c.

## Space and ownership

The wrapper owns 256 scratch roles, a GridBoundary and one protected output.
I use a fixed vocabulary of numerical fields and fixed tapes for selected
positions, target positions, the support union, and forward/inverse descriptors.
I allocate no role per selected coordinate. A conservative 128-lease budget
covers the planner's retained fields and nested lookup/arithmetic frames,
including the largest radix-sort frame. The physical execution uses fewer
simultaneous wrapper roles; I count the two children in their own inventories.

I suspend the wrapper allocation scope during each child call and pass
borrowed physical views. On return I copy the protected child output into an
owned wrapper stream, consume that child output and erase its return marker,
then consume the old owned packet. I require closed, consumed children before
reuse. I preserve each source child's compiled marker/template baseline.

On the composed branch I retain the two children’s linear workspace bounds.
On the literal branch the expanded P-grid packet is at most twice the original
volume. Each direct root has d=1 and O_q(p) working width, fixed streams and
local address scratch; it requires no exceptional-record sort or recursive
stock. These yield O_q(V) occupied space even with short original records.
Metadata takes O(p) cells and global Counts take O(p+log(C+1)) cells. I include
both fixed native compilations in F_q. During reuse I charge maximum preceding
visited extents; clearing a simulator tape does not shrink its backing array.

## Scope

I supply the complete arbitrary-support invocation under the pinned source
contracts. Bounded q=2 fixtures reduce root guards/reservations and, where
declared, the external suffix width. I retain the standard production formulas
in the executable planner and proof. I do not claim that these finite fixtures
execute production GL64/O(73,2) packets or prove their universal admission.

A future global transform must include its number of calls, precision choices
and complete error budget. Raw-H scaling, the enclosing integer multiplication
assembly, packing and both supplier obligations remain separate. I leave the
selected frontier unchanged.
