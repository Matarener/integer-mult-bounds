# Register 354 holds -1 before it doubles register 39

**Partial. No new exponent.**

Immediately before event 24284, register 354 holds `-1` when register 359
starts at `1`. Its last scalar write is event 20745. The addition multiplies
that value by `2` and contributes `-2`. Register 39 holds `-2`, so the sum
is `-4`. The data register contributes `0`. At the literal magnitude `256`,
register 354 holds `-256`.

## What was executed

The trace applies the published scalar rules and stops before event 24284.
Register 354 passes through `-1/4` and `-1/2` and then stays at `-1` after
event 20745. Changes of register 39 after this addition are left for the
next reading.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
source value. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-target-four/verify.py
python3.12 -B research/qq16-target-four/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-target-four
```

The replay finishes in under a second.

## Open next questions

The addition leaves register 39 at `-4`. The next reading is whether that
register changes again before event 24438.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
