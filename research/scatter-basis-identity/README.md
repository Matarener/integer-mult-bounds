# The corrected scatter returns d + S p

**Partial. No new exponent.**

The selected cut adds `S p` into the destination. A target change of basis
therefore has to multiply `S` on the left. The corrected word is
`U; scatter(U S); U^{-1}`, and

```text
U^{-1}(U d + U S p) = d + S p
```

whenever `U` is invertible. The checker confirms this on the shear
`U = [[1, 1], [0, 1]]`, whose inverse is `[[1, -1], [0, 1]]`, for nine
integer target and source pairs.

The published invoices split into extra ADDs and extra sign scales:

```text
167 + 18 = 185
794 + 84 = 878
```

The sign scales are six per changed tetrad, `6 · 3 = 18` and `6 · 14 = 84`.
The cut ADD counts move from 176 to 181 and from 176 to 214. The published
recursive-histogram delta is zero; this package does not recompute that
histogram.

## What was executed

The checker multiplies the sample matrices and adds the invoices. It does
not replay the 704 columns.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the invoice in PR 3632, head
`7e7a889cbf6da2c4461af806fe52a888c621a7e7`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
identity. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/scatter-basis-identity/verify.py
python3.12 -B research/scatter-basis-identity/test_verify.py
python3.12 -B scripts/research_package.py --package research/scatter-basis-identity
```

## Open next questions

This identity and this invoice are the correction. Replaying the columns
would leave them.

## Credit

Ross Richardson published the corrected scatter word and these two invoices.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
