# Linear feedback synthesis and its uniform cost boundary

This result pairs Clifford/Pauli circuit algebra with elementary matrices and
reversible linear networks. Its lower bound uses a discrete uncertainty
argument proved below. All linear identities are over Q(i). Cost statements
refer to the explicitly stated full-array alphabet, not arbitrary algorithms.

## 1. Literal selected boundary and normalization

The pinned selected archive contains the forward phase-B children at events
12806 and13402 on register195, with frames0→2→252 and ranks1,1. Write their
actual serialized operators A,B and the direct rank2 recipe0→252 as C. The
only intervening event touching195 or521 is12807, `L195 += L521/2`.
All other intervening operations act on disjoint registers and are carried
unchanged. Thus arbitrary physical payloads x,y require

    (x,y) ↦ (Cx + B y/2, y),                 C=BA.              (1)

This statement retains all global phases. It does not identify an endpoint
match with operator equality. The fresh exact checker evaluates every source
column, using the serialized monomials and normalized coordinate kernel.
With a=(1+i)/2, b=(1−i)/2 it establishes

    A=aI+bR,  B=aI+bP,
    R e_t = i³ (−1)^parity(14&t) e_(t xor30),
    P e_t =    (−1)^parity(96&t) e_(t xor224).

R²=P²=I and RP=PR. Their independent translations partition the512 source
coordinates into128 orbits of size4. The ordered chart R^r P^p e_t, r,p∈{0,1},
is monomial and makes R,P the two independent bit flips on each orbit.
The checker verifies every chart, including its phases. Consequently A,B
become independent two-point kernels and C their product. Each kernel is
unitary: |a|²+|b|²=1 and a conjugate(b)+b conjugate(a)=0.

For positive f use tensor lifts A_f,B_f,C_f and any identity spectators.
Let V=512^f times spectator multiplicity be the physical size of EACH payload.
The target boundary is (C_f x+B_f y/2,y). The sole rank2f native call acts on
one V-sized payload. No doubled concatenated operand is priced as one V call.
Every column of B_f has exactly2^f nonzeros. Every nonzero entry of C_f has
modulus2^(−f). In normalized child coordinates any rank2f Clifford recipe has
the same maximum-entry bound and is unitary. Its phase/permutation wrappers
and identity spectators preserve both properties. Nonunit diagonal charts,
if allowed outside the native kernel, are counted as surrounding monomial
maps and do not alter the normalized cut used in Section4.

## 2. Constructive dirty-helper feedback identity

For any involution P, the unit u=aI+bP has u^−1=bI+aP. Let E_ts(v) be the
2×2 elementary matrix adding v times payload s to payload t. Direct ring
multiplication in Q(i)[P]/(P²−1) gives

    diag(u,u^−1)
      = E12(u−I) E21(I) E12(u^−1−I) E21(−u).                  (2)

Indeed the first three factors on the right, multiplied left to right,
are [[u,0],[I,u^−1]], and multiplication by E21(−u) removes the lower-left
entry. Operators act right to left. Expanding each coefficient into its I,P
terms gives this application-order schedule on donor y and helper z:

    z += −a y
    z += −b P y
    y += −a z
    y +=  a P z
    z +=     y
    y += −b z
    y +=  b P z.                                             (3)

The seven additions implement (y,z)↦(u y,u^−1 z) for EVERY y,z; no clean
helper premise is used. They use changing mixtures as sources, which is the
precise relaxation of #3989's read-only monomial-donor accumulation contract.
Apply (3) for each tensor factor j. The factors commute, so the resulting
network T_f is diag(B_f,B_f^−1). Then perform

    x ← C_f x
    (y,z) ← T_f(y,z)
    x += y/2
    (y,z) ← T_f^−1(y,z).                                    (4)

Equation(4) gives (C_f x+B_f y/2,y,z) for arbitrary x,y,z, with one rank2f
child and no other recursive call. The inverse network reverses the individual
shear order and negates each coefficient. This is an all-f algebraic proof,
not extrapolation from finite tests. The helper returns exactly its arbitrary
entry value, and donor521 returns before its next original touch. Target195
has the original physical output and frame252 at the boundary. A host must
provide the extra dirty V-sized payload, disjoint from unchanged intervening
work, or price its allocation; its availability is not assumed for free.

## 3. Complete explicit pass ledger

A Gaussian coefficient c=r+it is implemented by `target += r source`, then
source multiplication by i, `target += t source`, and source multiplication
by −i, omitting zero terms. For a P term, apply P before this sequence and
undo P afterward. Each source transformation is restored before the next
shear, even when that source is a mixture. Each seven-shear factor has six
complex half coefficients and one real unit coefficient: thirteen rational
ADDs, six signed-P maps, twelve unit-phase maps. Compute and uncompute give:

| Item | Original boundary | Network(4) |
|---|---:|---:|
| Recursive child widths | f,f | 2f on one V-sized payload |
| Rational array ADDs | 1 | 26f+1 |
| Gaussian monomial-source shears | 1 | 14f+1 |
| Signed-P source maps | 0 new | 12f |
| Source unit-phase maps | 0 new | 24f |
| Live vector payload | 2V | 3V |
| Additional arbitrary dirty payload | 0 | V, restored |
| Additional recursive helper calls | 0 | 0 |

Each rational ADD visits V coordinates. Thus the construction executes
(26f+1)V coordinate additions and36f full-array source maps. A signed-P map
contains a signed address permutation; one such map is not one scalar machine
instruction. Coefficients have constant denominator2, but this does not imply
constant intermediate precision. Data routing, descriptor/stock preparation,
precision, helper hosting, and compiler admission remain separately unpriced
obligations, not zero costs. Counted maps already include donor/helper
restoration; any additional host recovery must still be charged.

The constructive change is exponential→linear transfer passes: #3989 needed
exactly2^f Gaussian monomial accumulation channels in its narrower class;
(4) uses14f+1, already less at f=7 (99<128), and O(f) thereafter. These are
operation counts in their respective stated alphabets, not a measured κ.
The rational-only counts and source maps above are the executable schedule.

## 4. Feedback lower bound via uncertainty

Allow a fixed linear program on arbitrarily many equal V-sized vector
registers. Permit arbitrary invertible coordinate-dependent monomial maps,
including global coordinate permutations; grant them free for this lower
bound. Permit full-array shears adding a monomial image of one register into
a distinct register, with nonzero scalar coefficient (absorbed into its
monomial). Source mixtures, donor feedback and any order are allowed. Permit
exactly one normalized rank2f child on ONE V register. Auxiliaries may be clean
zero or independent arbitrary dirty data, but must be returned as specified.
There is no free fanout, input-dependent pre-encoding, reset, discarded output,
concatenated native call, sparse-coordinate operation or implicit source mixing.
This is a generous fixed-linear full-array model, not a universal native or
RAM lower bound. Requiring common-frame legal operations only narrows it.

Write s(w) for total nonzero coordinate count over ALL registers. A monomial
preserves s. A shear and its inverse each increase s by at most a factor2:
its target support is contained in the union of old target and permuted source,
while all other supports remain. Take the legal boundary input x=0,y=e_t,
all auxiliaries zero. Dirty auxiliaries may be specialized to zero because the
contract holds for every independent dirty value. Required final total support
is2^f+1, since the target B_f e_t/2 has2^f nonzeros and donor has one.

Split k shears into k_pre before and k_post after the sole child. If v is its
input, forward propagation bounds s(v)≤2^k_pre. Reverse the ENTIRE postnetwork
from the prescribed final state, including every auxiliary: the child output
Qv has support at most2^k_post(2^f+1).

For any unitary Q with |Q_ij|≤μ and nonzero v, put S=s(v), T=s(Qv). For each
output coordinate, Cauchy–Schwarz gives

    |(Qv)_i| ≤ μ Σ_(j in supp v)|v_j| ≤ μ sqrt(S) ||v||₂.

Summing squares only on its T nonzero coordinates and using unitarity gives
1≤μ²ST. Here μ=2^(−f), hence

    4^f ≤ s(v)s(Qv) ≤ 2^k (2^f+1).                            (5)

For k≤f−1, the right side is at most2^(f−1)(2^f+1)<4^f for every f≥1.
Thus **k≥f**. If v=0 the child does nothing on this input and ordinary support
propagation yields2^f+1≤2^k, hence k≥f+1 instead. This covers that degenerate
case without dividing by ||v||₂=0. The complete inverse postnetwork argument
is essential: auxiliary supports cannot be omitted from the cut.

The lower bound f and construction14f+1 establish Θ(f) Gaussian
monomial-source shear complexity for this exact one-child feedback problem.
Rational-only shears are a subclass, and26f+1 supplies their linear upper
bound. This theorem does not cover variable-size payloads or sparse/adaptive
coordinate operations; extending its support count to their actual arithmetic
volume would require a new proof.

## 5. Budget, κ screen and stopping decision

The pinned selected moment exponent is
α=67018507072324140917/40000000000000000000000, with0<α<1. Dropping the common
positive selected normalization, widths f,f→2f save

    δ f^(1−α),   δ=2−2^(1−α)≈0.0023213362673.

This is only0.1160668% of the original pair's recursive charge. Before synthesis,
the family budget therefore ruled out adding another rank-f recursive call
or unit-pricing a doubled-volume rank2f call; either erases even this ideal
saving. A one-call adapter needed a uniform complete bill. Sections2–4 give
its exact constructive bill and a lower bound for the changed feedback class.

Under the inherited volume-linear child charge expression A V (r f)^(1−α)
for a fixed A>0, the maximum recursive saving is A V δ f^(1−α). Because every
counted shear acts on all V coordinates, at least fV arithmetic operations
are necessary. Credit the original ADD's V operations, and even grant every
monomial, helper, precision and routing cost zero. A necessary condition for
strict improvement is still

    f−1 < A δ f^(1−α).                                       (6)

For any fixed A>0 this fails eventually: (f−1)/f^(1−α) tends to infinity as
f grows. Consequently this one-call full-array feedback class cannot supply
a uniform improvement against that inherited charge expression. This compares
an available recursive upper-charge model, not an optimal-runtime lower bound.
No finite crossing threshold is claimed without its actual A and full invoice.
The constructive schedule itself has26f additional array ADDs over baseline,
plus its source maps and helper obligation, so it also fails this uniform screen.

The output is a positive O(f) exact implementation and a matching asymptotic
order lower bound for the changed contract. Stop expansion within this model;
no selected profile, claimed κ, template, record or frontier is changed. A new
supplier replay is unwarranted. A justified next step must change the arithmetic
volume premise, e.g. a fixed sparse-coordinate network with a proved sum of
processed volumes and complete restoration/hosting, then compare that bill
before synthesis. This theorem does not prejudge such a different model.

## 6. Evidence and scope of verification

The registered verifier uses exact Gaussian rationals, checks the formal
ring identity, all1536 basis inputs of the literal three-payload boundary,
all128 source orbit charts, and complete reduced tensor bases for f=1,2,3
(12+48+192 inputs). Tensor orbit decomposition is an algebraic all-f reduction;
we do not claim to enumerate3·512² literal f=2 inputs. Four mutated schedules
fail: dropped final restoration map, wrong coupling coefficient, reversed
order without inverse signs, and wrong phase. Integer tests through f=256
control(5); the proof above, not this finite range, establishes all f.

This is a physical coupled macro. Its intermediate coordinate ADDs are not
claimed to satisfy the inherited scalar word's common-frame event rule.
Operator identity, native pass ledger, compiler admission and global supplier
qualification are distinct obligations. Only the first two are established.
