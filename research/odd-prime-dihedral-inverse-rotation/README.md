# Odd-prime dihedral inverse-rotation pairs keep the four-call floor

**Research construction / recursive interface; no new kappa.** Answers open
question 1 of [#1953](https://github.com/CrocSwap/integer-mult-bounds/pull/1953)
(`research/d10-reflection-sharing-seeda3def8`): for every odd prime
`p ∈ {5,7,11,13,17,19,23,29,31}`, the target

```text
diag([st],[ts],[e])
```

in the formal group algebra `F₂[D_{2p}]` on three arbitrary dirty scalar
registers has exact paid-call minimum **four** when the only paid address
labels are the two reflections `s,t`. Exhaustive search over all 28 rank-one
idempotent projectors rules out every word of length at most three; the direct
four-call word attains the endpoint. The `p=5` row recovers the pinned D10
certificate digests byte-for-byte.

Selected κ stays `0.001672660197076918`. No native supplier mapping, compiler,
hosting/precision invoice, or selected-frontier change is claimed.

## Exact model and result

Let `G = ⟨s,t | s²=t²=e, (st)^p=e⟩` be the dihedral group of order `2p` for an
odd prime `p`. Set `r=st`; then `ts=r⁻¹`. Work in the full formal group algebra
`F₂[G]`. A paid factor is

```text
D_N(g) = I + ([g]+[e]) N,
```

where `g ∈ {s,t}` and `N=xyᵀ` is a rank-one idempotent in `M₃(F₂)` with
`yᵀx=1` (exactly 28 projectors). The endpoint is coefficientwise equality in
`M₃(F₂[G])`; its third diagonal entry is `[e]`, so the dirty helper is restored.

**Theorem for this certified domain.** For each listed odd prime, the minimum
is four. The direct word

```text
D_{E₀₀}(s) D_{E₀₀}(t) D_{E₁₁}(t) D_{E₁₁}(s)
```

equals `diag([st],[ts],[e])`. Through length three there are respectively
`1`, `56`, `3136`, and `175616` candidates per prime (`178809` total), with
**zero** exact endpoints on every certified `p`. Across nine primes that is
`1,609,281` words. The `p=5` primary state digests equal the pinned
[#1953](https://github.com/CrocSwap/integer-mult-bounds/pull/1953) certificate.

This does not prove a uniform all-odd-prime invariant, does not cover even
rotation orders (see [#1881](https://github.com/CrocSwap/integer-mult-bounds/pull/1881)
for D8), and does not restate the odd-dihedral **reflection** tariffs of
[#1966](https://github.com/CrocSwap/integer-mult-bounds/pull/1966).

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3.12 -I -B research/odd-prime-dihedral-inverse-rotation/verify.py
python3.12 -I -O -Werror -B research/odd-prime-dihedral-inverse-rotation/verify.py
python3.12 -I -B research/odd-prime-dihedral-inverse-rotation/independent.py
python3.12 -I -B research/odd-prime-dihedral-inverse-rotation/test_package.py
python3.12 -B scripts/research_package.py --package research/odd-prime-dihedral-inverse-rotation
```

Expected:

```text
PASS_ODD_PRIME_DIHEDRAL_INVERSE_ROTATION primes=[5, 7, 11, 13, 17, 19, 23, 29, 31] min_calls=4 ... p5_crosscheck=true no_new_kappa
PASS_INDEPENDENT_ODD_PRIME_DIHEDRAL_INVERSE_ROTATION primes=[5, 7, 11, 13, 17, 19, 23, 29, 31] min_calls=4 hits=0 no_new_kappa
PASS_ODD_PRIME_DIHEDRAL_INVERSE_ROTATION_PACKAGE_TESTS groups=4
PASS_REGISTERED_RESEARCH_PACKAGE research/odd-prime-dihedral-inverse-rotation outcome=completed
```

Default verify is read-only and compares a fresh rebuild to
[CERTIFICATE.json](CERTIFICATE.json). Use `--write` only to regenerate that
receipt (then `independent.py --write` to merge independent digests). Admission
uses `need()` (not `assert`); `-O` also passes.

## Scope and overlap

Base commit `bb4bccbf42844d2801487450727c2f63e10d1d0f` (CrocSwap/main; preferred
pin `20ecf289…` has moved — re-pinned and disclosed). Direct predecessor:
[#1953](https://github.com/CrocSwap/integer-mult-bounds/pull/1953) / D10 OQ1.
Complementary leave-alone-safe distinction from
[#1966](https://github.com/CrocSwap/integer-mult-bounds/pull/1966) (reflection
tariffs) and from the odd-kernel / PR2298 §3 / precision-blind cascades.
Soft-overlap vs D10 is an intentional successor census, not a same-group
scaffold retarget; vs #1966 the endpoint class differs (rotations vs
reflections).

## Open next questions

1. Can a torsion-aware invariant prove the four-call floor for every odd prime
   `p` without a separate census?
2. Does any odd prime `p>31` admit a three-call inverse-rotation share?
3. Is there a justified native supplier/compiler for a paid two-reflection
   alphabet realizing this endpoint?

## Credit

Prepared by Wentao Li ([VictorLiwentao](https://github.com/VictorLiwentao),
[@Is__Victor](https://x.com/Is__Victor)) with substantial AI assistance, under
Apache-2.0. Credit [#1953](https://github.com/CrocSwap/integer-mult-bounds/pull/1953)
(D10 inverse-rotation), [#1881](https://github.com/CrocSwap/integer-mult-bounds/pull/1881)
(D8 rotation/inverse), [#1966](https://github.com/CrocSwap/integer-mult-bounds/pull/1966)
/ [#1941](https://github.com/CrocSwap/integer-mult-bounds/pull/1941) (dihedral
tariff lineage), and the retained eumemic / PR288 register-model lineage.
