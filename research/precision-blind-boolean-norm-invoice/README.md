# Dual-scale Boolean paid inventory for precision-blind Norm∘F_(4,1)

**Research construction / recursive interface; no new kappa.** Answers open
question 1 of
[#4053](https://github.com/CrocSwap/integer-mult-bounds/pull/4053)
(`weighted-callee-boolean-norm-invoice`): does the Norm∘F_a Boolean inventory
remain complete for the precision-blind family `a=(1+p^{w-1},1)` on
`(Z/p^w Z)^2` without enlarging the two-coordinate scale support?

On the **unchanged PR2808 Boolean origin-plane fixture** at `q=3`, `w=2`
(`M=9`, `n=2`, `a=(4,1)`, volume **6561**, **13** planes) the raw weighted
callee attains only **729/6561** agreements with interchange `J` (formula
(5)). The single shared-factor Norm pattern of #4053 is **obstructed** on this
ring: no `s` with `4s≡1` and `s²≡1 (mod 9)`. Dual asymmetric scales
`(s_{H1},s_{D0})=(7,4)` on the **same** coordinates `(H'_1,D'_0)` realize
`F_{(4,7)}` with `(P')²=I`, and the ordinary wrapper attains **6561/6561**.
Paid inventory:

| Line item | Count |
|---|---:|
| scale | **341172** |
| inverse | **341172** |
| source_access | **170586** |
| restoration | **170638** |
| frame_copy (pad_in + pad_out + callee) | **511758** |

Algebraic remap controls (shared `(2,2)`, identity, zero, swapped dual) and
one live Boolean shared-`(2,2)` control stay imperfect. Selected κ stays
`0.001672660197076918`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/precision-blind-boolean-norm-invoice/verify.py
python3.12 -I -O -Werror -B research/precision-blind-boolean-norm-invoice/verify.py
python3.12 -I -B research/precision-blind-boolean-norm-invoice/independent.py
python3.12 -I -B research/precision-blind-boolean-norm-invoice/test_package.py
python3.12 -B scripts/research_package.py --package research/precision-blind-boolean-norm-invoice
```

Expected:

```text
PASS_PRECISION_BLIND_BOOLEAN_NORM_INVOICE q=3 w=2 a=(4,1) raw_agreements=729/6561 normalized_agreements=6561/6561 dual_scales=(7,4) target=(4,7) scale=341172 inverse=341172 source_access=170586 restoration=170638 frame_copy=511758 single_factor_obstructed no_new_kappa
PASS_INDEPENDENT_PRECISION_BLIND_BOOLEAN_NORM_INVOICE raw=729/6561 normalized=6561/6561 dual_scales=(7,4) scale=341172 inverse=341172 source_access=170586 restoration=170638 frame_copy=511758 single_factor_obstructed no_new_kappa
PASS_PRECISION_BLIND_BOOLEAN_NORM_INVOICE_PACKAGE_TESTS groups=5
PASS_REGISTERED_RESEARCH_PACKAGE research/precision-blind-boolean-norm-invoice outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()`; `-O` also passes.

## Scope and overlap

Base commit `20ecf2891d80b5acf18d980b2164fb44ea7faa90` (CrocSwap/main). Closest
prior: [#4053](https://github.com/CrocSwap/integer-mult-bounds/pull/4053)
Boolean inventory for `a=(2,1)` on `(Z/3Z)^2` (OQ1); `weighted-wrapper-contract`
precision-blind family and Theorem 1 / formula (5). Soft overlap is intentional
semantic successor (new dual-scale algebra, single-factor obstruction, M=9
Boolean meters), not a ~0.9 scaffold retarget reprinting the `(3,2,(2,1))`
counts. Does not edit those packages.

Clear of leave-alones: not a GL2(F3)/wrapper-toy `F_I` census, not odd-kernel
BIT-supplier/tariff/run retarget, not PR2809/priced-park, not route-cube, not
UT4 unfinished, not stock-envelope/finite-C/rho, not gate-operand dest-absent,
not a thin reprint of #4053's `(2,1)` meters.

## Open next questions

1. Does every odd prime-power precision-blind pair `a=(1+p^{w-1},1)` admit a
   dual-scale Norm on the same two coordinates into some reciprocal unit pair
   `(u,u^{-1})`? First classify when `a_0` is a square modulo `p^w`.

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit Jerry Chen (@CubeJerry) for `weighted-wrapper-contract`
Theorem 1 / formula (5) / precision-blind family; #4053 Boolean inventory
predecessor; Nick Petalas for PR2808's ordinary wrapper and PR2786 padding.
No independent human review is claimed. No new kappa.
