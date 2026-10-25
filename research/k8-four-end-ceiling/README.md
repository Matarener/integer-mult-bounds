# The four-end histogram sits inside one incumbent grid cell

**Partial. No new exponent.**

The named domain is the exhibited four-end profile

```text
{1:2400, 2:446, 3:416, 4:142, 5:82, 8:8}
```

Its rank mass is 5,582. Under the selected coverage total 7,232 the idle mass
is 1,650. This is the partition already attained by contracting ends
574, 575, 580 and 581. No other partition was searched.

`ceiling.ceiling` at grid `1/10^12` returns the cell

```text
33803961/20000000000 < a < 1690198051/1000000000000
```

The note's bracket `0.001690198050302 < best ceiling < 0.001690198050303`
lies inside that cell. The high endpoint divided by the selected ceiling
`169005411/100000000000` exceeds 1 by less than `0.00852%`. The selected
saving `kappa/(1-kappa)` stays below the high endpoint, so the fraction of
this cap realized by the selected record is below one.

## What was executed

The checker rebuilds the profile and calls `ceiling.ceiling`. It does not
rerun the endpoint LP.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the four-end profile sentence.

## Scope and evidence

Original card: `selected-packing`, priority revision 6, refined to this
published histogram. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the k8 note, the ceiling function and the
selected record. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/k8-four-end-ceiling/verify.py
python3.12 -B research/k8-four-end-ceiling/test_verify.py
python3.12 -B scripts/research_package.py --package research/k8-four-end-ceiling
```

## Open next questions

This histogram's incumbent cell is the bound. Another partition would leave
this cell.

## Credit

Gareth Davidson prepared the unrestricted-end note with OpenAI Codex. Douglas
Colkitt prepared the packing ceiling with Claude (Anthropic).

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
