# Exact OPEN and reverse carrier interfaces

Scientific pin: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. This local
construction changes the paired complex boundary. It is not an admitted
recursive supplier or a new kappa bound. No ordinary helper or private field
is used by either source-carrier word below.

## Actual geometry and phases

The frozen `D4-BUS-INPUT.json` gives four triples of actual binary root
directions `(p,q,r)=(p,Op,O^2p)`, with groups

    A = [7,2,50,55], B = [13,61,8,56], C = [117,64,69,112].

The core is `(a,b,c)=(7,13,117)`, radical basis `(5,53)`, and dual basis
`(30,96)`. Their Gram matrix is I3 plus two hyperbolic planes. Let D be the
exact real four-point Walsh transform on the radical address coordinates,
with its positive-native phase corrected by `-i`. The exact invariant full
native transform is `F=X_33 F7`. Define

    E_A=D C_a, E_B=D C_b, E_C=D C_c,
    V_A=D C_b C_c, V_B=D C_a C_c, V_C=D C_a C_b.

Every operator here is an actual pinned Gaussian Clifford. In particular
`C_p^2=X_p`, with no dropped global phase. A source p enters C_p and its
paired target enters C_q. The target endpoint is F C_p^-1. The ordinary
paired source endpoint would be F C_q^-1. These are actual representatives,
not a choice of canonical frame based only on a subspace.

## Zero-helper OPEN word

At each of the four radical coordinates, use source A itself as the carrier.
Bring the three sources to E_A,E_B,E_C. Move A to E_B, add it to target A,
then swap A with B. Move the carrier to E_C, add it to target B, then swap
it with C. Move it through V_B to V_C and add it to target C. Advance each
target to its endpoint. The carrier stays at V_C. Two raw whole-field swaps
per coordinate return the three source value lineages to their fixed family
IDs, carrying their actual outgoing frames.

The exact arbitrary-input scalar identity before that final ID cleanup is

    (x_A,x_B,x_C ; y) -> (x_C,x_A,x_B ; y+x_original).

`source_carrier.py` verifies all 24 independent source/target columns, in
normal and optimized Python. It also verifies the exact Clifford phase of
every native query and outgoing lineage. No claim that a swap between
unequal frames is free is used: the final swaps are explicit whole-field
arithmetic, and their transported native operators are retained.

The complete child histogram is

    rank 1: 8, rank 2: 40, rank 3: 16; total rank mass 136.

There are no helper fields or private fields. The scalar word, including ID
cleanup, uses 60 complex ADDs and 16 complex negations, before additional
monomial normalizer scans. Rank-zero address/phase maps must be compiled as
monomials and paid as whole-array scans; their displayed native expressions
are not instructions to execute their unsimplified histories for free.

The resulting physical two-bank boundary at each port is

    [[S_p,0],[J_p,T_p]],
    T_p=F C_p^-1 C_q^-1, J_p=F X_p.

For groups A and B, `S_p=F C_p^-1 C_r^-1`. For group C,
`S_p=V_C C_p^-1`. All source and target channels have native rank 5, so
their coverage is 120 and the local uncovered mass is 16. This accounting
does not, by itself, provide the global source/target endpoint required by
an old caller.

## Normalization of all twelve OPEN ports

For groups A and B an exact orthogonal address transposition R_p fixes p and
swaps q,r. Applying R_p on source input and output normalizes S_p to T_p.
The new physical kernel is `K_p=C_q C_p^-1 R_p`. This is the closed-star
normalization already checked in `source_carrier.py`.

For the four C ports, `SPLIT-LAGRANGIAN.md` proves that a source normalizer
P exists with P, its outgoing correction, and F P F^-1 all monomial. The
parent's `shared-helper-budget/common_frame_normalizer.py` constructs this
family. The independent producer `common_frame_inverse_search.py` checks
that seed using the actual Clifford operators and constructs stronger
explicit members of the same common-cut family. The winners occur after
181,225,311,91 bounded candidates for p=117,64,69,112 respectively. Their
G and quadratic chirp Q, full-phase monomial lowerings and native histories
are in `COMMON-FRAME-INVERSE-SEARCH.json`.

Writing P for the chosen source input monomial and `post=T P^-1 S^-1`,

    post S P=T, K=T^-1 J P=C_q C_p^-1 P.

The resulting normalized forward boundary is exactly

    F_K = [[T,0],[T K,T]].

The actual logical kernel at the paired fronts is

    A=C_q^-1 K C_p=C_p^-1 P C_p.

Physical P and logical A are different operators. A need not be monomial,
orthogonal or involutive. The actual physical implementations of A^-1 at
X entry C_p and completed Y at F C_p^-1 are both monomial. This is checked
for every explicit C-port winner, using tableau and global phase.

The literal inverse of F_K, with bank roles exchanged and T^2 applied to
both outputs, has a generally different inverse kernel. Its exact input and
output corrections are

    AB=T K^-1 T^-1 K^-1, BB=T AB^-1 T^-1.

For all four new winners, both AB and BB are monomial, including their
actual phase. The receipt verifies both the cross and diagonal of the
corrected backward boundary

    B_K = [[T,-T K^-1],[0,T]].

Thus both orientations retain the OPEN histogram of mass 136. The inverse
queries are adjoints of the forward queries with the same Bruhat ranks.
No extra positive-rank correction is hidden in the B wrapper. The receipt
has four named defect controls per port: omitting post, omitting the common
chirp, omitting AB, and substituting K for K^-1 each breaks its stated
contract. Those sixteen checks are mutation sensitivity, not an exhaustive
optimality certificate.

## The common-code algebra and its remaining caller obligation

Let H=A^-1 and use the same logical pre-X H and post-Y H in either
orientation. Direct block multiplication, without an involution or
commutation assumption, gives

    diag(I,H) [[I,0],[A,I]] diag(H,I)
      = diag(H,H) [[I,0],[I,I]],
    diag(I,H) [[I,-A^-1],[0,I]] diag(H,I)
      = diag(H,H) [[I,-I],[0,I]].

A common diag(H,H) commutes with the scalar integer shear matrix even when
different stages' H operators do not commute with one another. This is the
correct chosen relay algebra. A possible rank-four lower bound for a
different, source-oriented pre-Y correction is not a cost of this relay.

What remains is an actual routed multistage word. It must verify the
pre-X/post-Y physical cuts under every accumulated port chart and previous
code, retain the chronological product of common H factors, and either
absorb or explicitly decode that endpoint. A scalar augmentation fixture
does not settle the routed operator product. Owner matching, public banks,
padding, the final native missing directions and all terminal restores must
be priced for that actual word. The parent and algebra lane own this
dependent obligation; the local alphabet here does not close it.

The subsequent `ENDPOINT-GAUGE.md` review identifies a terminal rank debt in
the specific shared-common2/disjoint-fresh/common-code relay. Every C port
misses four directions and every A/B port misses at least two, uniformly
over the common-F normalizer family. This is a debt of that caller, not a
failure of the all-input local OPEN word or a caller-independent bound.

## Reverse full-source carrier resource

The frozen `reverse_carrier.py` instead moves source A through

    C_p -> E_A -> V_A -> V_C -> V_B -> F C_q^-1
       ranks 2,3,2,2,2.

It delivers target A before swapping with C, target C before swapping with
B, then target B. Sources B/C and all targets have paths [2,1,2]. After the
eight raw ID cleanup swaps, all twelve source lineages have native operator
`J_p=F X_p` of rank 7. Targets retain T_p of rank 5. The complete histogram is

    rank 1:20, rank 2:56, rank 3:4; total mass144,
    coverage12*7+12*5=144; uncovered mass zero.

All 24 arbitrary columns and native phases are checked. Source rank seven
is a resource and must not be silently normalized down to rank five. The
raw forward boundary is `[[J_p,0],[J_p,T]]`. With source entry q, target
entry p and partner O^-1, the flipped backward boundary is

    [[T,-J_q],[0,J_q]]
      = T [[I,-Kold^-1],[0,Kold^-1]], Kold=C_q C_p^-1.

This flipped orientation and the same-prototype backward orientation are
different; the latter has J_p in the cross. A changed caller may consume the
extra two source directions to fill a real terminal vacancy, but that claim
requires its complete operator word and actual fronts. The zero excess of
this local box does not establish that such a global use exists.

## All-size meaning and costs still open

Each displayed actual Clifford product and each source/target scalar word
tensors columnwise over every chunk parameter f. Monomial normalizers remain
address permutations and pointwise Gaussian units under this lift. Operator
identities are not replaced by a finite-character approximation. In
particular no four-translation expansion at f=1 is charged as four scalar
ADDs for arbitrary f: its tensor support would have 4^f terms.

All target and source inputs are arbitrary Gaussian dyadics. The exact
local identities have no dirty helper to restore. Their scalar prefix,
native child precision, rounded cleanup, global bank stock and physical
tape implementation still need the full routed caller and its inherited
error contract. No positive kappa or complete joint supplier is asserted.
