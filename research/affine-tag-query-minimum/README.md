# Sharp affine native tag membership with 46 queries on nine axes

This scoped proof and executable certificate were produced by Nick Petalas.
For a known binary affine permutation on n axes and a phase promised to be
quadratic over Z/4 with even mixed coefficients, deciding membership in the
normalized affine tag family requires exactly

```text
d(n) = 1 + n + binom(n,2) = 1 + n(n+1)/2
```

exact phase evaluations in the worst case. The lower bound covers every
deterministic adaptive decision algorithm, even though the constant phase
and even-linear tag are free unknowns. A matching test queries zero, the
unit vectors, and the pair sums. On nine axes it uses 46 evaluations; the
cube contains 512 addresses. This is an optimal oracle query count, not a
measured speedup, physical saving, new supplier or new kappa.

[PROOF.md](PROOF.md) states the complete oracle contract and proves both
bounds. The reusable `certify` function in [verify.py](verify.py) returns the
unique constant and mask, or raises `ValueError` on a nonmember. `adversary`
constructs an invalid residual agreeing with zero on any insufficient query
set. The implementation supports 1 through 64 axes; the written theorem
covers every positive dimension.

## Why this boundary matters

JoyboyBrian's [PR6106](https://github.com/CrocSwap/integer-mult-bounds/pull/6106)
extends normalized native tags to affine maps and notes that coordinate
evaluations alone do not establish that a general quadratic residual is
linear. This package supplies a complete test for that question and proves
its sharp black-box cost. It does not replay the predecessor's warp, inverse,
512-column census, or calibration results.

The reduction subtracts the known phase `wt(Ax+b)-wt(x)`. The remaining
polynomial must have even linear coefficients and zero mixed coefficients.
For a shorter test, an affinely deficient query set misses an odd-parity
residual. A full-span query set with fewer than d(n) points misses twice a
nonzero quadratic polynomial. These explicit impostors prove the adaptive
lower bound by following the accepted oracle's transcript.

## Evidence and reproduction

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -B research/affine-tag-query-minimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -I -O -B research/affine-tag-query-minimum/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/affine-tag-query-minimum
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/affine-tag-query-minimum --check-source-history
```

Any CPython 3.12 path can replace the local interpreter path. The verifier
prints `PASS_AFFINE_TAG_QUERY_MINIMUM` in a generated JSON receipt bound to
all six package files. It writes no files and imports no predecessor code.

The complete finite checks enumerate 2,192 promised phases through three
axes and compare membership with literal cube values and every possible
tag. They also enumerate all 58,916 insufficient distinct query subsets
through four axes, construct an impostor for each, and check both its zero
transcript and its nonmembership by literal values. Thirty-six affine
constructions cover dimensions 1,2,3,4,5,9,16,32,64, with full cube comparisons
through five axes and exact queried-address comparisons thereafter.
Fourteen malformed-input/nonmember controls reject; a separate cubic control
shows why the polynomial promise is necessary. These finite checks support
the written proof and do not replace it.

## Scope and engineering limits

The known affine permutation, exact phase oracle and structural quadratic
promise are hypotheses. For an arbitrary function, an unqueried cubic can
pass this test. The lower bound does not apply when coefficients may be read
directly, or to bounded-error randomized or quantum queries. A serialized
native circuit still needs a proof that its action has the promised form.
No complete tensor identity, physical caller, dirty restoration, precision,
tape bound, supplier invoice or multiplication theorem is certified here.
No selected cold replay, Lean, Docker, independent human review or formal
proof-kernel acceptance is claimed.

All executable loops have finite bounds. Public membership queries validate
1 <= n <= 64 and affine invertibility before calling the oracle, and use at
most 2,081 calls. Binary elimination uses at most 2,081 rows and columns;
literal enumeration is restricted to at most four axes. Managed Python
allocation and the standard frozen dataclass are documented departures from
static-allocation and no-generation rules. Their retained data sizes are
bounded by these limits; the oracle's internal time and memory are outside
the query contract. Functions stay below 60 physical lines, use explicit
checks under optimized execution, and propagate failures. Warning-strict
normal and optimized runs are the registered diagnostics.

## Sources and overlap

The exact affine convention is credited to
[PR6106 head 9d0126c](https://github.com/CrocSwap/integer-mult-bounds/blob/9d0126c134720258cfe685b661ce288da01008fa/research/native-affine-phase-tags/README.md).
It is explanatory provenance, not an executable input or an unmerged source
dependency. The proof defines the entire problem locally.
ToikY's [PR4002](https://github.com/CrocSwap/integer-mult-bounds/pull/4002)
supplies normalized linear lifts and retains Chris R / Clear1nsight's
PR3987, Dugongue PR3945/3929, dataisfire PR3734, Cinna Davis PR2226 and the
native/compiler lineage. Ali Romman's
[PR5369](https://github.com/CrocSwap/integer-mult-bounds/pull/5369)
decides fixed group-algebra identities across tensor widths; that different
problem is not reduced to this membership test. Classical interpolation
and binary linear algebra are not claimed as new methods.

Before the advance claim, current main and merged PRs were searched for
quadratic membership, affine phase tags, phase probes and interpolation,
including general-dimension forms. The cached overlap snapshot covered 407
open PRs and 5,816 Discussion records with complete remote pagination; its
sparse local notes omitted 8,272 paths, so main was searched directly too.
These are bounded overlap checks, not a proof of global novelty. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19246894)
records the changed card scope. The selected frontier is unchanged.

## Open next questions

- Bind this test to one serializer whose quadratic phase and affine
  permutation are structurally authenticated. First expose its exact phase
  oracle and polynomial induction, then price its complete caller. Arbitrary
  circuit membership and physical delivery are still missing.
- Determine the optimal bounded-error randomized query cost for this same
  promise problem. First specify error probability and one-sided versus
  two-sided rejection. The deterministic transcript lower bound does not
  settle that problem.

Apache-2.0. The scoped proof, checker and adversary were produced by Nick Petalas.
