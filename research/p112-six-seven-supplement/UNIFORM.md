# Uniform sharpness and the five-site equality geometry

Use the root, lattice, label and code conventions of [PROOF.md](PROOF.md).
In particular roots have squared norm two, an arbitrary orthogonal frame
`F` of eight root lines is removed, and `P` is the remaining 112 lines.
All support statements are unchanged by choices of signs for root representatives.
The coefficient field is any characteristic-zero field.

The arguments below use the analytic support capacities 12/20/36, the
root-rigidity implication `|Off(h)|<70 => h is a scalar root direction`,
and the quadratic character identities proved or explicitly assumed in
PROOF.md. The standard real Weyl-chamber theorem and ADE root-system facts
remain inherited mathematical inputs. No additional census or executable
receipt is a premise of these extensions.

For spaces of dimensions at most six and seven write

    e(h;U6,U7) = |Off(h) \ (Lambda(U6) union Lambda(U7))|.

The following conclusions hold uniformly in the orthogonal frame.

* If `h` is a scalar nonframe-root direction, then `e>=5`, and five is
  attained. Every such root has exactly three pairs `(U6,U7)` attaining five.
* If `h` is a scalar removed-frame-root direction, then `e>=8`, and eight
  is attained. Every frame root has exactly 945 pairs attaining eight.
* If `h` is not a scalar root direction, then `e>=14`. Sharpness of fourteen
  is not asserted.

The first bound is the theorem of PROOF.md. The new assertions here are its
uniform sharpness, the equality description, and the two normal-type bounds.
These statements do not assert priority over all earlier unpublished work.
PR2816 already records the numerical three large seven-sections for each
nonframe-root target; the arguments below identify the complete five-site
equality pairs and their intrinsic geometry.

## 1. The 24-root quarter and its four-dimensional quotient

Let `v,w` be distinct orthogonal root lines, represented by roots, and put
`u=v+w` in `V=L/2L`. Thus

    q(v)=1, q(u)=0, B(v,u)=0, u!=0.

Define the two affine six-spaces

    X = {x : B(v,x)=1, B(u,x)=1},
    A_C = {x : B(v,x)=1, B(u,x)=0}.

Their root sections have 32 and 24 points, respectively. Write `C` for the
24-root section. The full nonself neighborhood of `v` is their disjoint
union. This is the completion and quarter calculation in PROOF.md.

The direction space of `A_C` is `H=<v,u>^perp`. Its polar radical is
`R=<v,u>`, of dimension two. For `x in A_C`, translation by either radical
generator preserves the value of `q`:

    q(x+v)+q(x) = q(v)+B(x,v) = 1+1 = 0,
    q(x+u)+q(x) = q(u)+B(x,u) = 0.

Consequently `q` descends to an affine quadratic function `Q` on the
four-dimensional affine quotient `A_C/R`. Its polar form is nondegenerate.
The signed sum on `A_C` is 16, and every quotient fiber has four points,
so the quotient signed sum is `+4`. Thus `Q` has exactly six value-one
points. We call this six-point set `Omega`. This description of the plus
four-dimensional quadric includes its sign; only nondegeneracy and that
positive signed sum are used below.

### No affine plane lies in Omega

Suppose an affine plane `a+T` of dimension two had constant value one.
Polarization makes `T` totally isotropic. Nondegeneracy in dimension four
then gives `T^perp=T`. The restriction of the quadratic function to every
coset of `T` is a constant times a character of `T`. Precisely one coset
has trivial character: the other cosets cancel in its signed sum. The
coset `a+T` is that coset, and contributes `-4`. The total signed sum would
therefore be `-4`, contrary to `+4`. Thus Omega contains no affine plane.

### Fifteen four-point hyperplane sections

For every nonzero linear functional on the four-dimensional direction
space, nondegeneracy gives a quadratic Walsh sum of absolute value four.
The signed character sum over Omega is consequently `+2` or `-2`.
The two parallel affine hyperplanes therefore meet Omega in two and four
points. There is one four-point side for each of the fifteen nonzero
functionals.

Four distinct points of Omega cannot have affine span two, by the preceding
paragraph. Hence each four-point section spans its unique affine hyperplane
of dimension three. The fifteen sections are distinct. Their complements
are fifteen distinct pairs of points of Omega, so every pair occurs exactly
once, since `binomial(6,2)=15`.

Lifting a four-point section gives sixteen roots of C in an affine
five-space, and lifting its omitted pair gives eight roots in an affine
three-space. All sixteen-root sections have binary support rank six:
their label rank is at most six, and sixteen exceeds the rank-five
capacity twelve.

Conversely, every rank-six label space meeting C in sixteen roots is one
of these lifts. Indeed, C spans its seven-dimensional label space `W_C`.
A sixteen-point intersection has rank at least six, again by capacity
twelve, so the rank-six space is contained in `W_C`. Its leading-one
section is an affine hyperplane of `A_C`. If its defining functional were
nonzero on R, it would keep exactly two points from each of the six root
fibers and contain only twelve roots. Thus the functional descends to
the quotient, where its section must be one of the fifteen four-point sides.

## 2. Uniform attainment for every nonframe root

Let `v` be a root outside the removed frame. Exactly four frame roots have
nonzero pairing with v. Choose signed representatives `f1,...,f4` and signs
`epsilon_i` so that

    v = (epsilon_1 f1 + epsilon_2 f2
         + epsilon_3 f3 + epsilon_4 f4)/2.

This follows from orthogonality of the frame and the identity
`sum_(f in F) <v,f>^2=4`: the four nonzero pairings are `+1` or `-1`.
Flip exactly two signs, for example set

    w = v - epsilon_3 f3 - epsilon_4 f4.

The vector w belongs to L, has squared norm two, and is orthogonal to v.
It is therefore a root. Set `u=v+w` and use X and C from Section 1.
For each of the four frame neighbors,

    B(v,f_i)=1, B(w,f_i)=1, B(u,f_i)=0.

Thus all four deleted neighbors lie in C, and none lies in X. The other
four frame roots have `B(v,f)=0` and lie in neither section. In particular
all 32 roots of X are live.

The four distinct residues of `f1,...,f4` sum to zero: modulo `2L`, signs
are irrelevant and the signed sum is `2v`. They form an affine plane in
`A_C`. Its image in `A_C/R` has dimension at most one, since Omega has no
affine plane. Choose a pair of Omega containing that image, and take the
four-point hyperplane section whose omitted pair it is. Its lift Y has
sixteen roots and avoids all four deleted frame neighbors. All of Y is live.

In fact the frame plane projects onto exactly two quotient points. Let D
be its two-dimensional direction space. Every nonzero vector of D is the
sum of two orthogonal frame roots and has q-value zero. But q on
`R=<v,u>` is nonzero, since `q(v)=1`. Consequently `dim(D intersect R)<=1`;
the image of D has dimension at least one. Combined with the preceding
upper bound it has dimension exactly one. The omitted pair, and hence Y,
is therefore unique for this choice of X.

The eight roots lifted from that omitted pair form an affine three-space.
The four deleted frame neighbors form an affine plane inside it. Its other
four points form the complementary parallel affine plane, consisting of
live roots. Call this four-point set E4. The complete live root-word support
is the disjoint union

    Off(v) = X disjoint-union Y disjoint-union E4 disjoint-union {v},
    sizes       32              16               4              1,
    ranks        7               6               3              1.

The first two ranks follow from capacities twenty and twelve. The four
points of an affine plane have leading-one label rank three. The self
label is outside `W_C` and outside the high section: `B(v,v)=0`, whereas
the leading-one points in both spaces satisfy `B(v,x)=1`. Hence
`E4 union {v}` has binary support rank four. This proves uniform attainment
five by a profile `(7,6,4)`, with sizes `(32,16,5)`.

Give each part the actual coefficient `<r,v>` of the root word at its
sites and zero elsewhere. These are characteristic-zero coefficient
identities on every live site, rather than support-only covers. Splitting
off the self site gives the disjoint profile `(7,6,3,1)` above.

## 3. The sharp frame-normal supplement is eight

Suppose v is one of the removed frame roots and at most seven sites remain
outside `U6 union U7`. Its support has 56 sites. Deleting the six-flat
and those seven sites leaves at least `56-20-7=29` sites in U7.
The completion theorem of PROOF.md therefore forces U7 to be a 32-root
completion X as above. Its complementary quarter C has 24 roots.
None of C is removed: every frame root has even pairing with v. A six-flat
meets C in at most sixteen roots. At least `24-16=8` sites therefore remain,
a contradiction. This proves the lower bound eight.

To attain it, choose any other frame root w. The sections X and C from
Section 1 contain no frame roots, because all their points have `B(v,x)=1`.
Choose any of the fifteen sixteen-root lifts Y in C. Its complement E8
in C is the lift of a pair in Omega, hence is an affine three-space of
eight live roots and has binary label rank four. Thus

    Off(v) = X disjoint-union Y disjoint-union E8,
    sizes       32              16               8,
    ranks        7               6               4.

Restricting the actual root-word coefficients to these parts gives the
sharp frame-normal coefficient partition. No claim of sharpness for a
smaller binary rank of the eight-site part is made; its rank is exactly four.

Both uniform constructions have a three-piece space of minimum basis cost
`7+6+4=17`; the nonframe split has four-piece minimum cost `7+6+3+1=17`.
For disjoint nonzero supports, the determinant-matching argument in
PROOF.md proves this minimum. Their code intersection is exactly one
dimensional: every codeword in the piece span vanishes on the live roots
perpendicular to v. There are respectively 59 or 56 such roots, exceeding
the rank-six root-system bound 36, so they span the seven-dimensional
perpendicular hyperplane. Its annihilator is the line of v.
Thus these are genuine intrinsic slack-nine spaces: `d=1`, cost seventeen,
with `t=2` for the three-piece spaces and `t=3` for the nonframe split.
They are not actual marked decoders.

## 4. Every five-site equality cover has the preceding form

Assume a nonzero codeword has exactly five uncovered sites outside U6 and
U7. Its total support is at most `20+36+5=61`, so root rigidity makes its
normal a scalar root v. Section 3 excludes a frame normal. Hence v is a
nonframe root and its support has 53 sites.

After deleting U6 and the five uncovered sites, at least 28 target sites
remain in U7. They have label rank exactly seven, since a six-flat holds
at most twenty roots. Let A be the affine six-space of U7. If `B(v,.)`
varied on A, its value-one slice would be an affine five-space with at
most twenty roots; the self root could add at most one. A constant-zero
value would leave only that self root. Neither case holds 28 targets.
Therefore A is contained in `B(v,x)=1`.

Write A using a second equation `B(s,x)=theta`, with s independent of v.
The character calculation of PROOF.md gives 24 or 32 roots when
`B(v,s)=0`, and 28 when `B(v,s)=1`. The first case cannot have 24 roots
because at least 28 targets remain. We next exclude the 28-root case.

### The 28-root complementary section has six-flat capacity sixteen

When `B(v,s)=1`, the direction space `<v,s>^perp` is nondegenerate of
dimension six. The parallel section

    A' = {x : B(v,x)=1, B(s,x)=theta+1}

also has 28 roots and signed quadratic sum `+8`. For every nonzero
functional on its direction space, nondegeneracy gives a Walsh sum of
absolute value eight. The signed sums on its affine hyperplanes are
therefore `(8+8)/2=8` or `(8-8)/2=0`. Their root counts are twelve or
sixteen. An arbitrary rank-six label space meets this 28-root section
in at most sixteen roots: intersect with its seven-dimensional label
span and enlarge to a hyperplane there if needed.

At most four roots of A' can be deleted by the frame, since every one is
nonorthogonal to v. Thus at least 24 live roots in A' must be covered by
U6 and the five uncovered sites. Their combined capacity is at most
`16+5=21`, a contradiction. This excludes the 28-root case analytically.

### Equality forces the full 32+16 partition

Consequently U7 is a full 32-root completion X, with complementary C of
size 24. Let f be the number of deleted frame neighbors in C; `f<=4`.
If U6 contained the self label, its C-capacity would be at most twelve
by PROOF.md, leaving at least `24-f-12>=8` quarter sites uncovered.
It does not contain self. The uncovered count is therefore at least

    1 + (24-f) - 16 = 9-f >= 5.

Equality forces `f=4`, exactly sixteen live C roots in U6, and no deleted
frame root in that sixteen-root section. Section 1 identifies U6 with
the unique four-point quotient section avoiding the projected frame pair.
The uncovered set is exactly self plus the complementary live affine plane.

There are exactly three possible high completions. Indeed, put `w=v+u`
for its associated orthogonal root. All four frame neighbors lie in C,
so `B(w,f_i)=1` for each. The frame norm identity for w forces its four
pairings there to be `+1` or `-1` and every other frame pairing to be zero.
Thus w has the same four-axis expression as v. Orthogonality requires
exactly two sign changes. Six choices of two signs become three root lines
after identifying w with -w. Conversely each such choice gives Section 2's
construction. Distinct w give distinct completions: the perpendicular
two-space has the unique nonzero singular vector u. Each completion has
the unique low section just proved. Hence exactly three `(U6,U7)` pairs
attain five for each nonframe root.

This also describes any representation with support-rank bounds
`(7,6,3,1)`. Its small supports have union at most five sites, while the
main theorem requires at least five uncovered sites. They must be disjoint
and exactly fill the uncovered set. The rank-three piece occupies the
four-point affine plane and the singleton piece occupies self: a set
consisting of self and three quarter points would have rank four.
The high and low root sections are disjoint and contain only sites of
the root word. Thus cancellation outside that word is impossible, and
each of the four pieces is, up to its nonzero combination coefficient,
the restriction of the root word to its corresponding part.

### Every frame-normal eight-site equality pair

Suppose a frame root v has exactly eight uncovered sites. Deleting U6 and
those sites leaves at least `56-20-8=28` targets in U7. The same argument
forces its affine six-space into `B(v,x)=1`, with either 28 or 32 roots.
In the 28-root case its parallel complementary section has 28 roots,
all live, and six-flat capacity sixteen. It would leave at least twelve
sites uncovered, so that case is impossible. Thus U7 is a 32-root
completion, and its complementary quarter C has 24 live roots. Exactly
sixteen must be in U6. Section 1 gives precisely its fifteen quotient
hyperplane lifts; all are live because C has no frame roots.

The possible completions are in bijection with the 63 root lines w
orthogonal to v. Equivalently, these are the 63 nonzero singular vectors
u perpendicular to v, by `w=v+u`. The root count 63 is the inherited E7
perpendicular-root count. Distinct w determine distinct completions,
because u is the unique nonzero singular vector of `<v,u>`.
There are consequently exactly `63*15=945` equality pairs per frame root,
or 7,560 across its eight directions. Their uncovered eight points always
form an affine three-space and have binary label rank four.

## 5. Nonroot directions and caller scope

For a normal that is not a scalar root direction, inherited root rigidity
gives `|Off(h)|>=70`. The two global capacities give the elementary bound

    e(h;U6,U7) >= 70-20-36 = 14.

This bound is not claimed sharp. In particular, a cover with at most
thirteen extra sites forces a root direction; a frame direction requires
at least eight, and a nonframe direction requires at least five.

The equality classification supplies a complete intrinsic geometric normal
form for the nearby `d=1`, `t=3`, cost-seventeen profile `(7,6,3,1)`.
Its feasibility is uniform, so it cannot be discarded by a stronger
unqualified support obstruction. A decoder application must additionally
use the actual coefficient maps, correction witnesses, restricted duals
and actual-basis surplus hypotheses. None of those follows merely from
this classification. No additional positive-d profile exclusion, marked
invoice floor, C1 completion, decoder floor, physical supplier or new
multiplication exponent is asserted here.

Credit DreamingOfClouds for PR2816's code, cover/circuit framework and
three large target sections, and PR3154's caller context; Nick Petalas for
the retained PR3161/3162 geometry, PR3269/3300 signed-capacity arguments
and adjacent support work; David Arias for the earlier E8 quadratic model;
and joaqcoo and the retained E8/P112 lineage. New derivations in this
supplement are by conorholds with substantial OpenAI Codex assistance.
Internal analytic checking is separate from independent human review and
from a complete proof-kernel formalization.
