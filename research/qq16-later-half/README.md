# Register 356 holds 1/2 at its later read

**Partial. No new exponent.**

Immediately before event 19156, register 356 holds `1/2` when register 359
starts at `1`. Event 11809 copies register 360, which holds `1`, and leaves
`1`. Event 16016 copies that `1` into register 292. Event 16017 then adds
`-1/2` times register 292, which holds `1`, and leaves `1/2`. The data
register contributes `0`. At the literal magnitude `256`, register 356 holds
`128`.

## What was executed

The trace applies the published scalar rules and stops before event 19156.
Those are the only two scalar changes of register 356 in the prefix. The
value of register 354 at event 24284 is left for the next reading.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to
these changes. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-later-half/verify.py
python3.12 -B research/qq16-later-half/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-later-half
```

The replay finishes in under a second.

## Open next questions

Event 24284 takes register 39 from `-2` to `-4`. The next reading is the
scalar value of register 354 immediately before that addition.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
