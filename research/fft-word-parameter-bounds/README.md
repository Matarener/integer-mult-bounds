# The FFT word parameters keep one spare coefficient bit

**Partial. No new exponent.**

For a width `n >= 2`, let `beta = ceil(log2 n)`, `B = 2^beta` and
`q = ceil(n/beta)`. The ring length `r = 2^ell` is the least power of two
that is at least `2q`, so

```text
2q <= r < 4q,    r * beta >= 2n,    ell >= 1.
```

The normalized precision is `p0 = 2 beta + ell`, and `2^p0 = r B^2`. The
ordinary product has degree at most `2q - 2`, which is strictly below `r`,
so the ring product does not wrap. A coefficient of that product is at most
`q(B - 1)^2`. That quantity is strictly below `q B^2`, and

```text
q B^2 <= r B^2 / 2 = 2^(p0 - 1).
```

Every coefficient therefore has a spare leading bit on the signed `p0`-bit
grid. These relations hold for every width from 2 through 65536 and at width
1000000.

The direct scalar screen at `rho = 1/500` is `8/5 - rho = 799/500`, which is
greater than 1. Absorbing a logarithm at `delta = 1/10000` produces

```text
1 - rho + delta = 9981/10000.
```

The inherited Fourier power is `99827619697/100000000000`. The positive gap
is `17619697/100000000000`. The series bound `e < 3 < 4` gives `ln 2 > 1/2`,
which is the constant used to absorb `log2(n+2)^2` by `24 delta^(-2) n^delta`.
The selected kappa is unchanged.

## What was executed

The checker tests the digit relations at the listed widths and compares the
three rationals. It does not run the word multiplier.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the parameter schedule in PR
3787, head `9b5474f47b0ea9a3c76bb5b1b577fb36704815e0`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to
these bounds. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

Overlap search on 2026-10-18T21:04Z covered 494 open pull requests and 2,509
discussions. The matches are earlier uses of this card. This package changes
the question to the FFT digit bounds.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/fft-word-parameter-bounds/verify.py
python3.12 -B research/fft-word-parameter-bounds/test_verify.py
python3.12 -B scripts/research_package.py --package research/fft-word-parameter-bounds
```

## Open next questions

These bounds are the parameter comparison. A word-multiplier replay would
leave them.

## Credit

Jose Manuel stated the digit schedule, the spare-bit headroom and the
absorbed power.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
