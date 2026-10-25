# Coefficient-bit tariff for odd-kernel ADDRESS lowerings

## Claim

Let `address_word(k)` be the seven-event ADDRESS lowering of
`M(k)=I+(k/4)sr^T` used by PR840 / `#2687`. Define the **coefficient-bit
tariff**

```text
T_word(k) = Σ_{c = p/q in affine coeffs} ( bit_length(|p|) + bit_length(q) )
```

with each `c` in lowest terms. For kernel `q` and dyadic index `j`,

```text
T_fused(q,j)     = 2·T_word(q·2^j) + T_word(q·2^{j+1})
T_baseline(q,j)  = 4·T_word(q·2^j)
```

matching the three-query fused and four-query separate power lists. Then for
every certified odd kernel `q ∈ {3,5,7,9,15}` and every `j ∈ {0,…,32}`:

```text
T_fused(q,j) > T_fused(1,j)
T_baseline(q,j) > T_baseline(1,j).
```

Typed child / affine / XOR counts remain `3/18/2` (fused) and `4/24/4`
(baseline) independent of `q`. Therefore, on this named tariff, larger-`q`
coefficient tables never pay for themselves against the dyadic path.

Selected kappa is unchanged.

## Closed form for `T_word`

The affine coefficients of `address_word(k)` are ten units `±1` together with

```text
a, 1+a, -a, -a, -1/a, 1/a - 1     where a = k/4.
```

Each unit contributes `bit_length(1)+bit_length(1)=2`, so

```text
T_word(k) = 20 + bits(a) + bits(1+a) + 2·bits(a) + bits(4/k) + bits((4-k)/k)
```

with `bits(p/q)=bit_length(|p|)+bit_length(q)`. The formula is sign-invariant
(`T_word(k)=T_word(-k)`) and matches direct enumeration on `|k|≤64`.

## Non-monotonicity

`T_word` is **not** monotone in `|k|`:

```text
T_word(4) = 32 < T_word(2) = 38 < T_word(1) = 45.
```

A word-level “larger `|k|` ⇒ larger bill” argument is false. The claim is the
fused/baseline program comparison on the certified kernel grid, not word
monotonicity.

## Grid evidence

For each of the `5×33 = 165` odd pairs `(q,j)` the verifier checks fused and
baseline strict exceedance separately (`165` comparisons each). Spot values at `j=2`:

| q | T_fused(q,2) | T_baseline(q,2) |
|---:|---:|---:|
| 1 | 102 | 128 |
| 3 | 126 | 160 |
| 5 | 145 | 184 |
| 7 | 147 | 188 |
| 9 | 166 | 212 |
| 15 | 168 | 216 |

Fusion saves coefficient bits for every kernel, but the odd fused bill remains
strictly above the dyadic fused bill on the whole grid.

## Relation to `#2687` / PR840

`#2687` proved the excluded-prime admission pattern and recorded identical
typed invoices for all odd `q`, leaving open whether coefficient-table
bit-sizes can still favor some `q` under a concrete physical tariff. This
package attaches one named tariff to the same `address_word` and answers that
obligation in the negative on `j=0..32` for the certified kernels.

## What this does not claim

- No alternate tariff (max-height only, packing, modulus-dependent encoding).
- No BIT-supplier hosting bill (still `#2687` OQ1).
- No new kappa and no production adoption.
