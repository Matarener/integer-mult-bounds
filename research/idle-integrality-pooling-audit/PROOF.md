# Global integer counts do not imply per-call integer counts

This is an audit of one domain inference in [PR3729](https://github.com/CrocSwap/integer-mult-bounds/pull/3729)
at `c7c68f89e020f9e62f38514afdfc99dda01430d4`. It is a counterexample in
the stated aggregate rank-mass relaxation, **not a counterexample packing in
the physical supplier**. The distinction is necessary: additional owner and
hosting constraints might imply a stronger upper bound by a different argument.

## 1. Source-bound model and the extra hypothesis

Write `f_a(r) = (r/73)^(1-a)`, for `0<a<1`. The selected certificate and its
independent invoice give `N=144` complete calls, `W=14336` live families and
the local paid profile per call

```
L = {1:2412, 2:418, 3:432, 4:142, 5:82, 8:8}.
```

Its rank mass is 5586. PR1012's coverage identity gives total paid mass
`72W+64N = 1041408`. Subtracting the local mass `5586N=804384` leaves
`M=237024=1646N` units of aggregate idle mass. The outer guard permits idle
ranks at most 51 because `2*51^2 < 73^2 < 2*52^2`.

The aggregate integer relaxation therefore consists of histograms `h` with

```
h_r in Z_{≥0},  1 ≤ r ≤ 51,  sum r*h_r = 237024,
moment(h,a) = [N*sum L_r*f_a(r) + sum h_r*f_a(r)] / W.
```

Dividing the mass equation by `N` gives an average mass of 1646 per call.
It does **not** make `h_r/N` integer. Nor does it imply that every histogram
can be partitioned among `N` calls with each part of mass exactly 1646.

PR3729's `integrality.moment` applies `best_idle` to `q['idle_mass']=1646`
and divides its result by `w=W/N`. This correctly solves the problem in which
each call separately receives a mass-1646 integer partition. It does not solve
the aggregate integer problem above. The missing implication is a theorem
requiring such a partition, or a direct lower bound of the same strength for
every physical owner configuration. Neither follows from mass conservation
and integer total counts alone.

## 2. The aggregate optimum is already known

Credit Penguin (OpenAI) for Maximus Putnam / PR1685,
`research/idle-packing-stability`, for the following theorem and proof.
For `0<a<1`, `f_a` is strictly concave on `[0,51]` with `f_a(0)=0`.
Two positive nonmaximal ranks `x,y<51` can be replaced by:

* `x+y` if `x+y≤51`;
* `51,x+y-51` otherwise.

In both cases cost strictly decreases. For the second case, concavity of
`f_a(t)+f_a(x+y-t)` on `[x+y-51,51]` puts its minimum at the endpoints.
Each replacement decreases the number of nonmaximal positive ranks, so
iteration terminates. The unique minimizing histogram for integer mass `M`
is `floor(M/51)` rank-51 children and, when nonzero, one child of rank `M mod 51`.
This argument has no owner/hosting constraints. It supplies an optimum of a
relaxation, not a realizability theorem.

Applied per call it gives `{51:32,14:1}`. Repeated 144 times, that is

```
H_separate = {51:4608, 14:144}.
```

Applied to the complete selected cohort it gives the already published PR1685
aggregate optimum

```
H_pooled = {51:4647, 27:1}.
```

Both conserve exactly 237024 units of idle mass. `H_pooled` has integer
counts and respects the same rank cap. It cannot be partitioned into 144
mass-1646 pieces: all but at most one piece lack the unique rank-27 child
and would therefore have mass divisible by 51, whereas `1646 mod 51 = 14`.
Thus the added per-call condition strictly shrinks the aggregate domain.

## 3. A separating moment decision

The import-free positive-binomial engine in `verify.py` gives the following
outward decimal enclosures at the simple rational `a=1689/1000000`:

| Idle histogram | Complete normalized moment |
| --- | --- |
| `H_separate` | `[1.000001152479605767560524, 1.000001152479605767560525]` |
| `H_pooled` | `[0.999996966877034959759759, 0.999996966877034959759760]` |

This saving exceeds PR3729's upper bound `0.001688603446527`. Its per-call
restriction rejects the saving, while the aggregate integer relaxation accepts
it. At the PR's exact upper endpoint, the corresponding intervals are
`[1.000000000000001699259733,1.000000000000001699259734]` and
`[0.999995815381823332558901,0.999995815381823332558902]`.
The PR's lower endpoint is accepted under its own per-call model, an independent
positive control of the arithmetic. The discrepancy concerns the feasible set.

Using the credited optimum theorem and strict increase of each `f_a(r)` in `a`,
the correct **fixed-144-call aggregate integer** root lies strictly between

```
0.001690044548222 < a_144 < 0.001690044548223.
```

Both endpoint signs are certified in `RESULT.json`. This is a necessary ceiling
in the aggregate relaxation. It is not an attainable supplier saving. It is
slightly below the earlier fractional ceiling, rather than the much lower
per-call integer figure.

## 4. What the literal selected owner interface charges

The pinned selected owner rows and plan are recounted without importing or
executing a predecessor verifier. The exact source `t16/indep16.py`, whose
bytes also match the copy in selected PR1094's frozen `upstream1087.tar.gz`,
keys occupied cells by `(owner_replica, child, port)`. Its `check_roles` unions
the cells consumed by all hosted calls in that bin and charges one leftover
rank. `hosting/PROOF.md` writes that rank as `C_g - sum widths in g`.

One literal selected bin `(0,6,85)`, physical family 645, has capacity 32:

| Hosted call time | Offset | Width |
| --- | --- | --- |
| 9 | 0 | 9 |
| 11 | 9 | 4 |
| 13 | 13 | 9 |
| 15 | 22 | 9 |

Its one residual rank is `32-(9+4+9+9)=1`. It depends on four calls, not
an isolated call's local invoice. The full capacity recount recovers the
selected idle histogram `{1:2276,3:377,7:7,48:4866}`. There are 17217 used
bins with allocations from more than one call; the distinct-call inventory
is recorded in `RESULT.json`.

The same recount confirms bin capacities `{8:10752,16:7168,32:7168,48:7168}`,
total capacity 774144 and allocated width 537120. Every residual in this
unchanged bin recipe is at most 48, so `H_pooled`'s rank-51 children cannot be
realized there. These inventories and the shared-bin accounting rule are
already documented in Hanson's `selected-t16-pattern-dual`, which independently
checks Ali Romman's PR1129 fixed-inventory bound and cites Josie Elliston's
rank-48 relaxation. The present check supplies no new optimum in that domain.

This is evidence about the source interface, **not a proof that the selected
histogram lacks every artificial mass-1646 partition**. Nor does it make
`H_pooled` physically legal. The recount checks call/owner identities,
declared window membership, nonoverlapping prefix slices, complete helper
inventory and residual ranks. It does not rederive source-event windows,
native frames, phase semantics, providers, physical tape costs or admission.

## 5. Normalization and replication

In the coverage relaxation with `N=9T`, `W=896T`, the aggregate idle mass is
`1646N`. If `N` is a multiple of 51, this can be placed entirely in integer
rank-51 children. For example `N=153,W=15232` gives `{51:4938}` and hence

```
4938/153 = 1646/51.
```

Its normalized moment is **identically** the fractional relaxation for every
`a`, despite every total count being integer. Its root independently reproduces
`[0.001690054109088,0.001690054109089]`. Likewise 17 copies of the complete
selected cohort give `N=2448,W=243712` and `{51:79008}` with zero aggregate
residue. These are algebraic statements about a pooled relaxation. They do
not establish a T17 template, permit physical coalescence across cohorts,
or override a restriction to exactly 144 calls. The fixed-144 counterexample
does not depend on this scaling observation.

The PR also declares the two-unpaid-coordinate lever nonintegral because
its average idle mass is `13918/9`. For nine calls the changed-law total is
the integer 13918, with integer histogram `{51:272,46:1}`. Thus its fractional
average does not establish infeasibility of the aggregate integer model.
The changed coverage law and a physical two-unpaid-coordinate supplier remain
unproved; this example addresses only the integrality inference.

## 6. Independent enclosure and its verification boundary

Let `p=1-a`, `z=1-r/73`. For `0<p<1` and `0<z<1`, the generalized binomial
series is

```
(1-z)^p = 1 - sum_{k>=1} t_k,
t_1 = p*z,
t_{k+1} = t_k*z*(k-p)/(k+1).
```

Every `t_k` is positive and every successive ratio is less than `z`. After
terms through `k`, the uncomputed tail is bounded by `t_{k+1}/(1-z)`.
The implementation brackets each term on the integer grid `10^-70` with
directed floor/ceiling multiplication. Induction encloses each term and each
partial sum. Subtracting an upper sum and upper tail gives a lower price;
subtracting a lower sum gives an upper price. The tail stopping threshold
is `10^-45`. No floating-point operation supplies a verdict or decimal bound.
Failure to converge within 29999 terms raises an exception.

All source-relevant prices are summed with the actual integer multiplicities
and divided by the actual `W`. The engine imports no predecessor pricing,
optimizer or verifier. The optimizer's mathematical argument is explicitly
reused from PR1685. Polynomial calibrations square the price bounds for all
72 ranks at `a=1/2`, and cube them at `a=1/3,2/3` for five relevant ranks.
They independently check against rational powers without a transcendental
library. Small exact partition enumeration cross-checks the credited optimum.
Wrong histogram domains, missing normalization, call factors, source changes,
owner identities and slice allocations are covered by controls.

This is one author-executed AI-assisted audit. No independent human review,
formal proof-kernel acceptance, physical counterexample, complete supplier
invoice or selected cold replay is claimed. The original fractional ceiling
and every selected certificate remain unchanged.
