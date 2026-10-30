# The FFT invoice terms stay within 256, 512 and 64

**Partial. No new exponent.**

For a width `n >= 3`, write `beta = ceil(log2 n)`, `q = ceil(n/beta)`,
`ell = ceil(log2(2q))`, `r = 2^ell` and `p0 = 2 beta + ell`. Every such
width through `2^20` satisfies

```text
r beta < 8n,
ell + 1 <= 2 beta,
p0 <= 4 beta,
beta <= n.
```

Replacing the scalar power `8/5` by the larger square, the three setup terms
are then at most

```text
r(ell+1)p0^2 <= 256 n beta^2,
r p0^3       <= 512 n beta^2,
p0^3         <= 64 n beta^2.
```

The products of the stated factors are exact:

```text
(8n/beta)(2 beta)(4 beta)^2 = 256 n beta^2,
(8n/beta)(4 beta)^3         = 512 n beta^2,
(4 beta)^3                  = 64 beta^3 <= 64 n beta^2.
```

All 1,048,574 widths from 3 through 1,048,576 meet the comparisons. The
selected kappa is unchanged.

## What was executed

The checker builds the digit geometry and compares the three terms. It does
not run the word multiplier.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the time paragraph of PR 3787,
head `9b5474f47b0ea9a3c76bb5b1b577fb36704815e0`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to
these constants. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/fft-time-constants/verify.py
python3.12 -B research/fft-time-constants/test_verify.py
python3.12 -B scripts/research_package.py --package research/fft-time-constants
```

## Open next questions

Every width through 2^20 meets the three comparisons, and the constant
products are exact. A word-multiplier replay would leave this package.

## Credit

Jose Manuel (jmbarrancoml) stated these multiples in PR 3787. This package
checks them on the published digit geometry.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
