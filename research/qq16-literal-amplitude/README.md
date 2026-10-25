# Register 359 starts at amplitude 256

**Partial. No new exponent.**

The literal execution assigns register 359 the scalar `256` and expands every
register by scaling the constant vector. The first amplitude of that
expansion is real `256`, imaginary `0`, at exponent `0`. The saved receipt
stores the scalar and does not store the amplitude.

## What was executed

The initial state is built by `scaled(ONE, x)` before any event. For the
constant vector, scaling by the integer 256 multiplies the real part by 256
and leaves the exponent at 0, so no dyadic cancellation occurs. The receipt's
literal check has the keys `T`, `u`, `eta`, `max_data_error` and
`coordinates`. The 26,099 events were not replayed.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
initial amplitude. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the scaling formula, the assignment and
the saved receipt. No selected frontier file changes.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-literal-amplitude/verify.py
python3.12 -B research/qq16-literal-amplitude/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-literal-amplitude
```

The replay finishes in under a second.

## Open next questions

The cut comparison uses the value present at event 24438. The next reading
is whether any earlier event writes register 359.

## Credit

Tekalign supplied the literal execution, as its source states.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
