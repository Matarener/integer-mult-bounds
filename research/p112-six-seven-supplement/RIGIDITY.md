# Intrinsic (7,7,6,4) and (7,6,6,5,1) exclusions

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
The retained geometry and predecessor credits are those of
[PROOF.md](PROOF.md), [UNIFORM.md](UNIFORM.md), [D2-PROFILE.md](D2-PROFILE.md)
and SOURCES.json. These are written characteristic-zero proofs; finite
corroboration and partial formal cores are distinguished below.

Use their E8/P112 roots, arbitrary orthogonal removed frame F, labels
ell(r)=(1,r mod 2L), characteristic-zero field K and root code C.

## First theorem

For independent pieces A,B,L,M of binary support ranks at most 7,7,6,4,
respectively,

    dim_K(C intersect span_K{A,B,L,M}) <= 1.

The key statement is stronger than the sharp five-site supplement: every
actual coefficient representation of a root word by ranks (7,6,4) is one of
the sharp partitions, even though a rank-four support can have eight sites.
This statement is about a three-piece root representation; it does not
classify arbitrary covers with a genuinely arbitrary eight-site supplement.

## 1. A root (7,6,4) cover forces a 32-root completion

Let a root word C_v be supported in U7 union U6 union U4, where the U_i are
label spaces of the displayed dimensions. Its support has 53 live sites for
nonframe v and 56 for frame v. The high flat therefore carries at least
53-20-8=25 target sites.

The leading-one section of U7 is an affine six-space H. If B(v,.) varies on H,
the nonself target slice is an affine five-space with at most 20 roots; self v
could add at most one. If it is constantly zero, only self could contribute.
Thus H is contained in B(v,x)=1. In particular the high flat misses self. The
signed quadratic calculation in PROOF.md Section 4 gives high-root section
size 24, 28 or 32. Size 24 is too small.

If size 28 occurs, the parallel complementary section C28 has 28 roots and
nondegenerate six-dimensional direction space. Every affine hyperplane of this
section has at most 16 roots, by the Walsh calculation in UNIFORM.md Section
4. Hence a rank-six label space meets C28 in at most 16 roots.

If v is frame, all C28 roots are live, but U6 and U4 cover at most 16+8=24.
This is impossible. If v is nonframe, at least 24 C28 roots are live, and self
v must be in one low flat. Self is outside the label span of C28. If self lies
in U6, the intersection rank drops to at most five, giving C28 capacity at
most 12+8=20. Otherwise self is in U4, whose intersection rank drops to at
most three, giving capacity at most 16+4=20. Again impossible.

Consequently U7 is a 32-root completion X and its deleted quarter C24 has the
model Omega times R from UNIFORM.md Section 1. Here R has dimension two; Omega
consists of six points in an affine four-space, contains no affine plane, and
its affine hyperplane sections have size two or four. The quarter has label
rank seven and misses self v.

## 2. Nonframe self cannot be in U6

Suppose v is nonframe and ell(v) is in U6. Then U6 intersects the quarter
label space in rank at most five, so its quarter capacity is at most 12. U4
has capacity at most eight. The live quarter has at least 20 roots. Equality
is necessary: all four frame neighbors of v lie in C24, and the two low flats
cover disjoint live quarter sections of sizes 12 and 8.

An eight-root rank-four quarter section is exactly two complete radical
fibers. To see this, its affine dimension is at most three. Projection
dimension zero gives at most four roots; dimension two gives at most 3*2=6
roots because Omega has no plane; projection dimension three gives at most
four. Thus eight requires a one-dimensional projection and the full
two-dimensional radical.

Likewise a twelve-root rank-five quarter section is exactly three complete
radical fibers. Its affine dimension is at most four. Projection dimensions
zero or one give at most eight roots; dimension three gives at most 4*2=8;
dimension four gives at most six. Thus twelve requires projection dimension
two and full radical fibers, with three Omega points in the projected affine
plane.

The four deleted frame roots form an affine plane in C24. Its direction is
totally singular, whereas q on R is nonzero, so its intersection with R has
dimension at most one. Its projection cannot be a plane inside Omega. Thus it
projects onto exactly two Omega points, with two deleted roots in each fiber.
There are only four unpunctured fibers. The disjoint twelve- and eight-root
live sections would require five distinct complete unpunctured fibers, a
contradiction.

This proves ell(v) is not in U6. Self must therefore be in U4.

## 3. The actual nonframe coefficient partition is forced

Since self lies in U4 but outside the quarter label space, the quarter
capacity of U4 is at most four. Together with U6's quarter capacity 16,
covering the at least 20 live quarter roots forces equality. All four frame
neighbors lie in C24; U6 contains exactly sixteen live quarter roots; U4
supplies the other four.

UNIFORM.md Section 1 identifies the sixteen-root section as a full lift of a
four-point affine hyperplane section of Omega. It spans U6, so all full-root
labels in U6 are these sixteen roots Y. The omitted pair of Omega points lifts
to an affine three-space of eight roots. The deleted frame plane is one affine
plane inside this space, and its four remaining points are the complementary
parallel affine plane E4. Thus E4 has label rank three. The high section X has
no deleted frame roots, since all four frame neighbors lie in C24.

Because ell(v) is outside the quarter label space, the labels of E4 and self
span U4 in dimension four. Their intersection with the root-neighbor label
hyperplane B(v,x)=leading_bit is exactly span ell(E4). Accordingly U4 has no
further neighbor roots. Any additional root labels in U4 are orthogonal to v.
In an actual coefficient representation

    C_v = alpha A + lambda L + mu M,

with support ranks 7,6,4, these extra sites of M must have coefficient zero: A
and L are supported entirely in B(v,x)=1, whereas C_v vanishes there. Every
displayed coefficient is nonzero, since deleting any piece leaves root-target
capacity at most 32+20=52.

The representation therefore has the exact disjoint support partition

    supp(A)=X32, supp(L)=Y16, supp(M)=E4 union {v},

and each scaled piece is the restriction of C_v to its support. This is
precisely the nonframe sharp partition of UNIFORM.md.

## 4. The actual frame coefficient partition is also forced

For frame v the whole C24 is live. Its cover by U6 and U4 has capacities 16
and 8, so equality forces disjoint full sections of those sizes. The rank-six
section is a full lift of four Omega points, and its complement is the full
lift of the omitted pair, an affine three-space of eight roots. These root
sets span their entire respective label spaces, so neither low piece has any
additional root sites. The high piece is the disjoint X32 restriction.
Therefore the exact actual partition is

    supp(A)=X32, supp(L)=Y16, supp(M)=E8.

This is the frame sharp partition of UNIFORM.md. In particular a shared
rank-four actual piece in a nonframe representation has exactly five support
sites, and in a frame representation exactly eight.

## 5. Two-dimensional code intersection is impossible

Suppose a two-dimensional code subspace D lies in the span of independent
A,B,L,M. Restrict the A and B coefficient functionals to D. Their joint kernel
is zero, since a codeword supported on L and M has at most 28 sites, below
distance 53. Thus their two one-dimensional kernels are distinct. Killing
either high coordinate leaves support size at most 36+20+8=64<70; root
rigidity makes the two kernel words scalar root words C_a and C_b in distinct
root directions. Relabeling the highs, write

    C_a = alpha A + lambda L + mu M,
    C_b = beta B + lambda' L + mu' M.

All six coefficients are nonzero: each root word has at least 53 sites, and
deleting a low piece leaves target capacity at most 52; the high coefficient
is nonzero by injectivity of the pair of high coordinates.

If exactly one of a,b is frame, Sections 3--4 force the same actual piece M to
have support size both five and eight, impossible.

If both are nonframe, Section 3 forces M to contain both self sites a,b, and
the ratio C_b/C_a is the fixed nonzero scalar mu'/mu on its support. If a and
b are orthogonal this ratio is zero at a, impossible. Otherwise, after signs,
(a,b)=epsilon in {+1,-1}. Its values at the two self sites are epsilon/2 and
2/epsilon, which are unequal in characteristic zero. Again impossible.
Root-representative signs cancel from these ratios.

If both are frame, Section 4 puts the sixteen-site support of L inside their
common 24-root quarter, and C_b/C_a is constant there. The two ratio classes
+1 and -1 in that quarter have twelve roots each, as proved in D2-PROFILE.md
Sections 3--4. A constant-ratio set cannot have sixteen sites. This is the
last contradiction.

## 6. A six-dimensional plus quadric has affine-four capacity ten

The affine quadratic quotient used below has nondegenerate polar form in
dimension six and signed sum +8, hence 28 one-points. Its affine-five sections
have capacities twelve or sixteen: the nonzero linear Walsh coefficients are
+8 or -8, and splitting the ambient sum gives section signed sums zero or +8.

For an affine-four section a+H, the polar restriction to H has rank four or
two; its radical has dimension at most two by ambient nondegeneracy. Rank four
gives signed sum +/-4 and thus at most ten one-points. For rank two put
R=rad(H), dim R=2; necessarily H=R-perp. If the affine quadratic function
varies on R, cancellation gives eight one-points. Otherwise a+H is the unique
parallel H-coset on which the radical character vanishes: all other parallel
cosets cancel. Its signed sum is therefore the full ambient +8, giving four
one-points. In particular the putative twelve-point negative-sign case is
impossible. This proves the sharp capacities ten and sixteen without a flat
census.

Both exact engines separately check all 2,604 affine-four sections and 126
affine-five sections of q=x1*x2+x3*x4+x5*x6. Their histograms are respectively
{4:315,6:1008,8:945,10:336} and {12:63,16:63}.

## 7. Second theorem: intrinsic (7,6,6,5,1)

For any independent five pieces of support ranks at most 7,6,6,5,1, their span
meets C in dimension at most one. This permits overlap and cancellation in the
original family.

Otherwise choose a two-dimensional code intersection and kill the seven-piece
coordinate. A nonzero codeword remains in pieces of ranks 6,6,5,1, with total
support capacity 20+20+12+1=53. Root rigidity forces a nonframe root word C_v:
a frame needs 56 sites and a nonroot at least 70. Equality forces all four
coefficients nonzero and the four actual supports to be disjoint, wholly
inside Off(v), of sizes 20,20,12,1.

Self cannot belong to a twenty-site piece. Containing self reduces its
neighbor-intersection rank to at most five, hence its target capacity to
12+1=13. Similarly a rank-five piece containing self has target capacity at
most 8+1=9, rather than twelve. Thus the unit piece is exactly self.

On the affine seven-space B(v,x)=1, translation by v preserves q since
q(x+v)=q(x)+q(v)+B(x,v)=q(x). Quotienting by this direction turns the 56-root
neighborhood into the six-dimensional nondegenerate affine quadric with 28
roots and signed sum +8 of Section 6.

Each twenty-site piece spans an affine five-space, and the twelve-site piece
spans an affine four-space: otherwise the smaller global capacities would
preclude their sizes. If its direction omitted v, projection would inject its
roots into an affine-five or affine-four quotient section. The capacities
sixteen and ten exclude these possibilities. Each piece's direction therefore
contains v. Saturation of the global 20/20/12 capacities also says its actual
support is the complete full-root section of its label span. Consequently each
support is stable under translation by v.

Their union would make the punctured neighborhood N(v) minus F stable. But
every removed frame neighbor f has a live root partner f+v. It is a root by
q(f+v)=1; it is not another frame point, since f+v=f' would give
q(v)=q(f+f')=0 for distinct orthogonal frame roots. Thus a live neighbor would
translate to a removed one. This contradiction proves the theorem.

## Verification and proof boundary

The first theorem uses the actual coefficient partition, rather than assuming
that an arbitrary rank-four piece has only five sites. The eight-root closure
of every one of the 336 nonframe sharp covers has exactly the five target
sites plus three orthogonal sites; both engines check this explicitly. Actual
root representations must have zero coefficients on those extra sites, as
Section 3 explains.

Both engines also examine all 15,360 root/high complementary cases, 12,000
distinct 28-root sections, and every hyperplane restriction of each section.
The nonzero functional histogram is {0:1,12:63,16:63}, corroborating the cap
sixteen used to exclude the 28-root branch. These finite checks corroborate
the analytic proofs. The complete E8 instantiation and the assembly of both
intrinsic theorems remain outside Lean. No source-list completeness, N8 or
correction count is a premise.

## Dimension-deletion consequences

For an independent family with code intersection dimension d>=2, killing any
d-2 piece coordinates leaves a code intersection of dimension at least two in
the remaining span (CALLERS.md; formal/DimensionDeletion.lean). Thus, for
every d>=2, the first theorem excludes the T-level profile consisting of d
sevens followed by6,4. The second excludes d-1 sevens followed by6,6,5,1.
Coordinatewise smaller profiles are excluded as well. These are intrinsic span
exclusions. Deletion does not by itself preserve an actual basis or its
correction ledger, so no actual d>=3 invoice is claimed from these
corollaries.