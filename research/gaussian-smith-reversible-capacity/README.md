# Sharp clean storage for reversible Gaussian overwrite

The exact initially clean storage for destructively overwriting
`C tensor n times x modulo pi^P`, with `C=[[i,1],[1,i]]` and `pi=1+i`, is

```text
K(n,P) = sum_j binom(n,j) min(2j,P) bits.
```

This minimum allows arbitrary reversible mixing and arbitrary finite borrowed
dirty workspace, even if the dirty field may change. An explicit bit permutation
through the cited Smith factors attains it while leaving dirty workspace alone.
The retained auxiliary output cannot then be erased reversibly from the modular
response alone. This answers the destructive-overwrite portion of Open next
question 4 in [Ali Romman's PR #5821](https://github.com/CrocSwap/integer-mult-bounds/pull/5821).

At normalized precision `p>=n`, raw precision is `P=p+n` and the sharp clean
capacity is `n*2^n` bits. At `p=n>0`, that is half the public raw input size.
These are storage bounds, without a time or kappa improvement.

## Claim and evidence

This is a scoped written mathematical proof with exact finite corroboration.
[PROOF.md](PROOF.md) states the contract, counting lower bound, attaining
permutation, inverse and cleanup consequence. The predecessor's image theorem
and Smith factors are cited; its image census and precision/cost replays are
not this contribution. The new verifier checks the augmented reversible map.

The finite checks enumerate 17,898 full public/auxiliary states in 14 complete
permutations, including 646 clean-input endpoints. They also check 432 larger
interfaces, 272 clean endpoints, 1,492 individual retained-bit witnesses,
216 dirty-undercapacity comparisons, ten invalid-input controls and four
semantic controls. The verifier emits a generated SHA256-bound receipt to
stdout and writes no files. No receipt is hand-authored or stored in this package.

The original `uniform-transfer-audit` card is explicitly changed to this
successor-interface result. It concerns `owned_erasure` and `precision_tape`
boundaries, but does not discharge an assumption of selected #5599. The source
preserving array contract remains different: retaining the original source
already retains the lost information. Physical reversible gates, tape routing,
operation costs, reusable clean restoration and independent human/formal
proof-kernel review remain unclaimed. The selected frontier is unchanged.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
PY=/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12
"$PY" -W error -B research/gaussian-smith-reversible-capacity/verify.py
"$PY" -O -W error -B research/gaussian-smith-reversible-capacity/verify.py
"$PY" -B scripts/research_package.py --package research/gaussian-smith-reversible-capacity
"$PY" -B scripts/check_research_commit.py --package research/gaussian-smith-reversible-capacity --check-source-history
```

The last command checks publication bytes after committing. Both registered
commands have 30-second timeouts. Normal and optimized verification use explicit
exceptions, so optimization cannot remove the checks. A Git-free exported copy
can run the direct verifier from any working directory. Source history is
required only for metadata provenance and publication checks. No predecessor
code, Git object from a pending PR, network access or dependency installation
is needed by the scientific replay.

## Execution bounds and implementation decisions

Only `overwrite` and `dimensions` are the executable interface; arithmetic and
chart helpers receive validated internal values. The implementation caps depth
at 8 and raw precision at 16, hence 256 public coordinates and 4,096 bits in
each public/auxiliary field. This bound restricts the executable corroboration,
not the all-size written theorem. Exhaustive enumeration is separately capped
at 14 total bits. Larger fixtures use `n<=5`, `P<=8` and eight patterns per case.

The implementation uses bounded loops without recursion, direct calls and no
generated code. Every function is under 60 physical lines. Runtime contracts
and verifier failures use exceptions that remain active under optimization.
Python requires dynamic object allocation, a Power of Ten rule 3 deviation.
Its scope is this bounded offline model. Fixed dimension limits, a maximum
16,384-entry exhaustive state set and the registered timeout bound resources;
no host-memory or physical-tape bound is inferred from Python execution.
A lower-level physical implementation would need its own allocation and
operation ledger. Warning-strict normal/optimized replay is the available
diagnostic check; separate Python static analyzers are unavailable on PATH.

## Open next questions

1. Implement the attaining pi-adic permutation on one permitted reversible
   native/tape host. The clean-capacity optimum alone gives no operation bill.
   Start with the one-axis map and charge chart conversion and each bit move;
   the physical gate alphabet and representation contract are blockers.
2. Price source-preserving compute-copy-uncompute against destructive overwrite
   plus retained kernel information for one real caller. Start by listing exactly
   which source or kernel information the caller retains at its next cut.
   Caller lifetimes and a complete paid bill are required before comparing routes.

## Credit and provenance

This contribution was produced by Nick Petalas. Apache-2.0.
Credit Ali Romman #5821 for the explicit open question and image-information
theorem; Dugongue #5815 for the Smith circuit and Gaussian correction context;
and the classical finite-ring cardinality and reversible-embedding arguments.
The Gaussian/native/controller/compiler lineage retained by those sources,
including Cinna Davis, Cao Yifan and the credited predecessor contributors,
remains theirs. Their files and credit lines are unchanged.

The exact predecessor heads are recorded in [PROOF.md](PROOF.md) and
[TASK.json](TASK.json). They are literature references, not runtime dependencies.
[SOURCES.json](SOURCES.json) pins the task catalogue and selected-record
provenance at main `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8.
Live overlap checks included the handoff board, open PRs, this account's recent
PRs, concurrent reservations, exact main-text searches and merged-PR searches.
The cached helper searched 426 open PRs and 5,331 discussion records; its sparse
local notes covered 200 of 7,845 paths. Direct Git searches supplemented that
incomplete local coverage. No global literature-priority claim follows.
