# Two readings of the tensor-frame child

## Proposition

Let the pinned mixed profile from
`research/staged544-mixed-fourth-entry/RESULT.json` be

```
n = {1: 8060060, 2: 2310120, 3: 751813, 4: 327210, 5: 66425, 8: 25920, 48: 138492}
```

and let `W = 896 * 360`, `m = 73`, and

```
k = 43274477891769811819 / 25000000000000000000000
```

be that file's `root_lower`. Write

```
M(f, a) = sum_r a(r) * r^(1-k) - W * (m*f)^(1-k).
```

For a positive integer `f`, the two readings of one rank-`r` transition inside
a core of width `73f` are

- **single child:** `a(r*f) = n_r` and `a` is zero elsewhere below the parent;
- **factorwise copies:** `a(r) = f * n_r` and `a` is zero on every rank that is
  not one of the original ranks.

At this fixed `k`:

1. The scalar bill `M(1, n)` is strictly negative.
2. The single-child bill `M(f, a)` is strictly negative for every integer `f >= 1`.
3. The factorwise bill is strictly positive for every integer `f >= 2`.
4. Both pinned recipe reports, `RECORD-base.json` and `RECORD-extra.json`,
   list local child ranks inside `{1,2,3,4,5,8}` and do not name a tensor frame.

No new κ follows. The selected frontier stays the conditional value in
`certificates/selected-result.json`.

## Why these two readings

`research/unconditional-batched-crt/COMPLEX.md` says that every rank-`r`
native transition executes one proper `C tensor (r f)` child, and that
replacing a frame label `T` by `T tensor f` is supplied by the native directed
recipe identities. The same paragraph says those corrections add no unpriced
child. PR #4184 certifies the free-word cancellation on the four actual
programs and states that the native frame and rank-child coordinate is still
unpriced.

The #4088 moment compares `sum n_r r^(1-k)` with `W * 73^(1-k)`. Substituting
one child of rank `r*f` and parent width `73f` multiplies every term by
`f^(1-k)`, so the sign is unchanged. Repeating the scalar child once per
tensor factor multiplies only the child side by `f` and the parent side by
`f^(1-k)`. Those are different bills. The recipe files on the same base are
the scalar records: 72 warps, a local histogram on ranks at most 8, and no
tensor-frame field.

## Proof

All logarithms and exponentials below are enclosed by alternating series with
explicit tails. `ln 2 = 2 artanh(1/3)`. For a positive integer `n = m * 2^e`
with `1 <= m < 2`, `ln n = ln m + e ln 2`, and `ln m = 2 artanh((m-1)/(m+1))`
when `m > 1`. The artanh tail after `N` terms is at most the next geometric
majorant `z^(2N+1) / ((2N+1)(1-z^2))`. Then

```
r^(1-k) = r * exp(-k ln r).
```

For `0 <= x < 1`, the Taylor remainder of `exp(-x)` after term `N` is smaller
than the next term and has its sign. The verifier uses `N = 80` for artanh and
`N = 30` for the exponential. Every rank that occurs satisfies `k ln r < 1`.

Let `P = sum_r n_r r^(1-k)` and `Q = W * 73^(1-k)`, so the scalar moment is
`M = P - Q`. The enclosures give

```
-3.85 * 10^-14 < M < -3.84 * 10^-14 < 0,
Q > 2.337 * 10^7.
```

The displayed decimals in the receipt are truncated toward zero. The
pass/fail comparisons use the exact rational enclosures.

**Single child.** For `a(r*f) = n_r`,

```
M(f, a) = f^(1-k) * M.
```

Since `f^(1-k) > 0` and `M < 0`, the product is negative. The verifier also
encloses the multiplied histogram directly at `f in {1,2,3,4,8,73}` and checks
that each upper bound is negative.

**Factorwise copies.** The bill is

```
h(f) = f*P - Q*f^(1-k) = f*M + Q*(f - f^(1-k)).
```

Its derivative is `h'(f) = P - (1-k) Q f^(-k)`. At `f = 2` the enclosed
lower bound of `h'(2)` is greater than `68435`, so `h'(2) > 0`. For `f > 2`,
`f^(-k) < 2^(-k)`, and `(1-k)Q > 0`, hence `h'(f) > h'(2) > 0`. Therefore `h`
is increasing on `[2, infinity)`, and `h(f) > h(2)`. The direct enclosure
gives `h(2) > 56052 > 0`. Every integer `f >= 2` is therefore positive.
The samples `f in {3,4,8,73}` are checked directly as well.

**Controls.** At `f = 1` both readings reproduce the scalar sign. Adding
`10^9` rank-1 children makes the scalar upper bound positive, so the sign
test is not vacuous. The pinned `lower_moment_interval` upper bound in
`RESULT.json` is negative; that is a file pin, not an input to the series.

## What this does not prove

The single-child sign does not exhibit a native program that emits a child of
rank `r*f`, and it does not price the left and right monomials. A monomial
that adds another paid child, or that changes `W`, can destroy the negative
sign. Factorwise failure does not forbid some third schedule whose child
ranks are neither `r` nor `r*f`. The argument uses one rational endpoint of
one finite histogram. It is not an all-size theorem and it does not move κ.
