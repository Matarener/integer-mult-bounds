# Eight-line anchor-box floor

For rational `P,Q` with eight rows and three columns, `M=P Q^T`, nonzero
diagonal, and canonical `tau_i>=1`, **`box(M)>=5`**. This answers the next
threshold question in
[PR3393](https://github.com/CrocSwap/integer-mult-bounds/pull/3393).
Sharpness at five is not established.

[PROOF.md](PROOF.md) proves a stronger matrix statement: every real
eight-by-eight matrix of rank at most three with nonzero diagonal has distinct
indices `(i,j,k)` with all three forward entries `M_ij,M_ik,M_jk` nonzero.
An independent triple would give a rank-basis identity forcing the other five
vertices to be independent, a contradiction. Otherwise neighborhood counts
eliminate bidirectional nonzero pairs. Eight associated rank-one matrices
would then span a positive eight-dimensional space for the trace form on
three-by-three real matrices, whose positive index is six.

An ordered triple and a disjoint nonzero pair become a five-line box witness:
use full source anchors and tied unit target labels in the first block, then
tied unit source labels and full target anchors in the second. The directed
zero constraints between the blocks are precisely the original SG implication.
This permits asymmetric labels and needs no anchor-type census. A short
corollary also gives the six-line floor four from two disjoint nonzero edges.

## Exact evidence

The working rational fixture duplicates Aaron Wang's PR2978 core with block
sizes `3,3,2`:

```
P0 = [(-1,-3,0), (1,-1,-2), (3,3,3)]
Q0 = [(1,-3,2),  (3,-1,-2), (3,-1,2)]
M  = diag(8 J3, 8 J3, 12 J2).
```

It has rank three, `gamma=0`, and every tied count is two. Its box is **six**:
two size-three blocks give six kept lines, while every seven-set meets all
three blocks and forces a triangular rank-three label minor inside a common
two-dimensional target space. This is a positive control, not a sharpness
example for the lower bound five.

`verify.py` constructs the ordered blocks using exact arithmetic and checks
their labels both literally and with the unchanged target-first Gaussian
oracle exported from corrected PR3393 head
`8e1e574fa68465dc0ec69d07852266b9597f9597`. The export is authenticated before
execution. Controls exercise the directed-cycle boundary, rank-four exclusion,
SG/nonempty-tie/diagonal admission, the rank-basis identity, and the distinction
between symmetric and skew trace directions. [RESULT.json](RESULT.json)
records finite checks; the general theorem rests on the written proof.

From the repository root, with Python 3.12 (tested with 3.12.15):

```sh
python3 -B scripts/research_package.py --package research/fstar-eight-line-floor --check-only
python3.12 -B scripts/research_package.py --package research/fstar-eight-line-floor
```

Normal and isolated optimized replays are registered. There are no third-party
Python dependencies. Exact source history and hashes are in
[SOURCES.json](SOURCES.json); the selected record and task catalogue are
historical provenance. Development searches are not proof premises or claims
of an exhaustive rational census.

## Scope

The abstract result needs real rank at most three, nonzero diagonal, nonempty
tied sets and SG. Canonical rational three-total factors satisfy SG through
their actual 2-adic normalization. The trace argument uses real positivity;
no arbitrary-field extension is asserted. The proof is analytic, not formally
machine verified or independently reviewed by a human.

This is a scoped box theorem. The full F-star conjecture, complete multiplication
theorem, physical controller/supplier admission and selected kappa are unchanged.
The explicitly changed `independent-moment` scope, baseline, stop rule and next
question are recorded in [TASK.json](TASK.json). The canonical investigation is
[Discussion1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-19008770).

## Open next questions

Does `v=9` force six kept lines? A sufficient next target is two disjoint
transitive nonzero triples. Start from the `3,3,3` three-block duplication,
which has box six. One arbitrarily chosen triple can leave a six-line matrix
with no transitive triple, so the current argument does not answer this
question. Choosing a better triple or using further anchor information needs
a new argument; the matrix condition is sufficient, not necessary.

## Attribution

New work by **Sagar Thakrar with substantial OpenAI Codex assistance**, including
separate proof, exact-control and review agents. Separate AI runs are not
independent human review. New work is Apache-2.0.

Aaron Wang/navinor supplied the directed sub-anchor box, SG and valuation
lineage through [PR2914](https://github.com/CrocSwap/integer-mult-bounds/pull/2914)
and [PR3031](https://github.com/CrocSwap/integer-mult-bounds/pull/3031), and the
three-line core in [PR2978](https://github.com/CrocSwap/integer-mult-bounds/pull/2978).
DreamingOfClouds supplied the F-star/certificate origins and earlier fixtures in
[PR1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590) and
[PR2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111).
Arham Tahir's [PR3105](https://github.com/CrocSwap/integer-mult-bounds/pull/3105)
gave the earlier joint triple classification. Those contributors retain their
source-specific assistance disclosures. The frozen independent oracle and the
six-line predecessor are Sagar Thakrar's
[PR3393](https://github.com/CrocSwap/integer-mult-bounds/pull/3393).
