# The sharp unit-fee target-rank threshold

This scoped proof is produced by Nick Petalas. New material is Apache-2.0.
The fee-charged partition contract comes from Ali Romman's PR #5769. Strict
concavity, Jensen's inequality and balancing are classical ingredients.

## Contract and theorem

Fix `p=99/100`. Replace one productive target of integer rank `R` by `k>=2`
independent productive targets with positive integer ranks `r_1,...,r_k`, whose
sum is `R`. Charge **one additional paid rank-one recursive child per piece**.
Keep every other paid child, productive target and fee fixed. Under the raw
power tariff, the improvement in paid cost minus productive credit is

```text
G(R;r_1,...,r_k) = sum_i r_i^p - R^p - k.
```

A positive `G` means a strictly cheaper complete invoice. The `R^p` debit is
essential. The charge is `k`, including every resulting piece. This theorem
uses neither `k-1` fees nor a free distinguished piece. A scalar addition is
not assumed to cost a recursive rank-one child.

**Theorem.** Such a strictly improving partition exists if and only if
`R>=288`. At the first rank, `(96,96,96)` has improvement strictly between
`6289/1000000` and `6290/1000000`. Every proper partition with `R<=287` loses.
In fact its improvement is less than `-4077/1000000`.

This is an arithmetic screening result for the declared fee. It does not assert
that arbitrary target partitions are physically realizable or useful.

## Rejecting every smaller rank

For any fixed `R,k`, Jensen's inequality gives

```text
sum_i r_i^p <= k(R/k)^p = R^p k^(1/100),
G <= J(R,k) = R^p (k^(1/100)-1) - k.
```

For every `k>=2`, `J(R,k)` strictly increases with positive real `R`.
Consequently, for `R<=287` and `2<=k<=R`, it suffices to bound `J(287,k)` for
the complete finite list `k=2,...,287`. No integer partitions are omitted by
this reduction; it even grants arbitrary positive real piece sizes at each k.

The standalone checker supplies an exact dyadic certificate for each of those
286 inequalities. Let `D=2^128`. To bound a positive `n^(a/100)`, compute

```text
L = floor_root_100(n^a D^100),
U = L if L^100=n^a D^100, else L+1.
```

The checker verifies `L^100 <= n^a D^100 < (L+1)^100` using integers.
Thus `L/D <= n^(a/100) <= U/D`. Use `a=99` for `287^p` and `a=1` for each
`k^(1/100)`. With their respective upper numerators `U_287,U_k`,

```text
D^2 J(287,k) <= U_287 (U_k-D) - k D^2 < 0.
```

Every right-hand numerator is present in the generated receipt. The largest
Jensen upper bound occurs at `k=3` and is strictly negative. Monotonicity proves
the stated rejection for every smaller integer rank and every proper partition.

The stronger integer margin uses balancing, proved below. The checker also
encloses the balanced integer partition's profit at rank 287 for every one of
the same 286 piece counts. The largest upper bound occurs at `k=3`, with parts
`(95,96,96)`, and is below `-4077/1000000`. Balanced profit strictly increases
with R at fixed k, as shown below, so this integer margin applies to every
proper partition at every smaller rank too. Jensen's real-size relaxation is
used only for the sign, not for this stronger integer margin.

## Attainment and all larger ranks

At `R=288`, take three rank-96 pieces. The exact root enclosures above, with
`a=99`, give

```text
6289/1000000 < 3*96^p - 288^p - 3 < 6290/1000000.
```

All comparisons are integer cross-multiplications. This proves attainment at
288 independently of any floating-point approximation or source executable.

For completeness, the witness extends to every larger rank. For fixed k,
strict concavity implies that a maximizing integer partition has parts differing
by at most one. Indeed, if `b>=a+2`, replace `(a,b)` by `(a+1,b-1)`.
The decreasing increments of `x^p` make the credit strictly larger.

Write `B_k(R)` for the balanced partition's improvement. When `R` increases by
one, increase a smallest piece `q=floor(R/k)` by one. Then

```text
B_k(R+1)-B_k(R) = ((q+1)^p-q^p) - ((R+1)^p-R^p) > 0,
```

since `q<R` and `x^p` has strictly decreasing increments. Apply this with
`k=3` for every integer `R>=288`. The positive rank-288 witness and this strict
monotonicity establish existence at every larger rank. No additional search or
new supplier premise is used.

## What the executable proves

The written argument reduces the infinite claim to 286 root-enclosed Jensen
inequalities and one positive witness. `verify.py` checks those inequalities
and rational margins with integer arithmetic. It also checks the balancing
lemma on every proper sorted integer partition of ranks 2 through 24, uses an
independently implemented bisection oracle for eleven decisive powers, and
rejects forged certificates and invalid partitions. These finite checks
corroborate the written proof; they are not proof-kernel verification.

The receipt is generated on stdout and binds every package file by SHA256.
No receipt is hand-written or stored as an assumed mathematical input. Normal
and optimized modes must emit identical receipts. A supplied `--check-receipt`
file is checked against a fresh computation and fresh source hashes.
