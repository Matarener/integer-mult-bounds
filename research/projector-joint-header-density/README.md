# Exact joint header law for orthogonal rank-one requests

This scoped counting proof determines the exact dependence between rank-one
first-pivot guards that share a complete header. It also determines the full
success-count distribution and the minimum number of headers needed to cover
an orthogonal rank-one family. No new kappa or multiplication theorem is claimed.

## Result and interface

Let F be any finite field of order q. Let P_1,...,P_k be rank-one idempotents
on F^m, with P_i P_j = 0 for every i != j, and 1 <= k <= m. A request passes
header G in GL_m(F) when `(G P_i G^-1)[0,0] != 0`. The exact fraction passing
every request is

```text
J(q,m,k) = (q-1)^k [q^(m-k)(q-1)^k - (-1)^k] / [q^k(q^m-1)].
```

Set J(q,m,0)=1. No independence assumption is used. For example, at q=3,m=2,
one request passes 7/12 of headers, while two orthogonal requests both pass
1/6, which differs from `(7/12)^2`.

For a complete resolution `P_1+...+P_m=I`, let S be the number of passing
requests. Write `D=(q^m-1)q^(m-1)`. Its exact distribution is

```text
Pr(S=s) = binom(m,s)(q-1)^s [(q-1)^s-(-1)^s](2q-1)^(m-s) / (q D),
          0 <= s <= m.
```

In particular, over F2, only odd success counts occur and
`Pr(S=s)=binom(m,s)3^(m-s)/D` for odd s. All requests can share one passing
header except when q=2, k=m and m is even. Exactly two headers suffice in
that exceptional case. These are algebraic header counts and existence results;
they do not price finding, emitting, dispatching or returning those headers.

The retained `controlled_normalizer.py:prepare` reverses projector columns,
then uses its northeast pivot `a[0][m-1]`. At rank one this is precisely P[0,0].
Its executable domain requires an odd q and rank < m. The F2 statements here
extend the same guard algebra and are outside that source's admitted domain.
The pinned BIT.md explicitly says to count per request, rather than intersect
all requests. This theorem concerns a changed shared-header proposal and does
not identify an error in that recurrence. No claim is made that its actual
request stream forms an orthogonal rank-one family.

## Proof

### 1. Reduce to coordinate projectors and uniform scalar pairs

Choose a nonzero u_i in each image. Since P_i is rank one, write P_i=u_i v_i,
with v_i u_i=1. Orthogonality implies v_i u_j=0 for i != j. These vectors are
independent. The sum of the P_i is an idempotent of rank k; complete its image
basis with a basis of its kernel. In this basis, P_i=E_ii. Changing that fixed
basis permutes the complete GL header domain, preserving all fractions.

For a header U in that basis put `a=e_1^T U` and `b=U^-1 e_1`. Then a.b=1,
and `(U E_ii U^-1)[0,0]=a_i b_i`. Every ordered pair a,b with a.b=1 occurs.
Indeed take a as the first row of U and any ordered basis of the hyperplane
`b^perp` as the remaining rows. These rows are independent because a.b=1.
They give U b=e_1, as required. Each pair has exactly
`|GL_(m-1)(F)|` such headers, independently of the pair; use |GL_0|=1.
There are D such pairs: choose any nonzero a, then one of q^(m-1) vectors b.

### 2. Count nonzero sums

Let T_k be the number of ordered k-tuples of nonzero field elements with
sum one. T_0=0. For a partial tuple of length k-1, its last entry is forced;
it fails to be nonzero exactly when the partial sum was one. Thus

```text
T_k = (q-1)^(k-1) - T_(k-1) = [(q-1)^k - (-1)^k]/q.
```

This uses only field addition and holds for every finite-field order.

### 3. Count a prescribed simultaneous-good set

Put d=m-k. Suppose d>=1. Requiring a_i b_i != 0 for the first k coordinates
forces their a_i to be nonzero. If the remaining a coordinates are zero,
there are `(q-1)^k T_k q^d` pairs. If those coordinates are not all zero,
there are `(q-1)^(2k)(q^d-1)q^(d-1)` pairs. The last factor counts the
solutions of one nonzero linear functional, for each choice of the first
k b coordinates. Their sum is

```text
G_k = (q-1)^k q^(d-1) [q^d(q-1)^k - (-1)^k].
```

Divide by D to obtain J. If k=m, choose the m nonzero a coordinates and
the products whose sum is one. The count is `(q-1)^m T_m`; this gives the
same displayed fraction without a negative-exponent counting argument.

### 4. Count every success pattern and the minimum cover

For a specified set of s successful coordinates in a complete family,
choose their nonzero products with sum one in T_s ways. Each nonzero
product has q-1 realizations as a_i b_i. Each zero product has 2q-1
realizations, including `(0,0)` once. Choosing the successful set gives
the displayed distribution. In F2 the sum-one condition is exactly odd
support size. Every odd support set is realized by a scalar pair and
therefore by a header, by step 1.

J is positive for k<m. At k=m it vanishes exactly when
`(q-1)^m=(-1)^m`, equivalently q=2 and m even. In that case a header with
the first m-1 requests passing and another with the final request passing
cover all m requests. Both exist because their prescribed support sets
have odd size. No single header works, proving the exact cover number two.
For q>2 or odd m over F2, J(q,m,m)>0, so one header suffices.

For a fixed orthogonal family of split rank-one projectors over Z/p^w,
the guard depends only on reduction modulo p. Every GL_m(F_p) header has
exactly p^(m*m*(w-1)) invertible lifts. Consequently complete equally
weighted lift packets have the same joint fractions. The low family must
be fixed across the packet. This does not cover arbitrary restricted or
unequally weighted headers, nor changing projectors selected from the header.

## Evidence and reproduction

[verify.py](verify.py) implements two finite enumerators. The scalar-pair
census checks every prescribed subset and every success-count bin. The separate
complete-matrix census inverts each admitted header and checks its pair fiber
size, joint counts and success distribution. F4 arithmetic uses
`F2[x]/(x^2+x+1)`, independently of integer arithmetic modulo four.
The precise case lists and counts are in the generated [RESULT.json](RESULT.json).
Source pins are in [SOURCES.json](SOURCES.json); no predecessor verifier is imported.
The replay also constructs actual one-or-two-header covers in dimensions 2
through 12 over F2, F3, F4 and F5. Six controls distinguish independence,
even binary support, omitted zero-product multiplicity, duplicated requests,
integer arithmetic modulo four and a corrupted count.

The constructor in step 1 is explicit: choose j with b_j != 0 and use
`e_i-(b_i/b_j)e_j` for the remaining rows, for every i != j. In the exceptional
binary case choose a=b with support of size m-1, then support the last
coordinate. For odd m, a is all ones and b consists of pairs 1,-1 followed
by 1. For even m over q>2 use those pairs followed by x,1-x, where x is
neither zero nor one. All these pairs have scalar product one.

The verifier has fixed finite case lists, no recursion and no subprocesses.
Each full matrix scan has at most 262,144 candidates; each pair scan has
at most 65,536 candidates. Vector tables have at most 256 entries and
the largest retained pair-fiber dictionary has 1,008 keys. Formula-control
dimensions stop at 128; explicit cover dimensions stop at 12. All functions
fit below 60 physical lines. Checks use explicit exceptions and stay active
under optimization. Managed Python allocation is a documented Power of Ten
rule 3 deviation: the interpreter allocates during these bounded scans.
The fixed input sizes and collection capacities bound live application state;
interpreter/library internals are not allocation-instrumented. A fixed-storage
native replay would be needed if this verifier became a production kernel.

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/projector-joint-header-density/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/projector-joint-header-density/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/projector-joint-header-density
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/projector-joint-header-density --check-source-history
```

Any CPython 3.12 executable may replace the local interpreter path. The verifier
recomputes the receipt, including hashes of its five package files
and both live inputs. To create a candidate receipt, use `--write-receipt`
with a new path outside the checkout. It refuses to overwrite an existing file.
The receipt excludes its own bytes to avoid a circular hash dependency.

The universal claim rests on the written proof. The finite checks do not supply
independent human review or a proof-kernel theorem. No selected cold replay,
GL64 enumeration, general higher-rank joint law, physical header compiler,
fallback repricing, stock, precision or outer multiplication proof was run.
The prime-power lift statement is proved by equal fibers; finite enumeration
of those lifts is not included in this package.

## Open next questions

1. Determine the joint guard law for two nonorthogonal rank-one requests.
   Start by classifying the pair under simultaneous conjugation, retaining
   `tr(PQ)` and image/kernel intersections. This decides whether any useful
   shared-header model applies outside an orthogonal family. No caller is bound.
2. Extract a fixed orthogonal request family from an actual producer and price
   the entire shared-header schedule. Include header selection, dispatch,
   returned dirty state and stock. Existence of one or two algebraic headers
   leaves each of those physical costs unknown.

## Credit and scope

This package was produced by Nick Petalas. Apache-2.0. Source527, commdata2338
and Jose Manuel retain the normalizer and recursive-closure credit. Cinna Davis
supplies the pinned BIT.md per-request context; Chris R / Clear1nsight's #3950
supplies earlier deterministic counting context. Nick Petalas's #4227 at
`3d793eade8de2ba49ec08f8d004c1b2f566a78e6` and #4228 at
`bb25dcedb5bbbacd3c35359eb6b5488b087bcde6` supply the exact marginal laws.
This work extends them to simultaneous orthogonal requests; it does not
independently audit them. The k=1 formula specializes to their rank-one law.
The unchanged selected-source notices retain their full lineage.
Independent human and formal proof-kernel review are unclaimed.
