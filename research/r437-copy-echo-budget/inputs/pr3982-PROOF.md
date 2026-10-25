# Parabolic COPY with batched pivot and graph routing

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.

## Result and boundary

For m=64, r=7 and every split rank-seven projector over Z/q^w, the construction
below replaces PR3950's alternate generic SL64 word by **8,036 ordered scalar
ADD slots per column and 196 ordinary width-f interchanges**, surrounding the
same single reversed child of width 7f. PR3950's alternate has 41,832 of each.
All slots, including zero coefficients, are charged. This is a uniform algebraic
construction and a **conditional relative caller/cost theorem**; an encoded
physical compiler has not been implemented. The original R437 good/fallback
implementation is a different construction and its tariff is not altered.

The change combines the parabolic stabilizer of a projector with small fixed
permutation networks. It removes unnecessary internal image/kernel basis work
and shares routing across commuting graph passes and mutually exclusive pivot
stars. Generic conjugacy, local-ring split projectors and elementary matrices
are credited predecessor mathematics, not new claims of this package.

Even the reduced positive ordinary term is not absorbable from the pinned B1/B2
upper tariffs at the R437 target scaling. The optimistic decision is therefore:
retain this smaller constructive relative bill, then stop supplier expansion
until a cheaper complete ordinary adapter or a different consumer is supplied.
This does not lower-bound actual runtime or exclude the original algorithm.

## 1. Domain and a principal chart that always exists

Fix an odd prime q, w>=1, R=Z/q^w, A=q^w, m>=2 and 0<r<m. For the application,
m=64 and r=7. Let P be a split rank-r projector and g invertible over R, and
put Q=gPg^-1. Let H=diag(h_i) consist of arbitrary units; h_i may depend on
physical header and column, but not on body addresses or fresh unused rows.
The requested two-bank address map, with tail coordinates reflected, is

    D_H(Q)=diag(H,I) [[I-Q,Q],[Q,I-Q]] diag(H^-1,I).

Every Boolean source function is allowed, including arbitrary correlated dirty
captures. Equal field-header values at distinct physical prefix ordinals remain
distinct. There is no SOURCE projection or clean-data assumption.

A principal r-by-r minor of Q is a unit. Indeed a split idempotent is similar
to E=diag(I_r,0), so its characteristic polynomial is t^(m-r)(t-1)^r. Its
coefficient of t^(m-r) is (-1)^r times both 1 and the sum of all principal
r-minors. Reducing modulo q, their sum is 1. At least one is nonzero. This
argument also works when q divides r; trace is not used as a rank certificate.

Choose a sorted subset S=(s_0,...,s_(r-1)) with unit principal minor, so
 i<=s_i<=m-r+i. One effective deterministic rule is the first unit subset in
lexicographic order. This fixed-m search can be very expensive: at m=64,r=7
there are binom(64,7) subsets. It is charged in gamma below, not called free
or a practical large-instance implementation. No enumeration of GL64 is needed.
The same S selected modulo q works at every high lift and precision.

## 2. Fixed-support pivot stars

For i=0,...,r-1 and every k in i+1,...,m-r+i, let e_ik=1 if s_i=k and 0
otherwise. Use three stars, in chronological left-action order:

    all E_(i,k)(e_ik), then all E_(k,i)(-e_ik),
    then all E_(i,k)(e_ik).

At most one flag is nonzero in this entire i-stage. Consequently this is either
identity (s_i=i) or the signed swap (x_i,x_s)->(x_s,-x_i). Grouping the triples
into stars is legal precisely because of that mutually exclusive flag property;
it would be false with two active candidates. Earlier stages cannot move s_i,
which is strictly larger than every earlier s_j. The product J therefore moves
the original S to the first r coordinates and has determinant one.

The schedule has 3r(m-r) scalar factors with support independent of S, q, w,
header and column. No conditional physical permutation or low-class regrouping
is assumed: only scalar coefficients carry the pivot flags. All zero factors
remain emitted and paid. This addresses a source-dependent routing issue that
merely choosing a matrix basis would leave unresolved.

## 3. Quotient out the stabilizer

Write Q'=JQJ^-1 in blocks [[A0,B],[C,D]], with A0 an invertible r-by-r matrix.
Put X=C A0^-1 and Z=-B. Define

    L_X=[[I,0],[X,I]], U_Z=[[I,Z],[0,I]], T0=L_X U_Z.

Then Q'=T0 E T0^-1. Here is a proof over the local ring, without a probabilistic
chart hypothesis. The first r columns of Q' are independent modulo q; since
im(Q') is a free direct summand of rank r, they form an R-basis of that image.
Thus D=C A0^-1 B=XB. Idempotence gives A0^2+BC=A0, hence A0+BX=I. Multiplying
out T0 E T0^-1 gives blocks I-BX, B, X(I-BX), XB, exactly Q'. Both L_X and
U_Z have determinant one; each is r(m-r) commuting elementary shears.
Set T=J^-1 T0, so Q=TET^-1 and det(T)=1.

This uses only the image/kernel splitting, rather than a full arbitrary GL64
basis. The stabilizer degrees of freedom do not need to be implemented.

## 4. Ancestor units and kernel-only normalization

Let H'=J H J^-1=diag(d_i). This is diagonal because J is a signed
permutation. Define the determinant-one diagonal

    D*=diag(d_0,...,d_(r-1), (product_(i<r) d_i)^-1, 1,...,1),
    Z_h=H'^-1 D*.

Z_h is identity on every image coordinate; its arbitrary unit kernel entries
are allowed. The desired head and tail conjugators are

    U_t=T=J^-1 T0,
    U_h=H T Z_h
       =J^-1 (H' L_X H'^-1)(H' U_Z H'^-1) D*.

Both have determinant one. The conjugated graph matrices have the same supports
and their coefficients are multiplied by d_target/d_source. Kernel ancestor
weights remain present in these coefficients; they have not been discarded.
The right compensation Z_h fixes every image coordinate, so diag(Z_h,I)
commutes with D(E). Therefore

    K=diag(U_h,U_t),   K D(E) K^-1=D_H(Q).

Normalizing an image column independently would generally change the weighted
swap. Here only the kernel compensation is free. This image-only diagonal
choice emerged in the coordinating agent's cross-review of the first all-axis
normalization; it removes unnecessary kernel diagonal factors. The result and
all checks remain in this same assisted research session.

For any unit a, diag(a,a^-1) on coordinates (i,k) is four shears:

    U(1) L(a-1) U(-a^-1) L(-a(a-1)).

This displayed product uses ordinary matrix multiplication; chronological left
actions run right to left. Its off-diagonal entries vanish and its diagonal is
(a,a^-1). Pair each image coordinate i<r with the single kernel hub k=r.
Their pair diagonals multiply to D*, giving 4r scalar factors, with two in each
orientation. This identity is checked separately over all units of several
local rings. Unlike implementing an entire arbitrary SL_m diagonal, no factors
are emitted for the other kernel coordinates.

## 5. Fixed permutation networks for ordered ADD

An ADD is assumed available only when the source block precedes its target
physically. Blocks contain f atoms; the coefficient for each column comes from
unchanged saved metadata. Ordinary block interchange is a **completed**, same-q,
source-preserving primitive that preserves the entire intervening spectator,
returns its heads and restores owned work. Its full cost is b(v,f).

A reverse individual shear can be implemented by swapping its two whole blocks,
performing the ordered ADD on the relabelled coordinates, and swapping back.
This is used for the diagonal factors and costs two ordinary calls per reverse
factor. It is never identified with the central reversed child.

A whole reverse pivot star has centre i and arms in i+1,...,m-r+i. Swap i with
its largest arm, execute the entire relabelled star, and swap back. All arms
then precede the centre (or the opposite relation in the reflected bank).
There are exactly two ordinary calls per reverse star, regardless of the
number of arms. The routing permutation is fixed, even if every coefficient
is zero. The one-hot property is needed for the algebraic regrouping, not
for the routing operation itself.

For a reverse graph pass, put t=min(r,m-r). Swap i with m-t+i for i=0,...,t-1,
execute its relabelled shears, then undo these t swaps. The images now lie
entirely after the kernels (or entirely before them in reflected order), so
every ADD is ordered. This costs 2t ordinary calls per reverse graph pass.
It preserves the original layout at the pass boundary and acts pointwise on
all external spectators, fresh rows and physical prefix ordinals.

Within this permutation-only route-and-return model, t swaps per direction
are optimal for reversing the complete image/kernel order: the smaller group
must all leave its original side and a transposition moves at most one of its
members to the other side. This narrow claim does not lower-bound all COPY
implementations. Exhaustive permutations through dimension seven check it.

Head/tail physical orders are opposite. Across both banks and both directions,
there are 6r reverse pivot stars and four reverse graph passes. The diagonal
appears only on the head, in both directions, and has 4r reverse scalar
slots in total. Hence the exact fixed emitted counts are

    scalar ADD factors = 4[3r(m-r)+2r(m-r)]+2[4r]
                       =20r(m-r)+8r,
    ordinary calls     =20r+8 min(r,m-r).

At (m,r)=(64,7), these are **8,036** and **196**. Breakdown of ordinary calls:
84 pivot, 56 graph, 56 diagonal. There is one reversed child, not one per
prefix. At fixed header/column some coefficients can vanish; the invoice does
not omit them. The interpreter checks every emitted ADD's physical direction
and executes every ordinary swap, including routing back.

## 6. Full caller, consumer and relative bill

Use the complete packet shape and ownership contract of PR3950:

    [Z physical prefixes][U unused fresh rows][B][A^n head][G][A^n tail][S],
    n=64f+delta, 0<=delta<64, v=Z U B G S A^(2n).

Clone the borrowed complete arbitrary source. Apply the complete address
permutation using the two conjugation words and one reversed 7f child, return
the owned result to the actual COPY private port, and preserve it through all
63 literal XOR readers. Release every intermediate only after its last reader.
At the equality guard, clear the private output and reset its port.

Matrix words are chronological left actions on address vectors. Pullback
implementation reverses the entire vector-event order. That reversal preserves
the physical direction and coefficient of each emitted ADD; it is not the
operation of negating a factor. Inverse conjugators separately reverse and
negate their scalar words. The finite payload checker executes these primitive
pullbacks and all 63 dirty consumers, rather than checking only matrix rank.

The central child's spectators are B'=B, G'=G A^(114f+2delta), S'=S, with
fresh rows U and all Z physical prefixes. Their volume equals v exactly and
keeps the peeled atoms/external gap in their original coordinate order. The
child is one complete call outside any prefix loop. For the inherited stock
K0=269241600 |GL64(F_q)| q^(4096(w-1)) and
D(n)=0 below64, otherwise1+D(42 floor(n/64)), the standard parent stock
 t K0^D(n) leaves U=t*9475*K0^(D(n)-1). Since 7f<=42f<n, child divisibility
follows. This is reuse of the stock implication; it does not prove the original
producer's stock coefficient or authorize replacing its source program.

Let t_R(v,7f,w) be the full completed reversed-child cost. Let gamma include
principal-chart search, matrix/weight coefficient generation and recomputation,
Counts, source/program authentication, numerical work erasure and metadata
preparation not included in the completed primitives. Let C_scan cover actual
linear copying, scalar ADD, transfers, rewinds, releases and disposal. Then

    C_residual <= t_R(v,7f,w) + 196 b(v,f)
                     + C_scan,q v(8036f+196+3) + gamma.          (1)

There are at most 8036f+196+1 intermediate releases; this upper bound is paid in
the scan term. Borrowed source is never cleared. For the literal COPY episode,
append 63 X(v) for the completed XOR readers and the actual outer owner gather,
route/scatter, directory producer and protected return charges if those have
not already been charged by the caller. No reader recomputes the residual;
no reader's arbitrary incoming target is assumed zero.

Conditional on fixed reusable tape inventories, a conservative visited-cell
reserve is

    2v + S_R(v,7f,w) + S_B(v,f) + S_ADD(v) + M_coeff + F_q,

where each backend reserve is a whole-run lifetime maximum on its fixed
reusable inventory, including owned output, numerical work, parking and
blank-but-visited cells. The two volume buffers must likewise use fixed reusable
inventories; M_coeff and F_q include whole-run coefficient and finite-control
backing. Per-call live occupancy does not establish these bounds. If a backend
allocates disjoint tapes across occurrences, their lifetime backing must be
summed instead. Sequential cleanup does not justify taking a maximum
across disjoint tape inventories. There is no stored length-f array of matrices;
coefficients can be recomputed from header and column, with recomputation time
included in gamma. Successful cleanup is covered by the named contracts;
interruption recovery is not proved.

No hidden absorption is made in (1). Under the additionally admitted backend
and root/history metadata premises one may substitute
b(v,f)<=C_B v(fw)^p+E_B and absorb the justified scan/preparation terms. However
the 196 C_B v(fw)^p contribution remains, as does 196 E_B until separately
absorbed. This package does not prove those physical premises or implement a
source-bound alternative SelectedBinding.

## 7. Cost gate, evidence and remaining obligations

For c_R=1736646042038446578551/10^24, n approximately e and w approximately
e^c_R, the retained B1 and B2 rates give (1+c_R)(1-a_B)-1>0. Multiplying their
upper bound by 196 instead of 41832 does not change its exponent. Thus this
new constructive constant improvement still cannot infer an O_q(v(n+w^p))
local allowance from those upper bounds. It is not a runtime lower bound.

The source-bound finite evidence reconstructs all nine actual capture projectors
from R437's root rows at a24f9ff, covering45 contexts at q=3,5,7,11 with high
lifts and unit ancestors,192 GL2/weight contexts, an ambient64 nonzero graph
with singular leading chart, complete small arbitrary payload/63 readers,
and semantic failures. Separate principal-minor/chart and routing checks do not
import the compiler. Tests at small q establish their stated algebraic cases;
large-prime supplier cost theorems still require their admitted q domain.

Still open: an encoded coefficient producer and physical primitive realization
for this alternate schedule; a genuinely cheaper complete ordinary tariff or
an actual jointly charged consumer; uniform source/return/refinement and visited
reserve admission; full native/router/precision/recovery obligations. No selected
exponent changes. The written proof has not received independent human or
formal-kernel review; separate code is still from this assisted session.
