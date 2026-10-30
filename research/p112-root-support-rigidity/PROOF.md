# A four-piece P112 representation obstruction

Let R be the 120 canonical doubled E8 root lines, F the fixed orthogonal
frame of eight lines, and P=R\F the literal P112. Use the pinned leading-one
nine-bit labels ell(r). Over any characteristic-zero field K, write

    C = {c_h=(r dot h)_(r in P) : h in K^8},
    w(q) = rank_F2 {ell(r) : q(r) != 0}.

Theorem. If four arbitrary vectors q0,q1,q2,q3 have support-rank bounds
2,5,6,6, respectively, then

    C intersect span_K(q0,q1,q2,q3) = {0}.

The pieces need not be independent or have disjoint supports. Their
coefficients, overlaps and cancellations are unrestricted. This proves a
necessary quotient contract for the historical `2,5,6^8` caller below. It
does not exclude that full caller.

## Full-root section rigidity

For a root normal a, put O_a={r in R : r dot a != 0}. Let V be any binary
subspace of the nine-bit label space, of dimension at most d. Set
H(V)={r in R : ell(r) in V}. The following finite lemmas are new here.

* If d=5 and |H(V) intersect O_a|>=11, then H(V) has exactly twelve roots,
  lies entirely in O_a\{a}, and is invariant under the root reflection s_a.
* If d=6 and |H(V) intersect O_a|>=17, the corresponding conclusions hold
  with exactly twenty roots.

Both numeric thresholds are sharp for these conclusions. RESULT.json gives
actual full-root sections with binary dimensions 5 and 6 and off-normal
sizes 10 and 16, respectively, which fail reflection invariance. Its masks
use bit i for root i in the sorted full 120-root inventory. The control
script checks the dimensions, sizes and failure, rather than merely reading
the listed thresholds.

Here is the exhaustive proof and its scope. At a=R[0], the primary enumerates
all 3,309,747 five-spaces and 788,035 six-spaces in F2^9. Each is the kernel
of one unique reverse-echelon annihilator. For each space it computes the
actual full-root section and its off-normal intersection. The global full-root
capacities are twelve and twenty. Every intersection above the stated
threshold has full section equal to its off-normal section and invariant
under s_a. There are 1,260 critical five-spaces and 336 critical six-spaces.
All section sizes, the complete off-normal histograms, critical support-set
digests and boundary sections appear in RESULT.json.

The separate program enumerates affine four- and five-spaces of F2^8 using
forward generator bases and complementary coset representatives. These are
exactly the sections of binary five- and six-spaces on the leading-one
hyperplane. It directly reconstructs all 3,212,592 and 777,240 affine
sections. Binary spaces contained in the leading-zero hyperplane have empty
root sections; their Gaussian-binomial counts are 97,155 and 10,795.
Adding those zero entries gives the same complete histograms and every
critical-support digest. The second program uses a separate set-based
reflection check. The engines share authenticated geometry and digest
encoding, so this is computational corroboration, not independent human or
proof-kernel review.

The replay checks all 960 root/simple-reflection label identities. In
simple-root coordinates a reflection changes coordinate j by an integral
Cartan linear combination. Modulo two this is an invertible linear map on
the leading-one label space. The generated orbit of R[0] contains all 120
root normals. Consequently each full-root section statement transports to
every a, with its reflection-invariance conclusion. This transport does not
claim that a Weyl transformation preserves the fixed frame F. The frame is
handled literally after transport. Lower-dimensional V extends to dimension
d; the near-threshold points already force dimension d because a leading-one
set in dimension d-1 has at most 2^(d-2) points, namely eight or sixteen.

## Why the codeword must be a live root normal

The replay establishes full-root support capacities 12 and 20 for ranks
five and six. Leading-one rank-two supports have at most two points. Thus
any proposed four-piece codeword has support at most

    2+12+20+20 = 54.

We use the standard finite-root-system Weyl-chamber theorem, as in the
pinned root-simplex proof. A nonzero characteristic-zero root-evaluation
codeword with support below 70 is proportional to a root codeword. The
finite ingredients are replayed here. A six-node parabolic has at most 36
root lines; the seven-node faces have counts

    42,28,22,14,16,23,37,63.

A support below 70 leaves at least 43 live perpendicular roots, so only the
last seven-node face is possible. Its normal is a root. To pass from real
to arbitrary characteristic-zero coefficients, the rational perpendicular
roots must have rational rank seven. Otherwise a generic real normal would
contradict the rank-six bound 36. Their one-dimensional rational kernel
generates the field-valued normal after scalar extension. This argument
also gives minimum live support 53. Direct enumeration gives support 53 for
every live root normal and 56 for each frame normal. Hence a proposed
nonzero word of support at most 54 has normal a in P and support E of size
53. The standard Weyl theorem is an inherited mathematical premise, not
formally proved by the executable.

## Slack one forces reflection-closed containers

Absorb the four scalar coefficients into the pieces, so that their sum is
the proposed root codeword. Let M_i be their actual support sizes, let
c=(2,12,20,20), and let k_r count their nonzero entries at r. Every r in E
has k_r>=1. The exact nonnegative slack identity is

    1 = 54-53
      = sum_i(c_i-M_i)
        + sum_(r outside E) k_r
        + sum_(r in E)(k_r-1).

Let J_i count sites in E where piece i alone is nonzero. Each nonsingleton
incidence of one fixed piece is bounded by the last overlap sum. Therefore
c_i-J_i<=1, giving J_1>=11 and J_2,J_3>=19.

Extend each large piece's binary support span to the relevant dimension.
Its singleton sites lie in O_a and reach the rigidity threshold. Its entire
support therefore lies in a full-root section H_i of size c_i, invariant
under s_a and excluding the normal root a. Write

    delta_i = c_i-M_i.

Every frame root in H_i is absent from the live support and consumes one
unit of delta_i. The slack identity gives sum_i delta_i<=1.

For every live a the literal frame has exactly four members f with
f dot a != 0. Each has a distinct reflection partner p=s_a(f) in P\{a},
and each p lies in E. All 112 such four-partner inventories are checked.
Since the large containers exclude a, the small piece must cover a. It
has at most two support sites, so covers at most one of the four partners.
At least three partners must be covered by the large pieces. Reflection
invariance then forces the three distinct missing frame partners into their
respective containers. Even if a live partner belongs to several pieces,
choose one that covers it. Within each chosen piece distinct live partners
have distinct frame preimages. Consequently

    delta_1+delta_2+delta_3 >= 3 > 1,

a contradiction. This proves the theorem. The proof does not restrict values
on nonsingleton sites or assume cancellation is absent.

## Exact consequence for the literal caller

Suppose ten independent pieces have bounds `2,5,6^8`, span T, and satisfy
dim(T intersect C)>=6. The quotient T/(T intersect C) has dimension at most
four. By the theorem, the two small pieces together with ANY TWO distinct
rank-six pieces have no nonzero codeword in their span. Their four quotient
images are therefore independent. The quotient dimension is exactly four,
and the code intersection dimension exactly six.

After quotienting further by the two small images, the eight rank-six
images lie in a two-dimensional space. Any pair is independent. They are
therefore eight distinct projective endpoints in P1(K). This is a necessary
condition, not a contradiction over characteristic zero. It rules out every
caller argument that assumes a collision of two such endpoints, and pins
the remaining problem to distinct endpoints and three-piece relations.
No finite-field point count is applied to K.

## Scope and credit

This is a computer-assisted finite section lemma, a written four-piece
representation theorem under the standard Weyl premise, and a partial caller
consequence. Full `2,5,6^8` exclusion, the historical public unresolved count,
full C5, C(P112)>=64, actual decoder/consumer/restoration/hosting costs,
supplier admission, multiplication and a new kappa remain unproved here.
No selected-frontier change follows. Lean, Docker, selected cold replay,
independent human and proof-kernel review are unrun.

Credit Nick Petalas's PR3295 for the explicit caller handoff, PR3289 for the
historical quotient contract, PR3161/3162 and the root-simplex geometry,
DreamingOfClouds/PR3154, joaqcoo and the retained E8/P112 lineage.
New work and pinned inputs are Apache-2.0.
