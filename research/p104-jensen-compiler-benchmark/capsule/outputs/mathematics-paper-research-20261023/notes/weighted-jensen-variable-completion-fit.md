# Weighted Jensen for the variable completion and helper-split proposal

The proposed Jensen implication is correct and strict under the stated
strict geometric-mean condition. The source higher-moment theorem permits
the endpoint `u=C`. A single fixed `u=C_test` also covers both requested
savings after the explicit small offset correction below.

This is a paper-only sufficient-condition review for the fixed PR5565
paid invoice and the strategy's named hypothetical target splits. It is
not a construction of those splits, an executed finite compiler certificate,
or a new multiplication endpoint. The root's earlier finite benchmark
receipt remains separate.

## 1. Primary weighted Jensen statement

The already inspected primary source is Wassily Hoeffding, *Probability
Inequalities for Sums of Bounded Random Variables*, JASA58(301),13–30(1963),
DOI[10.1080/01621459.1963.10500830](https://doi.org/10.1080/01621459.1963.10500830).
Printedp14/PDFpage3, equation(1.9), states finite weighted Jensen for a
continuous convex function on an interval and positive weights summing
to one. The original scan was downloaded and this page visually read.
[Original published scan](https://www.cs.rpi.edu/academics/courses/spring06/random/hoefding.pdf).

No new primary search is needed. The application uses an explicit convex
exponential and a strict inequality between two arguments; it does not
depend on importing an unstated strict version of Jensen.

## 2. Exact lemma and strictness

Let positive paid ranks `r` have nonnegative multiplicities `p_r`, with
at least one positive multiplicity. Omit zero-weight terms. Define

```
P_s = sum_r p_r*r^s,
P1 = sum_r p_r*r > 0,
w_r = p_r*r/P1,
mu = sum_r w_r*log(r),
t = 1-C, 0<C<1.
```

The weights are positive on their support and sum to one. For
`f(x)=exp(-C*x)`, continuity and convexity hold on all real numbers;
indeed `f''(x)=C^2*exp(-C*x)>0`. Weighted Jensen therefore gives

```
P_t/P1 = sum_r w_r*exp(-C*log(r)) >= exp(-C*mu).
```

The weights are proportional to rank mass `p_r*r`, not call count
`p_r`. Replacing them by call-count probabilities changes the identity
and does not prove the stated comparison.

If `log(c)>mu`, multiplication by `-C` reverses the strict inequality,
so

```
c^(-C) < exp(-C*mu) <= P_t/P1,
P1/c^C < P_t.
```

For any positive target moment `T_t`, the endpoint ratio consequently
satisfies

```
gamma_C = P1/(c^C*T_t) < P_t/T_t = alpha.
```

Strictness follows already from `log(c)>mu`. If equality holds there,
strict Jensen would still give a strict final inequality whenever the
supported ranks are not all equal; that optional refinement is not needed
for this candidate. If `log(c)<mu`, failure of this sufficient test proves
no impossibility: the Jensen gap can still make `P1/c^C<P_t` true.

Let `B` count the actual productive fields, and let `b` be the proposed
completion floor base. If `b*B<=P1`, then

```
delta = b*B/(c^C*T_t) <= gamma_C < alpha.
```

Thus, conditional on `alpha<1`, these two inequalities supply all three
strict subunit ratios. They are sufficient, not necessary, conditions
for the retained completion/splitting route. Neither Jensen nor this
argument bounds all possible changed controllers or compiler routes.

## 3. The endpoint and the fixed-u correction

The authenticated higher-moment README§2 requires
`u>=C`, `sigma=t+u>=1`, integer `1<c<b<m0`, and integer `v>=1`.
It explicitly identifies `u=C`, `sigma=1` as the rank-one-tail endpoint.
The last inequality in its paid-split proof becomes equality at that
endpoint, so there is no missing strict-exponent condition.

At each separate saving one may set `u=C`. To use a single fixed offset
at both savings, set

```
C_goal=.0033,
C_test=.0033000005=6600001/2000000000,
u=C_test,
s=u-C in [0, 1/2000000000].
```

Then `t+u=1+s>=1`, as required. If every positive paid rank is at most
`Rmax`, the exact finite-sum bound

```
P_(1+s) <= P1*Rmax^s
```

and Jensen give

```
gamma_u
 = P_(1+s)/(c^(C+s)*T_t)
 <= alpha*exp(-C*(log(c)-mu)+s*log(Rmax/c)).
```

For the fixed invoice `Rmax=72` and `c=12`, the correction is `s*log6`.
It is enough to certify the positive gap

```
x = C*(log12-mu)-s*log6 > 0.
```

Then `gamma_u<=alpha*exp(-x)<alpha`. For a rational upper certificate,
`exp(x)>=1+x` gives `exp(-x)<=1/(1+x)`.

Keep the completion comparison separate: `delta<=gamma_C` does not
automatically imply `delta<=gamma_u` when `u>C`. The ratio
`P_(1+s)/c^s` need not increase with s. Instead use

```
delta = (b*B/P1)*gamma_C < (b*B/P1)*alpha.
```

The strategy's explicit count margin below makes this sufficient at both
points without asserting monotonicity in u.

## 4. Binding to the strategy's one named hypothetical inventory

The paid invoice is fixed at PR5565 head
`9af814164b9dfc21f19ec737959d67cb71488c95`. Its complete paid rank mass
is `P1=241268`; the largest paid rank is72. The new target proposal
replaces145 distinct baseline rank9 helper targets per FULL by rank4 and
rank5 targets, hypothetically selecting145 from the425 declared baseline
rank9 targets. No actual target IDs or realizing edits are supplied.
Its proposed local helper profile is

```
{4:228, 5:150, 8:14, 9:280}.
```

It preserves helper rank mass and raises the local field count from527
to672. Across18FULL calls it adds2610 proposed productive fields,
giving `B=15424`. The complete target rank mass remains242028 and the
rank-one surplus remains760. The proposed completion bases are
`c=12`, `b=13`, with ambient base145.

The following numerical certificates are supplied by the strategy's
paper derivation; this literature worker has checked their algebraic
role but has not executed their arithmetic or a scientific verifier:

```
sum_r p_r*r*log(r) < 2940373489/5000,
mu < 2940373489/1206340000,
log12 > 1553/625,
log12-mu > 57140143/1206340000,
13*B/P1 = 50128/60317 < .84.
```

The logarithm estimates use the stated rational brackets on log2, log3
and log5, with conservative replacements for the rank7 and rank56 terms.
Their full certificate belongs to the strategy's frozen packet and later
independent qualification.

For the fixed-u version, the supplied positive gap bound is

```
x > 188561391079677/1206340000000000000.
```

The strategy reports that this gives `1/(1+x)<99985/100000`. It also
reports complete raw target-minus-paid margins above
`.37780894998100236055` at the goal and `.37769467317179821257` at the
tested point, and hence `alpha<1-1e-6` at both. Taken as premises, these establish

```
gamma_u < .99985,
delta < .84*alpha < .84,
alpha < 1-1e-6.
```

These are paper sufficient bounds for the one named target proposal.
They do not inherit the earlier fixed17/18 negative result or refute it:
both the target inventory and the cutoff/completion choices have changed.
No nearby tuple, source scan, or parameter sweep was run here.

## 5. What the source theorem then allows, and what it does not

Once actual source-bound ratios below one are available, README§2
proves that a sufficiently large finite tensor power yields a strict
charged moment through

```
alpha^v+2*gamma_u^v+2*delta^v.
```

The strategy nominates the single additional finite tuple

```
v=32768, rho=19997/20000, alpha_reserve=1e-6,
theta_bar=39/40, logarithm_power=22000,
uniform_grid_step=14000000000, j_upper=1500000.
```

Its paper bound is `rho^v<1/128` and hence the normalized upper bound
`1/(1+32768*1e-6)+4/128=516137/516384<1`. It supplies geometric,
capacity and initial-range witnesses, plus a finite upper bracket for
the uniform threshold. These remain strategy-derived paper evidence;
this literature round did not execute their comparisons, find the
least j, or rerun an engine. The candidate needs its own exact finite
qualification. Jensen supplies neither a least tensor power nor a
fully certified uniform compiler. The generic positive-logarithm-power
theorem and native precompilation assumptions remain the same as in
the preceding review.

Most importantly, the proposed target split changes productive field
count. The source disjoint-axis identity for a paid rank9 job merely
implements it as rank4 then rank5 on the same arbitrary owner. It does
not create two distinct independent productive inputs. The145 target
splits therefore need an actual construction with the additional original
input fields, autonomous endpoints, exact charts and absolute phases,
legal whole-job adapters, and all ownership/restoration requirements.
The source's completion operation also creates no new productive input.

Until that construction exists, the changed B and target moment are a
hypothetical contract. Their favorable count and Jensen bounds cannot
establish physical split availability or preserve the source paid invoice.
The complete expanded scalar, movement, storage, precision and fixed-tape
costs require new binding as well; old scalar caps do not transfer from a
moment calculation.

Any next finite qualification of this nomination is proposed as
compiler-only hypothetical-profile feasibility. BIT and the particular retained outer54+4 ledger are later
complete-admission obligations, not requirements for that first gate to
pass. That predicate count is not universal for a changed consumer route.
No funded or selected kappa, native word, scientific replay or upstream
write is claimed by this note.

## 6. Source custody and review status

The primary PDF remains SHA256
`3021bcc097ef23a99a84d0eef8dcce2fd835c71df79a105727d3e03f8f0b8930`.
The exact generic source README is Gitblob
`0a736ca89e1eafb73a30e1f2589cc45e6b5f76c3`, SHA256
`ebe80b68ff026ce90f71f274c31744f4c0b36132d15ebb7e39cf2d5df4df270d`,
authenticated at canonical`5e0052ca0aa3036a3afa8b0438927377c8d97d53`.
Its endpoint and proof were reread from the previously frozen export.
No new feed read or theorem search was performed.

The conclusion is a checked paper implication from the supplied positive
moment/count premises. All numerical candidate certification remains
separate. This note preserves the preceding146 ledger records and the
frozen earlier compiler-capacity note.

The final strategy packet is `variable-completion-split-family.json`,
SHA256`e432573e6390a7c4922dea42dcf239d679fa886b54df18988d268b6aef4d1dbb`.
Its JSON and companion prose were read and preserved under this round's
reference directory. The new ownership receipt recorded in that packet
is strategy/curator evidence; this worker performed no independent feed
refresh.
