# A two-guard reciprocal with thirteen-candidate correction

A changed seeded reciprocal routine satisfies `|1-cy| < 2^(-p-1)` for every
real `1 <= c < 2` and positive integer `p`, with two fractional guard bits
per Newton stage and a final correction using at most thirteen products.
The fixed six-bit warm-up remains. For `p>=4`, the maximum rounded precision
falls from the credited three-guard routine's `p+3` to `p+2`.

Claim type: a scoped written mathematical proof and explicit numerical
construction, corroborated by exact finite enumeration. No runtime or kappa
improvement is claimed. Extra products, exact intermediate products, physical
tape costs and caller integration remain payable.

The stage index starts at two and advances to `min(2m-1,p)`. Its weaker
invariant `|1-cx|<2^-m` permits two guard bits. The last correction searches
thirteen adjacent grid positions against the truncated input. [PROOF.md](PROOF.md)
proves that this window contains the nearest reciprocal of that prefix and
that its true-input residual meets the required strict bound. It also counts
the complete arithmetic operations of this new numerical interface.

This answers the changed-schedule question in Charles Bethin / cbethin's
[PR #1655](https://github.com/CrocSwap/integer-mult-bounds/pull/1655).
Its unchanged-schedule lower bound, ToikY's
[PR #1638](https://github.com/CrocSwap/integer-mult-bounds/pull/1638)
upper theorem and Ross Richardson's
[PR #1678](https://github.com/CrocSwap/integer-mult-bounds/pull/1678)
failure-locus census are cited context. They are not replayed or audited.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19226175)
records the delivered scope.

## Evidence

The verifier covers every real input by prefix cells for targets 1 through 12:
32,896 half-open cells, checking both residual endpoints. A separate integer
significand implementation checks each Newton trace, and an exact-division
oracle checks final selection without importing the construction's helpers.
There are also 95 cases through target 4096, including inputs near both
normalization endpoints, and twelve rejecting input/result controls.

For example, at `c=127379/65536`, `p=15`, the new routine returns
`16859/32768`, with residual `1087/2147483648 < 2^-16`.
This is the new routine's output, not a recheck of the predecessor execution.
The all-target theorem rests on the written induction, not the finite census.

The Python implementation supports rational inputs and targets through 4096,
with a 16384-bit input-size cap. The proof permits arbitrary positive targets
and real inputs, interpreted through finite binary prefixes. It assumes exact
products before floor rounding. No correctly rounded reciprocal, sharp guard
minimum, independent human review or proof-kernel acceptance is claimed.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/reciprocal-two-guard-correction
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/reciprocal-two-guard-correction/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/reciprocal-two-guard-correction --check-source-history
```

The scientific marker is `PASS_TWO_GUARD_RECIPROCAL`; the registered launcher
must report `PASS_REGISTERED_RESEARCH_PACKAGE`. Both warning-strict normal and
optimized checks are registered. `verify.py --receipt /absolute/new/path.json`
optionally generates an exclusive-create receipt bound to every package file
and live source hash. Default replay writes no files.

## Scope, sources and credit

Base main is `19fdb086ea96af9a9f87936a2b888e10af4ed810`, priority revision 8.
[SOURCES.json](SOURCES.json) binds the exact predecessor documentation, task
catalogue and selected record. The source documentation is authenticated before
the new checks; predecessor executables are never imported. Overlap checks
included live open PRs and Discussions, this account's recent work, merged PR
searches and main's reciprocal/guard/correction terminology. These searches
establish bounded text coverage, not exhaustive novelty.

The original `uniform-transfer-audit` card is explicitly changed to a numerical
side result. This downstream reciprocal corollary is outside the selected
supplier. The five selected assumptions remain; the selected frontier is
unchanged. No complete root/recovery caller, physical rounder, fixed-tape
machine or multiplication algorithm is built.

The construction, proof and verifier were produced by Nick Petalas.
Credit Charles Bethin / cbethin #1655 for the open question, ToikY #1638
for the directed-rounding framework, Hanson Sun / bbMisk #1528, the retained
manuscript and classical Brent/Newton lineage. Ross Richardson #1678 supplies
separate fixed-schedule context. Source files and their credit lines remain
unchanged. New work is Apache-2.0. Independent human and formal proof-kernel
review are unclaimed.

## Open next questions

- Can the final window be reduced or its search replaced by fewer products?
  This matters to a real cost comparison. First prove a sharper signed
  pre-correction bound, then test the reduced window. No optimality proof is
  currently supplied.
- Can one guard bit work with another correction or input-prefix contract?
  First derive a true-input interval invariant and state the additional prefix
  precision explicitly. This theorem proves sufficiency of two only.
- Can this exact arithmetic routine replace the numerical call in the retained
  root/recovery algorithm? First bind its prefix reads, full product widths,
  correction and storage to that caller. Physical tape and complete bit-time
  costs are unproved.

Structured questions and blockers are in [TASK.json](TASK.json).
