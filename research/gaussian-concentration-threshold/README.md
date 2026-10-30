# A sharp Gaussian concentration threshold

Scoped proof with exact finite controls. This contribution was produced by
Nick Petalas. Apache-2.0. No new kappa is claimed.

For the nearest-grid Gaussian matrix with expansion ratio \(1+1/s\), even
\(s\), and any retained bandwidth \(2\le w<s/2\), let \(A_{s,w}\) be the
continuous concentration at which the largest off-diagonal row sum equals
one. [PROOF.md](PROOF.md) establishes

\[
A_{s,w}=\frac{\log s-\log\log s+\log2}{2}+o(1),
\]

uniformly in the bandwidth. Every row is strictly dominant exactly above
that threshold. The result determines both the log-log correction and the
additive constant. Integer concentration \(u\), with \(a=\pi u\), has the
corresponding bounded rounding uncertainty.

The new proof sharpens the farther-tail estimate to obtain

\[
R_i(a)\le e^{-2a\theta}+2e^{-2a}
                    +\frac{2e^{-6a}}{1-e^{-6a}},\qquad a\ge1.
\]

Three literal entries at the half-tie row give the matching obstruction.
At \(a=k\log2\) and \(s=2^{20}\), the exact controls certify failure for
\(k=8\) and dominance for \(k=9\). A separate \(s=2^{19},k=8\) control
shows that deleting one of the two leading tail contributions falsely
certifies dominance. These finite examples are supporting certificates;
the asymptotic statement follows from the written proof.

## Reproduction and evidence

From the repository root, using CPython 3.12 and only its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/gaussian-concentration-threshold
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/gaussian-concentration-threshold --check-source-history --check-modes
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -B research/gaussian-concentration-threshold/verify.py
```

Use another CPython 3.12 executable on other machines. The registered commands
run both normal and optimized modes. Each prints
`PASS_GAUSSIAN_CONCENTRATION_THRESHOLD` and a generated report bound to the
package and live-source SHA256 hashes. No receipt is handwritten.

The finite checks enumerate 522 geometry equalities, 336 complete band rows
and their 4,368 retained off-diagonal entries. They also classify all 231
declared dyadic concentration/period pairs through \(s=2^{24}\), with 136
certified dominant and 95 certified nondominant cases, none unresolved.
Four malformed arithmetic-domain cases are rejected. All interval endpoints
are integers on a 192-bit dyadic grid, using outward integer multiplication,
integer square roots and bounded exponentiation. No floating point,
transcendental implementation or predecessor verifier is used.

The retained sources have exact main-commit, Git-blob and SHA256 pins in
[SOURCES.json](SOURCES.json). Their mathematical conventions are inputs;
their prior scientific results are cited rather than re-audited. The source
checker authenticates both live files before the new finite calculations.

## Scope and relation to existing work

The [original question](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19241969)
changes concentration outside the unchanged production guard. It asks for
a matching obstruction and sufficient condition at that changed guard.

Jose Manuel's [PR3851](https://github.com/CrocSwap/integer-mult-bounds/pull/3851)
supplies the physical matrix convention. The retained PR1673 phase-cell
audit by Vlado Vojdanovski, with its RaD/hipotures predecessors, supplies
the nearest-neighbor majorant. Its farther-tail estimate has coefficient
five; the new estimate and half-tie obstruction determine the threshold.
Gaussian convexity and geometric-series arguments are standard.

[PR6099](https://github.com/CrocSwap/integer-mult-bounds/pull/6099) concerns
coefficient perturbation and leaves production row dominance open.
[PR6126](https://github.com/CrocSwap/integer-mult-bounds/pull/6126) improves
the inverse bound under unchanged production guards. Neither is a theorem
dependency here. The present result varies the guard and supplies a matching
failure family, rather than computing that production inverse bound.

No complete physical caller at reduced concentration is supplied. The theorem
does not bound numerical coefficient errors, infinite periodization error,
LU growth, physical preparation, tensor assembly or the full recursive bill.
No selected cold replay, proof kernel or independent human review ran.
The selected frontier and all five inherited assumptions remain unchanged.
There is no sign claim at the exact critical asymptotic offset.

## Open next questions

1. Can a reduced-concentration physical caller pay its coefficient errors and
   retain a sufficient inverse allowance? This could reduce normalization
   charges. Start with the explicit sufficient bound above at one complete
   production parameter tuple; physical geometry and the full error/cost
   invoice remain blockers.
2. What is the first vanishing correction to the continuous threshold? Start
   with the same three half-tie entries and a sharper uniform remainder.
   Identifying an exact maximizing row is the remaining obstacle. This is
   separate from the proved additive \(\log2/2\) constant.

## Verifier bounds

The verifier has fixed finite fixture sets, at most 24 root or exponent-bit
iterations per arithmetic call, and at most 256 indices in a geometry loop.
Its matrix fixtures have at most 32 rows. It uses no recursion or indirect
code execution. Python allocates managed integers and dictionaries during
execution, a documented deviation from static allocation; their sizes are
bounded by these fixtures and the fixed grid. Runtime contracts remain
enabled under optimization. The universal mathematical claim rests on the
proof, not on expanding those finite bounds.
