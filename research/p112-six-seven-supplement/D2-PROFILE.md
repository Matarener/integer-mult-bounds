# The intrinsic (7,7,5,5) profile has code intersection at most one

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
Use the roots, frame, code C and leading-one binary labels of
[PROOF.md](PROOF.md), over any characteristic-zero field K. This proof uses
its root-direction rigidity, rank-five capacity12, rank-seven root-target
capacity32 and root32-completion theorem. The quarter model and frame
punctures are those of [UNIFORM.md](UNIFORM.md), Sections 1--2.

**Theorem.** If independent pieces A,B,L,M have binary support ranks at
most 7,7,5,5, respectively, then

    dim_K(C intersect span_K{A,B,L,M}) <= 1.

This is an intrinsic piece-span statement. It does not assert a complete
actual d=2 invoice, actual-basis adaptation, or global C1 normalization.

## 1. A nonframe root has no (7,5,5) cover

Suppose a nonframe root word C_v is supported in one rank-seven and two
rank-five label flats. Its support has53 live sites. The seven-flat must
carry at least `53-12-12=29` of them. PROOF.md Section 4 therefore forces
it to be a full32-root completion X. Its complementary quarter C24 has
the model

    C24 = Omega x R,       |Omega|=6,       dim R=2,

from UNIFORM.md Section 1. Omega contains no affine two-plane and every
affine hyperplane contains at most four of its points. The seven-flat
misses C24 and the self label v. One of the five-flats must carry v.
Since v is outside the quarter's label seven-flat, that five-flat meets
it in rank at most four, hence in at most eight roots. The other
five-flat has capacity twelve.

At most four roots of C24 are removed frame roots. Covering its live part
requires at least20 sites, while the two low parts can cover at most
`8+12=20`. Equality is necessary: all four punctures lie in C24, the low
parts cover disjoint sets of eight and twelve live quarter roots, and
each attains its full section capacity.

Here is the full-fiber consequence of equality. A rank-four label section
has affine dimension at most three. If its projection to the quotient
has dimension two, it contains at most three Omega points and its
radical fibers have size at most two, giving at most six roots. Projection
dimension three gives at most four roots. To contain eight roots it must
therefore be the lift of two Omega points, with both four-point radical
fibers present in full.

Similarly, a rank-five label section has affine dimension at most four.
Projection dimension three gives at most `4*2=8` roots; dimension four
gives at most six. Projection dimension at most one gives at most eight.
Thus a twelve-root section must project onto three Omega points in an
affine two-plane and contain their three radical fibers in full.

The four frame punctures form an affine plane. As in UNIFORM.md Section 2,
its direction is totally singular, whereas R contains the anisotropic
normal v. The intersection of those directions has dimension at most one.
The puncture plane cannot project to an affine plane in Omega, so it
projects onto exactly two Omega points, with two punctures in each fiber.
Only four of the six radical fibers are unpunctured. The disjoint live
eight- and twelve-root sections would require respectively two and three
full unpunctured fibers: five distinct fibers where only four exist.
This contradiction proves the lemma.

## 2. Coordinate kernels force two frame words

Suppose the theorem fails and choose a two-dimensional subspace D of the
code intersection. Restrict the A and B coordinate functionals to D.
Their joint kernel is zero: a nonzero word in it would be supported on
L and M, hence on at most24 sites, below code distance53. Consequently
both restrictions are nonzero and their one-dimensional kernels are
distinct.

Killing either seven-piece leaves a codeword supported on at most
`36+12+12=60<70` sites. Root-direction rigidity makes its normal an E8
root direction; Section 1 excludes a nonframe root. Thus the two kernel
words are scalar multiples of frame words C_a,C_b for distinct frame
axes a,b. Relabel A,B so

    C_a = alpha A + lambda L + mu M,
    C_b = beta B + lambda' L + mu' M.

Each displayed coefficient is nonzero: omitting any term leaves capacity
at most44, below the frame word's support size56.

## 3. Equality forces the low pieces to be sign halves

Write N(a)=supp(C_a), so |N(a)|=56. The root-target and low-rank capacities
give

    56 <= |N(a) intersect supp A|
          + |N(a) intersect supp L| + |N(a) intersect supp M|
       <= 32+12+12 = 56.

All inequalities are equalities. In particular L,M each have exactly12
support sites, wholly inside N(a), disjoint from each other and from
A's support in N(a). Repeating the argument with C_b puts both low
supports inside N(b), disjoint from B's target support. Since
`|N(a) intersect N(b)|=24`, their union is precisely this common quarter.

At every site in supp L the two expansions reduce to

    C_a(s)=lambda L(s),       C_b(s)=lambda' L(s).

The ratio C_b/C_a is therefore constant there, and likewise on supp M.
On the common quarter both frame pairings are +/-1, and their ratio
classes +1 and -1 each have12 sites. Thus the two low supports are exactly
the same-sign and opposite-sign halves, in either order. Disjointness
and absence of outside low support were forced by equality, not assumed.

## 4. Each sign half has label rank at least six

The common quarter is the model Omega x R of UNIFORM.md Section 1 with
`R=span_F2{a,b}`. Omega affinely spans the four-dimensional quotient,
since an affine hyperplane could contain at most four of its six points.

The orthogonal reflections s_a,s_b commute. For a common neighbor r,
reflection in a negates (r,a) and preserves (r,b); reflection in b does
the reverse. Each flips their product. This product is unchanged by
r -> -r, so canonical choices of projective root representatives do
not affect the argument. On binary residues the reflections are

    x -> x+a,       x -> x+b,

because `s_a(r)=r-(r,a)a` and the coefficient +/-1 becomes one modulo two.
They act regularly on each four-point radical fiber. Each product-sign
half therefore contains two points in every fiber, whose difference is
the nonzero radical vector a+b.

Each half projects onto all six Omega points and its affine direction
span has a nonzero kernel under that projection. Its affine span has
dimension at least `4+1=5`, so its leading-one label rank is at least six.
This contradicts the rank-at-most-five bounds on L and M and proves the
theorem. No finite exact-rank-seven premise is required.

## 5. Literal source callers and scope

The dimension-deletion lemma of [CALLERS.md](CALLERS.md) extends the
theorem: if a piece span meets C in dimension at least d>=2, killing any
d-2 chosen piece coordinates leaves an intersection of dimension at least
two. It cannot leave four pieces of ranks at most 7,7,5,5.

In DreamingOfClouds's pinned PR3154 output
`research/p112-reduction-to-conjectures/checks/CONJG2/land_e2_k8.out`,
head `708f0ad8928c383de8294aea3c126e9461d2066d`, this excludes the literal
t2,d2,slack8 profile `[7,7,5,5]` and t2,d3,slack7 profile
`[7,7,7,5,5]`; delete one seven-piece in the latter. These are literal
profile implications, not a current open-case count or a claim of global
source-list completeness. This intrinsic theorem alone does not give an actual invoice;
[D2.md](D2.md) separately proves the complete actual d=2 invoice.
Actual d>=3 invoices remain open.

Credit DreamingOfClouds's PR2816 circuit/coordinate-kernel lineage and
Nick Petalas's PR3171 root-pencil lineage, with the exact pins recorded in
CALLERS.md. The analytic capacities, quadratic model and predecessor
attributions are retained in PROOF.md and UNIFORM.md, including Nick
Petalas and David Arias. This composition is by conorholds with substantial
OpenAI Codex assistance. It is written mathematics with scoped geometric
inputs, not a Lean proof of the complete theorem.
