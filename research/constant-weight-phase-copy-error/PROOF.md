# Exact COPY error from constant-weight phase histories

This scoped proof was produced by Nick Petalas. New work is Apache-2.0.

## Contract and theorem

Let n and f be positive integers, and let 1 <= k <= n. Write S = diag(1,i).
For a k-element subset A of {1,...,n}, let U_A be the n-axis diagonal unitary
that applies S on the axes in A and I on the other axes. Let V_A = U_A tensor
... tensor U_A, with f factors. Its dimension is D = 2^(nf). Exterior scalar
coefficients are not raised to the f-th power.

There are N = binom(n,k) available histories. The admitted accumulator word
is any finite sequence of operations

    (x,y) -> (x, y + c V_A x),   c in C, |A|=k.

Both x and the initial accumulator y are arbitrary independent inputs. The
source x must return unchanged. Repetition and order are unrestricted, but
source mixing, other history operators and other register operations are
outside this contract. Equal histories can be collected, so every such word
has endpoint (x, y + Mx), where M = sum_A c_A V_A. Conversely any coefficient
vector has that endpoint using at most N accumulator operations.

Use the normalized response norm ||R||_HS^2 = tr(R* R)/D. Define

    q = 2^(-f),
    L(n,k,f) = sum_{j=0}^{min(k,n-k)} binom(k,j) binom(n-k,j) q^j,
    b = ((1-i)/2)^(kf).

Then the exact minimum COPY error is

    E(n,k,f) = min_c ||I - sum_A c_A V_A||_HS^2
             = 1 - binom(n,k) q^k / L(n,k,f).

It satisfies 0 < E(n,k,f) < 1. The unique coefficient vector attaining the
minimum is constant on the layer:

    c_A = b / L(n,k,f)   for every A.

Thus no admitted word realizes exact COPY. The statement allows arbitrary
complex coefficients, including coefficients depending on f. It is stronger
than a claim restricted to Gaussian-dyadic coefficients, but does not assert
that its minimizer is implementable in that smaller alphabet.

## Phase-sensitive kernel

Use the inner product <P,Q> = tr(P* Q)/D, conjugate-linear in P.
For two k-subsets A and B, put j = |A minus B| = |B minus A|.
On an axis in A minus B the normalized trace contribution is (1-i)/2;
on an axis in B minus A it is (1+i)/2. All other axes contribute one.
Consequently

    <V_A,V_B> = [((1-i)/2)^j ((1+i)/2)^j]^f = q^j,
    <V_A,I> = b.

The cancellation of the two phases depends on equal subset cardinalities.
Taking absolute trace values before deriving b would lose its phase and
produce the wrong attaining coefficient.

For fixed A, exactly binom(k,j) binom(n-k,j) choices of B remove j axes from
A and add j axes from its complement. Every row of the Gram matrix G
therefore sums to L. This is a constant-weight subset intersection count.

## Independence and the attained optimum

The two operators I^(tensor f) and S^(tensor f) are linearly independent.
Their diagonal entries at the all-zero address are both one, while at an
address with exactly one set bit they are one and i. After a fixed permutation
of the tensor axes, the full 2^n family indexed by all subsets A is the tensor
product of n copies of this independent pair. It is therefore independent.
This elementary tensor-basis argument works at every positive f.

In particular, the k-layer is independent, so G is positive definite. Its
normal equations for approximation of I are Gc = b 1. Since G1 = L1 and
L>0, their unique solution is c = (b/L)1. Its squared projection mass is

    c* G c = N |b|^2 / L = N q^k / L.

The residual is orthogonal to every V_A. For every other coefficient vector d,

    ||I - sum_A d_A V_A||_HS^2
      = E(n,k,f) + (d-c)* G (d-c).

This proves global optimality and uniqueness, over all complex coefficients.
The projection is nonzero since b is nonzero, so E<1. Since k>=1, I is the
empty-subset member of the full independent family and is not in the k-layer
span. Hence E>0. No finite enumeration is needed for these universal steps.

For the one-phase layer, k=1, the formula simplifies to

    E(n,1,f) = (2^f - 1)/(2^f + n - 1).

For example E(2,1,1)=1/3, E(4,2,1)=7/13, E(8,4,1)=251/321 and
E(8,4,2)=1851/1921. The first coefficient vector is c_A=(1-i)/3.

## Complete independent columns and the physical boundary

The complete two-register endpoint and desired COPY are

    B_M = [[I,0],[M,I]],      B_COPY = [[I,0],[I,I]].

Their only differing block is M-I. Thus all source-return columns and all
columns of the initially arbitrary accumulator already have their required
values. The response norm in the theorem is normalized by D. The squared
Hilbert-Schmidt distance of the complete 2D-dimensional matrices, normalized
by 2D, is E/2 at the optimum. Their operator-norm squared distance is at least
E, since the maximum squared singular value of M-I bounds its average.

One algebraic realization of a summand phases x by V_A, adds c_A x to y,
and applies V_A inverse to x. This explains source restoration explicitly.
The verifier executes this sandwich on every input basis column in its
finite domain. No state is assumed initially zero. There is no extra helper.

This algebraic word does not supply native physical queries or their tariffs.
In particular, c_A can have an odd denominator. Coefficient preparation,
phase/inverse delivery, movement, ownership, precision, storage and the full
recursive invoice remain unpriced. A lower bound remains valid if the caller
restricts the coefficients, but attainment in such a restriction is unclaimed.
The theorem excludes only its fixed available-history span, not arbitrary
Clifford programs, networks with feedback or changes to the source contract.

## Evidence and credit

The universal claim is the written argument above. The standalone exact
verifier independently constructs literal diagonal tensor matrices for every
1<=n<=6, 1<=k<=n and 1<=f<=min(8,floor(10/n)). It solves the complex normal
equations using rational elimination and positive Schur pivots, checks the
literal squared residual, and executes both register input columns at every
address. It imports no predecessor implementation and uses no floating point.

The generated stdout receipt reports actual counts and hashes of all package
files. It distinguishes the literal cases from 160 larger evaluations of the
formula, whose matrices are not enumerated. Its nine semantic controls cover
conjugation, exterior-coefficient exponentiation, exchange distance, the
diagonal Gram term, inclusion of the identity history, changing S to Z,
restricting coefficients to real values, erasing dirty y and failing to restore
x. Ten malformed or out-of-range evaluator inputs are rejected. The evaluator
is capped at n<=128 and f<=256; the written theorem has no such cap.

Ali Romman's [PR #5727](https://github.com/CrocSwap/integer-mult-bounds/pull/5727)
poses the finite paid-history application and supplies its exact projection
contract. Its general contraction engine and theorem are cited, not rechecked.
This contribution supplies a new explicit history family, its closed optimum
and attaining coefficients. Constant-weight intersection counts, tensor-product
independence and Hilbert-space normal equations are classical ingredients.
The broader Clifford/native/controller lineage remains with the contributors
credited in #5727. No new general projection method or literature priority is
claimed. Independent human and formal proof-kernel review are unclaimed.
