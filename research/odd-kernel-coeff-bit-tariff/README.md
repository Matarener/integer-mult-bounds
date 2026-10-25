# Odd-kernel coefficient-bit tariff (answers #2687 OQ2)

**Card `connector-alphabet-change`, priority revision 6**, refined to open
question 2 of
[#2687](https://github.com/CrocSwap/integer-mult-bounds/pull/2687)
(`research/odd-kernel-query-pair`). No new kappa
(`0.001672660197076918`).

`#2687` showed that every odd kernel `q` has the same typed fused invoice as
the dyadic case (`4→3` children, `24→18` affine, `4→2` XOR) and left open
whether coefficient-table bit-sizes can still favor some larger `q` under a
concrete physical tariff. This package attaches one named tariff to the PR840
`address_word` lowering and answers that obligation.

**Tariff.** For each affine diagonal/control coefficient `c=p/q` in lowest
terms, charge `bit_length(|p|)+bit_length(q)`. Summing over `address_word(k)`
gives `T_word(k)`. Program bills are

```text
T_fused(q,j)    = 2·T_word(q·2^j) + T_word(q·2^{j+1})
T_baseline(q,j) = 4·T_word(q·2^j)
```

**Result.** On the certified kernels `{1,3,5,7,9,15}` and every
`j∈{0,…,32}`, every odd kernel strictly exceeds the dyadic fused and baseline
bills (`165+165` comparisons). `T_word` is not monotone in `|k|`
(`T(4)=32 < T(2)=38 < T(1)=45`), so the claim is the program comparison, not
a word-level size argument. Larger-`q` tables never pay for themselves on this
tariff.

```sh
python3.12 -I -B research/odd-kernel-coeff-bit-tariff/verify.py
```

Expected:

```text
PASS_ODD_KERNEL_COEFF_BIT_TARIFF kernels=[1, 3, 5, 7, 9, 15] j=0..32 odd_fused_exceeds_dyadic=165 odd_baseline_exceeds_dyadic=165 no_new_kappa
```

## Evidence

- Closed-form `T_word` (ten unit coeffs + six variable rationals in `a=k/4`)
  matches enumeration on `|k|≤64` and the byte-pinned `#2687` `address_word`.
- Grid: odd fused/baseline bills exceed dyadic at every `(q,j)` above.
- Spot `j=2`: dyadic fused `102` vs odd `{126,145,147,166,168}`.
- Fusion saves bits for every kernel but does not overturn odd `>` dyadic.
- Non-monotonicity control and inflated-dyadic adversarial control.

Default verify is read-only against `CERTIFICATE.json`. Admission uses
`need()` and stays enforced under `python -O`. Explicit `--write` regenerates
the certificate only.

## Reproduce

```sh
python3.12 -I -B research/odd-kernel-coeff-bit-tariff/verify.py
python3.12 -I -O -Werror -B research/odd-kernel-coeff-bit-tariff/verify.py
python3.12 -I -B research/odd-kernel-coeff-bit-tariff/independent.py
python3.12 -I -B research/odd-kernel-coeff-bit-tariff/test_package.py
python3.12 -B scripts/research_package.py --package research/odd-kernel-coeff-bit-tariff
```

## Open next questions

1. **Does any alternate physical tariff ever make a certified odd kernel beat
   dyadic at some `j`?** First step: name max-height / packing / modulus-dependent
   encoding on the same coefficients and replay the grid. Blocked by: no
   alternate tariff admitted here.
2. **Can an admitted BIT supplier host a small odd-kernel shear with a favorable
   fully charged bill versus dyadic?** First step: one exact source-return
   boundary with routing, precision and dispatch. Blocked by: still `#2687` OQ1;
   not constructed here.

## Credit

Credit `#2687` / `research/odd-kernel-query-pair` (OQ2 answered), PR840 /
`research/dyadic-query-pair`, the pending triadic kernel-3 package, and
PR521/PR677 ADDRESS / DATA-shear lineage. Predecessor notices are unchanged.

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. No independent human review is claimed. No new kappa.
