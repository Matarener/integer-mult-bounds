# Exact projection cuts can stop at a strict local minimum

Scoped proof with exact finite corroboration. For every field K and every
power tariff f(r)=r^t, 0<t<1, a legal three-vertex frame graph can be a
strict local minimum for every rank-one projection move while two commuting
projections lower its complete paid objective. The exact minimum number of
parallel edges in the stated two-boundary class is

    2 floor(1/(2-2^t))+1.

At t=997/1000 this minimum is 481. Fix boundary frames 0 and K^2, give one
free frame S 241 incoming and 240 outgoing edges, and charge every edge:

| Free frame | Complete paid objective |
|---|---|
| Initial K^2 | 241 * 2^t |
| Any line, after one projection | 481, strictly larger |
| Zero, after two complementary projections | 240 * 2^t, strictly smaller |

The same graph is a strict trap for 0<t<=997/1000. Its minimality is claimed
only at t=997/1000. [PROOF.md](PROOF.md) proves the all-field, all-power
construction and sharp threshold. Two exact integer inequalities certify
the numerical example without floating point or an exponential oracle.

## Why this matters

David Ganz / Dugongue's [PR556](https://github.com/CrocSwap/integer-mult-bounds/pull/556)
optimizes every legal binary choice for one rank-one projection by a
minimum cut. This example shows that even an exhaustive collection of
those exact moves does not certify a joint optimum. A search needs richer
simultaneous moves or permission to cross an intermediate increase.
The predecessor theorem and implementation are cited, not reverified.

This is an abstract frame-search obstruction. It supplies no scalar word,
productive target map, arbitrary-dirt physical implementation, phases,
restoration, owner/stock/precision/tape costs, complete signed caller bill
or uniform compiler. No new kappa or multiplication theorem is claimed.
The five selected framework assumptions remain. The selected source pin
places its complex exponent inside the example's interval; no embedding
in that supplier or gain in its actual invoice follows.
The free vertex has 481 incident edges. It is not identified with an
ordinary bounded-arity scalar instruction.

The complex-rank-shape-decoder card is explicitly changed to this side
question. The source-bound baseline passed. No selected scientific replay,
Lean or Docker run was performed.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/projection-local-trap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/projection-local-trap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/projection-local-trap
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/projection-local-trap --check-source-history
```

A reviewer may substitute a local CPython 3.12 path. The direct checker
writes nothing, recomputes the receipt, and requires exact agreement with
[RESULT.json](RESULT.json), including SHA256 of the six scientific and
metadata files. `--generate` emits a fresh computed receipt to stdout.
This is not a formal proof-kernel certificate.

Finite corroboration covers every positive a,b<=40 for every distinct
rational h=1+n/d, 1<=n<d<=32, plus every pair below each predicted minimum.
The checker enumerates all 2-by-2 matrices over F2,F3,F5,F7,F11, filters
rank-one idempotents, checks every ordered pair of them, and literally
retains all 481 edges for every subspace. The universal statement rests on
the written proof, not these finite domains. Exact power comparisons also
exclude every smaller incoming multiplicity at t=997/1000.

The generated receipt records 323 rational tariffs and 516800 multiplicity
pairs, with 125663 strict traps and 614 ties having a cheaper zero frame.
It also checks 28047 pairs below the predicted graph minima, 17764 field
matrices, 236 projectors, 21640 ordered projector pairs and 236 joint
escapes. All 43 subspaces retain 20683 literal edge occurrences in total.
The exact-power check rejects 28680 pairs with a<241. Fifteen named controls
cover tariff and multiplicity domains, strict boundaries, non-idempotent
maps, a noncomplementary pair, invalid powers and altered receipts.

## Verification design

All loops have fixed finite bounds. The largest matrix inventory is
11^4=14641, with 132 retained projectors; the scalar grid stores only its
tariffs and running counts. No recursion, subprocess, dynamic import,
network, predecessor execution or filesystem write is used. Functions
remain below 60 physical lines. Invariants and rejection controls remain
active under optimized Python.

Power-of-ten rule 3 deviation: CPython and Fraction allocate dynamically.
The scope is this terminating checker. Fixed field/grid bounds, at most
121 vectors and 132 projectors per field, and at most 1000 in power
denominators bound retained data and integer sizes. Normal and optimized
replays exercise these maxima. A runtime with static allocation would be
needed for literal allocation-free compliance. No shared runtime is changed.
Warning-strict replay is the available interpreted-language diagnostic;
no additional static analyzer is required by this isolated package.

## Open next questions

1. Can a legal selected scalar-word neighborhood realize this coordinated
   projection advantage after every productive target and restoration fee?
   Start with one actual frame neighborhood, retain its fixed observations,
   and produce both complete signed invoices. The present abstract graph
   does not supply independent physical data paths.
2. Can a two-projection move be optimized with an exact certificate on a
   useful restricted class of frame graphs? Start with two specified
   commuting projections and four image choices per event. Their mixed
   inclusion rules and full paid/target objective remain to be derived.

## Credit and overlap

This contribution was produced by Nick Petalas. David Ganz / Dugongue
retains the binary projection-cut theorem, frame-graph contract and search
implementation in PR556. That theorem credits standard graph-cut methods
to Picard and Kolmogorov/Zabih; rank-nullity and concavity are standard.
The new contribution is the all-field strict trap, sharp multiplicity
formula and exact 481-edge witness in this specific frame-search model.
No general literature-priority claim is made for local-search traps.

Base: a5bff3bf133e482541c09eba4e773884bdb2b1b7, priority revision 8.
The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19272058)
and local reservation identify this question. Live PR/discussion searches,
merged README/formula searches and recent account contributions found no
matching result. The overlap helper reported 310 open PRs and 5900
discussion records, but only 92 of 8623 local notes were materialized;
separate Git searches covered main READMEs. This is bounded coverage, not
proof of novelty. PR5428's superoptimizer proposal is related motivation;
it supplies no strict-trap threshold. PR563 uses contextual provider
selection and cites PR556; it computes a different construction.

Independent human and formal proof-kernel review are unclaimed. New files
are Apache-2.0. Predecessor source bytes and credit are unchanged.
