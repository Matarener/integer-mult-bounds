# Four P112 pieces with ranks 3,5,6,6 cannot represent a codeword

Over every characteristic-zero field, the P112 root-evaluation code has zero
intersection with the span of four arbitrary pieces of binary support ranks
at most **3,5,6,6**, conditional on the standard E8 Weyl-chamber theorem.
This increases PR3397's first-rank allowance from two to three. Arbitrary
coefficients, overlaps and cancellations are allowed.

The stronger statement permits any first piece on at most four sites. Three
large sections of ranks 5,6,6 always leave at least five sites of a live root
word uncovered in the necessary cover domain. A literal five-site piece does
complete a representation, so this cardinality allowance is sharp. Its binary
rank is five. The separate rank-four question remains open.

[PROOF.md](PROOF.md) gives the complete implication and its premise. The primary
checks all 4,097,782 binary five/six-spaces in each of three root-normal orbits.
A separate forward affine enumeration matches the section sets and complete
residual profiles. [RESULT.json](RESULT.json) records the exact quantities and
two five-site boundary witnesses. Their four pieces have sizes 5,10,20,18 and
ranks 5,5,6,6, and sum to a literal root codeword on all live coordinates.

## Reproduction

Standard library, Python 3.12, from the repository root:

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/p112-four-piece-rank3
```

Direct commands work on a Git-free export containing all declared inputs:

```sh
python3.12 -W error -B research/p112-four-piece-rank3/verify.py
python3.12 -W error -B research/p112-four-piece-rank3/independent.py
python3.12 -O -W error -B research/p112-four-piece-rank3/test_controls.py
```

Set TMPDIR to an external run directory for disposable control fixtures. Nine
behavioral groups include the actual five-site coefficient boundary, rejection
when the excluded small-support allowance is incorrectly raised to five, and
four optimized CLI mutations of sources, links and receipts. Production checks
remain enabled under `-O`.

## Limits

The standard Weyl theorem remains a mathematical premise. The two enumeration
engines share authenticated geometry and digest encoding. Internal checks are
not independent human or proof-kernel approval. No complete caller, full C5,
decoder floor, physical supplier, new kappa or selected-frontier change follows.
Lean, Docker and the selected cold replay are unrun.

## Open next questions

First-piece binary rank four remains unsettled. Its eight-site capacity raises
the budget to 60 and changes the necessary six-section threshold to 13. The
current 320-section domain cannot be reused as exhaustive there. A separate
application to an actual caller needs its literal quotient and relation
contract first. [TASK.json](TASK.json) records these questions and blockers.
This contribution starts no further supplier construction round.

## Sources and credit

[SOURCES.json](SOURCES.json) pins canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6, the exact
root-simplex geometry/proof and literal P112 labels and roots. The new proof
rechecks its finite capacity and chamber facts. It needs no unmerged Git object.
[PREDECESSORS.json](PREDECESSORS.json) distinguishes contextual pending work
from actual inputs.

Credit Nick Petalas/PR3397 and PR3405, PR3161/3162 and the root-simplex package,
DreamingOfClouds/PR3154, joaqcoo and the retained E8/P112 lineage. Apache-2.0.
Human and proof-kernel review are unrun.
