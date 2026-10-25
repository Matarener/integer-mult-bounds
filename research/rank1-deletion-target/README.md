# Deleting the rank-1 children still misses 1/99

**Partial. No new exponent.**

The selected local word is

```text
{1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}
```

with rank mass 5,586. The coverage total is 7,232, so the idle mass is
1,646. The largest idle rank allowed by the halving guard is 51, because
`2·51² < 73²` and `2·52²` is not.

Deleting the 2,412 rank-1 children moves that mass into the idle remainder.
The local mass falls to 3,174 and the idle mass rises to 4,058. At the
planning target `a = 1/99`, the published relaxation of this deleted word
still has its lower bound above one. The same relaxation of the full word
is higher. The selected saving `kappa/(1-kappa)` stays below the packing
cap `169005411/100000000000`.

## What was executed

The checker rebuilds the two profiles and calls `ceiling.relax` and
`ceiling.ceiling`. It does not search another idle histogram.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the ceiling note's rank-1
deletion sentence.

## Scope and evidence

Original card: `selected-packing`, priority revision 6, refined to this
deletion. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the ceiling note, the ceiling function and
the selected record. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/rank1-deletion-target/verify.py
python3.12 -B research/rank1-deletion-target/test_verify.py
python3.12 -B scripts/research_package.py --package research/rank1-deletion-target
```

## Open next questions

This deletion is the residual. Another idle histogram would leave this
target.

## Credit

Douglas Colkitt prepared the packing ceiling with Claude (Anthropic). The
coverage identity is PR 1012's. The catalogue mixture bound is Ali Romman's
heterogeneous-owner assembly, as that note credits.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
