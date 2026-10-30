# The named dirty helper has magnitude T

**Partial. No new exponent.**

The F0 scalar fault witness sets dirty helper `L359` to `T` and the original
data input `L112` to 1. Immediately before event 24438, `L39` is `-4T` and
`L359` is still `T`. Each of the four stored completed defects equals `4 u T`.

## What was executed

The stored instruction at index 24438 is an add of 4 times `L359` into `L39`.
The receipt's source coefficient for the dirty helper is 1 and its target
coefficient is -4. The completed-defect formula is `4*u*T`. The four stored
powers of two are 0, 8, 64 and 256, and each completed defect equals four
times the stored unit times that power of two. All 480 helpers are recorded
as restored exactly. The 26,099-event word is not replayed.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
one helper. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the fault readme and result. No selected
frontier file changes. This is the permissive fault specification, not a
measured rounding of an implemented producer.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-dirty-helper-magnitude/verify.py
python3.12 -B research/qq16-dirty-helper-magnitude/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-dirty-helper-magnitude
```

The replay finishes in under a second.

## Open next questions

The helper magnitude stays the symbol `T`. The next reading is whether the
native dirty-fault package stores a concrete vector for `L359`.

## Credit

Arham Tahir supplied the scalar fault witness. Nick Petalas supplied the
endpoint handoff that this witness follows, as that readme states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
