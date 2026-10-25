# An axis residue fits its field and needs one subtraction

**Partial. No new exponent.**

The chirp axis state keeps five fields: radix, index, value, difference and
coefficient. For `r = 2^ell` the residue modulus is `q = 2r = 2^{ell+1}`. A
field of `ell+1` bits holds every residue and does not hold the modulus
itself.

For every width `w` from 2 through 12, and every pair of residues modulo
`2^w`,

```text
0 <= a, b < 2^w,    so    a + b < 2^(w+1).
```

The representative is `a + b` when that is below the modulus, and
`a + b - 2^w` otherwise. That is at most one subtraction. There are
22,369,616 such pairs. Five fields occupy `5w` bits. The selected kappa is
unchanged.

## What was executed

The checker tests the bit width and every pair. It does not run the
middle-map consumer.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the five-field record in PR 3763,
head `6bb7dfdae182a69f7c8836a9ec1be0b2b747e124`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
width. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/chirp-field-width/verify.py
python3.12 -B research/chirp-field-width/test_verify.py
python3.12 -B scripts/research_package.py --package research/chirp-field-width
```

## Open next questions

The widths and the pairs are finite. A middle-map replay would leave this
package.

## Credit

Jose Manuel (`jmbarrancoml`) stores these five fields in the chirp middle map
of PR 3763. This package checks the bit width and the subtraction.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
