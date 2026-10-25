# Register 274 holds -1/2 before its addition

**Partial. No new exponent.**

Immediately before event 19133, register 274 holds `-1/2` when register 359
starts at `1`. Event 18927 writes that value as `-2` times register 360,
which holds `1/4`. The addition at event 19133 multiplies register 274 by
`1/2` and contributes `-1/4` to register 280, which is `0` until then. The
data register contributes `0`. At the literal magnitude `256`, register 274
holds `-128`.

## What was executed

The trace applies the published scalar rules and stops before event 19133.
Register 274 changes once, at event 18927. The read of register 360 is the
same `1/4` recorded at its later use. The first half of register 103 is left
for the next reading.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
source value. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-leading-half/verify.py
python3.12 -B research/qq16-leading-half/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-leading-half
```

The replay finishes in under a second.

## Open next questions

Event 23507 takes register 103 from `0` to `-64`. The next reading is the
scalar value of register 343 immediately before that addition.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
