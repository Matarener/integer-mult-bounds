<!-- SPDX-License-Identifier: Apache-2.0 -->

# Repair the mutual-zero neighborhood classification

PR #2890 Lemma C5's nonparallel-center branch is false as stated. A
three-row rational example with nonempty, even canonical tied sets
already contradicts it. The corrected theorem preserves the intended
no-odd-wheel conclusion:

> For a matrix over any field with rank at most three and nonzero diagonal,
> every mutual-zero open neighborhood is a disjoint union of complete
> bipartite components and isolated vertices.

Here a mutual-zero edge means **both** directed matrix entries are zero.
The theorem concerns the graph induced by a center's open neighborhood,
not the whole mutual-zero graph or the graph of one-way zeros.

## First working example

```text
P = [(1,1,0), (1,0,1), (0,1,1)]
Q = [(1,1,-1), (1,-1,1), (-1,1,1)]
P Q^T = 2 I3
```

The center's factors `(1,1,0)` and `(1,1,-1)` are not parallel. Its two
mutual-zero neighbors are adjacent, contradicting C5's edgeless conclusion.
Three vertices are minimal for an edge inside an open neighborhood.
Every factor column is active, the actual valuation minima and gamma are
zero, and the canonical masks are `A=(3,5,6)`, `B=(7,7,7)`: all ties have
cardinality two.

Repeating each paired row four times gives `2 diag(J4,J4,J4)`. The center's
neighborhood is `K4,4`. Unit labels `1,4,2` on the three respective groups
give a full twelve-line box. This refutes the source lemma, not the
twelve-line box-eight target or F-star.

## What is corrected

The pinned [PR #2890 source](https://github.com/CrocSwap/integer-mult-bounds/blob/08a44355403604c346f8d907811edce992382cc4/research/fstar-chi4-zero-digraph-seed73765f29/README.md)
uses `q_t=e1, p_t=e2` in the nonparallel case. That would make the center
diagonal zero. Coordinate changes preserving a factorization act dually
on P and Q; parallelism of their corresponding rows is not invariant.

The replacement proof in [PROOF.md](PROOF.md) first classifies every
rank-two matrix with nonzero diagonal. A vertex has a projective column
direction and a different row-kernel direction. Mutual-zero edges connect
exactly reciprocal pairs of these types, giving complete bipartite
components. A rank-three center's mutual-zero neighbors have principal
rank at most two, so the classification applies uniformly.

Thus every such neighborhood is bipartite. No odd wheel can occur,
including as a non-induced subgraph. The predecessor's Lemma C4 survives
with a valid stronger proof. The source's parallel branch is overbroad:
its same-type clique option is excluded by nonzero diagonal.

## Verification and source boundary

From the repository root, using CPython 3.12:

```sh
python3 -B scripts/research_package.py --package research/fstar-mutual-zero-neighborhood --check-only
python3.12 -B scripts/research_package.py --package research/fstar-mutual-zero-neighborhood
python3 -B scripts/check_research_commit.py --package research/fstar-mutual-zero-neighborhood --check-source-history
```

`VERIFY.json` registers normal and isolated/optimized/warnings-as-errors
replays. The exact controls bind the predecessor statement, check the
canonical counterexamples, compare literal mutual-zero graphs with the
reciprocal-type classification, and exercise the nonzero-diagonal,
one-way-zero and dual-coordinate boundaries. They are finite controls for
an analytic proof, not a proof by exhaustive rational search.

The predecessor README is frozen unchanged in `inputs/`; its original
commit, path, blob and SHA256 are in `SOURCES.json`. Read-only inspection
of the pinned predecessor verifier found no use of the false nonparallel
case as a search prune: its sequential construction uses actual nullspaces
and dot products. That engine was **not rerun**, and no changed census
result or comprehensive downstream audit is claimed.

New work is Apache-2.0, by Sagar Thakrar with substantial OpenAI Codex
assistance. The original C3/C4/C5 statements, source package and F-star
context retain Aaron Wang/navinor's attribution. Separate same-session
agents contributed proof, controls and review; these are not independent
human acceptance or formal kernel checking. No supplier admission,
selected-frontier change or κ improvement is claimed.

## Open next questions

1. Which downstream arguments, if any, use the rejected nonparallel-empty
   branch? Check the actual caller before changing it; a citation to the
   predecessor engine is not evidence that its search used this lemma.
2. What additional information controls canonical anchor boxes when local
   bipartite mutual-zero neighborhoods do not settle global coloring?
   Keep ordinary directed coloring separate from tied-coordinate-compatible
   labelings and actual rational realizability.

Coordination: [canonical claim and handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-19009680),
following the [released predecessor handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18966804).
