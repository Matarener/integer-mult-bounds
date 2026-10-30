# Functional decoder pairings cannot beat cost v

This contribution was produced by Nick Petalas. Apache-2.0.
Claim type: scoped proof with exact finite corroboration. Independent human
and formal proof-kernel review are unclaimed.

For every binary pairing B with unit diagonal and at most one off-diagonal
one per row, an explicit integer signing preserves the rank of every
rectangular submatrix, simultaneously, over every field. The transposed
class has the same property. Consequently every exact decoder compatible
with B has total binary COPY-rank cost at least v, for any finite number
of totals and over any coefficient field. The bound is attained with v
coordinate totals. Attainment with three totals is not asserted.

The construction puts one minus sign on each odd directed successor cycle.
Every square minor of the resulting matrix is 0, 1 or -1. The proof uses
leaf expansion and the retained Hadamard/lift rank argument. See
[PROOF.md](PROOF.md) for all quantifiers and the field-independent proof.

This adds a sufficient reduction to DreamingOfClouds's PR #2111, Open next
question 8. It does not replay its examples or signing searches. Classical
total unimodularity and the predecessor's Hadamard rank argument retain
their credit; no historical novelty is claimed for those tools. The new
contribution is this explicit sparse-class reduction and its checker.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/functional-pairing-lift/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/functional-pairing-lift/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/functional-pairing-lift
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/functional-pairing-lift --check-source-history
```

Another CPython 3.12 path may replace the local interpreter. The scientific
marker is `PASS_FUNCTIONAL_PAIRING_LIFT`. Direct replay reads the pinned
PR2111 README but executes no predecessor code. It needs no Git or network.
The generic source-history check additionally needs the retained Git history.

Every functional matrix of orders one through four is enumerated. The
checker compares binary and exact rational ranks on all rectangular
submatrices and computes every square minor by an independent Leibniz
formula. Larger cycles, paths, stars and disjoint-pair families through
order sixteen have prefix/suffix rectangular-rank checks. Nontrivial
two-total cycle decoders and coordinate-total attainments are checked.
Malformed inputs, the capacity boundary and an unsigned odd-cycle lift
distinguish the hypotheses. The generated [RESULT.json](RESULT.json)
records counts and binds every proof, code and metadata file by SHA256.
Normal replay writes no files. `--emit NEW_EXTERNAL_PATH` creates a new
receipt without overwriting an existing file.

## Limits and implementation bounds

The row or column condition is imposed on the complete chosen pairing,
not a subset of its edges. General pairings and the general three-total
lift conjecture remain open. This is a mathematical cost obstruction,
not a new decoder, native word, supplier invoice, kappa or selected-frontier
update. Physical ownership, restoration, routing, precision, compiler and
analytic recovery obligations remain separate. No selected cold replay,
Lean or Docker run is part of the claim.

The signer caps dense input order at 256 and uses no recursion, subprocess,
network, mutable global cache or predecessor import. All loops have bounds
from that cap or fixed census limits. Each function is below sixty lines.
Explicit exceptions remain active under `-O`; warning errors are enabled
in both registered commands. No external static analyzer is claimed.

Power of Ten rule 3 deviation: CPython allocates integer, Fraction and
collection objects during execution. This one-shot exact checker cannot
disable those allocations. The signer retains O(256^2) cells, the complete
census works on matrices of order at most four, and the larger fixtures
have order at most sixteen. It retains one current submatrix at a time.
The endpoint and oversize controls check the input bound. A future native
steady-operation implementation would need fixed-capacity storage before
removing this deviation.

## Sources and overlap

The exact base is `3f0152a32eeebac0df11946dbd50cabe5a7f7839`, priority revision
8. [SOURCES.json](SOURCES.json) pins the source README, historical card and
selected record. The current baseline binding check passed; it is not a
scientific supplier replay. The card's scope change is in [TASK.json](TASK.json).

The [advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19267785)
and reservation followed live open-PR, recent-account, handoff, main README
and merged-PR searches. Targeted terms included functional pairing,
pseudoforest, cactus, one off-diagonal contact and directed-cycle decoder.
The cached overlap scan omits sparse local notes; explicit Git searches
covered all main README paths for the distinctive terms. This is bounded
overlap evidence, not a novelty certificate or coverage of unpublished work.

Credit DreamingOfClouds #2111 for the model, lift hierarchy and open reduction
question; #1590 for the exact decoder and Hadamard/lift lemma; and #446/#595
for the underlying cost model. The E8/P104, native, helper, caller and
compiler sources retain their predecessor credit. Existing files and
their credit lines are unchanged.

## Open next questions

1. Can a named second contact preserve simultaneous ranks? Specify its
   entire pairing graph and first overlapping cycles. The one-successor
   argument does not decide this larger class.
2. Can the reduction prune a new decoder search? Start with its complete
   chosen pairing and preserve all nonfunctional candidates. This package
   supplies no search integration or physical supplier.
