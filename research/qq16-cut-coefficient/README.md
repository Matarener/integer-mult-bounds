# Register 359 holds coefficient 1 at the cut

**Partial. No new exponent.**

With register 359 starting at `1` and every other register at `0`, its scalar
coefficient is `-1` after the scale at event 9545, `0` after the addition at
event 9549, and `1` after the addition at event 24433. Immediately before the
fault it is `1`. The literal amplitude `256` is unchanged, and the data
register contributes `0`.

## What was executed

The trace applies the published scalar rules to the 26,099-event word and
stops before event 24438. Climbs, adapters and the other non-scalar events
leave the coefficient unchanged. The same trace puts `-4` in register 39,
which is the published partner of this coefficient. The register that
restores the value at event 24433 is not traced.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
coefficient. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-cut-coefficient/verify.py
python3.12 -B research/qq16-cut-coefficient/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-cut-coefficient
```

The replay finishes in under a second.

## Open next questions

The addition at event 24433 restores the coefficient from `0` to `1`. The
next reading is the scalar value of register 103 immediately before that
addition.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
