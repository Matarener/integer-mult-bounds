# Exact canonical carry frequency for a rational shear

## Contract and result

Fix a nonzero reduced rational coefficient `c=a/h`, where `a` is an integer,
`h>=1`, and `gcd(|a|,h)=1`. Let `q>=2` be an integer with `gcd(q,h)=1`.
The low input is the ordered pair `(x,y)` in `{0,...,q-1}^2`. Apply the shear

```text
(x,y) -> (x+c*y,y).
x' = the canonical residue of x+c*y modulo q.
C(x,y) = (x+c*y-x')/q.
```

Rational residues use the inverse of `h`. The exact rational `C` has denominator
dividing `h`. This is the elementary instance of the carry contract in Ali
Romman's [PR #5841](https://github.com/CrocSwap/integer-mult-bounds/pull/5841).
That package counts potential final correction sites and explicitly permits
additional zero corrections on particular low rows. Its source binding and
whole-word fusion are predecessor results, not conclusions of this package.

Write `A=|a|`, `H=max(A,h)` and `m=floor((q-1)/H)`. The exact number of zero
carries is

```text
Z(a,h,q) = (m+1)*q - A*m*(m+1)/2.
```

Consequently exactly `q^2-Z` low pairs have a nonzero exact carry. Both signs
of the coefficient have the same count. No primality assumption on `q` is
needed for this scalar result.

## Counting proof

Suppose first that `a>0`. The equation `C=0` says `x'=x+a*y/h` as a rational
equality. In particular `h` divides `a*y`, and reducedness implies `y=h*t`.
Conversely, for such a `y` the exact carry is zero precisely when

```text
0 <= t <= floor((q-1)/h),
0 <= x <= q-1-a*t.
```

There are `q-a*t` choices of `x` when `a*t<=q-1`, and none otherwise. Thus
the permitted values of `t` are exactly `0,...,m`. Summing the arithmetic
progression gives the displayed formula.

For `a<0`, write `A=-a`. The same integrality condition gives `y=h*t`, and
the no-wrap interval is `A*t<=x<=q-1`. It again has `q-A*t` entries. This
proves the sign symmetry and the entire formula.

## Exact carries versus high-digit translations

For width `w>=2`, put `M=q^(w-1)`. The actual high-digit correction is the
residue of `C` modulo `M`, rather than the rational number `C` itself.
Writing arbitrary full inputs as `x+q*hx` and `y+q*hy`, the high output is

```text
hx + c*hy + C(x,y) modulo M.
```

These two notions of a zero correction agree whenever `q>=A+h`. Indeed

```text
h*C = (h*(x-x') + a*y)/q
```

is an integer, and `|h*C| < A+h <= q <= M`. Since `h` is a unit modulo `M`,
the residue of `C` vanishes exactly when `M` divides `h*C`. In that strict
interval it can do so only when `C=0`. Under this sufficient radix bound,
`q^2-Z` therefore counts nonidentity high translations at every width `w>=2`.
The proof does not assert that this sufficient bound is necessary.

The distinction matters outside that bound. For `q=3`, `w=2`, `c=4`, and
`(x,y)=(1,2)`, one has `x'=0` and exact `C=3`, but its high residue modulo
three is zero. At width one there is no nontrivial high ring at all.

## Conditioning on an invertible low matrix

Let now `q` be prime and `n>=2`. Choose a matrix uniformly from `GL_n(F_q)`
and take two specified distinct coordinates in one specified row. Let

```text
B_n(q) = product over j=1,...,n-1 of (q^n-q^j).
```

Every nonzero row has exactly `B_n(q)` invertible completions. To see this,
successively choose each remaining row outside the span of its predecessors.
The numbers of choices are `q^n-q`, `q^n-q^2`, and so on.

For every nonzero coordinate pair `(x,y)`, exactly `q^(n-2)` nonzero rows
project onto it. The pair `(0,0)` has one fewer such row. It always has zero
carry, so it contributes nothing to the nonzero-carry count. It follows that
the exact number of invertible matrices with nonzero exact carry is

```text
(q^2-Z(a,h,q)) * q^(n-2) * B_n(q),
```

and their proportion is

```text
(q^2-Z(a,h,q)) * q^(n-2) / (q^n-1).
```

Under `q>=A+h` these also count nonidentity high translations for every
`w>=2`. The matrix must be uniform over the complete stated general linear
group. This law is not asserted for an arbitrary subset of admissible matrices,
correlated invocations, composite-radix general linear groups, or a selected
construction's actual execution distribution.

## Smaller coefficients can have more carry events

For fixed `a,h`, the scalar nonzero-carry proportion tends, as the radix grows
through integers coprime to `h`, to

```text
1 - 1/H + A/(2*H^2),  H=max(A,h).
```

This follows by dividing the exact formula by `q^2` and using `m/q -> 1/H`.
In particular coefficients `1`, `1/2`, and `1/4` have limiting proportions
`1/2`, `5/8`, and `25/32`, respectively. More generally `c=1/2^s` has limit

```text
1 - 2^(-s) + 2^(-2*s-1),
```

which increases strictly to one. For successive denominators `h` and `2h`,
the increase is `(4*h-3)/(8*h^2)>0`. This is a scoped obstruction to using
coefficient magnitude alone as a predictor of carry sparsity. It is not a
lower bound on a complete physical circuit's cost.

## Scope and credit

This is a scoped written counting proof with finite corroboration. It adds an
exact per-input law to the cited potential-site contract. It neither audits
that source nor certifies its complete G20 word. Exact uniform frequencies
do not improve a worst-case recursive invoice without a legal skipping or
amortization argument. Computing the predicate, retaining low data, preparation,
cache erasure, physical movement, restoration and full supplier admission remain
separate obligations. All selected framework assumptions remain open at their
previous status. No new kappa or complete multiplication theorem is claimed.

Credit Ali Romman #5841 for the question's source and fused carry contract,
Nick Petalas's earlier elementary carry identity, ToikY #5801/#5805,
Tekalign #3343/#4000, JoyboyBrian and the retained G20/native/ROW lineage.
Arithmetic-progression counting and uniform general-linear-group row counting
are classical. The new formula, consequences and verifier were produced by
Nick Petalas. Apache-2.0. Independent human and formal proof-kernel review are
unclaimed.
