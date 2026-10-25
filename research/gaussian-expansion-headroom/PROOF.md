# Gaussian expansion with certified chirp headroom

Prepared by Dugongue with substantial OpenAI Codex assistance. Apache-2.0.
This is an informal universal proof with executable rational corroboration.
It has not received independent human review or a new Lean kernel audit.

## 1. The result and its exact interface

For positive integers s, t and u, define the normalized periodic Gaussian map

    (A z)_k = 1/(2√u) ∑_{j∈ℤ} exp(−π(j−s k/t)²/u) z_{j mod s},
    0 ≤ k < t.

Thus A is the existing source-normalized expansion S/2, with α² = u.
No Fourier permutation or normalization is changed. Define

    b(u) = 1/2 + 1/(20^u − 1).

**Theorem 1 (one axis).** For every such s, t, u, every p ≥ 1 and q ≥ 8,
and every complex p-grid input with max_j |z_j| ≤ 1, `prepare` followed by
`line` returns complex p-grid output y satisfying

    max_k |y_k| ≤ b(u) ≤ 21/38 < 3/5.

If δ is the maximum `Row.deficit` returned by preparation, then also

    max_k |y_k − (A z)_k| ≤ δ + √2 · 2^(−p)
                              ≤ δ + 2 · 2^(−p).

The construction is finite, uses nonnegative downward dyadic coefficients,
and certifies δ by exact rational arithmetic. The norm conclusion does not
require δ to be small. Accuracy requires the displayed, computable bound.

**Theorem 2 (all tensor dimensions).** Let D ≥ 1 and let the axis parameters
be positive integer triples (s_i, t_i, u_i). Apply each axis once in the
declared row-major layout, rounding after each axis as in `tensor`. For every
unit sup-norm input tensor the returned tensor satisfies

    ||y||∞ ≤ M_D = ∏_{i=1}^D b(u_i) ≤ 21/38 < 3/5.

Put M_0 = 1, E_0 = 0, and let δ_i be the maximum prepared row deficit on
axis i. Relative to the exact tensor product of the maps A_i, its error is
at most E_D, where

    M_i = b(u_i) M_{i−1},
    E_i = b(u_i) E_{i−1} + δ_i M_{i−1} + 2 · 2^(−p).

No independence, orthogonality, equal axis lengths, or volume factor is
assumed. These two theorems are sufficient norm and error contracts.

PR3763 requires an encoded p-grid input of norm at most 0.6 and p−A ≥ 13.
Theorems 1–2 establish the numerical norm clause for these expansion outputs;
the caller must separately establish p−A ≥ 13 and the actual encoded physical
handoff. An additional approximation of modulus at most 9/190 still satisfies
the norm clause, because 3/5 − 21/38 = 9/190. This is a handoff allowance,
not an assertion that unimplemented physical operations have zero error.

## 2. Periodization and the theta bound

We use the classical Gaussian Fourier formula and Poisson summation, present
in the linked Lean tree as `fourier_gaussian_pi'`, `Real.tsum_eq_tsum_fourier`
and `Complex.tsum_exp_neg_quadratic`. The exact source references and evidence
levels are in LIBRARY-BRIDGES.md. They are mathematical precedents, not new
formalization claims.

Let g(x) = u^(−1/2) exp(−πx²/u). In the Fourier convention
ĝ(ξ) = ∫ g(x) exp(−2πiξx) dx, the Gaussian formula gives
ĝ(ξ) = exp(−πuξ²). Both g and ĝ have Gaussian decay. In particular, their
integer translates have summable sup norms on every compact interval, and
their sampled Fourier series converges absolutely. These verify Poisson's
hypotheses and justify

    u^(−1/2) ∑_{j∈ℤ} exp(−π(j−x)²/u)
      = ∑_{n∈ℤ} exp(−πu n²) exp(2πinx)
      = 1 + 2∑_{n≥1} exp(−πu n²) cos(2πnx).

The series on the left is nonnegative. Taking absolute values on the right,
or using cos ≤ 1, bounds half of it by

    1/2 + ∑_{n≥1} exp(−πu n²)
      ≤ 1/2 + q0/(1−q0),       q0 = exp(−πu).

Here n² ≥ n and 0 < q0 < 1. This is the same geometric majorization used
by Mathlib's `norm_jacobiTheta_sub_one_le`; no new theta identity is claimed.
For an entirely rational universal constant, π > 3 and

    exp(3) > ∑_{n=0}^9 3^n/n! > 20

imply q0 < 20^(−u) for integer u ≥ 1. Since q/(1−q) is increasing on
(0,1), every normalized row mass is strictly below

    1/2 + 1/(20^u−1) = b(u) ≤ b(1) = 21/38.

All exchanges of sums below are justified by nonnegativity or absolute
convergence. Grouping j by j mod s partitions the full integer lattice;
every winding is included, even when several j have the same residue.
Consequently A has nonnegative real entries and row sums at most b(u), for
every center s k/t, including boundary, fractional and wrapped centers.

For any complex vector v, the triangle inequality now proves

    |(A v)_k| ≤ ∑_r A_{k,r}|v_r| ≤ b(u)||v||∞.

This is an induced sup-norm estimate. Frobenius or Euclidean tensor bounds
would introduce different dimension factors and are not substituted for it.

## 3. A finite downward coefficient construction

Fix one row center c = s k/t. The code chooses

    R = max(u, floor(√(u(q+16))) + 2)

and retains all integers from floor(c)−R through ceil(c)+R, inclusive. This
contains every integer at distance at most R. On each omitted side the
first distance is at least R, and successive distances increase by one.
Thus the first Gaussian term is at most exp(−πR²/u), and the ratio of each
successive term to its predecessor is at most exp(−π(2R+1)/u). Put

    a = floor(3R²/u),      b = floor(3(2R+1)/u).

Because π > 3 and e > 2, the two omitted sides, after multiplication by
1/(2√u), have total mass at most

    T = 2^(−a)/(1−2^(−b)).

We used √u ≥ 1. R ≥ u ensures b ≥ 6, so the denominator is positive.
The bound remains valid when the first omitted distance exceeds R; no
integer term at the endpoints is silently dropped. The chosen R also gives
a ≥ 3(q+16), so this tail is much smaller than one q-grid unit.

For a retained j, let c_j = exp(−π(j−c)²/u)/(2√u). The credited outward
interval backend supplies q-grid endpoints l_j ≤ c_j ≤ h_j. The construction
uses w_j = max(0,l_j), also a q-grid value. Since c_j ≥ 0,

    0 ≤ w_j ≤ c_j,       c_j − w_j ≤ h_j − w_j.

Sum w_j over retained j in each residue class to form the finite matrix B.
Then entrywise 0 ≤ B ≤ A and

    ∑_r (A_{k,r} − B_{k,r}) ≤ T + ∑_j (h_j−w_j) = δ_k.

This is exactly the stored row deficit. It simultaneously bounds the
operator error ||A−B||∞ and prevents coefficient rounding from increasing
the analytic row mass. The implementation also checks the rational
inequality ∑_r B_{k,r} ≤ b(u). This finite check corroborates the universal
argument and rejects malformed coefficients; it is not a replacement for
the theta proof.

For completeness, the interval arithmetic has the following justification.
Addition and negation use exact endpoint arithmetic; multiplication rounds
the extreme endpoint products outward. Positive reciprocation reverses
endpoints. Integer square root on u·2^(2q) brackets √u between consecutive
q-grid points. Machin's identity for π is evaluated with alternating
arctangent remainders before outward rounding. For exp(−x), x ≥ 0, the
backend reduces x by powers of two into [0,1/8], encloses the positive
Taylor series for exp(x) there with its geometric factorial tail, takes
the positive reciprocal and squares back outward. At q ≥ 8 the dyadic
division retains the [0,1/8] endpoint. If x ≥ q, exp(−x) < 2^(−q) follows
from e > 2 and justifies the backend's [0,2^(−q)] shortcut. These operations
enclose every coefficient; no floating-point exponential enters acceptance.
The full predecessor interval proof and authorship remain credited.

`Row.check` verifies shape, positivity and the mass inequality. `line` also
compares each supplied row to canonical certified preparation, so changing
its center, deficit or weights cannot turn an arbitrary row into an
accepted approximation certificate. Source hashes are checked before the
vendored numerical module is imported. These guards assume an unchanged
trusted program and manifest, rather than claiming security against their
coordinated malicious replacement.

## 4. Inward grid rounding preserves the hard disk bound

For a real x define Q_p(x) = sign(x) floor(2^p|x|)/2^p, with Q_p(0)=0.
It satisfies |Q_p(x)| ≤ |x| and |Q_p(x)−x| < 2^(−p). Apply it separately
to the real and imaginary parts. For every complex z,

    |Q_p(z)|² ≤ |z|²,       |Q_p(z)−z| ≤ √2 · 2^(−p).

`line` computes Bz exactly from integer numerators, then applies Q_p once
per component. Therefore

    |Q_p(Bz)| ≤ |Bz| ≤ b(u)||z||∞,
    |Q_p(Bz)−Az| ≤ √2·2^(−p) + δ||z||∞.

This proves Theorem 1, including arbitrary signed complex phases. Inward
rounding is nonlinear; we use only its pointwise modulus and error bounds,
not a false assertion that it is a linear or nonexpansive operator on
differences. Nearest-grid rounding can increase modulus, as the coarse-grid
control demonstrates. At production precision its small increase could
instead be charged against 9/190; the present construction preserves the
hard bound directly.

## 5. Tensor composition, layout and error transport

Lift A_i and B_i to the full tensor by acting along axis i and leaving
every spectator coordinate unchanged. Each lifted map has the same induced
sup-norm bound as its line map: every output coordinate belongs to exactly
one spectator line. The row-major index is

    (((k_1 s_2 + k_2)s_3 + k_3) ... )s_D + k_D

before that axis is replaced by its target length. The code fixes spectator
coordinates, reads all source positions, and writes every target position
once. This is a bijective enumeration of the declared coordinate tuples.
It does not perform a CRT permutation or infer one from coordinate count.

Suppose the implemented intermediate tensor has norm at most M_{i−1} and
error at most E_{i−1} relative to the exact intermediate tensor. Positivity
and inward rounding give its next norm bound b(u_i)M_{i−1}. For error, add
and subtract A_i applied to that same implemented intermediate tensor:

    Q_p(B_i y) − A_i x
      = [Q_p(B_i y)−B_i y] + (B_i−A_i)y + A_i(y−x).

The three terms are bounded respectively by 2·2^(−p), δ_i M_{i−1} and
b(u_i)E_{i−1}. This proves the recurrences and Theorem 2 by induction.
Equivalently, every earlier error is multiplied by the later contraction
factors. No independence assumption is used, and spectator multiplicity
does not multiply a sup-norm error.

The exact Gaussian tensor execution, tensor packing and three-mode
telescope modules in the shared library suggested this decomposition.
Their Gaussian-integer or orthogonal/Frobenius hypotheses are different;
the positive rectangular sup-norm argument above proves what is needed
here directly. For the retained bulk caller, the number of actual resampled
axes is D = d−1. The inherited recovery exponent remains
γ = ∑_i (2u_i + j_i + 1). The factor 1/2 in each expansion is preserved,
and this norm improvement removes none of the required recovery scales.

## 6. Explicit bounded windows and dirty exterior

The host `window` adapter names injective source and output positions and
requires them to be disjoint. It reads exactly the source positions, uses
the certified line map, copies the finite storage map and writes exactly
the output positions. Hence every borrowed source and every other existing
storage entry retains its original value, with no condition on dirty
exterior contents. Theorem 1 holds on the returned output positions.
The proof is simply inspection of the read and write sets and injectivity.

This instantiates an arithmetic frame contract inspired by
`FootprintedRuns.frame`. It is a host dictionary adapter. No multitape
transition table, physical head restoration, or tape running-time bound is
deduced from the Lean frame theorem without an actual run and footprint.

## 7. Cost, finite evidence and remaining composition

For one prepared axis there are t rows with at most 2R+2 retained integer
terms each. Coefficients can be prepared once and reused across all
spectator lines. The supplied dense reference retains s coefficients per
row, so its online arithmetic costs O(st) integer multiply-adds per line,
plus p-grid truncation; preparing transcendental enclosures and arbitrary
precision integer bit costs are additional. A tensor axis with current
volume N has N/s lines. Indexed arrays and complete dense coefficient rows
are used. These costs do not establish the desired fast physical expansion.

The retained exact checks cover 34 rows, 340 complex line values and 80
tensor output coordinates. They include u = 1, 2, 4, 10, nonsquare √u,
fractional centers, repeated periodic residues, complex signs, two and
three axes, and a p = 101 case. A separately indexed residue-first oracle
and a direct Kronecker matrix compare the results and their error bounds.
They share the credited interval transcendental backend; they are not an
independent transcendental implementation. Finite corroboration is not a
proof for all parameters; the preceding argument supplies that proof.

The physical source-normalized expansion, protected page encoding,
catalogue/halo routing, sequential tape costs, complete outer tensor caller,
CRT conversions, and final integer recovery remain to be joined. PR3851's
compression core and PR3763's chirp consumer are not executed by this
package. Their other hypotheses are inherited only when a future caller
actually instantiates them. No new κ, complete multiplication theorem,
selected-frontier change, or practical speedup is claimed.
