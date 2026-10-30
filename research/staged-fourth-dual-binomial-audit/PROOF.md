# Independent certificate for the fixed PR4091 pooled dual

This is a scoped verification of Ross Richardson's PR4091 theorem, not a new
packing theorem or construction. Its source is
`a29bdd8f56cd18b805917775cdec09ff935eddc4`; the package is unchanged at the
scientific base `32890bc5de034ab8fc93ac88ead7279a6a416d04`. Its frozen PR4088
inputs come from Cinna Davis's `76088d49e3ed4142a958659aa996b0ca4da5e88e`.
The eight input files and their exact bytes are listed in `SOURCES.json`.

## 1. Declared model and source boundary

Write `H_r(a)=r^(1-a)`, with `H_0=0`. There are 3,240 calls and a real variable
`0 <= x <= 3240` for FOUR calls. The reported local invoices are

```
L3 = 2487 H1 + 713 H2 + 224 H3 + 102 H4 + 20 H5 + 8 H8,
d = L4-L3 = 2 H1 + 3 H3 - 3 H4.
```

This audit **inherits those local reports**. It does not recompute the scalar
word's paid transitions or operator correctness. It separately enumerates
the complete binary spans of the entry and exit frames of all 408 helpers in
both orientations. Entry is contained in exit, and only helper 601 changes,
from residual width 8 to 7. This gives the item inventory

```
(N5,N6,N7,N8,N9) = (90720,58320,181440+x,301320-x,690120).
```

The template has 112 ports, each with six capacity-8 and four each of
capacity-16/32/48 children. The current order is exactly nine stages times
360 replicas, so the available bins are

```
(B8,B16,B32,B48) = (241920,161280,161280,161280).
```

The historical template's `replicas:37` fields are not multipliers. The stock
coefficient `(896*360)H73` is a declared comparison premise of PR4091's proof,
not inferred from the historical template's physical-field count.

A pattern consists of a capacity `c`, five nonnegative integral helper counts
`n_w`, and a residual `r=c-sum(w*n_w)>=0`. Each bin pays exactly `H_r`.
The relaxed objective is

```
3240 L3 + x d + sum_pattern y_pattern H_residual,
```

where `y>=0` obeys all four bin balances and all five item balances. This
retains every empty bin and allows real multiplicities. Chronology, identities,
physical-family exclusions and offsets are omitted. A legal source fill maps
to this relaxation only under the declared whole-helper/residual accounting
contract. This audit supplies no new physical justification of that contract.

## 2. Complete patterns by two finite methods

The checker enumerates the Cartesian product
`0 <= n_w <= floor(c/w)` and keeps precisely the capacity-feasible tuples.
Independently, let `A(s)` be the coefficient of `z^s` in

```
product_(w=5..9) 1/(1-z^w).
```

The ordinary unbounded-coin recurrence computes these coefficients through
degree 48. For each capacity and every residual, the first enumeration must
have exactly `A(c-r)` distinct patterns. It also verifies nonnegative integral
counts and the exact capacity equation for every tuple. Thus there are
5, 21, 158 and 657 patterns respectively, 841 in total. Missing empty or
nonempty patterns, duplicates at unchanged total count, and wrong residuals
are rejected. The complete ordered census is hashed in `RESULT.json`.

## 3. A different exact power enclosure

The numerical part imports no predecessor Python and uses no logarithms,
exponentials, Decimal powers, floating-point decisions or optimizer. For an
integer `r>=1`, put `z=1-1/r`. If `0<a<1`, the binomial series gives

```
(H_r(a)-r)/a = -r sum_(k>=1) t_k(a),
t_1(a)=z,
t_(k+1)(a)=t_k(a) * (k-a) * z/(k+1).
```

Equivalently,
`t_k(a)=z^k/k * product_(j=1..k-1)(1-a/j)`. Every term is nonnegative and
nonincreasing in `a`. The convergent sum therefore shows that the normalized
power `g_r(a)=(H_r(a)-r)/a` is nondecreasing in `a` (including `r=1`, where
it is zero). This is enough for an interval result, not merely a grid test.

After `N` included terms, consecutive omitted terms have ratio at most `z`.
Their sum is at most `t_(N+1)/(1-z)=r*t_(N+1)`. At scale `S=10^40`, the
implementation starts with floor/ceiling bounds for `S*z`, rounds each positive
rational recurrence outward using integer division, and sums those bounds.
If `L_k <= S*t_k <= U_k`, positivity of the multiplier preserves this relation.
Consequently its final bounds are

```
-r * (sum_(k=1..N) U_k + r*U_(N+1))/S
    <= g_r(a) <=
-r * sum_(k=1..N) L_k/S.
```

It uses `N=2048`. The tail is included even if it is much larger than rounding
error. Independent exact rational-power fixtures and short Fraction sums check
the arithmetic, direction of rounding and first-omitted-term index. A one-term
enclosure is deliberately too wide for the dual and must fail closed.

Every nonzero dual slack below has zero rank mass: `sum c_r*r=0`. Hence

```
(sum c_r H_r(a))/a = sum c_r g_r(a).
```

For each positive coefficient, use the lower `g_r` bound at `a0=173/100000`
and the upper bound at `a1=174/100000`; reverse them for negative coefficients.
This encloses the expression **for all real a in [a0,a1]**. The checker refuses
to cancel the linear part when the rank mass is nonzero.

## 4. Recovering the duals and their faces

There are nine dual variables: four capacity prices `u_c` and five item prices
`v_w`. The desired inequalities are

```
u_c + sum n_w v_w <= H_(c-sum w*n_w).
```

The source certificate's eight central primal patterns are declarative data,
not executable evidence. We solve their eight tightness equations symbolically
over rational coefficients of `H_r`. The ninth equation is one of:

- middle: `v8-v7=d` (free-mixture stationarity);
- left: tightness of capacity-32 pattern `7+8+8+9`;
- right: tightness of capacity-48 pattern `6+6+9+9+9+9`.

Each exact linear system is nonsingular, and its solution must equal the
published potential expressions. Every recovered dual is then evaluated on
all 841 patterns. Zero expressions are recognized algebraically; all others
have strictly positive interval lower bounds. The following displayed bounds
are conservative rational truncations of `RESULT.json`:

| Dual | Identically tight | Strict | Lower bound on every nonzero slack/a |
|---|---:|---:|---:|
| Left | 11 | 830 | > 4.38806 |
| Middle | 8 | 833 | > 0.69698 |
| Right | 9 | 832 | > 2.37161 |

The left face has eleven tight patterns, even though the chosen affine witness
uses nine. No uniqueness claim about every left-face allocation is needed.
The middle face has exactly the eight source patterns.

## 5. Primal balance, uniqueness and the whole interval of mixtures

For the middle support, solve all nine balance equations with its eight
multiplicities and `x` as unknowns. The determinant is exactly `-10` and the
unique solution is

```
x=1080,
y=(241920,161280,1620,10620,58320,90720,138492,22788)
```

in the source table's order. Each multiplicity is positive. Its idle invoice
is `22788 H3+1620 H5+138492 H48`. All other patterns have strict dual slack,
so any global optimum must use this support. The exact balance system then
forces the displayed multiplicities and mixture. This proves uniqueness in
the relaxed pattern program for every exponent in the certified interval.

For each side, add its ninth tight pattern and solve the nine balances with
right-hand side affine in `x`. The result gives every multiplicity as
`b_j+d_j*x`; no sampled interpolation is used to infer this form. Exact
nonnegativity at each segment's endpoints proves it throughout that segment.
All patterns in the affine witnesses are symbolically complementary to the
corresponding dual. Thus both witnesses attain the dual bound for every real
`x` in `[0,1080]` or `[1080,3240]` respectively.

The complete objective slopes are independently recovered as

```
s_left  = d-H3/20-H5/4+H48/20,
s_right = d+(H5-H3)/2.
```

The binomial certificate encloses `s_left/a` in
`[-0.348858,-0.348494]` and `s_right/a` in `[4.365719,4.365912]`.
The complete bill therefore strictly decreases to 1080 and strictly increases
after 1080. These facts concern the complete invoice, not scalar ADD counts.

At `x=1090`, the derived right-face witness has idle
`22783 H3+1625 H5+138492 H48` and exactly five capacity-48 bins containing
`6+6+9+9+9+9`. This verifies the pooled feasibility question raised by PR5280.
The eight central patterns alone cannot serve `x=1090`: the central balance
system forces `x=1080`. The original central idle multiset itself also has ten
too few residual rank units at `x=1090`. Thus PR4170's request for that same
idle multiset at 1090 must change the mixture or the invoice; it is not an
unresolved chronological rearrangement. All these formulas already follow
from PR4091. Their derivation and audit, not their discovery, are claimed here.

## 6. Root implication and limits

The derived complete profile is

```
8060040 H1 + 2310120 H2 + 751788 H3 + 327240 H4
 + 66420 H5 + 25920 H8 + 138492 H48.
```

The checker evaluates only the coarse endpoints `a0,a1`, obtaining negative
and positive signed moments respectively against `(896*360)H73`.
Every paid rank is positive and below 73. After division by `H73`, every term
is strictly increasing in `a`, so this profile has exactly one root in the
certified interval. At that root the middle dual bounds every feasible
complete profile below by the same stock bill. Each such normalized profile
is also strictly increasing, so none has a larger root, including outside
the interval where these dual formulas were certified.

This independently checks the pooled optimality implication. The published
24-place root bracket is not recomputed, refined or used as an acceptance
input. No κ improvement, chronological construction, native/operator replay,
stock implementation, compiler, precision/tape, BIT/outer admission or
all-size multiplication theorem is claimed. The current selected result is
a changed mechanism and is not subject to this historical fixed-model cap.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Ross Richardson, Cinna Davis and the predecessor lineage credited in README.md
retain their construction and theorem credit. Apache-2.0.
