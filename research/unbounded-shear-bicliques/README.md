# Unbounded bipartite rank metrics in four-dimensional rational shears

This construction and scoped proof were produced by Nick Petalas.

For every n, the following two families realize the distance metric of
K_(n,n) inside commuting 4-by-4 integral shear operators:

```text
E(t) = [[t,t^2],[1,t]],  O(a) = [[a,a^2],[0,-a]],  0 <= t,a < n,
Phi(M) = [[I_2,M],[0,I_2]],  d(Phi(M),Phi(N)) = rank_Q(N-M).
```

Every cross distance is one; every distinct same-part distance is two.
The [proof](PROOF.md) gives a literal rank-one factorization and the two
within-part determinants. Matrix dimension stays four. Entries have
magnitude at most max(1,(n-1)^2).

Jerry Chen / CubeJerry's [PR907](https://github.com/CrocSwap/integer-mult-bounds/pull/907)
supplies an eight-frame rational shear example and proves the abstract
formula c_1(K_(n,n))=2(n-1)/n. The new step realizes every size by actual
rational shear frames. Thus their distortion approaches two in fixed
matrix dimension; the countably infinite family has distortion exactly
two. The predecessor's abstract distortion proof is cited, not rechecked.

Claim type: scoped written construction proof with exact finite
corroboration. There is no new kappa or supplier. This is a changed frame
alphabet side result under `coverage-law-change`; it does not meet that
card's complete paid/productive invoice gate. The selected baseline
orientation passed, but the selected scientific replay was not run.

## Evidence and reproduction

Run from the repository root with the recorded CPython 3.12 interpreter:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/unbounded-shear-bicliques/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/unbounded-shear-bicliques/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/unbounded-shear-bicliques
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/unbounded-shear-bicliques --check-source-history
```

Another absolute CPython 3.12 path may replace the recorded path. The direct
commands print `PASS_UNBOUNDED_SHEAR_BICLIQUES` in a generated JSON receipt
bound to all six package files. No receipt is handwritten.

The checker compares determinant-based ranks with independent rational
elimination for every ordered label and 4-by-4 operator pair in thirteen
balanced fixtures, n=2 through 12, 16 and 32, and one 9-by-11 rational
fixture with negative, zero and fractional parameters. There are 8,116
ordered pairs, 301 explicit factorization/determinant checks, 400 ordered
group-product checks, and ten rejection controls. Controls catch a wrong
square entry, omitted unit, wrong diagonal sign, duplicate parameters and
invalid finite-fixture inputs. Normal and optimized commands preserve
every check. The n=32 realization has distortion 31/16 by PR907.

## Limits and credit

This is a rank-metric construction. It supplies no nonlinear circuit,
native physical implementation, complete bill, dirty-input protocol or
recursive gain. The infinite result uses the cited all-n distortion
theorem. The universal construction uses the written determinant proof.
Finite tests alone prove neither universal statement. Independent human
and formal proof-kernel review are unclaimed. No Lean, Docker, full native,
selected-supplier or complete multiplier replay is part of this package.

PR907 retains its metric/cut theorem and concrete eight-frame credit.
eumemic's PR288 supplies the rational shear framework, navinor's PR825 the
separate common-flag obstruction, and Jeremy Diviney's PR836 the separate
signed-potential restrictions. Their results are neither audited nor
overridden here. No predecessor code is copied. The new contribution is
the unbounded explicit realization and its consequence for this fixed
matrix dimension. Elementary rank and block-matrix identities are standard;
no literature-priority claim is made. Apache-2.0.

## Open next questions

1. Can this contact geometry be used in a changed interface that satisfies
   every endpoint and has a favorable complete signed bill? First specify
   the legal gates, demanded output and paid cleanup. The known common-flag
   obstruction must be addressed before searching within its closed model.
2. What coefficient-height growth is necessary for such integral bicliques
   at fixed matrix dimension? First compare this quadratic-height
   construction with rank-one contact equations under a bounded-entry
   constraint. This question concerns representation size, not an assumed
   physical saving.

## Verifier engineering bounds

The verifier is a standalone standard-library program. All loops range
over fixed fixtures or matrices of order at most four; finite fixture
construction rejects more than 64 parameters per part. It has no
recursion, external dispatch or writes. Runtime checks stay active under
optimization. Each function is shorter than sixty lines.

Power-of-Ten rule 3 deviation: CPython and Fraction allocate during
arithmetic. Live matrices have at most sixteen rational entries and each
fixture has at most 64 labels in this replay. The checker runs one pair at
a time, so it retains no quadratic matrix collection. Rules 8 and 9 use
ordinary Python entry-point dispatch and bounded negative-control lambdas;
the callable targets are literal functions in this file. Warning-strict
normal and optimized replay, syntax inspection and publication checks
provide the available diagnostics. No separate static analyzer is required
or claimed.
