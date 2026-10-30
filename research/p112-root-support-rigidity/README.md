# Four small pieces cannot represent a P112 root-code word

Over every characteristic-zero field, the P112 root-evaluation code has zero
intersection with the span of four arbitrary pieces of binary support ranks
at most `2,5,6,6`. Overlaps, cancellations and arbitrary coefficients are
allowed. The proof uses the standard E8 Weyl-chamber theorem and exact finite
geometry checked here.

The new finite step is sharp near-normal section rigidity. Eleven off-normal
roots in a binary five-space force its whole twelve-root section to be
reflection-invariant. Seventeen in a six-space force a twenty-root section.
Literal boundary sections of sizes ten and sixteen show why the thresholds
cannot decrease. [PROOF.md](PROOF.md) combines this with the four missing-frame
partners of each live normal. The representation budget has slack one;
reflection closure would consume at least three missing frame sites.

For the historical independent-piece caller `2,5,6^8` with code-intersection
dimension at least six, this proves that the quotient has dimension exactly
four and its eight rank-six endpoints are pairwise distinct after removing
the two small images. The full caller exclusion remains open. This is a
partial answer to PR3295's explicit handoff, not another arbitrary-cut
extension or a new public unresolved count.

## Evidence and replay

The primary checks all 4,097,782 binary five- and six-spaces. A separate
forward-basis affine-coset implementation checks 3,989,832 nonempty-domain
sections and accounts for the remaining leading-zero spaces. Complete
histograms, critical section-set hashes and both sharp boundary masks agree.
The replay also checks linear label transport on all eight simple
reflections, the 120-normal orbit, all 112 literal four-partner inventories
and the finite chamber counts. [RESULT.json](RESULT.json) contains the exact
receipt. The scripts use the standard library and accept no solver result.

```sh
python3.12 -W error -B scripts/research_package.py \
  --package research/p112-root-support-rigidity
```

Direct commands also work on a source export with all declared inputs:

```sh
python3.12 -W error -B research/p112-root-support-rigidity/verify.py
python3.12 -W error -B research/p112-root-support-rigidity/independent.py
python3.12 -O -W error -B research/p112-root-support-rigidity/test_controls.py
```

Set TMPDIR to an external run directory to choose the disposable control
location. Four actual optimized CLI mutations, duplicate JSON keys, changed
and linked geometry, and both lowered-threshold fixtures are checked.

## Limits

The engines share the authenticated root/label source and digest encoding.
Their separate enumerations are internal computational corroboration. The
standard Weyl theorem remains a mathematical premise; human and proof-kernel
review are unrun. No full `2,5,6^8` exclusion, full C5, decoder floor, physical
consumer/restoration/hosting bill, supplier, selected-frontier change or new
kappa is claimed. Historical heavy caller suites, Lean, Docker and the selected
cold replay are unrun.

## Open next questions

The next useful question is the actual caller with eight distinct projective
endpoints. First derive one three-endpoint relation and its complete support
and coefficient contract. Pair collisions cannot be assumed. That unresolved
relation is the blocker; this package does not reserve a larger search or
another construction round. Structured details are in [TASK.json](TASK.json).

## Sources and credit

[SOURCES.json](SOURCES.json) pins canonical main
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision 6, exact geometry,
the root-simplex proof and the PR3295 handoff. No unmerged Git object is needed.
Credit Nick Petalas/PR3295 and PR3289, PR3161/3162 and the root-simplex geometry,
DreamingOfClouds/PR3154, joaqcoo and the retained E8/P112 lineage. Apache-2.0.
Automated assistance was used for research and implementation. No independent
human or proof-kernel approval is claimed.
