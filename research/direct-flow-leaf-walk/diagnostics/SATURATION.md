# Diagnostic: the predicted saturation, observed by importance sampling

The walk is monotone, because every step `ln r ≥ 0`. So the leaf law is exactly the `G`-fold tilted
P-product restricted to `S_G ≤ B`, where `B = G ln 5` at level starts. `saturate.py` (numpy, about
1 minute) samples `S_G` as a multinomial sum at the Esscher tilt whose mean is `B/G`. It reweights by
`e^{λ(S−B)}`, and estimates the conditioned overshoot `E[B − S_G | S_G ≤ B]` from 400,000 samples per
row.

| G | 50 | 200 | 1,000 | 4,000 | 16,000 | 64,000 | 256,000 | 10⁶ |
| --- | --- | --- | --- | --- | --- | --- | --- | --- |
| overshoot | 8.01 | 15.54 | 32.01 | 55.16 | 84.73 | 111.53 | 125.74 | 131.66 |

- **The limit.** The overshoot tends to `1/λ* = 133.35`, as predicted.
- **Consistency with the exact data.** At `G ≈ 50` the exact computation gives
  `D − (ln m − μ) ≈ 11.10 − 3.17 = 7.93`, consistent with the sampled 8.01.
- **The crossover.** It sits near `G× ≈ 8,100`, as predicted.

## Refined estimates

These keep the measured shares (leaf about 0.914, boundary depth about 1.84, source depth about 2.45).

- **The limit:** `g∞ ≈ 0.914·(3.17 + 133.35) − 2.29 ≈ 122.5`, so the cap is
  `s*·g∞/(g∞ + 5.796) ≈ 0.00257`.
- **Saving 0.0023:** this needs `g ≈ 34.5`, an overshoot of about 37, so `G ≈ 1,340` and
  `N ≈ 121·5^{1340} ≈ 10^{940}`. That replaces the README's rougher `10^{700}`.
