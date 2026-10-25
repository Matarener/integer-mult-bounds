# Register 356 holds a copy of 1

**Partial. No new exponent.**

Immediately before event 11810, register 356 holds `1` when register 359
starts at `1`. Event 11809, the immediately preceding scalar addition, copies
that `1` from register 360 with coefficient `1`. Event 11810 then multiplies
the copy by `-1/2` and contributes `-1/2` to register 360. The data register
contributes `0`. At the literal magnitude `256`, register 356 holds `256`.

## What was executed

The trace applies the published scalar rules and stops before event 11810.
Register 356 changes once, at event 11809. After that copy, registers 356 and
360 both hold `1`. The addition that first placed this `1` into register 360
is left for the next reading.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
source value. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-adjacent-copy/verify.py
python3.12 -B research/qq16-adjacent-copy/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-adjacent-copy
```

The replay finishes in under a second.

## Open next questions

Event 9564 is the first write of `1` into register 360. The next reading is
the scalar value of register 357 immediately before that addition.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
