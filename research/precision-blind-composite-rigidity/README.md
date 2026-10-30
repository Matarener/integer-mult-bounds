# Composite moduli: antidiagonal rigidity of precision-blind dual scales

**Scoped exact lemma; no new kappa.** #4073 classified dual-scale supports for odd prime powers and left composite odd moduli open. The same far/near count is not the new fact. The new fact is why the count is stable, and when the single-factor obstruction flips.

For every odd modulus `M≥3` and every odd length `n≥3`, a unit weight `a=(a0, middles, 1)` with `a0≢1` admits an involutory dual-scale target on exactly two supports when the middles are reciprocal, and on none otherwise:

- far end `(H'_{n-1}, D'_0)` with scales `(a0^{-1}, a0)` and target `(a0, middles, a0^{-1})`
- near end `(H'_0, D'_{n-1})` with the same scales and target `(1, middles, 1)`

Off the antidiagonal `j=n-1-i`, both scales are forced to `1`, so a dual scale cannot change a weight. A shared single-factor scale exists on the two ends if and only if `a0²≡1`. Such an `a0` outside `{±1}` exists if and only if `M` is not an odd prime power: the Chinese remainder theorem builds it from any coprime split, and `gcd(a0-1, M)` recovers a split from any nontrivial solution of `x²=1`. On an odd prime power the valuations of `x-1` and `x+1` cannot split, so the only solutions are `±1`, and `1+p^{k-1}` stays single-factor free.

This is the composite-modulus answer to #4073 OQ1. It does not reprint the n=5 or n=7 prime-power grids, and it carries no Boolean meter inventory. Selected κ stays `0.001672660197076918`.

## Reproduction

```sh
python3.12 -I -B research/precision-blind-composite-rigidity/verify.py
python3.12 -I -O -Werror -B research/precision-blind-composite-rigidity/verify.py
python3.12 -I -B research/precision-blind-composite-rigidity/independent.py
python3.12 -I -B research/precision-blind-composite-rigidity/test_package.py
python3.12 -B scripts/research_package.py --package research/precision-blind-composite-rigidity
```

Expected markers:

```text
PASS_PRECISION_BLIND_COMPOSITE_RIGIDITY composites=7 defects=4 illegals=3 prime_powers=5 single_factor_iff_square=true prime_power_only_pm1=true boolean_meters=false no_new_kappa
PASS_INDEPENDENT_PRECISION_BLIND_COMPOSITE_RIGIDITY checks=13 single_factor_iff_square=true boolean_meters=false no_new_kappa
PASS_PRECISION_BLIND_COMPOSITE_RIGIDITY_PACKAGE_TESTS groups=5
PASS_REGISTERED_RESEARCH_PACKAGE research/precision-blind-composite-rigidity outcome=completed
```

Default verify is read-only. Admission uses `need()` and still fires under `-O`. `--write` is the only regenerator.

## Overlap

Closest prior is [#4073](https://github.com/CrocSwap/integer-mult-bounds/pull/4073) (`research/precision-blind-odd-n-support`), which proves far/near exclusivity for odd prime powers by a support census on n=5 and n=7. [#4072](https://github.com/CrocSwap/integer-mult-bounds/pull/4072) and [#4070](https://github.com/CrocSwap/integer-mult-bounds/pull/4070) are the n=3 and n=2 prime-power cases. [#2950](https://github.com/CrocSwap/integer-mult-bounds/pull/2950) supplies the reciprocal-middle condition. The load-bearing step here is the antidiagonal forcing, which is what makes the composite modulus and the single-factor flip theorems rather than another grid. Soft overlap is the shared `F_a` vocabulary, not a retarget of those certificates.

## Credit

Credit [#4073](https://github.com/CrocSwap/integer-mult-bounds/pull/4073) for the odd prime-power classification and for leaving composite moduli open; [#4072](https://github.com/CrocSwap/integer-mult-bounds/pull/4072) and [#4070](https://github.com/CrocSwap/integer-mult-bounds/pull/4070); Jerry Chen (@CubeJerry) / [#2950](https://github.com/CrocSwap/integer-mult-bounds/pull/2950) for Theorem 1. Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao), [@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under Apache-2.0.

## Open next questions

1. What is the paid Boolean inventory of one composite single-factor fixture, for example `M=15` and `a0=4`? Existence of the scale is not a gate or frame-copy bill, and a thin meter retarget is out of scope.
2. Does the same rigidity classify even lengths? Even `n` is left with [#4070](https://github.com/CrocSwap/integer-mult-bounds/pull/4070) and is not claimed here.
