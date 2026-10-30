# One aggregate histogram stays below one where the copied per-call histogram does not

**Partial. No new exponent.**

The selected invoice has 144 calls and idle mass `237024 = 144 * 1646`.
None of the four actual idle counts divides by 144. At the per-call ceiling
`1688603446527/10^15`, the aggregate histogram `{51:4647, 27:1}` has certified
moment strictly below one. One hundred forty-four copies of `{51:32, 14:1}`
have certified moment strictly above one. Both histograms have the same idle
mass.

That aggregate histogram also splits into 144 integer call histograms:
39 calls of `{51:33}`, one call of `{51:32, 27:1}`, and 104 calls of
`{51:32}`. Its own bracket is

`1690044548222/10^15` to `1690044548223/10^15`.

The selected saving sits below that lower endpoint.

## What was executed

The checker prices the two named histograms and locates the aggregate bracket.
It does not search another histogram.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the aggregation counterexample
in PR 3747, head `98847f9aba65ba835a15725c9f173c04a98788b3`.

## Scope and evidence

Original card: `selected-packing`, priority revision 6, refined to this gap.
[TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record and the two invoices.
No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/idle-aggregation-gap/verify.py
python3.12 -B research/idle-aggregation-gap/test_verify.py
python3.12 -B scripts/research_package.py --package research/idle-aggregation-gap
```

## Open next questions

This gap is the aggregation counterexample. Another histogram would leave it.

## Credit

Arham-Tahir64 compared the aggregate histogram with the copied per-call histogram.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
