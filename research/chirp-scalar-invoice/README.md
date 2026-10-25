# The chirp scalar charges add to `16N(ell+1) + 28N`

**Partial. No new exponent.**

The middle-map invoice counts four groups of scalar word products. With
`L = ell + 1` and `N` coefficients,

```text
kernel     4 N L
endpoints  8 N
twists    12 N
ring      12 N L + 8 N
```

The terms that grow with `L` contribute `(4 + 12) N L = 16 N L`. The
remaining terms contribute `(8 + 12 + 8) N = 28 N`. The total is

```text
16 N (ell + 1) + 28 N = 4 N (4(ell + 1) + 7).
```

The cell count is `V = 2(p + 2) N`, so

```text
(scalar total) (p + 2) = V (8(ell + 1) + 14).
```

Both identities hold for every precision `p` from 16 through 256, every
length `ell` from 2 through `p - 1`, and every copy count from 1 through 8:
32,294 parameter rows. The selected kappa is unchanged.

## What was executed

The checker adds the four charges and compares the total with the cell count.
It does not run the middle-map consumer.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the invoice paragraph of PR 3763,
head `6bb7dfdae182a69f7c8836a9ec1be0b2b747e124`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
invoice. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/chirp-scalar-invoice/verify.py
python3.12 -B research/chirp-scalar-invoice/test_verify.py
python3.12 -B scripts/research_package.py --package research/chirp-scalar-invoice
```

## Open next questions

The four charges add on every admitted row. A middle-map replay would leave
this package.

## Credit

Jose Manuel (jmbarrancoml) stated these four charges in PR 3763. This package
adds them.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
