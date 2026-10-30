# Near-unit rational normalization of Stein generators

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and predecessor

Let E be an m by m matrix over Q(i), m >= 1, with rank r. Norms are
Euclidean vector norms and the induced operator norm. A coefficient row a
is a row, without an additional conjugation. Jose Manuel's PR4198,
`research/rational-stein-generators/PROOF.md` section 1, supplies exact
orthogonal Gram-Schmidt residuals v_j spanning the column space of E and
the factorization

    n_j = v_j* v_j > 0,
    g_j = v_j/c_j,
    a_j = (c_j/n_j) v_j* E,
    E = sum_j g_j a_j.

The star denotes conjugate transpose. That construction uses c_j equal
to the least power of two whose square is at least n_j, giving the strict
row bound 2||E||. We retain its residuals, term count and row convention.
We change only the scalar normalization. The predecessor's executable,
Schur examples and macro receipts are not replayed here.

## 1. A dyadic upper approximation with a bounded mantissa

Fix n > 0 rational and an integer p >= 1. Let e be the unique integer with

    2^(2e-2) < n <= 2^(2e).

Put u = 2^(e-p-1) and

    k = ceil(sqrt(n/u^2)),       c = k u.

These definitions imply

    2^p < k <= 2^(p+1),
    (c-u)^2 < n <= c^2,
    sqrt(n) <= c < sqrt(n) + u.

Since 2^e < 2 sqrt(n), we have u < 2^-p sqrt(n). Consequently

    n <= c^2 < (1+2^-p)^2 n.                         (1)

The strict upper inequality also holds when n has an exactly representable
square root: then c=sqrt(n). No floating approximation is used.

For an exact algorithm, write n/u^2 = A/B in positive reduced integers.
Let f = isqrt(A // B), and set k=f when f^2 B=A, otherwise k=f+1.
The identity floor(sqrt(A/B))=isqrt(A // B) proves this formula.
If d is the numerator bit length of n minus its denominator bit length,
start e=d//2+1, and decrease it once if 2^(2e-2)>=n. The bit-length bounds
2^(d-1)<n<2^(d+1) prove that this gives precisely the required e.
The equality cases are settled by the squared comparison.

This is ordinary integer square-root and round-up arithmetic; no novelty
is claimed for these operations. Their bounded-mantissa use at this exact
generator interface is the normalization change.

## 2. The improved generator theorem

Apply section 1 to every nonzero residual norm n_j. The cancellation

    g_j a_j = (v_j v_j*/n_j) E

does not depend on the positive scaling c_j. The orthogonal projectors
sum to the identity on the column space of E, so reconstruction and the
number r of terms are unchanged. In particular, no term is dropped because
it is small. Equation (1) gives

    ||g_j||^2 = n_j/c_j^2 <= 1,
    ||a_j|| <= (c_j/sqrt(n_j)) ||E||
             < (1+2^-p) ||E||.                    (2)

All emitted coefficients are Gaussian rational. The zero matrix has no
terms. The term count is minimal: a sum of s outer products has rank at
most s. This proof is for every finite m and every p>=1; the implementation
has the explicit finite capacities stated in the README.

At p=3 the old factor two is replaced by 9/8. As a concrete exact fixture,
let E have first column (1,1,1)^T and its other columns zero. Its squared
operator norm is 3. The old power-of-two normalizer is c_0=2. The new one
is c=7/4, with

    g = (4/7,4/7,4/7)^T,       a=(7/4,0,0),
    ||g||^2=48/49,             ||a||^2=49/16.

The old row is (2,0,0) and has squared norm 4. These are two evaluations
of the displayed formulas, rather than a replay of a predecessor fixture.

## 3. Encoding overhead

For a reduced rational, height means the maximum bit length of numerator
and positive denominator. The height of c is at most |e|+p+2, because
the unreduced representation is k 2^(e-p-1), with k <= 2^(p+1).
The integer operations above use O(h+p) bit operands when n has height h.
Integer division and integer square root have polynomial bit complexity.
There is no search over 2^p mantissas in the producer.

More directly, compare with PR4198's c_0=2^e. The new emitted components are

    g_new = (2^(p+1)/k) g_old,
    a_new = (k/2^(p+1)) a_old.

Each rational multiplier has height at most p+2. Multiplication therefore
increases the height of each real or imaginary generator component by at
most p+2. Exact reduction can only decrease that bound. The residual
calculation is unchanged. Thus the predecessor's polynomial coefficient
generation remains polynomial with an additive O(p) output-height cost.
This does not assert the predecessor's unchanged numerical height constant
for later inverse-series coefficients, rounded children or physical pages.

## 4. Exact factor one can fail over Q(i)

Consider the same rank-one E from section 2. If a single Gaussian-rational
outer product E=g a satisfied ||g||<=1 and ||a||<=||E||=sqrt(3), then the
rank-one product norm equality would force ||g||=1 and ||a||=sqrt(3).
Because E has only its first column nonzero, a=(z,0,0) with z in Q(i),
and consequently |z|^2=3.

No Gaussian rational has squared norm 3. Otherwise clear denominators in
z=x+iy to obtain coprime integers u,v,w, w>0, with

    u^2+v^2=3w^2.

Modulo three, both u and v must be divisible by three. The equation then
forces w to be divisible by three, contradicting coprimality. This is the
classical norm obstruction at a prime congruent to three modulo four.

Thus every positive requested slack can be achieved by section 2, while
the uniform exact factor one cannot always be achieved with the minimal
number of terms. Allowing extra terms changes this conclusion: E can be
split into three coordinate outer products. No impossibility is claimed
in that different term-count contract.

## 5. What the finite checks establish

The checker independently exhausts small exponent/mantissa choices and
compares them with the integer-square-root producer. A separate row
elimination checks the rank of each new matrix fixture. It verifies every
entry of the reconstructed E and all pairwise residual orthogonalities.

For every emitted row it also checks the stronger matrix inequality

    a_j* a_j <= (c_j^2/n_j) E* E.

An exact Hermitian Schur test verifies positive semidefiniteness, including
zero-pivot cases; no numerical singular values are used. This inequality
implies the row norm comparison used in (2). The universal statements
rest on the proof above, not extrapolation from the finite fixtures.

This is a scoped coefficient-generation result. Native operator admission,
the full Gaussian caller, dirty restoration in rounded execution, FFT and
triangular child execution, coefficient delivery, physical tape costs and
the five framework assumptions remain outside it. No multiplication
theorem or new kappa is claimed.
