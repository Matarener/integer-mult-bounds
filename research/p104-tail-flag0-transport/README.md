# The flag-0 promotion is compiled record 34

**Partial. No new exponent.**

The tail package's compiled transport file has 208 rank-1 records, one
promotion and one restoration for each of the 104 targets. Target 34's
promotion is the only record whose compressed frames are event 5758. Its
restoration is event 5807.

## What was executed

Event 5758 is

```text
transport Y34
  [499, 23, 232, 32, 112, 15, 7, 2]
  -> [1, 2, 4, 8, 16, 32, 64, 128, 256]
  rank 1
```

The promote record for target 34 has those compressed columns and recipe rank
1. Event 5807 is the reverse pair, and the restore record for target 34 has
those compressed columns. No other record has either pair. The physical
columns in the promote record are a different integer list from the witness
frame. The Clifford operators in the recipe are not executed.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
record match. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the tail word and the compiled transports.
No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/p104-tail-flag0-transport/verify.py
python3.12 -B research/p104-tail-flag0-transport/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-tail-flag0-transport
```

The replay finishes in under a second.

## Open next questions

The compressed frames match. The next reading is whether target 34's promote
recipe satisfies the native checker's operator equation.

## Credit

Cinna Davis supplied the tail word and the compiled transport records.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
