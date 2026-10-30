# The forward and backward cones do not meet

**Partial. No new exponent.**

The dimension-5 transfer leaves X102 on 1,725 edges. Y71 has 12 dimension-8
writers: 2 through arrival slot 142 and 10 through arrival slot 143, the two
arrival slots of channel 71. Expanding through the dimension-8 relation leaves
those 12 edges in place. Dimension 7 raises the cone to 22 edges, and
dimension 6 raises it to 37. The intersection with the 1,725 forward edges is
empty.

The 37 backward edges leave from departure slots 41 (2), 43 (2), 54 (4),
131 (2), 135 (4), 145 (4), 146 (2), 149 (1), 155 (4), 159 (4), 171 (4) and
194 (4).

## What was executed

Both cones are recomputed from the frozen witness and certificate. The forward
edges are compared with the archived forward-cone list, and the backward edges
with the archived backward-cone list. The other required pairs are not
accumulated. [RESULT.json](RESULT.json) records a SHA-256 digest of the 37
backward edge indices.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
intersection. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the witness, the certificate and the
archived transfer rule. No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-cone-cut/verify.py
python3.12 -B research/p104-cone-cut/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-cone-cut
```

The replay finishes in a few seconds.

## Open next questions

This intersection concerns the pair Y71 from X102. The next reading is which
required pairs the same recurrence misses.

## Credit

Nick Petalas supplied the archived transfer rule in the pooled-cut checker and
the fixed endpoint covers in the certificate. The frozen channel witness
retains its own predecessor credit.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
