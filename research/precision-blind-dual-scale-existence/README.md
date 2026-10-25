# Dual-scale Norm exists for every odd-prime-power precision-blind pair

**Research construction / recursive interface; no new kappa.** Answers open
question 1 of
[#4063](https://github.com/CrocSwap/integer-mult-bounds/pull/4063)
(`research/precision-blind-boolean-norm-invoice`): for every odd prime `p` and
every `w≥2`, the precision-blind weight `a=(1+p^{w−1},1)` on `(Z/p^w Z)^2`
admits a dual-scale Norm on the same two coordinates `(H'_1,D'_0)` into the
reciprocal unit pair `(a0,a0^{−1})`, while no shared single-factor scale exists.

| Fact | Result |
|---|---|
| Single shared-factor Norm | **obstructed** for every certified `(p,w)` |
| Dual scales `(s_{H1},s_{D0})` | `(a0^{−1}, a0)` realizes `F_{(a0,a0^{−1})}` with `(P')²=I` |
| Square class of `a0` | **always** a unit quadratic residue mod `p^w` |
| Dual-scale uses square root? | **no** — invertibility only |
| Boolean meter inventory | **none** (not a `(p,w,a)` meter retarget) |
| `#4063` cross-check `(p,w)=(3,2)` | scales `(7,4)`, target `(4,7)` |

Certificate grid: odd primes `{3,5,7,11,13,17,19,23}` and widths `{2,3,4,5}`
with `p^w≤2000`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/precision-blind-dual-scale-existence/verify.py
python3.12 -I -O -Werror -B research/precision-blind-dual-scale-existence/verify.py
python3.12 -I -B research/precision-blind-dual-scale-existence/independent.py
python3.12 -I -B research/precision-blind-dual-scale-existence/test_package.py
python3.12 -B scripts/research_package.py --package research/precision-blind-dual-scale-existence
```

Expected:

```text
PASS_PRECISION_BLIND_DUAL_SCALE_EXISTENCE pairs=… single_factor=0 square=always dual_scales=inv crosscheck_4063=(7,4) boolean_meters=false no_new_kappa
PASS_INDEPENDENT_PRECISION_BLIND_DUAL_SCALE_EXISTENCE … no_new_kappa
PASS_PRECISION_BLIND_DUAL_SCALE_EXISTENCE_PACKAGE_TESTS groups=6
PASS_REGISTERED_RESEARCH_PACKAGE research/precision-blind-dual-scale-existence outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt. Admission uses `need()`; `-O` also passes.

## Scope and overlap

Base commit `20ecf2891d80b5acf18d980b2164fb44ea7faa90` (CrocSwap/main). Closest
priors: [#4063](https://github.com/CrocSwap/integer-mult-bounds/pull/4063)
`(3,2)` dual-scale Boolean invoice (OQ1); [#4053](https://github.com/CrocSwap/integer-mult-bounds/pull/4053)
`(2,1)` inventory; `weighted-wrapper-contract` Theorem 1 / precision-blind
family. Soft-overlap vs #4063 is intentionally low on the load-bearing claim:
this package ships a uniform existence/obstruction/square-class lemma and
**does not** reprint the M=9 dual-scale meters or any other `(p,w,a)` Boolean
inventory.

Clear of leave-alone #2687 BIT-supplier thin tariffs, #2888 GL2(F3) F_I toys,
PR2809 cascades, route-cube scaffolds, UT4 unfinished searches, and odd-kernel
run/tariff retargets.

## Open next questions

1. Does the same dual-scale reciprocal construction extend to precision-blind
   lists of length `n>2` with middle coordinates forced to `±1`?
2. Can a fully charged Boolean inventory for one further `(p,w)` be derived
   from this existence lemma without reprinting the M=9 line items?

Structured blockers are in [TASK.json](TASK.json).

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit Jerry Chen (@CubeJerry) for `weighted-wrapper-contract`
Theorem 1 / formula (5) / precision-blind family; #4063 / #4053 Boolean
inventory predecessors; Nick Petalas for PR2808's ordinary wrapper. No
independent human review is claimed. No new kappa.
