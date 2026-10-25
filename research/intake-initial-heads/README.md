# Three intake rows retain their original starting heads

**Partial. No new exponent.**

Intake rows 3107, 3184 and 3251 have a later head in the mutable metadata.
The ledger still records an earlier starting head. That starting head is the
named field of an authenticated receipt, and the later head is the `head`
field of the receipt for the revised observation. The two heads differ. The
metadata number, the current head, the reviewed head and the author agree
across the ledger row, the intake decision and both receipts.

| PR | Original field | Receipt |
| --- | --- | --- |
| 3107 | `initial_archived_head` | `queue-next-20261017` |
| 3184 | `previously_reviewed_head` | `queue-tail-20261017` |
| 3251 | `head` | `queue-refresh-20261017` |

The later heads are read from `queue-next-20261017`, `queue-tail-20261017`
and `queue-oct18-20261018` respectively. Each receipt is pinned by SHA-256.

## What was executed

The checker compares these three rows. It does not rewrite the ledger, the
intake decisions or the receipts.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the initial-head map in PR 3692,
head `af040ab4dd0083a3838f3c2fa78d1b9d861ffad1`.

## Scope and evidence

Original card: `overlap-receipt`, priority revision 6, refined to these three
heads. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record, the ledger, the intake
decisions and the four receipts. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/intake-initial-heads/verify.py
python3.12 -B research/intake-initial-heads/test_verify.py
python3.12 -B scripts/research_package.py --package research/intake-initial-heads
```

## Open next questions

These three heads are the split. Another revision would need its own receipt.

## Credit

roger-sato recorded the three authenticated receipts and the original fields.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
