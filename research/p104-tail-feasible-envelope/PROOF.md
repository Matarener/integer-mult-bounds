# Fixed-contract feasibility proof

Fix the retained PR5756 target and paid histograms `T_r,P_r`, saving
`C=622627591/200000000000` and `t=1-C`. Put `T=sum T_r r^t` and
`N=sum T_r=13390`. For integer cutoff `c>=1`, integer floor `b`, positive
real offset `u` and rational decay `rho`, the two source tail gates are

```
g(c,u) = sum P_r r^(t+u) / (c^u T) < rho,
d(c,b) = N b / (c^C T) < rho,
rho^128 < 1/16.
```

The capacity condition `c^64 < b^63` implies `b>=c+1`. Let
`R=2^(-1/32)`. A permitted rational rho exists if and only if both g and d
are strictly below R: rationals are dense in the open interval between their
maximum and R. Equality at R is excluded. This eliminates every decay choice,
not just a grid. We first use the weaker condition b>=c+1 to exclude parameters;
the sole remaining pair also passes the exact capacity condition.

## Exclude all but one integer pair

For positive u, g(c,u) decreases with c. For fixed c, g is a positive sum
of exponentials in u and is strictly convex, since a paid rank differs from c.
Its derivative is the same sum weighted by `log(r/c)`. A negative derivative
at l and positive derivative at h locate its unique global minimum in (l,h).
For x in this interval, convexity gives
`g(x)>=g(l)+g'(l)(x-l)>=g(l)+g'(l)(h-l)` when g'(l)<0.
The verifier uses a lower interval endpoint for both terms. The midpoint gives
an upper bound on the minimum. Strict convexity extends this statement to all
real u; no unsearched tail or sampled-grid premise remains.

At c=15 the resulting lower bound is `0.983563652257169`, while
`R<0.978572062087701`. Thus every positive u fails for c<=15.

For real c>=1, `(c+1)/c^C` has derivative with sign `(1-C)c-C`, which is
positive because `0<C<1/2`. Also d increases with b. At c=17,b=18 the
lower bound is `0.999697814388247>R`. Thus every c>=17 and every permitted
b fails. At c=16,b=18, d exceeds `0.999886507972867>R`, which excludes all
larger floors. The only pair left is c=16,b=17. It passes `16^64<17^63`.

## Full offset interval and optimum

For c=16, g(0)>R, g(1/7)<R and g(1)>R. Strict convexity, together with the
unique derivative zero, gives exactly two positive roots of g(u)=R and a
single open feasible interval between them. The exact root brackets are in
RESULT.json. The completion tail is constant in u and is below
`0.944337257529930`. It is below even the global minimum of g, so it never
binds in this interval. Thus these two roots specify the complete tail set.

The derivative has opposite signs at the endpoints of the reported best-offset
bracket. The convex minimum bound above gives the stated decay infimum.
The infimum is not attained by rho because g<rho is strict. Positive rational
u near the minimizer and rational rho above its value approach it arbitrarily
closely. If u is restricted to rationals, intersect the same interval with Q;
all exclusion and approximation statements remain valid.

At u=1/5, g exceeds R, so no permitted rho can repair this offset. At u=1/10,
`125/128<g<489/500`, and `(489/500)^128<1/16`; this checks the distinction
between fixed-decay failure and full infeasibility. The source point also
passes its reserve. Other compiler conditions are not inferred from these gates.

## Arithmetic and limits

The shared power engine encloses fractional powers with integer square roots
and directed products on a dyadic grid. For arbitrary rational exponent e,
write e=floor(e)+f with 0<=f<1 and multiply by the exact integer power.
This is valid for negative exponents as well. Positive denominators permit
outward interval division.

For x in [1,2], put z=(x-1)/(x+1). The first80 terms of
`2 sum z^(2j+1)/(2j+1)` are a lower bound for log x. The remaining positive
tail is at most `2 z^161/(161(1-z^2))`. An integer rank is reduced to this
range by an exact power of2. Subtraction gives a rigorous log(r/c) interval;
all four endpoint products handle its possible negative sign. Root bisection
proceeds only after strict opposite signs are proved. It fails on uncertainty.

The infinite parameter coverage follows from these monotonicity and convexity
arguments. The finite arithmetic controls do not establish the proof by
extrapolation. The source invoice and gate formulas are pinned premises;
this proof does not establish their native realization or a different compiler.
