# Register 343 holds -8 before its addition

**Partial. No new exponent.**

Immediately before event 23507, register 343 holds `-8` when register 359
starts at `1`. The addition multiplies that value by `8` and contributes
`-64` to register 103, which is `0` until then. The data register contributes
`0`. At the literal magnitude `256`, register 343 holds `-2048`.

## What was executed

The trace applies the published scalar rules and stops before event 23507.
Event 23274 adds register 18, which holds `-4`, and leaves `-4`. Event 23304
adds `2` times register 39, which holds `-2`, and leaves `-8`. The writes
that produce register 39 are left for the next reading.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
source value. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-eightfold/verify.py
python3.12 -B research/qq16-eightfold/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-eightfold
```

The replay finishes in under a second.

## Open next questions

Register 39 holds `-2` at event 23304 and `-4` at the fault. The next reading
is the scalar changes of register 39 before event 23304.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
