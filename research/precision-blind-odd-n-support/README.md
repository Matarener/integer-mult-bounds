# Odd-n precision-blind dual-scale support classification

**Research construction / recursive interface; no new kappa.** Answers open
question 1 of just-open
[#4072](https://github.com/CrocSwap/integer-mult-bounds/pull/4072)
(`research/precision-blind-n3-dual-scale/`): does the end-support pattern
certify every odd length `n=2k+1≥5` with reciprocal-legal `±1` middles?

**Yes, with a new n² support classification:**

- For reciprocal-legal precision-blind `a=(a0, middles, 1)` on
  `G=(Z/p^w Z)^n` (`a0=1+p^{w-1}`), exactly **two** of the `n²` dual-scale
  supports `(H'_i, D'_j)` admit scales yielding an involutory target `P'`:
  - **Far-end** `(H'_{n-1}, D'_0)` with `(a0^{-1}, a0)` →
    `P'=(a0, middles, a0^{-1})` (uniform lift of the #4072 n=3 end support).
  - **Near-end** `(H'_0, D'_{n-1})` with `(a0^{-1}, a0)` →
    `P'=(1, middles, 1)` (**new**: cancels both end precision defects).
- Illegal (non-reciprocal) middles admit **zero** dual-scale supports.
- Shared single-factor scale on either good support remains obstructed.
- Certificate grids: n=5 (25 supports/row) and n=7 (49 supports/row).

**No Boolean meter inventory. No reprint of the #4072 30-row n=3 grid or the
#4070 15-pair n=2 census. No new kappa.** Selected κ stays
`0.001672660197076918`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/precision-blind-odd-n-support/verify.py
python3.12 -I -O -Werror -B research/precision-blind-odd-n-support/verify.py
python3.12 -I -B research/precision-blind-odd-n-support/independent.py
python3.12 -I -B research/precision-blind-odd-n-support/test_package.py
python3.12 -B scripts/research_package.py --package research/precision-blind-odd-n-support
```

Expected:

```text
PASS_PRECISION_BLIND_ODD_N_SUPPORT n5_rows=… n7_rows=… goods=far+near … no_new_kappa
PASS_INDEPENDENT_PRECISION_BLIND_ODD_N_SUPPORT … no_new_kappa
PASS_PRECISION_BLIND_ODD_N_SUPPORT_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/precision-blind-odd-n-support outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()` (not `assert`); `-O` / `-Werror` also pass.

## Scope and overlap

Base commit `20ecf2891d80b5acf18d980b2164fb44ea7faa90` (CrocSwap/main tip).
Direct predecessor: [#4072](https://github.com/CrocSwap/integer-mult-bounds/pull/4072)
OQ1 (n=3 end-support). Soft overlap vs #4072 harness is real, but the
load-bearing delta is the **n² exclusivity classification** and the **near-end
unit-end target**, not another dimension bump of the far-end alone and not a
Boolean-meter reprint. Clear of #4063/#4053 meter leave-alones, #2687
odd-kernel BIT-supplier DEFERs, and #2888 F_I GL2(F3) toy cluster.

## Open next questions

1. Does the same far/near exclusivity hold for composite odd moduli (not just
   odd prime powers) under the `±1` middle restriction?
2. A fully charged Boolean inventory for one n=5 far-end or near-end fixture
   would need a new closed form — leave-alone policy still blocks thin meter
   retargets of #4063/#4053/#4072.

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit [#4072](https://github.com/CrocSwap/integer-mult-bounds/pull/4072)
for the n=3 end-support lemma and OQ1; [#4070](https://github.com/CrocSwap/integer-mult-bounds/pull/4070)
/ [#4063](https://github.com/CrocSwap/integer-mult-bounds/pull/4063)
/ [#4053](https://github.com/CrocSwap/integer-mult-bounds/pull/4053); Jerry Chen
(@CubeJerry) / [#2950](https://github.com/CrocSwap/integer-mult-bounds/pull/2950)
for Theorem 1 / formula (5) / precision-blind family. No independent human
review is claimed. No new kappa.
