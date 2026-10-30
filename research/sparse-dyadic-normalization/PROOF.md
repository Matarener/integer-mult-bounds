# Sparse dyadic normalization at rational rank one

Let R = Z[1/2]. One arbitrary scalar x is observed through the mandatory
coefficient a > 0 and selected eligible coefficients b_i in Z. The decoder
must have the form

    x = c_0 (a x) + sum_{i in J} c_i (b_i x),   c_i in R,

as an identity for every x. Each acquired menu entry i has its declared
positive cost w_i. The mandatory observation is already present and is not
included in this incremental charge. No other observation or arbitrary new
linear combination is available for free.

## 1. Exact scalar criterion

Such a decoder exists if and only if

    gcd(a, (b_i)_{i in J}) is a power of two.

For necessity, clear a common power-of-two denominator from a proposed decoder
identity at x = 1. The integer gcd must divide that power of two. For
sufficiency, integer Bezout coefficients express the positive gcd g as a
combination of the observed coefficients. If g is a power of two, dividing
those coefficients by g gives an allowed decoder. This also handles an empty
selection, zero menu entries and negative menu entries. The condition is on
the odd part of the gcd, not on rational rank or on whether one entry is a
dyadic unit.

The identity is valid over any R-module. Necessity already holds when x ranges
over R. This is not a statement for fields in which every odd prime is inverted.
Rational observation coefficients whose denominators are powers of two reduce
to the same integer criterion by clearing a common power of two.

## 2. Exact encoding of a finite weighted cover problem

Take any finite universe U, distinct odd primes p_u for its elements, and an
indexed menu of subsets S_i of U. Repeated subsets and the empty subset are
allowed. Define

    a = product_{u in U} p_u,
    b_i = product_{u in U minus S_i} p_u.

Empty products are one. For every selected index set J, unique prime
factorization gives the exact identity

    gcd(a, (b_i)_{i in J}) = product_{u not in union_{i in J} S_i} p_u.

Indeed, p_u divides a and every selected b_i precisely when no selected S_i
contains u. All coefficients are positive squarefree divisors of the same odd
integer a. Therefore J permits dyadic decoding if and only if its sets cover
U. Feasibility, every feasible index set, all positive additive costs, all
optimum costs and every optimum index set are preserved exactly. If no cover
exists, no allowed acquisition menu decodes. If U is empty, the mandatory
unit coefficient already decodes and the optimum incremental charge is zero.

Thus the menu-selection problem contains arbitrary finite weighted Set Cover
already at rational rank one. This is an exact finite optimization encoding;
no new complexity-theory classification or approximation lower bound is
needed for the obstruction claimed here.

## 3. Sharp unbounded acquisition count with rank unchanged

For any integer n >= 1, choose n distinct odd primes and let S_i = {i}. Then

    a = p_1 ... p_n,   b_i = a / p_i.

Every menu entry is necessary. If entry i is missing, every available observed
coefficient is divisible by p_i. Clearing dyadic denominators would force
p_i to divide a power of two, which is impossible. All n entries suffice
because the gcd is one, so the exact minimum incremental acquisition count
is n. For arbitrary positive prices the exact optimum is sum_i w_i.

The observation matrix has one column and rational rank one before any
acquisition, after every partial acquisition, and after completion. The
rational decoder (a x)/a therefore sees no rank deficit, while the constrained
dyadic decoder can require arbitrarily many acquisitions. The cheapest
unrestricted added observation would be x itself and would require one
acquisition; it is not in the declared singleton menu when n >= 2.

For example, a = 105 and the menu is 35, 21, 15. Every two-entry selection
leaves one odd prime in the gcd. All three decode with the literal identity

    -105 + 2*35 + 21 + 15 = 1.

This is the first delivered obstruction. No larger construction is pursued.

## 4. Connection and limits

Ali Romman's [PR #5789](https://github.com/CrocSwap/integer-mult-bounds/pull/5789)
explicitly distinguishes rational rank certificates from dyadic completion
and legal delivery. The new step is the sparse eligible-menu acquisition
obstruction, not another rank certificate or an audit of that tool. Bezout,
prime factorization and weighted Set Cover are classical ingredients.

The result concerns the existence of a decoder under a declared menu. It
does not construct a physical source, prove that any current caller realizes
these coefficients, price coefficient synthesis, constrain intermediate
magnitudes, restore dirty helpers, or admit an integer-multiplication supplier.
In particular it is not an n-call lower bound for unrestricted circuits, free
mixing of unacquired rows, nonlinear decoders, or a changed coefficient ring.
It changes no selected frontier or inherited framework assumption.

## 5. What the executable checks

The all-n result above is a written proof. The independent executable
corroborates a finite domain. It constructs menu coefficients from subset
complements, computes gcds with the standard-library integer oracle, produces
Bezout coefficients with a separate bounded Euclidean algorithm, and replays
the decoder at three exact rational scalar inputs. It compares optimum costs
with literal subset-union enumeration for every price tuple in {1,2,3}^m.

The complete menu domain is 0 <= |U| <= 3, 0 <= m <= 3, with every ordered
menu, including repetitions. Separately it checks every selection of the
singleton family for 1 <= n <= 12 and a modular missing-prime obstruction for
each infeasible selection. Signed, zero, non-squarefree and dyadic-unit
boundaries, invalid inputs, forged coefficients and rational-only decoding
controls are included. The report enumerates its actual counts and binds all
six package files by SHA256. It is generated on stdout, never hand-written.

## 6. Verification implementation bounds

The executable has no recursion, external dependencies or file writes. It
reads only the six package files for its generated hash receipt. Fixed test
domains bound every enumeration. The decoder permits at most 16 optional rows
of at most 4096 bits each. Extended Euclid has at most twice the larger input
bit length plus two iterations, since every two divisions at least halve the
positive remainder. Functions stay below 60 physical lines.

Python's integer and Fraction operations allocate dynamically. This is a
managed-runtime deviation from fixed-allocation rules, bounded here by the
finite domains and input limits. Iterative Bezout coefficient growth is bounded
by a product of at most 17 input magnitudes. Negative controls intentionally
pass one of a fixed set of direct functions as a callback. Production checking
does not use dynamic dispatch. Explicit ValueError checks remain enabled under
-O. No compiler, external linter, proof kernel, Lean or Docker is required.
