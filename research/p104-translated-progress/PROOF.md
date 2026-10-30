# Symplectic width, translated progress and the P104 adapter boundary

## 1. Question and exact scope

PR3954 and PR3962 condition their two-axis cost screens on at most 2312 units
of persistent progress per unchanged P104 call. This study supplies a proof
for a named, broad class of **matched translations of the intrinsic endpoints**,
and an actual canonical-frame counterexample showing why the intrinsic
endpoint qualification cannot be omitted. It does not prove that every
translated program retains the old paid profile, preserves the caller's
initial credit, or implements a new supplier.

The argument combines the binary symplectic description of Clifford address
operators with elementary rank-distance inequalities. These are standard
linear-algebra tools; the source-bound endpoint application and adapter
counterexample are the contribution. All matrix ranks in this note are over
F2. They are not rational operator ranks on arrays, tensor rank, or arbitrary
scalar-operation lower bounds.

## 2. The native width and a progress potential

Use Pauli coordinates (x,z), with X^x Z^z, and the unsigned symplectic matrix

    M = [A B; C D],       phi(M)=rank(B).

The pinned native compiler `vendor/clifford_exact.py:lower_child` sets its
positive child width to the rank of the X parts of the images of the Z
Paulis, exactly phi. Its `monomial` class has B=0. A child C on r independent
address bits has B of rank r. Binary address permutations, quadratic
fourth-root diagonal phases, Pauli translations and scalar phases have B=0.
Their physical work is still paid; saying phi=0 does not make them free.
The source compiler supplies a one-child normal form. For the bound below,
only the lower-bound direction is needed: any factorization into these
monomials and rank-r children has sum r >= phi of its product.

Indeed,

    B(MN)=A(M) B(N)+B(M) D(N),
    phi(MN)<=phi(M)+phi(N).

For a symplectic matrix, M^-1=[D^t B^t; C^t A^t] in characteristic two, so
phi(M^-1)=phi(M). Thus

    |phi(M)-phi(N)| <= phi(M N^-1).

One can instead use N^-1 M by factoring on the other side. A monomial factor
on either side preserves phi exactly: its relevant A or D block is
invertible. In contrast, arbitrary Clifford conjugation need not preserve
phi. Conjugating an X rotation by a Hadamard turns it into a diagonal Z
rotation, changing positive width from one to zero. The Hadamard and any
other inserted transformations require their own invoice.

For a program with a separate invertible Clifford chart Gamma_r on each
persistent physical role, use Phi=sum_r phi(Gamma_r). Native transports pay
at least each signed increment of Phi. Scalar additions in an identical
chart do not change charts or Phi, regardless of the logical row coefficients.
A role permutation preserves the sum, but its realization/return is not
thereby free. Summing the signed increments telescopes; decreases cannot be
credited twice. Remaining work made from this named grammar therefore pays
at least max(0,Phi_final-Phi_current). For the required full tensor endpoint,
phi(F_m)=m on each original role. This proves the relevant native-progress
inequality when the role-local/common-chart invariant actually holds.

This statement does not cover a general matrix of address operators coupling
several physical roles, a non-Clifford scalar algorithm, unproved owner
relabeling, or changed initial/final contracts. Those need a new potential or
an explicit comparison. Arbitrary dirty inputs cannot simply be deleted from
the endpoint sum.

## 3. A matched-translation theorem

Let Gamma_in and Gamma_out be two endpoint charts in the same ambient
Clifford space. Put K=Gamma_out Gamma_in^-1 and let

    delta(K)=rank(M(K)-I).

This full symplectic defect is conjugacy invariant. It is only an upper
bound on phi, not a native tariff: B is a submatrix of M-I, giving
phi(M)<=delta(M). For arbitrary fixed Clifford L and R, set

    Gamma_in'=L Gamma_in R,
    Gamma_out'=L Gamma_out R.

Then Gamma_out' (Gamma_in')^-1=L K L^-1, and consequently

    |phi(Gamma_out')-phi(Gamma_in')| <= phi(L K L^-1)
                                               <= delta(K).       (1)

Equation (1) permits arbitrary ambient symplectic L/R, spectator coordinates,
inverse orientation, phases, and nonorthogonal binary address descriptions.
It is a theorem about matched endpoints. It does not assert that every such
translation is legal at every internal addition, has the same native cost,
or supplies the prescribed global endpoint. Different translations at the
two ends introduce another operator and are outside (1) until that operator
is included and paid.

If only one side is translated, the sharper phi(K) or phi(Gamma_in^-1
Gamma_out) triangle can suffice. The conjugacy-invariant defect is useful
when both sides vary. No claim is made that a large defect lower-bounds the
cost of a translation; the inequality is in the opposite direction.

## 4. Intrinsic P104 endpoints and sharpness

The source native proof and compiler specify, for each odd physical root
label q in F2^9,

    C_q=((1+i)I+(1-i)X_q)/2,
    F_9=product_j C_ej,
    M(C_q)=[I q q^t; 0 I],       M(F_9)=[I I;0 I].

The scalar sign of C_q or its inverse does not affect its unsigned
symplectic action. Since q^t q=1, I+q q^t has kernel exactly span(q) and rank
8. The 280 intrinsic chart endpoints are therefore:

| Roles | Entrance | Exit | Relative symplectic defect |
|---|---|---|---:|
| 104 X | C_q | F_9 | 8 |
| 104 Y | I | F_9 C_q^-1 | 8 |
| 72 dirty helpers | I | F_9 | 9 |

Each relative matrix has just the displayed upper-right block, so its defect
is exactly 8, 8 or 9. Applying (1) separately to every legally retained role
bounds total signed progress by

    104*8+104*8+72*9=2312.

The original intrinsic endpoints attain equality, proving sharpness for this
endpoint specification. Inverse-oriented calls have the same absolute cap;
this is not a proof that the required opposite-oriented physical caller
exists. Phase/global-sign equality remains a separate implementation
obligation; unsigned rank checks do not certify it.

For a nondegenerate active space E with column basis V and nonsingular Gram
G=V^t V, the orthogonal projector is P_E=V G^-1 V^t. It is symmetric,
idempotent, and has rank dim(E). The quadratic Fourier phase defining C_E
has polarization 2 x^t P_E y, hence M(C_E)=[I P_E;0 I]. This includes
alternating nondegenerate spaces, without requiring an orthonormal basis.
For nested nondegenerate spaces, projector subtraction has rank equal to
the dimension difference. Tensor-axis embedding into a larger ambient space
and mixed inverse signs do not alter these defect ranks. The independent
control uses the alternating plane with basis (011,110) in F2^3, whose
projector has rank two.

**Changed endpoints can reopen the gate.** If an actual new word leaves every
Y in F_9 instead of F_9 C_q^-1, its Y cap is nine. With the same X and helper
endpoints, (1) gives the sharp new total 2416. The old 2312 must not be reused.
This is an endpoint-dependent corollary, not proof of the concurrent changed-
consumer construction, its paid mass, source-consuming logical return, or its
global moment. The complete bill must be recomputed from that actual word.

## 5. Why the canonical chart adapters matter

The native compiler uses a particular `canonical_frame` Gamma_W. It is a
monomial conjugate of a coordinate C tensor and is not always the intrinsic
C_W. The published program has **208 rank-zero intrinsic endpoint adapters**:
104 source-entry adapters and 104 target-exit adapters. They add no positive
child to the original 2368 invoice. They are distinct from the **208 rank-one
side-correction transports** used by the later corrected profile.

A fresh canonical-frame census gives:

- 102 X endpoint cocycles: phi=8, full symplectic defect=10;
- the other two X endpoint cocycles: phi=8, defect=8;
- all 104 Y endpoint cocycles: phi=8, defect=8;
- all 72 helper endpoint cocycles: phi=9, defect=9.

Thus applying an intrinsic defect-eight assertion to bare canonical X charts
would be incorrect. Here is a concrete control at actual port X0, whose
physical normal is q=386. Let G=Gamma_span(q), F=F_9 and let H be a Hadamard
symplectic swap on zero-based coordinate 1. A Gaussian-dyadic realization is
S C S on that bit, up to its explicitly retained global phase; use its actual
inverse where required. The source-bound matrices give

    phi(F G^-1)=8,  delta(F G^-1)=10,
    phi(H F G^-1 H^-1)=9.

Choose L=H and R=G^-1 H^-1. Then the matched bare canonical entrance L G R
is identity, while the exit L F R has phi=9. The claimed per-source cap eight
would fail for these bare endpoints. This is a legal Clifford endpoint
example, not a lower-cost P104 supplier or a counterexample to (1).

The missing intrinsic source adapter is A=G C_q^-1. Before translation
phi(A)=0, but after this translation phi(H A H^-1)=2. Including it restores
the intended intrinsic cocycle, for which

    phi(H F C_q^-1 H^-1)=8.

One cannot translate the canonical chart and continue donating its old
rank-zero adapter classification. Every converted wrapper must be evaluated
in its actual position. Conversely, this does not say every translation makes
adapters positive: ordinary monomial translations preserve phi.

As an explicit whole-word control, apply the same L=H and R=G^-1 H^-1 to all
280 canonical charts. Identical-chart additions remain identical-chart
additions. Reprice each of the 1410 literal transports by its actual
conjugated B block. The resulting canonical chart progress is 2066 and the
transport rank mass is 2248, leaving excess182. The original pair was
2312 and2368, excess56. This particular reduction in paid mass therefore
worsens the progress deficit. Intrinsic adapters and the side correction
still require separate repricing; no claim is made that2248 is a complete
corrected-call bill. The general proof, not this single census, supports the
intrinsic matched-translation cap.

## 6. Decision and cost consequence

NARROW translation-only attempts to raise progress while keeping the same
intrinsic endpoint contract. In the role-local common-chart grammar, the
progress cap used by PR3954/3962 is now justified for the matched translations
above. Their cost rejection still additionally assumes the corrected mass,
actual global initial credits/owner endpoint, native rank grammar and volume
normalization. Arbitrary translations can change the paid profile, so this
study does not promote those conditional screens to a universal P104 barrier.

Continue a changed Y endpoint, coupled operator-valued encoding, or genuinely
new word only with its actual endpoint-derived potential and full invoice.
A feasible first test is the concurrent all-F9 target proposal: verify its
whole logical return and paid events, then use2416 only if its intrinsic
endpoint truly matches the displayed changed contract. No selected frontier,
shared controls or frozen predecessor evidence is changed here.
