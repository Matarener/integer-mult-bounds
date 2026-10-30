# Exact commutator after a common Schur deletion

This package was produced by Nick Petalas. Apache-2.0.

**Scoped algebraic proof with finite corroboration. No new κ.** For two
commuting matrices over any field, deleting the same nonzero scalar pivot
leaves Schur complements whose commutator has rank at most two. An explicit
factorization gives an exact zero criterion and rank trichotomy. The bound is
sharp even for commuting idempotents of rank two in dimension three over F5.

This answers the one-step commutativity part of open question 1 in
[PR4259](https://github.com/CrocSwap/integer-mult-bounds/pull/4259), pinned at
`2a582d8f66d1900b22ee2cd0062ee5dca94e8f85`. That package proves laminar
preservation and asks for the changing Schur pair for nonnested overlap. The
present result identifies its commutator, rather than its full simultaneous
conjugacy orbit or a new header-counting law. The predecessor is a cited
motivation, not an audit target.

## Statement

Let P and Q commute over a field K. Write their common block split as

```text
P = [[p,r],[c,D]],   Q = [[q,s],[e,F]],   PQ = QP = [[h,t],[w,J]],
S = D-c r/p,        T = F-e s/q,         p != 0, q != 0.
```

Here r,s,t are rows, c,e,w are columns and h,p,q are scalars. Define

```text
u = c/p-e/q,       v = r/p-s/q,
x = w-h e/q,       y = t-h s/q.
```

Then the exact identity and rank classification are

```text
[S,T] = ST-TS = x v-u y,
rank [S,T] <= 2,
rank [S,T] = 2  iff  x,u are independent and v,y are independent.
```

The complements commute exactly in the following cases:

- If u=0, either x=0 or v=0.
- If u!=0 and v=0, y=0.
- If u!=0 and v!=0, there is a scalar λ with x=λu and y=λv.

Otherwise the commutator has rank one unless both independence conditions
hold, in which case it has rank two. The test includes zero vectors and works
in characteristic two. It uses the vector and row data, rather than only the
ranks and scalar pivots.

If P and Q are idempotents, S and T are idempotents of ranks one lower. Thus
this is an exact test for whether a commuting projector pair remains a
commuting projector pair after one admitted pivot. It also describes precisely
how commutativity can fail when the laminar preservation argument stops.

## Proof

The blocks of PQ=QP give

```text
DF = J-c s,       FD = J-e r,
D e = w-c q,      F c = w-e p,
r F = t-p s,      s D = t-q r,
r e = s c = h-p q.
```

Expand both Schur products and substitute these equalities:

```text
ST = DF-D e s/q-c r F/p+c (r e) s/(p q)
   = J-w s/q-c t/p+h c s/(p q),
TS = J-w r/p-e t/q+h e r/(p q).
```

Subtract. The result is

```text
w(r/p-s/q)-(c/p-e/q)t+h(c s-e r)/(p q)
  = (w-h e/q)(r/p-s/q)-(c/p-e/q)(t-h s/q)
  = x v-u y.
```

The factorization `[x u] [v; -y]` bounds the rank by two. If both factors
have rank two, the first is injective on K² and the second surjects onto K²,
so their product has rank two. If either factor has rank at most one, so does
the product. This proves the rank-two equivalence.

If u=0, the commutator is the outer product xv. It vanishes exactly when one
factor is zero. If u!=0 and v=0, it vanishes exactly when y=0. In the remaining
case u and v are nonzero. Choose an index j with v_j!=0. Equality xv=uy
forces x=(y_j/v_j)u. Substituting and choosing a nonzero entry of u forces
y=(y_j/v_j)v. Conversely these proportionalities imply equality. This proves
the zero criterion and completes the rank trichotomy.

For completeness, P²=P implies D²=D-cr, Dc=(1-p)c,
rD=(1-p)r and rc=p(1-p). Substitution gives S²=S. Invertible block row and
column elimination takes P to diag(p,S), so rank(S)=rank(P)-1. The same holds
for Q and T. This standard single-projector step also appears in
[PR4228](https://github.com/CrocSwap/integer-mult-bounds/pull/4228) at
`bb25dcedb5bbbacd3c35359eb6b5488b087bcde6`.

## Sharp examples

Over F5 take

```text
P = [[4,3,3], [3,4,3], [3,3,4]],
Q = [[4,4,3], [2,2,2], [0,0,1]].
```

They are commuting rank-two idempotents. Their shared pivot split gives

```text
S = [[3,2], [2,3]],   T = [[0,3], [0,1]],
[S,T] = [[4,2], [3,1]],   det [S,T] = 3 != 0.
```

The input ranks, pivot admission and commutation are checked directly. One
construction is to conjugate diag(0,1,1) and diag(1,0,1) by
`G=[[1,1,1],[1,4,0],[1,0,4]]`.

Rank one also occurs over F2, for

```text
P = [[1,0,0], [0,1,0], [1,0,0]],
Q = [[1,1,0], [0,0,0], [0,1,1]],
[S,T] = [[0,0], [1,0]].
```

This is a boundary witness, not a claim that every nonlaminar pair fails.

## Evidence and reproduction

The standard-library verifier computes Schur products directly, compares the
factorization, tests the zero criterion separately and checks the rank
classification. It exhausts every admitted commuting pair in these domains:

| Domain | Input class | Pairs | Commutator ranks 0 / 1 / 2 |
|---|---|---:|---:|
| F2, m=3 | arbitrary matrices | 1,864 | 1,684 / 132 / 48 |
| F3, m=2 | arbitrary matrices | 420 | 420 / 0 / 0 |
| F2, m=3 | idempotents | 253 | 241 / 12 / 0 |
| F3, m=3 | idempotents | 2,572 | 2,188 / 384 / 0 |
| F5, m=2 | idempotents | 76 | 76 / 0 / 0 |

The idempotent domains overlap the arbitrary-matrix domains where indicated;
these are domain counts, not disjoint input counts. It also enumerates all
20,160 headers of GL4(F2) for the fixed overlapping coordinate pair with masks
3 and 5. Both pivots pass in 5,040 headers; 3,696 give commuting complements
and 1,344 give rank-one commutators. These are header counts, not counts of
distinct conjugate pairs. The sharp F5 example is a separate fixed case.

All 7,442 quadruples of short vectors in the declared F2/F3/F5 domains test
the degenerate zero criterion independently of any matrix premise. Four
controls detect the false preservation rule, an incorrect plus sign, omission
of the product-pivot correction and omission of the original commutation
premise. The receipt is generated on stdout and binds all package files by
SHA256. No generated artifact is written into the checkout.

From the repository root, using CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/schur-commutator-criterion/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/schur-commutator-criterion/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/schur-commutator-criterion
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/schur-commutator-criterion --check-source-history
```

The scientific marker is `PASS_SCHUR_COMMUTATOR_CRITERION`. Another CPython
3.12 interpreter path may replace the local path. Both scientific commands
are read-only. The historical source pins are provenance, with no external
runtime input and no pending predecessor code imported.

## Limits and code constraints

The universal claim is the written field-algebra proof. The finite census is
corroboration, not a proof for every field or dimension. Independent human and
formal proof-kernel review are unclaimed. This is one scalar deletion, with two
nonzero pivots. Noncommuting input matrices, nonfield coefficient rings,
block pivots, later-step orbit distributions and complete header-count laws
remain outside the claim. No physical saving, supplier admission, selected
cold replay or complete multiplication theorem is supplied.

The verifier has no recursive call, generated code, indirect callback chain or
external process. Its largest matrix is 4 by 4; its largest full matrix
iteration has 65,536 entries. Vector enumeration has 6,561 quadruples at most
per domain. Python and its standard library allocate dynamically; this is a
managed-runtime deviation from fixed allocation, with these fixed input and
collection bounds. Every function is below 60 physical lines. Explicit
exceptions retain all checks under `-O`. Warnings are errors. No external
static analyzer or proof kernel is required or claimed.

## Open next questions

1. Determine the simultaneous conjugacy types and their transition weights
   after deleting a pivot from a nonnested commuting pair. This criterion
   separates the commuting and noncommuting outcomes but does not give their
   full orbit data. Start with the two rank-two projectors in dimension three;
   the remaining obstacle is a classification that retains more than the
   commutator rank. Coordinate with the active corank-one counting work.
2. Extend the identity to a shared block pivot and determine its sharp
   commutator-rank bound. A bound depending only on the deleted block size
   would constrain how much noncommutativity a wider elimination step creates.
   Start by expanding the two block Schur products; scalar commutations used
   here are no longer available.

## Credit and relation to the research bottleneck

Nick Petalas's #4259 supplies the open structural question and the laminar
preservation context. Nick Petalas's #4228 supplies the existing single-request
Schur/rank framework. Cinna Davis's
[PR4100](https://github.com/CrocSwap/integer-mult-bounds/pull/4100) at
`337d04939571a637aeab54a0f58f54fde811663a` supplies the BIT request/complete-header
context. Their results are cited dependencies and context, not independently
audited here. No predecessor file or credit line is changed.

This is a side result with scope changed from `uniform-transfer-audit`: it supplies an
uncovered algebraic interface statement useful for extending shared-header
laws beyond laminar requests. The producer, header selection/emission,
dispatch, dirty return, stock and full consumer bill remain unpriced. Unknown
costs are not treated as zero, and this package starts no construction campaign.
