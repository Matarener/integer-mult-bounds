# Adaptive architecture checks and independent receiver review

This package changes the number of paired banks and local calls, derives the
resulting native geometry, and prices its actual helper inventory. It also
independently reviews the positive receiver-sharing rewrite produced in the
sibling `native-alternatives` package.

The architectural investigation does **not** improve κ. Its main result is
an exact exclusion within the generalized paired-chain family, checked
separately for the original PR3734 supplier and the new receiver-sharing
supplier. Three pairs do admit an exact seven-call native
data geometry in dimension57. Their actual helper widths, however, impose a
clock-independent price ceiling below the four-pair result. Five pairs also
fail an exact pattern dual, and a single analytic argument excludes every
pair count from six upward. These results explain why changing the local
supplier remains consequential after the outer clock has been improved.

The separate receiver review is positive: the emitted new words preserve
all helper entrance/output frames and replace `H1 + H2` by `H3` on exactly
one receiver. The complete native operator and global κ admission are in
the sibling packages and the root integration; this review supplies a
separate check of the local identity, frame paths, source binding, and bill.

## Seven complete calls on three pairs

The current supplier has112 data ports per side, local paid profile

```
{1:2440, 2:725, 3:224, 4:102, 5:20, 8:8}
```

and408 helpers with width inventory

```
{4:26, 5:2, 6:18, 7:53, 8:96, 9:213}, width sum3278.
```

All eight centre `H8` children are retained. Both ordinary provider variants
have this same interface. The source words and native phase data are
authenticated by SHA256; the package does not substitute an optimistic
deleted-centre word for the complete supplier.

The paired-chain controller on three pairs is

```
F0, B0, bridge(0,1,+1), F0, bridge(0,1,-1),
B1, bridge(1,2,+1), F1, bridge(1,2,-1), B2, F2,
bridge(2,1,+1), bridge(1,0,+1), signed exchange.
```

Here `F(x,y)=(x,y+x)`, `B(x,y)=(x-y,y)`, and a bridge applies
`X_dst += c X_src`, `Y_src -= c Y_dst`. The exact6×6 scalar matrix is
identity after the final signed exchange. The first call makes nine native
axes available; each subsequent call adds eight, for57 axes in total.

`seven_geometry.py` reconstructs the actual port-dependent orthogonal
involutions and affine corrections for stages0 through6. It checks all784
port/stage routes, all3,136 side-specific entrance/exit phase identities,
every actual bridge frame, and all672 productive `FULL57` endpoints. The
phase test compares the full quadratic character multiplier modulo4, so it
is an all-character identity rather than a sampled numerical test. The
ordinary local supplier interface is retained source-bound evidence; this
script does not repeat its full local native replay.

The twelve positive idle children per port have the following census.
Each row occurs on both sides, with112 physical ports on each side.

| Owner pair | Native rank | Owner stages between the endpoints |
|---|---:|---|
| 1, initial interval | 16 | 0–1 |
| 1, short interval | 8 | 2 |
| 2, initial interval | 32 | 0–3 |
| 2, short interval | 8 | 4 |
| 0, final interval | 32 | 3–6 |
| 1, final interval | 16 | 5–6 |

Thus the complete per-replica native idle histogram is
`{8:448,16:448,32:448}`, of rank mass25,088. Seven local calls contribute
35,938, and the helper width credit is22,946. If every helper is hosted on
these data families, the remaining idle mass is2,142 and the complete raw
mass is38,080, compared with the productive normalizer57×672=38,304.

The stage labels in the table describe each owner's own chronology. They
do not restrict which stage a different replica's call may have when it
borrows that owner. The small `clock_screen.py` nominations explicitly
demonstrate this distinction: stage-blocked packing is infeasible, while
several interleaved eight-replica clocks satisfy the aggregate time/width
linear constraints. No physical fill is claimed for those nominations.

## Actual widths remove the apparent seven-call gain

Putting all2,142 remaining units at rank32 is too optimistic. The exact
unrestricted pattern relaxation instead has idle profile

```
{1:602/3, 5:896/9, 32:406/9}.
```

Its rigorously enclosed moment root is

```
[0.001718630707363138070731,
 0.001718630707363138070732].
```

The sibling `global-budget/p3_certificate.py` authenticates the emitted
seven-call geometry, checks its rational pattern primal and every dual
inequality, and proves this ceiling under every clock and replica count.
The relaxation has already dropped chronology and physical-family
injection; adding those requirements cannot improve its price. The finite
clock search therefore stopped at that point.

## Generalized pair-count screen

For `p` pairs in the same fixed-q paired-chain geometry, write

\[
m=16p+9,\qquad c=2p+1,\qquad W=224p.
\]

The idle bins are224(p−1) copies of rank8, and448 copies of each rank16q for
q=1,…,p−1. The unchanged local word has rank mass5,134 and helper width
credit3,278 per call. Consequently

\[
R=(2p+1)(112m-6078),\qquad
D=mW-(5134c+R)=96p-64.
\]

Here `R` is the remaining idle rank mass and `D` the complete raw deficit.
The proof applies when the helper credit is supplied by these productive
data families; additional external productive banks change the model.

`pair_count_screen.py` nominates unrestricted bin patterns using column
generation. Its finite knapsack state space includes every combination of
widths4 through9. All emitted nonzero primal counts are reconstructed as
rationals and checked against every bin and helper equation. Floating
solver duals are diagnostic, and are not used as certificates.

`pair_count_certificate.py` rechecks those primal equations without SciPy
and derives exact duals from rational outward child prices. An exact
knapsack dynamic program verifies all integer patterns, including patterns
that were never nominated by the search. It also checks rejecting
perturbations and reproduces the four-pair target as a positive control.

For the exclusion, every remaining native idle child is granted its
unsplit price even if its rank violates the outer guard. This strengthens
the relaxation. The actual guard is `2r² < m²`, whose largest integer rank
is `isqrt((m*m-1)//2)`; a `0.7m` approximation is not used in the final
certificate. Splitting a remainder into permitted positive children can
only increase its price for an exponent between0 and1.

| Pairs | Dimension | Original supplier, unsplit relaxed root | Receiver-sharing supplier, unsplit relaxed root |
|---:|---:|---:|---:|
| 2 | 41 | Raw width capacity shortfall7,430 | Same raw shortfall |
| 3 | 57 | 0.001718630707363138… | 0.001718807452513541… |
| 4 | 73 | 0.001730578437266246… | 0.001730739780298357… |
| 5 | 89 | 0.001695085010372571… | 0.001695230571360293… |
| 6 | 105 | 0.001647674588177460… | 0.001647806668022288… |
| 7 | 121 | 0.001597187924293713… | 0.001597308527612954… |
| 8 | 137 | 0.001546308951553315… | 0.001546419602497432… |

The decimal columns summarize the emitted profile brackets; the complete
rational endpoints and dual lower bounds are in
`evidence/PAIR-COUNT-CERTIFICATE.json`.

For each supplier, the p3 and p5–p8 duals strictly exclude that supplier's
own four-pair target. The new p4 aggregate profile is additionally checked
to equal the complete physical profile in
`global-budget/receiver-sharing/PRICE.json` exactly, after division by360
replicas. The receiver word payloads and the independent width review are
hashed inputs to the family certificate; the changed word is priced using
its changed local bill throughout.

### One analytic bound for every p≥6

Let `a` be the retained four-pair target and

\[
A=\sum_r n_r r\log r.
\]

Grant all idle rank the largest native rank `m−25`, independently of its
actual bins or the permitted rank guard. Applying `exp(x)≥1+x` to the
moment shows it exceeds one whenever

\[
f(m)=a\!\left[5134\log m-A+
(112m-6078)\log\frac m{m-25}\right]-48+\frac{896}{m-1}>0.
\]

Exact rational log bounds give
`f(105) > 0.13416910002396307622`. Moreover,

\[
f'(m)\ge\frac{5134a}{m}-\frac{896}{(m-1)^2},
\]

because `log(m/(m−25))≥25/m`; the dropped term is
`81950a/[m(m−25)]`, which is positive. The certificate checks the rational
gate `5134a·104² > 896·105`. Since `(m−1)²/m` increases for `m>1`, this
derivative bound stays positive for every real `m≥105`. Every integer
`p≥6` therefore fails the target. This is an analytic tail argument, not a
finite search extrapolated to untested pair counts.

For the receiver-sharing supplier, `A` increases by `3log(3)−2log(2)` and
the certificate uses its own improved four-pair target. The same two exact
gates pass, with `f(105)>0.13454854262937513114`. Its entire `p≥6` tail is
therefore excluded as well.

These statements are restricted to the stated paired-chain coverage law,
current supplier profile, current helper stock, and productive fields.
They do not exclude changed local words, other scalar controllers,
different endpoint contracts, or new bank families.

## Independent review of the positive receiver rewrite

The sibling construction modifies two consecutive ordinary B events
involving `h=544`, `u=672`, and `v=676`. Their frames are

\[
P=\operatorname{span}(51),\quad
Q=\operatorname{span}(414,51),\quad
R=\operatorname{span}(413,72,48,3),
\]

with exact dimensions1,2,4 and `P⊂Q⊂R`. The old two operations are
`u += h/2` and `v -= h/2`, both atQ. The replacement is

```
u += v      at P
v -= h/2    at Q
u -= v      at R
```

This preserves arbitrary initial values, including dirty receiver and
helper values. Let `A` denote the canonical native lift fromP toQ and `B`
the lift fromQ toR. The old outputs, when compared atR, are

\[
u_R=BAu+Bh/2,\qquad v_R=BAv-Bh/2.
\]

The new program obtains the same outputs by cancellation of `BAv`. No
commutation of the two frame lifts is required. The original first later
contacts are B1109 foru and B1114 forv, both atR; there are no intervening
receiver reads or warps. Moving those lifts earlier consequently has the
required local contract.

`review_receiver.py` imports none of the constructor's scalar, frame or
cleanup helpers. For both emitted providers it independently checks:

- Exact old and new event preimages, unchanged surrounding scalar events,
  and the single necessary shift of subsequent warp indices.
- The complete three-register rational matrix, with a wrong-sign control.
- All632 live frame paths using explicit finite binary spans, including
  retained warps, centre contacts, terminal frames, and a nonmonotone-frame
  rejection control.
- The exact path-profile change on receiver672 alone:
  `−H1−H2+H3`; every other register's positive native steps are unchanged.
- All408 helper widths, their unchanged total3,278, and the unchanged
  entrance/output frame maps.
- The complete inverse cleanup syntax on the admitted owned-buffer roles.

The new supplier profile is

```
{1:2439, 2:724, 3:225, 4:102, 5:20, 8:8}.
```

Its raw rank mass remains5,134. The extra scalar operations are one B add
and one inverse-cleanup add, or four real scalar primitives per complete
local call. Because the widths and endpoints are unchanged, this edit is
eligible to reuse the retained physical owner allocation; that actual
binding and the precision/global price are separate root and
`global-budget` obligations.

The review does not independently replay every whole-word Gaussian
operator column, every native phase recipe, or the complete multiplication
reduction. Those checks have separate native and integration receipts.

## Reproduction

Run from the repository root, with assertions enabled:

```
python3 -B research/kappa-adaptive-continuation/architecture/seven_geometry.py
python3 -B research/kappa-adaptive-continuation/architecture/review_receiver.py
python3 -B research/kappa-adaptive-continuation/architecture/pair_count_certificate.py
```

These commands use the Python standard library. Their source dependencies
are the prior frozen followup package, the exact outward-rational invoice
engine, and the sibling emitted receiver words. They do not rerun the old
350-second global residual suite. Each receipt records portable relative
paths and exact source hashes. Regenerated gzip payloads are compared by
their canonical decompressed content when container bytes are irrelevant.

Optional discovery replay, requiring NumPy and SciPy:

```
python3 -B research/kappa-adaptive-continuation/architecture/pair_count_screen.py --guard native
python3 -B research/kappa-adaptive-continuation/architecture/clock_screen.py --replicas 8 --slopes 1/2 1 2 4 --seconds 15
```

The optional floating nomination files are not independent proofs of
optimality or physical allocation. The exact certificate consumes only
their explicit pattern tuples and rational counts, and rechecks the
relevant mathematical inequalities itself.

## Sources and attribution

The original paired-chain and E8 local constructions are attributed to
Jacob Sussman and the generalized B_K work of DaysSky and its retained
contributors. Rohan Arun's `complex501-followups` stage-count screen
provided a historical comparison with a different120-port, larger-helper
inventory. Its negative seven-stage result was not treated as a barrier
for the current112-port supplier.

The actual modern supplier and native phase data come from the retained
PR3734 `staged544-producer-return` package by dataisfire, with the
PR3682/PR3638/PR3605 and earlier PR3133/PR2979 ancestry credited in its
`SOURCE-CREDITS.md`. That package remains frozen. Erwan Secousses /
ChaloupeMusic's PR3815 `staged544-clock-ceiling` supplied the current
clock/weak-duality context; the new exact pattern certificate uses a
separate rational knapsack implementation.

The receiver-sharing mechanism is the transpose of Nick Petalas's
`rank7-shared-restore-fanin` dirty-source identity. The new construction is
owned by the sibling native-alternatives package. This directory adds the
changed-architecture experiment, analytic family argument, and a bounded
independent review. It does not claim a new independent human review.

New work was prepared under the user's direction with substantial OpenAI
assistance. Apache-2.0. Original contributor credit and inherited
conditional theorem obligations are retained.

## Open next questions

- Can a changed native supplier preserve the helper stock while replacing
  several small recursive children by a larger admitted child? The exact
  receiver rewrite is a concrete positive instance; any extension should
  start from its fully priced native word and explicit frame contacts.
- Can a different endpoint contract or scalar controller change the raw
  coverage identity? Such a construction lies outside the pair-count
  exclusion and requires a new complete native/hosting invoice.
- Can the inherited uniform/all-size realization, precision/recovery, or
  analytic transfer obligations be discharged for the newly admitted
  words? This package preserves those assumptions and does not settle them.
