# The selective repair bills 124 against 112

**Partial. No new exponent.**

The centre-support vector is

```text
(2, 8, 9, 2, 8, 9, 8, 9, 8, 8, 2, 8, 9, 2).
```

Blocks 0, 3, 10 and 13 each contribute 2. Those four supports sum to 8, so the
nominal sensitivity is `112 - 8 = 104`. The same four blocks contribute four
rank-one terms each, and the other ten blocks contribute four rank-two terms
each: 16 ones and 40 twos.

The port defect is 4 in each chosen block, hence 16. One repair factorization
uses three rank-one terms and one rank-two term in every chosen block. Each
block costs 5, and four blocks cost 20. The repaired sensitivity is
`104 + 20 = 124`, which is 12 above the baseline 112.

The oriented forward repair adds `252 + 24 = 276` scalar operations. Its cut
moves from 176 to 212. The first-block scratch control checks 25 columns
through four lines, which is 100 scalar ADDs.

## What was executed

The checker adds these published ranks and invoices. It does not replay columns.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the co-delivery bill in PR 3691,
head `b37d0e75433837482c351863a672543056f95bd5`.

## Scope and evidence

Original card: `centre-path-sharing`, priority revision 6, refined to this
bill. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/codelivery-repair-bill/verify.py
python3.12 -B research/codelivery-repair-bill/test_verify.py
python3.12 -B scripts/research_package.py --package research/codelivery-repair-bill
```

## Open next questions

This bill is the comparison. Replaying the columns would leave it.

## Credit

zxv published the selective co-delivery bill.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
