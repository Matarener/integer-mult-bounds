# The native check sets the helper to 256

**Partial. No new exponent.**

The native dirty-fault receipt sets helper `L359` to `T` times the unit
constant payload, and its literal check uses `T = 256`. The stored maximum
data error `1/1024` equals `4 u T`, and the stored injection `1/512` equals
`8 u T`.

## What was executed

The receipt names dirty register 359 and fault index 24438. The data-error
formula is `4*u*T` and the local allowance is `8*u*T`, with unit
`1/1048576`. Both stored fractions match those products at `T = 256`. The
readme says the physical input is `L359 = Tχ`, where `χ` is the unit constant
payload, and that the frame vector at this fault is the 512-entry constant
vector. The receipt does not list those 512 components. It calls the fault a
permissive completed-ADD fault, not a concrete rounding failure.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
literal value. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the native readme and result. No selected
frontier file changes. The 1,004 frame vectors are not reconstructed.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-native-helper-value/verify.py
python3.12 -B research/qq16-native-helper-value/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-native-helper-value
```

The replay finishes in under a second.

## Open next questions

The scalar is 256 and the frame vector is described as constant. The next
reading is the first component of that frame-1 vector from its published
formula.

## Credit

Tekalign supplied the native receipt, as its task states. Arham Tahir
supplied the scalar witness that the native readme credits through PR 2995.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
