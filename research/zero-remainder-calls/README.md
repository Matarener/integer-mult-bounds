# One hundred fifty-three calls clear the rank-51 remainder

**Partial. No new exponent.**

The selected local profile has one-unpaid idle mass 1646 on each call. That is
`32 * 51 + 14`. A whole number of nine-call replicas has idle mass divisible by
51 exactly when the call count is a multiple of 153, the least common multiple
of 9 and 51. At 153 calls the idle mass is `251838 = 4938 * 51`, with no
remainder child. The live width is `153 * 896/9 = 15232`.

Every smaller positive multiple of nine calls leaves a nonzero remainder. The
selected kappa is unchanged.

## What was executed

The checker computes this call count from the selected invoices. It does not
price a moment.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the zero-remainder replication in
PR 3759, head `f665c47e71425933792eaf910e9cb35c27ff5608`.

## Scope and evidence

Original card: `selected-packing`, priority revision 6, refined to this call
count. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record and the two invoices.
No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/zero-remainder-calls/verify.py
python3.12 -B research/zero-remainder-calls/test_verify.py
python3.12 -B scripts/research_package.py --package research/zero-remainder-calls
```

## Open next questions

This call count is the divisibility. A moment enclosure would leave it.

## Credit

Arham-Tahir64 recorded the 153-call replication.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
