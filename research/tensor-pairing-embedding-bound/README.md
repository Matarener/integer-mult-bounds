# Exact embedding boundary for PR3895's tensor pairing

The full sixteen-port pairing in [PR3895](https://github.com/CrocSwap/integer-mult-bounds/pull/3895)
cannot embed in a nine-bit bilinear label alphabet. Under an **injective common
E8 root-line map**, the largest principal restriction has **exactly eight
vertices**. We provide an attaining witness in the actual selected P112 ports.
That witness preserves only the binary pairing: restricting the tensor decoder
to it fails a required scalar zero coefficient.

This closes a specific prerequisite left open by the predecessor's ideal
rank-16 screen. It is a scoped obstruction, not a new decoder, COPY-cost floor,
supplier, kappa improvement or complete multiplication theorem.

## Exact scope and evidence

[PROOF.md](PROOF.md) gives the universal argument. [verify.py](verify.py)
corroborates it with exact integer/rational arithmetic:

- Reconstruct `B4=(G0^tensor4+J) mod2=P16+J16`, and check rank sixteen.
  This full-matrix obstruction allows different source/reader maps.
- Check all 65,536 principal restrictions against the exact rank formula.
  The largest size passing the rank-at-most-nine screen is twelve; this is
  **not** an injective twelve-label embedding assertion.
- Check an abstract nine-bit, nine-distinct-label example which E8 geometry
  excludes. The positive-definite matching Gram proof gives the E8 cap eight.
- Rebuild E8/P112 independently and authenticate all 12,544 pairings against
  the selected archive, using PR3566's explicit root-to-port bijection.
- Check the eight-root, four-pair attaining witness and a masked-zero scalar
  mismatch, including the favorable global normalization of the tensor Gram.
- Exercise malformed-map, pairing, label and identity controls. Normal and
  optimized Python modes use explicit checks rather than assertions.

The eight-vertex theorem requires one common map and distinct root lines. It
does not bound principal restrictions under different source/reader maps,
repeated labels, splitting, recoding, or a changed coefficient identity. The
witness establishes the maximum cardinality; it does not classify all smaller
embeddable restrictions. The proof is written mathematics, not proof-assistant
verification. AI review is not independent human review.

## Reproduce

From the repository root, with Python 3.12 and no third-party dependencies:

```sh
python3.12 -I -B research/tensor-pairing-embedding-bound/verify.py
python3.12 -I -O -B research/tensor-pairing-embedding-bound/verify.py
python3.12 -I -B scripts/research_package.py --package research/tensor-pairing-embedding-bound
python3.12 -B scripts/check_research_commit.py --package research/tensor-pairing-embedding-bound --check-source-history
```

`--write` regenerates [RESULT.json](RESULT.json); ordinary replay is read-only.
The retained sources are parsed or hashed as data, never executed. The selected
archive is an existing main-branch dependency; it is not duplicated here.
Its compressed Git/SHA256 identity and the decompressed canonical-word digest
are both checked. `PORTS.json` is a small derived projection, revalidated on
each run against that payload and the retained PR3566 source literal.

## Sources, overlap and credit

Scientific base: canonical main `20ecf2891d80b5acf18d980b2164fb44ea7faa90`,
priority revision 6; selected conditional kappa `0.001672660197076918` remains
unchanged. [TASK.json](TASK.json) records the task refinement, scope, checkpoint
and overlap coverage; [SOURCES.json](SOURCES.json) pins all consumed sources.
Coordination: [Discussion3925](https://github.com/CrocSwap/integer-mult-bounds/discussions/3925).

Credit **homelab-05 / 1337isnot1337, PR3895** for the exact two-root tensor
decoder, its pairing and its open embedding question; **Gonzalo Mier, PR3566**
for the selected root-to-port bijection; **Adam Gall**, the retained
`p112-tetrad-local-decoder` package, for the P112 root/frame convention; and
**DreamingOfClouds / PR717**, **themilkman216 / PR968**, **woklerx / PR1077**
and the retained E8 decoder lineage. **Hanson Sun / bbMisk, PR1633** supplies
related excess-rank scope, not the theorem used here. PR3567's tetrad
effective-rank result and PR3039's charged block-climb screen are different
questions. No general fixed-alphabet effective-rank result is claimed.

The two retained Python files preserve their predecessor bytes. Their original
substantial OpenAI Codex assistance and Apache-2.0 attribution remain. This
new proof, checker and review package were prepared by **ToikY with substantial
OpenAI Codex assistance**, including bounded AI subagent implementation and
independent proof review. No mathematical-priority claim or independent human
review is made. New material is Apache-2.0.

## Open next questions

A useful continuation must specify a changed pairing/consumer contract before
pricing it: separate maps or recoding may evade the common-map theorem, but
the full literal sixteen-by-sixteen pairing still cannot fit nine-bit labels.
First verify every constrained scalar coefficient of such a changed identity.
Then account for arbitrary dirty inputs, frames, restoration, accumulation,
owner chronology, hosting, precision/tape and the complete recursive bill.
Those obligations, the selected all-size/compiler and analytic assumptions,
and bit H1-H5 remain open. This package supplies none of those interfaces.
