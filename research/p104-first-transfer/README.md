# The dimension-1 transfer leaves X102 on 16 edges

**Partial. No new exponent.**

X102 has 16 dimension-1 readers among the 2,309 compatible edges. Those 16
edges all use X102's initial line, and the dimension-1 relation joins exactly
the edges on one line. One read-first transfer therefore leaves X102 on those
same 16 edges.

## What was executed

The compatible edges and dimension-1 reads are recomputed from the frozen
witness and certificate. The transfer seeds each reader and spreads its signal
along the dimension-1 interval relation. The dimension-2 relation is not built.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
transfer. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the witness, the certificate and the
archived transfer rule. No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-first-transfer/verify.py
python3.12 -B research/p104-first-transfer/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-first-transfer
```

The replay finishes in under a second.

## Open next questions

The dimension-1 transfer leaves the count at 16. The next reading is the
dimension-2 transfer, whose archived layer says 25 edges have reached X102.

## Credit

Nick Petalas supplied the archived transfer rule in the pooled-cut checker and
the fixed endpoint covers in the certificate. The frozen channel witness
retains its own predecessor credit.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
