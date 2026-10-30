# A two-guard reciprocal with a bounded correction

For every real `1 <= c < 2` and positive integer `p`, the algorithm below
returns a dyadic `y` with `|1-cy| < 2^(-p-1)`. Every Newton step uses two
fractional guard bits relative to its stage index. The unchanged warm-up
uses six fractional bits. The maximum rounded precision is `max(6,p+2)`.
Exact intermediate products remain required, as in the predecessor interface.

## Algorithm

Write `R_t(z)=floor(2^t z)/2^t`. Define

```text
N_t(x) = R_t(x * (2 - R_t(R_t(c) * x))).
x = N_6(5/8); m = 2
while m < p:
    m = min(2*m-1,p)
    x = N_(m+2)(x)
t = p+2; S = 2^t
n = floor(S*x); C = floor(S*c)
J = {j in Z : n-6 <= j <= n+6 and S/2 <= j <= S}
choose the smallest j minimizing |S^2-C*j| over J
return y = j/S
```

An incoming iterate retains its stored precision, including when the first
Newton step uses fewer than six bits. No reciprocal or division by `c` is
used by the correction. It tests at most thirteen integer products. Reading
a binary prefix, exact products and floor rounding are the stipulated
arithmetic operations; no physical tape implementation is inferred.

## Stage invariant

The directed-error identity from ToikY's PR #1638 is useful here. Put
`e=1-cx`, `delta=2^-t`, `h=c-R_t(c)`,
`a=R_t(c)*x-R_t(R_t(c)*x)` and `b=x*(2-u)-N_t(x)`, where
`u=R_t(R_t(c)*x)`. Each of `h,a,b` belongs to `[0,delta)`, and expansion gives

```math
e_+ = e^2-c h x^2-c x a+c b.
```

At the seed `x=5/8`, `|e|<=3/8`, `cx<5/4` and `cx^2<25/32`.
Thus the six-bit warm-up satisfies

```math
-65/2048 < e_+ < 11/64 < 1/4.
```

The upper bound uses `e^2<=9/64` and `cb<2/64`; the lower bound discards
`e^2` and uses `(25/32+5/4)/64=65/2048`. This establishes the invariant
`|e|<2^-m` at `m=2`. Both signs and positivity of the warm-up output follow.

Suppose `m>=2` and `|e|<2^-m`. Then `x>0`, `cx<5/4`, and
`cx^2=(cx)^2/c<25/16`. At the next stage `m'<=2m-1` with
`delta=2^(-m'-2)`, the same identity implies

```math
e_+ > -(25/16+5/4)delta = -(45/64)2^{-m'} > -2^{-m'},
```

```math
e_+ < 2^{-2m}+2delta <= (1/2+1/2)2^{-m'} = 2^{-m'}.
```

So the invariant is preserved for every real normalized input. The stage
index strictly increases, since `2m-1>m` for `m>=2`. For `p>=2`, it reaches
`p` in exactly `L=ceil(log2(p-1))` updates: before capping, `m_k=2^k+1`.
For `p=1` no update is needed and the warm-up already satisfies
`|e|<2^-p`. Consequently the iterate before correction satisfies

```math
|x-1/c| < 2^{-p}/c <= 4 delta,
```

now with `t=p+2` and `delta=2^-t`.

## Why thirteen candidates suffice

Set `q=R_t(c)`. Then `1<=q<2` and `0<=c-q<delta`, so

```math
0 <= 1/q-1/c = (c-q)/(cq) < delta.
```

Let `z` be the nearest point to `1/q` on the `delta` grid, with ties rounded
down. Since `1/2<1/q<=1`, we have `1/2<=z<=1` and
`|z-1/q|<=delta/2`. Also `0<=x-n delta<delta`. The triangle inequality gives

```math
|z-n delta| < (1/2+1+4+1)delta = (13/2)delta.
```

Both `z/delta` and `n` are integers. Their difference therefore has absolute
value at most six. Thus `z` is among the candidates `J`, including when
`p=1` or `p=2` and the warm-up was stored on a finer grid.

Minimizing `|S^2-Cj|` is exactly minimizing `|1-q(j/S)|`. It chooses `z`,
because `q>0` and the tie rule agrees. In particular, `J` is nonempty.
The true residual satisfies

```math
|1-cz| <= |1-qz|+(c-q)z
         <= q delta/2+(c-q)z
         < delta+delta = 2^{-p-1}.
```

This strict inequality proves the claimed all-real-input residual contract.
It does not assert correct rounding of `1/c`.

## Arithmetic bill and scope

Put `L=0` for `p=1`, and `L=ceil(log2(p-1))` otherwise. The construction
uses `L+1` Newton updates, hence exactly `2(L+1)` exact products in those
updates. The correction enumerates at most thirteen candidates, uses one
integer product per candidate, and at most twelve score comparisons. Its
products satisfy `0<=Cj<2^(2t+1)` and therefore need at most `2t+1` bits.
Prefix extraction, shifts, subtractions, absolute values and loop control
remain additional operations. At most `L+2` prefix reads suffice without
reusing the last one. This is an arithmetic count, not a bit-time or tape bill.

For `p>=4` the largest rounded fractional precision is `p+2`, one bit below
the credited three-guard routine's `p+3`. The extra correction products prevent
any runtime comparison from this fact alone. For small targets the fixed
six-bit warm-up dominates. Optimality of two guards and of the thirteen-point
window is unclaimed. The finite implementation caps `p` at 4096 and rational
input numerator/denominator lengths at 16384 bits; the mathematical argument
above has neither cap.

This is a changed schedule and output correction, so it does not contradict
Charles Bethin's PR #1655 lower bound for the unchanged schedule. The numerical
reciprocal is a downstream arithmetic corollary, not the selected multiplication
supplier. No selected assumption, physical caller, complete multiplication
theorem or new kappa is established.

## Credit

This proof was produced by Nick Petalas. Credit Charles Bethin / cbethin,
PR #1655, for the changed-schedule question and fixed-schedule boundary;
ToikY, PR #1638, for the directed-error identity and three-guard theorem;
Hanson Sun / bbMisk, PR #1528, and the retained manuscript and classical
Brent/Newton lineage. Binary rounding and nearest-grid correction are
classical. The contribution is the stated schedule, bounded correction,
all-input guarantee and explicit arithmetic bill. Apache-2.0.
