# Register 354 holds -1 before its addition

**Partial. No new exponent.**

Immediately before event 24280, register 354 holds `-1` when register 359
starts at `1`. The addition multiplies that value by `64` and contributes
`-64` to register 103, which already holds `-64`. The data register
contributes `0`. At the literal magnitude `256`, register 354 holds `-256`.

## What was executed

The trace applies the published scalar rules and stops before event 24280.
Register 354 changes three times: event 18932 leaves `-1/4`, event 19679
leaves `-1/2`, and event 20745 leaves `-1`. The registers added at those
three events are not traced.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
source value. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-half-source/verify.py
python3.12 -B research/qq16-half-source/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-half-source
```

The replay finishes in under a second.

## Open next questions

Event 20745 takes register 354 from `-1/2` to `-1`. The next reading is the
scalar value of register 258 immediately before that addition.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
