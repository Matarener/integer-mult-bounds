# Register 295 holds -1/2 before it doubles register 292

**Partial. No new exponent.**

Immediately before event 19164, register 295 holds `-1/2` when register 359
starts at `1`. One addition writes it. Event 19156 adds `-1` times register
356, which holds `1/2`, and leaves `-1/2`. The data register contributes
`0`. At the literal magnitude `256`, register 295 holds `-128`.

## What was executed

The trace applies the published scalar rules and stops before event 19164.
Register 295 has no other scalar change in that prefix. The writes that
take register 356 from its earlier `1` to this `1/2` are left for the next
reading.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to
this change. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-negative-half/verify.py
python3.12 -B research/qq16-negative-half/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-negative-half
```

The replay finishes in under a second.

## Open next questions

Register 356 holds `1` at event 16016 and `1/2` at event 19156. The next
reading is the scalar changes of register 356 before event 19156.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
