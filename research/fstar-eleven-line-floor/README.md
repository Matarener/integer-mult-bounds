<!-- SPDX-License-Identifier: Apache-2.0 -->

# Eleven rational three-total lines admit a box of seven

For rational `M=P Q^T` with eleven rows, three factor columns, nonzero
diagonal, and nonempty canonical tied sets on every row, this package
proves **box(M)>=7**. It does not claim sharpness: the included rational
example has box exactly eight.

The new matrix theorem is stronger and works over **any field**: every
eleven-by-eleven matrix of rank at most three with nonzero diagonal has an
ordered nonzero four-block. An ordered block requires every forward entry
to be nonzero; an undirected clique is insufficient. The remaining seven
rows have an ordered triple by [PR3420](https://github.com/CrocSwap/integer-mult-bounds/pull/3420).
The retained asymmetric two-block labels then produce the seven-row box.

## Why the matrix theorem holds

[PROOF.md](PROOF.md) gives a self-contained analytic argument, including
the retained seven-row lemma. Its new steps are:

1. A rank-at-most-two matrix with nonzero diagonal has an ordered block of
   at least half its rows. Order the projective column classes randomly;
   retain a row after its unique forbidden class. Every row is retained
   with probability at least one half.
2. An eleven-row counterexample cannot have repeated projective factor
   directions. The two-copy boundary forces an independent triple and
   six columns in a plane. Coordinate-zero counting divides those six
   columns into three proportional pairs. The supposed obstruction then
   forces their rank-at-most-two principal matrix to have three nonzero
   rank-one diagonal blocks, a contradiction.
3. With both sets of factor directions distinct, zero rows are distinct
   projective lines on eleven distinct points. A nonzero out-neighborhood
   has at most six vertices, or its ordered triple could be prefixed to
   form four. Each zero line therefore contains at least four points.
   Eleven lines would account for at least `11*choose(4,2)=66` point pairs,
   whereas only `choose(11,2)=55` exist. Distinct lines cannot count the
   same point pair.

There is no positivity, characteristic-zero or finite-census premise.
The rational box transfer separately uses actual 2-adic normalization to
prove that scalar zeros imply binary anchor orthogonality, plus the
explicit nonempty-tie hypothesis.

## Exact control fixture

Duplicate Aaron Wang/navinor's PR2978 paired core rows `(4,4,3)` times:

```text
P = [(-1,-3,0), (1,-1,-2), (3,3,3)]
Q = [( 1,-3,2), (3,-1,-2), (3,-1,2)]
```

The eleven-row product is `diag(8 J4,8 J4,12 J3)`, with rank three,
`gamma=0`, two ties on every row, source anchors `011` in the first two
groups and `111` in the third, and target anchors all `011`. The constructor
returns a literal seven-row witness; the first two complete groups give
eight.

No witness can meet all three groups. Three retained representatives in
their actual order would have a lower-triangular binary label-dot matrix
with diagonal ones and rank three, but every target label lies in the
same two-dimensional space. Thus box is exactly eight. This verifies a
positive case and **does not establish sharpness of seven**.

## Reproduce

From the repository root with Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/fstar-eleven-line-floor
python3 -B scripts/research_package.py --package research/fstar-eleven-line-floor --check-only
python3 -B scripts/check_research_commit.py --package research/fstar-eleven-line-floor --check-source-history
```

The last command applies to the committed publication. `VERIFY.json`
registers normal and isolated/optimized replay with warnings treated as
errors. No third-party dependencies are needed; the author used CPython
3.12.15. The executable construction and finite semantic controls are
recorded in `RESULT.json`. They do not replace the analytic proof or
constitute formal verification of it.

The independent oracle is copied unchanged from corrected PR3393 at
`8e1e574fa68465dc0ec69d07852266b9597f9597`, exported through PR3420 at
`e2d39da9c7109f361d6cff677cf9f8eba51f3dd6`. `SOURCES.json` pins its original
Git blob and SHA256. It is reused checking code, not a newly independent
implementation. The theorem does not invoke that oracle. Bounded search
was discovery work only and is not a premise or published census.

## Coordination, attribution and limits

Canonical main and fork base: `6f100d4bb5083f8c35d96fd95a539811c62f245c`,
priority revision 6. The card baseline passed. `TASK.json` records this
handoff-first scope change, with status in the [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-19009289).
The complete overlap snapshot covered 336 open PRs, 2,761 closed/merged PRs,
and 2,262 Discussion records, fetched 2026-10-18 01:18:23–01:19:20 UTC.
Coverage was titles, bodies and local package prose, not every PR code diff.
Earlier eleven-row results concerned named fixtures; absence of a matching
claim is not proof of novelty.

Prepared by Sagar Thakrar with substantial OpenAI Codex assistance, including
separate proof, control and review agents. Same-session agent review is not
human acceptance. New work is Apache-2.0. DreamingOfClouds retains the
PR1590/2111 F-star/certificate attribution; Aaron Wang/navinor retains the
PR2914/2978/3031 directed-box, SG and core attribution. Arham Tahir's PR3105
joint-triple classification is related work, not a premise. The seven-row
lemma is retained from PR3420, and the two-block transfer from PR3409/3420.

This result does not handle zero-tie rows, settle general F-star, admit a
physical supplier, change the selected frontier, or improve κ. No formal
proof, independent human acceptance, or literature-priority claim is made.

## Open next questions

Do twelve admitted rational lines always have box at least eight? Start
with the `(4,4,4)` core duplication, whose box is exactly eight. Seek
disjoint ordered blocks with total size eight, allowing `4+4` or `5+3`.
The present theorem supplies one four-block; its eight-row complement is
guaranteed only a triple. A failure of this sufficient matrix condition
would not itself be a box counterexample.
