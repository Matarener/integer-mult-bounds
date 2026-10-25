# Selected signed-pair feedback without a vector helper

This note combines Clifford/Pauli algebra with segmented in-place linear
networks and block scheduling. Its new result is an exact source-bound
implementation and its processed-volume ledger. It does not claim a new
Fourier transform algorithm or an asymptotically sub-fV construction.

## 1. Source boundary and changed operation contract

The immutable selected source is pinned in SOURCES.json and by archive-member
hashes in verify.py. Forward phase-B events12806 and13402 are rank-one
children A:0→2 and B:2→252 on register195. Their available direct rank-two
child is C:0→252. The only intervening event touching195 or donor521 is12807,
`L195 += L521/2`. Every other intervening operation acts on disjoint registers
and is retained unchanged. Fresh complete-basis evaluation verifies BA=C,
including global phase, and

    B=aI+bP,    a=(1+i)/2, b=(1−i)/2,
    P e_t = (−1)^parity(96&t) e_(t xor224).                    (1)

P is an involution. The second factor A=aI+bR has
`R e_t=i³ (−1)^parity(14&t) e_(t xor30)`. R and P are commuting independent
involutions. Their128 four-coordinate orbits have monomial charts
`R^r P^p e_t`, in which they are the two independent bit flips. Every source
column and every orbit chart is checked; no endpoint-only assumption is used.

For positive f, A_f,B_f,C_f are the inherited tensor lifts, and arbitrary
identity spectators are retained. A single payload has V=512^f times the
spectator multiplicity coordinates. Arbitrary physical x,y must exit as

    (x,y) ↦ (C_f x + B_f y/2, y).                             (2)

The new operation class allows fixed coordinate-subset shears inside a
payload: add a rational multiple of one specified coordinate to a distinct
coordinate, plus signed/unit-phase coordinate monomials. Each touched target
coordinate is charged, together with source reads, routing and restoration.
The subsets and addresses depend only on f and public source labels, never on
input values. This changes #4009's full-array register-shear premise. It is
not a claim that the inherited common-frame scalar-word checker admits these
new within-register operations. There is one native rank2f child on ONE
V-sized target operand; no enlarged operand or second native call is hidden.

## 2. Exact pair factorization

Orient each P-orbit by the representative t with bit7 zero, and write
u=y_t, v=y_(t xor224), σ=(−1)^parity(96&t). Both directions have the same
sign because parity(96&224)=0. On this pair B is

    K_σ = [[a, σb], [σb,a]].                                 (3)

For σ=1, a direct elementary factorization is

    diag(1,−i) K_1 = E12(−i) E21(−a) E12(1).                 (4)

Here E_ts(c) adds c times coordinate s to coordinate t; products act right
to left. Conjugating by diag(1,σ), splitting −a into its two rational parts,
and combining the final phase gives the following chronological implementation:

    u +=  σ v
    v += −σ u/2
    u ← i u
    v += −σ u/2
    u ← −i u
    v ← i v
    u += −σ v.                                              (5)

To check without a factorization convention, put s=u_old+σv_old. Immediately
before the last two operations the donor pair is `(s,v_old−σ a s)`.
After the phase and subtraction it is
`(s−σ i(v_old−σ a s), i(v_old−σ a s))`, equal to(3) since
`1+i a=a`, `−i a=b`, and `i(1−a)=a`.
The verifier checks both signed2×2 matrices exactly over Q(i).

Each pair uses four rational coordinate ADDs and three unit-phase coordinate
maps. The only rational coefficients are ±1 and ±1/2. No multiplication by
an unpriced nonunit complex scalar, input-dependent lookup, source-mixture
oracle or temporary vector is used. The inverse reverses all seven operations,
negates ADD coefficients and inverts phases. It acts on arbitrary pair values;
there is no zero-data premise.

For every tensor factor j, run(5) on its V/2 disjoint pairs. The factor stages
commute as complete operators, so all f stages compute B_f in place. Execute

    x ← C_f x
    y ← B_f y                  using the signed-pair stages
    x += y/2
    y ← B_f^−1 y               inverse stages in reverse order.       (6)

Equation(6) gives(2) exactly for every x,y and all f. Donor521 returns to its
entry value and frame before its next original touch; target195 has its
original physical output and frame252 at exit. Intermediate donor frames
and within-register operations require the changed compiler contract above.
All other word operations can retain their original relative order because
none touches these two registers in the enclosed interval.

## 3. Arithmetic volume, addressing, storage and recovery

There are fV pair invocations in compute plus uncompute together. Each invokes
four coordinate ADDs and three coordinate phases. The central ADD visits V
coordinates. Therefore the complete added adapter schedule has exactly

    rational coordinate ADD volume       (4f+1)V,
    unit-phase coordinate-map volume       3fV.                        (7)

This counts execution on all coordinates, including zero inputs. The sparse
checker skips all-zero pair states only to evaluate basis fixtures quickly;
that implementation shortcut is not part of the construction or its invoice.
Inverse/restoration operations are included in(7), not postponed elsewhere.

| Item | #4009 feedback construction | This segmented construction |
|---|---:|---:|
| Native children | one rank2f on V | one rank2f on V |
| Rational coordinate ADDs | (26f+1)V | (4f+1)V |
| Source coordinate monomial maps | 36fV | 3fV unit phases |
| Live vector payload | 3V | 2V |
| Additional arbitrary dirty vector helper | V, restored | none |
| Standalone scalar coefficients | halves and units | halves and units |

The rational ADD excess over the original one-ADD boundary falls26fV→4fV,
an exact factor6.5. Total ADD work has ratio(26f+1)/(4f+1), not a claimed6.5
ratio at finite f. The old map count included signed-P permutations; the new
pair addressing below replaces them, so it is not legitimate to present
36→3 alone as total routing-cost improvement. There is no extra whole vector
stock or borrowed dirty return in(6). Native-child stock remains inherited.

An explicit fixed addressing algorithm avoids a V-sized lookup table. Store
the f original9-bit factors in the low9f address bits, with spectators outside.
For stage j put p=9j+7 and m=224·2^(9j). For q=0,...,V/2−1, form

    t = (q & (2^p−1)) | ((q >> p) << (p+1)),
    partner = t xor m,
    σ = (−1)^(((t >> (9j+5)) xor (t >> (9j+6))) & 1).          (8)

The inserted zero at p orients each pair once; XOR m stays inside that factor
and never changes spectator labels. This is a permutation of all V coordinate
addresses partitioned into V/2 pairs. No address or coefficient depends on y.
Constants for one stage are generated from j using O(1) words; control uses
O(1) address words of O(log V) bits, not an exponential descriptor table.
Each pair address uses a bounded number of shifts, bit operations and loop
updates, giving O(fV) address-word work and O(f) stage setup. This is a
word-RAM accounting statement with word width at least ceil(log2 V); it does
not make those address operations free in a bit/tape model.

A direct in-place primitive implementation has at most three coordinate
accesses per ADD (target/source reads, target write), and two per phase
(read/write), hence at most(18f+3)V logical coordinate reads/writes. Loading a
pair into two owned scalar working locations and storing it after all seven
steps can reduce array traffic to(4f+3)V coordinate loads/stores, excluding
native-child traffic; it requires those bounded scalar locations and their
ordinary lifecycle/cleanup. This is an optional RAM implementation, not free
borrowed scratch or a claim about cache misses. The abstract coordinate-shear
schedule itself uses no additional mathematical vector state. A physical host
must account for its scalar primitive workspace and addressing conventions.

At the real/imaginary component level, each rational complex ADD requires two
real additions/subtractions. The half coefficients require two component
halvings. Thus(6) uses(8f+2)V real additions/subtractions and(4f+2)V component
halvings, plus3fV unit phases, each a signed component swap. These figures do
not identify a high-precision operation with a constant-time bit operation.
Routing, scalar-stock implementation and tape realization are declared
obligations beyond this word/coordinate ledger.

## 4. Exact standalone precision bound

Assume both components of each input coordinate lie on2^(−p0)Z. After j
completed forward donor stages the grid denominator divides2^(p0+j), because
B_j has denominator2^j. Within the next pair schedule the first ADD preserves
that grid, its two half-ADDs share the same unmodified u up to unit phase,
and all other operations are additions or unit phases. Thus all intermediate
pair components lie on2^(−p0−j−1)Z; the two halves do not force two successive
new denominator bits. In the inverse direction the current donor is exactly
B_j y at a stage boundary, so the same argument bounds intermediates by
2^(−p0−j−1)Z before the exact inverse reduces to B_(j−1)y.
The entire donor compute/uncompute therefore fits the grid

    2^(−p0−f−1)Z.                                           (9)

This is an upper bound, not a sharpness assertion. The complete exact target
child C_f has denominator2^(2f); central delivery B_f y/2 needs f+1 bits.
For positive f,2f≥f+1, so if the exact native child is included, the entire
algebraic macro fits2^(−p0−2f)Z. Approximate-child errors and production
rounding are separate; this note does not derive their allowable budget.

If max coordinate complex modulus at donor entry is M, a completed j-stage
B_j has row absolute sum2^(j/2), so its coordinates have modulus at most
2^(j/2)M. During(5) or its inverse, the triangle inequality bounds the pair by
5 times its entry maximum. Thus all donor intermediates have modulus at most
5·2^(f/2)M. The target output is bounded by2^f M_x+2^(f/2−1)M_y when the child
is exact. Consequently a fixed coefficient denominator does not mean fixed
precision: integer and fractional storage may grow linearly in f. The stated
exact grid and magnitude bounds permit a finite arithmetic-word invoice;
a full selected approximate supplier still needs its own precision proof.

## 5. A uniform outer-prefix conditioning bound

Treat the exact native child as an atomic unitary operation; this statement
is about the surrounding coordinate network, not the child's internal program.
Every complete signed pair kernel is unitary, since |a|²+|b|²=1 and
`a conjugate(b)+b conjugate(a)=0`. Unit phases are unitary. For a shear
`I+cE_ts`, t≠s, both it and its inverse have spectral norm at most1+|c|
by the triangle inequality. The four coefficients in(5) have absolute values
1,1/2,1/2,1. Hence every partial pair and its inverse have norm at most
`2·(3/2)·(3/2)·2=9`, giving condition number at most81.

At any point within a donor stage, completed pair blocks are unitary, at most
one pair block is partial, and untouched blocks are identities. Their direct
sum and inverse still have norms at most9. Completed factor stages are
unitary, so before the central ADD the full network has condition at most81,
independent of f,V and spectator multiplicity.

A partial central ADD is `I+(1/2)E_xy⊗D`, where D is the diagonal mask of
coordinates already processed. Its off-diagonal part has norm at most1/2
and square zero, so it and its inverse have norm at most3/2, with condition
at most9/4. During uncompute, factor the prefix as partial-pair/direct-sum,
completed inverse unitaries, full central ADD, and completed forward unitaries
(including the atomic child). Submultiplicativity yields the uniform bound

    cond₂(every outer coordinate-program prefix) ≤ 81·9/4 = 729/4. (10)

The same argument covers all individual rational ADD and phase prefixes,
not merely completed butterflies. It supplies a useful concrete condition
parameter for separately investigated bounded-condition volume lower bounds.
No such external lower bound is a premise of this construction or its gate.
This spectral statement does not replace the exact grid bound or prove an
approximate-error, bit-precision or implementation-stability theorem.

## 6. Block scheduling test and budget decision

Grouping g tensor directions into cache blocks does not reduce this network's
arithmetic volume. Every direction still has V/2 pair kernels, and compute
plus undo still total fV kernels. Disjoint pairs or commuting complete stages
can be reordered for locality; the count in(7) is invariant under that
rescheduling. This is a statement about this network, not a lower bound for
all masked or segmented programs. No general sparse lower bound is claimed.

The source exponent is
α=67018507072324140917/40000000000000000000000 with0<α<1. Under the inherited
volume-linear child expression A V(rf)^(1−α), f,f→2f saves at most

    A V δ f^(1−α),    δ=2−2^(1−α)≈0.0023213362673.            (11)

Before synthesis the required target was o(fV) processed volume, ideally
O(V polylog f), because a constant multiple of fV eventually exceeds(11).
The constructed schedule removes a helper and substantially lowers the
constant, but does not meet that asymptotic target. Even crediting the original
ADD and granting all phases, addressing, scalar workspace and precision zero
extra cost, a strict saving needs

    4f < A δ f^(1−α),  equivalently f^α < Aδ/4.               (12)

For every fixed A>0 this eventually fails. This compares this schedule with
an inherited available charge expression; it is not an optimal runtime lower
bound, a finite cutoff without A, or a universal barrier. Any actual invoice
adds the explicit routing and precision costs rather than making(12) easier.

**Decision:** retain this exact no-vector-helper construction and its source
binding, but stop its expansion as a uniform κ proposal. No selected profile,
frontier, global result or cold replay changes. A materially different next
algorithm needs a complete sub-fV processed-volume invoice and legal compiler
contract before further synthesis; block/locality renaming alone does not
supply it. All-size supplier hosting, common-frame admission, tape/routing and
approximate precision remain unproved here.

## 7. Verification boundaries

The registered exact checker verifies both signed pair matrices and inverses,
all1024 source-bound two-register basis inputs, all128 monomial orbit charts,
and complete reduced tensor bases f=1,2,3 (8+32+128 inputs). Orbit charts and
tensor functoriality provide the written all-f reduction, not a claim to have
enumerated every512^f column. It independently enumerates the fixed scheduler's
pair/gate counts and checks nontrivial dyadic-grid fixtures. Four mutants are
rejected: wrong pair sign, omitted phase, reversed order without inverse signs,
and wrong central coupling coefficient. Exact tests are not formal-kernel or
independent human verification. Substantial AI assistance is disclosed.
