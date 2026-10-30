# The dimension-4 transfer leaves X102 on 365 edges

**Partial. No new exponent.**

The dimension-3 transfer leaves X102 on 52 edges. Dimension 4 grants X102 no
new read. The same interval bounds, now tested at dimension 4, add 313 edges.
Those edges leave from 98 departure slots on 74 channels. The resulting count
is 365.

## What was executed

The compatible edges and the relations through dimension 4 are recomputed
from the frozen witness and certificate. Dimensions 1 through 3 reproduce the
incoming 52-edge state. The dimension-4 transfer then spreads that state. The
dimension-5 relation is not built. [RESULT.json](RESULT.json) records a
SHA-256 digest of the 365 reached edge indices.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
transfer. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the witness, the certificate and the
archived transfer rule. No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-fourth-transfer/verify.py
python3.12 -B research/p104-fourth-transfer/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-fourth-transfer
```

The replay finishes in a few seconds.

## Open next questions

The dimension-4 transfer leaves the count at 365. The next reading is the
dimension-5 transfer, whose archived layer says 1,725 edges have reached
X102.

## Credit

Nick Petalas supplied the archived transfer rule in the pooled-cut checker and
the fixed endpoint covers in the certificate. The frozen channel witness
retains its own predecessor credit.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
