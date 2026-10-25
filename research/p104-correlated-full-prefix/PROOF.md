# The maximal full-prefix correlated P104 entrance

Let R=Z[i], pi=1+i, and V=R^512. Addresses are the nine-bit cube.
For S a subset of its bits, write x^S for the corresponding Boolean monomial.
The Gaussian Newton lattice is

    B = {sum_S a_S x^S : pi^|S| divides a_S}.

Its R-basis is e_S=pi^|S| x^S. The source is the unchanged PR2586 word and
native archive, authenticated by SOURCES.json. All event indices are zero-based.
This statement concerns one nine-bit payload, not arbitrary tensor depth.

The variable initial sources are Y27=y and Y26=-y, for y in B. All other Y
inputs may independently lie in 4B, all N inputs in 2B, and the other initial
public fields in B. These are mathematical entrance premises. Their physical
preparation, storage, routing and recursive costs are not supplied.

Exactness here means that every scalar ADD product is Gaussian-integral and
that every completed coordinate C factor in every native recipe agrees with
its ideal Gaussian-linear factor. Its output must be Gaussian-integral.
The native wrappers are their literal signed permutations. Individual floor
halves inside a C implementation are allowed to round. We do not assert that
each such half equals division by two.

## Result

The reduction below proves that the maximal admitted source set is

    M = { y in B : G_k y is in 4V for each of 24 listed maps G_k }.       (1)

The maps are explicitly defined by the 4-times-scaled literal replay below;
their exact coefficient matrix is reconstructed from the pinned source.
Thus (1) is a finite congruence presentation, rather than an unspecified
existence claim or an assertion that M is diagonal in the original Newton basis.

Exact finite elimination certifies

    B/M = (R/pi)^153 + (R/pi^2)^177 + (R/pi^3)^95 + (R/pi^4)^19,
    [B:M] = 2^868,
    [M:4B] = 2^1180.                                                 (2)

Here + denotes a direct sum. The other 68 elementary factors are trivial.
The complete numerical certificate is RESULT.json, checked by two separate
implementations. The written reduction proves that this computed lattice is
necessary and sufficient for all y, rather than extrapolating literal rounded
execution from basis tests.

PR3449's slice module M_slice contains M. Its independently calibrated index
is 2^280, so [M_slice:M]=2^588. The additional reads therefore remove a strict
part of that slice entrance. M still strictly contains the independent 4B
entrance. These indices are algebraic cardinalities, not bit-storage savings,
operation prices or evidence of a favorable supplier invoice.

## The C-factor exactness test

For Gaussian integers a,b, the ideal factor is

    C(a,b) = ((a+b+i(a-b))/2, (a+b-i(a-b))/2).

Write a-b=u+iv, with u,v integers. Both outputs are Gaussian-integral exactly
when u and v have the same parity, equivalently pi divides a-b.

The literal signed-floor implementation sets d=a-b, s=b+floor(d/2),
t=i*d and l=s-floor(t/2), with componentwise floor. It returns (l+t,l).
If u,v have the same parity, floor(u/2)+ceil(v/2)=(u+v)/2 and
floor(v/2)-floor(u/2)=(v-u)/2. Its two outputs therefore equal the ideal pair.
This also covers negative odd integers. If the parities differ, the ideal
pair is nonintegral and cannot equal a Gaussian-integral literal pair.

Consequently, for integral operands, integrality of the next ideal C output
is necessary and sufficient for exact literal execution of that factor.
This is the parity implication from PR3382, spelled out at the boundary used
here. The 256 pair residues in test_controls.py are a finite arithmetic control.

## Isolate the correlated variation

Subtract the reference execution with the two variable Y inputs zero.
The retained Newton-alphabet theorem makes each native prefix a B-automorphism.
For the reference execution, propagate pi reserves 4 on Y, 2 on N and 0 on
other initial fields. A native factor or wrapper preserves a reserve. At an
ADD d+=c*s the destination reserve is at least min(t_d,t_s+v_pi(c)).
The exact source ledger checks all 1,038 ADDs; every product reserve is
nonnegative. Thus the reference prefix stays in B with exact ADDs and exact
literal C factors. This is the independently sufficient product premise from
PR3406, restricted here to this prefix. It is credited, not a new product bound.

The ideal correlated variation is Gaussian-linear in y. Multiply its state
by four, denoting the resulting fields by v. Initially v_Y27=4y,
v_Y26=-4y, and the other v fields are zero. The complete prefix contains
1,038 ADDs, 883 transports and 104 signs. Forward source projection isolates
12 nonzero variation reads, all quarter reads of these Y sources, and 26
active native occurrences. No sign acts on an active variation.

The three actual cancellations are at events 1129 on D31, 1329 on D10 and
1492 on D20. The primary checker verifies all three zero maps on every e_S;
Gaussian linearity proves these cancellations on all B. It may then omit
later native operations on these zero variations. The secondary checker
uses forward dependency sets, retains those operations and removes only
congruence blocks whose complete matrices vanish modulo four.

For clarity, the quarter reads are:

| Destination | Event indices |
|---|---|
| D31 | 1090, 1129 |
| D12 | 1096 |
| D10 | 1190, 1329 |
| D20 | 1303, 1492 |
| D24 | 1499 |
| D4 | 1681 |
| D1 | 1763 |
| D23 | 1869 |
| D16 | 1937 |

The scaled ideal replay is integral on every e_S, including every C-factor
cut. Therefore its corresponding maps are integral on all B, by Gaussian
linearity. This finite-column fact does not assert that the *unscaled*
variation is integral on B.

At each of the 12 reads, record its scaled addend. At every C-factor output
in all 26 active occurrences, record its scaled state. There are 42 recorded
checkpoints. Eighteen complete congruence blocks vanish modulo four on every
Newton basis vector, including the source-path checks. All 24 remaining maps
are listed, in order, in RESULT.json's checkpoints field. They consist of the
12 addends and 12 destination C-factor outputs. Wrapper cuts need no extra
constraint because signed permutations preserve 4V.

Induct over the literal prefix. Its reference state is integral. At an ADD,
the variation's product is integral exactly when its scaled addend belongs
to 4V. For a native factor with already integral physical input, the next
ideal output is integral exactly when its scaled variation output belongs
to 4V. The C-factor test then proves literal exactness. Signs and wrappers
preserve integrality. Zero variations require no additional condition.
This proves sufficiency of (1) for every allowed dirty reference state.
Conversely choose that reference state zero. Failure of a condition gives a
nonintegral product or ideal C output, so the requested exact execution is
impossible. This proves necessity and maximality.

## A finite matrix over R/4R

Write y=sum_S b_S e_S. For each retained checkpoint and each of its 512 output
addresses, evaluate the scaled ideal replay on each e_S. These coefficients
form a 12,288 by 512 Gaussian matrix A, reduced modulo four. Its complete
canonical bit-plane digest is in RESULT.json. The exact condition is

    A b = 0 modulo 4.

The discarded blocks are zero on each e_S, so omitting them is an exact
linear implication. No inequality, approximate arithmetic or randomized rank
computation enters the matrix. Since all scaled outputs are integral, 4B is
in the kernel, and the calculation takes place in (R/4R)^512.

To compute its image size, realify each Gaussian row c=a+ib into the two rows
[a,-b] and [b,a]. This gives a matrix over Z/4 on 1,024 real input variables.
Unit pivots can be normalized and eliminated by invertible operations.
If there are u unit pivots, the remaining matrix is twice a binary matrix of
rank e. Elementary diagonalization gives image size 4^u*2^e. Streaming unit
elimination followed by binary elimination implements this reduction.

A separate algorithm computes the row-generated subgroup G. Reduction modulo
two has a binary basis of rank u. Relations between its lifts, together with
their doubles, generate G intersect 2(Z/4)^1024. If that subgroup has binary
rank t, then |G|=2^(u+t). The same diagonalization shows that row and column
images have equal cardinality. This addition-only algorithm uses different
pivots and does not normalize or eliminate unit coordinates from the even
residual system. It agrees with the primary calculation. Both algorithms
also agree with exhaustive image/kernel counts on all 256 two-by-two Z/4
matrices, including nonunit and carry cases.

For k=0,1,2,3 compute F(k)=log2 |image(pi^k A)|. The exact certificate is:

| k | Primary unit pivots | Primary even rank | F(k) |
|---|---:|---:|---:|
| 0 | 133 | 602 | 868 |
| 1 | 19 | 386 | 424 |
| 2 | 0 | 133 | 133 |
| 3 | 0 | 19 | 19 |

Because R is a principal ideal domain and the kernel contains pi^4 R^512,
its quotient has elementary exponents 0<=e_j<=4, with
F(k)=sum_j max(e_j-k,0). Successive differences yield multiplicities
68,153,177,95,19 for exponents 0,1,2,3,4. Their weighted sum is 868, proving
(2) from the exact finite certificate.

## Separating and admitted physical inputs

The separating y has only these nonzero Newton coefficients, written as
(mask,real,imaginary):

    (0,2,2), (1,0,-4), (8,-4,-4), (9,4,4), (16,-4,-4),
    (17,4,4), (24,8,8), (25,-8,-8), (129,-4,4).

Each satisfies B's weight divisibility. In PR3449's window coordinates,
w=-4*x_1. Thus the slice quarter and bit-zero difference conditions hold.
The literal full-prefix check finds its first failure at event 1190,
D10+=Y27/4, address zero. Its scaled addend is -2+2i, so its requested
physical addend is (-1+i)/2. Every earlier recorded condition holds.
This is a source-bound failure of that proposed entrance, not a rounding
instability or a claim that all correlated callers fail.

There is also a complete-prefix admitted source outside 4B:

    y = pi^3 * (e_0+e_162+e_170+e_490+e_506+e_507+e_510).

Its constant Newton coefficient has pi valuation three, so y is not in 4B.
Its coefficients solve the mod-pi residue kernel of A. Therefore A y is zero
modulo pi^4, proving admission. Both implementations additionally replay this
literal source. The independent full physical fixture puts it into the two
Y banks, assigns nonzero product-domain values to the other 356 initial
fields, and executes all 2,040 events through the first collector. All scalar
products and native C-factor outputs are exact and the private erase is
literal zero. A wrong cleanup sign is rejected. This finite fixture does not
extend the theorem to the remaining word or prove a favorable physical bill.

## Limits, sources and next decision

The new result is a maximal finite congruence presentation and certified
one-layer quotient for this fixed two-source correlation and complete first
prefix. It does not classify arbitrary correlations among the 58 cone banks,
construct an encoder, analyze general rounded trajectories or admit the other
3,373 word events. Other correlations, payload tensor depth, finite register
width, actual native-child realization and a complete physical consumer remain
open. The original Gaussian Newton alphabet and native/physical semantics
retain their predecessor assumptions. Human and proof-kernel review are unclaimed.

PR3423's unchanged-profile supplier stop remains. No kappa, selected frontier,
complete supplier or multiplication theorem changes. The next useful caller
must prepare this entrance and preserve the noncone recipients with explicit
ownership, restoration and a fully charged invoice before implementation grows.

Credit Nick Petalas/PR3449, PR3426, PR3406 and PR3416; Clear1nsight/PR3382 and
PR3423; ywz65/PR2586; Arham Tahir/PR2665; Tekalign/PR3025; Ross Richardson/PR3068;
and the retained native, geometry and compiler lineage. New work is Apache-2.0.
The retained proof texts and their notices are unchanged in inputs/.
