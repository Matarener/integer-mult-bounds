# Proof: dual-scale Norm exists for every odd-prime-power precision-blind pair

**Scoped interface lemma; no new kappa. No Boolean meter inventory.**

## Setup

Fix an odd prime `p` and an integer `w≥2`. Let `M=p^w`, `G=(Z/MZ)^2` and
`a=(a0,1)` with `a0=1+p^{w-1}`. Both weights are units, and

```text
P_a² − I = p^{w-1} I
```

as in `weighted-wrapper-contract` (precision-blind family). Formula (5) of that
package counts exactly `M^2 · gcd(M,a0−1) · gcd(M,0) = p^{4w−2}` correct
raw address pairs out of `M^4`.

## Single-factor obstruction

A shared scale `s` on coordinates `(H'_1,D'_0)` induces
`P'=(a0,s)`. Involutory weighted form and the matching `D'`-scale force

```text
a0 · s ≡ 1 (mod M)    and    s² ≡ 1 (mod M).
```

From `s²≡1` one has `s≡±1` for odd prime powers (the middle-coordinate argument
of `weighted-wrapper-contract`: `(s−1)(s+1)=0` and `p` cannot split between
the factors). Then `a0≡±1`. But

```text
a0 = 1 + p^{w−1} ≡ 1 + p^{w−1} ≢ 1 (mod M),
a0 ≡ 1 ≢ −1 (mod p)  (since p odd),
```

so `a0≢±1`. Hence no shared single-factor scale exists for any odd `p` and
`w≥2`.

## Dual-scale existence

Keep the same two-coordinate support. Set

```text
(s_{H1}, s_{D0}) = (a0^{−1}, a0).
```

After `F_a`,

```text
H = (a0 D_1, D_0),     D = (H_1, a0^{−1} H_0).
```

Dual Norm yields

```text
H' = (a0 D_1, a0^{−1} D_0),     D' = (a0 H_1, a0^{−1} H_0),
```

which is exactly `F_{P'}` for `P'=(a0, a0^{−1})`. Since `a0·a0^{−1}≡1`,
`(P')²=I`. Theorem 1 of `weighted-wrapper-contract` therefore makes two equal
ordinary calls equal interchange `J` on all of `G×G`.

This construction uses **invertibility of `a0`**, not an explicit square root.

## Square classification

For odd prime `p` and unit `u`, `u` is a quadratic residue modulo `p^w` if and
only if it is a quadratic residue modulo `p`. Here `a0≡1 (mod p)`, and `1` is a
square, so `a0` is **always** a unit quadratic residue modulo `p^w`. Hensel
lifting produces an explicit square root from any root modulo `p`.

Square-class membership is therefore uniform (`always`), and is independent of
the dual-scale construction above: existence never consults the square root.

## Certificate grid and #4063 cross-check

The executable certificate enumerates every odd prime
`p∈{3,5,7,11,13,17,19,23}` and every `w∈{2,3,4,5}` with `p^w≤2000`, checking
for each pair: unit status, single-factor obstruction, dual-scale bank identity,
square-class, and an explicit square root. The published `#4063` scales
`(s_{H1},s_{D0})=(7,4)` and target `(4,7)` at `(p,w)=(3,2)` reappear as the
instance `a0=4`, `a0^{−1}=7`.

## Limitations

This package does **not** reprint Boolean paid inventories, does not claim a
BIT supplier, and does not change κ. Length-`n>2` banks and any further
`(p,w)` Boolean meter census are left open under the leave-alone policy against
thin meter retargets.
