# The literal recurrence misses the same required pair

**Partial. No new exponent.**

The fixed-cover correction has 4,992 required pairs. The eight-layer literal
quotient recurrence reaches 4,991 of them. The only missing pair is target 71
from source 102. Its matrix entry is `-4`, so the coefficient is `-1/2`.

At every dimension the literal relation is the same adjacency as the interval
relation, and its digest equals the archived layer digest. The two engines
therefore carry the same sources. This comparison does not close the
fixed-cover contract, and it does not change the selected frontier.

## What was executed

Direct frame contacts and all eight literal layers are recomputed from the
frozen witness, certificate and fixture. Each literal relation is compared
with an independent interval relation and with the archived digest. Every
source bit is accumulated, and each required nonzero entry is checked against
the output mask. The backward cone is not rebuilt.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
literal missing-pair list. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the witness, the fixture, the certificate
and the archived relation rules. No selected frontier file changes.

Upstream checkpoint: `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority
revision 6, checked 2026-10-18 04:23 UTC. Canonical main and the fork main
were at that commit. The family record still asks for review of the submitted
fixed-cover support cut before treating that contract as closed.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-literal-missing/verify.py
python3.12 -B research/p104-literal-missing/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-literal-missing
```

The replay finishes in a few seconds.

## Open next questions

The literal and interval relations are the same adjacency at all eight
dimensions, and both match the archived digests. Another pass over this cut
would repeat that adjacency.

## Credit

Nick Petalas supplied the archived literal and interval rules in the
pooled-cut checker and the fixed endpoint covers in the certificate. The
frozen channel witness and fixture retain their own predecessor credit.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
