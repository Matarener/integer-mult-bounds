# Shared conjugators for a rank-two clean operation

This contribution was produced by Nick Petalas. Apache-2.0.

Work over any vector space in characteristic two and let g be a linear
involution. Put t=1+g, so t squared is zero. All identities below are formal
identities in F2[C2], hence hold without any finite-address assumption.
Each CNOT is one scalar role addition; each G applies g to the helper h.

Write A1 for `h += c`, A2 for `h += d`, B1 for `a += h`, B2 for `b += h`,
C1 for `a += c` and C2 for `b += d`. Strings in this proof are chronological.
Set A12=A1 A2 and B12=B1 B2; these pairs commute internally.

JoyboyBrian #5007 constructs the following three idempotents, with role
order a,b,c,d,h:

```text
x1 = a+h,       y1 = d*+h*
x2 = b+h,       y2 = c*+h*
x3 = a+b+h,     y3 = c*+d*+h*
```

Here stars denote coordinate covectors. Their sum is
`a c* + b d* + h h*`. The inherited construction and minimum retain
#5007's credit. Because t squared is zero, the three factors I+t xj yj
commute. Reorder them 1,3,2 and use #5007's literal conjugators:

```text
B1 A2 G A2 B1
B12 A12 G A12 B12
B2 A1 G A1 B2
```

The two boundary scalar strings simplify without moving any reflection:

```text
A2 B1 B12 A12 = A2 B2 A2 A1 = B2 C2 A1
A12 B12 B2 A1 = A2 A1 B1 A1 = A2 B1 C1
```

The only noncommuting rewrite is `Ai Bi Ai = Bi Ci`. It follows directly
by applying the three scalar additions to arbitrary inputs. The other
rewrites cancel repeated involutions or commute disjoint-source additions.
The resulting complete stream is

```text
B1 A2 G B2 C2 A1 G A2 B1 C1 G A1 B2
```

There are ten CNOTs and three G calls. The complete factor product is
`I+t(a c*+b d*+h h*)`. Thus a and b acquire t times c and d, both sources
are restored and the full helper action is `h+t h=g(h)`. A clean zero
helper returns to zero. No data role starts clean, is erased or is discarded.

For a proof independent of the conjugator notation, put t=1+g and track
the new stream. Immediately after the first G, h is `g(h0+d)` and a is
`a0+h0`. Immediately before the second G, h is `g(h0+d)+c`. Just after it,
h is `h0+d+g(c)` and b is `b0+g(h0)+t d`. Before the third G, h is
`h0+g(c)` and a has become `a0+t c`. The last two scalar additions restore
h to `g(h0)` and b to `b0+t d`. c and d are never destinations. This proves
the full five-input identity directly for any involutory linear g.

At stationary complete prices the clean bill is `3R+10C+H`. The cited
dirty stream is the separate echo on each pair,

```text
a += c; c <- g(c); a += c; c <- g(c)
b += d; d <- g(d); b += d; d <- g(d)
```

Its bill is `4R+4C`. Its two pieces use disjoint roles, so concatenation
creates no adjacent cancellation; no global scalar lower bound is claimed
for either stream. Subtracting the specified bills gives `-R+6C+H`,
establishing the strict comparison exactly when R>6C+H. The earlier
specified clean stream's sixteen CNOTs gave R>12C+H. Shared conjugators
remove six counted CNOTs while preserving all three reflections and every
input/output obligation. A common data-basis conjugation adds its complete
forward and inverse scalar costs to both bills and does not change this
comparison. No physical caller or primitive price is assumed available.
