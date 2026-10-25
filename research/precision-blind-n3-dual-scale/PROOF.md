# Proof: n=3 precision-blind dual-scale Norm on end support

**Scoped interface lemma; no new kappa. No Boolean meter inventory.
Does not reprint the #4070 15-pair n=2 census or any M=9 Boolean meters.**

## Setup

Fix an odd prime `p`, an integer `w≥2`, and a middle sign `m∈{+1,-1}`.
Let `M=p^w`, `G=(Z/MZ)^3` and

```text
a = (a0, m, 1),    a0 = 1 + p^{w-1}.
```

Both end weights are units, `m²≡1`, and

```text
P_a² = diag(a0, 1, a0),
```

so the precision defect lives only on the two ends (the odd-length middle is
forced to `±1` by `weighted-wrapper-contract`). Formula (5) of that package
is not restated here; this package only settles Norm support / existence.

Write `F_a` for the one-bank weighted map of that contract:

```text
H' = P_a(D) = (a0 D_2, m D_1, D_0),
D' = P_a^{-1}(H) = (H_2, m H_1, a0^{-1} H_0).
```

## Naive n=2 support is never involutory

The n=2 dual-scale lemma (#4070) scales coordinates `(H'_1, D'_0)`. Copying
that support to n=3 yields, for any scales `(s_{H1}, s_{D0})`,

```text
H''_0 = a0 D_2,     H''_2 = D_0
```

(the end coordinates are untouched). Any target weight list `P'=(p0,p1,p2)`
compatible with those two identities must satisfy `p0=a0` and `p2=1`, hence

```text
p0 · p2 = a0 ≢ 1 (mod M)
```

because `a0=1+p^{w-1}≢1`. Therefore `(P')²≠I`, so Theorem 1 of
`weighted-wrapper-contract` never applies. This is the new support obstruction:
the n=2 coordinate pair is the wrong support on length-3 banks.

## Dual-scale existence on end support

Keep middle coordinates untouched. Set

```text
(s_{H2}, s_{D0}) = (a0^{-1}, a0).
```

After `F_a` and this Norm,

```text
H'' = (a0 D_2, m D_1, a0^{-1} D_0),
D'' = (a0 H_2, m H_1, a0^{-1} H_0),
```

which is exactly `F_{P'}` for `P'=(a0, m, a0^{-1})`. Since
`a0·a0^{-1}≡1` and `m²≡1`, one has `(P')²=I`. Theorem 1 therefore makes two
equal ordinary calls equal interchange `J` on all of `G×G`.

Existence uses **invertibility of `a0`**, not an explicit square root. Both
middle signs `m=±1` work with the same end scales.

## Single-factor obstruction on the end support

A shared scale `s` on `(H'_2, D'_0)` would require `a0·s≡1` and `s²≡1`.
From `s²≡1` on an odd prime power one has `s≡±1`, hence `a0≡±1`, contradicting
`a0=1+p^{w-1}`. So no shared single-factor scale exists on the correct support
either (same arithmetic as #4070, now stated for the n=3 end pair).

## Square classification

As in #4070: for odd prime `p`, unit `u` is a quadratic residue modulo `p^w`
iff it is modulo `p`. Here `a0≡1 (mod p)`, so `a0` is always a unit quadratic
residue. Dual-scale existence never consults the square root.

## Certificate grid

The executable certificate enumerates every odd prime
`p∈{3,5,7,11,13,17,19,23}` and every `w∈{2,3,4,5}` with `p^w≤2000`, and for
each pair both middles `{+1,-1}` (30 rows). It checks unit status, naive-support
obstruction, single-factor obstruction, end dual-scale bank identity, and
square-class. Bank identity is exhaustive when `M^3≤2000` (so `M≤12`); larger
moduli use the closed form plus a lattice spot-check. The published n=2
closed form `(a0,inv)=(4,7)` at `(3,2)` is cited only as an anchor; the
15-pair n=2 census and all Boolean meters are not reprinted.

## Limitations

No Boolean paid inventory, no BIT supplier, no change of κ. Length `n>3`
(further odd banks with several `±1` middles) is left open; the same end-support
pattern is the natural candidate but is not certified here.
