# Complete Boolean paid inventory for Norm∘F_(2,1)

**Research construction / recursive interface; no new kappa.** Answers open
question 1 of
[`weighted-wrapper-contract`](../weighted-wrapper-contract/README.md)
([#2950](https://github.com/CrocSwap/integer-mult-bounds/pull/2950)): can a
proposed weighted callee be normalized at an affordable **complete** cost?

On the **unchanged PR2808 Boolean origin-plane fixture** (`M=3`, `n=2`,
`a=(2,1)`, volume **81**, **7** planes) the raw weighted callee attains only
**9/81** agreements with interchange `J`. Post-composing each `F_a` call by
the two output scales that realize `F_{P'}` for `P'=T P`, `T=diag(1,2)`, the
ordinary wrapper attains **81/81**. The paid inventory meters every OQ1 line
item on that fixture:

| Line item | Count |
|---|---:|
| scale | **2268** |
| inverse | **2268** |
| source_access | **1134** |
| restoration | **1162** |
| frame_copy (pad_in + pad_out + callee) | **3402** |

Wrong-scale controls stay imperfect. Selected κ stays
`0.001672660197076918`.

This supersedes the deferred algebraic scale-only bill
(`research/weighted-callee-scale-normalization/`, `scales_two_F=4V=36`) which
omitted inverse/source-access/restoration/frame/copy and was not Boolean-bound.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/weighted-callee-boolean-norm-invoice/verify.py
python3.12 -I -O -Werror -B research/weighted-callee-boolean-norm-invoice/verify.py
python3.12 -I -B research/weighted-callee-boolean-norm-invoice/independent.py
python3.12 -I -B research/weighted-callee-boolean-norm-invoice/test_package.py
python3.12 -B scripts/research_package.py --package research/weighted-callee-boolean-norm-invoice
```

Expected:

```text
PASS_WEIGHTED_CALLEE_BOOLEAN_NORM_INVOICE M=3 n=2 a=(2,1) raw_agreements=9/81 normalized_agreements=81/81 scale=2268 inverse=2268 source_access=1134 restoration=1162 frame_copy=3402 no_new_kappa
PASS_INDEPENDENT_WEIGHTED_CALLEE_BOOLEAN_NORM_INVOICE raw=9/81 normalized=81/81 scale=2268 inverse=2268 source_access=1134 restoration=1162 frame_copy=3402 no_new_kappa
PASS_WEIGHTED_CALLEE_BOOLEAN_NORM_INVOICE_PACKAGE_TESTS groups=5
PASS_REGISTERED_RESEARCH_PACKAGE research/weighted-callee-boolean-norm-invoice outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()`; `-O` also passes.

## Scope and overlap

Base commit `20ecf2891d80b5acf18d980b2164fb44ea7faa90` (CrocSwap/main). Closest
prior: `weighted-wrapper-contract` (Theorem 1 / formula (5); OQ1). Closest
deferred leave-alone: algebraic scale-only package on the same `(M,n,a)` —
soft-overlap is intentional semantic completion of that incomplete invoice, not
a ~0.9 scaffold retarget of a closed claim. Does not edit those packages.

Clear of leave-alones: not a GL2(F3)/wrapper-toy `F_I` census, not odd-kernel
BIT-supplier/tariff/run retarget, not PR2809/priced-park, not route-cube, not
UT4 unfinished, not stock-envelope/finite-C/rho, not gate-operand dest-absent,
not another thin `T=diag` scale-only bill.

## Open next questions

1. Does the same Norm∘F_a Boolean inventory remain complete for the
   precision-blind family `a=(1+p^{w-1},1)` on `(Z/p^w Z)^2` without enlarging
   the scale support? First re-run the harness at `p=3,w=2` with `a=(4,1)`.
   Blocked by a missing `w=2` Boolean Norm invoice.

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit Jerry Chen (@CubeJerry) for `weighted-wrapper-contract`
Theorem 1 / formula (5); Nick Petalas for PR2808's ordinary wrapper and
PR2786 padding. No independent human review is claimed. No new kappa.
