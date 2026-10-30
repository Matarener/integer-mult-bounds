# Event 24438 writes 0 into register 39

**Partial. No new exponent.**

Immediately before event 24438, register 359 holds `1` and register 39 holds
`-4` when register 359 starts at `1`. The fault addition multiplies register
359 by `4` and contributes `4`. The sum in register 39 is `0`. The data
register contributes `0` to both operands. At the literal magnitude `256`,
the operands are `256` and `-1024`, and the literal sum is `0`.

Register 359 was last written at event 24433. Register 39 was last written
at event 24284.

## What was executed

The trace applies the published scalar rules and stops before event 24438.
The sum is computed from those two values. Changes of register 39 after the
fault addition are left for the next reading.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
sum. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-fault-sum/verify.py
python3.12 -B research/qq16-fault-sum/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-fault-sum
```

The replay finishes in under a second.

## Open next questions

The fault addition writes `0` into register 39. The next reading is whether
a later scalar event changes that register.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
