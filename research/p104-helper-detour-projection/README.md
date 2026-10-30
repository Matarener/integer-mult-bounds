# Sharp helper-detour bounds and source fee budgets

For one flagged helper target and one paid query on its path, **no Clifford
intermediate chart beats the best query endpoint for a one-cut power tariff**.
This holds for every exponent `0 < C < 1`. It includes noncanonical charts and
extra spectator axes. For any finite number of intermediate charts, a separate
sharp bound is attained in the tariff model by the two query endpoints. Longer
detours cannot increase this bound.

On the exact PR5756 word, the checker inventories all **2534 helper queries and
559 independent helper targets**. At κ = .00311313795, even the optimistic gains
need at least **53 one-cut helpers**, or **33 arbitrary-path helpers**, to pay
one extra H1 native query. A single helper cannot pay that fee. This is a budget
for choosing future physical searches, not a new κ or a construction.

## Contract and native metric

The original helper has fixed endpoint charts A0 and B0. One paid query has
endpoints A and B. Assume these form a geodesic chain, with

```
u = d(A0,A), q = d(A,B) > 0, v = d(B,B0),
t = d(A0,B0) = u+q+v.
```

The source's nested canonical subspaces satisfy this condition. The function
`d(X,Y)` is the Gaussian rank of the relative Clifford map. If L_X and L_Y
are the images of the Z space, then
`d(X,Y) = n - dim(L_X intersect L_Y)`. It is a pseudometric: the intersection
codimension inequality gives its triangle inequality. Clifford phases and
rank-zero maps do not change it. The theorem grants all other costs for free,
so omitted scalar, normalization and ownership charges can only reduce the gain.

Write `phi(r) = r^(1-C)` and `phi(0)=0`. A one-cut choice F replaces the helper
target by A0→F and F→B0, and replaces the paid query by A→F and F→B. It debits
both original jobs. The signed gain is

```
phi(d(A0,F)) + phi(d(F,B0)) - phi(t)
- phi(d(A,F)) - phi(d(F,B)) + phi(q).
```

These are proposed independent target credits. The theorem does not prove that
an arbitrary F permits their independent inputs or physical restoration.

## One-cut optimum over every Clifford chart

Put `x=d(A,F)`, `y=d(F,B)` and `h_r(z)=phi(z+r)-phi(z)`. The triangle inequality
and monotonicity give

```
phi(d(A0,F))-phi(x) + phi(d(F,B0))-phi(y)
<= h_u(x)+h_v(y).
```

Also `x+y >= q`. There are nonnegative x'≤x and y'≤y with x'+y'=q. Concavity
makes each h_r decreasing, so the right side is at most
`h_u(x')+h_v(q-x')`. For a power with exponent strictly between zero and one,
each h_r is convex. This follows from its second derivative for z>0 and
continuity at zero, or by integrating the convex function
`(1-C)*(z+s)^(-C)` over `0<=s<=r`. A convex function on `[0,q]` has a maximum
at an endpoint. Therefore the exact maximum gain is

```
max(phi(u)+phi(q+v), phi(u+q)+phi(v)) - phi(t).
```

It is attained by F=A or F=B in the tariff model because the source endpoints
are geodesic. F=A wins when u≥v; F=B wins when v≥u. To see this, subtract the
two endpoint scores to obtain `h_q(v)-h_q(u)`. Ties in the two scores do not
imply that only these two physical charts can tie. If u=v=0 every one-cut gain
is nonpositive.

This proof uses only the native rank metric. It is not limited to canonical
binary charts or to dimension nine. Isometric spectator padding leaves the
four original distances unchanged. A new operation alphabet with a different
price, changed original endpoints or other shared jobs requires a new contract.

## Canonical projection for every concave tariff

There is a stronger structural statement for canonical subspaces and any
increasing concave phi with phi(0)=0. Suppose `A0<=A<=B<=B0` as subspaces.
For any canonical F, put `F'=A+(F intersect B)`. Then F' lies in `[A,B]`, and
its signed tariff is at least that of F.

Use the previously published native image formula
`L(W)={(x,z):x in W, z+x in W_perp}` from PR5772. It gives
`d(X,Y)=dim X+dim Y-2 dim(X intersect Y)`. Put

```
x_i = dim(F intersect A_i), with A_i = A0,A,B,B0;
k = x_2-x_1;
e_1 = u-(x_1-x_0) >= 0;
e_3 = x_3-x_2 >= 0;
s = dim(A0)-x_0 + dim(F)-x_3 >= 0;
delta = e_1+e_3.
```

The paid ranks are `k+s+delta` and `q-k+s+delta`. The two target ranks exceed
these paid ranks by `u-2e_1` and `v-2e_3`. Monotonicity permits increasing those
increments to u and v. Decreasing the common arguments to k and q-k then
increases h_u and h_v by concavity. The resulting expression is exactly the
signed tariff at F'. This proves projection without a finite search.

The endpoint maximum in the previous section needs the power hypothesis.
For the concave hinge `phi(r)=min(r,2)` and `(u,q,v)=(1,2,1)`, an interior cut
has score 2 and both endpoints have score 1. The verifier retains this
counterexample to prevent an incorrect extension to all concave tariffs.

## Any finite detour path

For intermediate charts F1,...,Fm, let the new target chain be
`A0,F1,...,Fm,B0` and the replacement paid chain be `A,F1,...,Fm,B`.
Every common interior edge cancels from the signed invoice. The gain is

```
phi(d(A0,F1))-phi(d(A,F1))
+ phi(d(Fm,B0))-phi(d(Fm,B)) + phi(q)-phi(t).
```

Every increasing concave phi with phi(0)=0 is subadditive. The metric triangle
inequality bounds the first difference by phi(u) and the second by phi(v).
Hence every finite path obeys

```
gain <= phi(u)+phi(q)+phi(v)-phi(t).
```

For m≥2, the tariff bound is attained by F1=A and Fm=B. Additional interior
charts cannot raise it. This applies to arbitrary Clifford coframes; their
native ranks need not come from canonical subspaces. It does not apply to a
shared graph that credits more targets than the stated target path, to several
original queries charged as one, or to changed original helper endpoints.
Those are different invoices and must be checked separately.

For source rank t≤9 and `0<C<=.01`, concavity bounds the three-part gain by
`3*3^(1-C)-9^(1-C)`. Jensen's inequality gives the bound at fixed t; scaling
makes it increase with t. It also increases with C on this interval:
`log(r)*r^(-C)` increases with r≤9 when `C*log(9)<1`.
At C=.01 the exact upper bound is below **.097259566**, hence below .1 H1.
No one-target path can pay even one extra H1 beyond the fully charged path.
This is a raw recursive bound; ordinary costs are additional.

## Exact source application

The source is PR5756 at `a1b338e5d9271b541f2a198f4fc19cefc565feed`.
The word and receipt are retained byte-exact. The source main fields are
`live union {r+112:r in live}`, not a contiguous prefix. The retained PR5751
local checker specifies this contract. All 559 complementary helper targets
and all 2534 helper-query flags are checked against it. Every source event
receives a frame and lifetime check, and the recounted full local paid and
target profiles equal the published receipt. This is not a repeat of the
source scalar endpoint or native-phase audit.

`QUERY-BOUNDS.json` records every instruction index, helper ID, four actual
frames and `(u,q,v)`. For each helper and each of the three tested exponents,
`RESULT.json` records the best query, target partition and exact gain enclosure.
It chooses at most one original query per helper. Alternative cuts on the same
helper are not added together. These are simultaneous optimistic maxima; their
physical compatibility is not established.

| C | One-cut total local gain | Arbitrary-path total local gain | Helpers needed for one H1: one cut / path |
| --- | --- | --- | --- |
| .00311313795 | 8.5995248896... | 13.4489218828... | 53 / 33 |
| .0034 | 9.3872657291... | 14.6816910724... | 48 / 30 |
| .01 | 27.2956951716... | 42.7447866237... | 17 / 11 |

The fee counts are exact minima in this relaxation. Every candidate comparison
and sorted prefix comparison has a rational interval separation or identical
signed coefficients. The previous prefix is strictly below one; the stated
prefix is at least one. They do not assert that those helpers admit compatible
physical splits. The source contains 32 helpers whose only query already spans
their complete target; all path gains for these helpers are nonpositive.

The complete caller uses 18 local copies. A local fee must be charged in every
copy that uses it. A fee shared across copies needs its own physical contract.
No whole-caller κ is obtained by adding these optimistic local gains.

## Verification

Run `python3.12 -B scripts/research_package.py --package
research/p104-helper-detour-projection`. Both normal and optimized runs are
registered. The standard-library verifier checks:

- all 4489 pairs of canonical native charts in dimension four;
- 183 actual binary flags, with 8784 concave-hinge projection checks;
- all 37180 feasible rank-nine flag-intersection patterns, with 334620 hinge checks;
- all 15 two-qubit Lagrangians and 6750 metric-hinge checks;
- all 135 three-qubit Lagrangians at three exact powers, with 405 endpoint checks;
- 4368 literal paths with up to three cuts, including nonnested paths;
- exact source ranks, frame chronology, target debits and per-helper fee prefixes.

The general proofs above cover arbitrary dimension and path length. The finite
checks test independent representations and their failure modes; they are not
the proof of the universal statements. A wrong contiguous-main partition, a
wrong query source frame and a missing original helper debit all reject.
The concave-hinge counterexample rejects a broader endpoint claim.
See VALIDATION.md for executed commands, source corruption and export results.

## Open next questions

1. Can a physical shared correction support at least the stated number of
   independent helper splits? Start with explicit helper IDs, source windows,
   arbitrary-input restoration and a complete native correction invoice.
2. Can a changed endpoint, several original queries or a non-path target graph
   beat these bounds? Write the changed signed edge invoice first.

The published retained-copy construction PR5774 and its active successor in
Discussion5600 change different contracts. The global chart work in5125/5593
also remains outside this theorem. No failure of those constructions is claimed.
Selected-frontier changes, merges and closures are outside this contribution.
Five inherited all-size assumptions and independent scientific acceptance remain.

Ali Romman with substantial OpenAI Codex assistance. No subagents. Apache-2.0.
Credit PR5756/5739 Joel Pulikkan with Claude assistance, PR5751, flyingviper PR5718,
zxv's moment arithmetic, the native compiler line and all retained source notices.
