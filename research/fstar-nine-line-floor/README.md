<!-- SPDX-License-Identifier: Apache-2.0 -->

# Sharp rational anchor-box floors: five at seven lines, six at nine

For rational three-total factorizations `M=P Q^T` with nonzero diagonal and
nonempty canonical tied sets on every line, this package proves
**box(M)>=6 at nine lines** and **box(M)>=5 at seven lines**. Both bounds
are attained by exact rational fixtures. Restricting to nine lines also
gives the required floor six at ten lines; use the original anchors when
restricting, rather than renormalizing the subset.

The general result is the analytic argument in [PROOF.md](PROOF.md).
The executable checks validate finite constructions and failure controls;
they are not an exhaustive matrix census or a formal proof.

## The new matrix argument

Over **any field**, a six-by-six matrix of rank at most three with nonzero
diagonal has either an ordered nonzero triple or an independent triple in
its undirected nonzero graph. An ordered nonzero block requires all its
forward off-diagonal entries to be nonzero; an undirected clique alone does
not suffice.

The six-row lemma uses a directed three-cycle minor. Its invertible case has
an entrywise nonzero inverse. Its singular case has rank two and a nullvector
with every coordinate nonzero. Rank reconstruction or the resulting factor
dependence forces a forbidden ordered triple among the remaining rows.

This implies that seven rows always contain an ordered nonzero triple. At
nine rows, an exchange across two independent triples proves the existence
of **two disjoint ordered blocks of sizes 3+3 or 4+2**. The proof classifies
three cross-intersecting bipartite edge families and uses their exact matrix
supports to force a fully nonzero four-block when exchanging triples fails.

The asymmetric label construction from [PR3409](https://github.com/CrocSwap/integer-mult-bounds/pull/3409)
then gives six box rows: put full source anchors and tied target units on
the first block, and tied source units and full target anchors on the second.
Actual scalar zeros imply binary anchor orthogonality by rational 2-adic
normalization. All cross-block constraints therefore hold.

The narrower condition “two disjoint ordered triples” is false on
`diag(J5,J2,J2)`. Its four-plus-two alternative works. This negative control
is not a counterexample to the box theorem.

## Sharp examples

Retain Aaron Wang/navinor's PR2978 rational core:

```text
P = [(-1,-3,0), (1,-1,-2), (3,3,3)]
Q = [( 1,-3,2), (3,-1,-2), (3,-1,2)]
```

Duplicate each paired row respectively `(3,3,3)` or `(3,2,2)` times. The
resulting scalar matrix is `diag(8 J_s,8 J_t,12 J_u)`, with rank three,
`gamma=0`, target anchors all `011`, source anchors `011` in the first two
blocks and `111` in the third, and exactly two tied coordinates per line.

No box can meet all three blocks: one retained representative per block
would give a triangular binary label-dot matrix with diagonal ones and rank
three, although all target labels lie in a two-dimensional space. The two
largest blocks attain the upper bound. Hence the nine-line example has box
exactly six, and the seven-line example has box exactly five.

## Reproduce

From the repository root with Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/fstar-nine-line-floor
python3 -B scripts/research_package.py --package research/fstar-nine-line-floor --check-only
python3 -B scripts/check_research_commit.py --package research/fstar-nine-line-floor --check-source-history
```

The last command applies to the committed publication. `VERIFY.json`
registers both normal replay and isolated, optimized replay with warnings
treated as errors. There are no third-party dependencies. The author used
CPython 3.12.15.

`verify.py` constructs the ordered blocks and compares literal box witnesses
with the frozen independent oracle. Controls cover directed order, the
rank/diagonal/tie/parity hypotheses, both cycle-minor branches, reconstruction
through both diagonal bases, the bipartite-family classification, and
counterfeit source rejection before execution. `RESULT.json` records the
finite receipt separately from the analytic theorem.

The oracle bytes come unchanged from corrected PR3393 at
`8e1e574fa68465dc0ec69d07852266b9597f9597`, exported through PR3409 at
`8758f9b5eb04f2914e874a39fc55770bcdab2dfa`. `SOURCES.json` pins their original
Git blob and SHA256; this is reused independent checking code, not a newly
independent implementation. The theorem itself does not invoke that oracle.

## Coordination, attribution and limits

Canonical main/fork base: `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority
revision6. The card baseline passed. This handoff-first scope change is
recorded in `TASK.json` and the [canonical claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-19009093).
The complete overlap snapshot covered 323 open PRs, 2,761 closed/merged PRs,
and 2,251 Discussion records, fetched 2026-10-18 00:56:50–00:57:46 UTC.
It covered titles, bodies and local package prose, not every PR code diff;
no match is not proof of novelty.

Prepared by Sagar Thakrar with substantial OpenAI Codex assistance, including
separate proof, control and review agents. Same-session agent review is not
human acceptance. New work is Apache-2.0. The F-star/certificate definitions
retain DreamingOfClouds's PR1590/2111 attribution; the directed box, SG and
sharp core retain Aaron Wang/navinor's PR2914/2978/3031 attribution. Related
joint-triple classification by Arham Tahir (PR3105) is not a premise here.
PR3332/3393/3409 supply the prior finite floors and two-block construction.

This settles the stated finite anchor-box thresholds under nonempty ties.
It does not settle general F-star, handle zero-tie rows, admit a physical
supplier, change the selected frontier, or improve κ. No formal proof,
independent human review, or literature-priority claim is made.

## Open next questions

1. Do eleven admitted rational lines always have box at least seven? Start
   with the `(4,4,3)` core duplication. A nonzero ordered four-block and the
   seven-row triple lemma would suffice, but existence of that four-block
   is not proved here.
2. Is the eight-line floor five sharp, or does every admitted instance have
   box at least six? The two-family version of the exchange step allows
   complementary two-edge matchings; the three-family argument does not
   directly resolve that case. Keep a failure of this sufficient matrix
   condition distinct from an actual box counterexample.
