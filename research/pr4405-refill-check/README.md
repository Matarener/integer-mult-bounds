# Independent check of #4405's refined template ranks and endpoint family

**Claim type:** an independent exact check plus a quantitative lever analysis. **No new κ.** It
checks 1337isnot1337's [#4405](https://github.com/CrocSwap/integer-mult-bounds/pull/4405), at head
`873d1b3c96a83b701a5c0bba8e37a861e6672fef`. That PR refines zxv's #4359:

- `TEMPLATE.md` (SHA256 prefix `3778e49c`) gives smaller explicit uniform ranks;
- `ENDPOINT.md` (`9b8d08cd`) gives a parameter family that admits every rational κ below the
  complex mixed root.

My #4404 audited #4359's original rank chain. Nothing is imported from #4405 or #4359, and the
invoices are embedded as printed in #4359.

## Results

**Part A: the refined ranks reproduce.** The refined induction requires only that the exit
coefficient satisfy `(16·n^{−h})^δ ≤ η = z0·m^{z0−1}`, not that it be at most `1/8 < η/2`. The
step is `L(n) ≤ A(n^{z0} − ηS + ηS)`, which is valid. With its own certified logarithms, the
verifier recomputes:

| | `H0` | `H1` | #4359's `H1` |
| --- | --- | --- | --- |
| Complex | 335,449 | 1,546,084,442 | 276,540,184,361 |
| BIT | 69,740 | 42,843,607 | 6,552,928,412 |

Both match #4405. Each `H0` is certified minimal, since one less fails for every value in the
log enclosure, and each `H1` is minimal. The endpoint's sufficient complex rank exponent,
2,099,384,703,303,215,709, also reproduces.

**Part B: #4405's suggested levers.** These answer `TEMPLATE.md`'s "next quantitative questions":

- **The intermediate `z0`.** A 199-point rational grid over `(t, z)` finds no `H1` below the
  midpoint's, in either family. The leading factor is `1/((z0−t)(z−z0))`, which is minimized at
  the midpoint, so optimizing `z0` gains nothing.
- **The exit constant 16.** Its `4δ` term is `1.2·10⁻⁴` of `H0` (complex) and `9.2·10⁻⁴` (BIT).
  Sharpening it is negligible.
- **The uniform saving.** This is the real lever. `H1` scales like `1/δ²`, where `δ` is half the
  gap between the tested mixed saving and the uniform saving:

  | Uniform saving | complex `H1` | BIT `H1` |
  | --- | --- | --- |
  | 0.002300 | 61,765,945 | 13,943 |
  | 0.002302 | 171,679,856 | 14,073 |
  | 0.002303 | 386,399,233 | 14,139 |
  | as used (0.002304 / 0.002760) | 1,546,084,442 | 42,843,607 |

  #4359 admits BIT at 0.0027 only so that it does not cap the complex supplier. A BIT uniform
  saving much closer to the complex one would therefore shrink the BIT rank to about `2^14000`.
  That would hold only if the cover fallback and conversion still leave BIT above the complex
  saving, which is not checked here.

**Part C: the endpoint family.**

- **The root bound.** The complex mixed moment at `C_test = 0.00230509019` is certified positive,
  about `4.7·10⁻⁷`, so `C_test < C*`. It is negative at 0.002306, so `C* < 0.002306`.
- **The gap identities.** These are all exact identities with strictly positive values at
  `κ = 0.00230509` and at 24 further rational κ between 10⁻⁷ and 0.0023:
  - `ξ = 29/32 + (1−d)q` and `εq = κ + d(3−q)`;
  - `λ−τ = d/2`, `λ−σ = 3d/2` and `λ'−λ = d/2`;
  - `(1−stop)b − a = d(1−b)`;
  - `ε − ξ = 3/32 − d − (1−d)q`;
  - `1 − (2ξ−2) − r0 − β = 3/16 − 2(1−d)q + 29d/10`;
  - the parameter order and the geometric gaps.

## Not covered

- The nine outer cost-row formulas themselves. Only the self-contained identities are checked.
- Native closure, adapters, the delayed cover and the BIT cover fallback.
- Whether a smaller uniform saving is admissible at the outer layer.

## Reproduce

```sh
python3.12 -B scripts/research_package.py --package research/pr4405-refill-check --check-only
python3.12 -B scripts/research_package.py --package research/pr4405-refill-check
```

The verifier prints `PASS_PR4405_REFILL_INDEPENDENT_CHECK` in about one second, using only the
standard library.

## Open next questions

1. **What is the smallest BIT uniform saving that still clears the complex binding row after the
   cover fallback and conversion?**
   - *Why it matters:* the BIT rank would drop from `2^42843607` to about `2^14000`.
   - *First step:* recompute #4359's BIT fallback bill as a function of the uniform saving and
     of `N`.
   - *Blocked by:* the fallback formula in `DELAYED-COVER-BRIDGE.md`.

## Credit

- The refinement and endpoint family are 1337isnot1337's (#4405).
- The construction and invoices are zxv's (#4359).
- Theorem 1G is Jacob Alan Sussman's (#4268).

Prepared by Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
