# Frame 1 starts with the component 1

**Partial. No new exponent.**

The stored frame numbered 1 is the nine axes
`[256, 128, 64, 32, 16, 8, 4, 2, 1]`. The published formula returns the
unnormalized constant vector for every rank-9 frame, so its first component
is real `1`, imaginary `0`, at exponent `0`.

## What was executed

The canonical word lists 1,004 frames. Only index 1 was read. Its nine axes
are independent and lie in the open range below 512, which is the condition
for the formula's early return. That return is the constant vector whose
real part is 512 ones and whose imaginary part is 512 zeros. The native
checker binds this same index to that constant vector. The other frames were
not evaluated, and the native word was not replayed.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
component. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the formula, the frame-index binding and
the replay archive. No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-frame1-component/verify.py
python3.12 -B research/qq16-frame1-component/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-frame1-component
```

The replay finishes in under a second.

## Open next questions

The formula gives the direction. The next reading is whether the literal
512-component execution stores the first amplitude of the initial `L359`
vector, or only the scalar `T`.

## Credit

Tekalign supplied the frame formula, as its source states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
