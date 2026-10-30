# Sharp binary off-diagonal pool cardinality

This scoped proof was produced by Nick Petalas. Apache-2.0.
Independent human and formal proof-kernel review are unclaimed.

## Model and theorem

Let W>=1, and let V be a d-dimensional linear subspace of the zero-diagonal
matrices in M_W(F2). Write off(N) for N with its diagonal deleted. Define

```
P(V) = {N : rank(N)=1, N^2=N, off(N) in V, off(N)!=0}.
```

These are scalar projectors, with no rational address frames or word order.
In particular, coordinate projectors do not belong to P(V).
Let R(V) be the nonzero elements of V which occur as off(N), and let e(V)
count the matrix units E_ij in V with i!=j.

**Theorem.** For every W and V,

```
|P(V)| = |R(V)| + e(V) <= 2^d + d - 1.
```

For every d>=1 and W>=d+1, some V attains equality. For d=0 the pool is
empty. Thus the maximum over all ambient register counts is exactly
2^d+d-1. This does not assert attainment at every smaller feasible W.

## 1. All fibers of diagonal deletion

**Lemma.** A realizable nonzero off-diagonal pattern has exactly one
rank-one-idempotent lift, except when it is a matrix unit E_ab with a!=b.
That pattern has precisely the two lifts

```
E_aa + E_ab = e_a (e_a+e_b)^T,
E_bb + E_ab = (e_a+e_b) e_b^T.
```

To prove this, suppose distinct rank-one idempotents N and M have the same
off-diagonal pattern. Then D=N+M is a nonzero diagonal matrix of rank at
most two. A rank-one idempotent has trace one, so trace(D)=0 in F2.
The number of nonzero diagonal entries of D is therefore even and at most
two. It is exactly two, at positions a and b.

Write N=x y^T and M=u v^T, with y^T x=v^T u=1. The rank-two image of D
is contained in span(x,u), so that span equals span(e_a,e_b). Applying the
same argument to D^T puts y and v in span(e_a,e_b). Both projectors are
therefore supported on the same two-by-two coordinate block, and differ
there by the identity.

For completeness, the rank-one idempotents on that binary block are

```
[[1,0],[0,0]], [[0,0],[0,1]],
[[1,1],[0,0]], [[0,1],[0,1]],
[[1,0],[1,0]], [[0,0],[1,1]].
```

This list follows by taking nonzero x,y in F2^2 with y^T x=1.
The only repeated nonzero off-diagonal patterns are the two single edges.
Their displayed lifts work in every ambient dimension. Any third lift
would, by the same argument with N, have to be in this list. This proves
the lemma. The zero pattern has the W coordinate projectors as its lifts;
its exclusion is essential.

woklerx's PR1456 already proves uniqueness for cyclic patterns. The lemma
retains that conclusion and treats every acyclic pattern and every
ambient dimension as well. The rank and trace facts are standard linear
algebra, not new methods claimed here.

## 2. Exact count and upper bound

Every pattern in R(V) contributes one projector. By the lemma, the only
extra projectors are one additional lift for each E_ij in V. All these
matrix units are realizable, so the exact count is |R(V)|+e(V).

There are at most 2^d-1 nonzero vectors in V. Distinct off-diagonal matrix
units are linearly independent, since they have disjoint one-entry
supports. A d-dimensional V consequently contains at most d of them.
The asserted upper bound follows.

One consequence useful before a scalar-pool search is

```
dim(sum_{N in P(V)} im(N)) <= |P(V)| <= 2^d+d-1.
```

The joint image is invariant under every projector in the pool. If the pool
is nonempty and W>2^d+d-1, it is a nonzero proper common invariant subspace.
This is a necessary restriction on the pool alone. Adding coordinate
projectors or other patterns to a chronological word can invalidate this
particular invariant subspace.

## 3. A family attaining the bound

Use coordinates 0,1,...,d, padding by arbitrary further coordinates if
W>d+1. Let

```
V = span(E_01, E_02, ..., E_0d).
```

For every nonempty subset J of {1,...,d}, the projector

```
N_J = e_0 (e_0 + sum_{j in J} e_j)^T
```

has off-diagonal pattern sum_{j in J} E_0j. Thus all 2^d-1 nonzero patterns
in V are realized. Exactly d of them are single edges, and their second
lifts are (e_0+e_j)e_j^T. These projectors are distinct and give precisely
2^d-1+d elements of P(V), proving sharpness. The fiber lemma excludes
additional lifts on padded coordinates.

## Scope and predecessor boundary

PR1456's open question asks for further pattern-space classification at
relation nullity two. This result gives an exact all-dimension size bound
before such a classification. PR1846's four-role flag and reducibility
census is cited context, not a dependency of this proof and not replayed.
Neither its flags nor any predecessor count is used above.

The field is specifically F2. For example, over F7 the distinct matrices
[[3,1],[1,5]] and [[5,1],[1,3]] are rank-one idempotents with the same
two-edge cyclic pattern, so the fiber lemma does not carry over unchanged.
The finite verifier checks this boundary literally.

No rational-frame feasibility, two-relation word, native implementation,
physical restoration, full cost invoice, supplier admission, improved kappa
or complete multiplication theorem follows from this scalar count. The
finite checks corroborate the written proof and do not establish its
unbounded quantifiers by enumeration.
