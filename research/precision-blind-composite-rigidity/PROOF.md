# Proof: antidiagonal rigidity on odd moduli

**Scoped interface lemma; no new kappa. No Boolean meter inventory.
Does not reprint the #4073 n=5 or n=7 prime-power grids.**

## Setup

Let `M≥3` be odd and let `n=2k+1≥3`. Work in `G=(Z/MZ)^n` with a unit weight

```text
a = (a0, m_1, …, m_{n-2}, 1),    gcd(a0, M)=1,    a0 ≢ 1 (mod M).
```

Every coordinate is a unit. A middle pair is reciprocal when
`m_i · m_{n-1-i} ≡ 1 (mod M)`. The `±1` middles of #4073 are the special
case in which each middle is its own inverse. Write `F_a` for the one-bank
weighted map `H'_k = a_k D_{n-1-k}`, `D'_k = a_{n-1-k}^{-1} H_{n-1-k}`.
A dual-scale Norm on support `(H'_i, D'_j)` multiplies those two coordinates
by units `(s, t)`.

Comparing coordinates with `F_{P'}` forces `p_k = a_k` for `k≠i` and
`p_i = s a_i`, and also `p_{n-1-k} = a_{n-1-k}` for `k≠j` and
`p_{n-1-j} = a_{n-1-j} t^{-1}`.

## Off the antidiagonal

If `j ≠ n-1-i`, the `D'` prescription writes `p_i` unscaled, so `s a_i = a_i`.
Since `a_i` is a unit, `s=1`. The same match on the slot `n-1-j` forces `t=1`.
The weight list is unchanged, so it is involutory only when `a` itself is.
The precision defect `a0 · 1 ≡ a0 ≢ 1` forbids that. Off-antidiagonal supports
contribute nothing.

## On the antidiagonal

If `j = n-1-i`, the two prescriptions touch only `p_i`. They agree precisely
when `t = s^{-1}`, and the pair `(i, n-1-i)` becomes reciprocal precisely when
`s = (a_i a_{n-1-i})^{-1}`. Every other pair keeps its old product. Therefore
the repaired list is involutory if and only if every pair except
`(i, n-1-i)` was already reciprocal.

The untouched end pair is `(0, n-1)` whenever `i` is not an endpoint, and that
pair multiplies to `a0 ≢ 1`. The only surviving indices are the endpoints:

| Support | Scales `(s, t)` | Target `P'` |
|---|---|---|
| Far `(H'_{n-1}, D'_0)` | `(a0^{-1}, a0)` | `(a0, middles, a0^{-1})` |
| Near `(H'_0, D'_{n-1})` | `(a0^{-1}, a0)` | `(1, middles, 1)` |

Both exist exactly when the middles are reciprocal, and then no other support
works. A non-reciprocal middle leaves **zero** good supports, on every odd
modulus. The bank identity is the same indexwise cancellation as in #4073:
the near-end scale multiplies `a0 D_{n-1}` by `a0^{-1}` and leaves unit ends.

## Single-factor dichotomy

A shared scale requires `s=t`. On either good support that is
`a0^{-1} = a0`, i.e. `a0² ≡ 1 (mod M)`. Thus a single-factor Norm exists on
the good supports if and only if `a0² ≡ 1`.

If `M = p^k` for an odd prime `p`, and `x² ≡ 1 (mod p^k)`, then `p` cannot
divide both `x-1` and `x+1` because their difference is `2`. The `p`-valuations
do not split, so `x ≡ ±1 (mod p^k)`. The precision-blind end
`1+p^{k-1}` is neither, which recovers the #4073 single-factor obstruction
without recounting that grid.

If `a0² ≡ 1` and `a0 ≢ ±1`, then `d = gcd(a0-1, M)` is a proper factor: no odd
prime divides both `a0-1` and `a0+1`, and neither factor is empty. Conversely,
any coprime split `M = M_1 M_2` with `M_i>1` produces
`a0 ≡ 1 (mod M_1)`, `a0 ≡ -1 (mod M_2)` by the Chinese remainder theorem, and
that `a0` squares to `1` and is not `±1`. So a nontrivial single-factor end
exists if and only if `M` is not an odd prime power.

## Limits

No Boolean paid inventory and no change of `κ`. Even lengths are outside this
odd-`n` answer. The selected `κ` stays `0.001672660197076918`.
