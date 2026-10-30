# A within-cell column budget for the downward gauge

**Claim type:** a written transfer inside one phase cell. **No new κ.**
This is the within-cell half of the open question in #4437. It does not bound
entries that cross a cell, and it does not edit the #4100 notes.

## Question

Inside one cell the rounded block is

```text
A = diag(ahat) Ghat diag(ahat)^{-1},
```

so a column is multiplied by the weight ratios `ahat_j / ahat_k`. Those ratios
do not preserve the ideal column sums. Which relative error still leaves a
column gap of size `1/(16p^2)`?

## Lemma

Inside a cell, `β_{i+h} = β_i + θ h` and `ρ = 1+θ`. The ideal entry factors as

```text
N_{i,i+h} = (a_i / a_{i+h}) exp(-a ρ h^2),
```

where `log(a_i/a_j) = a(i-j)(β_i+β_j)` is the gauge audit's identity. Thus the
bare kernel `G_h = exp(-a ρ h^2)` is symmetric and Toeplitz.

Suppose the rounded data satisfy `Ghat_0 = 1`, `0 ≤ Ghat_h ≤ G_h`, and

```text
(1-ε) a_i ≤ ahat_i ≤ a_i
```

with `0 ≤ ε < 1`. Every within-cell column then has off-sum at most the ideal
column off-sum divided by `1-ε`, and its diagonal entry is 1.

Take the ideal off-sum to be at most `1 - 1/(8p^2)`, which #4402 gives
eventually inside a constant-phase run. The sufficient budget is

```text
ε ≤ 1/(16p^2).
```

The rounded column gap is then at least `1/(16p^2 - 1)`, hence strictly above
`1/(16p^2)`. The gauge audit's stated allowance `ε ≤ 1/2` does not give this:
it multiplies the ideal off-sum by 2, and `2(1 - 1/(8p^2)) > 1`.

`GAUSSIAN.md` writes a relative error `< 2^{-C p}` for an unnamed positive
setup constant `C`. The smallest value that meets `ε ≤ 1/(16p^2)` for every
integer `p ≥ 2` is `C = 3`. At `p = 2` the powers are equal, and the note's
inequality is strict. `C = 2` fails at `p = 2`, where `2^{-4} = 1/16` and the
budget is `1/64`. This does not assert that the note's `C` is at least 3.

## Proof

The cell law `β_{i+h} = β_i + θ h` gives

```text
(ρ h + β_i)^2 - β_{i+h}^2 = (1+2θ) h^2 + 2 β_i h.
```

The gauge identity contributes `log(a_i/a_{i+h}) = -a h (2 β_i + θ h)`.
Subtracting that logarithm from the ideal exponent cancels `β_i` and one
factor of `θ`, and leaves `-a(1+θ) h^2`. The kernel depends only on `h`.

A rounded entry is

```text
(ahat_i / ahat_{i+h}) Ghat_h
    = (r_i / r_{i+h}) (a_i / a_{i+h}) Ghat_h,
```

with `1-ε ≤ r ≤ 1`. Downward rounding gives `Ghat_h ≤ G_h`, so the entry is
at most `N_{i,i+h} / (1-ε)`. Summing a column multiplies the ideal off-sum by
at most `1/(1-ε)`. The diagonal ratio is 1.

If the ideal off-sum is at most `1 - γ` with `γ = 1/(8p^2)` and
`ε = γ/2 = 1/(16p^2)`, the rounded gap is at least

```text
(γ - ε) / (1 - ε) = 1/(16p^2 - 1) > 1/(16p^2).
```

For `ε = 1/2` the comparison becomes `2(1-γ) = 2 - 1/(4p^2) > 1`.

The same budget in exponential form is `2^{C p} ≥ 16 p^2`. Equality holds at
`C = 3`, `p = 2`. For `p ≥ 2`, `(p+1)/p ≤ 3/2` and `(3/2)^2 = 9/4 < 8 = 2^3`,
so the inequality persists and is strict after `p = 2`. At `C = 2` and `p = 2`,
`2^4 = 16 < 64`.

A row-sum bound does not replace this argument. The downstream estimate is a
row bound, `||H-N|| < p · 2^{16p+7} η + 2^{-46p}`. Charging every one of the
`2p-1` band entries with a row mass `1/(16p)` produces a column change
`(2p-1)/(16p)`. That exceeds `1/(8p^2)` for every integer `p ≥ 2`, since
`p(2p-1) > 2`.

## Not covered

- Entries across a cell. The downstream note uses the downward dyadic
  approximation of the original entry there, not the ratio
  `ahat_j Ghat_(j-k)/ahat_k`.
- The claim that the written setup constant already satisfies `C ≥ 3`.
- `||A^{-1}||_2`, the exponents in #4406, and any new κ. The selected record
  remains `23/10000`.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/gaussian-gauge-column --check-only
python3.12 -B scripts/research_package.py --package research/gaussian-gauge-column
```

Base `2a13eb1827784206202db90e5dc8327cf8a250db`, priority revision 7, selection
refresh κ = `23/10000`.

Overlap on 2026-10-21 found no statement of this relative-error budget. The
search hit unrelated defect ledgers. #4402 supplies the in-cell ideal column
gap. #4437 extends that gap across a `g = 2` step and leaves this gauge
question open. A search miss is not a novelty certificate.

## Open next questions

1. **Do the exponents 12, 26, 28, 28 and 7 apply inside one cell once `ε ≤ 1/(16p^2)`?**
   Both gaps are then above `1/(16p^2)`, which is the ceiling #4406 used.
   The first step is the Neumann bound #4402 already wrote, applied to this
   rounded block. The global reference is still blocked because its
   across-cell entries are the downward original entries, not this ratio.

## Credit

- The gauge identity and the one-sided weight inequality are the capped-gauge
  audit's, from PR1673.
- The in-cell column gap is Ryanson Jonathan's #4402.
- The row perturbation that does not transfer is the downstream phase-cell note's.
- #4437 asked for this column after the ideal `g = 2` bound.

Prepared by James Reed with substantial Cursor Grok 4.7 assistance. Apache-2.0.
