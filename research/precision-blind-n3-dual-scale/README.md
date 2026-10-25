# n=3 precision-blind dual-scale Norm on end support

**Research construction / recursive interface; no new kappa.** Answers open
question 1 of just-open
[#4070](https://github.com/CrocSwap/integer-mult-bounds/pull/4070)
(`research/precision-blind-dual-scale-existence/`): does the dual-scale
reciprocal construction extend to precision-blind lists of length `n>2` with
middle coordinates forced to `±1`?

**Yes for `n=3`**, with a **new support analysis**:

- Precision-blind weights `a=(a0, m, 1)` on `G=(Z/p^w Z)^3` with
  `a0=1+p^{w-1}` and `m∈{+1,-1}`.
- **Naive copy of the n=2 support** `(H'_1,D'_0)` never yields an involutory
  target `P'` (forces `p0=a0` and `p2=1`, so `p0·p2=a0≢1`).
- **End support** `(H'_2,D'_0)` with dual scales `(a0^{-1}, a0)` realizes
  `F_{(a0,m,a0^{-1})}` with `(P')²=I`; the middle coordinate is never scaled.
- Shared single-factor scale on that end support remains obstructed
  (`a0≢±1`).
- `a0` is always a unit quadratic residue; existence uses invertibility.

Algebraic for all odd `p`, `w≥2`, both middles. Certificate grid: 30 rows
(15 moduli × 2 middles). **No Boolean meter inventory. No reprint of the
#4070 15-pair n=2 census or M=9 meters. No new kappa.** Selected κ stays
`0.001672660197076918`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/precision-blind-n3-dual-scale/verify.py
python3.12 -I -O -Werror -B research/precision-blind-n3-dual-scale/verify.py
python3.12 -I -B research/precision-blind-n3-dual-scale/independent.py
python3.12 -I -B research/precision-blind-n3-dual-scale/test_package.py
python3.12 -B scripts/research_package.py --package research/precision-blind-n3-dual-scale
```

Expected:

```text
PASS_PRECISION_BLIND_N3_DUAL_SCALE pairs=30 primes=[3, 5, 7, 11, 13, 17, 19, 23] widths=[2, 3, 4, 5] support=(H'_2,D'_0) middles=±1 single_factor=0 naive_n2=0 square=always dual_scales=inv boolean_meters=false n2_census=false no_new_kappa
PASS_INDEPENDENT_PRECISION_BLIND_N3_DUAL_SCALE pairs=30 support=(H'_2,D'_0) middles=±1 single_factor=0 naive_n2=0 square=always dual_scales=inv boolean_meters=false n2_census=false no_new_kappa
PASS_PRECISION_BLIND_N3_DUAL_SCALE_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/precision-blind-n3-dual-scale outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()` (not `assert`); `-O` / `-Werror` also pass.

## Scope and overlap

Base commit `20ecf2891d80b5acf18d980b2164fb44ea7faa90` (CrocSwap/main tip).
Direct predecessor: [#4070](https://github.com/CrocSwap/integer-mult-bounds/pull/4070)
OQ1 (n=2 dual-scale existence). Soft overlap vs #4070 harness ≈0.25–0.45, but
the load-bearing delta is the **n=3 end-support lemma and naive-support
obstruction**, not a reprint of the n=2 census or Boolean meters. Clear of
#4063/#4053 meter leave-alones, #2687 odd-kernel BIT-supplier DEFERs, and
#2888 F_I GL2(F3) toy cluster.

## Open next questions

1. Does the same end-support pattern certify every odd length `n=2k+1≥5` with
   independent `±1` middle coordinates that already satisfy the reciprocal
   middle condition of `weighted-wrapper-contract`?
2. A fully charged Boolean inventory for one n=3 `(p,w,m)` would need a new
   closed form or fixture obligation — leave-alone policy still blocks thin
   meter retargets of #4063/#4053.

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit [#4070](https://github.com/CrocSwap/integer-mult-bounds/pull/4070)
for the n=2 dual-scale existence lemma and OQ1; [#4063](https://github.com/CrocSwap/integer-mult-bounds/pull/4063)
/ [#4053](https://github.com/CrocSwap/integer-mult-bounds/pull/4053); Jerry Chen
(@CubeJerry) / [#2950](https://github.com/CrocSwap/integer-mult-bounds/pull/2950)
for Theorem 1 / formula (5) / precision-blind family. No independent human
review is claimed. No new kappa.
