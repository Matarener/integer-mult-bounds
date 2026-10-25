# Register 39 holds -2 before event 23304

**Partial. No new exponent.**

Immediately before event 23304, register 39 holds `-2` when register 359
starts at `1`. Event 23237 copies register 18, which holds `-4`, and leaves
`-4`. Event 23278 adds `-1/2` times register 343, which holds `-4`, and
leaves `-2`. The data register contributes `0`. At the literal magnitude
`256`, register 39 holds `-512`.

## What was executed

The trace applies the published scalar rules and stops before event 23304.
Those are the only two scalar changes of register 39 in the prefix. The
writes that produce the `-4` in register 18 are left for the next reading.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to
these changes. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-target-two/verify.py
python3.12 -B research/qq16-target-two/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-target-two
```

The replay finishes in under a second.

## Open next questions

Register 18 holds `-4` at event 23237, and that value is copied into both
register 39 and register 343. The next reading is the scalar changes of
register 18 before that event.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
