# X102 has 16 dimension-1 readers

**Partial. No new exponent.**

X102 is the only channel whose initial frame equals its own line. That line
belongs to departure slots 204 and 205, and both slots are compatible. They
lie on 16 of the 2,309 compatible edges. Under the archived contact rule those
16 edges are X102's dimension-1 readers. Dimensions 2 through 8 contribute no
further readers.

## What was executed

The channel paths, departure and arrival covers, and compatible edges are
recomputed from the frozen witness and certificate. A reader is an edge whose
bound contains a frame of X102 at that dimension. The read-first transfer is
not run.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
reader count. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the witness, the certificate and the
archived contact rule. No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-initial-readers/verify.py
python3.12 -B research/p104-initial-readers/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-initial-readers
```

The replay finishes in under a second.

## Open next questions

The 16 readers are the start of the forward cone. The next reading is how
many edges contain X102 after one read-first transfer.

## Credit

Nick Petalas supplied the archived contact rule in the pooled-cut checker and
the fixed endpoint covers in the certificate. The frozen channel witness
retains its own predecessor credit.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
