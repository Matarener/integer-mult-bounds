# Exact relaxed tail counts at the PR5569 price gate

26 October 2026. This is a paper derivation with finite rational arithmetic
and inherited source-bound intervals. No interval engine, source program,
contact inventory, native map, retiming solver or physical construction was
executed. The frozen single-tail gate is reviewed in
`PRICE-GATE-STATIC-REVIEW.md`. The companion
`STATIC-AGGREGATE-ARITHMETIC.json` contains the exact rational arithmetic;
it is not a newly root-qualified scientific package.

**Decision:** nominate a source-bound, inventory-only aggregate budget
certificate as the next distinct economic artifact. In the explicitly
defined optimistic isolated-tail relaxation, the exact minimum is146
changes per FULL when every permitted controller length is allowed. The
minimum is147 when the literal current18-FULL caller is retained. These
numbers hold at both declared points, C=.0033 and C=.0033000005. They are
minimum counts of ideal algebraic exchanges, not discovered contacts,
independent physical opportunities or a construction reaching the goal.

This economic scope is separate from Ali Romman's active Discussion5574
event-frame/event-order construction. The sole curator checked the bounded
overlap evidence and found no existing claimed aggregate isolated-tail-count
theorem or stronger completed bill. That is not a novelty certificate.
No author's source inventory is searched or reserved here. All physical
owned-scratch nominations remain held.

The curator subsequently identified additional active Ali Romman scopes:
Discussion5575 owned-scratch cancellation/retirement,5576 the fixed-scalar
all-holder/COPY-return screen, and the5125 changed-input/private-COPY
completion comment. Their source rows, lifetimes, COPY rewrites and
candidate enumeration are also excluded from this economic artifact. The
aggregate histogram theorem remains distinct in that bounded overlap read.

## Fixed sources and precise relaxation

Fix PR5569 head `af9f091ac6f30c6eaacb9c27777bfbe2d0e5ffdf` and the exact
local paid/independent-helper inventories recounted by the frozen gate:

```
P = {1:2211, 2:458, 3:496, 4:93, 5:164, 6:18, 7:14}
H = {4:83, 5:5, 8:15, 9:424}.
```

There are3454 local paid jobs and527 independent helper targets. Local
rank masses are6013 and4293. The controller retains104 ports, rank8 blocks,
the104-query tariff and the same prefix/suffix whole-idle law. Its relaxed
per-FULL deficit B(C) is inherited from the authenticated root result,
SHA256 `6ad37711165765c2f4f3fb9690e78b3db8b1fb6e8b91ff883b2f1286129f8335`.
PR5554's all-controller reduction is an explicit analytic premise.

One permitted exchange takes **one distinct old helper target** of rank r
and **one distinct old terminal paid job** of rank c, with

```
1 <= k <= min(c,r-1),    c <= r <= 9,
paid:   H_c -> H_(c-k),
target: H_r -> H_(r-k).
```

Rank-zero paid terms are omitted. The helper target stays positive. This
is the rank form of one shortened nested monotone tail; it includes the
lost productive credit. The relaxation freely matches eligible paid and
target inventory, grants any required current/nested frames, ignores all
chronology and compatibility, and charges zero for extra holder transport,
cleanup and restoration. These favorable grants make an upper bound useful
even if no legal corresponding contacts exist.

Each initial paid job and helper target may be used at most once. The
complete gain is the sum of the declared exchange gains minus nonnegative
extra debits. There are no new independent targets, extra paid fusions,
changed starts/intermediate paths, shared gains beyond that sum, recycling
of a changed target into a second exchange, or altered controller tariff.
Those mechanisms are outside the theorem. Granting zero restoration does
not claim that actual restoration is free.

## Maximum gain of one exchange

Put `H_j=j^(1-C)` and `H_0=0`, for0<C<1. One exchange gains

```
G(c,k,r)=H_c-H_(c-k)-H_r+H_(r-k).
```

For fixed k,r, concavity makes the increment `H_c-H_(c-k)` decrease as
c increases through c>=k. Thus

```
G(c,k,r) <= H_k+H_(r-k)-H_r.
```

The right side is largest at the balanced integer split, by concavity:

```
g_r(C) = H_floor(r/2)+H_ceil(r/2)-H_r.
```

The inequality is attained in the relaxed invoice by c=k and a balanced k.
It is not a claim that any literal terminal job has that attachment.

The balanced gain increases strictly with integer r>=1. For r=2m, the
difference g_(2m+1)-g_(2m) is
`(H_(m+1)-H_m)-(H_(2m+1)-H_(2m))>0`. For the next step it is
`(H_(m+1)-H_m)-(H_(2m+2)-H_(2m+1))>0`. Both follow from decreasing unit
increments; g1=0 begins the sequence. Consequently every allowed change
has gain at most

```
g9(C)=H4+H5-H9.
```

Any set of at most m exchanges in this class therefore gains at most m*g9,
before nonnegative debits. This bound does not assume the source contacts
exist or are compatible. It bounds the optimistic additive class itself.

## Rational bounds without another price-engine evaluation

The earlier qualified pooled-ceiling certificate supplies

```
.6931 < log2 < .6932,
1.0986 < log3 < 1.0987,
1.6094 < log5 < 1.6095.
```

Its finite rational log proof and frozen result are retained in
`../ceiling-qualification/`. These brackets are inherited numerical
premises here; no logarithm/exponential routine was run again.

For g=g9, g(0)=0 and

```
g'(0)=18 log3-8 log2-5 log5,
6.1817 < g'(0) < 6.1848.

g''(C)=4^(1-C)(log4)^2 +5^(1-C)(log5)^2
        -9^(1-C)(log9)^2.
```

Let l_r,u_r be the resulting log brackets at r=4,5,9 and let Cmax=.0034.
The elementary bounds `1-Cmax*u_r <= exp(-C log r) <= 1` give

```
g''(C) > 4(1-Cmax*u4)l4^2 +5(1-Cmax*u5)l5^2 -9u9^2
       = -22.9271590819903576 > -23,

g''(C) < 4u4^2 +5u5^2 -9(1-Cmax*u9)l9^2
       = -22.4837036154557504 < -22,
```

throughout0<=C<=.0034. All displayed decimal bounds are terminating
rationals obtained from those bracket endpoints. The lower linear factor
is positive on this domain. Integrating twice gives the strict bounds

```
g_lower(C) = 6.1817*C - (23/2)*C^2 < g9(C),
g9(C) < g_upper(C) = 6.1848*C - 11*C^2.
```

The resulting exact comparisons are:

| C | 145*g_upper | Inherited B(C), approximately | 146*g_lower |
| --- | ---: | ---: | ---: |
| .0033 | 2.94205725 | 2.9541456904615055784708 | 2.96005875 |
| .0033000005 | 2.94205769313449960125 | 2.9541524365283036465707 | 2.96005919572339958025 |

The comparisons use the actual rational outward endpoints in the frozen
receipt, not the approximate middle column. In both rows,

```
145*g9 < 145*g_upper < B_lower <= B <= B_upper
        < 146*g_lower < 146*g9.
```

Thus145 or fewer permitted changes fail the necessary all-controller raw
gate. The following146-exchange multiset realizes the upper envelope in
the inventory relaxation.

## Optimistic146-exchange invoice and all-controller minimum

Use93 of the93 available paid rank4 jobs and53 of the164 rank5 jobs. Match
them to146 of the424 rank9 targets, granting free attachments:

```
93 times: paid H4 -> 0, target H9 -> H5,
53 times: paid H5 -> 0, target H9 -> H4.
```

Every exchange gains g9. Nothing is overdrawn, no target is reused and no
new independent target is added. The resulting local inventories are

```
P146 = {1:2211, 2:458, 3:496, 5:111, 6:18, 7:14},
H146 = {4:136, 5:98, 8:15, 9:278}.
```

Paid count3308, helper count527, rank masses5376 and3656 give the same
local rank debt1720. The entire paid-minus-helper change is `-146*g9`.
This is a feasible histogram with freely assigned terminal attachments,
not a feasible source program.

For every compatible local debt L, `E_n=nL+104*c_n` in the source
architecture. Hence the change L -> L-146*g9 shifts every ratio E_n/n by
the same amount, and cancels from every J_n. The frozen J16/J17 signs
therefore retain n17 as the unique ratio minimizer. Since B-146*g9<0,
the relaxed n17 invoice passes the raw moment test at both declared points.
The n17 complete invoice has60604 paid jobs,12079 productive fields and
rank surplus712; it contains17 copies of the new local word,14 query and
14 whole-idle stages, and30 main banks.

Combining the upper bound for at most145 changes with this feasible146
histogram proves **146 is the exact minimum in the stated all-controller
invoice relaxation**. It does not prove the existence of an actual17-call
caller using those edits. The complete scalar, frame, native, ownership,
normalizer, ordinary, precision and compiler obligations remain open.

## The current18-call caller requires147 in this same relaxation

The146 result must not silently replace the physical current18-call caller
by a17-call invoice. The frozen J17 gives an exact way to assess n18
without another engine:

```
B18(C)=E18(C)/18 = B(C)+J17(C)/(17*18).
```

At C=.0033 this is about2.968145184409407574647. At C=.0033000005 it is
about2.968151983247484310071. Rational use of the inherited J and B
endpoints proves, at both points,

```
146*g_upper < B18_lower <= B18 <= B18_upper < 147*g_lower.
```

The optimistic147 multiset takes93 paid H4 and54 paid H5 jobs, with93
targets H9->H5 and54 targets H9->H4. It has local paid3307, helpers527,
rank masses5371/3651 and unchanged debt1720. The full18-call invoice has
64206 paid jobs,12814 targets and surplus760. Accordingly147 is the exact
relaxed minimum when the present18-FULL controller is kept. This again
establishes no literal attachment or compatible event edits.

Even the minimum-count witnesses have little spare recursive budget.
At C=.0033 the146/n17 complete raw surplus is enclosed by the coarse
rational derivation between .10052201215 and .13942736216; the147/n18
surplus is between .21938293063 and .26085898064. The second declared
point has similarly smaller positive intervals. Therefore one additional
uncompensated **global** H1 charge already defeats either of these specific
minimum-count witnesses. A cost split must be priced by its actual signed
delta, not automatically rounded to H1. Ordinary scalar/route costs remain
separate finite funding obligations even when no recursive job is added.

## Next discriminator and required source packet

The immediate distinct artifact can be a small exact certificate checking
the inherited log/B/J pins, the derivative brackets, the145/146 and146/147
inequalities, both complete optimistic invoices, and no-double-credit
inventory arithmetic. It requires no new engine or native replay. Root
may prepare and freeze that bounded qualification after independent review;
the present paper is not an instruction to execute it automatically.

For a physical proposal in this class, the smallest useful packet is now
an **aggregate source budget**, supplied by the owner or following a newly
established nonoverlapping scope. One attractive contact is insufficient
for the stated goal. Before full construction it must contain:

1. The exact current word/caller pins and the chosen controller count.
   A17-call proposal must supply its changed physical caller and complete
   nonlocal bill; an18-call proposal keeps the literal caller and faces the
   higher147 minimum.
2. Distinct candidate helper IDs and distinct old terminal paid-MOVE event
   IDs. For each: literal initial/current/old/new frame bytes, ranks r,c,k,
   owned/public direction, exact target alias and all affected intervals.
   These fields must justify that every advertised saving is one permitted
   isolated tail. An abstract rank4 or rank5 inventory entry is not a
   terminal attachment.
3. The protected-read/owned-lifetime/cancellation packet for each affected
   connected component, including every holder of each independent input,
   scratch INIT/CLEAR and exact source erase contract. Give shared-event
   ownership once, compatibility between changes and the complete jointly
   changed chronology. Separate source-author proof from independent checks.
4. One complete signed paid/target delta and its ordinary-work bill,
   including all holder acquisition, re-flagging, cleanup, restoration and
   endpoint normalizers. No target or removed paid job may be credited
   twice; no scalar span or shared scratch state becomes an independent
   productive target.

The first discriminating check on such an owner-supplied packet is an
optimistic sum of its actual rank-specific rewards. If fewer than146
distinct eligible one-tail exchanges are available over all controllers,
or fewer than147 with the current caller, this isolated class fails
before construction. Even meeting those counts is only necessary: sum the
actual rewards and subtract all debits, then compare against B or B18.
Use actual r,c,k rather than assigning g9 to every helper. If compatibility
or costs are missing, retain an upper bound and hold physical admission.

No such source packet currently exists in our intake. In particular2832
parent-word skipped points supply neither this count nor these identities.
No list of146 contacts has been requested or generated here. Do not start
an event-retiming, event-order or scratch-inventory scan inside the active
Discussion5574 scope. The sole curator owns subsequent ownership/source
refresh; expiration alone is not release.

The same hold applies to the subsequently identified5575/5576/5125 scopes.
Nothing in the optimistic count theorem dispatches a search of their rows,
lifetimes, private COPY programs or omitted points.

## Limits and credit

The result is at two exact points and under a fixed isolated-tail language.
It is not a general P104 ceiling, a count lower bound on arbitrary native
algorithms, a global larger-C theorem, a funded saving, or evidence that
minimal histogram witnesses can pay all compiler/outer losses. Several
tails with nonadditive shared gains, new targets, other paid-path exchanges,
or a changed controller contract require a different complete invoice.

Credit zxv/PR5554 for the all-controller net-debt frontier; GamingPuzzled's
PR5472/5569 for the successor handoff and re-flagging costs; DreamingOfClouds
for5561/5553 and tooling; thu-nmrc for5551; Ali Romman and the P104 lineage;
Clear1nsight's caller/native and exact-price audits; Matarener's endpoint
contract audit; and all retained native/compiler/precision predecessors.
Balanced concavity is elementary, not a claimed new theorem. The present
contribution is its exact source-bound aggregate budget and minimum count,
prepared with OpenAI Codex assistance.
