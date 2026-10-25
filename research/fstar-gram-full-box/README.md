# Full boxes for rational three-total Gram factorizations

For every rational factorization **`M=P P^T` with three columns**, if each
row has a nonempty canonical tied set, its retained directed anchor box is
full: **`box=n`**, for any number of rows.

[PROOF.md](PROOF.md) gives the complete argument. A common global scaling
makes the factor rows 2-adically integral, and their odd supports are exactly
the original canonical tied sets. Rows with two odd coordinates split into
two classes according to the product of those coordinates modulo four.
Neither class has an internal zero entry. Place all odd-tied rows between
these classes and apply the retained asymmetric sub-anchor labels. Every
forward-zero constraint then follows directly from the canonical scope
identity.

This is a theorem about **Gram factorizations**, not arbitrary symmetric
matrices. Canonical normalization can make the two factor arrays unequal;
the proof handles that explicitly and never renormalizes a kept subset.
Aaron Wang's retained three-row core already gives a symmetric positive
definite matrix with box two for its supplied asymmetric factors; it is
credited as a scope control, not presented as a new counterexample.

## A sufficient condition for general rational factors

For general `M=P Q^T`, retain every odd-tied row and every row satisfying

```text
A_i = B_i,  |A_i| = 2,  v2(M_ii) = gamma + 1.
```

All those rows can be kept simultaneously. The diagonal valuation condition
is relative to the original normalization `gamma`. Matched two-bit anchors
without this condition do not suffice: the explicit four-row rational
fixture in the proof has matched anchors, nonzero diagonal and box exactly
three. A separate Gram example has `A!=B`, and a scaled-row example shows
why nonempty canonical ties cannot be dropped.

## Evidence and reproduction

From the repository root, with CPython 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/fstar-gram-full-box
```

[VERIFY.json](VERIFY.json) registers the executable checks and
[RESULT.json](RESULT.json) records their exact outcomes. The checker uses
exact rational normalization, modulo-four arithmetic and the retained
definition-level witness interface. [SOURCES.json](SOURCES.json) identifies
the exact source and provenance dependencies. The universal result comes
from the written proof, not extrapolation from finite cases.

The replay covers all 96 admitted modulo-four factor types and their 9,216
ordered pairs, eight Gram fixture families, three 100-row asymmetric
families, and partial retention. Nine failure controls exercise the source
pin and mathematical hypotheses. Exhaustive maximum-box searches are
limited to the four-, three- and two-row boundary examples.

Validation on 2026-10-18 used CPython 3.12.15 on Linux: both registered
commands passed, including `-I -O -B -Werror`. The frozen oracle was also
compared byte for byte with its pinned original Git source. No solver,
third-party Python package or proof assistant is needed for this replay.

## Open next questions

The unrestricted asymmetric rational case remains open. A useful next step
is to classify which unmatched two-tied anchor types, or higher-valuation
matched rows, can be inserted into the three-block witness while preserving
the actual directed-zero constraints. Start with the four-row box-three
fixture and the original canonical labels; arbitrary binary parity patterns
are not substitutes for realizable rational factors.

The result does not supply native COPY admissibility, a physical controller,
a supplier invoice, an outer multiplication theorem or a new kappa. It is
an elementary scoped proof with executable evidence, not a proof-assistant
certificate or independent human approval. The selected frontier is unchanged.

## Attribution

Prepared by Sagar Thakrar with substantial OpenAI Codex assistance, including
separate proof, checker and review agents. Apache-2.0.

Credit Aaron Wang/navinor's root-unit/anchor-decoder framework and box
definitions through [PR2914](https://github.com/CrocSwap/integer-mult-bounds/pull/2914)
and [PR3031](https://github.com/CrocSwap/integer-mult-bounds/pull/3031),
DreamingOfClouds's F-star/certificate lineage, and the retained predecessor
notices. The labeling transfer is inherited from
[PR3409](https://github.com/CrocSwap/integer-mult-bounds/pull/3409),
[PR3420](https://github.com/CrocSwap/integer-mult-bounds/pull/3420) and
[PR3445](https://github.com/CrocSwap/integer-mult-bounds/pull/3445).
[PR3454](https://github.com/CrocSwap/integer-mult-bounds/pull/3454) already
checks the known Yu--Oh Gram example; its ray construction is credited to
Sixia Yu and C. H. Oh. This contribution proves the stated general Gram
case and sufficient asymmetric row criterion, rather than reclaiming those
definitions, labels or constructions.

Canonical coordination:
[Discussion1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-19015031).
