# The FFT carry recovers the integer product

**Partial. No new exponent.**

Split an integer of width `n` into `q` digits of `beta` bits, with
`B = 2^beta`. The convolution digits are

```text
c_i = sum_(j+k=i) a_j b_k.
```

The carry scan starts at `K_0 = 0` and sets

```text
z_i = c_i + K_i,
d_i = z_i mod B,
K_(i+1) = floor(z_i / B).
```

The update identity `c_i + K_i = d_i + B K_(i+1)` keeps

```text
sum_(i<m) d_i B^i + K_m B^m = sum_(i<m) c_i B^i.
```

If `K_i <= q(B-1)` and `c_i <= q(B-1)^2`, the next carry satisfies the same
cap, because

```text
(q(B-1)^2 + q(B-1)) / B = q(B-1)
```

exactly. After `r` digits, with `r` at least the product degree, the value
`ab` is below `B^r`, so the final carry is 0 and the digits `d_i` are `ab`.

Every pair of integers of width 2 through 10 was recovered on the published
FFT geometry: 1,398,096 products. The same division was checked for every
base from 2 through 256 and every digit count from 1 through 256. The
selected kappa is unchanged.

## What was executed

The checker builds the convolution, runs the carry, and compares the digit
word with the product. It does not run the word multiplier.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the carry section of PR 3787,
head `9b5474f47b0ea9a3c76bb5b1b577fb36704815e0`.

## Scope and evidence

Original card: `uniform-transfer-audit`, priority revision 6, refined to this
recovery. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the selected record. No selected frontier
file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/fft-carry-recovery/verify.py
python3.12 -B research/fft-carry-recovery/test_verify.py
python3.12 -B scripts/research_package.py --package research/fft-carry-recovery
```

## Open next questions

The carry invariant is an integer identity and every product of width at
most 10 was recovered. A word-multiplier replay would leave this package.

## Credit

Jose Manuel (jmbarrancoml) stated this carry in PR 3787. This package checks
the reconstruction on the published digit geometry.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
