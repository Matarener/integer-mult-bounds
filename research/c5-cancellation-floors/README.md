# The C5 floors are 45 and 561/16

**Partial. No new exponent.**

The published integer lifts are `2, 8, 1, 7, 2, 3, 3, 4, 6`. They sum to 36,
so the weights sum to

```text
36/16 = 9/4
```

The granted local floor is 20, and `20 · 9/4 = 45`. The full-support total is
`ρ = 303/16`, which is greater than 9, and the credit per remaining
full-support term is

```text
303/16 - 9 = 159/16
```

The fit-level floors are therefore

```text
45 - (159/16) · |σ_J|
```

which is 45 when there is no J term and `45 - 159/16 = 561/16` when there is
one. Both are greater than the termwise ceiling `180/7`.

The diagonal identity has tariff `112 · 2 = 224`, which meets 45. The
J-extension has `112 · 111 = 12432` off-diagonal terms and total tariff
`9 + 16088 = 16097`, which meets `561/16`. The named-support scan covers
`1596² = 2547216` rectangles; this package does not repeat that scan.

## What was executed

The checker multiplies these weights and tariffs. It does not scan the
rectangles.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the floor derivation in PR 3643,
head `4a59001080cacc7070f3273201a7b7c2d760a6ef`.

## Scope and evidence

Original card: `coverage-law-change`, priority revision 6, refined to these
floors. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/c5-cancellation-floors/verify.py
python3.12 -B research/c5-cancellation-floors/test_verify.py
python3.12 -B scripts/research_package.py --package research/c5-cancellation-floors
```

## Open next questions

These floors are the certificate. Scanning the rectangles would leave them.

## Credit

VictorLiwentao published the named-class cancellation charge and these floors.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
