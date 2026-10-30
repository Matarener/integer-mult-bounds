# Minimum-paid split trees with the least target error

This proof was produced by Nick Petalas. Apache-2.0.

## Model and statement

There are n>=1 ordered linear factors A_0,...,A_(n-1) on a normed
vector space. Each full ordered binary tree with n leaves assigns these
factors to its leaves from left to right. A node covering a consecutive
factor interval splits it into its left product B and right product A,
so its required product is AB. Every internal node uses the same four
completed-child commutator as Adam Gall's PR #2067, with a distinct dirty
connector at each depth and reuse between siblings. In chronological order,

```
positive: U, V, U^-1, V^-1
negative: V, U, V^-1, U^-1
U: z += B x
V: y += A z
```

A leaf performs one paid shear y += s A_j x, for s=+1 or -1. A negative
child is its complete inverse, including reversed chronology, not a sign
change applied to an unchanged instruction list. Source, target and all
connectors may contain arbitrary initial vectors. Sources and connectors
are restored at the ideal completed endpoint.

After every paid leaf an arbitrary additive defect is introduced at that
leaf's destination only. Each defect has norm at most epsilon. Every
ordered subset product of the factors, including the empty product, has
operator norm at most G>=1. No factor commutation is assumed.

Write P(tree) for the paid leaf count and C(tree) for the sharp universal
coefficient in the completed-target bound C(tree) G epsilon. Sharpness
means the coefficient cannot be lowered for this model: scalar identity
factors, G=1 and independent signed defects attain it. It does not mean
that an actual deterministic rounded kernel realizes independent defects.

Put

```
d = floor(log2 n), q = 2^d, k = n-q.
```

Among ALL full ordered binary trees on these n factors,

```
minimum P = 3qn - 2q^2.
```

Among precisely those trees attaining this minimum, the minimum coefficient
is

```
C_min(n) = 3^d + 2 * sum of the k smallest members of W_d,
W_d = multiset containing 2^j with multiplicity binomial(d,j), 0<=j<=d.
```

For k=0 the sum is zero. Equivalently, fill the bins j=0,1,... in order,
taking at most binomial(d,j) values of 2^j until k values have been taken.
The construction below attains both minima, uses ceil(log2 n) dirty
connectors and preserves the original factor order. The theorem concerns
this recursive commutator family, not all reversible linear programs.

## The endpoint response depends on the tree

For a leaf, P=C=1. For an internal node with left and right subtrees L,R,

```
P = 2 P(L) + 2 P(R),
C = C(L) + 2 C(R).
```

The paid recurrence counts all inverse and restoration calls. For the
response recurrence, the completed-child induction of #2067 applies to
unequal arbitrary child trees. The argument uses their endpoint contracts,
not their leaf counts or balanced shapes. A left-child destination response
reaches the parent target in exactly one of its two executions. Both
right-child destination responses reach that target. Deeper connector
responses stay in those deeper registers because each later completed
child fixes them. The same statement holds for the literal inverse order.

For completeness, a positive parent's four phases transport a left-child
target defect respectively by zero or by -A, and a right-child target defect
by the identity in each of its two phases. A negative parent's first
right-child defect stays at the target; its following positive left-child
defect reaches the target through the negative right child; the negative
right-child defect stays; its last left-child defect does not reach the
target. Signs do not change the count. Each surviving coefficient is one
signed ordered-subset monomial. Products concatenate adjacent ordered
factor intervals in their original product order. Thus the norm premise
bounds every surviving response by G.

The exact linear error identity is the sum of ideal suffix responses to
all realized defects. It remains valid when defects depend on the actual
trajectory, after fixing that trajectory. The triangle inequality gives
the stated upper bound. With scalar identity factors each nonzero response
is +1 or -1. Choosing each defect with its response sign attains C epsilon.
This also proves sharpness for every tree, in both orientations.

If a leaf has depth ell and its root-to-leaf path contains r right edges,
the recurrences give

```
P = sum_leaves 2^ell,
C = sum_leaves 2^r.
```

Expanding an internal position of right-edge weight w replaces a leaf of
weight w by leaves of weights w and 2w. Hence its increase in C is 2w.
These are response counts, not a bound on scratch error or interior growth.

## Exactly which trees minimize paid calls

Suppose a tree has a shallow leaf at depth a and a deepest cherry whose
two leaf children have depth b>=a+2. Such a cherry exists by maximality of
b. Expand the shallow leaf into a cherry and collapse the deepest cherry.
The number of leaves is unchanged and the paid count changes by

```
(2^(a+2)-2^a) + (2^(b-1)-2^(b+1))
= 3(2^a-2^(b-1)) < 0.
```

The operation produces another full ordered tree. Its leaves can still be
assigned the same ordered factors from left to right; no product is
permuted. Therefore a minimum-paid tree cannot have leaf depths differing
by two or more.

For a full binary tree, Kraft equality is sum_leaves 2^(-ell)=1. Leaves
whose depths differ by at most one must consequently lie at depths d,d+1
for nonpowers n, with q-k shallow leaves and 2k deep leaves. At a power of
two every leaf has depth d. Conversely all such trees exist and have the
same paid count

```
(q-k)q + (2k)(2q) = q^2+3qk = 3qn-2q^2.
```

The exchange strictly decreases an integer paid count whenever the depth
condition fails, so every other tree has larger P. Existence and this
strict condition prove both minimality and the characterization.

## Minimize the target coefficient without paying more

Every minimum-paid tree starts with the perfect depth-d tree. It expands
exactly k of that tree's q leaves into cherries. Each depth-d path is a
binary string of length d; its right-edge weight is 2^(Hamming weight).
There are binomial(d,j) paths of weight 2^j. The unexpanded perfect tree
has coefficient (1+2)^d=3^d, and expanding a path of weight w adds 2w.

Every subset of k bottom paths is a valid full ordered tree. Therefore
the least possible coefficient is obtained by choosing the k smallest
weights, giving the formula. Equal-weight ties are arbitrary. Label the
resulting leaves by A_0,...,A_(n-1) in order and emit the four phases at
each internal node. This is an explicit attaining word, restores the
arbitrary dirty connectors in the ideal model and uses no extra depth.

## First strict improvements and a necessary boundary

The source's floor-left/ceiling-right tree on n=3 has P=10 and C=7.
The tree with two factors on the left and one on the right has the same
ten calls and two dirty connectors, but C=5. This is already strict.
For n=5 the optimum is C=11 instead of 17, retaining 28 paid calls and
three connectors. For n=63 it is C=665 instead of 727, retaining 4,000
paid calls and six connectors.

This is a minimum at fixed minimum P. Dropping that condition changes the
answer: at n=4 a left comb has C=7 but P=22, whereas the minimum-paid tree
has C=9 and P=16. The theorem makes no unrestricted target-error optimum
claim and supplies no cost-free improvement to arbitrary caller contracts.
