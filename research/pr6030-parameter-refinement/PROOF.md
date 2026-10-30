# Conditional PR6030 parameter refinement

Prepared with OpenAI Codex assistance, 29 October 2026. Apache-2.0.

This is a parameter corollary of DreamingOfClouds' and Ali Romman's admitted
PR6030 construction. It changes neither the physical word nor its invoice.
The compiler and outer parameter families are inherited, not claimed as new.
The contribution is a source-bound instantiation beyond the selected numerical
claim, together with a proof of the remaining interval of attainable savings.
It is not a new reviewed frontier or a claim of literature-wide priority.

## Theorem

Under the same five framework assumptions as the selected PR6030 result,
integer multiplication on its fixed finite-alphabet multitape model satisfies

\[
T(n)=O\bigl(n(\log n)^{1-\kappa}\bigr)
\quad\text{for every fixed }0<\kappa<C,
\qquad C=\frac{6251623}{2000000000}=0.0031258115.
\]

In particular, the explicit rational choice

\[
\boxed{\kappa=\frac{3125811}{10^9}=0.003125811}
\]

exceeds the selected `781451/250000000 = 0.003125804` by exactly
`7/10^9`. Constants and eventual thresholds may depend on the chosen
\(\kappa\). No uniform big-O constant as \(\kappa\uparrow C\) is asserted.

The five retained assumptions are `native_all_columns`, `owned_erasure`,
`compiler`, `precision_tape`, and `analytic_recovery`; their full statements
are pinned in `vendor/selected-result.json`. The physical construction and
its existing application proof are pinned in `SOURCES.json`.

## 1. The complete source invoice

For a rank histogram \(R\), write \(R_s=\sum_r R(r)r^s\).
The inherited complete target and paid histograms are:

| Rank | Productive multiplicity | Paid multiplicity |
| --- | ---: | ---: |
| 1 | 252 | 41502 |
| 2 | 144 | 8226 |
| 3 | 72 | 8928 |
| 4 | 1926 | 1800 |
| 5 | 252 | 2934 |
| 6 | 36 | 198 |
| 7 | 162 | 108 |
| 8 | 342 | 18 |
| 9 | 6930 | 0 |
| 16, 24, 32, 40, 48, 56, 64 | 0 at each | 416 at each |
| 17, 25, 33, 41, 49, 57, 65 | 416 at each | 0 at each |
| 72 | 0 | 208 |
| 73 | 208 | 0 |
| 145 | 208 | 0 |

They have 13,444 productive fields and 66,834 paid calls. Their rank masses
are 240,912 and 240,152. These counts include all 18 local invocations,
1,560 query calls and 3,120 whole idle jobs. Arbitrary productive helper
inputs occupy distinct fields; owned zero scratch receives no credit.

The finite word, signed native maps, whole-job adapters, routing and physical
caller are exactly those of PR6030. Their source-bound application argument
is `vendor/PROOF-REVIEW.md`. Changing the numerical exponent does not change
any of these finite identities or their attribution.

## 2. Strictification at the new tested exponent

Take \(t=1-C\), \(u=1/7\), \(v=1024\), cutoff base \(c=16\), and completion
floor base \(b_0=17\). Exact rational interval evaluation gives

\[
T_t-P_t>0.000013986416340427664617903659.
\]

Define

\[
\alpha=P_t/T_t,\qquad
\gamma=P_{t+u}/(16^uT_t),\qquad
\delta=13444\cdot17/(16^CT_t).
\]

The enclosures in `CERTIFICATE.json` prove

\[
\begin{aligned}
\alpha&<0.999999999941318152971528074101<1-10^{-12},\\
\gamma&<0.975562352633791143800057186523<125/128,\\
\delta&<0.950628643799561988901683113169<125/128.
\end{aligned}
\]

These are rational bounds, not floating-point decisions. The two pinned
engines independently enclose the target and paid moments. Both use
\(\log x=2\sum_{j\ge0}z^{2j+1}/(2j+1)\), \(z=(x-1)/(x+1)\), after binary
range reduction. The omitted logarithm tail after 80 terms is bounded by
\(2z^{161}/(161(1-z^2))\). Taylor exponential tails are bounded geometrically;
the first engine additionally rounds every intermediate interval outward.
The second computes \(r^{1-C}=r/\exp(C\log r)\) with exact rational fractions.
The checker compares both resulting intervals and rejects a tested exponent
above the pinned crossing.

Here \(t+u\ge1\), as required by the higher-moment theorem. Chronological
tensor substitution, paid completion on each existing owner's disjoint
axes, and integer splitting give normalized paid charge at most

\[
\alpha^v+2\gamma^v+2\delta^v
<\frac1{1+1024\cdot10^{-12}}+\frac4{2^{32}}<1.
\]

For the first term use Bernoulli's inequality on
\((1-10^{-12})^{-v}\); for the other terms use
\((125/128)^{128}<1/16\) and \(v=8\cdot128\).
The last upper bound has the exact positive gap

\[
\frac{97179323}{1048576001073741824}.
\]

Thus completion and splitting are funded, not omitted. The resulting
finite unit has maximum paid rank \(16^{1024}\), minimum productive rank
at least \(17^{1024}\), and ambient rank \(145^{1024}\). The permitted
chronological substitution and disjoint-splitting interfaces are precisely
the retained compiler assumptions; no additional independent inputs or
free adapter operations are introduced.

## 3. Arbitrarily small positive compiler loss

Use logarithm power \(p=1024\) and \(\bar\theta=63/64\).
Exact integers and interval enclosures prove

\[
16^{64}<17^{63},\quad
2(16^{1024})^{64}\le(145^{1024})^{63},\quad
(1-C)145^{-1024C}>(63/64)^{1024},\quad
145^{1024C}<2^{1024}.
\]

Consequently the retained logarithmic-majorant compiler bounds its normalized
rank-one leaf count by \(N^{1-C}(1+\log_2N)^{1024}\).
For any fixed \(d>0\), an integer \(H\) exists with

\[
(H+1)^{1024}<2^{dH}.
\]

At \(N=2^H\) this yields a strict uniform saving \(C-d\).
This is an existence assertion about a finitely specified compiler;
the enormous winning word need not be materialized to specify the algorithm.

For the explicit witness take

\[
d=(C-\kappa)/7=1/14000000000,\qquad
H=707182000000000,\qquad dH=50513.
\]

The checker verifies \((H+1)^{1024}<2^{50513}\) by integer arithmetic.
It also verifies failure of the preceding grid point \(H-d^{-1}\), without
asserting this is the smallest possible carrier under all compiler choices.
The new uniform saving is
\(C-d=\kappa+6d=547017/175000000\).

## 4. Outer transfer and the whole interval of savings

For every \(\kappa\in[0.003125804,C)\), put

\[
\begin{gathered}
d=(C-\kappa)/7,\quad b=\kappa+5d,\quad a=\kappa+4d,
\quad q=\kappa+3d,\\
\epsilon=1-d,\quad\beta=1-3d,\quad
r_0=d/10,\quad\mathrm{stop}=\mathrm{layout}=d.
\end{gathered}
\]

The complex supplier has saving \(\kappa+6d\); the admitted ordinary BIT
saving remains \(17/5000\). The actual ordinary saving is
\(8590884599/2500000000000>17/5000\), with atom exponent \(1/250\).

For this interval, \(0<d<2\cdot10^{-9}\),
\(0<q<a<b<C<0.0034\), and \(\epsilon,\beta>0.99999999\).
The old outer formulas simplify with
\(\xi=29/32+(1-d)q\), so \(0.90625<\xi<0.91\).
The important vanishing slacks are explicitly positive:

\[
\begin{gathered}
a-q=b-a=d,\quad b-q=2d,\quad
(1-d)b-a=d(1-b)>0,\\
\lambda-\tau=\lambda'-\lambda=d/2,\quad
1-\epsilon=d,\quad\epsilon-\beta=2d,\\
1-\epsilon-r_0=9d/10,\quad
1-\beta-2(1-\epsilon)=d.
\end{gathered}
\]

Here \(\sigma=1-b<\tau=1-a\), hence the internal exponent is \(\tau\),
and the leaf exponent is \(1-(1-d)b<\tau\). This proves the remaining
intermediate-exponent orderings. The group guard equals
\(3-2\xi-\beta>0.18\), and subtracting \(r_0\) preserves positivity.
The remaining cap, short-record, halo and fixed-constant conditions follow
directly from the displayed bounds on \(\xi,\epsilon,\beta,a,b\).
The two stock expressions are \(\beta(1-3/1000)\) and
\(\beta(1-1/250)\), both strictly between zero and one.

In the order of the retained nine-row outer ledger, the margins are

\[
\begin{gathered}
\epsilon q,\quad a,\quad d+q\beta,\quad d+a\beta,\quad
1-2d,\quad\epsilon q+d,\\
\epsilon q+13/32+d,\quad 1-d,\quad77+4d.
\end{gathered}
\]

All strictly exceed \(\kappa\). In particular,
\(\epsilon q-\kappa=d(3-\kappa-3d)>0\),
\(d+q\beta-\kappa=d(4-3\kappa-9d)>0\), and
\(d+a\beta-\kappa=d(5-3\kappa-12d)>0\).
All 54 named strict predicates and four functional predicates are also
recomputed separately for the explicit rational witness. Its minimum
outer margin is the main-transform margin, with exact gap

\[
\epsilon q-\kappa=
\frac{41956238643}{196000000000000000000}>0.
\]

The retained fixed-tape/precision and analytic-recovery interfaces therefore
give the claimed multiplication bound. The unchanged physical template
retains all ordinary-work, owned-storage and norm-growth charges. A larger
fixed compiler threshold changes fixed constants and eventual thresholds,
not these strict exponent inequalities. For \(0<\kappa<0.003125804\),
the already selected bound implies the conclusion directly. This proves
the theorem for the entire claimed interval. ∎

## Limits and next questions

The gain is approximately **0.00022394% in exponent saving**. This is a
small parameter improvement, not a practical speedup or a changed supplier.
The published fixed-invoice crossing is in
`(0.00312581155791, 0.00312581155792)`, leaving less than `5.58e-10`
above the explicit witness before any downstream losses. A substantive
improvement needs a changed complete productive/paid profile or a different
interface; this package does not supply one.

An independent reviewer can first replay the certificate and inspect the
cofinal argument in Section 4. A circuit researcher can instead investigate
the unremoved helper-469/471 rungs named by PR6030, with full restoration,
native maps and caller costs. Those physical changes have not been proved here.

Credits: DreamingOfClouds, Ali Romman, Mason Hale, Pierre-Loic Doulcet and the
cumulative P104 contributors; Jacob Alan Sussman's productive recursion,
Cinna Davis's controller, zxv and Cao Yifan's arithmetic/compiler work;
Matarener and Chris R/Clear1nsight's independent verification; and the
retained BIT, analytic and original OpenAI framework authors. The pinned
source notices and application review preserve the detailed lineage.
