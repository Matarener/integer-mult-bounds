# The unique optimal origin for a finite Gaussian chirp

This contribution is produced by Nick Petalas. Apache-2.0.

For every finite banded Gaussian chirp in the family below, the unique
real origin minimizing the largest off-diagonal row sum is
`c*=(n-1)/2+beta/theta`. At the ten-vertex, width-2, p=19 section of
James Reed's [PR #4305](https://github.com/CrocSwap/integer-mult-bounds/pull/4305),
the changed origin `-1435/2` gives `||N-I||_infinity < 2^-38`.
The cited origin-zero section has the predecessor's bound `97/100`.
The actual norm strictly decreases by uniqueness of the minimizer.

Claim type: a scoped written analytic proof with exact finite corroboration.
No kappa, supplier admission or selected framework assumption changes.
The favorable norm requires a chirp diagonal range of `exp(81*pi)` in
the example, which has no paid implementation here.

## Model and new step

For integers `n>=2`, `1<=W<=n-1`, real `a,theta>0`, `beta` and origin `c`,
use diagonal 1 and, for `h=j-i`,

```text
N(c)[i,j] = exp(-a(1+theta)h^2 - 2a beta h
                + a theta((i-c)^2-(j-c)^2)),  0<|h|<=W.
```

All other entries are zero. This is Cinna Davis's PR #4100 Gaussian
chirp formula, the same family as James Reed's #4304/#4305 sections.
Their fixed-origin results are cited, not independently replayed.

[PROOF.md](PROOF.md) expands the exponent, reflects the finite path and
proves strict convexity of each row sum and their maximum. These facts
give the unique optimizer over every real origin. If
`delta=1-(n-3)theta>0`, it also proves
`||N(c*)-I||_infinity <= 2W exp(-a delta)`.
At `n=10,W=2,theta=1/1444,beta=-1/2,a=9*pi`, exact elementary
bounds give `a delta>28` and `exp(28)>2^40`.

Only the origin varies. This is not optimization over all positive
diagonal scalings. The matrices are diagonally similar and have the same
eigenvalues. Optimality does not imply contraction in every parameter regime.

## Evidence and reproduction

From the repository root, with standard-library CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/gaussian-origin-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/gaussian-origin-optimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gaussian-origin-optimum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gaussian-origin-optimum --check-source-history
```

Another installed CPython 3.12 can replace the local interpreter path.
The direct verifier also runs in a Git-free export and prints
`PASS_GAUSSIAN_ORIGIN_OPTIMUM`. `--emit` prints only its generated JSON
receipt, including hashes of all six package files. It writes no files.
There is no handwritten receipt or expected-output file.

The fixtures take `a=96 log(2)`, so every entry is an exact rational
power of two. They compare the literal squared-distance formula with
the expanded formula, check reflected rows and strict row midpoint
inequalities, and check strict improvement at two offsets from c*.
There are 216 parameter fixtures, 4,140 exponent fixtures, 2,790
reflected-row equalities and 3,222 strict inequalities.
The prime-scale certificate checks all 34 in-band entries using rational
exponent inequalities, Machin's arctangent bound and a positive Taylor sum.
Finite fixtures corroborate the written proof's universal quantifiers.

Fifteen controls cover invalid dimensions, bandwidths and theta values,
nonintegral and oversized fixture exponents, the wrong beta sign,
the wrong path midpoint, an omitted theta term, a valid noncontracting
regime and the degenerate theta-zero boundary. Explicit exceptions keep
checks active in optimized Python.

## Sources and limits

The scientific base is canonical main
`19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8.
[SOURCES.json](SOURCES.json) pins the original catalogue, selected record,
James Reed's retained PR #4305 README and Cinna Davis's gauge-free formula
as bibliographic provenance. No predecessor executable or numerical
receipt is consumed. The selected metadata baseline passed for orientation;
it is not a scientific replay.

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19220028)
states the changed origin-optimization scope. Entry searches included live
open PRs, recent account PRs, active Discussions and handoffs, targeted
merged searches and all-main README terms. They rejected the already-solved
origin-zero question before this claim. Sparse cached local-note coverage
is incomplete, and search absence is not proof of novelty.

No physical conversion, precision/tape invoice, source ownership, native
supplier, recursive Schur schedule, stock, compiler or analytic recovery
theorem is established. The five selected assumptions remain. Lean,
Docker, selected cold replay, independent human review and formal
proof-kernel review are unrun. No construction expansion is proposed.

Build the Lever supplies a standalone exact verifier. Prove It Works
requires full row sums of its rational fixtures. Power of Ten bounds
fixtures by ten vertices, bandwidth three, rational exponents of magnitude
at most 4096, and six files of at most 128 KiB. Functions stay below
60 physical lines. Warning-strict normal and optimized Python provide
recurring diagnostics. Managed allocation is a bounded rule-3 deviation
because Python integers and Fractions allocate dynamically. There is no
recursion, subprocess, network access or dynamic code generation.
The rejection helper's ten callbacks are fixed local controls, a bounded
rule-9 deviation; no external callback is accepted.

## Open next questions

What origin is best under an explicit logarithmic range budget on the
chirp diagonal? This matters because the unconstrained example needs
range `exp(81*pi)`. First intersect the origins with a specified range
allowance and minimize the convex row-norm objective there. A real caller
must supply the scaling and precision budget. The structured question is
in [TASK.json](TASK.json) and is not reserved here.

## Credit

The new origin-optimization proof and verifier were produced by Nick Petalas.
James Reed / jwr404 supplied the origin question and fixed-origin sections
in #4304/#4305. Cinna Davis supplied the PR #4100 Gaussian and gauge-free
formulas. Their attribution and frozen files remain intact. Convexity,
path reflection, Machin's identity and Taylor bounds are classical methods.
Independent human and formal proof-kernel review are unclaimed.
