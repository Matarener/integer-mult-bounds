# P104 cut stability and a concrete residual-preserving COPY

For the complete PR5551 word, two independent exhaustive interpreters certify
**prefix amplification 131072** and **final-suffix amplification 135415/4** over
all 25,311 cuts. A separately checked recurrence bounds every intermediate
scalar interval by **2^296**, with dyadic denominator exponent at most 54.
All 735 arbitrary public inputs, 743 state positions and eight owned lifetimes
are retained. No new kappa is claimed.

The implementation realizes all eight COPY operations as ADD into their
initialized owned zero. This preserves the exact trajectory, every MOVE request,
paid/helper histogram and scalar tariff (217428). It also preserves arbitrary
injected owned residuals. The source's first such residual reaches public output
112 with coefficient one; treating COPY as an assignment would erase it.
`RESIDUAL-WORD.json.gz` records the literal eight-opcode implementation, while
the published input remains frozen.

[PROOF.md](PROOF.md) gives the cut matrices, all-interval induction, finite
integer/fractional formats and coordinate error interface. The retained
unitary active-fiber method yields the local conversion
`2^ceil((9f+1)/2)` with no external spectator-count factor. The new contribution
is its current complete-word binding and residual-aware source application;
the general method is credited to Ross Richardson / Adam Gall and the earlier
P104 precision/recovery contributors.

The [whole-caller application](whole-caller/PROOF.md) retains all 32 main banks,
9486 independent helpers and a constructive 248-position owned reservation.
Its interval bound is **2^5844** in maximum-individual-field Hilbert norm and
**2^(5844+ceil((265f+1)/2))** in coordinate norm, after exactly one conversion
on the 265f active coordinates. It includes a fresh ordinary/normalization
ledger and fixed finite range/storage constants. The coarse chart-product
bound and denominator ledger are retained as crosschecks.

This is evidence toward scientific review of PR5551's existing conditional
kappa 0.00304153. The five selected native/ownership/compiler/precision-tape/
analytic premises remain. Recursive child internals, a fixed-tape microprogram,
the enormous uniform word and a rounded multiplier are not materialized.
Literal C-butterfly precision witnesses are not priced as recursive services.
Scientific adoption and selected-frontier promotion remain maintainer decisions.

## Reproduce

Python 3.12 and its standard library; mathematical replay needs no Git/network:

```sh
python3 -I -B research/p104-cut-stability/verify.py
python3 -I -O -B research/p104-cut-stability/verify.py
python3 -B scripts/research_package.py --package research/p104-cut-stability
python3 -B scripts/check_research_commit.py --package research/p104-cut-stability --check-source-history
```

The first two commands authenticate retained bytes, run the dyadic and separate
Fraction all-cut censuses, reproduce maximum-row/COPY controls, check the
independent interval fixture, replay the retained source's typed interpreter
on both literal words, and join the whole-caller census to this exact source.
They write nothing. The last two additionally require repository provenance.
Expected marker: `PASS_P104_CUT_STABILITY_AND_CALLER_BOUNDS`.

The Fraction [peer](peer/README.md), [witness/proof review](proof-peer/REVIEW.md),
[range appendix](range-peer/PROOF.md) and [fiber review](FIBER-REVIEW.md) retain
their original narrower claims and input snapshots. The aggregate wrapper
binds every consumed numerical field to the current source. These are separate
author-side algorithms and reviews, not human or formal-kernel acceptance.
Executed validation and cold replay scope are in [VALIDATION.md](VALIDATION.md).

## Open next questions

Can independent source-bound scientific review accept this finite error/range
application together with the original PR5551 complete conditional price?
The concrete first step is the ADD-COPY residual interface, complete cut peers,
active-fiber conversion and actual ordinary/reservation ledger. Applying the
retained recursive child and tape contracts remains distinct from proving them.
This package stops before a new source-family search or frontier promotion.

## Credit

Retain Ali Romman, Gareth Davidson, David Arias, Cinna Davis, Cao Yifan, zxv,
Jacob Alan Sussman and the full PR5551 native/geometry/compiler/precision
lineage. The earlier cut-error and active-fiber/grid methods retain Adam Gall,
Ross Richardson, Arham Tahir, Nick Petalas and ywz65 attribution. Their old
358-input/5268-event partial-word constants are not transferred to this word.
Prepared for thu-nmrc with substantial OpenAI Codex assistance, including
independent subagents. New work Apache-2.0; source notices remain unchanged.
