# Named-class cancellation charging beats the termwise `180/7` ceiling

## Premises and named term classes

Fix the 56 physical nondegenerate binary planes and the 23 induced C5s of the
plane-orthogonality graph retained by PR2782/PR1825. Complete-plane binary
pairing tariffs and the local inequalities

```
sum_t r_C(A_t, B_t) >= 20
```

are granted as predecessor premises; this note does not prove them.

A **named-class** asymmetric scalar decomposition uses only the four term
classes that already appear in the published identity fixtures:

- diagonal outer products `e_i e_i^T`,
- the full-support term `J = 11^T`,
- off-diagonal coordinate outer products `e_i e_j^T` (`i != j`),
- pairwise Gram outer products `(e_i + e_j)(e_i + e_j)^T`.

Every such term has plane-support of size at most two, except `J`, which has
full support of size 56.

## Cancellation identity

**Step 1 (identical-support netting).** Cancel opposite-signed terms that share
the same plane-support rectangle before charging. The netted term list is still
an exact decomposition of the same matrix, so the granted local floors continue
to apply to it.

**Step 2 (named-support domination).** Choose nonnegative weights `λ_C` with

```
sum_C λ_C = 9/4
```

recorded exactly in RESULT.json (integer lifts `weight16` summing to 36). Demand

```
sum_C λ_C r_C(A, B)  <=  r(A, B)
```

for every source/target rectangle whose plane supports have size 1 or 2. Both
scanners check all `1596^2 = 2,547,216` such rectangles; the inequality is tight
on at least one of them.

**Step 3 (explicit J credit).** Full-support rectangles are **not** required to
satisfy uncredited termwise domination. Write

```
ρ = sum_C λ_C r_C(full, full) = 303/16.
```

Each remaining net full-support term contributes an additive credit of
`ρ - 9 = 159/16` on top of its global tariff 9.

## Fit-level corollary

Summing the named-support inequalities over netted non-full-support terms and
charging each net full-support term with the credit above yields, for every
named-class decomposition `F` with `|σ_J|` remaining net full-support terms,

```
20 sum_C λ_C  <=  Cost(F) + (ρ - 9) |σ_J|.
```

Equivalently

```
Cost(F)  >=  45 - (159/16) |σ_J|.
```

In particular:

- if `σ_J = 0` (J-free after netting), then `Cost(F) >= 45`;
- if `σ_J = 1`, then `Cost(F) >= 561/16 = 35.0625`.

Both floors strictly exceed the classical termwise aggregation ceiling
`180/7 < 26` of `c5-global-charging-obstruction` / `c5-global-charging-ceiling`.
The uncredited full-support test on these same weights fails (`ρ > 9`), so the
improvement is precisely the cancellation credit, not a silent relaxation of
the classical method on all rectangles.

## Discriminating fixtures

- Diagonal identity `I = sum_i e_i e_i^T`: J-free, tariff exactly 224, meets the
  J-free floor 45.
- J-identity extension `I = J - sum_{i != j} e_i e_j^T`: one net full-support
  term, tariff exactly 16097, meets the one-J floor `561/16`.

Residual/local-opt summing `sum_C Cost_opt(K|_C) <= Cost_opt(K)` remains false
on the diagonal (`460 > 224`) and is not reused; this note answers the successor
cancellation-identity question left open there.

## Limits

No new global decoder floor outside named classes, no supplier, no native
program, no dirty restoration, no selected-frontier update and no new kappa.
Local cost-20 theorems are granted, not replayed. A cost-preserving lemma that
eliminates every net `J` from named-class exact fits is left open; without it
the universal named-class floor is the one-J bound `561/16`, still above
`180/7`.
