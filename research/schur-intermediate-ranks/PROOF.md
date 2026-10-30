# Nonmaximal Schur-commutator ranks for prescribed pivots

Nick Petalas. Apache-2.0.

This answers, in part, Open next question 1 of Krzysztof Wojt's
[PR #5128](https://github.com/CrocSwap/integer-mult-bounds/pull/5128)
(`research/arbitrary-pivot-schur-minimum`). Its sector factorization, the maps
`L,R` of its equations (4), (7), (8) and its rank-`2d` minimum are cited, not
rechecked. Sections 1–4 are an all-field proof. Section 5 is a finite
certificate.

## 0. Setting

Let K be a field, d >= 1, A,B in GL_d(K), H in M_d(K). Put

```
T00 = I-A-B+H,  T10 = A-H,  T01 = B-H,  T11 = H,   nu_j = nullity T_j.
```

Consider commuting idempotents P,Q in M_n(K) with `P11=A`, `Q11=B`,
`(PQ)11=H`, Schur complements S, Z as in #5128, and ρ = rank(SZ-ZS).

## 1. Reduction to two block subspaces

By #5128 §3–4, such pairs are exactly the choices of sector spaces V_j and maps
`Y_j: U -> V_j`, `X_j: V_j -> U` with `X_j Y_j = T_j` (U = K^d); then
n = Σ dim V_j. By #5128 (5), (7), (8),

```
SZ-ZS  ~  L R,   L = Y G,   R = G' X,
```

with `Y = diag(Y10,Y01,Y11)`, `X = diag(X10,X01,X11)` and fixed maps

```
G(x,y)    = (A^-1 y, -B^-1(Hx+y), (I-B^-1 H)x + (A^-1-B^-1)y),
G'(a,b,c) = (A^-1 a - B^-1 b + (A^-1-B^-1)c,  H B^-1 b + (H B^-1 - I)c).
```

The 00 sector does not enter L or R. Put `M = G G'` on U^3,
`I = im X = ⊕ I_j` and `N = ker Y = ⊕ N_j`. Then `I_j ⊇ im T_j`,
`N_j ⊆ ker T_j`, and

```
ρ = rank(Y M X) = dim(M I + N) - dim N =: f(I,N).                (1)
```

**Cost.** For fixed (I_j, N_j) the least dim V_j is
`dim I_j + (d - dim N_j) - rank T_j`. Sylvester's inequality gives the lower
bound. For attainment, write T_j = σφ with σ a basis of im T_j, add
coordinates ψ reading a complement of N_j in ker T_j, and add columns τ
completing σ to a basis of I_j:

```
Y_j = [φ; ψ; 0],   X_j = [σ, 0, τ].
```

Then `X_j Y_j = T_j`, `im X_j = I_j`, `ker Y_j = N_j`. The 00 sector costs
at least rank T00, attained by a rank factorization. Hence

```
n_min(ρ) = rank T00 + Σ nu_j + min{ dim I - dim N : f(I,N) = ρ },     (2)
```

the minimum over block subspaces `im T_j ⊆ I_j`, `N_j ⊆ ker T_j`. Any larger
n is reached by padding the 00 sector.

## 2. Unit steps

Enlarging I by one dimension, or shrinking N by one, raises the cost in (2)
by exactly one and changes f by 0 or +1. For I this is immediate from (1).
For N' ⊂ N of codimension one, `dim(MI+N')` falls by at most one while
`dim N'` falls by exactly one. Every admissible (I,N) is reached from
`(im T, ker T)` by such steps. Consequences:

* The least dimension at any rank is `n0 = rank T00 + Σ rank T_j`. At n0 the
  rank is forced: `ρ0 = f(im T, ker T) = rank(T M T)`, with
  `T = diag(T10,T01,T11)`.
* Every feasible rank lies in [ρ0, 2d]. If ρ is feasible at n, so is every
  rank in [ρ0, ρ]: a step chain to the attaining pair passes through each
  value. Thus **the ranks feasible at dimension n form the interval
  [ρ0, ρmax(n)]** for n >= n0, and none are feasible below n0.
* `n_min(ρ) >= n0 + (ρ - ρ0)`.

## 3. Deficiency identity

Let `a = Σ (d - dim I_j)` and `b = Σ dim N_j`. Then

```
rank R = 2d - a,     rank L = 2d - b.                            (3)
```

*R.* A row pair (u,v) annihilates R exactly when
`Φ(u,v) = (uA^-1, (-u+vH)B^-1, u(A^-1-B^-1) - v + vHB^-1)` lies in
`⊕ I_j^⊥` (#5128 (8)). Φ is injective because G' is onto. Each pure
covector lies in im Φ:

```
w(A-H)=0:  Φ(wA, w)  = (w, 0, 0),
w(B-H)=0:  Φ(0, w)   = (0, w, 0),
wH=0:      Φ(0, -w)  = (0, 0, w).
```

Since `I_j ⊇ im T_j`, `I_j^⊥` lies in the left kernel of T_j. Hence
`⊕ I_j^⊥ ⊆ im Φ`, the annihilator of R has dimension exactly a, and
`rank R = 2d - a`.

*L.* `ker L = G^-1(N)`. Each pure vector of `⊕ ker T_j` lies in im G:

```
(A-H)z=0:  G(-z, Az) = (z, 0, 0),
(B-H)z=0:  G(z, 0)   = (0, -z, 0),
Hz=0:      G(z, 0)   = (0, 0, z).
```

G is injective, so `dim ker L = dim N = b`.

From (3), `2d - a - b <= ρ <= 2d - max(a,b)`. In particular
`a + b <= 2(2d - ρ)`. The cost in (2) equals `rank T00 + Σ nu_j + 3d - a - b`,
and `nmax = 3d + rank T00 + Σ nu_j` is #5128's formula. Therefore
`n_min(ρ) >= nmax - 2(2d - ρ)`.

## 4. All-field theorem

For every field, d, A,B in GL_d(K) and H in M_d(K):

```
feasible ranks at n = [ρ0, ρmax(n)]        (n >= n0; empty below n0),
n0 = rank T00 + Σ rank T_j,     ρ0 = rank(T M T),
n_min(ρ) >= max( n0 + ρ - ρ0,  nmax - 2(2d - ρ) ),   ρ0 <= ρ <= 2d.   (4)
```

Both bounds are tight at their endpoints: n_min(ρ0) = n0 and
n_min(2d) = nmax (#5128). Also `2d - 2Σ nu_j <= ρ0 <= 2d - Σ nu_j`, by (3)
at a = b = Σ nu_j.

Equality in (4) for all fields and all d is **not** proved here. Attainment
needs a pair with a = b and `im R ∩ ker L = 0` at every intermediate rank, plus
efficient unit steps below the crossover. Section 5 certifies equality only
for d = 2 over F2.

## 5. Finite certificate: d = 2 over F2

`verify.py` enumerates all 576 triples A,B in GL_2(F2), H in M_2(F2)
(288 with AB != BA). For each it enumerates every admissible block pair
(I,N) and computes (1) and (2) exactly. It checks (3) and the sandwich on
every enumerated pair, and checks that equality holds in (4) for every ρ.
For every triple and every feasible rank it then assembles a literal pair
P,Q at the claimed least n, recomputes the Schur complements from the matrix
entries, and checks idempotence, commutation, the three blocks and the rank.
That is 2,496 literal witnesses.

Outcome: ρ0 is 0 for 408 triples, 2 for 144 and 4 for 24; there are 16
distinct profiles. Rank two, the first step named in #5128, is feasible at
n exactly when ρ0 <= 2 and `n >= max(n0 + 2 - ρ0, nmax - 4)`. The 24 triples
with ρ0 = 4 are those with T10, T01, T11 all invertible. They admit only
rank 4, at n = n0 = nmax.

## 6. Boundary

This concerns one common deletion with invertible pivots over a field. It
gives no header count, physical header producer or consumer, dirty-owner
restoration, precision, stock, recursive compilation or outer transfer. No
kappa changes.
