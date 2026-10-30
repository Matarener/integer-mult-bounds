# Minimal standard-dot embedding of the two-cube restriction

This is an exact finite geometry and scalar fitting result. It supplies no
Gaussian native word, phase compiler, dirty-return schedule or kappa claim.
The input is the literal E8 data underlying #5439, pinned in `embed.py`.

## 1. The restriction and its bilinear space

Use cube a with root support (0,1,2,3), cube b with root support
(0,1,4,5), and fix both remaining factors to cube a. There are
16*8*8=1024 distinct concatenated binary vectors in F2^27. The scalar
pairing is the ordinary binary dot product. Each vector has norm one.

The verifier computes their actual span V and proves

    dim V=12, rank(B|V)=4, dim rad(V)=8.

These are ranks of the literal 27-bit vectors and their exact Gram form,
not ranks of a floating numerical address evaluator. It lists a
nondegenerate four-space N and an eight-vector radical basis R, and checks
V=N perpendicular R. The restriction on N is nonalternating: V contains
odd vectors, whereas every radical vector is even.

## 2. An explicit optimal I20 embedding

Let r1,...,r8 be the listed radical basis. Add formal d1,...,d8 satisfying
B(ri,dj)=delta_ij and B(di,dj)=0, all perpendicular to N. The resulting
20-space is nondegenerate with form N perpendicular H^8, where H has
Gram [[0,1],[1,0]]. Its full 20-by-20 Gram matrix is in EMBEDDING.json.

`orthonormal_basis` splits off norm-one vectors. If an alternating
hyperbolic part remains, it uses the explicit identity

    o,e,f -> o+e, o+f, o+e+f

for a unit o perpendicular to a hyperbolic pair e,f. The three new vectors
have norm one, are pairwise perpendicular, and form the same three-space.
Since N is nonalternating, at least one unit is available. Repeating gives
the twenty listed vectors with Gram I20. Thus no 21st coordinate is required
by the characteristic-two norm functional.

For a raw vector x in V, solve its coordinates in the listed basis (N,R),
append eight zero d-coordinates, and send it to

    phi(x) = ( B(x,o1), ..., B(x,o20) ).

Because the oj are an orthonormal basis of the completion, phi is injective
and preserves B. The receipt contains all 1024 q20 values, all twelve raw
basis images, and the full coordinate/orthonormal basis information. The
checker additionally compares all 1024^2=1,048,576 ordered Gram entries,
checks distinctness and norm one, and checks image-span dimension twelve.

This ambient dimension is minimal for any injective isometric embedding
into a nondegenerate symmetric space W. Indeed rad(V) is an eight-space
and V is contained in its orthogonal complement in W. Hence

    12=dim V <= dim W - 8,

so dim W>=20. This lower bound is about preserving all vector identities
and pairings, not merely realizing the orthogonality graph.

## 3. The four common eight-space pairs survive unchanged

The sixty-four polarized H_ab rectangles have four distinct pairs of
source/read spans. Each pair has sixteen channels, and each side uses
128 literal fields. The four source sets partition cube b's 512 fields;
the four reader sets partition cube a's 512 fields.

All four pairs retain source/read dimensions eight, each self-pairing rank
two, and zero cross-pairing. Every listed original vector and every linear
combination has the same pairing after phi. Therefore these properties
are preserved by the explicit I20 embedding, rather than inferred from
matching field names or nominal rank labels. Each common frame basis and
its complete field set is in `orthogonal_eight_space_pairs`.

For the physical H_ab-only module, the dimensions permit the proposed
geometric paths qline -> S8 -> full20 and ground -> S8 -> qperp19, with
Gaussian rank differences 7,12 and 8,11 respectively. The corresponding
25-dimensional paths have 7,17 and 8,16. This removes five spectator axes
from each path. It does not prove a native word or remove the actual
Gaussians, independent scratch inputs, phases, dirty cleanup, or global
caller obligations. A new canonical-frame implementation must use these
actual q20 values and preserve all absolute tensor-width phases.

## 4. An exact scalar minimum fitting rank: 256

Choose an orthonormal basis of N. Quotienting V by rad(V) identifies its
pairing form with I4. The 1024 literal vectors give precisely the eight
odd vectors of F2^4, each repeated n=128 times.

Write Ai for the unit vector ei and Bi for 1111+ei, i=1,...,4. Within
either A or B, different types are orthogonal. Across Ai and Bj they are
orthogonal exactly when i=j. Within a single type, all distinct vectors
pair to one, so a fitting matrix has identity n-by-n diagonal blocks.
Here fitting means diagonal entries one and an off-diagonal entry forced
zero whenever the two binary vectors have pairing one; allowed entries
are arbitrary complex numbers.

Two distinct nonorthogonal types, for example quotient values 1 and 7,
give a forced identity principal submatrix of size 2n=256. This proves
rank(F)>=256 for every such complex fitting F.

For the matching upper bound, order each of the four A-type buckets and
form 128 cliques by taking the kth element of each bucket; do the same
for the four B-type buckets. On each four-clique set F=J4, with all other
entries zero. Each clique consists of four mutually orthogonal norm-one
vectors, so its binary span is nondegenerate of dimension four. The full
matrix is a direct sum of 256 rank-one blocks, is fitting, and has rank256.
All 256 partitions are explicit in the receipt and checked against q20.

## 5. Every minimum-rank fitting has F^2=4F

The following argument proves more than the particular clique partition.
Let F be any complex fitting matrix of rank 2n, with the eight type blocks
of size n. Factor F=UV through a 2n-dimensional space. Write U_Ai for the
n rows of U at type Ai and V_Ai for the n columns of V there; define
U_Bi,V_Bi likewise. Since U_Ai V_Ai=I_n and U_Bi V_Bi=I_n, each U block
is surjective and each V block is injective.

For fixed i and j different from i, the forbidden cross block gives
U_Ai V_Bj=0. Thus each n-dimensional image im(V_Bj), j!=i, equals the
n-dimensional kernel ker(U_Ai). For any j,k there is an i different from
both, so all four im(V_Bj) equal one common n-space W_B. Therefore every
U_Ai annihilates W_B, including im(V_Bi). The four allowed matching
cross blocks also vanish. Interchanging A and B proves the opposite
cross blocks vanish as well.

Consequently F=diag(A,B). Both diagonal blocks have rank at least n
because their type diagonal blocks are I_n. Their ranks sum to 2n, so each
has rank exactly n. Factor A=PQ through an n-space, with four block rows
Pi and columns Qi. The equalities Pi Qi=I_n show that Pi and Qi are square
inverses, so also Qi Pi=I_n. Hence

    QP=sum_i Qi Pi=4 I_n,     A^2=P(QP)Q=4A.

The same argument gives B^2=4B. Thus F^2=4F for every minimum-rank fitting
matrix, without symmetry, positivity, rationality or a chosen partition.
In characteristic zero, F has eigenvalue four with multiplicity 2n and
zero otherwise. Therefore

    (I-F)^-1 = I+F/3,       det(I-F)=(-3)^(2n)=(-3)^256.

If F is dyadic, its inverse has diagonal entries 4/3 and is not dyadic.
This is a property of the minimum-rank code. It is not a physical
impossibility theorem: fixed odd rational scalars are allowed by the
retained implementation contracts when their actual work, grid and
precision are supplied. In particular the canonical coded-native
PHYSICAL.md explicitly implements a 1/52 inverse coefficient and requires
its finite precision bill. The centre-code-services package supplies
literal MULTIPLY_ODD/DIVIDE_ODD words and exact typed-grid obligations.

## 6. Construction relevance and prior art

The clique code K=I-J4 is a common-frame scalar code. Its exact inverse is
I-J4/3, not itself. The generic `block_word` in the pinned canonical
`check_clique_codes.py` already implements I-J_s and its inverse for an
arbitrary clique block of size s. Setting s=4 gives exactly this code:
three ADDs subtract the pivot from the other fields; the pivot is scaled
by -3 and subtracts those three fields; three ADDs add the pivot back.
The inverse uses the corresponding odd division by three. These are
ordinary scalar words on arbitrary inputs, using no extra fields.

The existing centre-code-services README explicitly describes signed
clique responses, their rational inverses, full input-grid conditions,
and the open routed/typed/native caller obligations. Accordingly this
scalar four-clique code is not a new producer family and is not being
reimplemented or packaged as an innovation here. The new source-bound
constructive aid is the optimal I20 realization preserving the four
common polarized eight-space interfaces. The active physical construction
remains the H_ab module, whose phases, full inputs and bill must be proved.

The finite checker corroborates this proof's literal geometry, embedding,
partition and independent-set lower bound. The arbitrary-complex
rank-factorization theorem in section 5 is a written proof; a census of
arbitrary fitting matrices is neither attempted nor claimed.
