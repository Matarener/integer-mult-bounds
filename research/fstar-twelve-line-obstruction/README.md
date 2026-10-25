<!-- SPDX-License-Identifier: Apache-2.0 -->

# Twelve-line obstruction reduction: general structure and an F₂ theorem

The rational twelve-line anchor-box floor eight remains **open**. This
package narrows failures of a sufficient matrix route and proves that the
route always succeeds over F₂. It also settles the rational case with an
odd canonical tied cardinality on at least one row.

An ordered nonzero block is a sequence of distinct indices with a nonzero
matrix entry from every earlier index to every later index. Suppose a
twelve-by-twelve matrix over any field has rank at most three and nonzero
diagonal, but has no two disjoint ordered blocks retaining at least eight
indices in total. Then:

- its rank is exactly three;
- every projective direction among either factor's rows occurs at most twice;
- each matrix row and column has at most five zero entries.

These restrictions exclude the entire residual class over F₂. There are
only seven projective directions: twelve nonzero Q rows with multiplicity
at most two have either six doubled directions and one absent direction,
or five doubled directions and two singletons. The zero-degree restriction
then permits at most three or five P directions, respectively, and hence
at most six or ten P rows. Neither permits twelve.

This is an analytic theorem, not a finite matrix census. [PROOF.md](PROOF.md)
gives the rank-two partition and prescribed-prefix constructions, the
repeated-direction reduction, the zero-degree reduction, and the F₂ count.
The retained seven-row ordered-triple lemma is attributed to [PR #3420 at
its exact head](https://github.com/CrocSwap/integer-mult-bounds/blob/e2d39da9c7109f361d6cff677cf9f8eba51f3dd6/research/fstar-nine-line-floor/PROOF.md).

## What transfers to rational anchors

For canonical rational three-total factorizations, actual zero entries
satisfy the binary support condition SG. Two ordered blocks therefore
give a directed sub-anchor witness by the retained asymmetric labeling.
Rank at most two admits a partition into two ordered blocks, so it gives
a full box of all rows under the nonempty-tie hypothesis.

For twelve rows, one odd tied cardinality suffices: apply [PR #3435's
eleven-row four-plus-three matrix theorem](https://github.com/CrocSwap/integer-mult-bounds/blob/0833fff0bdc9acdd3b174c7677ab1b46873b22d3/research/fstar-eleven-line-floor/PROOF.md)
to the other eleven rows and place the odd row, with its full anchors,
between the two blocks. This keeps eight rows. The original global
anchors are retained; they are not recomputed on the eleven-row subset.

The unresolved rational case thus has rank three and tied cardinality two
on every row. Its normalized matrix has **zero diagonal modulo two**.
Consequently the F₂ theorem's nonzero-diagonal assumption fails: reducing
the factors modulo two does not solve the rational problem. A failure of
the two-block route would also not itself be a box counterexample.

## First working example

Use Aaron Wang's PR #2978 rational core and repeat each paired row four times:

```text
P = [(-1,-3,0), (1,-1,-2), (3,3,3)]
Q = [(1,-3,2), (3,-1,-2), (3,-1,2)]
```

The twelve-row product is `diag(8 J4, 8 J4, 12 J4)`, with rank three,
canonical gamma zero, and tied cardinality two everywhere. Two components
give an eight-row witness. The box is exactly eight: any larger witness
would meet all three components, whose three representatives have zero
off-diagonal pairings. Their ordered label matrix would have rank three,
whereas every B sub-anchor lies in the same two-dimensional binary
coordinate plane. This example is an upper bound for the sought floor,
not a proof that all rational instances attain it.

## A rejected intermediate lemma

The tempting statement “eight rows of rank three with no ordered
four-block must contain an independent triple” is false over Q. The
retained exact counterexample is:

```text
P = [(1,0,0), (0,-1,1), (-1,1,0), (0,1,0),
     (-1,1,-1), (1,0,0), (0,0,1), (0,0,1)]
Q = [(1,0,0), (0,0,1), (0,1,0), (1,1,0),
     (1,0,0), (1,1,1), (0,1,1), (0,0,1)]
```

Its product has rank three and nonzero diagonal. All 1,680 ordered
four-tuples fail, and none of its 56 triples is independent in the graph
joining pairs with at least one nonzero directed entry. Its canonical
ties all have cardinality one, so full anchors retain all eight rows.
It refutes the intermediate matrix lemma, not an anchor-box bound.

## Reproduction and evidence

From the repository root, using CPython 3.12:

```sh
python3 -B scripts/research_package.py --package research/fstar-twelve-line-obstruction --check-only
python3.12 -B scripts/research_package.py --package research/fstar-twelve-line-obstruction
python3 -B scripts/check_research_commit.py --package research/fstar-twelve-line-obstruction --check-source-history
```

`VERIFY.json` registers normal and isolated/optimized/warnings-as-errors
replays. `verify.py` and `RESULT.json` provide finite exact controls for
the constructions and proof branches, the F₂ multiplicity count, positive
anchor witnesses, and the rejected shortcut. The frozen independent box
oracle is authenticated before execution. These controls are not formal
proof checking or an exhaustive search of rational matrices. Bounded
discovery searches are not premises and are not publication artifacts.

New work is Apache-2.0, by Sagar Thakrar with substantial OpenAI Codex
assistance. Separate same-session agents contributed proof, controls and
review; this is not independent human acceptance. `SOURCES.json` preserves
the exact oracle lineage and predecessor attribution, including
DreamingOfClouds's F-star definitions and Aaron Wang/navinor's directed
box, SG and rational-core work. The selected frontier and κ are unchanged.

## Open next questions

1. Exclude or realize the residual rational matrix class: rank three,
   direction multiplicities at most two, and zero degrees at most five.
   An exact counterexample must check all ordered-block alternatives,
   not only the four-plus-four split.
2. If that sufficient route fails, inspect its actual canonical anchors.
   The rational twelve-line target only remains open when all ties have
   cardinality two; a zero-diagonal F₂ reduction cannot use this package's
   finite-field theorem.

Coordination: [canonical claim and handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-19009506).
