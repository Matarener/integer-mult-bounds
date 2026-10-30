# Audit of inherited support, incidence and field arguments

## Scope and findings

On the exact declared E8/P112 root labels, this audit confirms global support
capacities12/20 and A2 joint incidence20/32, hence also the inherited22/32.
The stronger rank-five20 is Nick Petalas's existing PR3280 theorem, not a new
bound. His PR3269 and PR3288 supply the existing analytic global and rank-six
proofs. No mathematical objection was found in those arguments.

The new finite implementation imports no predecessor executable. It gives a
complete alternative check of the global and incidence upper bounds. The
written chamber argument below derives precisely the needed geometric statement
from finite reflection closure and positivity, without leaving the standard
Weyl-chamber theorem as an unproved external premise. The scalar-extension step
uses rational matrix rank; it makes no assumption that K embeds in R or C.

This is a written proof and independent computational audit of predecessor
packages, not independent human or proof-kernel acceptance. It establishes no
full C5, global decoder floor, physical supplier, new kappa or selected result.

## 1. Exact model and complete subspace domains

Let R contain the120 doubled E8 root-line representatives of norm8, oriented
by their first nonzero coordinate. The live P112 rows are parsed directly from
the canonical original caller table. Adding the eight omitted frame lines
`2e_0 +/-2e_1, ..., 2e_6 +/-2e_7` produces exactly the full elementary E8 root
patterns:56 two-coordinate lines and64 all-odd lines with even minus parity.

The simple roots alpha_i form an invertible rational basis. Their literal
definition is compared with the pinned predecessor source by AST literal
parsing; that source is never executed. Dense exact elimination supplies every
root's integral coordinates c_i. The labels are

    ell(r) = (1, c mod2) in F2^9,

with the fixed coordinate in bit0. All112 original caller labels agree in
order. Thus this audit uses the actual support-rank convention. It also checks
the live evaluation Gram matrix112 I_8.

For n-dimensional binary space, a d-space is the kernel of a unique
(n-d)-dimensional annihilator. In the reversed-column reduced-echelon convention,
each annihilator row has highest pivot p, other pivot columns zero, arbitrary
nonpivot columns below p, and zero columns above p. Choosing its pivot set and
all those free bits enumerates every annihilator exactly once. Rank-nullity
then gives every d-space exactly once. This is a mathematical coverage argument;
an expected cardinality alone would not prove uniqueness or completeness.

The checker counts all3,309,747 five-spaces and788,035 six-spaces of F2^9.
Their full-root trace maxima are12 and20. Their P112 trace maxima are also12
and20, with literal spanning witnesses retained in RESULT.json. Any smaller
support span extends to a checked space, so these are bounds for binary ranks
at most5/6, not only equality-rank spaces or full binary closures. The receipt
records complete trace-size histograms. A separate small-domain control compares
the enumerator against every generating subset through binary dimension5.

These direct counts independently discharge the exact global capacities used
by the inherited caller. They do not assume the analytic character-sum proof.

## 2. Audit the signed analytic support argument

The quadratic form on eight-bit residues is

    q(x) = sum_i x_i + sum_(i<j) G_ij x_i x_j,
    G_ij = (alpha_i dot alpha_j)/4, modulo2.

The norm identity is q(c mod2)=||sum_i c_i alpha_i||^2/8 modulo2.
Exact reconstruction binds the120 root residues to all q=1 points, checks
polar nondegeneracy and all65,536 polarization pairs, and obtains signed sum+16.

For an affine quadratic function f on a nondegenerate binary n-space, a
k-dimensional direction space L with polar radical T of dimension t, and
an affine section a+L, let S=sum_(x in L)(-1)^f(a+x). Put q0=f+f(0).
Expanding S squared and grouping by the difference h gives

    S^2 = 2^k sum_(h in T) (-1)^(q0(h)+B(a,h)).

The exponent restricts to a linear character on T. Therefore S=0 or
|S|=2^((k+t)/2), and t<=n-k. In the saturated case k+t=n, L=T-perp.
When that radical character vanishes, set g=q0+B(a,.). It vanishes on T.
Every coset of T outside L has zero g-sum, so sum_L(-1)^g=sum_E(-1)^g.
Multiplying by (-1)^f(a) and translating by a yields

    S = sum_E (-1)^f.

The constants cancel; this identity is valid for affine f with linear and
constant terms. In particular a positive ambient sign cannot become the
negative saturated extremum. No gap was found in this crucial sign step.

For the ambient plus-type eight-space, affine dimension4 has polar ranks0,2,4.
At rank0 the restriction is balanced or has S=+16, so at most8 ones; at ranks2
and4 the maxima are12 and10. At affine dimension5, radical dimension excludes
polar rank0. Polar rank2 gives S=0 or+16, hence at most16 ones; polar rank4
gives at most20. A rank-d leading-one binary label space has affine dimension
at most d-1, so this recovers12/20. Smaller sections extend to these dimensions.

The sign hypothesis is substantive. On the minus-type eight-space the controls
construct actual affine four-/five-sections with16/24 ones. In a minus-type
six-space they construct affine four-/five-sections with12/20 ones. Dropping
the positive Gauss sign would make both global and A2 analytic conclusions false.

## 3. Every A2 fiber, including arbitrary ambient support spaces

Every A2 root plane contains a nonorthogonal root pair with inner product+/-4.
The appropriately signed sum supplies its third root line. All7,140 pairs
therefore exhaust the1,120 A2 planes without a transitivity assumption. Exact
evaluation pairs partition each full root set into a zero class of36, three
projective classes of27, and three singleton classes. There are3,360 distinct
large fibers A. This is the complete nonzero-fiber domain, not just one orbit
representative or coefficient slope.

For every A, the checker obtains W=span_F2(A), dim W=7, and

    R intersect W = A union {p},

with exactly one extra root p. Its leading-one affine six-space has nondegenerate
polar form and signed sum+8. These finite binding facts independently match the
existing analytic premises for every fiber. No Weyl transport is needed here.

Inside each W, the new direct census checks all2,667 five-spaces and127
six-spaces. Over all fibers this is8,961,120 and426,720 tests. Five-space root
capacity is10 and joint capacity is20. The six-space table, checked for EVERY A,
is

    (m,j):  (0,0) (12,11) (12,12) (16,15) (16,16)
    count:      1      27      36      36      27,

where m=|R intersect V| and j=|A intersect V|. In particular m<=16 and
m+j<=32. Complete per-fiber records are bound by a deterministic digest.

For arbitrary V of dimension at most5, if V is contained in W the census gives
m+j<=20. Otherwise dim(V intersect W)<=4. Its leading-one section has at most8
points, so j<=8, while the global bound gives m<=12. Thus again m+j<=20.

For arbitrary V of dimension at most6, containment gives32. Otherwise
dim(V intersect W)<=5. Extend that intersection to a five-space in W; its root
capacity10 bounds j. The global m<=20 then gives m+j<=30<32. These dimension
arguments include lower-rank spaces, spaces extending beyond W and arbitrary
partial supports. Replacing a partial support by its binary closure only
increases the quantities being bounded. A singleton projective fiber gives
j<=1, so its bounds13/21 are already below20/32.

The analytic proofs pass the same audit: inside the positive six-space an affine
four-section has at most10 roots and an affine five-section at most16. These
are exactly the two finite capacities corroborated above. Their inside/outside
split does not silently assume that the actual piece spans only fiber labels.

Frame puncturing or restricting to a common residual coordinate set takes
subsets and cannot increase either incidence term. Thus20/32 holds on P112,
and the older inherited22/32 is conservative. Literal all-live equality
witnesses found by the census are recorded without claiming predecessor novelty.

## 4. Finite-group proof of the required chamber statement

The eight alpha_i are a basis with squared norm8. For each i define the real
orthogonal reflection

    s_i(x) = x - (x dot alpha_i)/4 * alpha_i.

All1,920 images of the240 signed roots under these eight generators belong to
the same signed root set. Each s_i is an invertible involution, hence permutes
that finite set. A linear map is determined by its action on a spanning subset
of the roots. The group G generated by the s_i therefore injects into the
permutation group of240 objects and is FINITE. Its order need not be computed.

Choose the checked rational vector

    rho=(0,1/2,1,3/2,2,5/2,3,23/2),

for which rho dot alpha_i=1 for every i. For any h in R^8 maximize
(g h) dot rho over the finite group, and call a maximizing vector u. If
u dot alpha_i<0, then

    (s_i u) dot rho - u dot rho = -(u dot alpha_i)/4 >0,

contradiction. Thus u is in the closed chamber defined by all eight nonnegative
simple-root pairings. This argument proves the needed chamber property; it
does not infer it merely from a reflection-closure PASS marker.

Every root has all its checked simple coordinates nonnegative or all
nonpositive. For a positive root beta=sum c_i alpha_i, its pairing with u is
a sum of nonnegative terms. It vanishes exactly when c_i=0 at each index
where u dot alpha_i>0. The perpendicular roots are therefore precisely the
roots supported on the vanishing simple-coordinate indices. Those simple
roots themselves belong to the face and form its basis. This proves the
needed parabolic-face assertion directly, without an unproved classification
or Weyl-chamber theorem.

The finite face inventory gives at most20 root lines at rank<=5, at most36
at rank<=6, and seven-node counts42,28,22,14,16,23,37,63. The63-line face
has a root normal. The only six-node faces with at least28 lines have30 or36;
their normal planes contain respectively two orthogonal root lines or an A2
root pair. These exact normals and all face cases are checked in RESULT.json.
Their two-root Gram determinants are64 and48, so they are independent over
every characteristic-zero field.

The chamber move is used only for full-root cardinalities and normal-space
types. It need not preserve the omitted frame or the live binary supports.
Actual P112 union bounds are obtained separately by enumerating every relevant
root plane against the literal live set; no frame-preserving Weyl action is
silently assumed.

## 5. Root-spanned subspaces and rational scalar extension

First let Z be a rational subspace spanned by some roots, of rank d<8.
Choose a generic nonzero real vector v in Z-perp. Each root outside Z gives
a proper hyperplane in Z-perp, so finitely many such hyperplanes can be
avoided. The full roots perpendicular to v are exactly R intersect Z and
span Z. Apply Section4: after one element of G, their span is exactly the
simple-root span of the corresponding face. Its rank is d, not an unspecified
larger rank. This justifies using the rank-d face capacities for an arbitrary
root-spanned rational Z; no assumption that Z was initially a parabolic span
has been made.

Now let K be any characteristic-zero field. The embedding Q into K preserves
the rank of every rational matrix: a nonzero rational minor remains nonzero,
and all larger minors remain zero. Its rational nullspace extends to its full
K-nullspace by Gaussian elimination. Consequently, for directions h_1,...,h_s
independent over K, the rational span Z of all roots perpendicular to them
has rank at most8-s.

In particular, a nonzero word c_h with support below70 on P112 has at least43
live zero roots. Rank<=6 of Z would allow at most36 full root lines, impossible.
Thus rank Z=7. Among the seven-node faces only the63-line face reaches43,
so Z-perp is a rational root-normal line. Its extension contains h. The full
root alphabet is invariant under G, so the conclusion transports back.
Direct exact evaluation gives112 root normals of live support53 and eight
of support56. Hence the minimum code distance is53. The Gram112 I_8 proves
evaluation injectivity over K.

Similarly, two independent codewords with union at most84 have at least28
common live zero roots. Their Z has rank<=6; rank<=5 would permit only20
root lines. Thus rank Z=6, and Section4 identifies its rational normal plane
as D6 or E6. Its two-dimensional scalar extension is exactly the span of
the two given K-directions. Replacing them by a rational basis preserves the
actual live union: a root annihilates the entire plane over K exactly when it
annihilates that rational basis. No real/imaginary split or embedding of K
is used. The fresh actual-plane census gives E6 live unions78 or80 and the
D6 union histogram82:448,84:2688,85:448,86:168,88:28.

These are the precise completeness and field-transfer implications needed in
PR3931 and PR3295. The procedure does not assert a new uniform normal-plane
bound under unrelated support/cut hypotheses.

## 6. Coefficient columns really give a single projective fiber

Use a rational basis a,b of a normalized code plane, and express its two
codewords as a fixed2-by-n matrix A applied to the actual pieces. At a live
union site where only piece i is nonzero, the rational evaluation pair
(r dot a,r dot b) is that scalar value times column i of A. A zero column
cannot have such a singleton in the union. A nonzero column with any singleton
therefore has a rational projective slope. All its singleton sites have that
same slope: proportionality of two rational pairs over K is equivalent to
vanishing of their rational2-by-2 determinant, hence to proportionality over Q.

The preceding all-fiber incidence bound consequently applies to arbitrary
K-valued coefficients. Extra piece support outside the evaluation union and
cancellations contribute to M, while J remains a subset of that one fiber.
They do not evade the upper bound on M+J. Thus the inherited A2 incidence
use in the six-piece proof is sound over all characteristic-zero fields.

In particular its conservative allowance16+3*22+2*32=146 is below the required
2*78=156. The existing stronger20 would give140, but no change to that frozen
proof or receipt is needed. This audit supplies the specifically requested
inherited bounds and field implications; it does not automatically certify
every other caller reduction or the complete C5 conjecture.

Characteristic zero is essential to these particular arguments. The controls
exhibit the nonzero direction e0+e1 whose evaluations vanish modulo2 on all
live roots while they are nonzero over Q. They also exhibit the three proper
hyperplanes covering F2^2, whereas a rational point avoids their rational
counterparts. These controls expose failed extensions of the hypotheses;
they are not substitutes for the rational-rank proof above.

## Evidence boundary and credit

All new counts, witnesses and normal types are freshly reconstructed from the
original table and fixed simple-root definition. The original PR3269, PR3280
and PR3288 registered packages were separately replayed and passed. Their37
public file Git blobs match canonical main at the pinned exact heads. A merged
archive's ledger status remains partially reviewed; this audit does not change
maintainer review status or the selected frontier.

Credit Nick Petalas/PR3269/3280/3288/3262 and their cited predecessors, David
Arias's quadratic-model work, DreamingOfClouds/PR3154, joaqcoo and the retained
E8/P112 lineage. The signed bounds and equality tables are their prior results.
The finite-group maximization is a standard elementary chamber proof written
out here for the assigned exact model; it is not claimed as a new general
theorem. New audit code/prose is by Chris R / Clear1nsight with substantial
OpenAI Codex assistance, Apache-2.0. Full C5, other caller reductions,
physical/native/consumer/restoration/supplier/all-size admission, selected cold
replay, Lean, Docker and independent human/kernel acceptance remain outside scope.
