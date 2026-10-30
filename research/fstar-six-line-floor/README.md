# Sharp six-line anchor-box floor

For rational `P,Q` with six rows and three columns, `M=P Q^T`, nonzero
diagonal, and canonical tied counts `tau_i>=1`, **`box(M)>=4`**.
[PROOF.md](PROOF.md) gives a complete analytic argument for the directed,
ordered sub-anchor box definition. The bound is sharp. This answers the first
open question in [PR3031](https://github.com/CrocSwap/integer-mult-bounds/pull/3031)
and the six-line follow-up in
[PR3332](https://github.com/CrocSwap/integer-mult-bounds/pull/3332).

The proof restricts the possible numbers of singleton tied sets to zero through
three. Unit-label graph arguments cover most cases; two remaining configurations
use the fact that proportional primitive rational rows have equal binary
anchors, and that two independent factor rows have a one-dimensional
annihilator. It does not enumerate all directed zero patterns or assume that
every binary pattern satisfying the zero-parity implication is realizable.

## Sharp fixture

Duplicate each row of Aaron Wang's PR2978 three-line core twice:

```
P0 = [(-1,-3,0), (1,-1,-2), (3,3,3)]
Q0 = [(1,-3,2),  (3,-1,-2), (3,-1,2)]
M  = diag(8 J2, 8 J2, 12 J2).
```

Here `rank(M)=3`, `gamma=0`,
`A=[3,3,3,3,7,7]`, `B=[3,3,3,3,3,3]`, and every `tau_i=2`.
Keep the first two blocks, giving each block a different unit label: this
keeps four lines. Every five-set meets all three blocks. Representatives from
those blocks would yield a triangular three-by-three label matrix with unit
diagonal, but every target label belongs to a common two-dimensional binary
space. Thus five cannot be kept. The independent exact oracle also returns
`box=4`.

## Evidence and reproduction

`independent_box.py` fixes target labels, solves restricted binary affine
systems, and recursively chooses a compatible source order. It was written
separately from the predecessor's source-label enumeration and completion DP.
`verify.py` authenticates the unchanged predecessor bytes before using them for
source agreement; the independent oracle does not import predecessor code.
The executable checks are finite evidence and controls, not formal verification
of the general proof.

The receipt checks 20,136 restricted affine systems against direct submask
truth enumeration. Controls reject a wrong forward order, an out-of-anchor
label with unchanged diagonal parity, a zero diagonal, a `tau=0` fixture, and
counterfeit predecessor code before execution. Exact signed rational column
rescalings and a global valuation shift preserve the expected anchors. An
abstract rank-six example has box two, recording why the rank-three premise
cannot be dropped. Both normal and isolated optimized replays are registered.

A separate exact rational fixture exercises repeated blocker types whose
actual rows differ: the even target rows span dimension two, so a common
annihilator cannot be inferred from matching types alone. The proof treats
this multiplicity case using a 2+2 witness or a rank-four contradiction.
The fixture checks the valid pair order and rejects its reversal.

From the repository root, using Python 3.12 (tested with 3.12.15):

```sh
python3 -B scripts/research_package.py --package research/fstar-six-line-floor --check-only
python3.12 -B scripts/research_package.py --package research/fstar-six-line-floor
```

There are no third-party Python dependencies. Source commits, blobs and hashes
are in [SOURCES.json](SOURCES.json). The catalogue and selected record are
historical provenance; the two frozen source exports are authenticated locally.
The independent rational normalization uses actual valuations, including zeros
and negative inputs; predecessor agreement is confined to bounded integer
fixtures and does not endorse its finite valuation sentinel for arbitrary input.

## Scope and limitations

This proves a scoped rational three-total box statement. It does not prove the
full F-star conjecture, a complete multiplication theorem, native COPY
admissibility, a controller or supplier invoice, or a new kappa. The selected
frontier is unchanged. The proof assumes nonzero diagonal and `tau_i>=1` on
every selected line; neither hypothesis is silently removed.

The same argument gives four kept lines in any larger instance satisfying
these hypotheses: restrict to six lines while retaining the original normalized
factor rows and anchors. Recomputing the anchors of the restriction is neither
required nor assumed. In particular this also supplies the conjectured
`floor(2v/3)` threshold at `v=7`.

Original card `independent-moment`, changed scope, selection rationale and
structured next question are recorded in [TASK.json](TASK.json). The canonical
investigation is [Discussion1317](https://github.com/CrocSwap/integer-mult-bounds/discussions/1317#discussioncomment-19008465).

## Open next questions

Does the floor reach five at `v=8`? Start with the three-block fixture having
block sizes `3,3,2`, then classify the failed five-line unit-label patterns.
This is the next threshold in `floor(2v/3)`; the present six-line case proof
does not establish it, and witnesses from separate subsets cannot simply be
combined. See the structured first step and blocker in `TASK.json`.

## Attribution

Prepared by **Sagar Thakrar with substantial OpenAI Codex assistance**, including
separate proof, checker and diagnostic agents. These are separate AI executions,
not independent human review. New work is Apache-2.0.

The box definition, valuation/scope identities and zero-digraph lineage are
Aaron Wang/navinor's work through
[PR2914](https://github.com/CrocSwap/integer-mult-bounds/pull/2914) and
[PR3031](https://github.com/CrocSwap/integer-mult-bounds/pull/3031); the sharp
core is from [PR2978](https://github.com/CrocSwap/integer-mult-bounds/pull/2978).
DreamingOfClouds introduced the F-star/certificate lineage in
[PR1590](https://github.com/CrocSwap/integer-mult-bounds/pull/1590) and the
fixtures in [PR2111](https://github.com/CrocSwap/integer-mult-bounds/pull/2111).
Arham Tahir's [PR3105](https://github.com/CrocSwap/integer-mult-bounds/pull/3105)
gave the earlier joint triple classification. The complete predecessor credit
and assistance disclosures remain in the unchanged
[PR3031 source README](inputs/pr3031-README.md#credit).
