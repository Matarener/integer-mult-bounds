# Dense port mixing does not reduce scalar thin-query information

Claim type: scoped mathematical proof with exact finite corroboration. No new
kappa or selected-frontier change.

The [proof](PROOF.md) extends a port-local information deficit to arbitrary
linear queries mixing independent ports, with adaptive query selection and
arbitrary deterministic decoding. If each port needs fifteen dimensions beyond
its free information, P ports need total returned scalar capacity at least 15P.
Touching many ports with one scalar response does not increase its capacity.

This builds on Matarener's [PR #5996](https://github.com/CrocSwap/integer-mult-bounds/pull/5996),
exact head `47242572d3b22ce49371245edc561dd75bf263e8`, and its question about
cross-port channels. The reported per-port deficit is cited as a premise. This
package does not replay or validate it. The linear information principle is
classical; the new contribution is the cross-port observation contract and its
conditional thin-pool capacity constraints. The repository's
[outside-input rank probe](../outside-input-research-targets/README.md) already
states the fixed-observation quotient formula. Matarener's
[nonlinear centre floor](../centre-nonlinear-fresh-floor/README.md) covers a
different history and continuous or semialgebraic fresh encoders. Neither is
replayed here, and neither source's general dimension principle is claimed new.

For 528 requests on 104 independent ports, scalar capacity two is insufficient;
with capacity at most three, at least 504 requests need capacity three. For 112
ports, capacity three is insufficient; with capacity at most four, at least 96
requests need capacity four. Keeping every request scalar instead requires at
least 1032 or 1152 additional free dimensions respectively.

These are necessary information budgets, not physical schedules. Scalar output
capacity is explicitly different from native frame rank. Binding the actual
multi-port data and its free operations to this contract remains an obligation.
An entire independently readable output vector is charged by its coordinates.

## Reproduce

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/cross-port-thin-capacity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/cross-port-thin-capacity/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/cross-port-thin-capacity
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/cross-port-thin-capacity --check-source-history
```

The standalone verifier needs no Git, network or predecessor source. It
enumerates all triples of binary free/query/target subspaces in dimensions zero
through four. Through dimension three, a separate literal input-fiber oracle
checks whether any lookup-table decoder exists. Rational recoding and
side-information fixtures, adaptive decision trees, packet arithmetic, and
semantic/boundary controls corroborate the written proof. The universal theorem
rests on that proof, not these finite examples. `--receipt PATH` writes a new
receipt bound to package file hashes outside the package.

The run enumerates 304,993 subspace triples and makes 4,230 independent fiber
comparisons. It also checks 116 rational fixtures, 510 complete adaptive
transcripts, 255 ambiguous shortened transcripts, four semantic controls and
four invalid-input rejections. Normal and optimized commands each completed
locally in under one second; these are replay-budget observations, not speedups.

## Verifier bounds

No recursive code, solver, subprocess, network access or hidden input is used.
The largest subspace census has 67 spaces, 4489 pair joins and 67 cubed triples.
Binary vectors have at most eight bits, spans at most 256 elements, and rational
matrices at most 32 rows by 16 columns. Adaptive trees enumerate at most 256
inputs per dimension. Every function is below sixty lines. Invariants use
explicit exceptions and stay enabled under optimization. The four indirect
control calls have a fixed, visible target list. Source hashing reads six files
of at most one MiB each. The optional receipt is created exclusively.

Power-of-Ten rule 3 deviation: Python's managed objects and Fraction arithmetic
allocate during verification, so fixed allocation after initialization is not
claimed. The finite dimensions above bound live collections and integer sizes;
there is no unbounded input arithmetic. The compensation is checked by the
boundary controls and both registered executions. A larger-input verifier must
declare new bounds before extending these constants. Rule 10 uses warning-strict
normal and optimized replay; no separate Python static analyzer is configured
for this isolated package.

## Open next questions

- Can a physical thin query deliver enough independently readable coordinates
  to meet the capacity distribution above at a favorable complete cost? First
  specify its input/output maps and native frame tariff. Physical realization,
  dirty restoration and causal availability are unproved.
- Do the actual port data and every allowed free operation admit the independent
  direct-sum observation model? First give the input-coordinate and free-span
  maps. This package does not establish that application premise.
- Can a changed producer supply the required new free information more cheaply
  than the omitted scalar requests? First price one new independent observable,
  including its later consumption and restoration. No such producer is supplied.

The proof and verifier were produced by Nick Petalas. Credit Matarener for the
per-port deficit and question, Cinna Davis for the controllers, Ali Romman for
the direct-controller construction, Dugongue for the target atlas, and the
predecessor lineage retained in PR #5996. Independent human and formal
proof-kernel review are unclaimed. Apache-2.0.
