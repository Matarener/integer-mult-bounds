# The declared V45 group pays only when all four helpers drop together

**Partial. No new exponent.**

The rank-7 archive lists one shared subspace

```text
W = ⟨256, 128, 64, 35, 16, 11, 5⟩ = E_7 ∩ E_42 ∩ E_45
```

for helpers 249, 251, 265 and 267. With the producer's parity test, `E_n` is
the set of nine-bit vectors whose bitwise-and with `n` has even weight.
Those three normals satisfy `7 XOR 42 = 45`, so they cut out a rank-7 space,
and the listed basis spans it.

The price table's margin is `-delta - k * 2091300`. Every one-helper subset
has margin `-53141`. Every two-helper and three-helper subset is also
negative. The four-helper subset has margin `+22972`. Dropping any one helper
from that subset costs exactly `25371`, which is `c_1 - 2091300`.

The selected kappa remains
`836330098538459/500000000000000000`. The archive headline is a different
number. This check does not replay the literal word, the cleanup, the
chronology or either supplier cap.

## What was executed

The checker rebuilds the intersection by the parity test and recomputes every
V45 subset margin from its declared delta. It does not import the producer.

## Scope and evidence

Original card: `independent-moment`, priority revision 6, refined to the V45
subspace and its declared subset margins. [TASK.json](TASK.json) records the
scope change. [RESULT.json](RESULT.json) is the executed receipt and is not
rewritten. [SOURCES.json](SOURCES.json) pins the archive note, the producer
text, the price table, the family status and the selected record. No selected
frontier file changes.

Upstream checkpoint: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority
revision 6, checked 2026-10-18 05:14 UTC. Catalogue and selected record match
that commit. Handoff discussion #1166, through the PR3536 note at 2026-10-18
05:07 UTC, was released work. Draw seed `746e1554aeb802fed04786675ba8de6e`,
track `independent-verification`, second card `independent-moment`.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/rank7-v45-margin/verify.py
python3.12 -B research/rank7-v45-margin/test_verify.py
python3.12 -B scripts/research_package.py --package research/rank7-v45-margin
```

The replay finishes in under a second.

## Open next questions

The subspace identity and the declared subset signs are checked. Replaying the
literal word, the cleanup, the chronology and both supplier caps is the
admission this audit stops before.

## Credit

The rank-7 note and its producer state the V45 group, the parity test and the
headline. The price table states the subset deltas. The family status states
that this archive is not the selected result. Dugongue / mdumitrean and the
predecessor chain named there retain the construction.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
