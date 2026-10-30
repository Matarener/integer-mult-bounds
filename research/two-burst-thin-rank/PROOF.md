# Fixed-schedule rank certificate

## Statement

Work over `F2[x0,x1,x2,e]/(e^2)`. The six full calls are the first six
records in the pinned `SOURCE-WORD.json` of PR #5699, inherited from Ali
Romman's PR #5673. Call i is

`Fi = I + x_stage(i) Pi + e Ri + e x_stage(i) Ri`.

The full-call order is exactly `(1,3,2,4,0,5)`. A gap numbered k is after k
full calls. Thin queries may occur only in gaps 2 and 4, and each is `I+e Q`
with Q a constant binary rank-one matrix. Legal source thin queries also have
`Q^2=0`. The intended endpoint is `(1+e) A`, where

`A = product_(j=0..2) (I + xj (P_(2j)+P_(2j+1)))`.

The minimum number of thin queries in this schedule is eight. The lower
bound allows arbitrary rank-one Q, so it also applies when square zero is
required. This is a finite binary certificate with a mathematical reduction.

## Reduction to two aggregate matrices

Since `e^2=0`, a consecutive burst satisfies

`product_i (I+e Qi) = I+e sum_i Qi`.

Let Z1 and Z2 be the sums at the two gaps. Let `A+e B` be the product of
the six full calls, with later calls multiplying on the left. Let Lg and Rg
be its e-free suffix and prefix at gap g. Contributions containing two e
factors vanish. Thus the complete endpoint is correct exactly when

`L2 Z1 R2 + L4 Z2 R4 = A+B`.

This equation has no products of unknown entries. Every xj occurs in two
full calls, so all exponents lie in `{0,1,2}^3`. Comparing all 27 monomials
and all 64 matrix entries produces exactly 1,728 equations on 128 unknown
binary entries. Zero equations are retained. No coefficient is discarded.

`algebra.build_system` constructs each column by substituting a single
matrix unit into one aggregate. It constructs A independently from the three
stage projectors, checks the e-free endpoint, and computes the discrepancy
A+B from the six calls. Every matrix is represented by eight packed binary
rows; no floating arithmetic is used.

## Complete finite domain

Binary row elimination on the augmented system finds 104 pivots and 24 free
coordinates. Back substitution constructs one particular solution z0 and
one homogeneous vector vj for each free coordinate. The verifier checks the
particular and all homogeneous vectors in the original coefficient system.
Each vj has free coordinate j equal to one and every other free coordinate
zero, as follows directly from its construction. Consequently every solution
has a unique representation

`z = z0 + sum_(j=0..23) bj vj`, with `bj in F2`.

The loop runs through all 24-bit reflected Gray words. At step i>0 the bit
that changes is the least significant set-bit position of i, so XORing the
corresponding vj visits every assignment once. It visits exactly `2^24`
solutions. Eight-row binary elimination computes both aggregate ranks at
every step. The resulting complete histogram has no pair with rank sum below
eight and has pairs of ranks `(4,4)`. Stdout includes that histogram and the
reconstructed affine basis rather than trusting a saved search verdict.

The finite calculation therefore certifies

`rank(Z1)+rank(Z2) >= 8`

for every feasible binary aggregate pair. It says nothing about assigning
nonbinary extension-field values to the free coordinates.

## Query count and attainment

If burst i contains ki rank-one queries, matrix rank subadditivity gives
`rank(Zi) <= ki`. Thus `k1+k2 >= 8` for every complete word in this schedule.
This implication permits repeated factors, any number of factors and any
binary entries; it does not assume that either aggregate is square zero.

PR #5699 supplies four rank-one square-zero factors in each burst. The new
verifier reads those cited factors, checks each rank and square, checks their
aggregate sums, and substitutes the two sums into every endpoint coefficient.
They give eight queries, proving attainment. The construction and its credit
remain with the predecessor. The new contribution is the exhaustive lower
bound for the fixed schedule, not an audit of its earlier gap optimum.

## Implementation bounds and verification limits

All loops have fixed finite bounds: matrices have eight rows, polynomials at
most 27 monomials, the coefficient system has 1,728 rows and 128 columns, and
the exhaustive loop has exactly 16,777,216 iterations. Row elimination is
iterative. Functions are below 60 physical lines. Checks use explicit failures
and remain enabled under `-O`.

Python's managed allocation is a documented Power of Ten deviation. The
enumeration holds one 128-bit solution, 24 basis vectors, two eight-row rank
bases, and an 81-entry histogram. It never retains the solution list. Polynomial
and system storage are bounded by the fixed dimensions above. Each source
input is bounded by one MiB. The standard-library JSON parser and Python
runtime allocate internally; no claim of allocation-free execution is made.
The one local module is loaded by its explicit sibling path so isolated and
Git-free execution use the same code. No recursion, external solver, subprocess
or network call occurs in the verifier. Warning-strict normal and optimized
registered runs provide the available runtime diagnostics; no Python static
type-checker certification is claimed.

Controls cover invalid row encoding, changed full order and gaps, a damaged
aggregate, a rank-one factor that is not square zero, an inconsistent system,
an altered endpoint, a constant-only false positive and a small Gray-domain
enumeration. All 512 three-by-three binary matrices also receive an independent
kernel-cardinality rank check with five identity coordinates.

This does not establish a field-uniform obstruction, a new native word,
physical restoration, a favorable supplier invoice or any multiplication
theorem. All five selected framework assumptions remain separate.
