# The sector dimensions sum to 28,800

**Partial. No new exponent.**

The published idempotents have ranks `1, 8, 35, 112, 84`, which sum to 240.
Each odd-Gram sector and its swap has dimension twice the product of the two
ranks:

```text
2·8·1 = 16
2·112·1 = 224
2·8·35 = 560
2·112·35 = 7840
2·8·84 = 1344
2·112·84 = 18816
```

These six dimensions sum to `120 · 240 = 28800`. The first three, the sectors
that survive at `u = v = 0`, sum to 800. The remaining single-block ports
satisfy `28800 + 2160 = 30960`.

A width-17 return then costs `17 · 9424 = 160208` for the published quintic
minimum and `17 · 20400 = 346800` for the published septic minimum. Both
exceed 30,960 ports. For every positive replica count `L` and either invoice
`C`, the inherited deficit `(L-1)·30960 - L·C` is negative because `C` exceeds
the port count.

## What was executed

The checker multiplies these ranks. It does not act on the 28,800 columns.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the sector table in PR 3649, head
`f8768756d8ac4abb263295170a436ba54562fdcd`.

## Scope and evidence

Original card: `scalar-to-moment`, priority revision 6, refined to these
dimensions. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/h6-sector-dimensions/verify.py
python3.12 -B research/h6-sector-dimensions/test_verify.py
python3.12 -B scripts/research_package.py --package research/h6-sector-dimensions
```

## Open next questions

These dimensions are the obstruction. Acting on the columns would leave them.

## Credit

Ross Richardson published the odd-Gram sector table and the two rank minima.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
