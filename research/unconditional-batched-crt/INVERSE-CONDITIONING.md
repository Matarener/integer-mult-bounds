# Uniform conditioning from a banded row gap

Independent derivation for the unconditional-route audit, 2026-10-19.
This is an auxiliary mathematical lemma, not a multiplication bound.

Let E be an N by N complex matrix, E[i,j]=0 when |i-j|>b, and let
max_i sum_j |E[i,j]| <= rho < 1. Put delta=1-rho and H=I-E.
Here N is arbitrary and b is a nonnegative integer. Then

    ||H^-1||_infinity <= 1/delta,
    ||H^-1||_1 <= 1/delta + 2 b rho/delta^2,
    ||H^-1||_2 <= sqrt((1/delta)(1/delta + 2 b rho/delta^2)).

Proof. Submultiplicativity gives ||E^k||_infinity <= rho^k. Induction on k
shows that E^k has bandwidth at most kb. Each column consequently contains
at most 2kb+1 nonzero entries, each bounded in absolute value by rho^k.
Thus ||E^k||_1 <= (2kb+1)rho^k. The Neumann series converges in both norms.
Summing sum rho^k=1/delta and sum k rho^k=rho/delta^2 proves the first
two bounds. The standard inequality ||M||_2^2 <= ||M||_1 ||M||_infinity
proves the third. No constant depends on N.

Every principal section has the same row gap and bandwidth after preserving
the original order (compression of the order can only reduce distances).
It therefore obeys the same bounds. For an invertible principal block A of
such a section T, the complementary Schur inverse is the corresponding
principal block of T^-1. Restriction cannot increase either induced 1-norm
or infinity norm, so the same inverse bounds hold for that Schur complement.
The Schur complement itself is bounded by D-C A^-1 B; all factors have
uniform norm bounds. Iterated elimination is covered by the quotient identity,
provided each intermediate matrix is a Schur complement of a principal section
of the same original matrix.

For the narrow Gaussian reference, GAUSSIAN.md establishes b<p and
delta>=1/(16p^2) for one truncated, rounded matrix, including its augmented
holes. The lemma therefore supplies polynomial two-sided conditioning
across arbitrarily many cells and for the stated principal eliminations.
GAUSSIAN.md separately supplies the shallow circuits and their execution cost.

The bandwidth hypothesis matters: E[i,0]=rho for i>0 and all other entries
zero gives E^2=0 and ||(I-E)^-1||_1=1+(N-1)rho despite the same row gap.
Hence a row gap alone cannot justify a dimension-independent 1-norm bound.
