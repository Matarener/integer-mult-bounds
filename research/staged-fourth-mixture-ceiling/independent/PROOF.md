# Independent pooled ceiling for the frozen PR4088 mixture

This is a mathematical check of PR4088 head
`76088d49e3ed4142a958659aa996b0ca4da5e88e`, using the source snapshot in
`../source4088/`. The finite supplier is credited to Cinna Davis with OpenAI
Codex assistance and the predecessor authors credited in that package. The
candidate optimal patterns and symbolic dual were nominated by the separate
owner-allocation specialist. This check independently verifies their arithmetic,
complete pattern coverage, sharpness for the relaxed model, endpoint signs and
comparison. It imports neither a solver nor the source pricing code.

## Model and actual source invoice

Write `H_r(k)=r^(1-k)` for positive r, with `H_0=0`, and
`d=2H_1+3H_3-3H_4`. Among 3240 calls, let `x` use the fourth entry and the
remaining `3240-x` use the third entry. Every original call has 408 helpers.
The source subspaces give actual widths

| Width | THREE | FOUR | Demand over all calls |
|---|---:|---:|---:|
| 5 | 28 | 28 | 90720 |
| 6 | 18 | 18 | 58320 |
| 7 | 56 | 57 | 181440+x |
| 8 | 93 | 92 | 301320-x |
| 9 | 213 | 213 | 690120 |

Only helper 601 changes, from width 8 to width 7, in both orientations.
Independent GF(2) elimination checks the dimensions and the containment of every
entry subspace in its terminal subspace. The local profiles are retained source
invoices, checked against both words' report fields; this check does not replay
the entire scalar operator or native implementation.

The 18 distinct children have capacities `6*8+4*16+4*32+4*48` per port. There
are 112 distinct ports and 360 replicas, hence

`B8=241920`, `B16=B32=B48=161280`.

The current replication is derived from all 3240 unique `(stage,replica)` pairs
in `owner/ORDER.json`, with stages 0..8 and replicas 0..359 and preserved
per-replica stage order. Historical template fields such as `replicas=37` are
not used. The retained source moment convention has ambient width 73 and stock
`W=896*360=322560`.

Total capacity is 17418240, hosted helper width is `10695240-x`, local paid rank
mass is `16708680-x`, and residual rank mass is `6723000+x`. Complete paid rank
mass stays `23431680=65088*360`; no helper, residual or empty bin is dropped.

## Pooled pattern relaxation

For each capacity c in {8,16,32,48}, enumerate every vector of nonnegative
integer counts `n=(n5,...,n9)` satisfying `sum w*nw <= c`. Its residual rank is
`r=c-sum w*nw`. There are respectively 5, 21, 158 and 657 patterns, including
all four empty patterns: 841 in total.

Allow nonnegative real multiplicities `z[c,n]`, subject to exact bin-count and
item-count equations

`sum_n z[c,n]=Bc`,

`sum_(c,n) nw*z[c,n]=Nw(x)`.

Allow real `0<=x<=3240`. These relaxations contain every legal integral,
chronological, distinct-family allocation in the frozen interface. They erase
chronology, physical families, helper identity and offsets, while retaining each
helper's whole integer width and every original capacity.

The complete moment before subtracting stock is

`3240*L3(k) + x*d(k) + sum z[c,n]*H_(c-w.n)(k)`.

## Exact dual and integer primal

Set

```
v9=(H3-H48)/5
v7=(v9-H5)/2
v8=v7+d
v6=v7-d
v5=-H5
u8=-v8
u16=-v7-v9
u32=H5-3*v9
u48=H48
```

The checker certifies `u_c+sum n_w*v_w <= H_(c-w.n)` for every pattern,
uniformly throughout

`K=[0.001730980255989036959962,0.001730980255989036959963]`.

Eight inequalities are exact symbolic identities. All other 833 are strictly
positive after outward rational enclosure; their common minimum is greater
than 0.00120724281727557. No floating-point LP residual is accepted as evidence.

Summing the inequalities gives a complete lower moment. The coefficient of x
is exactly `d+v7-v8=0`, so it applies simultaneously to every real x, and hence
every integer x, without sampling mixtures or choosing the sign of an interval.

The following integral pooled fill attains equality:

| Capacity | Width multiset | Multiplicity | Residual |
|---|---|---:|---:|
| 8 | 8 | 241920 | 0 |
| 16 | 7,9 | 161280 | 0 |
| 32 | 9,9,9 | 1620 | 5 |
| 32 | 7,7,9,9 | 10620 | 0 |
| 32 | 6,8,9,9 | 58320 | 0 |
| 32 | 5,9,9,9 | 90720 | 0 |
| 48 | empty | 138492 | 48 |
| 48 | 9,9,9,9,9 | 22788 | 3 |

Every count, capacity and demand equation is checked exactly. Strict slack on
all other patterns forces every pooled optimizer in K to use only these eight
patterns. The width-6 equation forces 58320 copies of `(6,8,9,9)`, while the
capacity-8 equation forces 241920 width-8 items. Thus

`301320-x=241920+58320`, giving the unique optimal mixture `x=1080`.

The other equations force the displayed multiplicities. Its idle profile is
`22788 H3+1620 H5+138492 H48`, and its complete paid profile is

`{1:8060040,2:2310120,3:751788,4:327240,5:66420,8:25920,48:138492}`.

## Independent review of the broad-interval refinement

`review_broad.py` independently checks the owner specialist's three-dual,
piecewise-affine refinement using this directory's separate enclosure engine.
It certifies all 841 patterns for each dual throughout `0.00173<=k<=0.00174`.
The central dual has 8 exact identities and 833 strict inequalities; the left
dual has 11 identities and 830 strict inequalities; the right dual has 9
identities and 832 strict inequalities.

Each nonidentity slack has zero rank mass. Thus dividing a form `sum e_r H_r`
by k gives `sum e_r g_r(k)`, where `g_r=(H_r-r)/k`. Its derivative is

`g'_r(k)=r[1-(1+k log r)exp(-k log r)]/k^2 >= 0`,

by `exp(t)>=1+t` for `t>=0`. Using the lower endpoint for positive-coefficient
lower bounds and the upper endpoint for negative-coefficient lower bounds gives
an outward interval for the whole range. This argument requires the exact zero
rank-mass test; the checker rejects a form that fails it.

The exact optimal idle profiles for real x in the pooled relaxation are

```
0<=x<=1080:
  (22842-x/20) H3 + (1890-x/4) H5 + (138438+x/20) H48
1080<=x<=3240:
  (23328-x/2) H3 + (1080+x/2) H5 + 138492 H48.
```

The review encodes every proposed multiplicity as exact rational affine
coefficients. It verifies bin and item balance coefficient by coefficient, each
integer pattern's capacity, nonnegative multiplicities at both interval
endpoints, and symbolic complementary slackness with the corresponding dual.
Affineness proves nonnegativity on every real x between endpoints. The complete
left derivative divided by k lies in
`[-0.348857712,-0.348494057]`, while the complete right derivative divided by k
lies in `[4.365719222,4.365911869]`. These signs include the changed local paid
profile and prove the unique optimum x=1080 throughout this broad k interval.

The broad review rejects a nonzero-mass factorization, an increased capacity-8
dual that preserves zero rank mass, a missing capacity-48 bin, an extra affine
pattern, and a negative endpoint multiplicity. The result is in
the report emitted by `independent/review_broad.py`. It remains a relaxation with real pattern multiplicities.

## Root certificate and comparison

The independent enclosure computes `log r` by range reduction and 108 positive
atanh terms with an explicit geometric tail. It then computes
`H_r=r*exp(-k log r)` on the exact integer lattice of spacing `10^-90`, using
outward term recurrences and even/odd alternating Taylor bounds through degrees
64 and 65. Signed coefficients reverse interval endpoints. The source pricing
engine is not imported or called.

For the ideal profile, complete moment minus `W*H73` is strictly negative at
the lower endpoint (approximately `-1.7332795175363e-17`) and strictly positive
at the upper endpoint (approximately `4.8939596059017e-17`). Every positive rank
is below 73. Therefore its normalized moment is strictly increasing in k, giving
the displayed root bracket. At the upper endpoint, duality puts **every** legal
frozen-interface mixture strictly above stock; monotonicity bounds every such
mixture's root by that endpoint. The pooled primal makes the bracket sharp for
the relaxed model.

The PR4088 literal profile has the independently checked root bracket

`[0.001730978305075885693430,0.001730978305075885693431]`.

Subtracting brackets puts the pooled ceiling's root headroom over the literal
root in

`[0.000000001950913151266531,0.000000001950913151266533]`.

The literal-minus-ideal idle profile is
`-3H3+5H5+H16+2H32-2H48`. Its truncated-rank sums at the knots 3,5,16,32,48
are 9,21,32,32,0. Between knots these are affine and nonnegative, strictly
positive on a set of positive measure. Since for `0<p<1`,

`r^p=p(1-p)*integral_0^infinity min(r,t)*t^(p-2) dt`,

the literal moment is strictly larger than the ideal moment for every
`0<k<1`. This comparison uses equal complete rank mass and the same width,
stock, local suppliers and surcharge convention.

## Coverage and limits

This is a written duality/majorization proof with finite exhaustive rational
checks over the complete 841-pattern domain, an exact integral pooled witness,
and exact endpoint enclosures. It is not a formal-kernel proof or a fresh native
operator proof. The root cap applies to all THREE/FOUR mixtures using the frozen
3240-call, 360-replica, width-73 and stock-322560 interface and these unchanged
original capacities, even with improved chronology and allocation. It does not
apply to changed supplier words, widths, call counts, capacities, stock, ambient
width or any broader mechanism.

The optimistic fill has no certified chronological or distinct-family realization.
Its root is a ceiling, not a construction or achieved kappa. This check neither
invalidates PR4088's finite literal witness nor supplies its missing inherited
all-size/ordinary/outer admission, source access, precision, tape, recovery or BIT
transfer obligations. No new kappa claim follows.

Replay from the package directory with standard-library Python:

```
python3.12 -I -B independent/check.py --source source4088 \
  --target-k 0.001730980255989036959963 --controls
python3.12 -I -B independent/review_broad.py --source source4088
```

The first command always checks both ideal endpoints and both literal endpoints;
the explicit target additionally checks the all-mixture upper bound. An optional
`--output PATH` saves the exact rational intervals and source hashes in a fresh
report. The second command checks all three duals and both affine primal regions
over the wider interval `[0.00173,0.00174]`.
Controls reject a wrong bin-dual sign, a raised capacity-48 dual and an omitted
capacity-48 bin. Arithmetic controls check all k=0 integer powers and the
nontrivial exact identity `(2^100)^(99/100)=2^99` through the full enclosure path.

Either independent command accepts `--output PATH` to save its report. The
committed top-level `RESULT.json` is the primary checker's certificate; the
independent commands freshly derive their own endpoint, primal, dual and control
evidence and do not trust that primary certificate.
