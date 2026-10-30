# Register 39 stays at -4 after event 24284

**Partial. No new exponent.**

From event 24284 through event 24437, register 39 has one scalar change when
register 359 starts at `1`. Event 24284 takes it from `-2` to `-4`. The other
153 scalar events in that window leave it there. The data register contributes
`0`. At the literal magnitude `256`, the held value is `-1024`.

## What was executed

The trace applies the published scalar rules, includes event 24284, and stops
before event 24438. Every event in the window is scalar. The value present at
the start of the fault event remains `-4`.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
window. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scalar rules and the certificate. No
selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-held-four/verify.py
python3.12 -B research/qq16-held-four/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-held-four
```

The replay finishes in under a second.

## Open next questions

Register 39 holds `-4` at the start of event 24438. The next reading is the
sum that event writes.

## Credit

Tekalign supplied the scalar update rules, as the checker states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
