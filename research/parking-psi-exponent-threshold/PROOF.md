# The strict parking hypothesis at the manuscript exponent

## 1. The pinned statement

`notes/batched-bit-rows.tex` fixes `m, W >= 2` and a child list
`t_1,...,t_J` of integers in `[1, m-1]`, and puts

```text
Psi(x) = (1/W) sum_{i=1}^J (t_i/m)^x,       t_* = max_i t_i < m.
```

It proves: if `Psi(tau) < 1` for some `0 < tau < 1`, then the normalized
recurrence `F(e) <= (1/W) sum_i F(t_i floor(e/m)) + C` satisfies
`F(e) = O(e^tau)`.

`upstream/build/sections/03-motifs.tex` displays the two relative rank
deficits

```text
eta_b = (W_b m - s_b)/(W_b m) = 339/22587335000000,
eta_c = (W_c m - s_c)/(W_c m) =  73/19906842167500,
```

fixes `tau = sigma = 1 - 2^-50`, and concludes `s_b/W_b < m^tau` and
`s_c/W_c < m^sigma` from

```text
eta > 20*2^-50      and      log m < 20.
```

`upstream/build/sections/04-swap.tex` states that the number of recursive calls
is the sum of the edge ranks, exactly `s`, and that each child has field width
`b = e/m`. So the schedule uses rank-one calls: `t_i = 1` for every term and
`J = s = sum_i t_i`.

## 2. The collapse on a rank-one node

**Lemma 1.** On a node with `t_i = 1` for all `i`, and
`1 - eta = s/(W m)` with `s = J`,

```text
Psi(tau) = (1 - eta) m^(1 - tau).
```

*Proof.* Every term is `(1/m)^tau`, so
`Psi(tau) = J m^-tau / W = (J/(W m)) m^(1-tau) = (1-eta) m^(1-tau)`. ∎

**Lemma 2.** For `0 < eta < 1` and `m >= 2`, the map
`tau -> (1-eta) m^(1-tau)` is strictly decreasing on `(0,1)`, and

```text
Psi(tau) < 1   <=>   tau > tau*(eta) := 1 - ln(1/(1-eta)) / ln m.
```

*Proof.* Strict decrease is immediate since `m^(1-tau)` is strictly decreasing.
For the equivalence,

```text
(1-eta) m^(1-tau) < 1
<=> m^(1-tau) < 1/(1-eta) = W m / s
<=> (1-tau) ln m < -ln(1-eta)
<=> tau > 1 - ln(1/(1-eta))/ln m.
```

All steps are equivalences because `1-eta > 0` and `ln m > 0`. ∎

A single exponent serves both recurrences, so the hypothesis holds jointly iff
`tau > max(tau*(eta_b), tau*(eta_c))`.

## 3. Exact brackets

Every quantity below is computed with rational arithmetic. `ln m` uses
`ln z = 2 atanh((z-1)/(z+1))` after the scaling `z = 2^e s`, `s` in `[1,2)`;
the series has positive terms and its tail is majorised by
`y^(2K+3)/((2K+3)(1-y^2))`. `-ln(1-eta)` uses its positive series with the
majorant `eta^2/(2(1-eta))`. `m^(2^-50) = exp(2^-50 ln m)` uses
`1+u <= e^u <= 1+u+u^2/(2(1-u))` for `0 <= u <= 1`. The verifier asserts every
inequality exactly and only then renders decimals.

With `m = 10^6`, `ln m = 13.815510557964274...` and `2^-50 ln m = 1.2270e-14`:

| quantity | exact bracket |
| --- | --- |
| `tau*(eta_b)` deficit | `[1.0863449905681094e-12, 1.0863449905762616e-12]` |
| `tau*(eta_c)` deficit | `[2.6543216407854528e-13, 2.6543216407903196e-13]` |
| `Psi_b(1-2^-50)` upper | `0.9999999999850038599515...` |
| `Psi_c(1-2^-50)` upper | `0.9999999999963451897731...` |

`RESULT.json` records the same brackets as truncated decimals together with the
two child counts, the two role counts and the two integer deficits.

## 4. Theorem

**Theorem.** Let `m = 10^6`, `tau = 1 - 2^-50`, and let the bit and complex
nodes carry the displayed deficits. Then

```text
Psi_b(tau) <= 1 - 1.4996140048450776e-11 < 1,
Psi_c(tau) <= 1 - 3.6548102269157696e-12 < 1.
```

The joint threshold is `tau* = tau*(eta_c) = 1 - 2.65432164079...e-13`, so the
admissible exponents are exactly the `tau` in `(tau*, 1)`. The manuscript's
`tau` clears the threshold by the factor `298.85`, and the margins above are
the exact distances to failure.

*Proof.* Lemma 1 gives `Psi` as a single monomial on each node. Lemma 2 turns
`Psi < 1` into a comparison of `2^-50 ln m` with `-ln(1-eta)`. The verifier
computes the brackets in §3 and checks

```text
(1-eta) * exp(2^-50 ln m) < 1
```

on both nodes before rendering any decimal, and checks
`tau > tau*(eta)` on both. The binding node is the one with the smaller
deficit, `eta_c`. ∎

## 5. Relation to the manuscript's displayed comparison

**Corollary.** The displayed comparison `eta > 20*2^-50` is sufficient but
strictly weaker.

- `20*2^-50 = 1.7763568394e-14`. Both deficits exceed it, by `844.90` and
  `206.44`.
- The exact first-order condition is `eta > 2^-50 ln m = 1.2269e-14`, so the
  constant `20` may be replaced by `ln m = 13.8155` even though the manuscript's
  own proof only yields `log m < 20`.
- The gap is real, not cosmetic: `tau = 1-2^-42` satisfies `Psi < 1` on both
  nodes but fails `eta > 20*2^-50` on the complex node, because
  `20*2^-42 = 4.547e-12 > eta_c = 3.667e-12`. The recorded control rejects
  that exponent under the displayed comparison and accepts it under the exact
  decision.

## 6. What this does not establish

This is one exact scalar inequality on each of two recurrences, under the
manuscript's own rank-one schedule. It does not reprove the transfer theorem,
does not change the manuscript's exponent, and does not address any supplier,
kappa or selected-frontier record. Two limits are worth naming.

- **The constant.** The `O(e^tau)` conclusion carries `C/(1-Psi(tau))`. At
  `Psi_b = 1 - 1.4996e-11` that factor is about `6.67e10`; at
  `Psi_c = 1 - 3.6548e-12` it is about `2.74e11`. The statement is asymptotic
  and says nothing about the finite base range `1 <= e < m`.
- **The rank-one hypothesis.** If a child list batches several rank units into
  one call, some `t_i > 1` and `sum_i (t_i/m)^tau` exceeds `s/(W m^tau)`;
  the displayed `s/W < m^tau` comparison would then no longer imply
  `Psi < 1`. Lemma 1 does not apply to such a list.

Independent human and formal proof-kernel review are unclaimed. Credit retains
the manuscript's `Psi` definition, deficit displays and exponent, and the
previous `research/uniform-parking-psi` package whose open question this
answers.
