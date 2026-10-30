# Register 357 returns the initial helper value

**Partial. No new exponent.**

Immediately before event 9564, register 357 holds `1` when register 359
starts at `1`. Event 9544 writes `-2` times register 359 into it while
register 359 still holds that initial `1`. Event 9561 scales the result by
`-1/2`, leaving `1`. Event 9564 adds that `1` into register 360, which is
`0` until then. The data register contributes `0`. At the literal magnitude
`256`, register 357 holds `256`.

## What was executed

The trace applies the published scalar rules and stops before event 9564.
Register 357 changes twice, at the load and the scale above. The value read
from register 359 is its initial `1`. Later uses of register 360 are left
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
python3.12 -B research/qq16-origin-one/verify.py
python3.12 -B research/qq16-origin-one/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-origin-one
```

The replay finishes in under a second.

## Open next questions

Event 18932 is the first write into register 354, and it reads register 360
again. The next reading is the scalar value of register 360 immediately
before that addition.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
