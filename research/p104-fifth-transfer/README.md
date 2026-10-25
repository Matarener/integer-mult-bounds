# The dimension-5 transfer leaves X102 on 1,725 edges

**Partial. No new exponent.**

The dimension-4 transfer leaves X102 on 365 edges. Dimension 5 grants X102 no
new read. The interval transfer adds 1,360 edges from 172 departure slots on
97 channels. The resulting 1,725 edges are the archived forward cone.

## What was executed

The compatible edges and the relations through dimension 5 are recomputed
from the frozen witness and certificate. Dimensions 1 through 4 reproduce the
incoming 365-edge state. The dimension-5 transfer then spreads that state.
The reached edges are compared with the archived forward-cone list. The
backward cone is not built. [RESULT.json](RESULT.json) records a SHA-256
digest of the 1,725 reached edge indices.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
transfer. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the witness, the certificate and the
archived transfer rule. No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-fifth-transfer/verify.py
python3.12 -B research/p104-fifth-transfer/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-fifth-transfer
```

The replay finishes in a few seconds.

## Open next questions

These 1,725 edges are the forward cone. The next reading is whether they meet
the backward cone.

## Credit

Nick Petalas supplied the archived transfer rule in the pooled-cut checker and
the fixed endpoint covers in the certificate. The frozen channel witness
retains its own predecessor credit.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
