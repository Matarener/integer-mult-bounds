# The owner slices leave the selected idle histogram

**Partial. No new exponent.**

The pinned owner file has 69120 rows. Each of the 144 calls uses helpers
`0` through `479` once. The declared bins have capacities

`{8: 10752, 16: 7168, 32: 7168, 48: 7168}`,

so the total capacity is 774144. The slices are packed from offset zero with
no gaps or overlaps, and their widths sum to 537120. Every unused suffix is
one idle child. Those suffixes are exactly the selected idle histogram
`{1: 2276, 3: 377, 7: 7, 48: 4866}`.

Bins touched by more than one call number 17217. The bin `(owner 0, child 6,
port 85)` has capacity 32 and the four slices `(9, 0, 9)`, `(11, 9, 4)`,
`(13, 13, 9)`, and `(15, 22, 9)`, whose widths sum to 31. The selected kappa
is unchanged.

## What was executed

The checker recounts these slices. It does not replay phase events.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the owner-ledger recount in
PR 3759, head `f665c47e71425933792eaf910e9cb35c27ff5608`.

## Scope and evidence

Original card: `supplier-boundary-audit`, priority revision 6, refined to this
ledger. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record, the independent idle
histogram, and the owner plan. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/owner-slice-ledger/verify.py
python3.12 -B research/owner-slice-ledger/test_verify.py
python3.12 -B scripts/research_package.py --package research/owner-slice-ledger
```

## Open next questions

This ledger is the slice recount. A phase replay would leave it.

## Credit

Arham-Tahir64 recounted these owner slices.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
