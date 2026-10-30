# Dyadic affine feasibility beyond a finite precision cap

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: scoped algebraic proof with exact finite corroboration. No new kappa.
The result distinguishes a permanent dyadic obstruction from insufficient binary
precision for a rational linear parameter region with supplied affine equalities
and a strict rational witness. It also constructs a feasible point at an explicit
sufficient precision, without enumerating that grid.

Ali Romman's [#5794](https://github.com/CrocSwap/integer-mult-bounds/pull/5794),
head `b67e65c5fcc313f3fcb1e92b199025a63cc1dec7`, constructs minimum-precision
points by bounded grid search. Its `infeasible_through_limit` deliberately leaves
finer grids open. The new step here is an all-precision decision for the supplied
strict affine model. The predecessor's search, receipts and example are cited,
not replayed or independently reviewed.

## The exact criterion and sufficient precision

Let E be an integer m by n matrix, b an integer column, A a rational k by n
matrix, and h a rational column. Consider

```text
E x = b,                  A x < h.
```

All inequalities are strict. Supply a rational witness x* satisfying both,
and integer unimodular matrices U,V giving a Smith decomposition

```text
U E V = D = diag(d_1,...,d_r,0,...),       d_i > 0,
c = U b,                                y = V^-1 x.
```

The diagonal can be rectangular. The witness ensures c_i=0 for i>r. Rational
equalities can first be cleared of denominators row by row. A precision-p point
means x belongs to 2^(-p) Z^n, with one nonnegative common precision p.

The region contains a dyadic point at some precision **if and only if**

```text
oddpart(d_i) divides c_i,                i=1,...,r.             (1)
```

When (1) holds, put

```text
p_eq = max(0, max_i [v2(d_i) - v2(c_i)]).                      (2)
```

A zero c_i contributes zero to this maximum. Equivalently, p_eq is the largest
binary denominator exponent of the reduced fractions c_i/d_i. It is the exact
minimum precision for the affine equalities alone, even after an arbitrary
unimodular change of coordinates.

For each inequality row a_l define

```text
delta_l = h_l - a_l x* > 0,
S_l = sum_(j=r+1..n) |(A V)_(l,j)|.
```

Choose any integer p>=p_eq such that

```text
S_l < 2^(p+1) delta_l                    for every row l.      (3)
```

This is an explicit finite bound. Let y*=V^-1 x*. Keep y_i=c_i/d_i for i<=r
and round every free coordinate y*_j to the nearest multiple of 2^(-p), with
halfway cases toward positive infinity. Then x=V y is a feasible precision-p
point. The checker computes the least p satisfying this sufficient bound by
integer bit lengths and one exact comparison per row. It does not claim that
this p minimizes precision for the inequalities.

## Proof

An integer unimodular matrix and its inverse both preserve Z^n. Therefore
x is in 2^(-p) Z^n exactly when y=V^-1 x is in that same grid. The transformed
equalities fix y_i=c_i/d_i for i<=r and leave the other coordinates free.
A fixed rational coordinate belongs to some dyadic grid exactly when its
reduced denominator is a power of two. This is precisely (1), and the largest
required exponent is (2). If (1) fails, the offending coordinate excludes every
precision, independently of the inequalities. If it holds, choosing all free
coordinates zero attains p_eq for the equalities alone.

For the strict region, use the rounded free coordinates described above. Their
individual errors are at most 2^(-p-1); the fixed coordinates have zero error.
Thus, row by row,

```text
|a_l (x-x*)| <= 2^(-p-1) S_l < delta_l.
```

Consequently a_l x<h_l. The transformed equalities remain exact, so E x=b.
There are finitely many positive margins and finite S_l. Hence a finite p
satisfying (3) always exists. This proves sufficiency and completes the
all-precision criterion. The argument includes rank zero, full column rank,
redundant equality rows and an empty inequality list.

The strict sign in (3) cannot generally be weakened to equality for this
rounding rule. With no effective equality, x*=1/2 and x<1, rounding at p=0
returns 1. Here S=1 and 2^(p+1) delta=1. The factor 1/2 in the error bound is
attained. The next precision returns x=1/2 and is feasible.

## Discriminating examples

- The rational singleton 3x=1 is nonempty but has no dyadic point at any
  precision. More grid enumeration cannot repair this odd obstruction.
- The singleton 2^60 x=1 first becomes feasible at precision 60. A failed search
  through precision 30 cannot distinguish it from the preceding example.
- The coupled equation 3x+y=1 has no odd obstruction. For the strict interval
  1/4<x<1/2 and witness (1/3,0), the supplied chart
  V=((0,1),(1,-3)) gives the construction (3/8,-1/8) at precision three.
  An odd coefficient by itself is not a permanent obstruction.

These examples concern representation feasibility. Their points are not new
supplier parameters and their precisions are not physical storage invoices.

## Evidence and reproduction

The standard-library verifier checks the supplied integer chart determinants,
Smith diagonal/divisibility, rational witness, grid membership, literal original
equalities and every constructed strict inequality. Its finite corpus is:

- All 2,080 scalar equalities a*x=b with 1<=a<=32 and -32<=b<=32.
- 5,568 coupled strict regions in dimensions two and three, yielding 3,712
  constructed points and 1,856 odd obstructions. Each dimension uses identity,
  every single signed elementary shear and the first/last coordinate swap for
  both charts. Six diagonal profiles, two right-hand-side signs and margins
  1/3 or 1/17 are enumerated. These are parameterized fixtures, not a count of
  distinct regions modulo equivalence.
- 216 complete bounded-grid cases over six two-dimensional diagonal profiles,
  six right charts, two signs and precisions zero through two. Every numerator
  pair in [-8,8]^2 is checked, totaling 62,424 points. The box contains a
  zero-free-coordinate attaining point whenever the equality system is feasible
  at that precision, so absence in this corpus is a valid comparison.
- Eleven rejected-input controls and three semantic controls for the strict
  rounding boundary, precision 60, and coupled cancellation of odd coefficients.

For the coupled corpus the diagonal profiles are zero; (1,0,...); (2,0,...);
(3,0,...); (1,...,1,6); and (2,...,2). The rational witness in Smith coordinates
has constrained entries sign/d_i and free entries sign/3 or sign/17. The strict
rows bound each original coordinate above and below by the stated margin.
The bounded-grid corpus uses profiles (0,0),(1,0),(2,0),(3,0),(1,2),(2,4).

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/dyadic-affine-feasibility/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/dyadic-affine-feasibility/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/dyadic-affine-feasibility
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/dyadic-affine-feasibility --check-source-history
```

Another CPython 3.12 path can replace the absolute interpreter path. Each direct
run emits `PASS_DYADIC_AFFINE_FEASIBILITY` in a generated JSON stdout receipt
with the enumerated counts and SHA256 hashes of all five package files. It
writes no files. Normal and optimized checks use explicit exceptions for
contracts, so optimization does not disable them. Finite evidence corroborates
the written proof; it does not replace its quantified argument.

## Scope, provenance and limitations

The original `uniform-transfer-audit` card is changed to this parameter-format
side result. It resolves no selected framework assumption and supplies no
actual physical caller. Its use is to stop futile precision searches when an
exact equality forces an odd denominator, or construct a point preserving
supplied strict margins when the obstruction is absent.

Base is canonical main `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority
revision 8. [SOURCES.json](SOURCES.json) pins the catalogue and selected record
as historical provenance. No external scientific code is imported or replayed.
The [#5794 guide at its exact head](https://github.com/CrocSwap/integer-mult-bounds/blob/b67e65c5fcc313f3fcb1e92b199025a63cc1dec7/docs/research/dyadic-parameter-search.md)
supplies the finite-grid context. Smith normal form, localization at two and
nearest-grid error bounds are classical; no literature-priority claim is made
for those ingredients. The contribution is the combined all-precision decision,
exact equality threshold and margin-preserving constructor at this interface.

The theorem is unrestricted in dimension and precision. The executable helper
accepts at most six equality rows/coordinates, 32 inequalities, input integers
and reduced rational numerators/denominators of at most 64 bits, and constructed
precision at most 4,096. Unsupported inputs raise an error, not an infeasibility
claim. The replay CLI takes no arguments. Smith extraction, affine-hull recovery
and finding the rational strict witness are not implemented. General closed
regions require exposing any forced equalities and supplying the stated strict
witness for the remaining rows. Nonlinear constraints are outside the theorem.

All loops have finite bounds from those dimensions or the explicitly enumerated
corpus. There is no recursion, dynamic code generation or external process.
Functions are below 60 physical lines. Python's managed allocation is a stated
deviation from fixed-allocation discipline; finite input bit sizes, dimensions,
precision and corpus bound live storage. Warning-strict direct execution and
registered replay are the applicable diagnostics; no separate static analyzer
or proof kernel is claimed.

The selected source-binding baseline passed as orientation only. No selected
scientific replay, Lean, Docker, native execution, stock/precision/tape costing,
compiler admission or analytic recovery proof is supplied. Independent human
and formal proof-kernel review are unclaimed.

## Open next questions

1. Can an actual supplier's parameter proof supply the integer equalities,
   Smith charts and rational strict witness required here? Start with one
   literal constraint list and charge its resulting format. Source validity,
   nonlinear terms and physical arithmetic remain blockers.
2. Can a checked affine-hull extractor turn a general closed rational region
   into this strict relative-interior interface? Start with equalities forced
   by pairs of closed inequalities. Exact identification of all forced faces,
   rather than a bounded-grid failure, is the missing step.

Credit Ali Romman for #5794's bounded dyadic parameter interface and explicit
finite-limit distinction. The selected supplier and its full credited lineage
are historical context only. Existing contributor files and credit are unchanged.
