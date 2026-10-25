# Route 1: a sharp conditional budget and a separate favorable candidate

The new PR #3609 full dual does not yet reopen the stopped P104 supplier.
Under the named paired-chain coverage law, **425 integer rank deletions per
dual remain insufficient for every pair count**. A hypothetical deletion of
426 rank-one children passes the optimistic moment at seven pairs, but leaves
less than 4.558 units of additional normalized cost. No such deletion network,
compatible owner map, or complete P104 caller is constructed here.

There is a more developed, separate Route 1 candidate: PR #3605's T740
construction. This audit independently verifies its stated complete histogram
and strict rational moment bracket at its updated exact head. It does not
rerun or replace that predecessor's finite native/owner release or inherited
physical, recursive, and analytic hypotheses.

## 1. Frozen profiles and the actual coverage contract

The inputs are the PR #2458 forward profile recounted in PR #2744, and the
changed full dual in PR #3609's executed receipt. They are not the original
native-channel profile or a partial omitted-bank replacement.

| Rank | Forward F | Changed full dual D |
| ---: | ---: | ---: |
| 1 | 1216 | 1316 |
| 2 | 74 | 61 |
| 3 | 86 | 74 |
| 4 | 104 | 86 |
| 5 | 48 | 33 |
| 6 | 42 | 25 |
| 7 | 68 | 46 |
| 8 | 8 | 8 |
| 9 | 0 | 93 |
| Calls | 1646 | 1742 |
| Rank mass | 3070 | 3542 |

Use Nick Petalas's existing all-pair coverage model, derived from Jose Manuel
(`jmbarrancoml`)'s four-pair calculation and the retained larger-gain template.
For an integer $p\ge1$, there are $p+1$ forward calls and $p$ dual calls,
width $m=16p+9$, and $W=208p$ original families. Each family has one unpaid
coordinate. Grant the full persistent endpoint progress $P=3014$ to every
call, even after hypothetical deletion, and grant the missing forward
corrections and all unspecified implementation costs free. With $B\ge0$
fully paid banks, the optimistic remaining rank mass is

$$
I_B=\max(0,(m-1)W+mB-(2p+1)P).
$$

All residual children are optimistically allowed rank $m$. This is a
conditional coverage model, not a construction of its owner windows or a
proof that those endpoint credits can be retained after changing the words.
PR #3609 changes the dual histogram, not this coverage law. The new source is
`13f974dae4af66027afb01f3ab42df9e830c2e90`; the main-branch predecessor inputs
are frozen at `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

## 2. What a real replacement must establish

Let $D'$ be an actual proposed replacement profile. Let $\Delta\ge0$ be
**genuinely unpaid** additional coverage relief, and let $G(a)\ge0$ be every
additional charge expressed in the same normalized rank-moment units.
Native children already included in $D'$ must not also be charged in $G$.
Conversely, omitted scalar, owner, routing, restoration, precision, or
controller costs must not silently be set to zero in a claim of a complete
bill. The model's exact test is

$$
m^a\sum_r[(p+1)F_r+pD'_r]r^{1-a}
+\max(0,J_B-\Delta)+G(a)<m(W+B),
\qquad J_B=(m-1)W+mB-(2p+1)P.
$$

This formula also covers arbitrary resynthesis: use its actual profile,
without pretending it consists of deletions from $D$. If $E_{\rm old}$ is the
old excess numerator, define the **net** native saving

$$
T=m^ap\sum_r(D_r-D'_r)r^{1-a},\qquad
R_\Delta=\max(0,J_B)-\max(0,J_B-\Delta).
$$

The exact criterion is $T+R_\Delta>E_{\rm old}+G$, with
$0\le R_\Delta\le\Delta$. A changed coverage law must justify its new $J_B$;
it cannot be inserted into an unchanged calculator without that proof.
For example, added positive children of total rank mass $A$ cost at least
$A$, since $r(m/r)^a\ge r$. If they earn at most $A$ units of extra progress,
that progress alone cannot yield a net budget gain. Likewise, for $p\ge2$
the term $mB$ from fully paid banks cancels between residual work and capacity;
the sign of the excess is unchanged. These statements explain why a profile
saving, a free endpoint credit, and a paid physical replacement are different
obligations.

## 3. A sharp integer deletion allowance across all pair counts

Suppose each dual's inherited positive children of integer ranks $r_j$ are
changed only to ranks $r_j-\delta_j$, with integer
$0\le\delta_j\le r_j$ and $\sum_j\delta_j\le d$. For $0<a<1$,

$$
r^{1-a}-(r-\delta)^{1-a}\le\delta.
$$

Indeed, the successive unit increments of the concave function $x^{1-a}$
decrease and the first increment is one. Therefore deleting $d$ rank-one
children gives at least the native saving of any such deletion of $d$ rank
units. This comparison, including whole-child deletions, is inherited from
Jose Manuel's discount argument. It does not cover arbitrary replacement
networks, which must use Section 2.

Put $D_d=D-dH_1$ and, for a fixed $a$, define

$$
V=\sum_rF_rr^{1-a},\qquad
U_d=\sum_r(F_r+D_{d,r})r^{1-a}.
$$

Using the unclamped residual, the excess is

$$
E_d(p,a)=(16p+9)^a(pU_d+V)-6236p-3014.
$$

Clamping can only increase this lower bound. In particular, at $p=1$ the
zero-bank clamp adds 4050, so a negative signed residual is never counted as
actual negative work. All $mB$ terms cancel in this lower bound.

The useful new step is strict convexity in the *real* variable $p\ge1$:

$$
\frac{\partial^2 E_d}{\partial p^2}
=16a(16p+9)^{a-2}
\left[(16(1+a)p+18)U_d-16(1-a)V\right]>0.
$$

For the cases here $U_d>V>0$, so the bracket is positive. Consequently three
strict comparisons at the neighboring integers 6, 7, and 8 suffice to locate
the global integer minimum; no unbounded enumeration or sampled tail is used.

Take the favorable test saving
$a=\kappa=836330098538459/500000000000000000$. Independent outward rational
intervals certify:

| p | Strict rational decimal enclosure for E425(p, κ) |
| ---: | --- |
| 6 | $(2.62322106,\ 2.62322107)$ |
| 7 | $(1.60068641,\ 1.60068642)$ |
| 8 | $(1.97354361,\ 1.97354362)$ |

Thus $E_{425}(7)<E_{425}(6),E_{425}(8)$ and $E_{425}(7)>0$. Convexity proves
rejection for every integer $p\ge1$, every finite fully paid $B$, and every
deletion allowance $d\le425$. Since every child moment increases with $a$,
the rejection also holds at the stricter required primitive saving.

The integer boundary is sharp **within this relaxation**. At $p=7$, delete
426 actual histogram entries of rank one, leaving $D_{426,1}=890$.
At the stronger rational test $a=1/596$,

$$
-4.55707137<E_{426}(7,1/596)<-4.55707136.
$$

This saving exceeds the selected primitive test and satisfies
$a/(1+a)=1/597>\kappa$. Four additional normalized cost units still pass;
five already fail. Thus the abstract profile's total extra-cost allowance is
only $4.557071360876949\ldots$, across the entire seven-pair bill. At fixed
$p=4$, 427 deletions fail at $\kappa$ while 428 pass at $1/596$.
Varying the pair count saves two units in this optimistic target; it does not
supply a compatible deletion or make the previous 416-unit gift sufficient.

## 4. The favorable named alternative uses its own bill

Ross Richardson's updated PR #3605 head is
`3efbb5de06a49ffeea6684482f2d3fe48cdca3fb`. Its complete stated T740 profile,
including the rank-six stratum, is independently reconstructed as
$H=6660L+I$ from the pinned derivation and compared with both pinned JSON
claims. It has 23,953,011 children and rank mass 48,165,120, against
$73\cdot663040=48,401,920$ capacity. Its distinct moment is

$$
M(b)=\frac{\sum_r rH_r(73/r)^b}{73\cdot663040}.
$$

The checker independently proves $M(C)<1<M(D)$ for the adjacent rationals

$$
C=0.001730006549538841847005,\qquad
D=0.001730006549538841847006.
$$

The certified margins are approximately $1-M(C)=2.4237\cdot10^{-24}$ and
$M(D)-1=4.1334\cdot10^{-25}$. All ranks are below 73, proving strict
monotonicity and a unique crossing. One additional unpaid rank-one child
already rejects at $C$. At $\kappa/(1-\kappa)$ the stated profile gives
$0.9998452720273953\ldots<1$. The displayed outer endpoint
$C-10^{-46}-10^{-70}$ also agrees arithmetically with its claim; the modern
outer implication is inherited, not reproved by this check.

This is stronger evidence of a Route 1 opportunity than an unrealized P104
deletion: a named candidate already publishes a complete finite source,
native, owner, physical-prefix and outer release. Our result authenticates
its four quoted files and checks only their arithmetic. We did not rerun the
1,138-second predecessor release, the new wrapper's unrun full tail, the
owner/native/physical checks, or its inherited all-size/compiler, common-label,
mutable-source, whole-call hosting, recursive precision/tape/recovery,
analytic and BIT H1–H5 assumptions. Its T740 histogram is not transplanted into
the P104 coverage law, and its claimed endpoint does not update the selected
frontier. Review of that named complete release is the most developed Route 1
next step visible in this bounded audit.

## 5. Comparison, reproducibility, and credit

PR #3574 (`eb11cd484c23990c250bdc67ae61829ebae35536`, jwr with Cursor) already
computes a different 1126/1127 hosting threshold. Its native-channel profile
has mass 2368, its 208 unit-step helpers add 1872, and its ideal rank-51 idle
mass is 2472 under $W=832/9$. Each extra rank-one hosting unit **displaces**
one unit of that idle mass. Independent arithmetic here reproduces the
moments $0.9999997022411797\ldots<1$ at 1126 and
$1.0000006822219608\ldots>1$ at 1127. Those are different provider, coverage,
and displacement assumptions; 1126 is not a free additional-work allowance
for the new full P104 words. Its matching, optimizer, and physical obligations
are not replayed here.

Run `python3 -I -B budget.py` or `python3 -I -O -B budget.py` in this directory.
Both authenticate `SOURCES.json`, all eleven exact source files, and the
typed deterministic receipt. The interval engine imports no predecessor
executable: it range-reduces logarithms to $[1,2]$, uses 48 positive atanh
terms with a geometric tail bound, and encloses exponentials with 20 positive
Taylor terms and their geometric tail. All sign decisions use rational
arithmetic. The source and receipt control evidence is kept separately from
the scientific receipt; no historical native suite is rerun.

The new contribution is the changed-profile all-pair convex threshold, its
explicit replacement-cost boundary, and an independent arithmetic comparison
of the two named alternatives. Credit Jose Manuel for the original four-pair
screen and deletion inequality; Nick Petalas for the previous all-pair and
endpoint-geometric budgets; Vasek (`flyingviper`) for PR #2744; Ross Richardson
and the retained PR #2458/PR #3133 lineage; PR #3609's exact full-word
replacement and all its notices; jwr for PR #3574; and Ross Richardson's
updated PR #3605 release. The latter retains dcharb78's PR #3133, Jeremy
Diviney's PR #3148 owner geometry, PR #3531's modern transfer, dataisfire's
bootstrap, Yiyang Lu's staged kernel/flow, and their full source notices.
This bounded audit was prepared by Clear1nsight with OpenAI assistance.
