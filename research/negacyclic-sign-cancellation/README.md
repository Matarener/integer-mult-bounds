# The cyclic and negacyclic wraps carry the same sign

**Partial. No new exponent.**

Let `r` be a power of two and let `zeta` satisfy `zeta^r = -1`. Substituting
`x = zeta y` into a product sends a term `x^{i+j}` to `zeta^{i+j} y^{i+j}`.
Reducing the exponent modulo `zeta^r + 1` and the degree modulo `y^r + 1`
either leaves both unchanged or subtracts `r` from both. Each subtraction
contributes a minus sign, so the product of the signs is `+1` and the reduced
exponent equals the reduced degree.

Therefore the substituted product, reduced modulo `y^r + 1`, is the image of
the cyclic product modulo `x^r - 1`. Every exponent pair at
`r = 2, 4, ..., 4096` has this cancellation: 22,369,620 pairs. Raising the
basis element `zeta` to the `r`-th power yields `-1` at each of those rings.
Every product of 0-1 polynomials at `r = 2, 4, 8` agrees on the two sides:
65,808 products. The selected kappa is unchanged.

## What was executed

The checker compares the wraps and multiplies the binary polynomials. It does
not run the middle-map consumer.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the cyclic-convolution paragraph
of PR 3763, head `6bb7dfdae182a69f7c8836a9ec1be0b2b747e124`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
identification. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/negacyclic-sign-cancellation/verify.py
python3.12 -B research/negacyclic-sign-cancellation/test_verify.py
python3.12 -B scripts/research_package.py --package research/negacyclic-sign-cancellation
```

## Open next questions

The sign cancellation is an integer comparison and every exponent pair through
ell 12 was checked. A middle-map replay would leave this package.

## Credit

Jose Manuel (jmbarrancoml) stated this substitution in PR 3763. This package
checks the two wraps and the binary products.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
