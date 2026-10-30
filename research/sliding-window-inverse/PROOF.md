# Exact sliding-window preparation with certified weighted recovery

## Root theorem and actual contribution

Let H be a fixed N×N rational matrix, N ≥ 2, and D a fixed positive rational
diagonal matrix. Suppose G = D^−1 H D has real positive diagonal entries and

    δ = min_i (G_ii − Σ_(j≠i) |G_ij|) > 0.

Let 1 ≤ m ≤ N. Begin with an ordered list J of m distinct source indices;
each slide removes the first index and appends an index absent from the retained
list. The incoming index may equal the outgoing index. Then both algorithms
below construct exactly `H[J,J]^−1` after every slide. After one dense initial
inverse, T slides use `O(m³ + T m²)` rational field operations and `O(m²)` live
cache storage, in addition to access/storage for the unchanged global H,D.
The output stream, if retained, has its separate output-storage cost.
All final reduced inverse entries have bit height polynomial in m and the fixed
input coefficient height, independent of T. The weighted residual tests below
supply sufficient numerical error and integer-recovery guarantees.

This is an exact arithmetic preparation component, not a finite-tape compiler,
a revised online page format, a runtime benchmark, or a new κ. The mathematical
identities are classical and found in the shared library. The contribution is a
source-bound composition, two exact algorithms, explicit safety/precision/height
conditions and a checked reuse target for the current Gaussian preparation.

## 1. Every principal window and every pivot exists

Every principal restriction G_J has diagonal-dominance gap at least δ.
For nonzero z, choose i with |z_i| = ||z||_∞. The reverse triangle inequality
on row i gives

    ||G_J z||_∞ ≥ δ ||z||_∞.

Thus G_J is injective, hence invertible in finite dimension, and
`||G_J^−1||_∞ ≤ 1/δ`. Similarity by the positive diagonal restriction D_J
makes H_J invertible as well. This holds for all principal subwindows and
permutations, not merely the finitely tested windows. No spectral oracle is
required. Empty retained windows at m = 1 use the empty block convention.

## 2. Schur deletion and bordering

Move the outgoing coordinate to the end by the same row/column permutation.
Write the old matrix and its inverse as

    M = [ B  u ; v  d ],       M^−1 = [ E  f ; g  h ].

When m > 1, B is an invertible principal matrix. Let
`σ_old = d − v B^−1 u`. The block factorization

    M = [ I 0 ; v B^−1 1 ] [ B 0 ; 0 σ_old ] [ I B^−1 u ; 0 1 ]

shows σ_old ≠ 0, and multiplication of the inverses gives
`h = σ_old^−1 ≠ 0` and

    B^−1 = E − f h^−1 g.                                  (2.1)

This is the deletion step. For the incoming source index, read its column u',
row v' and diagonal d' from the SAME global H. Compute

    w = B^−1 u',    z = v' B^−1,    σ = d' − v' w.

The new principal matrix is invertible by section 1, so σ ≠ 0. Its inverse is

    [ B^−1 + w σ^−1 z    −w σ^−1 ;
      −σ^−1 z             σ^−1 ].                         (2.2)

Multiplying on either side verifies every block entry, proving the new inverse.
The empty case m = 1 simply returns `1/d'`. Formula (2.1) is the specialization
of two-sided Schur elimination; assuming a one-sided formula in an arbitrary
ring without the required inverse conditions would not justify both directions.

## 3. Complementary rank-two Woodbury update

Keep the same outgoing-last order. The replacement changes only the final
row and column. Let c be the entire new-minus-old final column, e the final
standard basis vector, and r the new-minus-old final row with its last entry
SET TO ZERO. Then

    Δ = c eᵀ + e r,      U = [ c e ],      V = [ eᵀ ; r ].

The diagonal change occurs in c exactly once; counting it again in r is wrong
when the two source diagonals differ. Let Q = M^−1 and C = (I_2+VQU)^−1.
The inverse exists: if `(I+VQU)t=0`, then `(M+UV)QUt = U(I+VQU)t = 0`;
invertibility of M+UV implies Ut = 0, and the original equality then gives
t = 0. In finite dimension the core is invertible. The two-sided Woodbury
identity from the shared DAG gives

    (M+UV)^−1 = Q − QU C VQ.                              (3.1)

For completeness, put A=QU and B=V. The DAG identity says
`(I+AB)(I−ACB) = (I−ACB)(I+AB) = I` whenever C is a two-sided inverse of
I+BA. Since M+UV = M(I+QUV), right multiplication by Q yields (3.1).
This proof fixes the multiplication orientation even for nonsymmetric H.
The core has size 2 regardless of m. The implementation evaluates its inverse
by its exact determinant. At small widths the extra core work need not beat
fresh elimination; the quadratic bound is asymptotic field arithmetic only.

## 4. Operation and coefficient-height bounds

Deletion (2.1) is one scaled outer product. Bordering (2.2) is two matrix-vector
products and one outer product. Thus each costs O(m²) field operations.
The Woodbury route uses products with two-column/two-row factors and a 2×2
inverse, hence also O(m²). The initial dense inverse costs O(m³).
The tested deterministic width-8 instance uses 414 field operations for a
Schur slide, 869 for Woodbury, and 1,920 for the retained fresh Gauss–Jordan
algorithm. These exact counters count rational additions/subtractions/products/
divisions equally. They exclude source generation, bit costs, checking, page
emission and tape scans; they are not timings or an end-to-end speedup claim.

Suppose each source numerator and positive denominator has at most B bits,
B ≥ 1. Clear denominators separately in each m-row principal matrix. The row
multiplier is at most 2^(mB), and resulting integer entries have magnitude at
most 2^((m+1)B). Expanding a k×k minor bounds its magnitude by
`k! 2^(k(m+1)B)`. Cramer's rule for `A^−1 = adj(Z) diag(row_multipliers)/det(Z)`
therefore bounds each numerator and denominator by bit height at most

    L = m(m+1)B + m ceil(log2(max(m,2))) + 3.

Reduction cannot increase that bound. Every cache checkpoint is the inverse
of a principal submatrix of the fixed source, so this L is independent of T.
The retained inverse after deletion has the analogous bound at width m−1.
Each formula forms at most O(m)-term sums of products of a fixed number of
bounded-height rationals; even using the product of denominators as a common
denominator bounds temporary bit height polynomially in m,B. Reduce after
each operation, as `Fraction` does. Ordinary integer arithmetic and gcd hence
give a polynomial bit-cost per slide, rather than an unproved constant-cost
or repeated-unreduced-fraction claim. No fast multitape implementation follows
solely from the rational operation count.

## 5. Frames, exact weights and residual certificates

A source-label permutation P is an exact orthogonal frame change:
`(PᵀAP)^−1 = PᵀA^−1P`. Permuting coordinates preserves both ∞ norm and
squared Euclidean norm; this is the finite coordinate use of the robust-frame
and tensor-packing precedents. Positive diagonal D is generally NOT orthogonal.
For it define the pullback norm `||x||_D = ||D^−1x||_∞`; then
`||A||_D = ||D^−1 A D||_∞` by substitution. This is a separate weighted-norm
argument, not an application of an orthogonal-frame theorem to arbitrary D.
It is essential when similarity weights have large ratios.

For a candidate inverse Z of the weighted principal G_J, compute the exact
rational residual `ρ = ||I−G_J Z||_∞`. If ρ < 1, the Neumann series gives

    ||G_J^−1||_∞ ≤ ||Z||_∞/(1−ρ).

Indeed `G_J Z = I−R` is invertible and its inverse has norm at most 1/(1−ρ).
Using the independent dominance bound from section 1 gives the sharper
solution-error certificate needed here:

    ||Z−G_J^−1||_∞ = ||G_J^−1(G_J Z−I)||_∞ ≤ ρ/δ_J,

where δ_J is the computed principal gap, at least δ. Thus for an input with
`||D_J^−1 b||_∞ ≤ B_0` and an additional weighted application error η,

    ||D_J^−1(y−H_J^−1b)||_∞ ≤ B_0 ρ/δ_J + η.             (5.1)

If each entry of the exact weighted inverse is rounded with absolute error
at most ε, the weighted operator error is at most mε. Rounding in weighted
coordinates avoids a spurious `max(D)/min(D)` multiplier. Restoring physical
coordinates multiplies the error bound by max_i D_ii, exactly once.
If the exact solution is known independently to be integral and this physical
bound is STRICTLY below 1/2, nearest-integer recovery is unique. Integrality is
an explicit application premise; a Gaussian inverse output is not generally
integral. At the 1/2 boundary uniqueness cannot be asserted. The finite tests
choose b = H_J z for literal integer z, so that premise is actually discharged.

## 6. Tensor payloads, correlations and block-local precision

Packing a finite tensor into a vector is a coordinate bijection and preserves
the sum of squared coordinates. Applying the same inverse separately to its
columns, or to real and imaginary components, needs no statistical independence.
For block ℓ of width m_ℓ and weighted gap δ_ℓ, the elementary ∞-to-2 comparison
and section 1 give

    ||x_ℓ||_2² ≤ (m_ℓ/δ_ℓ²) ||b_ℓ||_2².

Here x,b are in the weighted coordinates. Consequently the sum of output
energies is at most `max_ℓ(m_ℓ/δ_ℓ²)` times the sum of input energies, even
for identical or otherwise correlated inputs. Choosing c_ℓ with
`m_ℓ/δ_ℓ² ≤ 4^c_ℓ` specializes the shared DAG's block-energy accounting.
It uses the maximum block depth, not the total number of unrelated blocks.
These are separate applications of an inverse to given payloads, not a claim
that a sequential product of inverses has this bound. Cache coefficients reset
to the exact current inverse after every slide; their uniform bound likewise
depends on δ and m, not on the number of prior windows.

## 7. Injective ports and arbitrary dirty exterior

For any injective list of caller ports p_1,…,p_m, lift a local linear map T by
reading those values, applying T, writing the m results to those same ports,
and preserving every other memory value. A coordinate check proves

    lift(T_2 T_1) = lift(T_2) ∘ lift(T_1),    lift(I) = I.

Thus the generic injective word-transport theorem from the shared CNOT/TI
library applies to the SAME sequence of local maps. It does not enlarge the
generator alphabet or claim a new shortest-word/tape-time bound. For every
outside port, its arbitrary initial value is invariant, by cases on membership
in the finite port image. This is the locality/frame principle made explicit
by the shared footprint proofs, here proved directly for the finite-memory
API. The interpreter tests unstructured dirty exterior values and noncontiguous
ports. We have not built a program in that Lean multitape semantics or proved
its tape heads, halt state, restoration or primitive transition count.

## 8. Current-source relevance and evidence boundary

PR3851 prepares exact old-H principal/interior/Schur matrices, then publishes
rounded factor pages. Its producer already preserves one global rounded H;
its dense local q-model is a different matrix and cannot replace it.
This contribution freezes that boundary and supplies a reuse component for
streams of one-index-shift principal windows from the same H. Schur elimination,
weights and coefficient/minor reasoning already occur in that predecessor;
we do not claim to introduce them to the project. The newly assembled piece
is the two-sided sliding inverse cache with weighted residual and port/energy
contracts. Producing the existing protected page layout from these cached
inverses, transporting the cache through encoded tapes and pricing the complete
outer catalogue remain future integration work.

The immutable 3×3 fixture is extracted without executing upstream code from
Jose Manuel's PR3851 `gaussian_check_setup.py`. It is a rational setup fixture,
not a production Gaussian window. The 13×13 weighted cyclic band fixture is
new and synthetic. Both are labelled in RESULT.json. Across 244 slides both
routes agree with a separate forward-elimination/back-substitution solver,
satisfy both inverse identities and recover the deliberately integral payloads.
The written arguments give the universal sufficient statements; finite tests
are implementation evidence. The combined result is not newly kernel checked.

RaD's retained reusable-banded-inverse review already proves a circular-wrap
Woodbury correction and reused per-axis setup. The present delta is a changing
principal index set, not a new wrap solver. A nontrivial positive diagonal must
pass the weighted gap test itself; in the predecessor's stated ordinary
row-dominant domain D = I is admissible. No unconditional claim about every
choice of its Gaussian similarity weights is made.
