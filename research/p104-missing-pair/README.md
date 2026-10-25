# The interval recurrence misses one required pair

**Partial. No new exponent.**

The fixed-cover correction has 4,992 required pairs. The eight-layer interval
recurrence reaches 4,991 of them. The only missing pair is target 71 from
source 102. Its matrix entry is `-4`, so the coefficient is `-1/2`.

## What was executed

Direct frame contacts and all eight interval layers are recomputed from the
frozen witness, certificate and fixture. Every source bit is accumulated, and
each required nonzero entry is checked against the output mask. The literal
quotient engine is not run.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
missing-pair list. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the witness, the fixture, the certificate
and the archived output rule. No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-missing-pair/verify.py
python3.12 -B research/p104-missing-pair/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-missing-pair
```

The replay finishes in a few seconds.

## Open next questions

The interval engine misses one pair. The next reading is whether the literal
contact engine misses that same pair.

## Credit

Nick Petalas supplied the archived output rule in the pooled-cut checker and
the fixed endpoint covers in the certificate. The frozen channel witness and
fixture retain their own predecessor credit.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
