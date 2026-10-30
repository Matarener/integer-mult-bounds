# Pooled whole-helper ceiling for the fixed PR4088 words

Prepared with OpenAI Codex assistance. Apache-2.0.

## Scope and source premises

This result fixes PR4088, Cinna Davis, head
`76088d49e3ed4142a958659aa996b0ca4da5e88e`, and its THREE/FOUR word interfaces.
The source inherits the PR4085 receiver-sharing words and PR4076 staged-entry
lineage. Its native, hosting, restoration, precision, controller and outer
transfer premises remain source premises; this calculation does not discharge
them. Source file digests used here are in `RESULT.json`.

Let `a` be the exponent saving and `H_r(a)=r^(1-a)`, with `H_0=0`. There are
3240 calls, and `x` of them use FOUR. The local profiles are fixed as

```
L3 = 2487 H1 + 713 H2 + 224 H3 + 102 H4 + 20 H5 + 8 H8,
d  = L4-L3 = 2 H1 + 3 H3 - 3 H4.
```

For THREE the whole-helper widths per call are
`{5:28,6:18,7:56,8:93,9:213}`. FOUR changes helper 601 from width 8 to width 7
and leaves every other helper width unchanged. Thus the pooled demand is

```
(N5,N6,N7,N8,N9) = (90720,58320,181440+x,301320-x,690120).
```

The source TEMPLATE has 2016 entries, already including all 112 ports. Its
capacity counts are `{8:672,16:448,32:448,48:448}`. Equivalently there are 18
distinct child slots per port, with counts `{8:6,16:4,32:4,48:4}`. Multiplying
the TEMPLATE counts by 360, once, gives

```
(B8,B16,B32,B48) = (241920,161280,161280,161280),
total bins = 725760, total capacity = 17418240.
```

The pooled model ignores source windows, chronology, call identity, repeated
physical-family exclusions and any other restrictions on where a helper may
be hosted. It allows real nonnegative pattern multiplicities and real
`0<=x<=3240`. Each pattern still contains whole helpers. This is an explicitly
optimistic relaxation of a legal source owner fill. The result gives a lower
bound on the paid bill of every such fill, including any nonuniform dispatch
of these fixed words. It does not construct a changed supplier.

## Complete finite pattern program

A pattern is `(c,n5,n6,n7,n8,n9)` with
`n_w>=0` integral and `sum_w w*n_w<=c`. Its residual rank is
`r=c-sum_w w*n_w`. There are exactly 841 patterns: 5 at capacity8,21 at 16,
158 at 32 and 657 at 48. Empty patterns are included.

For pattern multiplicities `y>=0`, require exactly `B_c` bins of each capacity
and exactly the demands above. The paid objective is the complete expression

```
3240 L3 + x d + sum_patterns y_pattern H_residual.
```

Every admissible source allocation maps to such a feasible point. No idle bin
is discarded. The helper rank mass is `10695240-x`, the local rank mass is
`16708680-x`, and the residual rank mass is `6723000+x`. Consequently the full
paid rank mass is always 23431680, or `65088*360`. This is distinct from the
comparison stock mass `(896*360)*73=23546880`.

## Exact optimum and dual certificate

For every `a` in `[0.00173,0.00174]`, the unique optimal mixture is `x=1080`.
An integral optimum of the pooled program is:

| Capacity | Whole helpers in each bin | Multiplicity | Residual |
| --- | --- | ---: | ---: |
| 8 | 8 | 241920 | 0 |
| 16 | 7+9 | 161280 | 0 |
| 32 | 9+9+9 | 1620 | 5 |
| 32 | 7+7+9+9 | 10620 | 0 |
| 32 | 6+8+9+9 | 58320 | 0 |
| 32 | 5+9+9+9 | 90720 | 0 |
| 48 | empty | 138492 | 48 |
| 48 | 9+9+9+9+9 | 22788 | 3 |

Thus the optimal residual profile is

```
I* = 22788 H3 + 1620 H5 + 138492 H48.
```

Here is a dual certificate, written as exact rational linear combinations of
the functions `H_r`, rather than rounded decimal prices. Set

```
v9 = (H3-H48)/5,
v7 = (v9-H5)/2,
v8 = v7+d,
v6 = 2v7-v8,
v5 = -H5,
u8 = -v8,
u16 = -v7-v9,
u32 = H5-3v9,
u48 = H48.
```

For every pattern the checker proves

```
u_c + sum_w n_w v_w <= H_residual.
```

The eight displayed patterns give exact symbolic equality. All other 833
constraints have strictly positive slack throughout the stated interval;
the certified minimum of slack divided by `a` is greater than
`0.696988114241`. The mixture coefficient is identically
`d+v7-v8=0`. Weak duality therefore gives the same lower bound for every real
`x` and every feasible pattern allocation. Equality is attained by the table.

Because every other pattern has positive slack, an optimum uses only the
eight displayed patterns. The nine bin/item equations, including variable
`x`, have determinant `-10`. Their solution is the displayed table and
`x=1080`, proving uniqueness in the pooled program. One can also see the
mixture directly: width 5 fixes 90720 bins of pattern `5+9+9+9`; width 6 fixes
58320 bins of `6+8+9+9`. Width 8 balance then forces
`241920+58320=301320-x`, hence `x=1080`.

## A genuine mixture breakpoint

The fixed-mixture optimum can also be stated for every real `x` in the full
range. Let `t=x-1080`, and begin with the table above. Keep the capacity8,
capacity16 and `5+9+9+9` rows fixed.

For `-1080<=t<=0`, replace the affected multiplicities by

```
cap32, 9+9+9:       1620-t/4,
cap32, 7+8+8+9:          -t/2,
cap32, 7+7+9+9:    10620+3t/4,
cap32, 6+8+9+9:    58320,
cap48, empty:       138492+t/20,
cap48, five9:       22788-t/20.
```

For `0<=t<=2160`, use

```
cap32, 9+9+9:       1620+t/2,
cap32, 7+7+9+9:    10620+t/2,
cap32, 6+8+9+9:    58320-t,
cap48, empty:       138492,
cap48, five9:       22788-t/2,
cap48, 6+6+9+9+9+9:     t/2.
```

All multiplicities are nonnegative on their segments, and all constraints
hold as exact affine identities. These are witnesses in the relaxation.
They do not assert chronological or physical-family feasibility.

For the left segment replace `v8` by `(v7+v9)/2`; for the right segment set
`v6=(-H48-4v9)/2` and `v8=2v7-v6`. Keep the other dual formulas. The checker
certifies all 841 inequalities for each dual over the same exponent interval,
and each corresponding affine witness is complementary to its dual.
Consequently the optimum complete bill has slopes

```
s_left  = d-H3/20-H5/4+H48/20,
s_right = d+(H5-H3)/2.
```

Throughout the exponent interval, exact bounds give
`s_left/a` in `[-0.348857711147,-0.348494057120]` and `s_right/a` in
`[4.365719222915,4.365911868442]`, using outward rounded displayed bounds.
Thus the bill strictly decreases to 1080 fourth calls and strictly increases
after 1080. Increasing the fourth-call frequency beyond PR4088's one-third
mixture cannot improve even this optimistic pooled bill.

## Exact root ceiling and remaining headroom

The complete optimum profile is

```
8060040 H1 + 2310120 H2 + 751788 H3 + 327240 H4
  + 66420 H5 + 25920 H8 + 138492 H48.
```

Compare this with the same source stock `(896*360) H73`. Rational logarithm
and exponential remainder bounds, imported unchanged from the source engine,
give a strict root bracket

```
0.001730980255989036959962 < a* < 0.001730980255989036959963.
```

The lower and upper signed moment intervals have signs negative and positive,
respectively; the exact endpoints are in `RESULT.json`. Approximate values are
`-1.73328*10^-17` and `+4.89396*10^-17`. Every positive rank in any feasible
complete profile is less than 73. After division by `73^(1-a)`, its complete
moment is strictly increasing in `a`. Therefore positivity of the pooled lower
bound at the upper endpoint excludes any feasible fixed-word owner allocation
having a larger moment root, including exponents outside the interval where
the displayed dual was certified. The pooled table attains `a*`, so this is a
sharp ceiling for the relaxation.

PR4088's literal chronological fill already has 1080 FOUR calls. Its residual
profile is `22785 H3+1625 H5+H16+2H32+138490 H48`. Literal minus pooled optimum
is exactly

```
D(p) = -3*3^p + 5*5^p + 16^p + 2*32^p - 2*48^p,  p=1-a.
```

This difference is strictly positive for every `0<p<1`. Indeed, for its
coefficients `c_r`, the piecewise linear function
`S(t)=sum_r c_r min(r,t)` has values 9,21,32,32,0 at the knots 3,5,16,32,48;
it is nonnegative everywhere and positive on an interval. The identity

```
D(p) = p(1-p) integral_0^infinity S(t) t^(p-2) dt
```

proves strict positivity. The source literal root bracket and the new rational
bracket show that the entire remaining root headroom lies within

```
[1.950913151266531*10^-9, 1.950913151266533*10^-9].
```

This is a limit on the fixed words, capacities and paid-profile comparison,
not a new kappa or supplier claim. Reaching even this small headroom still
requires a legal chronological distinct-family fill (or a changed interface
with its own fully charged costs). New words, capacities, stock or transfer
interfaces fall outside the bound.

## Verification level and reproduction

`verify.py` uses only the Python standard library and the unchanged source
rational enclosure engine. No floating optimizer is part of the certificate.
It independently rescans binary frame dimensions in all four raw words,
checks source widths, declared local profiles and template multiplicities, checks exact
primal balance, enumerates all 841 patterns for three exact duals, certifies
the uniform real exponent interval, checks the root signs, and rejects altered
mixture, primal, pattern-coverage, dual and paid-profile controls.

```
python3.12 -I -B verify.py --source source4088 --controls
```

By default recomputation is compared with the saved `RESULT.json`; it does not
rewrite it. `--output PATH` explicitly writes a regenerated certificate.

The 841-pattern coverage and rational enclosure computation are finite exhaustive
checks. The accompanying affine/weak-duality argument and monotonicity proof
cover every real mixture in `[0,3240]` and every exponent in the stated
interval; the monotonicity argument gives the claimed global root ceiling.
This is a written proof backed by exact finite arithmetic, not a formal kernel
proof and not an all-size multiplication theorem. Source native and operator
claims remain attributed conditional premises; the source's complete owner and
operator replay has not been repeated by this relaxation checker.
