# Exact tariffs for consecutive queries sharing a detour

For consecutive queries that partition a geodesic helper target, a common
detour of any finite length has an exact tariff optimum at an existing internal
query endpoint. Extra charts cannot improve it. This holds for every
nondecreasing concave tariff with value zero at zero, in any metric or
pseudometric space. It answers a restricted part of Open next question 2 in
[Ali Romman's PR #5779](https://github.com/CrocSwap/integer-mult-bounds/pull/5779).

The result is a **scoped mathematical proof with finite corroboration**.
It does not supply physical independent targets, dirty-state restoration,
a shared correction, a new kappa or a complete multiplication theorem.

## Contract and result

Let `C_0,...,C_k`, with `k >= 2`, be metric charts on a geodesic in that order.
Put `s_0=0`, `q_i=d(C_{i-1},C_i)>0`, `s_i=sum_{a=1}^i q_a`, and `t=s_k`.
The geodesic hypothesis means

```
d(C_i,C_j) = |s_i-s_j|  for every i,j.
```

Let `phi:[0,infinity) -> [0,infinity)` be nondecreasing and concave, with
`phi(0)=0`. The old invoice has one productive target `C_0 -> C_k` and the
`k` paid queries `C_{i-1} -> C_i`.

Choose a nonempty finite sequence `F_1,...,F_m`. The new productive target
chain is `C_0,F_1,...,F_m,C_k`. Each of the `k` paid queries is replaced by
`C_{i-1},F_1,...,F_m,C_i`. Each occurrence of an edge is charged, including
repeated edges across different query replacements. Productive edges are
credits and paid edges are debits. Define the gain as new minus old signed
credit. This is a declared tariff relaxation; realizability is not assumed.

Write

```
M = min_{1 <= j < k} sum_{i=1}^{k-1} phi(|s_i-s_j|).
```

**Theorem.** The maximum gain over every such path, including all ambient
charts and all finite lengths, is exactly

```
G_max = sum_{i=1}^k phi(q_i) - phi(t) - 2 M.
```

It is attained with `m=1` and `F_1=C_j` for a minimizing internal endpoint.
If a fixed length `m>1` is required, repeat that endpoint at every position.
Repeated charts have zero distance. The theorem asserts attainment, not
uniqueness. Flat tariffs can have other maximizing paths.

For `k=2`, `M=0`. For `k=3`, `M=phi(q_2)`, so the exact formula is
`phi(q_1)+phi(q_2)+phi(q_3)-phi(t)-2phi(q_2)`.

## Proof

For any chart F, put `S(F)=sum_{i=1}^{k-1} phi(d(C_i,F))`.
Literal cancellation of the first and last boundary edges gives

```
G = sum_i phi(q_i) - phi(t) - S(F_1) - S(F_m)
    - (k-1) sum_{a=1}^{m-1} phi(d(F_a,F_{a+1})).                 (1)
```

The common interior edges receive one productive credit and `k` paid debits,
hence their coefficient is `-(k-1)`. In particular, they do not cancel as in
the single-query contract. For `m=1`, the final sum is empty and the two
boundary sums refer to the same chart.

We prove `S(F) >= M`. Set `r_i=d(C_i,F)` for the internal endpoints. The
triangle inequality gives `|s_i-s_j| <= r_i+r_j`. Therefore the real intervals
`[s_i-r_i,s_i+r_i]` intersect pairwise. Finitely many intervals on the real
line have a common point: their largest left endpoint is at most their
smallest right endpoint. This common intersection also meets
`[s_1,s_{k-1}]`, since each interval contains its own center in that segment.
Choose x in both intersections. Then `|x-s_i| <= r_i` for every i, so

```
S(F) >= sum_i phi(|x-s_i|).                                  (2)
```

Between consecutive internal endpoint positions, every absolute value is an
affine function of x with constant sign. The sum on the right of (2) is
concave on each such segment. A concave function has a minimum at one of
the segment's endpoints. Consequently its global minimum on
`[s_1,s_{k-1}]` is M. A single internal endpoint is the trivial one-point
case. Thus `S(F) >= M` for every ambient chart, including charts outside
the original geodesic.

All costs in the final sum of (1) are nonnegative. Substitution proves the
upper bound. The constant path at a minimizing `C_j` has `S(F_1)=S(F_m)=M`
and all interior costs zero. It attains the bound. This proves the theorem
for arbitrary finite path length and arbitrary ambient dimension.

The interval argument and concave minimization are elementary classical
facts. The contribution here is their application to the changed multi-query
invoice and its exact optimum, not priority for those general facts.

## Consequence at rank at most nine

Suppose all `q_i` are positive integers, `t<=9`, `k>=3`, and
`phi(r)=r^(1-C)` with `0<C<=1/100`. Then **every common detour has gain
strictly less than `-9/5`** in unnormalized rank-one tariff units.

There are at least two distinct internal endpoints. At any minimizing
endpoint at least one other endpoint has integer distance at least one,
so `M>=1`. Write `p=1-C`. Since `q_i^p<=q_i`, the theorem gives

```
G <= t-t^p-2 <= 9-9^p-2 <= 9-9^(99/100)-2 < -9/5.
```

The middle inequality follows because `r-r^p` increases for `r>=1`.
The last inequality is the exact integer comparison
`44^100 < 9^99 * 5^100`. The verifier checks it directly.
Thus this particular multi-query path contract cannot fund an improvement
in the positive integer rank-nine domain through saving .01. No statement
about other query graphs, unchanged source calls or different target credits
follows from this calculation. This package does not inventory the actual
queries of any supplier or claim that a specific caller satisfies the contract.

The rank restriction matters. At `phi(r)=sqrt(r)` and query lengths `(9,1,9)`,
the optimum is `5-sqrt(19)>0`. The verifier encloses this positive value using
integer square roots. Nongeodesic endpoints also matter: three leaves of a
unit-edge star have linear distance sum four at each leaf and three at the
center. For a convex tariff, even two line terminals can have a cheaper
interior center. These controls rule out broader median claims.

## Reproduction and finite evidence

Use CPython 3.12 and the standard library from the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B scripts/research_package.py --package research/consecutive-query-detour
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/consecutive-query-detour/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/consecutive-query-detour/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/consecutive-query-detour --check-source-history
```

The verifier emits a generated JSON receipt containing enumerated counts and
SHA256 hashes of every package file. It writes no files. Redirect stdout to
an external scratch directory to retain a receipt. Normal and optimized runs
are registered separately. Their mathematical checks use explicit exceptions,
so optimization does not disable them.

Finite checks exhaust all integer one-point pseudometric extensions of the
unit paths of lengths two through five with every new distance in
`0..t+1`, and every nonempty subset of internal query endpoints. They also
exhaust all one- and two-cut paths through the 135 three-qubit binary
Lagrangian charts for query profiles `(1,2)`, `(2,1)` and `(1,1,1)`.
All one-, two- and three-cut paths are checked on the 15 two-qubit charts
for profile `(1,1)`. Every distance in the latter fixtures is computed as
`n-log2(|L intersect L'|)` from explicit isotropic subspaces of `F_2^(2n)`.

The checks compare literal paid/target invoices with (1), test the predicted
optimum and its attaining endpoint, and test every hinge tariff on those
integer distance domains. Every nondecreasing concave tariff on
`0..D` with value zero at zero is a nonnegative combination of the hinges
`min(r,h)`, `1<=h<=D`. Indeed, for successive increments `a_h`,
its coefficients are `a_h-a_{h+1}`, with `a_{D+1}=0`.
The coordinate domination check applies to all nondecreasing tariffs. The
endpoint attaining M may depend on the tariff. Hinge objective checks are
finite corroboration, not a numerical exhaustion of the nonlinear minimum
formula over all mixtures. The written proof covers those mixtures.
The printed counts enumerate exactly what ran. The unbounded theorem is
proved above.

The standalone checker needs no Git, network, predecessor code or selected
supplier replay. The two source pins in SOURCES.json preserve task-selection
provenance only. The pending predecessor README is cited at the exact head
below and is not a runtime or proof premise of the metric theorem.

All enumeration bounds are constants in the checker: path lengths at most
three, at most 135 ambient charts, dimensions two and three, and unit paths
of length at most five for one-point extensions. The latter enumerate
126,114 candidate vectors. Python allocates managed objects within these
finite domains; fixed allocation is not claimed. There is no recursion,
network access, subprocess, or output-file mutation. All functions fit within
60 physical lines. Standard-library warning-strict runs provide the available
diagnostics; no separate Python static analyzer is configured for this package.

## Open next questions

1. Can nonconsecutive original queries, with unqueried gaps or overlaps,
   profit from a shared replacement path? Start by retaining the signed
   multiplicity of every boundary and interior edge. The cancellation in
   (1) need not hold, so the present theorem does not answer that question.
2. Can a physically legal shared graph realize independent target credits
   with a better fully charged invoice? Start with explicit arbitrary-input
   maps and restoration, then price each shared edge once per actual use.
   This theorem supplies neither that graph nor its native implementation.

These are also recorded in TASK.json. Native execution, phase conventions,
independent helper inputs, retention, dirty restoration, stock/precision,
fixed-tape movement, all-size compilation, outer admission and independent
human/formal proof-kernel review remain unclaimed. The selected frontier and
its five framework assumptions are unchanged.

## Credit and exact predecessor

This contribution was produced by Nick Petalas. Apache-2.0.

Credit Ali Romman's
[PR #5779 README at 071e4b8f17992846dc555502f6a38ad3dc98be08](https://github.com/aliromman/integer-mult-bounds/blob/071e4b8f17992846dc555502f6a38ad3dc98be08/research/p104-helper-detour-projection/README.md)
for the single-query geodesic rank-metric invoice, its common-edge
cancellation and the explicit several-query question. That source's
single-query bound is cited, not rechecked or claimed as this result.
The present contract changes the number of old queries to a complete
consecutive partition, makes all of them share the replacement path, and
retains their full edge multiplicities.

Credit Joel Pulikkan/GamingPuzzled #5756/#5739, #5751, flyingviper #5718,
zxv's moment arithmetic, #5772's canonical rank formula and the retained
P104/native/Clifford/compiler lineage for the motivating model. No source
code or predecessor evidence is copied or changed. Independent human and
formal proof-kernel review are unclaimed.
