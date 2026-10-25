# Register 18 holds -4 before it is copied

**Partial. No new exponent.**

Immediately before event 23237, register 18 holds `-4` when register 359
starts at `1`. One addition writes it. Event 20575 adds `-2` times register
292, which holds `2`, and leaves `-4`. The data register contributes `0`.
At the literal magnitude `256`, register 18 holds `-1024`.

## What was executed

The trace applies the published scalar rules and stops before event 23237.
Register 18 has no other scalar change in that prefix. The writes that
produce the `2` in register 292 are left for the next reading.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to
this change. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-shared-four/verify.py
python3.12 -B research/qq16-shared-four/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-shared-four
```

The replay finishes in under a second.

## Open next questions

Event 20575 reads register 292 at `2`. The next reading is the scalar
changes of register 292 before that event.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
