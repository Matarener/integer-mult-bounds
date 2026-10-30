# T360 has 470,016 fewer roles

**Partial. No new exponent.**

The 488-replica allocation has `488 · 9 = 4,392` calls and
`4,392 · 408 = 1,791,936` literal roles, with 437,757 physical families.
The T360 allocation has

```text
360 · 9 · 408 = 1,321,920
```

literal roles and physical stock 323,069. The gaps are

```text
1,791,936 - 1,321,920 = (488 - 360) · 9 · 408 = 470,016
437,757 - 323,069 = 114,688
```

## What was executed

The checker factors these counts. It does not rerun the 2,551-pattern replay.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the comparison in PR 3638, head
`d62e1acd7518a231440383f0d0dddf54d6edf8c1`, against the 488-replica schedule
in PR 3633, head `72c268f113368ea0387d188225e3f81ba6d6ef73`.

## Scope and evidence

Original card: `independent-moment`, priority revision 6, refined to this gap.
[TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/t360-role-gap/verify.py
python3.12 -B research/t360-role-gap/test_verify.py
python3.12 -B scripts/research_package.py --package research/t360-role-gap
```

## Open next questions

This gap is the comparison. The pattern replay would leave it.

## Credit

zxv published the T360 allocation. hexapode published the 488-replica schedule
it is compared with.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
