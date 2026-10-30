# Register 360 holds 1/2 before its addition

**Partial. No new exponent.**

Immediately before event 16152, register 360 holds `1/2` when register 359
starts at `1`. The addition multiplies that value by `-2` and writes `-1`
into register 262, which is `0` until then. The data register contributes
`0`. At the literal magnitude `256`, register 360 holds `128`.

## What was executed

The trace applies the published scalar rules and stops before event 16152.
Register 360 changes twice: event 9564 leaves `1`, and event 11810 leaves
`1/2`. The registers added at those two events are left for a later reading.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
source value. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-signed-half/verify.py
python3.12 -B research/qq16-signed-half/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-signed-half
```

The replay finishes in under a second.

## Open next questions

Event 11810 takes register 360 from `1` to `1/2`. The next reading is the
scalar value of register 356 immediately before that addition.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
