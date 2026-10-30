# Register 360 holds 1/4 at its later use

**Partial. No new exponent.**

Immediately before event 18932, register 360 holds `1/4` when register 359
starts at `1`. The addition multiplies that value by `-1` and contributes
`-1/4` to register 354, which is `0` until then. The data register
contributes `0`. At the literal magnitude `256`, register 360 holds `64`.

## What was executed

The trace applies the published scalar rules and stops before event 18932.
Register 360 is `1` after event 9564 and `1/2` after event 11810. Event
16153 then adds `1/4` times register 262, which holds `-1`, and leaves
`1/4`. The next source of register 354 is left for the following reading.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
later value. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-quarter-value/verify.py
python3.12 -B research/qq16-quarter-value/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-quarter-value
```

The replay finishes in under a second.

## Open next questions

Event 19679 takes register 354 from `-1/4` to `-1/2`. The next reading is
the scalar value of register 280 immediately before that addition.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
