# Exact dyadic scale and complete replay equivalence

The frozen source is PR5826 at58f93cf41751920f3d6766a39caccc2974ce18b0.
Its official source export is retained unchanged. The candidate changes the
arithmetic representation of sparse coefficients. It changes no native word,
error allowance, operation count, endpoint, guard inequality or scientific claim.

For each row, keep an upper bound d on the exponent of two in the denominator
of any coefficient. Start d=0. A reset sets d=0. MOVE leaves it unchanged.
SCALE by n/2^k sets d to d+k. ADD or additive COPY from s into r sets
`d_r=max(d_r,d_s+k)`. Injection of a new unit defect requires only exponent0.
The same rule on the transposed word uses `d_s=max(d_s,d_r+k)`. These bounds
ignore cancellations and powers of two in n; thus they can be conservative.
Take E to be the largest bound on either traversal and S=2^E.

Induction on each event proves that every exact forward and transposed
coefficient is an integer multiple of 1/S. Store its numerator at this common
scale as a Python arbitrary-size integer. Multiplication by n/2^k is exact:
first multiply by n, then divide by 2^k. The implementation checks divisibility
before every division. It does not truncate, use a modulus or accept a floating
comparison. A nondyadic coefficient is rejected. The same scale covers ideal
input coefficients; it is a representation bound, not a numerical precision
or magnitude promise for the physical caller.

Choose separate power-of-two scales A and C for the nonnegative local weights
a_j and c_j. If a coefficient is z/S, its three exact score contributions are

`abs(z)*a_j*A/(S*A)`, `abs(z)*c_j*C/(S*C)`, and `abs(z)/S`.

The numerator updates use the signed sum z_old+q*z_source before taking its
absolute value. Thus a cancellation changes the score by
`abs(z_new)-abs(z_old)`, including negative changes. The candidate does not
replace signed transfer by an absolute-value propagation bound. All score units
are fixed, so comparisons, tie choices and Pareto order agree with the rational
reference. Fraction conversion occurs only at the result and hash boundaries.
Canonical reduced numerator/denominator encodings preserve all source hashes.

The transposed pass uses a separate traversal with the same proved scale. It
checks every final signed coefficient and score. The original literal scalar
execution and reverse-cut oracles remain unchanged. The original contract's
complete ideal endpoint, native frame/ownership checks, guards, attaining
fixtures and six rejection controls remain active.

`contract.py` is an explicit adapted copy of the source runner. Its four declared
edits add source-directory and backend parameters. Its obsolete direct CLI is
removed; this package supplies its own CLI. The checker reconstructs these
exact edits before loading the runner. This is ordinary dependency injection;
no module, global function, source file or import hook is patched at runtime.

Qualification compares the complete baseline and candidate results, all actual
signed witness rows, and120 separate finite dyadic error words with cancellation,
scaling, reset, COPY and varied defect sites. It also compares each finite
transposed result and rejects nondyadic scalars, nondyadic weights and inexact
integer divisions. The frozen source and package code remain distinct.

The default command runs the fast complete source contract and compares the
entire result to the frozen expected record. `--qualify` additionally runs the
slow reference and the extra cross-checks; its cost is not hidden in the speedup.
`--baseline` runs the unmodified source contract for a matched timing. Timings
include source authentication, archive extraction and full original controls.
No cache is shared between processes. Local measurements are not a promise
about another machine or hosted CI.

The original precision theorem remains conditional. Native unitary gauges,
physical resets, exact owned return, compiler, precision-tape and analytic
admission retain their prior status. Faster verification is not a new kappa.
