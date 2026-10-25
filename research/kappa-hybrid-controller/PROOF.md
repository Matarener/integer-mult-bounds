# Conditional saving 0.003001053 from the hybrid controller

Subject to the inherited native and transfer hypotheses stated below,
the construction gives

\[
T(n)=O\!\left(n(\log n)^{1-\kappa}\right),\qquad
\kappa=0.003001053.
\]

The physical change is proved in `NATIVE.md`. It specializes sixteen
transverse factors of the source Laurent controller to identity and pays
for their remaining $Q^{-1}$ shears directly. The final raw controller
has nineteen source-bound native invocations, 1792 directly paid Gaussian
requests, and 11560 independent productive fields. The native supplier
uses [PR4441's fresh-helper boundary retiming](https://github.com/CrocSwap/integer-mult-bounds/pull/4441),
with unchanged local source bytes pinned at
`ccdae89b2ab9ced24ee3e7adfdb670ef80d223d9`. The query-thinning
mechanism and p17 schedule were independently given in
[PR4440](https://github.com/CrocSwap/integer-mult-bounds/pull/4440),
at head `40e22a83ed660d3d6074c4f2dbf14bfb621eee51`.

Updated PR4441, at
`5f9d871c6bd1b9e34db5a7ea5ef08a908e94db39`, also combines this
retimed supplier with the same p17 profile and admits `0.00300105`.
That updated head and its complete dependency changes remain in the
publication ancestry. The contribution here is an independent
source-bound physical certificate, the bounded controller search,
the separately replayed p6 BIT supplier, and the endpoint refinement
to `0.003001053`. The combined raw profile is shared with updated
PR4441.

The retimed supplier replaces the preliminary lifetime-pruned local word.
Its construction subsumes the fifteen earlier terminal-climb deletions.
The final invoice uses the retimed profile directly and adds no separate
pruning gain. Its complete local source and boundary proof are retained
at [../fresh-helper-boundary/](../fresh-helper-boundary/).

This theorem remains conditional on the admitted all-column native
semantics, permitted whole-job matchers, spectator law, mixed compiler,
fine-prime/analytic estimates, precision, stock, fixed-tape realization,
and exact recovery used by the PR4359/PR4416 line. The scripts check the
finite native modifications and exact arithmetic inputs. They are not a
formal verification of the complete multiplication theorem.

## 1. Complete raw moments

Use the productive and paid multiplicities $T_k,P_r$ in
`parameters.py`, including all local helper outputs, direct queries and
specialized whole idle requests. Put

\[
T_\tau=\sum_kT_k k^\tau,\qquad
P_\tau=\sum_rP_r r^\tau,\qquad \tau=1-C.
\]

The exact rank-one moments and number of productive owners are

\[
T_1=260798,\qquad P_1=259998,\qquad B=11560.
\]

Thus the complete rank-one surplus is 800. The raw ranks overlap:
the smallest productive rank is four and the largest paid rank is 72.
A positive raw moment therefore still requires a strictification step.

The numerical discovery root is approximately 0.003001054183175. The
certificate uses the strictly smaller rational point

\[
C=C_{\rm test}=0.003001054=\frac{1500527}{500000000}.
\]

All later inequalities use rational interval bounds. No floating-point
root or search score is used as acceptance evidence.

## 2. Chronological native tensor substitution

The hybrid unit retains the same all-column request interface as its
native components. At a direct paid position with $f$ columns it makes
one rank-$f$ request on a complete owned copy. The surrounding address
route is $P\otimes I_f$, with the inverse route and repeated $q$
translation. Every field includes its full control and spectator ranges.
The query retains the current complete ancestor weight.

Apply the chronological tensor construction of the admitted native rule.
Suppose units $U,V$ have productive ranks $k_i,h_j$, and paid ranks
$r_\ell,s_a$. Run copies of $U$ on the distinct $j$-indexed owners
at column count $h_j$. At each common paid position $\ell$, pause
those copies. Normalize their complete current jobs, run one full $V$
unit at column count $r_\ell$, restore the whole-job matchers, and resume
the paused $U$ copies. Canonicalization uses both recorded monomial
boundary factors of each complete physical job. These factors need not
be an inverse pair. Placement on the desired disjoint coordinates then
uses coordinate conjugation; Fourier rank alone does not supply an
unrecorded normalizer.

The resulting productive ranks are $k_i h_j$. The remaining paid ranks
are $r_\ell s_a$. Arbitrary-input correctness permits correlated current
values, while physical owners remain distinct. Every suspended owned
center or direct-copy bank remains allocated until its own release.
No copy or zero-initialized work stream receives productive credit.
Every unused coordinate remains an arbitrary spectator.

This is chronological replacement of complete physical requests. It does
not expand a scalar sum and assign rank products without a program. The
copied-stream interface and the arbitrary-input native gates provide the
same closure at direct and native paid positions.

After $v$ copies the raw productive and paid moments are
$T_\tau^v,P_\tau^v$. There are $B^v=11560^v$ productive owners.
The conservative ambient rank is $m=281^v$; unused stage coordinates
are retained in this bound. Raw productive ranks are at most $153^v$.

## 3. Paid completion and complete split tails

Choose

\[
v=17160,\qquad J=18^v,\qquad L=19^v.
\]

After the entire native product has finished, normalize each productive
job of rank $K<L$ and append a paid transform on $L-K$ disjoint
coordinates of the same owner. The completed target has rank $L$.
There is room inside the ambient $281^v$, and no new productive input
is introduced. Every whole-job input/output normalizer is an actual
finite program record, including its phase and movement.

Next split every paid rank above $J$, including all completion requests,
into consecutive disjoint jobs of ranks $J,\ldots,J,r$. For a paid
rank $R>J$, write $R=qJ+r$. Its split moment is at most

\[
qJ^\tau+r^\tau\le RJ^{-C}+J^\tau\le2RJ^{-C}.
\]

Keeping unsplit requests of rank at most $J$, the full original paid
part is bounded by

\[
P_\tau^v+2P_1^vJ^{-C}.
\]

A completion request $D<L$, whether larger or smaller than $J$,
has split charge less than $2LJ^{-C}$. Therefore all completion requests
together contribute at most $2B^vLJ^{-C}$. The new target moment is at
least $T_\tau^v$. The complete normalized paid moment is consequently
at most

\[
\alpha^v+2\gamma^v+2\delta^v,
\quad
\alpha=\frac{P_\tau}{T_\tau},\quad
\gamma=\frac{259998}{18^C T_\tau},\quad
\delta=\frac{11560\cdot19}{18^C T_\tau}.
\]

Two independently implemented exact rational interval engines verify

\[
0<\alpha<1-\frac1{10^{10}},\qquad
0<\gamma<\frac{9991}{10000},\qquad
0<\delta<\frac67.
\]

For orientation, the certified quantities are approximately

```
1-alpha = 0.0000000001880266712457359,
gamma   = 0.99907124299228386731,
delta   = 0.84399113766577138522.
```

The exact rational comparisons

\[
(9991/10000)^{780}<1/2,\qquad (6/7)^5<1/2
\]

provide at least twenty-two decay blocks for both tails. Bernoulli's
inequality gives the exact full bound

\[
\alpha^v+2\gamma^v+2\delta^v
<\frac1{1+17160/10^{10}}+\frac4{2^{22}}
=\frac{262144250000429}{262144449839104}<1.
\]

The certified gap is $199838675/262144449839104$, exceeding
0.0000007623227389. The verifier rejects the unpadded rank-one tail condition
even at the raw minimum target. It also rejects an undamped completion
tail and the inadequate one-block estimate.

Every final paid rank is at most $18^v$, and every target lies between
$19^v$ and $153^v$. Thus the rule has strict rank separation. Its
rank-one surplus remains exactly

\[
260798^v-259998^v>0,
\]

because completion adds equal productive and paid rank and splitting
preserves paid rank.

## 4. Explicit finite uniform compiler

Apply the inherited integer whole-job compiler, attributed in the source
to Jacob Alan Sussman's Theorem 1G. Select

\[
\kappa=0.003001053,\qquad
d=\frac{C-\kappa}{7}=\frac1{7000000000},\qquad
u=\kappa+6d=\frac{21007377}{7000000000}.
\]

Here $u$ is the uniform complex saving. Put

\[
t=1-C,\qquad z=1-u,\qquad z_0=(t+z)/2,
\qquad \Delta=z_0-t=\frac1{14000000000}.
\]

The exact inequality $18^{55}<19^{54}$ bounds the exit exponent by
$54/55$; use $h=1/55$. Retaining the full ambient $281^v$, the bounds
$18<2^5$, $281<2^9$ give

\[
\frac{mE(x)}x<2^{A}x^{-h},\qquad
A=(5+9h)v=88608.
\]

The complement coefficient $\eta=z_0m^{z_0-1}$ satisfies

\[
-\log_2\eta<1+9v(1-z_0)=\frac{32513793811}{70000000}.
\]

The following integers are sufficient:

\[
\begin{aligned}
H_0&=\left\lceil\frac{A\Delta+1+9v(1-z_0)}{h\Delta}\right\rceil
     =357651736794440,\\
H_1&=\left\lfloor\frac{H_0(1-z_0)}{z-z_0}\right\rfloor+1
     =15026650096742881962201,\\
N&=2^{H_1}.
\end{aligned}
\]

`endpoint.py` checks $H_0\ge9v$, the complete exit/complement
inequality, and the final strict power inequality. The last inequality's
gap is exactly $1/14000000000$. Reducing either threshold by one fails
its stated sufficient bound. Strong induction below and above the
threshold gives the admitted uniform saving $u$ at rank $N$.

These are sufficient finite values. The enormous tensor and uniform
programs are specified by finite recipes; they are not materialized and
are not claimed to be practical or minimal.

## 5. Ordinary BIT input and the outer ledger

The ordinary BIT supplier is the separately source-bound six-pair
construction in `bit/BIT-P6-TENSOR.md`. It has thirteen native invocations,
7039 arbitrary input columns, 5707 independent helper owners, and 117
owned-copy episodes. The complete source rational charts are embedded in
the 92-dimensional carrier. Every whole idle and endpoint is regenerated.

Its exact raw profiles are

```
T_BIT = {8:5707, 22:444, 36:444, 50:222, 92:222},
P_BIT = {1:17199, 2:17446, 3:1027, 4:572, 5:1326,
         6:143, 7:1357, 14:444, 28:444, 42:222}.
```

The BIT proof uses tested saving 0.00314, a native tensor power of 6000,
uniform saving 0.003135, and covered saving 0.00313. Its normalized paid
moment is bounded by $1653/1696<1$. All native tensor substitutions
and whole-job matchers precede one delayed global cover, with one common
external weight. Internal queries are not separately lowered to
incompatible covered weights. The inherited two-call ordinary wrapper
has fixed multiplicity.

With atom exponent 0.0032 and the inherited old ordinary saving
$384599/10^{10}$, the exact conversion gives

\[
(1-0.0032)\,0.00313+0.0032\frac{384599}{10^{10}}
=\frac{9750334599}{3125000000000}
=0.00312010707168>0.00312.
\]

The complex outer ledger uses this certified ordinary saving 0.00312 and

\[
b=\kappa+5d,\quad a=\kappa+4d,\quad q=\kappa+3d,
\quad\epsilon=1-d,\quad\beta=1-3d,
\quad r_0=d/10,\quad\mathrm{stop}=\mathrm{layout}=d.
\]

The authenticated outer ledger checks all 54 strict predicates and the
three inherited functional predicates. A fourth functional predicate
binds the actual BIT atom exponent $\delta_{\rm BIT}=0.0032$:

\[
\beta(1-\delta_{\rm BIT})
=\beta\frac{623}{625}
=\frac{622999999733}{625000000000}>0.
\]

The inherited BIT stock predicate uses the old atom $0.003$; retaining
that predicate does not replace this check for the actual supplier.
The new inequality also follows from the BIT certificate's stronger
$\delta_{\rm BIT}<1-a_{\rm ordinary}$ and the outer $\beta>0$.
It is a stock condition for the BIT atom, while copied-query work is
charged by the finite envelope in the next section.

Every strict and functional value is positive. The limiting
main-transform margin above $\kappa$ is exactly

\[
\frac{10489496313}{24500000000000000000}.
\]

Mutation controls reject closed precision/uniform gaps, a final endpoint
equal to the tested raw saving, and an insufficient ordinary BIT premise.

## 6. Full finite costs, owned stock and precision

The raw hybrid scalar invoice is 3500584. It includes the source native
words in two forward and seventeen backward orientations, both literal
controller boundary programs, all scalar bridges and signed swaps, and
64 pointwise real-scalar operations per direct port episode. In
particular it includes initialization, complete-stream copying, read/add,
and release of each of the 1792 owned direct copies.

Movement is charged separately. Each direct episode has an allowance of
eight full-stream movement/control records, covering its two coordinate
routes, inverse translation, and the associated stream operations. Thus
the raw direct contribution is 14336 such records. All 8512 surviving
native contacts, every helper input/output normalizer, endpoint
normalizer, idle route, and whole-job matching route also belong to the
complete movement inventory. They are not absorbed by declaring a
rank-zero operation free.

Use separate owned banks for every suspended native center and every
suspended direct copy. A raw hybrid invocation has 19 native center-bank
episodes and 1792 direct-copy episodes, for 1811 owned-bank episodes. Within
a direct stage the ports can be processed sequentially, but no such
reuse is needed to justify the conservative bound that counts every
episode. A copied stream remains allocated while its recursive request
executes. It is released only after its destination read/add is complete.
Distinct productive helpers retain their independent arbitrary inputs.

After tensor substitution, target completion, disjoint splitting and
uniform compilation, count all actual expanded records. Let $U$ be the
number of raw hybrid instances in that finite recipe, and let $R$ count
all nonrecursive movement/normalization records, including every inherited
and new route. The conservative scalar envelope can use

\[
G=3500584\,U+8R.
\]

Count every complete owned work-bank volume, with separate entries for
nested suspended copies and centers. Let $O$ be their conservative
total in the same complete-stream units used by the inherited closure,
$W$ the final productive width, and $P$ the final paid rank-one leaf
count. Completion and compiler temporaries, if allocated, also enter
$O$; they are not inferred from the raw 1811 figure alone. Substitute
these enlarged fixed counts in the retained envelope

\[
\begin{aligned}
Z&=W+O,\\
E&=64(Z+N+P+G+1)^3,\\
B_{\rm const}&=P+E,\\
C_0&=32N B_{\rm const}^2.
\end{aligned}
\]

All these counts are finite and specified by the complete chronological
recipe. In particular, both monomial boundary factors of every retimed
helper and every new internal transport recipe enter the movement count.
The fixed-template precision, recurrence and eventual absorption
arguments use these new constants. Numerical allowances from the old
small p7 word are not substituted for the expanded program. Coordinate
permutations and unit phases have zero coefficient height but still have
movement and owned-stock costs.

This use of the enlarged constants retains the inherited all-column
physical, fine-prime, analytic, stock, fixed-tape and recovery hypotheses.
The finite scripts certify their explicit arithmetic inputs and the
modified native contracts. The final theorem is conditional on those
written premises.

## 7. Reproduction and source separation

From the repository root run

```sh
python3 -I -O -B research/kappa-hybrid-controller/verify.py
```

The default complex source root is the existing
`research/pr4359-p7-padding/source` export. The default BIT source root is
the repository root. The retained `../fresh-helper-boundary/` package
provides the pinned PR4441 retiming and its complete phase recipes.
Explicit source-root arguments allow independent source preparation.
The verifier authenticates the exact original bytes, regenerates the
retimed local supplier and rational controller, checks the required
physical phases, and uses two independent rational interval engines.

The default command compares the full regenerated receipt with
`RESULT.json`. `--write-result` writes those receipts when deliberately
rebuilding a changed construction. Geometry gzip files are compared by
their canonical uncompressed JSON payload; the original source gzip
files retain their exact byte pins.

The discovery program under `search/` is separate. Its floating scores
found the selected parameters. The positive construction receives exact
certificates; no global optimality or obstruction outside the searched
minimal-cut path family is claimed.
