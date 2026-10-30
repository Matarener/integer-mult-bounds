# Three-channel gauges do not reduce the rank-34 plane invoice

**Scoped negative result. No new supplier or κ.** The exact PR3335 scalar fit
has a full-plane one-total invoice of 224. We tested whether a small change of
basis among its 34 latent channels can mix nonorthogonal plane groups, preserve
the exact scalar fitting matrix, and lower that invoice. No signed-ternary
change of basis acting on any three channels improves the price.

## Exact question and result

Let `K = A A^T` be the 112-by-112 rational fitting matrix from PR3335's 34
disjoint support indicators. For any triple of channels, replace the three
source columns by `A S` and the three reader rows by `S^-1 A^T`, leaving the
other 31 channels fixed. This preserves `K` exactly for every invertible
`S` over `Q`, while allowing source and reader supports to mix across plane
groups. Each transformed term is priced on the complete two-dimensional plane
spans touched by its source and reader supports, using the inherited exact
`F2` pairing-rank tariff.

The exhaustive finite domain is:

- all `3^9 = 19,683` matrices with entries in `{-1,0,1}`;
- all `11,808` matrices nonsingular over `Q`;
- all `396` distinct source-column / inverse-reader support maps they realize;
- every one of the `binom(34,3) = 5,984` channel triples.

This prices **2,369,664** triple/support-map cases. The minimum invoice remains
224. The local invoice delta histogram is:

| Delta | Cases |
| ---: | ---: |
| 0 | 520,608 |
| 1 | 332,352 |
| 2 | 155,148 |
| 3 | 237,912 |
| 4 | 175,596 |
| 5 | 242,424 |
| 6 | 171,324 |
| 7 | 220,680 |
| 8 | 70,320 |
| 9 | 158,016 |
| 10 | 20,916 |
| 11 | 48,732 |
| 12 | 7,848 |
| 13 | 7,692 |
| 14 | 96 |

There are no negative deltas. A separate exact rational fixture with determinant
2 checks all 12,544 entries of the scalar matrix after a nontrivial change of
basis; using `S` instead of `S^-1` is rejected. The verifier reconstructs the
support-map census and full invoice from the pinned inputs.

## What the result rules out

This closes one natural way to escape the 224-unit **orthogonal-local** floor:
re-basing any one triple of the published 34 channels with signed-ternary
coefficients. It does not prove a floor for arbitrary scalar factorizations.
Larger overlapping blocks, sequential gauges whose combined matrix lies
outside this finite family, arbitrary rational coefficient matrices, and
changed copy contracts remain open.

The nearest concurrent results are [PR3463](https://github.com/CrocSwap/integer-mult-bounds/pull/3463),
which bounds pair-span gauges, and [PR3472](https://github.com/CrocSwap/integer-mult-bounds/pull/3472),
which bounds one common external-query perturbation. This census uses neither
architecture: it changes basis inside the fixed 34-channel PR3335 factorization
and re-prices each resulting source/reader term. It does not close the broader
jointly recoded-block question left open there.

The 224 tariff already exceeds the 160-unit ideal plane-port allowance in the
retained zero-overhead screen. A successful local reduction would have been a
useful step toward that gate; this negative result does not establish or rule
out a complete supplier. Native gathering, dirty-helper restoration,
chronological ownership, consumer, precision, all-size compilation, the bit
supplier and the selected κ remain unaddressed.

## Reproduce

From repository root, with Python 3.12 and the standard library:

```sh
python3.12 -B research/paired-plane-rank34-triple-gauge/verify.py
python3.12 -O -B research/paired-plane-rank34-triple-gauge/verify.py
python3.12 -B -m unittest discover -s research/paired-plane-rank34-triple-gauge -p 'test_verify.py'
python3.12 -B scripts/research_package.py --package research/paired-plane-rank34-triple-gauge
```

The exact input hashes, source heads and support-map witnesses are in
[SOURCES.json](SOURCES.json) and [CERTIFICATE.json](CERTIFICATE.json). The
selected archive supplies all 112 port labels. The rematched supports are the
byte-pinned PR3335 certificate retained by the paired-plane rank-34 audit.
No predecessor verifier is imported. The registered replay passed on CPython
3.12.15, including both normal and optimized exhaustive runs and the focused
controls; the package metadata and source pins also pass.

## Open next questions

Can a four-channel or overlapping multi-block rational gauge reduce the
invoice? A useful next step is to build an interaction graph from the zero-delta
triples and use it to screen four-channel support/inverse patterns before any
larger matrix census. Even a cheaper scalar factorization would still need a
complete native decoder and consumer before it could affect κ. The exact
question and blockers are recorded in [TASK.json](TASK.json).

## Credit

Mark / Matarener and Claude via Claude Code supplied the rank-34 matching,
supports and discovery in PR3335. Arham-Tahir64's paired-plane rank-34 copy
audit supplies the independent exact mask check, full-plane tariff, and the
open boundary at nonorthogonal cross-group terms; its authorship and predecessor
credits remain intact. The selected labels retain the PR1094 lineage. This
scoped gauge census was prepared by OpenAI Codex with substantial AI assistance;
no independent human review or formal proof assistant is claimed. Apache-2.0.
