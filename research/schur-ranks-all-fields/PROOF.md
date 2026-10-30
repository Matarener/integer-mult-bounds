# Exact intermediate Schur ranks over every field

Prepared by apoursh with substantial OpenAI Codex assistance. Apache-2.0.

This resolves both open next questions in Nick Petalas's
[PR #6031](https://github.com/CrocSwap/integer-mult-bounds/pull/6031),
`research/schur-intermediate-ranks`, scientific head
`acc000f4edfa0b0c4a90b505c6e02a4c3572f74c`. We use its sector-subspace reduction
and minimum realization cost, and Krzysztof Wojt's
[PR #5128](https://github.com/CrocSwap/integer-mult-bounds/pull/5128),
`research/arbitrary-pivot-schur-minimum`, scientific head
`2839d35e58b3285a1992a3ecbae2809ebef7661b`, for the Schur factorization and
commuting-idempotent realization. Those predecessor reductions are cited,
not claimed as new or independently re-proved here. The added argument is a
sector-preserving decomposition into two bilinear pairings. Reducing a
bilinear pairing to a rank core and its radicals is classical linear algebra;
no historical priority is claimed for that operation.

## 1. Statement and setting

Let K be any field, let d >= 1, and fix A,B in GL_d(K) and H in M_d(K).
No commutation among A,B,H is assumed. Define

```
F = A-H,       J = B-H,       T00 = I-A-B+H,
s = nullity F + nullity J + nullity H,
n0 = rank T00 + rank F + rank J + rank H,
nmax = 3d + rank T00 + s.
```

Here `nmax` denotes the least dimension attaining the maximum commutator
rank 2d, as in #5128; it is not an upper bound on the ambient dimension.
Consider all commuting idempotents P,Q in M_n(K) satisfying

```
P11 = A,       Q11 = B,       (PQ)11 = H,
```

where the leading block has size d. Their Schur complements are

```
S = P22 - P21 A^-1 P12,       Z = Q22 - Q21 B^-1 Q12.
```

Put rho = rank(SZ-ZS), and let n_min(rho) be the least ambient dimension
for that rank with the prescribed A,B,H.

**Theorem.** The minimum possible rank is

```
rho0 = rank(J A^-1 F) + rank(F B^-1 J) + 2 rank H - 2d.           (1)
```

For every integer rho with rho0 <= rho <= 2d,

```
n_min(rho) = max(n0 + rho - rho0, nmax - 2(2d-rho)).             (2)
```

There are no other possible ranks. A rank rho in this interval is feasible
at dimension n exactly when n >= n_min(rho). Thus the theorem also decides
the complete rank set at every ambient dimension. Both formulas hold in
arbitrary characteristic and over finite or infinite fields.

## 2. Cited reduction and the deficiency pairing

Write U = K^d and E = U direct-sum U. In the 10,01,11 sectors put
`T10=F`, `T01=J`, `T11=H`. The reduction in #6031, Sections 1--3, permits
arbitrary sectorwise subspaces

```
im Tj <= Ij <= U,       Nj <= ker Tj.                            (3)
```

They are realized by maps Xj,Yj with XjYj=Tj, im Xj=Ij and ker Yj=Nj.
Their least sector dimension is
`dim Ij + d - dim Nj - rank Tj`; the 00 sector can have dimension
rank T00. In particular, with

```
a = sum_j (d - dim Ij),       b = sum_j dim Nj,
```

the least ambient dimension realizing these choices is

```
n = nmax - a - b.                                               (4)
```

The same predecessor supplies the maps

```
G(x,y)    = (A^-1 y, -B^-1(Hx+y), (I-B^-1 H)x + (A^-1-B^-1)y),
G'(u,v,w) = (A^-1 u - B^-1 v + (A^-1-B^-1)w,
             H B^-1 v + (H B^-1-I)w).
```

Here G:E -> U^3 is injective and G':U^3 -> E is surjective. If
`I = I10 direct-sum I01 direct-sum I11` and similarly N, the Schur
commutator rank equals the rank of `L R`, with `L=Y G`, `R=G' X`.
Let

```
C = G'I <= E,       D' = annihilator(C) <= E*,
K' = G^-1 N <= E.
```

The deficiency identities in #6031 give dim D'=a and dim K'=b. Restrict
the natural bilinear evaluation pairing `E* x E -> K` to D' x K',
and call its rank q. Its right kernel is K' intersect C. Therefore

```
rho = dim C - dim(C intersect K')
    = 2d - a - b + q.                                           (5)
```

All annihilators here are algebraic dual annihilators, not Hermitian
orthogonal complements.

For the largest possible deficiencies, take Ij=im Tj and Nj=ker Tj.
Their spaces D,K have the following direct-sum decompositions; w is a
row covector and z is a column vector:

```
D10 = {(wA,w) : wF=0},       K10 = {(-z,Az) : Fz=0},
D01 = {(0,w)  : wJ=0},       K01 = {(z,0)   : Jz=0},
D11 = {(0,-w) : wH=0},       K11 = {(z,0)   : Hz=0},
D = D10 + D01 + D11,         K = K10 + K01 + K11.                (6)
```

These are precisely the pure-sector lifts in #6031's deficiency proof.
For example G(-z,Az)=(z,0,0) when Fz=0, whereas G(z,0)=(0,-z,0)
when Jz=0 and G(z,0)=(0,0,z) when Hz=0. The minus sign in the 01 lift
does not change its subspace. The covector lifts follow by composing
with G'. Injectivity of G and of the dual map of G' proves that the
sums in (6) are direct. Each of D and K has dimension s.

More generally D' is an arbitrary direct sum of subspaces of the three
Dj, and K' an arbitrary direct sum of subspaces of the three Kj.
Indeed, a choice of covectors Wj <= left ker Tj corresponds exactly
to Ij=annihilator(Wj), and a subspace of Kj corresponds exactly to Nj.
Thus every sectorwise subspace choice made below is allowed by (3),
not merely a choice in the unrestricted spaces E or E*.

## 3. Only two pairing blocks survive

Compute the evaluation pairing of (6). The entry in each cell is the
value on the corresponding w,z, with their row and column constraints:

| | K10 | K01 | K11 |
|---|---|---|---|
| D10 | 0 | w H z | 0 |
| D01 | w H z | 0 | 0 |
| D11 | 0 | 0 | 0 |

For example the D10,K10 entry is `-wAz+wAz=0`. The D10,K01 entry
is wAz=wHz because wF=0; the D01,K10 entry is wAz=wHz because Fz=0.
The D10,K11 entry vanishes since wA=wH and Hz=0. The D11,K10 entry
vanishes since Az=Hz and wH=0. All remaining entries vanish directly.
These identities also hold in characteristic two.

Let

```
r1 = rank of (left ker F) x (ker J) -> K,       (w,z) |-> wHz,
r2 = rank of (left ker J) x (ker F) -> K,       (w,z) |-> wHz,
r  = r1 + r2.                                                   (7)
```

The two nonzero blocks have separate domain and codomain sectors, so
the full D x K pairing has rank r. The two ranks need not be equal.
At the largest deficiencies a=b=s, equation (5) gives

```
rho0 = 2d - 2s + r.                                             (8)
```

Every restriction has q <= r and a,b <= s. More precisely, the
rank lower bound rho >= rho0 follows either from the unit-step
argument in #6031 or by deleting one basis direction at a time
from the full pairing: such a deletion lowers a+b by one and q by
zero or one, so (5) cannot decrease. Thus (8) is the minimum rank.
Its least dimension is `nmax-2s=n0` by (4).

## 4. Sharp dimension for every intermediate rank

Put delta=2d-rho. For any admissible pair D',K', equation (5) says
`delta=a+b-q`. Since q <= min(a,b,r),

```
a+b <= 2 delta,       a+b <= delta+r.
```

Equation (4), or the corresponding lower bound for a nonminimal
realization of the same subspaces, therefore implies

```
n >= nmax - delta - min(delta,r).                              (9)
```

We now attain (9), for every integer
`0 <= delta <= 2s-r = 2d-rho0`, while respecting all three sectors.

Reduce each of the two nonzero bilinear blocks in the table to rank
normal form by choosing bases within its row and column sectors.
Each block is a direct sum of paired one-dimensional coordinates
with evaluation matrix I, and zero left/right radical coordinates.
Because the blocks use disjoint sectors, these two basis changes
can be performed independently. There are r paired coordinates on
each side in total, and `2s-2r` unpaired radical coordinates across
the two sides, including both 11 sectors.

* If `0 <= delta <= r`, choose any delta of the paired coordinates,
  retaining each on both sides. This gives a=b=delta and q=delta.
  Hence the resulting rank is `2d-delta`, with cost `nmax-2delta`.
* If `r <= delta <= 2s-r`, retain all r paired coordinates on both
  sides and add any `delta-r` radical coordinates. There are enough
  because `delta-r <= 2s-2r`. Then a+b=delta+r and q=r, giving rank
  `2d-delta` with cost `nmax-delta-r`.

The normal forms and all the selections are within individual sectors.
Section 2 therefore realizes them by actual commuting idempotents
with the prescribed three leading blocks. No field-size condition
or generic choice of a vector is needed.

Consequently equality holds in (9). Since

```
n0 = nmax-2s,       rho0 = 2d-2s+r,
n0+rho-rho0 = nmax-delta-r,
```

this equality is exactly (2). It also establishes every integer rank
in the stated interval; the factorization through E excludes ranks
above 2d. Padding the 00 sector with any number of coordinates on
which both X00 and Y00 are zero preserves A,B,H and the commutator
rank. It attains every larger ambient dimension. This proves the
claimed feasibility statement for each n, including zero-size Schur
complements when n=d.

## 5. Eliminating nullspace bases from rho0

For arbitrary square F,J,H of size d, the rank of the pairing
`(left ker F) x (ker J) -> K`, `(w,z) |-> wHz`, is

```
r1 = rank [[F,H],[0,J]] - rank F - rank J.                      (10)
```

One way to see (10) is to project the image of the block matrix to
its bottom component. That projection has image im J; its kernel
inside the block-matrix image is the top-component subspace
`im F + H ker J`. Subtracting rank F leaves the rank of the induced
map `ker J -> U/im F`, which is also the rank of the displayed
pairing against left ker F.

In our setting F+H=A is invertible. Adding the second block column
to the first changes the block matrix to `[[A,H],[J,J]]`. Eliminating
the bottom-left block gives the Schur complement

```
J - J A^-1 H = J A^-1 F.
```

Therefore

```
r1 = d + rank(J A^-1 F) - rank F - rank J,
r2 = d + rank(F B^-1 J) - rank F - rank J.                       (11)
```

The second identity uses J+H=B and the swapped pairing. Substitute
(11) and `s=3d-rank F-rank J-rank H` into (8) to obtain (1).
The order of factors is essential; A,B,H need not commute.

## 6. An odd minimum-rank fixture over F3

Take d=2 over F3 and

```
H = [[1,0],[0,1]],
A = [[1,0],[0,2]],       B = [[1,1],[0,1]],
F = [[0,0],[0,1]],       J = [[0,1],[0,0]],
T00 = [[0,2],[0,2]].
```

Then s=2, n0=5 and nmax=9. In this field

```
J A^-1 F = [[0,2],[0,0]],       F B^-1 J = [[0,0],[0,0]],
r1=1,       r2=0,       rho0=1.
```

Formula (2) gives the exact minimum dimensions

| rho | 1 | 2 | 3 | 4 |
|---|---|---|---|---|
| n_min(rho) | 5 | 6 | 7 | 9 |

In particular, neither equality of the two pairing ranks nor evenness
of rho0 can be imported from the binary d=2 census in #6031.
That census remains valid; this fixture is over a different field.

## 7. Scope and verification boundary

This is a written algebraic proof for one common deletion with invertible
pivots. The independent finite checks accompanying the package corroborate
its identities and constructions; they do not prove its universal
quantifiers or constitute proof-kernel verification. The theorem depends
on the cited predecessor factorization and sector realization.

It supplies no physical header producer or consumer, header count,
dirty-owner restoration protocol, precision bound, stock estimate,
recursive compilation or outer transfer. Those costs are unpriced here,
not zero. It changes neither the selected multiplication construction nor
kappa, and it makes no claim that archival publication is scientific
acceptance of the theorem.
