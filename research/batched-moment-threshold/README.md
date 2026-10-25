# Direct enclosures and sharp thresholds for the two batched moment bounds

**Independent arithmetic verification plus new quantitative coverage. No new
kappa, supplier or selected-frontier change.**

PR #10's batched interchange ("Batch recursive networks for a conditional
`kappa = 6149999/50000000000000 > 2^-23`") chooses its two recursive savings
because two displayed child-list moments are strictly below one:

```text
Psi_b(1 - 246/10^9) < 1        (bit side, controlled-basis child list)
Xi_c(1 - 7/10^7)    < 1        (complex side, whole-residual recursion)
```

The pinned certificates prove these through one sufficient route:

```text
Psi(1 - a) = sum_i w_i exp(a ln(1/r_i))
           <= sum_i w_i / (1 - a ell_i) < 1,      ell_i >= ln(1/r_i),
```

with rational log upper bounds `ell_i` and `e^x <= 1/(1-x)`. The registered
tests check that route and a failure at ten times each saving, but nothing
retained reports the direct margin or where each moment actually crosses one.

This package recomputes both inequalities **directly** with its own rational
enclosures and outward rounding, then locates each **sharp moment threshold**.

## Certified result

Both child lists are rebuilt from the pinned counts, not copied from the
stored weights: `m = 21952`, `h = 28`, the bit classes
`{784, 21840, 20384, 20330}` with multiplicities `{B, B, B, 2N}`, the complex
classes `{21896, 21168}` with `B_c` copies each, and the exact `eta` values
`39/520019360` and `5/12693352` are all re-checked.

| Quantity | Bit side | Complex side |
|---|---:|---:|
| Published saving | `246/10^9` | `7/10^7` |
| Certified direct moment upper bound | `0.9999999999490327` | `0.9999999841659643` |
| Certified direct margin (lower bound) | `5.0967e-11` | `1.5834036e-8` |
| Pinned sufficient gap (recomputed) | `4.7601965e-11` | `1.5818274e-8` |
| Sharp threshold (certified bracket) | `2.46167292e-7` | `7.29316527e-7` |
| Published saving below its threshold by | `0.068%` | `4.19%` |

Both published inequalities **hold**, now certified by a second, independent
method. The direct margins agree with the pinned sufficient gaps to within 7%
(bit) and 0.1% (complex), so the sufficient route loses almost nothing on
these two child lists: there is no hidden order-of-magnitude slack in the
certificates. What is new is the sharp crossing: the bit saving `246/10^9` sits
`0.068%` below the largest saving its displayed moment admits, and the complex
saving `7/10^7` sits `4.19%` below its own.

The enclosure method is stdlib-only: `ln` by power-of-two reduction plus an
atanh series with an explicit rational tail bound, `exp` by a positive Taylor
partial sum with a remainder bounded by twice the next term. Both directions
round outward, so every stored decimal is a certified bound. Precision is set
by the series lengths, not by a floating-point context: the direct intervals
are about `1e-60` wide after 64 log terms and 20 exponential terms.

## What this does not establish

- **The sharp threshold is a moment-only quantity.** It is the largest `a`
  with the displayed weight/ratio list still satisfying `Psi < 1`. It is *not*
  a claim that the assembly may raise either saving: the absorption gaps,
  compact-control exponents, depth and row reservations, the controlled-basis
  existence argument and every all-size premise are untouched and unexamined
  here. The assembly's selected `kappa` is unchanged.
- No network, census or tape machine is replayed. The child lists are taken
  from the pinned certificates; only their arithmetic is certified.
- The intermediate bit saving `177/10^9` and the retained PR #7 / F3 producer
  obligations are not re-derived. `logarithm_enclosures` and the weight
  identities are checked; the geometric class assignments behind them are not.
- Independent human or formal-kernel review is unclaimed.

## Reproduce

From the repository root, CPython 3.12, standard library only:

```sh
python3.12 -B research/batched-moment-threshold/verify.py
python3.12 -B research/batched-moment-threshold/test_verify.py
python3.12 -B scripts/research_package.py --package research/batched-moment-threshold
```

`verify.py` prints
`PASS_BATCHED_MOMENT_THRESHOLD bit_margin>=0.000000000050967300444702662660 complex_margin>=0.000000015834035766876648682217 no_new_kappa`
and compares every field against the generated `RESULT.json`.
`test_verify.py` prints `PASS_BATCHED_MOMENT_THRESHOLD_TESTS`. Both runs take
under a minute.

## Open next questions

1. Can the same direct enclosure certify the intermediate bit saving
   `177/10^9` (reported gap `> 1.78e-10`) and its smaller class list? The
   intermediate certificate JSON is not on canonical main.
2. Which other assembly constraint binds first? Comparing each margin in
   `certificates/batched-network.json` with the distance from its published
   saving to the moment threshold would say whether the moment or another
   parameter is the real limiter; that needs the full assembly derivation,
   which this package deliberately does not replay.

## Credit

icekylinx supplied PR #10, the batched-recursive-network proposal, its notes
and both pinned certificates, and the controlled-basis improvement from
`177/10^9` to `246/10^9`. Douglas Colkitt supplied the repository review guide
and workflow. The retained PR #7 and F3 producer lineage, the projector
batching and controlled-basis notes, and the Gaussian input correction keep
their own attribution in those sources.

This contribution was produced by Nick Petalas with AI assistance.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.
