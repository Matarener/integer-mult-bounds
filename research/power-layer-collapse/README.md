# Power tariffs collapse the fixed-spread antichain to one optimum

For every integer m >= 1 and 0 <= k <= m, the complete k-spread layer of
[Nick Petalas's PR #5901](https://github.com/CrocSwap/integer-mult-bounds/pull/5901)
`concave-invoice-antichains` family has **one unique cheapest invoice for every
power tariff r^p with 0 < p < 1**: spread precisely blocks 1,...,k.
The result answers that package's second open question. Its 252-member m=10
layer and 462-member m=11 layer each reduce to one representative under this
narrower tariff family, although every pair remains incomparable under the
larger increasing-concave family.

This is a scoped proof and exact finite corroboration, not a legal supplier,
a new kappa, a claim about arbitrary invoices, or a refutation of the predecessor.
The predecessor's all-concave theorem remains valid.

## Contract and proof

Write H_r for one rank-r paid call. For S subset {1,...,m}, retain the full bill

```
P_S = sum_(i not in S) 2 H_(2i) + sum_(i in S) (H_(2i-1)+H_(2i+1)),
I_S = P_S - H_M,                 M = 2m(m+1).
```

All candidates have 2m paid calls, mass M, and the same productive target.
No other fee, boundary, or consumer may differ in this comparison. The theorem
is about the synthetic family defined above; it grants no realization of it.

Fix p in (0,1). The cost difference made by spreading block i is

```
delta_i(p) = (2i-1)^p + (2i+1)^p - 2(2i)^p.
```

For x>1, integrating the second derivative twice gives

```
delta(x) = p(p-1) integral_[-1,1] (1-|t|) (x+t)^(p-2) dt.
```

The identity follows by applying the fundamental theorem of calculus on each
side of x, or by integration by parts on [-1,0] and [0,1]. The kernel is
nonnegative and positive in the interior. Since p-2<0, its power factor strictly
decreases as x increases. Since p(p-1)<0, **delta(x) strictly increases**.
Thus delta_1(p) < ... < delta_m(p) < 0, simultaneously for every p in (0,1).

Let S0={1,...,k}. If a k-subset S differs from S0, it contains j>k and omits
i<=k. Exchanging j for i decreases its complete bill by
`delta_j(p)-delta_i(p)>0`. Repeating terminates at S0. The target and all
unchanged paid blocks cancel at each exchange. This proves strict simultaneous
dominance and uniqueness for 0<k<m; at k=0,m the layer is a singleton. A common
normalization by any positive width to the power p preserves the result.

The same argument applies to any increasing sequence of block centers x_i>1
with a common symmetric spread h satisfying 0<h<min x_i: use
`(x_i-h)^p+(x_i+h)^p-2*x_i^p` and the triangular kernel on [-h,h].
It does not automatically cover varying spread widths.

## Why the larger antichain is consistent

At m=2 the bills for S={1} and S={2} differ by -1 under min(r,2) and by +1
under min(r,4). These hinge witnesses prove their concave incomparability, as
in the predecessor. Neither is a power tariff. In contrast, S={1} is strictly
cheaper for every p in (0,1). Equal count and mass alone would not establish
this; the ordered disjoint equal-width spreads supply the missing structure.

A reducer can discard the rest of the **complete layer** if it is pricing only
these powers. If a candidate pool omits S0, this theorem cannot manufacture a
replacement. Changed physical boundaries, productive targets, fees, or legal
realizability require separate checks. At p=0 or p=1 every layer member ties;
the strict theorem deliberately excludes those endpoints. For p=3/2 the
ordering reverses, so extending this pruning rule outside its interval is wrong.

## Evidence and reproduction

```
python3.12 -B scripts/research_package.py --package research/power-layer-collapse
python3.12 -B scripts/check_research_commit.py --package research/power-layer-collapse
```

The standard-library verifier enumerates every layer for 1<=m<=11. It evaluates
all distinct rational p=a/b in (0,1), b<=8, using rational intervals obtained
by **integer nth-root bounds**, never floating point. It checks every adjacent
spread inequality and strict complete-invoice dominance of every noncanonical
layer member. Endpoints, both hinge witnesses, the reversed p=3/2 order and
changed-target/fee counterexamples are exact controls. Normal and optimized
runs are registered; no package file is written by replay. The uniform theorem
is the written proof, not extrapolation from these checks.

Source provenance is pinned in SOURCES.json. Upstream was refreshed to
721c03822c421b7f7fcbb2598993b947c4d88419 (revision 8) on 2026-10-28 UTC;
the selected record there is #6030, kappa .003125804. The sparse baseline
preflight reported 1,393 omitted inputs; that unrelated selected supplier replay
was not materialized or run. Only the predecessor definition is a live input. The optional source-history checker
refuses this shallow repository; no full-history pass is claimed. All pins resolve
at the immediate main-branch base, which is an ancestor of the publication head.
The ordinary committed-byte preflight passes.

## Significance for researchers

An exponential frontier for every concave tariff need not obstruct optimization
of the power moments actually used for kappa. This family permits an exact
one-representative reduction across the entire relevant power interval. The
next useful question is whether legal supplier exchanges share its ordered
spread structure, with all physical costs retained.

## Open next questions

Can a legal source-bound supplier realize two independently selectable equal-width
spreads with a common complete boundary and fee? First extract two actual paid
rank exchanges and their target, restoration and native ledgers. No such physical
realization is supplied here; the synthetic family alone cannot raise kappa.

For a partial layer that omits S0, can one characterize all power-undominated
members? Start with the first index-incomparable pair and certify its difference
on 0<p<1. The exchange proof only orders componentwise comparable index lists.

## Credit

Prepared by [zxv](https://github.com/zxv) with substantial OpenAI Codex assistance.
[Nick Petalas](https://github.com/petalas) supplies the antichain family and open
question. Its lineage credits [Ali Romman](https://github.com/aliromman),
[zxv](https://github.com/zxv), [mightyOil](https://github.com/mightyOil) and [Dugongue](https://github.com/Dugongue) for the existing invoice
framework; no predecessor construction is claimed as new. The triangular-kernel
calculus identity and exchange argument are elementary. No independent human or
proof-assistant review is claimed. Apache-2.0.
