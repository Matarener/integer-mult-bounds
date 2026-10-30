# Bitset elimination for exact quadratic Gauss sums

This contribution was produced by Nick Petalas. It supplies a bounded exact
implementation with a scoped equivalence proof and empirical performance
evidence. There is no new kappa or selected-frontier change.

On one complete 64-axis, four-source Clifford projection calculation,
adjacency-bitset elimination reduces median command time by **40.6%**,
from **0.445 s to 0.265 s**. Five alternating fresh-process pairs return
identical complete output with zero errors. Times include source checks,
circuit generation, Choi construction, the full phase-sensitive kernel,
the exact normal-equation solve and output. This is a deterministic
computational fixture, not a measured production search or physical caller.

The old polynomial-substitution Gauss sum is replaced by bounded updates
of Z/4 diagonal coefficients and adjacency bitsets. The other contraction
and solve code is unchanged. [PROOF.md](PROOF.md) gives the elimination
identities and the exact admitted domain, at most 256 variables.

## Evidence and reproduction

The local host used CPython 3.12.15 on macOS arm64, with 18 logical cores
and a shared load. [BENCHMARK.json](BENCHMARK.json) contains all raw samples,
source hashes, work counters and output digests. Baseline times range from
0.4353 to 0.5052 seconds; bitset times range from 0.2641 to 0.3204 seconds.
Separate profiles identify the old Gauss elimination and the remaining
Choi construction as the limiting work. [VALIDATION.md](VALIDATION.md)
records those profiles, the inconclusive small-width replay result and
the correctness checks.

From the repository root, using the provided interpreter:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/bitset-gauss-elimination/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/bitset-gauss-elimination
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/bitset-gauss-elimination --check-source-history
```

The direct checker prints `PASS_BITSET_GAUSS_ELIMINATION` and a generated
receipt bound to package file hashes. A portable CPython 3.12 interpreter
may replace the local path. The standard library suffices.

To repeat the performance measurement, choose a new path outside the checkout:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/bitset-gauss-elimination/benchmark.py --workload projection --output /absolute/scratch/benchmark.json
```

`--workload replay` measures the entire inherited inventory replay instead.
Its overall gain was inconclusive locally. No speed claim is made for it.
The full differential replay remains a conformance check, not this
contribution's scientific deliverable.

## Scope and credit

Ali Romman's [PR5727](https://github.com/CrocSwap/integer-mult-bounds/pull/5727)
supplies the phase-sensitive contraction engine, exact finite-span solver,
complete replay and input set. PR5704's compact states, PR5526's tensor
theorem, PR5698's native recipe set and every retained notice keep their
credit. Quadratic Gauss-sum elimination and Boolean parity expansion are
classical. This package claims the new implementation, its bounded proof
binding and measured fixture improvement, not a new general Gauss-sum method.

All predecessor files are unchanged. The original consumer is authenticated
through [PINS.json](PINS.json) and declared as replay inputs. No wrapper is
installed into the selected replay. Native realization, dirty restoration,
physical time, rounding, compiler and outer obligations are not discharged.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.

## Open next questions

1. Can Choi construction's remaining affine substitutions be reduced while
   preserving exact state output? Start with the optimized projection profile
   and one substitution. No replacement or equivalence proof is supplied.
2. Does a named wider native-interface search benefit on another host? Bind
   its complete input, states, solve and output before timing five alternating
   pairs. Production-consumer and cross-platform evidence are absent here.
