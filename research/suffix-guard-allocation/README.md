# Optimal unequal guards for the THREE-base logical error ledger

This contribution was produced by Nick Petalas. Apache-2.0.

Claim type: finite certificate and scoped integer-optimality proof. There is
no new kappa or selected-frontier change.

David Ganz / Dugongue's [PR #4510](https://github.com/CrocSwap/integer-mult-bounds/pull/4510)
supplies a complete suffix-error ledger for the historical THREE-base native
word rewritten in #4505. Its logical perturbation theorem permits unequal
ADD and SCALE defect tolerances. This package chooses those tolerances to
minimize a stated precision charge. The ledger and perturbation theorem are
cited premises, not new derivations or re-verification deliverables. This is
not the selected #6030 word.

## Result and contract

Fix a target logical output-error allowance `2^-b`, with integer `b >= 0`.
Inputs are exact. Every entire-field ADD defect has norm at most
`2^(-b-g_A)` and every entire-field SCALE defect at most `2^(-b-g_S)`.
All other event classes are exact, and logical free warp operators are
isometries, exactly as in #4510's ADD/SCALE corollary. The guards `g_A,g_S`
are nonnegative integers. They describe absolute logical defect tolerances,
not physical mantissa widths or componentwise rounding quanta.

For each published output row `i`, write its ADD/SCALE weights as `a_i,s_i`.
The sufficient constraints are

```text
a_i / 2^g_A + s_i / 2^g_S <= 1, for every output i.
```

Define the event-weighted guard charge

```text
J = N_ADD * g_A + N_SCALE * g_S.
```

This is a declared logical precision objective. It is not peak storage, a
physical instruction bill, or measured runtime. A common base precision `b`
would add the same `(N_ADD+N_SCALE)*b` to every allocation.

| Orientation | ADD/SCALE events | Least uniform guards | Unique optimal guards | Uniform J | Optimal J | Saved |
|---|---|---|---|---:|---:|---:|
| Forward | 16,263 / 1,168 | 11 / 11 | 11 / 9 | 191,741 | 189,405 | 2,336 |
| Backward | 16,271 / 1,168 | 13 / 13 | 13 / 11 | 226,707 | 224,371 | 2,336 |

At the optimal assignments, the maximum sufficient output bound, divided by
`2^-b`, is `7257/8192` forward, attained at `L222`, and `827/1024` backward,
attained at `L328`. Every one of the 632 output constraints is checked in
each orientation. Both SCALE tolerances are four times their uniform values.
No smaller event-weighted charge satisfies this particular ledger.

## Optimality proof

Nonnegative weights make every constraint monotone in each guard. Forward,
`max a_i = 2355/2 > 2^10`, so every feasible allocation has `g_A >= 11`,
regardless of the SCALE guard. An allocation with `g_A >= 12` costs at least
`12*16263 = 195156 > 189405`, even with zero SCALE guard. Consequently any
allocation competitive with the displayed candidate must have `g_A = 11`.
At that guard, `g_S = 8` violates a published row, while `g_S = 9` satisfies
every row. Positivity of the SCALE event count makes the optimum unique.

Backward, `max a_i = 4300 > 2^12` forces `g_A >= 13`. Taking `g_A >= 14`
costs at least `14*16271 = 227794 > 224371`. At `g_A = 13`, `g_S = 10`
violates a row, whereas `g_S = 11` satisfies every row. This proves the
second unique optimum. The rejecting maxima are `20155/16384` forward and
`2233/2048` backward. The generated receipt retains these exact values. Uniform
optimality is checked by the same monotonicity argument.

The verifier separately enumerates every integer pair whose charge is at
most the uniform benchmark. That search clears row denominators and uses
integer inequalities, rather than the Fraction-based monotonicity certificate.
It confirms both optima without dropping or grouping output rows.

## Reproduction

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/suffix-guard-allocation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/suffix-guard-allocation/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/suffix-guard-allocation
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/suffix-guard-allocation --check-source-history
```

Any CPython 3.12 executable can replace the displayed local path. Expected
markers are `PASS_SUFFIX_GUARD_ALLOCATION`, `PASS_REGISTERED_RESEARCH_PACKAGE`
and `PASS_RESEARCH_COMMIT_BYTES`. The direct command prints a generated JSON
receipt bound to the input and every package file. It writes no output files.

The source ledger is pinned to base
`721c03822c421b7f7fcbb2598993b947c4d88419` in SOURCES.json. In a sparse
checkout, materialize `research/native-suffix-errors` before running. The
verifier reads that JSON but imports or executes no predecessor code.

Fifteen rejection controls cover insufficient ADD/SCALE guards, a needlessly
large ADD guard that cannot satisfy the optimality certificate, malformed
guards and corrupted input bytes. They remain active under optimization.
The code has no recursion, subprocesses or writes. Every function is below
60 lines; input bytes, rows, event counts and enumeration ranges are bounded.
Python allocates during exact arithmetic, a managed-runtime deviation from
fixed-capacity allocation; the authenticated one-MiB input and finite ranges
bound this artifact's live objects. No general-purpose optimizer is claimed.
Warning-strict compilation and the registered normal/optimized checks supply diagnostics; Ruff and Pyright were
unavailable. If this fixed artifact becomes a reusable allocation API, add
typed boundary validation and a configured static checker. The rejection helper
uses bounded indirect dispatch to only three local validators, with no external
callback registration; a reusable API should keep those targets explicit.

## Limitations

Optimality concerns the sufficient inequalities in the published ledger,
not the smallest true error of the native word. Physical norm conversion,
all non-ADD/SCALE defects, recursive feedback, rounding-grid ownership,
restoration, peak memory and a complete paid caller remain open. The allocation
must not be transferred to another word or to #6030 without new source-bound
weights. No selected framework assumption is discharged. Independent human
and formal proof-kernel review are unclaimed.

The predecessor's scientific replay, the selected cold replay, Lean and
Docker were not run. Source integrity is checked; the underlying source
ledger's mathematical correctness is assumed.

## Open next questions

Can one physical implementation supply these unequal entire-field defect
contracts with a smaller complete arithmetic bill? Start with a literal ADD
and SCALE implementation, translate their componentwise errors into the
ledger norm, then price width conversion, routing and restoration. Those
physical contracts are the blocker. Optimizing this logical charge alone
does not establish the saving in a multiplier.

## Credit

David Ganz / Dugongue supplied #4510's logical perturbation theorem, complete
row ledger and unequal-budget interface, and #4505's rewritten native word.
Its #4502 borrowed adapters, #4499 gauges, #4494/#4489 source selectors and
the retained zxv, Jacob Alan Sussman, Cinna Davis and Jeremy Kothe lineage
retain their credit. Reverse sensitivity and impulse-response bounds are
classical. The new result is the explicit nonuniform allocation, its declared
objective and its exact optimum certificate. No predecessor credit line or
source file is changed.
