# The dimension-3 transfer leaves X102 on 52 edges

**Partial. No new exponent.**

The dimension-2 transfer leaves X102 on 25 edges, through departure slots 165,
204 and 205. Dimension 3 grants X102 no new read. The interval transfer adds
27 edges. Their departure slots and edge counts are 10 (4), 11 (1), 20 (1),
21 (1), 77 (2), 78 (1), 79 (1), 86 (2), 87 (1), 172 (2), 173 (4), 202 (3) and
203 (4). The resulting count is 52.

## What was executed

The compatible edges and the dimension-1, dimension-2 and dimension-3
relations are recomputed from the frozen witness and certificate. The first
two transfers reproduce the incoming 25-edge state. The dimension-3 transfer
then spreads that state. The dimension-4 relation is not built.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
transfer. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the witness, the certificate and the
archived transfer rule. No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-third-transfer/verify.py
python3.12 -B research/p104-third-transfer/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-third-transfer
```

The replay finishes in under a second.

## Open next questions

The dimension-3 transfer leaves the count at 52. The next reading is the
dimension-4 transfer, whose archived layer says 365 edges have reached X102.

## Credit

Nick Petalas supplied the archived transfer rule in the pooled-cut checker and
the fixed endpoint covers in the certificate. The frozen channel witness
retains its own predecessor credit.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
