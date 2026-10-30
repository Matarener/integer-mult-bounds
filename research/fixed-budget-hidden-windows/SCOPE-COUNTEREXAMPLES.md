# Exact counterexamples to broader versions of the budget claim

These examples do **not** contradict the narrow theorem. They show why its
degree, two-crossing, and rank-alphabet restrictions must remain explicit.
All coefficients and call counts below are integers. The profiles are
obtained from the positive and negative coefficients of `Q`; both sides have
equal call count and equal rank mass. They are arithmetic profiles, with no
claim of physical supplier realizability.

Run the independent standard-library checker with:

```
python3 -I -B research/fixed-budget-hidden-windows/independent_check.py
```

It uses exact rational arithmetic and a separate Sturm-sequence root counter.
The saved result is [independent-check.json](independent-check.json).

## Seven ranks defeat even the order `constant/N`

On ranks `1,2,4,8,16,32,64`, take

```
Q_n(x) = -(x-1)(x-2)*[(x-1)^4-2*(n*(x-1)-1)^2].
```

For `n=10`, its coefficients in ascending order are

```
[482, -1595, 1937, -1010, 180, 7, -1].
```

Thus

```
A = 1595 H_2 + 1010 H_8 + H_64,
B = 482 H_1 + 1937 H_4 + 180 H_16 + 7 H_32.
```

Each has `N=W=2606` calls and rank mass `11334`. The endpoint zeros are
simple. There are exactly two interior zeros, and the difference is positive
between them and negative elsewhere in `(0,1)`.

For a root-count proof, set `y=x-1`. The quartic factors over the reals as

```
[y^2-sqrt(2)*(ny-1)] * [y^2+sqrt(2)*(ny-1)].
```

For `n>=3`, the first factor decreases strictly on `(0,1)` and changes from
positive to negative; the second increases strictly and changes from negative
to positive. Each has exactly one root there. The second factor's root is
below `1/n`, and the first factor's root is above it. This also proves the
stated sign pattern. Multiplication by `-(x-1)(x-2)>0` preserves that pattern.

At `n=10`, exact evaluation of the quartic gives

```
R(1099/1000) = -103940399/10^12 < 0,
R(11/10)    = 1/10000 > 0,
R(1101/1000)= -95939599/10^12 < 0.
```

Consequently its roots satisfy

```
1099/1000 < r < 11/10 < s < 1101/1000.
```

The elementary inequality `ln(1+t)<t`, for `t>0`, proves

```
W*ln(s/r) < 2606*(2/1099) = 5212/1099 < 12.
```

This strictly contradicts extending the claimed `12/(N*ln2)` lower bound to
this seven-rank alphabet. No decimal approximation is used.

More strongly, for all `n>=4` the count is `W_n=24n^2+24n-34`. If `u,v` are
the two roots in the `y` coordinate, then

```
nu = 1-u^2/sqrt(2),   nv = 1+v^2/sqrt(2),
v-u = (u^2+v^2)/(sqrt(2)*n).
```

The first quadratic factor is negative at `y=2/n`, since
`4/n^2-sqrt(2)<0`. Its strict decrease, together with the already established
root order, gives `0<u<1/n<v<2/n` for `n>=4`. The two displayed identities
therefore imply `nu->1` and `nv->1`. Hence `u,v ~ 1/n`, and the width is
asymptotic to `sqrt(2)/(n^3*ln2)`.

An order bound alone suffices for the obstruction:

```
v-u < 5/(sqrt(2)*n^3),
ln((1+v)/(1+u)) < (v-u)/(1+u) < v-u.
```

Since `W_n=24n^2+24n-34`, this proves `W_n*w_n -> 0` directly. No positive
universal bound of the form `constant/N` holds for this larger alphabet,
even with exactly two interior crossings and both endpoint equalities.

## An edge loss defeats an overbroad mesh claim

On the original five ranks, take

```
Q(x) = (x-1)(x-2)(10x-11)(x+1),
q = [-22, 31, 12, -31, 10].
```

Both profiles have `53` calls and rank mass `270`. The positive loss is the
edge interval `0<p<log_2(11/10)`; there is only one interior root. All interior
samples in the grid `{0,1/4,1/2,3/4,1}` have negative difference, and the two
endpoint samples are zero. Exact checks are

```
2^k * 10^4 > 11^4,  k=1,2,3,
2 * 10^8 < 11^8,    so p=1/8 is a positive-loss witness.
```

The maximum grid gap is `1/4`, which is smaller than even the theorem's
conservative rational threshold `120/(7*53)=120/371`. Hence this mesh would
hit every eligible two-crossing interior window, yet misses this edge loss.
The mesh corollary is valid only while retaining the theorem's zero pattern.

## A different five-rank alphabet defeats the same constant

On ranks `1,3,9,27,81`, use `F(p)=Q(3^p)` with

```
Q(x) = (x-1)(x-3)(3x-4)(2x-3),
q = [36, -99, 98, -41, 6].
```

Both profiles have `140` calls and rank mass `1404`. They satisfy the same
two-crossing sign pattern and endpoint equalities, but the width is
`w=ln(9/8)/ln3`. The old power-of-two constant would require
`140*ln(9/8)*ln2 > 12*ln3`. In fact,

```
140*ln(9/8)*ln2 < 140*(1/8)*(7/10) = 49/4 < 13 < 12*ln3.
```

Here `ln2<7/10` and `ln3>13/12` follow directly from the positive series
`ln((1+t)/(1-t))=2*(t+t^3/3+...)`: at `t=1/3`, the tail after the first term
is less than `1/36`, giving `ln2<25/36<7/10`; at `t=1/2`, the first two
terms give `ln3>13/12`. Thus the precise `12/ln2` constant is specific to
the stated power-of-two alphabet.
