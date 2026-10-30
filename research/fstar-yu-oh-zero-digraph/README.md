<!-- SPDX-License-Identifier: Apache-2.0 -->

# A known four-chromatic zero graph with a full thirteen-line box

The Yu–Oh thirteen-ray configuration supplies an admitted rational example
for the unrestricted `chi(Z)>=4` branch requested in PR #2890. Its three
relevant quantities are different:

| Quantity | Exact value |
| --- | ---: |
| Ordinary chromatic number of the mutual-zero graph | 4 |
| Dichromatic number of the zero digraph | 4 |
| Best canonical matched-unit-pivot value | 12 |
| General directed sub-anchor box | 13 |

Thus the coloring and unit-pivot obstructions coexist with a full general
box. This is not an F-star counterexample or a new graph construction.

The rays are due to **Sixia Yu and C. H. Oh**, [arXiv:1109.4396v1](https://arxiv.org/abs/1109.4396v1),
visible Eq. (1) on page 2 and Figure 2. The contribution is their exact
instantiation in the repository's rational, canonical-anchor and directed
label contracts, with separate proofs and executable witnesses. No novelty
is claimed for the thirteen rays or their known chromatic property.

## First working example

Take `P=Q`, with one row for every nonzero direction in `{-1,0,1}³`, using
the representative whose first nonzero coordinate is positive. The rows are
the three axes, the six face directions

```text
(0,1,±1), (1,0,±1), (1,±1,0),
```

and the four body directions `(1,±1,±1)`. The verifier uses lexicographic
order. The paper's `h1=(-1,1,1)` becomes its negative `(1,-1,-1)`; changing
a ray representative's sign preserves its zero relations.

The product has rank three, nonzero diagonal and 24 unordered zero edges.
Every zero edge occurs in both directions, so an acyclic color class is
exactly an independent set. Ordinary and dichromatic coloring coincide
for this example. Actual canonical gamma is zero and `A_i=B_i` is the
coordinate-support mask. Tied cardinalities are one on the three axes,
two on the six faces, and three on the four bodies; none is empty.

## Why the three values differ

The axes force three distinct colors in any proposed three-coloring.
Each orthogonal face pair must use the other two colors, leaving eight
orientations. In every orientation one body direction sees all three
colors, so a three-coloring is impossible. An explicit four-coloring
proves equality. [PROOF.md](PROOF.md) records the finite eight-case argument.

A matched unit-pivot solution retaining all thirteen rows would be a
proper three-coloring, so its value is at most twelve. An explicit
tie-compatible twelve-row coloring attains twelve. The verifier separately
cross-checks all `2^6 * 3^4 = 5,184` canonical pivot maps; this finite
enumeration is additional evidence, not the sole upper-bound proof.

The general directed box retains all thirteen. Put the three positive
face directions first, all seven odd-tie rows in the middle, and the three
negative face directions last. The first faces use full source anchors
and tied unit target anchors; the middle uses full anchors on both sides;
the last faces use tied unit source anchors and full target anchors.
The outer blocks have no internal forward zeros. Every remaining required
zero follows from the original binary support implication SG. The literal
definition and a source-authenticated independent oracle both check the
explicit witness. Thirteen is maximal because there are thirteen rows.

## Reproduction and attribution

From the repository root, using CPython 3.12:

```sh
python3 -B scripts/research_package.py --package research/fstar-yu-oh-zero-digraph --check-only
python3.12 -B scripts/research_package.py --package research/fstar-yu-oh-zero-digraph
python3 -B scripts/check_research_commit.py --package research/fstar-yu-oh-zero-digraph --check-source-history
```

`VERIFY.json` registers normal and isolated/optimized/warnings-as-errors
replays. Exact finite checks cover the matrix, canonical anchors, coloring,
pivot values, general box and semantic/source failure controls. No numerical
tolerance, quantum-mechanical premise or predecessor search replay is used.

`SOURCES.json` identifies the literature source, its inspected version and
PDF digest, the sign mapping, the frozen PR #2890 question, and the unchanged
corrected PR #3393 oracle. The paper is cited rather than redistributed;
the replay uses the explicit integer coordinates. Aaron Wang/navinor's
zero-digraph, matched-pivot and directed-box lineage and DreamingOfClouds's
F-star definitions retain attribution. The labeling mechanisms also retain
predecessor credit. New repository instantiation and controls are Apache-2.0,
by Sagar Thakrar with substantial OpenAI Codex assistance.

Separate same-session agents contributed proof, exact controls and review;
these are not independent human acceptance or formal kernel checking.
The declared PR #2890 searches are not contradicted: this is a known
literature configuration outside those retained search results.

## Open next questions and limits

The fixture does not settle a general anchor-box theorem, the all-even
twelve-line floor, or supplier admission. Its full witness uses seven
odd-tie middle rows, which the unresolved all-even case lacks. No selected
frontier or κ changes.

For another rational orthogonality configuration, check its actual canonical
anchors and explicit directed labels before treating a coloring obstruction
as a useful F-star obstruction. Keep unrestricted coloring, canonical unit
pivots and general sub-anchor witnesses as separate quantities.

Coordination: [canonical claim and handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-19009748),
following [PR #2890's released investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-18966804).
