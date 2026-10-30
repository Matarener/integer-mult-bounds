# Register 39 remains 0 after the fault

**Partial. No new exponent.**

From event 24438 through event 26098, register 39 has one scalar value change
when register 359 starts at `1`. The fault addition takes it from `-4` to `0`.
Five later additions name the same register. Their sources hold `0`, so each
contribution is `0`, and the value remains `0` through the last event. The
data register contributes `0`. The literal value is `0`.

The later additions are event 24743 from register 93 with coefficient `-256`,
then events 25771 through 25774 from registers 47, 81, 87 and 110 with
coefficients `1/2`, `-1/2`, `-1/2` and `-1/2`.

## What was executed

The trace applies the published scalar rules from the initial value through
the last event. The suffix contains 1412 scalar events, 240 residual
adapters, 8 native lines and 1 phase. Only scalar events update the
coefficient.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
suffix. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-later-zero/verify.py
python3.12 -B research/qq16-later-zero/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-later-zero
```

The replay finishes in under a second.

## Open next questions

Register 39 returns to `0` at event 24438 and remains `0` through the last
event. Tracing a later source that contributes `0` would be a new reading.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
