# The dimension-2 transfer leaves X102 on 25 edges

**Partial. No new exponent.**

The dimension-1 transfer leaves X102 on 16 edges: 7 through departure slot 204
and 9 through departure slot 205. Dimension 2 grants X102 no new read. Slot
165, the second departure of channel 82, uses the same plane as slot 205, so
the transfer adds slot 165's 9 edges. Slot 204's plane is not shared, and its
7 edges stay in place. The resulting count is 25.

## What was executed

The compatible edges and both relations are recomputed from the frozen witness
and certificate. The dimension-1 transfer produces the incoming 16-edge state.
The dimension-2 transfer then spreads that state across equal departure
planes. The dimension-3 relation is not built.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
transfer. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the witness, the certificate and the
archived transfer rule. No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-plane-transfer/verify.py
python3.12 -B research/p104-plane-transfer/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-plane-transfer
```

The replay finishes in under a second.

## Open next questions

The dimension-2 transfer leaves the count at 25. The next reading is the
dimension-3 transfer, whose archived layer says 52 edges have reached X102.

## Credit

Nick Petalas supplied the archived transfer rule in the pooled-cut checker and
the fixed endpoint covers in the certificate. The frozen channel witness
retains its own predecessor credit.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
