# Downward rounding of the actual across-cell Gaussian coefficient

**Result:** the retained two-ulp repair applies to the original across-cell
Gaussian exponent. It constructs a stored coefficient `H` satisfying

```text
0 <= H <= n,                 0 <= n - H < 4 * 2^-P.
```

This supplies the coefficient-construction step left open by James Reed's
[PR #4442](https://github.com/CrocSwap/integer-mult-bounds/pull/4442), pinned
at `d079c2b058ebd3d7a9ff424113b095bf61175427`. The subtraction/clipping method
is already in the retained phase-cell review. The contribution is its exact
caller instantiation, error accounting and separately written controls.
It does not establish that an existing executable page generator uses this
construction. No new kappa or selected-frontier change is claimed.

## Caller and exact exponential arguments

Let `s,t,u` be positive integers with `t>s` and `u=alpha^2`. Write

```text
rho = t/s,
q_i = floor(t*i/s + 1/2),
b_i = t*i - s*q_i,           beta_i = b_i/s.
```

Thus `-s/2 <= b_i < s/2`, including the specified tie convention. For any
integer offset `h`, the original coefficient in LOG-A section 1 is

```text
n_i,h = exp(-pi*u*((rho*h + beta_i)^2 - beta_(i+h)^2)).
```

Use the nonnegative integers

```text
j = u*((t*h + b_i)^2 - b_(i+h)^2),       k = s^2.
```

Then **exactly** `n_i,h = exp(-pi*j/k)`. No approximate exponent or
within-cell gauge identity is substituted. If `h != 0`,

```text
|t*h + b_i| >= t*|h| - |b_i| > s/2 >= |b_(i+h)|,
```

so `j>0`. If `h=0`, `j=0`; the source construction stores the diagonal as
exactly one instead of applying the repair. This proves the nonnegative
argument condition for every retained off-diagonal coefficient, including
cell changes and either sign of `h`.

A second form useful for checking the integer arithmetic is

```text
d = q_(i+h) - q_i,
j/k = u*d*(d + 2*b_(i+h)/s).
```

At a physical period cut, keep the unwrapped signed offset `h`:
`q_(i+s)=q_i+t` and `b_(i+s)=b_i`. Do not replace `h` by a residue before
forming the square gap. This treats the single retained coefficient at
that offset, not a sum of all periodic aliases. The truncation and deletion
of nonzero diagonal aliases remain the source construction's choices.
For a circular band with `2W<s`, retained signed offsets identify distinct
columns, so the entry count below applies without alias multiplicities.

## Repair lemma and its exact boundary

Let `eta=2^-P` and suppose the negative-real exponential routine returns a
real P-grid number `z` with `|z-n|<2*eta`. This is the error contract invoked
in the retained review's **Computable rounding and perturbation** section;
see also Harvey and van der Hoeven, [negative real exponentials, Lemma 2.13](https://www.texmacs.org/joris/nlogn/nlogn.pdf).
Take the real component if the routine represents its output as complex.
Define

```text
H = max(0, z - 2*eta).
```

If `z>2*eta`, then `H=z-2*eta<n` and
`n-H=n-z+2*eta<4*eta`. Otherwise `H=0` and
`n<z+2*eta<=4*eta`. In both cases `0<=H<=n` and the stated strict error
bound holds. The output remains on the P-grid. Underflow to zero is
permitted for these off-diagonal entries; the separate positive-weight
requirement inside a cell is not being weakened.

A two-ulp margin is necessary among nonnegative integer-ulp safety
margins under this black-box error
contract: `n=3*eta/2, z=3*eta` is admissible, but subtracting only one ulp
still exceeds `n`. The constant four is a sharp supremum for the same
contract: `z=2*eta, n=(4-delta)*eta`, with `0<delta<1`, produces zero and
error approaching `4*eta`. These are statements about the stated oracle
contract, not lower bounds for a more accurate exponential implementation.

The exact `j,k` above therefore discharge the missing application of the
repair to across-cell entries. If `j>=k*P`, zero is already safe because
`exp(-pi*j/k)<=exp(-pi*P)<2^-P`. Otherwise `j<k*P`; the exponential
routine receives an ordinary nonnegative rational argument. In the source
parameter regime, `log s`, `log t`, `log u`, `log W` and `P` are polynomially
bounded in the outer parameter. Forming `j,k`, subtracting two ulps and
clipping consequently need only polynomial per-coefficient work and no
larger output grid. This does not count all coefficient requests or prove
the global setup, routing or tape bound. The published fast exponential
lemma is an inherited mathematical input, not re-proved here.

For a row or column with at most `2W` retained off-diagonal entries, the
**across-cell rounding contribution alone** has absolute sum below
`8W*2^-P` when `W>0` (zero when `W=0`). This does not include truncation,
within-cell weight ratios, diagonal aliases or later page-rounding errors.
Under #4442's other hypotheses, its across-cell domination premise is now
available for the reference constructed with this routine. Its ideal gaps,
within-cell estimate and halo exponent/minimality calculations have not
been independently audited by this package.

## Two distinctions that matter at the caller

The repair must approximate the original `n_i,h`, not the bare Toeplitz
kernel. The inherited #4442 example has `s=4,t=5,u=1,i=1,h=1`:
`beta_i=1/4`, `beta_(i+h)=-1/2`, and the square gap is `2`, while
`rho*h^2=5/4`. The checker certifies that even the repaired 64-bit bare
kernel exceeds the true coefficient. This counterexample is credited to
#4442; its interval check is new here.

The reference `H` and its online coupling pages are separate objects.
Later nearest rounding to a coarser grid can destroy domination. For
example, the admissible oracle values `n=3*eta/2,z=3*eta` give `H=eta`;
nearest rounding to the `2*eta` grid, with ties upward, gives `2*eta>n`.
Further rounding **toward zero** preserves domination, with its own added
absolute-error budget. The source reports already charge separate coupling
rounding; no zero-cost or exact-page identification is asserted here.

## Evidence and reproduction

`verify.py` uses only Python's standard library and exact integer/Fraction
arithmetic. Its separately written numerical oracle encloses pi with
Machin's identity and alternating arctangent sums, encloses `exp(-x)` by
alternating Taylor sums after reducing to `[0,1/2]`, and rounds both
endpoints outward after every squaring. Monotonicity combines the argument
and exponential enclosures. A nearest-grid midpoint supplies `z`; the
checker then requires `H<=lower(n)` and `upper(n)-H<4*eta`. It does not
implement or test the published fast exponential routine.

The series enclosures follow from alternating terms of decreasing size.
After reduction, all exact exponentials and their clipped upper endpoints
lie in `[0,1]`; squaring is monotone there. Machin's identity is
`pi=16*atan(1/5)-4*atan(1/239)`. The chosen signs in `pi_bounds` round the
subtraction outward. Increasing internal precision until the interval is
shorter than `eta/8` terminates; no floating-point comparison is used.
The coarse underflow interval `[0,eta]` uses the analytic shortcut above.

[RESULT.json](RESULT.json) records 384 coefficient cases, 1,624 phase
identities, 2,019 oracle-boundary cases and the coefficient digest. In 81
coefficient cases the uncorrected approximation provably exceeds the exact
coefficient, so the downward correction has an observable effect.
Fixtures cover five rational phase models, precisions 24, 64 and 128,
positive and clipped outputs, both offset signs, internal and physical
period cuts, and nearest-index ties. These are boundary models, not
complete fine-prime multiplication instances. A separate rational mesh
checks every admissible integer oracle output at 513 exact target values.
Ten explicit controls cover missing/insufficient subtraction, missing
clipping, a nonstrict oracle error bound, later nearest rerounding,
wrong-kernel substitution and four invalid input domains. All checks use
explicit exceptions and remain active with `-O`.

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-cross-rounding --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-cross-rounding
```

The registered command runs ordinary and optimized Python. A Git-free
export containing the declared inputs can run the direct verifier:

```sh
python3.12 -B research/gaussian-cross-rounding/verify.py
python3.12 -O -B research/gaussian-cross-rounding/verify.py
```

These checks support the written lemma; finite cases do not prove its
universal quantifiers. No complete selected replay, Schur solve, native
supplier replay, Lean proof, independent human review or new kappa is
claimed. Source binding is separate from mathematical verification.

## Sources, coordination and attribution

Scientific base: canonical main
`2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selected
`kappa=23/10000`. [SOURCES.json](SOURCES.json) binds the four live caller
notes and the original catalogue/selected provenance. No frozen file is
changed. #4442 is a motivating handoff; its unmerged Git objects are not
required for replay. The canonical investigation is
[Discussion #4444](https://github.com/CrocSwap/integer-mult-bounds/discussions/4444).

The initial overlap scan fetched complete pagination for 301 open PRs,
3,289 Discussion records and 3,787 closed PRs at 21:01-21:03 UTC on
2026-10-21. Targeted searches covered `four-ulp`, `across-cell` and
`downward exponential`, plus available top-level package notes. This does
not search every diff or nested file and is not a novelty certificate.
The card's baseline command was attempted but stopped on the initially
omitted selected package in the sparse checkout; no baseline PASS or full
selected replay is claimed.

Credit: James Reed (#4442 and the #4438/#4439 chain) for the exact handoff
and wrong-kernel witness; RaD/hipotures and the retained phase-cell
producer/reviewer for the two-ulp repair and structured reference;
Vlado Vojdanovski and PR1673's credited contributors for LOG-A/capped
Gaussian construction; Chafik Boukhalfa (#1758/#1786) for the fine-prime
and setup-precision lineage; Cinna Davis (#4100) for the retained all-size
notes; Ryanson Jonathan (#4402) for the column-gap lineage; David Harvey
and Joris van der Hoeven for the exponential contract. Mason Hale's
certified Gaussian recovery and Dugongue's Gaussian expansion headroom
already use directed interval/coefficients; this package does not claim
that method as new and imports neither implementation. Douglas Colkitt,
the retained OpenAI framework and all source-specific notices retain credit.

Prepared for **mihir-s-05** with substantial **OpenAI Codex assistance** in
mathematics, code, verification and writing. No subagents. New work is
Apache-2.0.

## Open next questions

Does one actual online coupling-page generator preserve domination or
correctly charge its separate rounding error? This matters because the
coarse nearest-grid control fails even when the reference is downward.
First pin that generator, its output precision and rounding mode, then
check the control and the source coupling perturbation budget. The missing
piece is an executed page generator and its consumer; this package stops
at construction of the stored reference coefficient.
