# Centre 112 is already above one at saving zero

**Partial. No new exponent.**

One call has width `896/9`, dimension 73 and centre 112, with one coordinate
unpaid. The covered mass is `(73 - 1) * 896/9 + 112`. At saving zero every
rank unit costs `1/73`, so the per-width moment is the covered mass divided
by `73 * 896/9`. That simplifies to

`1 + (112 - 896/9) / (73 * 896/9) = 1 + 1/584 = 585/584`.

The value is greater than one. Two profiles with the same covered mass, one
made of rank 1 and one carrying a single rank 51, give the same moment. The
selected kappa is unchanged.

## What was executed

The checker evaluates this fraction. It does not replay the 704 columns.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the zero-saving screen in PR 3691,
head `b37d0e75433837482c351863a672543056f95bd5`.

## Scope and evidence

Original card: `coverage-law-change`, priority revision 6, refined to this
moment. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/zero-saving-centre-moment/verify.py
python3.12 -B research/zero-saving-centre-moment/test_verify.py
python3.12 -B scripts/research_package.py --package research/zero-saving-centre-moment
```

## Open next questions

This moment is the zero-saving comparison. A column replay would leave it.

## Credit

zxv recorded this zero-saving screen.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
