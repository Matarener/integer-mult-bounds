# Sharp table travel for skew-radix cached chirps

Choosing a largest radix as the fastest axis gives table-head movement
`Q <= 7TP` for the complete cached chirp enumeration, including initialization
and the final return to cell zero. Here `T` is the number of tensor records
and each table entry has `P` cells. There is no largest/smallest radix-ratio
restriction. The constant seven is sharp for this specified schedule: with
`d` binary axes, `Q/P = 7*2^d - 10`.

On the two-axis layout `(2,512)`, the exact closed table walk costs
`264708P`. Putting the 512-axis first costs `3078P`, with the same 1024
records. This is a count of unit head moves, not a timing measurement.

Claim type: scoped written mathematical proof with exact finite
corroboration. [PROOF.md](PROOF.md) gives the exact movement identity,
its all-size bound, sharpness family and physical boundary. No new kappa
or selected-frontier change is claimed.

## Reproduction

From the repository root, CPython 3.12 and the standard library suffice:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/chirp-radix-order/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/chirp-radix-order
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/chirp-radix-order --check-source-history
```

The standalone verifier prints `PASS_CHIRP_RADIX_ORDER` with exact counts
and SHA256 hashes of all six package files. It compares a literal complete
table walker with a separately implemented closed formula, checks the sharp
binary family through 64 axes, and executes exact quadratic-phase caches
against direct values at every original named coordinate in five fixtures.
The registered replay runs both normal and optimized warning-strict checks.
No predecessor executable or numerical certificate is replayed.

## Scope and credit

This contribution was produced by Nick Petalas. Apache-2.0.

Ryanson Jonathan, `pinterbanget`, supplies the sequential table layout and
suffix-product cache model in [PR #4325](https://github.com/CrocSwap/integer-mult-bounds/pull/4325),
retained as [pr4100-chirp-odometer-tariff](../pr4100-chirp-odometer-tariff/README.md).
Cinna Davis supplies the underlying chirp construction in PR #4100 and
Douglas Colkitt the retained compact-control ancestry. Their results and
notices are unchanged. The predecessor's balanced-radix travel and rounding
results are cited premises. The new result is the exact closed table-walk
identity and sharp uniform bound after changing the fastest axis.

The bound covers table-head movement only. Counter and cache actions,
arithmetic, setup, cleanup and allocation remain separately chargeable.
The phase stream is exact symbolic arithmetic; no rounded-word equality is
asserted. A physical consumer must accept the changed named-coordinate
order or pay for its conversion. No free transpose, encoded controller,
complete multiplier or discharge of the five selected assumptions is supplied.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

Can an actual chirp consumer use the largest-radix-fastest payload order
without an extra full transpose? Start by writing the complete input/output
layout and movement bill for one real caller. The missing physical producer
and consumer, rather than this table-movement estimate, are the blocker.
The structured question is in [TASK.json](TASK.json).
