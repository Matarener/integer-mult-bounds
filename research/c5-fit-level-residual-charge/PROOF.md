# Fit-level residual local-opt C5 charging fails on the identity

## Candidate

Grant every physical C5 local theorem

```
Cost_opt(K|_C) >= 20
```

for completed strict scalar fits `K` over a characteristic-zero field, where
`Cost_opt` is the complete-plane binary pairing tariff of PR2782 and `K|_C`
is the residual matrix on the ten scalar coordinates of cycle `C`. The
twenty-three cycles and the local floors are predecessor premises; this note
does not prove them.

A natural coefficient-sensitive completed-fit charging inequality uses only
those residual local optima:

```
sum_C Cost_opt(K|_C)  <=  Cost_opt(K)                 (*)
```

and more generally `sum_C λ_C Cost_opt(K|_C) <= Cost_opt(K)` for fixed
nonnegative weights `λ`. If `(*)` were universal, the granted floors would
give the global lower bound `Cost_opt(K) >= 460` on every completed fit.

## Diagonal counterexample

Take the explicit diagonal decomposition

```
I_112 = sum_{i=0}^{111} e_i e_i^T.
```

Each term touches a single complete plane on both sides. The binary pairing
of a nondegenerate plane with itself is `I_2`, of rank exactly two. Hence the
decomposition has tariff

```
112 * 2 = 224.
```

In particular `Cost_opt(I_112) <= 224`. The residual of `I` on every C5 is
again an identity on ten coordinates, so the granted floors give

```
sum_C Cost_opt(I|_C) >= 23 * 20 = 460.
```

Therefore `(*)` fails at `K = I_112`:

```
460 ≰ 224.
```

Any nonnegative weight vector with `sum_C λ_C > 224/20 = 56/5` likewise
cannot satisfy the weighted form on this same `K`.

## Why the J-bearing identity extensions do not decide the candidate

The two exact identity extensions retained by the predecessor obstruction
package both realize the residual matrix `I`, but they are expensive as
decompositions:

```
I = J - sum_{i != j} e_i e_j^T                 (12433 nonzero terms),
I = J - sum_{i<j}(e_i+e_j)(e_i+e_j)^T
    + (n-1) sum_i e_i e_i^T                   (6329 nonzero terms).
```

Against those particular term lists, the numerical comparison
`460 <= decomposition cost` holds for trivial reasons and does not certify
`(*)`. A discriminating test must use a cheap completed fit; the diagonal
identity is such a test.

## Relation to the termwise obstruction

Direct fixed-nonnegative termwise restriction charging remains capped at
`180/7` by the full-support term `J` (predecessor). The present note answers
the successor question about residual/local-opt completed-fit charging: that
candidate is not a valid inequality, so it cannot escape the individual-term
ceiling. No claim is made about every conceivable cancellation identity.

## Limits

No new global decoder floor, supplier, native program, dirty restoration,
consumer invoice, selected-frontier update or kappa is claimed. The local
cost-20 theorems are granted, not replayed. Historical heavy suites, Lean,
Docker and independent human or proof-kernel review are unrun.
