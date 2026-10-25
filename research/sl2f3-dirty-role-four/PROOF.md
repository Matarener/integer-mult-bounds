# Proof sketch: dirty role does not lower the SL2(F3) conjugate-triple floor

## Object

Let `G = SL2(F3)` (order 24) with

```text
i = [[0,1],[-1,0]],   w = [[0,-1],[1,-1]]   (entries mod 3),
c = w^{-1} i w.
```

Work in `R = F2[G]`. Paid factors are `D_N(g) = I + ([g]+[e]) N` with
`g ∈ {i, i^{-1}, w, w^{-1}}` and `N` any rank-one idempotent of `M4(F2)`
(120 such `N`; 480 factors). The target is

```text
T = diag([i], [w], [c], [e])
```

on four scalar roles: three target roles and one restored dirty role.

## Upper bound

The predecessor three-role word

```text
D_{E00}(i) D_{E11}(w) D_{E22}(w^{-1}) D_{E22}(i) D_{E22}(w)
```

extends verbatim to four roles by acting as the identity on role 3. Exact
group-algebra multiplication yields `T`, so five paid calls suffice.

## Lower bound

Every word of length `k ≤ 4` is excluded by exact meet-in-the-middle:

- Lengths `0..2` are enumerated directly.
- Length `3` splits as `1+2`; length `4` splits as `2+2`.
- The complete two-call table has `480^2 = 230400` words and `165261`
  distinct exact states. Each pair is cross-checked against full
  coefficient convolution in `F2[G]`.
- For every two-call suffix `B`, the required prefix `T B^{-1}` (with
  left diagonal action of the target labels) is looked up in the one- and
  two-call tables. No hit occurs.

Hence no word of length at most four realizes `T`, and five is minimal.

## Independent replay

A second engine builds `F2[G]` matrices as frozenset supports (no import of
the primary bit-mask transition), recomputes the direct word, omission
controls, the two-call state digest, and the same `1+2` / `2+2` joins.
It agrees on zero hits through length four.

## Limits

This answers the predecessor dirty-role OQ for **one** restored dirty
scalar. It is not a theorem for two or more dirty roles, not a physical
supplier invoice, and not a new kappa claim. Free scalar `GL4(F2)` mixing
is absorbed by the complete rank-one idempotent alphabet under augmentation,
as in the predecessor.
