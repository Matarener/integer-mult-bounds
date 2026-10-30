# Register 280 holds -1/8 before its addition

**Partial. No new exponent.**

Immediately before event 19679, register 280 holds `-1/8` when register 359
starts at `1`. The addition multiplies that value by `2` and contributes
`-1/4` to register 354, which holds `-1/4` until then. The data register
contributes `0`. At the literal magnitude `256`, register 280 holds `-32`.

## What was executed

The trace applies the published scalar rules and stops before event 19679.
Register 280 is `-1/4` after event 19133. Event 19671 adds `-1/2` times
register 354, which holds `-1/4`, and leaves `-1/8`. The register added at
event 19133 is left for the next reading.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
source value. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-eighth-value/verify.py
python3.12 -B research/qq16-eighth-value/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-eighth-value
```

The replay finishes in under a second.

## Open next questions

Event 19133 takes register 280 from `0` to `-1/4`. The next reading is the
scalar value of register 274 immediately before that addition.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
