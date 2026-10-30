# Sharp exponent threshold for the two motif parking recurrences

The pinned note defines, for a child list `t_1..t_J` with integer widths in
`[1,m-1]` and a role count `W`,

```text
Psi(x) = (1/W) sum_{i=1..J} (t_i/m)^x,
```

and proves that `Psi(tau) < 1` for some `0 < tau < 1` gives `F(e) = O(e^tau)`
for the normalized recurrence. The manuscript then fixes one rational exponent
for both motif recurrences,

```text
tau = sigma = 1 - 2^-50,
```

displays the two relative rank deficits

```text
eta_b = 339/22587335000000,      eta_c = 73/19906842167500,
```

and establishes `s_b/W_b < m^tau` and `s_c/W_c < m^sigma` through the
sufficient comparison `eta > 20*2^-50` together with `log m < 20`.

The manuscript's schedule makes every child a rank-one call, so `t_i = 1` for
every term and `J = s = sum_i t_i`. On such a node the strict hypothesis is not
merely sufficient but decidable:

```text
Psi(tau) = (1 - eta) m^(1 - tau),
```

because `s/(W m) = 1 - eta` and `sum_i (1/m)^tau = s m^-tau`. This package
computes the exact threshold

```text
Psi(tau) < 1   <=>   tau > tau*(eta) := 1 - ln(1/(1-eta)) / ln m
```

and evaluates it on the two displayed nodes. For `m = 10^6`:

| node | `eta` | `Psi(1-2^-50)` (upper bound) | `tau*` deficit bracket |
| --- | --- | --- | --- |
| bit | `339/22587335000000` | `1 - 1.4996140048450776e-11` | `[1.0863449905681094e-12, 1.0863449905762616e-12]` |
| complex | `73/19906842167500` | `1 - 3.6548102269157696e-12` | `[2.6543216407854528e-13, 2.6543216407903196e-13]` |

A single exponent serves both recurrences, so it must exceed the larger
threshold. **The complex node binds**, at `tau* = 1 - 2.65432...e-13`, and the
manuscript's `tau = 1 - 2^-50` clears it by a factor `298.85`. Both strict
hypotheses therefore hold, and the exact margins are `1.50e-11` (bit) and
`3.65e-12` (complex).

## What this changes

- **It answers the open question of the previous package.** `uniform-parking-psi`
  evaluated the bit node at `tau = 1/2`, found `Psi = 22587334999661/22587335000 > 1`,
  and asked whether the same node has `Psi < 1` at the manuscript's exponent.
  It does: `Psi(1-2^-50) <= 1 - 1.4996e-11`. The `1/2` evaluation is a
  legitimate statement about a stronger exponent; it says nothing against the
  manuscript's choice.
- **It replaces the displayed constant.** The manuscript uses `20*2^-50`
  because `log m < 20`. The exact condition is `eta > 1 - m^(tau-1)`, whose
  first-order form is `eta > 2^-50 log m` with `log m = 13.8155...`. The
  displayed constant is therefore conservative by a factor
  `20/log m = 1.4476`; on the two deficits it has slack `844.9` (bit) and
  `206.4` (complex).
- **It shows the displayed comparison is strictly weaker than the truth.** The
  exponent `1-2^-42` satisfies `Psi < 1` on both nodes but fails
  `eta > 20*2^-50` on the complex one. The exact threshold, not the displayed
  constant, is what the recurrences support.

## Evidence

- `verify.py` authenticates the three pinned manuscript inputs by SHA-256,
  re-derives `m`, `s_b`, `s_c`, `eta_b`, `eta_c` from their displayed forms,
  checks that `s/(1-eta)` is an integer multiple of `m`, and computes rigorous
  rational brackets: `ln m` from the atanh series with a geometric tail bound,
  `-ln(1-eta)` from its positive series, and `e^u` from `1+u <= e^u <=
  1+u+u^2/(2(1-u))`. Every comparison is exact; `RESULT.json` holds truncated
  decimal renderings of the brackets.
- `independent.py` shares no series and no logarithm. It proves the same
  conclusion from the manuscript's own two displayed facts and two elementary
  inequalities: `20*2^-50 < eta` by integer cross-multiplication, `log m < 20`
  from `m < 2^20` and `2 < e`, and `e^x <= 1/(1-x)`. It also brackets the
  threshold coarsely with `log m` in `(13,20)`.
- `test_controls.py` runs twelve mutation groups. Ten are rejected, including
  the deficits scaled down, `tau = 1/2`, `tau = 1`, and the sharp boundary pair
  `1-2^-38` (rejected) against `1-2^-42` (accepted). Two positive runs check
  that a larger modulus and a finer admissible exponent still pass the exact
  decision.

## Reproduction

```sh
python3.12 -B research/parking-psi-exponent-threshold/verify.py
python3.12 -B research/parking-psi-exponent-threshold/independent.py
python3.12 -O -B research/parking-psi-exponent-threshold/test_controls.py
python3.12 -B scripts/research_package.py --package research/parking-psi-exponent-threshold
```

`verify.py --emit` rewrites `RESULT.json` from the computation.

## Scope and limits

This is an exact statement about one scalar inequality per recurrence. It does
not reprove the transfer theorem, does not change the manuscript's exponent,
and does not touch any supplier, kappa or selected-frontier record. The
`O(e^tau)` conclusion carries the constant `C/(1-Psi(tau))`, which at these
margins is about `6.7e10 C` on the bit node and `2.7e11 C` on the complex node;
the bound is asymptotic and this package says nothing about the finite base
range. The identification `J = s` uses the manuscript's rank-one schedule; a
batched child list with some `t_i > 1` would need its own evaluation, and the
displayed `s/W < m^tau` comparison would then no longer imply `Psi < 1`.

## Open next questions

- Does a batched child list (`t_i > 1` for some calls) also meet the strict
  hypothesis at `tau = 1-2^-50`? The displayed `s/W` comparison does not decide
  it, and `sum_i (t_i/m)^tau` is larger than `s/(W m^tau)` when `t_i > 1`.
- Can the surrounding proof use a smaller exponent? The exact threshold admits
  every `tau` in `(1-2.6544e-13, 1)`, so `1-2^-41` is admissible for both
  nodes whereas `1-2^-38` is not; whether any downstream constant improves is
  not established here.

## Credit

The `Psi` definition, the strict hypothesis, the rank-one parking schedule, the
two relative deficits, the exponent `tau = 1-2^-50` and the displayed
comparison are the manuscript's, pinned by Git blob in
[SOURCES.json](SOURCES.json). The previous package
`research/uniform-parking-psi` (merged as PR3528) stated the `1/2` evaluation
and left the manuscript exponent as its open question. Nick Petalas.
Apache-2.0. No literature priority is claimed.
