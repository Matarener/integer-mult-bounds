# The T450 allocation has 450 replicas

**Partial. No new exponent.**

The published order joins a 37-replica chronology with an 8-replica chronology,
then takes ten copies:

```text
10 · (37 + 8) = 450
```

Each replica has 9 calls and each call has 408 helper roles, so the schedule
is `450 · 9 = 4,050` calls and `4,050 · 408 = 1,652,400` roles.

The published profile is

```text
{1:9983580, 2:2940300, 3:936579, 4:413100, 5:87495, 8:32400, 48:172221}
```

It has 14,565,675 children and rank mass 29,289,600. The conditional root is

```text
0.001730047552093344159584 - 10^(-46) - 10^(-70)
```

That value is greater than the T740 root
`0.001730006549538841847005` and greater than the selected kappa
`836330098538459/500000000000000000`.

## What was executed

The checker adds the published counts and compares the two rationals. It does
not expand the 1,652,400 roles.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the claim in PR 3624, head
`515a7c4490aa32ac3ca5014feb6f7da0d6952863`.

## Scope and evidence

Original card: `independent-moment`, priority revision 6, refined to this
allocation. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/t450-replica-count/verify.py
python3.12 -B research/t450-replica-count/test_verify.py
python3.12 -B scripts/research_package.py --package research/t450-replica-count
```

## Open next questions

This count and this root comparison are the ledger. Expanding the roles would
leave them.

## Credit

hexapode published the T450 allocation. Ross Richardson published the T740
chronology it compares against.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
