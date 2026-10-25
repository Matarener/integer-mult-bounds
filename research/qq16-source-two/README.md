# Register 292 holds 2 before it is doubled into -4

**Partial. No new exponent.**

Immediately before event 20575, register 292 holds `2` when register 359
starts at `1`. Event 16016 copies register 356, which holds `1`, and leaves
`1`. Event 19164 adds `-2` times register 295, which holds `-1/2`, and
leaves `2`. The data register contributes `0`. At the literal magnitude
`256`, register 292 holds `512`.

## What was executed

The trace applies the published scalar rules and stops before event 20575.
Those are the only two scalar changes of register 292 in the prefix. The
writes that produce the `-1/2` in register 295 are left for the next reading.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to
these changes. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-source-two/verify.py
python3.12 -B research/qq16-source-two/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-source-two
```

The replay finishes in under a second.

## Open next questions

Event 19164 reads register 295 at `-1/2`. The next reading is the scalar
changes of register 295 before that event.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
