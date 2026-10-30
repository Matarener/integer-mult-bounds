# Register 103 holds -128 before the restoration

**Partial. No new exponent.**

Immediately before event 24433, register 103 holds `-128` when register 359
starts at `1`. The addition multiplies that value by `-1/128`, and register
359 is `0`, so the addition restores it to `1`. The data register contributes
`0`. At the literal magnitude `256`, register 103 holds `-32768`.

## What was executed

The trace applies the published scalar rules and stops before event 24433.
Register 103 changes twice: event 23507 leaves `-64`, and event 24280 leaves
`-128`. The registers added at those two events are not traced.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
source value. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-restore-source/verify.py
python3.12 -B research/qq16-restore-source/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-restore-source
```

The replay finishes in under a second.

## Open next questions

Event 24280 takes register 103 from `-64` to `-128`. The next reading is the
scalar value of register 354 immediately before that addition.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
