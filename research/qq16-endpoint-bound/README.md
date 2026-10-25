# The QQ16 certificate stops at the endpoint

**Partial. No new exponent.**

The stored producer-defect certificate has 224 absolute row sums for the F0
inverse and 224 for the zero-retention decoder. Their maxima are 49 and 1923.
The certificate says it does not implement a physical producer, and it has no
dirty-helper field.

## What was executed

Each stored row carries an absolute row sum `l1`. The largest F0 sum is 49,
matching the stored sharp witness. The largest decoder sum is 1923. The result
scope is "Conditional endpoint bounds; no physical producer implementation."
The readme says these are endpoint sensitivities, not bounds on faults inside
producer instructions, and that the package does not implement the producer.
The `events` field is the integer 3823, not a list of producer instructions.
No result field is named `dirty`.

## Scope and evidence

Original card: `joint-query-controller`, priority revision 6, refined to this
endpoint reading. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the defect-transfer readme and result. No
selected frontier file changes. The decoder matrix is not recomputed.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/qq16-endpoint-bound/verify.py
python3.12 -B research/qq16-endpoint-bound/test_verify.py
python3.12 -B scripts/research_package.py --package research/qq16-endpoint-bound
```

The replay finishes in under a second.

## Open next questions

The endpoint constants are 49 and 1923. The missing bound is the magnitude of
one literal producer instruction, including its dirty helper.

## Credit

Nick Petalas supplied the endpoint certificate and the statement that it does
not implement the producer.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
