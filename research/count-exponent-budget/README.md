# The count 1e-10000 has a 33,220-bit denominator

**Partial. No new exponent.**

The spelling `1e-10000` has 8 characters, inside the 60-character count limit.
Parsed as an exact fraction it is `1/10^10000`, and that denominator has bit
length 33,220.

The published budget reads a trailing decimal exponent before constructing
the fraction and rejects an absolute value above 60. Here the exponent is
`-10000`, so the count is rejected. The boundary values behave as stated:
`1e-60` stays inside the exponent and the `10^60` component limit, while
`1e-61` does not.

## What was executed

The checker expands this one fraction and applies the exponent test. It does
not reprice the queue.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the budget in PR 3636, head
`52899946fcb27930c6d8204772aa6a66ba5fbcc2`.

## Scope and evidence

Original card: `portable-replay`, priority revision 6, refined to this count.
[TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/count-exponent-budget/verify.py
python3.12 -B research/count-exponent-budget/test_verify.py
python3.12 -B scripts/research_package.py --package research/count-exponent-budget
```

## Open next questions

This count is the hole. A larger exponent would leave it.

## Credit

roger-sato published the exponent budget and the `1e-10000` example.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
