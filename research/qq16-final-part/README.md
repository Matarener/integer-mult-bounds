# Register 258 holds -1 before its addition

**Partial. No new exponent.**

Immediately before event 20745, register 258 holds `-1` when register 359
starts at `1`. The addition multiplies that value by `1/2` and contributes
`-1/2` to register 354, which already holds `-1/2`. The data register
contributes `0`. At the literal magnitude `256`, register 258 holds `-256`.

## What was executed

The trace applies the published scalar rules and stops before event 20745.
One addition writes register 258: event 20719 leaves `-1`. The register added
there is left for the next reading.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
source value. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-final-part/verify.py
python3.12 -B research/qq16-final-part/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-final-part
```

The replay finishes in under a second.

## Open next questions

Event 20719 takes register 258 from `0` to `-1`. The next reading is the
scalar value of register 262 immediately before that addition.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
