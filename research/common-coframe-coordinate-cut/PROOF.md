# Exact scope and proof

## 1. The allowed coframes and the source graph

Use the complete forward and backward programs in the pinned
`research/native-center-free-code/CODED-WORDS.json.gz`. They contain 112 main
pairs, 408 independent helpers and the cleared owned centre. Both programs have
the same unordered multiset of proper and warp transitions. The graph has 1002
used original frame vertices.

Let Q be the central Gaussian and D the Gaussian on eight separate coordinate
axes. Let R=DQ. Give each original frame f an arbitrary coordinate mask S_f in
these nine axes. Its new coframe is the product of the selected positive
one-axis Gaussians. No constraint requires the new mask size to equal the old
frame dimension. This enlarges the dimension-only class in PR5687.

Fix ground to I, full to R, every main SOURCE input line to Q, and every main
receiver output hyperplane to D. The other main boundaries are ground or full.
These are the common main boundaries needed by the cited ordinary decoder.
Each scalar contact keeps one coframe for all operands because it retains its
original frame label. The owner code and its inverse are ordinary at the
common main boundaries. Grant their full correctness and zero extra cost for
this negative price test.

Assign every native logical generator the identity. A proper transition from
f to g then has physical map H_g H_f^-1. In this coordinate class its Gaussian
rank is |S_f symmetric-difference S_g|. Count that rank at every actual source
occurrence. For greater freedom, also allow H_f and H_g to differ at a native
warp, and charge the same transport rank there. Thus no equality constraint
on a warp can make the lower bound too large. A zero-rank transition has no
positive recursive charge. Every original helper i has target rank
|S_start(i) symmetric-difference S_final(i)|. Zero-rank helpers remain separate
identity outputs; they are not cleared or credited as positive targets.

This is a price model for a specified source specialization. The physical
source identity, ordinary decoder, precision and machine costs are not newly
admitted here. An invalid or more expensive decoder cannot improve this price
relaxation. A new scalar graph, non-coordinate coframes or coframes chosen
separately for each occurrence lie outside the model.

## 2. An exact minimum of 2464

For each coordinate axis, let x_f be its membership bit in S_f. Its contribution
to paid rank mass minus helper rank mass is

```
E(x) = sum_paid-occurrences |x_f-x_g|
       - sum_independent-helpers |x_start-x_final|.
```

The nine axes separate at rank mass. The eight private axes have identical
boundary bits. The central axis has a different boundary pattern. It is enough
to solve these two binary problems.

After fixing main boundaries, every negative helper edge has a fixed endpoint
except the pairs (114,285) and (115,284), with their actual multiplicities.
Branch on x_114 and x_115. Each of the four choices converts all negative
terms into constants or unary terms. Positive pair terms remain ordinary cut
edges. A unary term b x becomes a source edge of capacity b when b is
nonnegative. When b is negative, it becomes a sink edge of capacity -b and
constant b. An undirected positive edge of weight w becomes two directed
arcs of capacity w. Assign bit zero to the source side of a cut.

The verifier reconstructs this network from every source occurrence and helper
endpoint. For each branch, the retained integral flow satisfies all capacities
and conservation equations. Its value equals the capacity of its retained cut.
Weak flow/cut duality proves that the cut is a global minimum for that branch.
This does not depend on the discovery optimizer.

All four private-axis branches have minimum **224**. All four central-axis
branches have minimum **672**. Therefore every allowed nine-axis assignment
satisfies

```
P(1)-T(1) >= 8*224+672 = 2464.
```

Choose the branch-(0,0) minimum on each axis. Direct evaluation of every
source event in both orientations gives

```
P = 796 H1 + 348 H8 + 281 H9,
T = 405 H9 + 3 H0.
```

Its rank difference is 6109-3645=2464. Every original native warp has equal
endpoint masks in this assignment. Thus the same minimum is attained in the
smaller class that keeps all warps ordinary.

## 3. A uniform local moment bound

Write t=1-C with 0<=C<=1/100. P(t) and T(t) omit rank-zero jobs. Every positive
paid and helper rank is at most nine. There are only 408 helpers, so T(1)<=3672.
For each positive rank r,

```
r^(1-C) >= 9^(-C) r,        r^(1-C) <= r.
```

Consequently

```
P(t)-T(t)
  >= 9^(-C)[P(1)-T(1)] - [1-9^(-C)]T(1)
  >= 2464 - C log(9)(2464+3672).
```

Here exp(-z)>=1-z. The positive Taylor sum through degree 18 proves
exp(11/5)>9, so log(9)<11/5. The verifier checks that rational sum. Throughout
the stated interval,

```
P(t)-T(t) >= 2464 - (1/100)(11/5)(6136)
           = 291126/125 = 2329.008.
```

This bound covers all allowed assignments, including different assignments in
different native calls. It does not assert that the attaining rank-mass
assignment also minimizes every positive-exponent objective.

## 4. Every size of the declared query-thinned caller loses

Take p>=1, v=112 ports, N=p+2 native FULL calls, p-1 thin central query banks,
and any split of the IDLE histories into a prefix and a suffix. The standard
caller has one paired main output of rank 8N+1. Each of its other p-1 paired
main outputs has rank 8k+1 and is matched to one paid paired IDLE of rank 8k.
Each pair contains 2v fields. The thin queries cost v(p-1) rank-one jobs.

These are the stated controller inventories. No arbitrary new controller is
included in this theorem. For 0<t<=1,

```
(8k+1)^t-(8k)^t <= 1,       (8N+1)^t <= 8N+1.
```

Thus the main target moment, less IDLE and thin-query costs, is at most

```
2v[(p-1)+(8N+1)]-v(p-1) = 1904N-112.
```

Subtract the N complete native paid-minus-helper moments from Section 3. The
full signed moment is at most

```
1904N-112-(291126/125)N = -(53126/125)N-112 < 0.
```

This holds for every p and prefix split and every 0<=C<=1/100. Strict reserves
or additional ordinary charges only worsen it. At C=0 the sharper exact
rank-mass bound is

```
main rank - IDLE rank - thin rank - 2464N = -560p-1232.
```

It equals -10192 at p=16. The verifier checks the finite inventory identity for
all 1<=p<=100 and every split as a control; the displayed algebra proves it for
all p. No finite census is substituted for that proof.

## 5. Limits

This excludes coordinate common-main coframes on the fixed centre-free source
in the stated standard caller, over the stated saving interval. It does not
exclude non-coordinate Clifford coframes, changed native/scalar words, different
controller inventories, productive coupled outputs, or other constructions.
It does not bound the best possible kappa. The selected result is unchanged.
