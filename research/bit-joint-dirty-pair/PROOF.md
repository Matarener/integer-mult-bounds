# A sharp query tariff for two independent dirty inputs

This is a written all-parameter proof in the model below, not a formal-kernel
verification. The finite source checks accompanying it bind a particular pair
to the hypotheses; they do not replace this proof.

## Model and theorem

Fix an integer address half-dimension `d >= 2` and an independent common price
parameter `m > 0`. For each odd prime `ell`, the address space is

\[
\Omega_\ell=\mathbf F_\ell^{2d},\qquad N=|\Omega_\ell|=\ell^{2d}.
\]

A VALUE register is an arbitrary function `Omega_ell -> F_2`. Free operations
are invertible matrices over `F_2` mixing whole VALUE registers, with the same
scalar coefficients at every address. They include register permutations and
CNOTs. They do not include address-dependent mixing, nonlinear gates, or free
address permutations.

For a dyadic rational idempotent `P` of size `d` and rank `r > 0`, define

\[
S(P)=\begin{pmatrix}I-P&P\\P&I-P\end{pmatrix}.
\]

A paid query applies this address involution to one VALUE register and leaves
all other registers unchanged. There are no frame-path restrictions or costs
in this relaxed model: every such fixed dyadic projector is eligible as a paid
query. This relaxation does not enlarge the free gate set just specified.
At parameter `0 <= b <= 1`, its tariff is

\[
H_r(m)=m^b r^{1-b}.
\]

The price parameter `m` is not the address half-dimension `d`. For each fixed
pair `(d,m)`, the number of registers, finite gate word, scalar matrices,
and rational projectors must be independent of `ell`. The same word must have
the required endpoint for every sufficiently large odd prime `ell`.

Let `p=S(P)` and `q=S(Q)` be distinct rank-two partial swaps. Initially there
are `a >= 2` arbitrary independent VALUE registers and any finite number of
additional zero VALUE registers. The first two arbitrary inputs must become
`p f_1` and `q f_2`; every other arbitrary input must be restored, and every
initially zero register must return to zero. No arbitrary-input column is
omitted from these requirements. The notation for the address action is fixed
below.

**Theorem.** Every such word has tariff at least

\[
2H_2(m)=2m^b2^{1-b}.
\]

Two separate queries, one applying `p` to register 1 and one applying `q` to
register 2, attain this tariff. Thus it is the exact optimum in this model,
including arbitrary restored dirty spectators and restored clean ancillas.

## 1. Partial swaps and their Boolean operator defect

All matrices are reduced modulo an odd prime using their dyadic entries. Since
`P^2=P`, its rational characteristic polynomial is
`X^(d-r)(X-1)^r`. The same polynomial identity holds after reduction at every
odd prime. An idempotent is diagonalizable with eigenvalues 0 and 1 over every
field, so the reduced projector still has rank exactly `r`.

In the invertible coordinates `(x+y,x-y)`, the partial swap acts as

\[
(u,v)\longmapsto (u,(I-2P)v).
\]

It is an involution, has rational determinant `(-1)^r`, and fixes exactly
`ell^(2d-r)` addresses. Its permutation of `Omega_ell` therefore consists of
that many fixed points and

\[
D_r=\frac{\ell^{2d}-\ell^{2d-r}}2
    =\frac N2(1-\ell^{-r})
\]

two-cycles. On Boolean VALUE functions, each two-cycle contributes rank one
to the operator `I+rho_ell(S(P))`, and each fixed point contributes zero.
Consequently this Boolean operator has rank exactly `D_r` over `F_2`.

Here and throughout,

\[
(\rho_\ell(g)f)(z)=f(g^{-1}z).
\]

This inverse pullback makes `rho_ell(g h)=rho_ell(g)rho_ell(h)`. For a queried
involution its inverse is itself, so this convention does not change the query.

## 2. Scalar normalization and the full endpoint

Let there be `R >= a` registers, ordered so the arbitrary inputs precede the
zero inputs, and let `J` be the constant `R`-by-`a` coordinate inclusion. The
endpoint is the equality of complete `R`-by-`a` VALUE operators

\[
WJ=JD,\qquad D=\operatorname{diag}(p,q,I,\ldots,I). \tag{1}
\]

Here an address label means its VALUE action. In the dirty-only case `R=a`,
this specifies the entire square operator. When `R>a`, it specifies all
arbitrary input columns and the zero final rows of the clean ancillas; it does
not assert any action on hypothetical nonzero inputs in the clean slots.

Write the word, in operator order, as

\[
W=A_k Q_k A_{k-1}\cdots Q_1 A_0,
\]

where all `A_i` are scalar invertible matrices, and query `Q_i` acts on one
register with address label `g_i`. Let

\[
S=A_k\cdots A_0,\qquad B_i=A_{i-1}\cdots A_0.
\]

Then the exact factorization is

\[
W=S T_k\cdots T_1,\qquad
T_i=B_i^{-1}Q_i B_i=I+(g_i+1)E_i, \tag{2}
\]

where `E_i=u_i v_i` is a scalar rank-one idempotent: `u_i` is a column,
`v_i` a row, and `v_i u_i=1`. Scalar entries commute with address labels, but
address labels themselves are not commuted in (2).

Queries fix constant VALUE functions. Applying (1) to arbitrary constants in
the first `a` slots therefore gives

\[
SJ=J. \tag{3}
\]

In particular `S=I` in the dirty-only case. With clean slots only (3), not
`S=I`, is warranted.

## 3. Zero, one, or two queries

Fix any odd prime at which the endpoint holds. Applying (2), (3), and the
matrix-rank inequality `rank(AB-I) <= rank(A-I)+rank(B-I)` gives

\[
\begin{aligned}
2D_2
 &=\operatorname{rank}(JD-J)\\
 &=\operatorname{rank}\bigl(S(T_k\cdots T_1-I)J\bigr)\\
 &\le \sum_{i=1}^k \operatorname{rank}(T_i-I)
 =\sum_{i=1}^k D_{r_i}. \tag{4}
\end{aligned}
\]

The target rank is a sum because its two defects occupy independent input and
output register blocks. Conjugation by scalar invertible matrices preserves
each query's Boolean defect rank.

Zero or one query cannot satisfy (4): `D_r < N/2`, whereas
`2D_2=N(1-ell^(-2)) > N/2`. If there are two queries and one has rank one,
then, for the other rank `s`,

\[
D_1+D_s
 <N\left(1-\frac1{2\ell}\right)
 <N(1-\ell^{-2})=2D_2,
\]

where the second strict inequality uses `ell > 2`. Thus a two-query word has
both ranks at least two, and its tariff is at least `2H_2(m)`. This argument
already holds over any single odd prime field where the endpoint holds.

## 4. Lifting the uniform endpoint to a group algebra

Let `G` be the subgroup of `GL_(2d)(Q)` generated by the finite collection of
queried address maps together with `p` and `q`. Interpret the fixed word in
the matrix algebra over `F_2[G]`. Distinct group elements are distinct
rational linear maps; a fixed finite-field permutation representation need
not be faithful on this group algebra.

Nevertheless, the uniform endpoint (1) implies its formal `F_2[G]` version.
To see this, collect the finitely many distinct labels in each coefficient of
`WJ-JD`. For the finite union of these labels, choose an integer address `z`
such that all `g^{-1}z` are distinct over `Q`. Such a choice exists: each
coincidence is a proper rational linear subspace, and a finite union of these
subspaces cannot cover all integer vectors. More explicitly one can use
`z=(1,t,...,t^(2d-1))` for an integer `t` avoiding the roots of finitely many
nonzero rational polynomials.

Clear denominators and, for each pair of distinct images, select one nonzero
integer coordinate of their difference. Outside the finitely many primes
dividing these selected numerators or denominators, the images remain
distinct after reduction. For a chosen input register, an indicator VALUE
function at any one of these images separates its coefficient from all other
labels, when the output is evaluated at `z`. Hence a nonzero formal
coefficient would violate (1) at every sufficiently large prime. This proves
the formal identity.

This step uses fixed finite data and uniform correctness over sufficiently
large odd primes. It does not assert a lower bound for arbitrary
modulus-dependent words from one fixed-field representation.

## 5. Three rank-one queries are impossible, including clean ancillas

The determinant sign of a rational address map defines a homomorphism

\[
G\longrightarrow C_2,\qquad g\longmapsto t^{\sigma(g)},
\]

where `sigma(g)=0` for positive determinant and `1` for negative determinant.
All generators have determinant `+1` or `-1`. For a rank-`r` partial swap this
image is `t^r`. The induced ring map has codomain

\[
\mathbf F_2[C_2]
 =\mathbf F_2[\varepsilon]/(\varepsilon^2),\qquad t=1+\varepsilon.
\]

Suppose now that `k=3` and all three queries have rank one. Each label maps to
`1+epsilon`, while the even-rank target labels `p,q` both map to 1. Using the
formal identity from Section 4 and factorization (2),

\[
T_3T_2T_1\longmapsto I+\varepsilon(E_1+E_2+E_3).
\]

Set

\[
U=\begin{pmatrix}u_1&u_2&u_3\end{pmatrix},\qquad
V=\begin{pmatrix}v_1\\v_2\\v_3\end{pmatrix}.
\]

The constant coefficient of (1) is (3); its `epsilon` coefficient is
`SUVJ=0`. Since `S` is invertible,

\[
UVJ=0. \tag{5}
\]

On the other hand, expand the ordered product `T_3T_2T_1-I` in `F_2[G]`.
Each scalar matrix multiplying an address word is a linear combination of
nonempty ordered products of the `E_i`. Every such product has the form

\[
E_{i_1}\cdots E_{i_s}
 =u_{i_1}(v_{i_1}u_{i_2})\cdots
    (v_{i_{s-1}}u_{i_s})v_{i_s}.
\]

Therefore every group-label coefficient of

\[
WJ-J=S(T_3T_2T_1-I)J
\]

has image contained in `im(SU)` and row space contained in `row(VJ)`.
Cancellation or coinciding address words cannot enlarge either containing
space.

But the two distinct nonidentity target labels `p` and `q` have respective
coefficient matrices `e_1 e_1^T J` and `e_2 e_2^T J` in `JD-J`. Their images
span two independent register directions and their rows span two independent
input directions. Thus

\[
\operatorname{rank}U\ge2,\qquad
\operatorname{rank}(VJ)\ge2.
\]

Sylvester's rank inequality over `F_2` now gives

\[
\operatorname{rank}(UVJ)
 \ge \operatorname{rank}U+\operatorname{rank}(VJ)-3
 \ge1,
\]

contradicting (5). This excludes three rank-one queries without assuming that
the clean inputs were arbitrary. It also does not require noncommutativity,
an intersection condition on the two projector images, or a bounded number
of restored spectators beyond finiteness.

For comparison, in the dirty-only case a shorter parity argument is
available: taking determinants after the same ring map gives
`t^(sum r_i)=det(D)=1`, hence `sum r_i` is even. Each conjugated query has a
rank-one register coupling and determinant `t^r`; every scalar invertible
`F_2` matrix has determinant 1. This square-operator determinant argument alone
would not justify the clean-ancilla extension; the rectangular argument above
supplies it.

## 6. Completing the tariff bound

Put `alpha=1-b`, so `0 <= alpha <= 1`, and divide all tariffs by `m^b`.

- With at most one query the endpoint is impossible.
- With two queries, Section 3 gives a cost of at least `2*2^alpha`.
- With three queries, Section 5 excludes three rank-one queries. At least one
  rank is therefore at least two, giving cost at least `2+2^alpha`, which is
  at least `2*2^alpha` because `2^alpha <= 2`.
- With at least four queries, each has positive integer rank and costs at
  least 1, giving total at least `4 >= 2*2^alpha`.

The two direct rank-two queries meet the bound, proving the theorem for every
`b` in the closed interval, including both endpoints.

## 7. Conditional application and remaining scope

The theorem applies to a source rewrite only after its required endpoint has
been identified with (1), including all independent dirty columns and restored
rows. It permits jointly mixing the two dirty inputs with each other and with
any finite number of restored dirty or clean registers. The lower bound is
on their complete replacement operator, not on an individual spelling of the
two original queries.

One sufficient application condition is a fixed rejoining cut followed by an
unchanged injective suffix, with equality of the entire final state required.
When a replacement introduces clean ancillas, compare both words on the same
extended state space and extend the frozen suffix by the identity on those
new slots. This common extension remains injective, so equality of the entire
final state forces equality of the whole state at the cut, including zero in
the new slots. Cleaning them later with added gates changes the extended
suffix even if every old suffix record remains present.

The source-specific audit must still identify the cut, the independent inputs,
and the target operator. Equality of selected public outputs alone does not
supply this implication. A changed later compensation or cleanup word is a
different endpoint problem and is not excluded by this theorem.

The result charges only the stipulated query tariff with its independent
common parameter `m`; any native interpretation of that tariff is an inherited
conditional pricing premise, not a new conversion here. It does not certify a
native frame schedule, workspace or tape bound, integer precision bound,
compiler cost, or improved multiplication exponent. The field-uniform word,
linear scalar free gates, one-register queries, and complete endpoint are
substantive hypotheses. Other interfaces, nonlinear or address-dependent
free operations, and modulus-dependent constructions require new arguments.
