# Proof: odd-n dual-scale support classification

**Scoped interface lemma; no new kappa. No Boolean meter inventory.
Does not reprint the #4072 n=3 30-row grid or the #4070 15-pair n=2 census.**

## Setup

Fix an odd prime `p`, an integer `w≥2`, and an odd length `n=2k+1≥3`.
Let `M=p^w`, `G=(Z/MZ)^n` and

```text
a = (a0, m_1, …, m_{n-2}, 1),    a0 = 1 + p^{w-1},
```

where each middle satisfies `m_i ∈ {±1}` and the **reciprocal middle
condition** of `weighted-wrapper-contract` (4):

```text
m_i · m_{n-1-i} ≡ 1 (mod M)   for all i.
```

For `±1` this is exactly `m_i = m_{n-1-i}`. Then `P_a² = diag(a0, 1, …, 1, a0)`,
so the precision defect lives only on the two ends.

Write `F_a` for the one-bank weighted map:

```text
H'_k = a_k D_{n-1-k},
D'_k = a_{n-1-k}^{-1} H_{n-1-k}.
```

A **dual-scale Norm** on support `(H'_i, D'_j)` multiplies those two
coordinates by units `(s, t)` and leaves every other coordinate untouched.

## Far-end existence

Take `i=n-1`, `j=0` and `(s,t)=(a0^{-1}, a0)`. After `F_a` and this Norm,

```text
H'' = (a0 D_{n-1}, m_1 D_{n-2}, …, m_{n-2} D_1, a0^{-1} D_0),
D'' = (a0 H_{n-1}, m_1 H_{n-2}, …, m_{n-2} H_1, a0^{-1} H_0),
```

which is exactly `F_{P'}` for `P'=(a0, m_1, …, m_{n-2}, a0^{-1})`. Reciprocity
of the middles plus `a0·a0^{-1}≡1` give `(P')²=I`. Theorem 1 of
`weighted-wrapper-contract` therefore makes two equal ordinary calls equal
interchange `J` on all of `G×G`.

This is the uniform lift of the #4072 n=3 end support `(H'_2, D'_0)`.

## Near-end existence (new)

Take `i=0`, `j=n-1` and the **same** scales `(s,t)=(a0^{-1}, a0)`. Then

```text
H''_0 = a0^{-1} · (a0 D_{n-1}) = D_{n-1},
H''_k = m_k D_{n-1-k}  (1≤k≤n-2),
H''_{n-1} = D_0,
```

and likewise on `D''`, which is exactly `F_{P'}` for

```text
P' = (1, m_1, …, m_{n-2}, 1).
```

Again `(P')²=I` by the reciprocal middle condition. The near-end Norm
**cancels the precision defect on both ends**, leaving unit end weights.
For `n=3` this support is `(H'_0, D'_2)` with target `(1, m, 1)`; #4072
published only the far-end, so the near-end is a new named construction even
at `n=3`, and it is load-bearing for every odd `n≥5`.

## Exclusivity among all n² supports

Fix reciprocal-legal `a`. Suppose a dual-scale Norm on `(H'_i, D'_j)` equals
`F_{P'}` for some involutory `P'`. Comparing unscaled `H'` coordinates forces
`p_k = a_k` for every `k≠i`, and `p_i = s a_i`. Comparing unscaled `D'`
coordinates forces `p_{n-1-k} = a_{n-1-k}` for every `k≠j`, and
`p_{n-1-j} = a_{n-1-j}/t`. These two prescriptions must agree, and
`p_k p_{n-1-k}≡1` for all `k`.

- If `i∉{0,n-1}`, then `p_0=a0` and `p_{n-1}=1` are forced by unscaled `H'`,
  so `p_0 p_{n-1}=a0≢1`. Impossible.
- If `i=n-1` and `j≠0`, the unscaled `D'_0` forces `p_{n-1}=1`, while the
  scaled `H'_{n-1}` wants `p_{n-1}=s`; matching with the end-reciprocal
  constraint and the remaining `D'` equations collapses to `a0≡±1` or a
  conflicting assignment of `p_0` (same arithmetic that blocks `(n-1,n-1)`).
- If `i=0` and `j≠n-1`, symmetrically impossible.
- The only surviving cases are `(i,j)=(n-1,0)` and `(0,n-1)`, attained by the
  constructions above with `(s,t)=(a0^{-1},a0)`.

Thus exactly two of the `n²` dual-scale supports work.

## Illegal middles

If some middle pair violates reciprocity, then already no weight list extending
the unscaled middle coordinates can be involutory while matching both `H'` and
`D'` constraints for any dual-scale support: the executable census on the
certificate's illegal witnesses finds `good_supports=0` among all `n²` pairs.

## Single-factor obstruction

A shared scale `s` on either good support requires `a0·s≡1` and `s²≡1`. From
`s²≡1` on an odd prime power one has `s≡±1`, hence `a0≡±1`, contradicting
`a0=1+p^{w-1}`. So no shared single-factor scale exists on either good support.

## Square classification

As in #4070/#4072: for odd prime `p`, unit `u` is a quadratic residue modulo
`p^w` iff it is modulo `p`. Here `a0≡1 (mod p)`, so `a0` is always a unit
quadratic residue. Dual-scale existence uses invertibility, not an explicit
square root.

## Certificate grids

- **n=5:** every odd prime `p∈{3,5,7,11,13}` and `w∈{2,3,4}` with `p^w≤500`,
  all four reciprocal-legal ±1 middle triples; classify all 25 supports per row.
- **n=7:** every odd prime `p∈{3,5,7}` and `w∈{2,3}` with `p^w≤200`, all eight
  reciprocal-legal ±1 middle 5-tuples; classify all 49 supports per row.
- **Illegal witnesses:** `(n,p,w)∈{(5,3,2),(5,5,2),(7,3,2)}` with one
  reciprocity-breaking middle tuple each; `good_supports=0`.

Bank identity is exhaustive when `2 M^n` is small; otherwise the closed form
plus a deterministic lattice spot-check. The published n=2 and n=3 closed forms
are cited as anchors only; their censuses are not reprinted.

## Limitations

No Boolean paid inventory, no BIT supplier, no change of κ. Composite odd
moduli (extra middle units squaring to 1) are left open.
