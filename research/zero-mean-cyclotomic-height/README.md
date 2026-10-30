# A smaller averaged cyclotomic-height exponent

This scoped written proof was produced by Nick Petalas. For every prime-power
radix r>=3, put n=r-1, D=phi(r) and ell=ceil(log2 r). The coefficient heights
of Chafik Boukhalfa's PR #1025 obey

    sum_(k unit mod r) log H_k <= D [2(log r)^2+3 log r].

The predecessor's bound is D[4(log r)^2+8 log r+2]. The new step sets the
unused zero-residue value of log|1-zeta^s| to -log r. Its normalized Fourier
transform has mean zero, every other coefficient is negative, and its exact
absolute mass is log r. [PROOF.md](PROOF.md) derives the identity and substitution.

The cited nonzero-resultant/cofactor argument then gives, uniformly in the
primitive embedding and |z|=1,

    |P_k(z)| >= 2^-d,
    d=1+2ell+n D min(r,3ell^2).

The predecessor uses 8ell^2. At r=4096 the sufficient gap exponent decreases
from 9,661,317,145 to 3,622,993,945. These are analytic upper bounds on a
sufficient exponent. No inverse at that precision was executed. No new kappa,
physical supplier or selected-frontier change is claimed.

## Reproduce

From the repository root, using the local CPython 3.12 interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/zero-mean-cyclotomic-height
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/zero-mean-cyclotomic-height/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/zero-mean-cyclotomic-height --check-source-history
```

Other machines may substitute their CPython 3.12 path. Only the standard
library is required. The standalone verifier also works in a Git-free export
of these six files. It writes no files; stdout is a generated receipt bound
to all six package-file hashes. Registered replay runs warning-strict normal
and optimized modes. Explicit runtime checks remain active under optimization.

The exact checks cover all kernel identities at r=2..96, harmonic telescoping
at r=2..40 with two truncations, formal logarithmic DFTs at r=3,4,6, and
integer prime-power/dyadic budgets. Controls reject altered kernels, a false
zero mean and out-of-domain inputs. The proof supplies the universal result;
finite arithmetic is corroboration, not a proof-kernel certificate.

## Credit, overlap and limits

Credit Chafik Boukhalfa / [#1025](https://github.com/CrocSwap/integer-mult-bounds/pull/1025)
for averaged heights, the primitive-unit estimate and precision framework;
Ali Romman / [#621](https://github.com/CrocSwap/integer-mult-bounds/pull/621)
for the nonzero resultant and cofactor argument; Rohan Guliani / #846 and
Charles Bethin / #764 for the retained solver and suffix lineage. Classical
ingredients are the logarithm series, finite Fourier orthogonality and
cyclotomic product. No historical priority is claimed for those tools.

Hanson Sun / #1428 extends the earlier estimate to a different composite-radix
domain. That extension is not pursued here. Nick Petalas / #5080 improves an
independent inverse-envelope factor with a given circle gap; it does not prove
this averaged-height estimate, and its follow-ups are not this target.
Live PR bodies, the handoff discussion and merged/main searches were checked.
Sparse local overlap coverage and unpublished work remain limits.

No predecessor verifier is imported or replayed. Its analytic implications
are cited premises, with exact proof/notice provenance in SOURCES.json.
Actual reduced-precision inverse execution, preparation, common-label compiler,
dirty restoration, physical tapes/hosting, full transform and multiplication
obligations remain. No selected cold replay, native suite or Lean build was run.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.

## Open next questions

Structured first steps and blockers are in [TASK.json](TASK.json).

- Can another value at residue zero improve the complete interval bound,
  including the resulting nonzero mean? Begin with its exact piecewise-linear
  Fourier mass. Minimizing mass alone does not price the mean term.
- Can the new height estimate be used in an actual reduced-precision inverse
  execution with all preparation and rounding errors retained? Begin with one
  fixed small prime-power instance of the cited arbitrary-stride solver.

## Verifier constraints

Functions are below 60 lines and loops have explicit fixed bounds. The only
indirect calls are rejection controls with five locally named possible targets.
There is no recursion, subprocess, network, dynamic code execution or output
file creation. All mathematical comparisons use integers or Fraction.

Power-of-ten rule 3 deviation: CPython allocates managed integers, Fractions
and containers during checking. This six-file, one-shot verifier uses fixed
domains, arrays of at most 97 coefficients, at most 1,280 harmonic terms and
48 atanh terms. File reads are bounded by one MiB per file. No unbounded input
is accepted. Inspection and the normal/optimized commands exercise these bounds.
An embedded fixed-allocation implementation would require a separate runtime.
Rule 9 deviation: the rejection helper calls only the five named local contract
functions; every call has a fixed finite fixture and propagates unexpected
exceptions. The eleven controls exercise the allowed targets. Python has no
compiler warning mode; both registered checks use -W error and explicit guards.
