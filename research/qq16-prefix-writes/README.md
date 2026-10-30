# The prefix writes register 359

**Partial. No new exponent.**

Thirty-two events before index 24438 have destination register 359: 21
additions, 2 scales, 2 adapters and 7 climbs. The first is the adapter at
event 7761. The last is the addition at event 24433, which adds `-1/128` times
register 103. The value at the cut is the result of these writes.

## What was executed

The stored F0 word expands to 26,099 events. The scan reads the destination
field of each event before the fault and counts matches with register 359.
The fault instruction itself writes register 39 and reads register 359, so it
is outside the count. A climb's old frame is a frame index, and the three
climbs whose old frame is 359 but whose destination is another register are
excluded. No amplitude was evaluated.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
destination count. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the destination rules and the certificate.
No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-prefix-writes/verify.py
python3.12 -B research/qq16-prefix-writes/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-prefix-writes
```

The replay finishes in under a second.

## Open next questions

The coefficient present at the cut is determined by these 32 writes. The next
reading is that scalar coefficient of register 359 immediately before event
24438.

## Credit

Tekalign supplied the checker that names each destination field, as its
source states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
