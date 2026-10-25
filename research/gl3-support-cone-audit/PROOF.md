# Independent universal support-cone oracle

This implementation was constructed from the supplied mathematical contract.
No predecessor model, checker, source code, or other implementation was read.
The implementation enumerates the group using ordered independent columns,
then serializes every element as a literal tuple of its three row masks.

## Definitions and order

Let `G = GL_3(F_2)`. Matrices act on column vectors. The product `a*b`
applies `b` first and then `a`. The six generators are
`g_ij = I + e_i e_j^T`, for `i != j`. Each is an involution.
Let `B_k` be the set of products of at most `k` generators.

The algebra is `M_3(F_2[G])`. A coefficient is an element of the free group
algebra, represented by its exact parity set of group basis elements.
Binary matrices embed into this algebra using the identity group element.
The legal factors are

`F(g,N) = I + (g + 1)N`,

where `N = u v^T`, `u,v != 0`, and `v^T u = 1`. There are 28 such `N`.
For each factor, the group-algebra support of every entry is contained in
`{1,g}`. Also `F(g,N)^2 = I`: in characteristic two the cross terms vanish,
and `(g+1)^2 = g^2 + 1 = 0`. The binary entries of `N` commute with group
basis elements. This argument is valid in the complete formal group algebra.

## Universal forward and backward cones

Write an attaining word in time order as `A_1,...,A_n`, with every `A_j`
a legal factor. New calls multiply on the left. Suppose

`D = A_n ... A_1 = diag(T_0,T_1,T_2)`.

At cut `t`, put `P_t = A_t ... A_1` and
`Q_t = A_n ... A_(t+1)`. Thus `D = Q_t P_t`.

Forward expansion of `P_t` selects, in each summand, either the identity
or the generator from each of at most `t` factors. Register summation and
characteristic-two cancellations cannot create new group basis elements.
Every coefficient support of `P_t` is therefore contained in `B_t`.

The inverse of the suffix is, in the **reversed multiplication order**,

`Q_t^-1 = A_(t+1) ... A_n`,

because each factor is its own inverse. Its entries have support in
`B_(n-t)`. Since `P_t = Q_t^-1 D` and `D` is diagonal,

`(P_t)_(r,c) = (Q_t^-1)_(r,c) T_c`.

Consequently, for every row `r` and column `c`,

`supp((P_t)_(r,c)) subset B_t intersect (B_(n-t) * T_c)`.

The multiplication by `T_c` occurs on the **right**, as forced by the
matrix product `Q_t^-1 D`. No commutativity or order change is used.
This is a universal necessary condition; an allowed set is an exact
evaluation of this cone formula, not a claim that every allowed basis
element occurs in an attainable word. Endpoint off-diagonal zeros may
impose stronger constraints than this uniform cone.

No free-mixing normalization, complete circuit model, SAT conclusion,
minimal attaining length, proof replay, Lean theorem, or native admission
is asserted.

## Exact computation and independently checkable certificates

The group is enumerated by choosing nonzero column `a`, column `b` outside
`span(a)`, and column `c` outside `span(a,b)`. This gives
`7 * 6 * 4 = 168` distinct matrices. Closure is checked for all ordered
pairs. Breadth-first traversal from the identity under left multiplication
by all six generators computes the exact shortest distances. Each stored
shortest word is replayed, and every Cayley edge satisfies the distance
Lipschitz bound. Since every element has a word of its assigned length,
and along any word the distance can increase by at most one per edge,
these certificates independently prove the assigned distances are exact.

Distance layers have sizes `1,6,24,51,60,24,2`; the diameter is 6.
The cumulative ball sizes are `1,7,31,82,142,166,168` and remain 168.

The full canonical JSON contains every support row for `n=7,8`, every
cut `t=0,...,n`, all three matrix rows, and all three columns, for the
fixed targets `(1,4,3)`, `(2,4,3)`, `(1,2,4)`. There are 153 rows.
Every allowed-support map is keyed by a literal row tuple `(a,b,c)`;
there are no implementation-specific group labels.

Two distinct edge conventions are serialized with explicit definitions:

* BFS frontier edges are all directed generator edges that increase
  shortest distance by one. There are 378.
* Cut frontier edges are allowed group-level paths from one cone to the
  next, using a stay or a left generator step. They include columns but
  do not duplicate the identical universal group cone over matrix rows.
  There are 2,362 for length 7 and 4,660 for length 8. They do not assert
  realizable register transitions or ignore possible parity cancellation.

Canonical JSON uses ASCII, sorted object keys, and comma/colon separators.
Each count and hash convention is stated in the data. Hashes of the
ordered full support rows, BFS edges, and cut edges are included.

## Noncommuting legal positive witness and translation defect

Let `N=e_0 e_0^T`, `a=g_01=(3,2,4)`, and
`b=g_12=(1,6,4)`. In the complete algebra,

`F(a,N) = diag(a,1,1)`,
`F(b,N) F(a,N) = diag(b*a,1,1)`.

The target is `T=b*a=(3,6,4)`. The cut-one active coefficient has exactly
the support `{a}`. It belongs to `B_1*T`, since `b*T=a`. It does not
belong to `T*B_1`: the required element is `T^-1*a = a*b*a = (5,6,4)`,
which is neither the identity nor one of the six generators.
This is an actual legal two-call attaining word in `M_3(F_2[G])`.
The two dirty registers are exactly restored. It is not only a check of
the underlying three-by-three group product.

The code performs exact parity-set algebra multiplication at every
prefix and additionally executes the factors on all 504 basis inputs
of the three-register regular module. By linearity these checks cover
arbitrary inputs, including simultaneous arbitrary dirty registers.

Further positive diagnostics include a six-call word that temporarily
acts on both dirty registers and restores them, a mixed-register legal
two-call cancellation with off-diagonal intermediate coefficients, and
a nine-call word that attains the fixed target diagonal. All prefixes
satisfy the correct cones. The nine-call example is an upper-bound
witness only and makes no claim about lengths seven or eight.

All 168 legal factors (six generators times 28 rank-one idempotents)
are checked both by exact algebra squaring and by twice applying each
factor to each of the 504 regular-module basis inputs: 84,672 checks.

## Run

Use Python 3.12:

```
python3.12 -W error oracle.py --output ORACLE.json
python3.12 -O -W error oracle.py --output ORACLE.optimized.json
```

Without `--output`, only the compact result receipt is printed and no
files are written. There are no assertions whose removal could alter
the checks under optimization. Normal and optimized canonical outputs
are required to be byte-identical in the freeze receipt.
