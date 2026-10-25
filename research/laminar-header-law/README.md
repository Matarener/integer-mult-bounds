# Exact full-guard header law for laminar projector families

This scoped counting proof answers a nonorthogonal subcase of
[#4246's first open question](https://github.com/CrocSwap/integer-mult-bounds/pull/4246).
For a hierarchy of nested projectors with orthogonal siblings, the fraction
of complete headers passing every full guard is the product of the known
orthogonal-family laws at each branch. In particular, conditioning on a
containing projector's full guard gives the same internal joint fraction as
working inside its image. No independence assumption is needed.

The new step is preservation of containment under Schur deletion. The
orthogonal-family law and its Schur-orthogonality step are predecessor results
from Nick Petalas's #4246; they are used as cited inputs, not re-audited here.
This is a scoped proof with finite corroboration, not a supplier admission,
a new kappa or a complete multiplication theorem.

## Statement

Work over any finite field F_q. A finite family of distinct nonzero idempotents
on F_q^m is **laminar** if each pair is either orthogonal, or one is contained
in the other. Here P is contained in Q when PQ=QP=P, and orthogonality means
PQ=QP=0. These algebraic relations include the kernels as well as the images.
The requests are fixed before the header is selected.

Put the family in a forest ordered by containment. Siblings are the maximal
proper contained members of their parent. Add an unguarded virtual root of
rank m whose children are the maximal requests. A full-rank identity request,
if present, is a separate guarded child of that root and passes automatically.
Write d_v for a node's rank and C(v) for its children. Leaves contribute one.

Let O(q,n; s_1,...,s_k) be the exact orthogonal-family fraction from
[#4246 at a2d99d73bf21b39fbb0a9a88917424ff26c2e63c](https://github.com/CrocSwap/integer-mult-bounds/blob/a2d99d73bf21b39fbb0a9a88917424ff26c2e63c/research/orthogonal-chain-header-law/README.md).
For clarity its formula is reproduced here. For positive ranks s in dimension n,

```text
F(q,n;s) = prod_i(q^s_i-1) * [(q-1)^k q^(n-sum s_i) - (-1)^k]
           / [q^k (q^n-1)],
O(q,n;s) = prod_(t=0..max(s)-1) F(q,n-t;(s_i-t : s_i>t)).
```

Both functions equal one for an empty rank tuple. A request P of rank r passes
G in GL_m(F_q) when every leading principal minor of GPG^-1 of sizes 1 through
r is nonzero. The exact fraction of headers passing the whole laminar family is

```text
L(q,m; family) = prod_(v including virtual root) O(q,d_v;(d_c : c in C(v))).
```

This is a product of conditional fractions, not of individual request marginals.
All counts use the complete equally weighted GL_m cover.

For a single contained family P_1,...,P_k inside Q of rank r, with the P_i
pairwise orthogonal, this reads

```text
Pr(Q and all P_i pass) = A(q,m,r) * O(q,r;(rank P_i)),
A(q,m,r) = O(q,m;(r)).
```

Thus the conditional internal fraction does not depend on the ambient dimension
m. With one contained rank-one P it is

```text
Pr(P passes | Q passes) = (q-1)*[(q-1)q^(r-1)+1] / [q(q^r-1)].
```

At q=3,m=3,r=2 the joint fraction is 343/1404. Independent marginals instead
give 931/4563. A different example exposes an internal obstruction: over F2,
a rank-two Q and its two complementary rank-one subrequests have joint fraction
zero even in ambient dimension three. The obstruction is inside Q's image.

**Existence criterion.** A common passing header exists except when q=2 and
some node has a nonempty even number of children whose ranks sum to its rank.
This follows from #4246's zero criterion on each factor. It applies at every
internal node as well as at the virtual root.

## Proof

1. **One simultaneous orbit.** Commuting idempotents split the space into their
common zero/one eigenspaces. For this family, the atoms are the complement of
the maximal requests and, at each request, the intersection of its image with all its children's
kernels. Their dimensions are m minus the maximal ranks' sum, or d_v minus its
children's ranks' sum. Choose bases in these atoms. Every request becomes the
coordinate projector on its subtree. Therefore families with the stated tree
and ranks form one simultaneous GL_m conjugacy orbit. Right translation of
the complete header cover permits this coordinate form.

2. **First-stage factorization.** Put x=e_1^T G and y=G^-1 e_1. The pairs with
xy=1 have equal completion counts, as in #4228 and #4246. The first pivot of
a coordinate projector is the dot product of x and y restricted to its block.
For a block with nonzero dot product z, conditional on z its restricted pair is
uniform among pairs with that dot product. Multiplying its y vector by z^-1
maps it bijectively to the uniform dot-one pair. Every internal pivot scales
by z, so nonvanishing is unchanged. Conditional on all block dot products,
different blocks are independent. Consequently, conditional on a parent's
pivot being nonzero, the children's first-pivot probability is precisely
F(q,d_parent; child ranks), independent of the pivot's value and of the
outside coordinates. Starting with the virtual dot-one block and proceeding
down the tree gives the product of F over all nodes.

3. **Schur deletion preserves containment.** Write nested idempotents as

```text
P = [[a,b],[c,D]],   Q = [[alpha,beta],[gamma,E]],
S = D-c*b/a,        T = E-gamma*beta/alpha,
```

where a and alpha are nonzero. From PQ=P,

```text
DE = D-c*beta,  D*gamma = c*(1-alpha),
bE = b-a*beta,  b*gamma = a*(1-alpha).
```

Expand the product and substitute those four identities:

```text
ST = DE - D*gamma*beta/alpha - c*bE/a + c*(b*gamma)*beta/(a*alpha)
   = D-c*beta - c*(1-alpha)*beta/alpha - c*b/a + c*beta
       + c*(1-alpha)*beta/alpha
   = S.
```

Applying the same calculation to P^T Q^T=P^T gives TS=S. The single-request
Schur lemma from #4228 gives S^2=S, T^2=T and ranks one smaller. The orthogonal
Schur lemma from #4246 preserves zero products between siblings and unrelated
branches. Therefore deletion preserves the whole laminar family, reducing all
positive ranks by one and discarding zeros. The remaining leading minors are
the corresponding Schur leading minors times the nonzero first pivot.

4. **Uniformity and induction.** Left multiplication of G by diag(1,K)
preserves all first pivots and conjugates every Schur complement by K. On the
event that all first pivots pass, the remaining tuple therefore has a
GL_(m-1)-invariant distribution. Step 1 makes its support one orbit of the
reduced tree and ranks. Hence it is uniform on that orbit. Induction on the
maximum request rank yields a product over stages t and nodes v of
F(q,d_v-t;(d_c-t : d_c>t)). Interchange the finite products. Each node's stage
product is exactly O(q,d_v; child ranks), proving the formula. Empty or
zero-probability stages cause no conditional-distribution inference.

5. **Zeros.** All factors are nonnegative fractions. The predecessor zero
criterion for O is exactly q=2, a complete positive-rank family and even
cardinality. Applied at each node it gives the stated necessary and sufficient
criterion. A positive finite header count supplies existence, without pricing
header selection or emission.

## Evidence and reproduction

The standalone standard-library verifier enumerates complete GL header sets and
computes every principal-minor guard directly, without using Schur recursion.
It counts all 1,056 laminar coordinate families across 213,714 headers in
eight domains: F2 in dimensions 2, 3, 4; F3 and F4 in dimensions 2, 3; and F5
in dimension 2. This includes empty families and identity requests. The verifier
checks 181,836 Schur-containment cases, each in both directions. It counts
the all-pass events via a superset sum on the measured passing sets. Each subfamily of a
laminar family is laminar, so these counts also determine its full passing-set
law by inclusion-exclusion. Every predicted fraction and the zero criterion are
compared with the direct counts. The new Schur-containment identity is also
checked on named nontrivial rank-two/rank-three/rank-four pairs.

F4 is F2[x]/(x^2+x+1). The verifier checks an actual nonlaminar commuting pair
whose Schur complements cease commuting. This prevents extending the proof to
all commuting idempotents. One witness over F3 has

```text
G = [[0,1,1],[0,0,1],[1,1,0]],
P = G diag(1,1,0) G^-1,  Q = G diag(0,1,1) G^-1,
S = [[0,0],[0,1]],      T = [[1,0],[2,0]],
ST = [[0,0],[2,0]],     TS = [[0,0],[0,0]].
```

Both first pivots are one. Further controls distinguish independence,
orthogonality in place of containment, the internal F2 obstruction, its
odd-field positive counterpart, and F4 multiplication from integers modulo four.

From the repository root, with any CPython 3.12:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/laminar-header-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/laminar-header-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/laminar-header-law
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/laminar-header-law --check-source-history
```

The generated stdout receipt starts with `PASS_LAMINAR_HEADER_LAW` and binds
every package file's SHA256 to the enumerated results. No receipt is handwritten
and the verifier writes no files. Fixed domains bound each candidate scan by
262,144 matrices and each family table by 32,768 entries. Functions fit within
60 lines and use no recursion or subprocesses. Explicit exceptions keep checks
active under -O. Managed Python allocation during bounded scans is a Power of
Ten rule 3 deviation; field sizes and dimensions are fixed, not public inputs.

## Limitations

The universal result rests on the written argument and the cited predecessor
orthogonal-family theorem. The enumerations are finite corroboration, not a
proof-kernel check. General overlapping commuting families, noncommuting
families, prime-power rings, weighted or incomplete header sets, and adaptive
requests are outside scope. Header selection/emission/dispatch, dirty return,
stock, actual producer families, supplier admission and outer multiplication
costs remain unpriced. No selected replay or formal build is run.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. Determine the joint full-guard law for two commuting projectors with a
proper nonzero intersection and neither containing the other. The verifier's
nonlaminar witness shows that commutativity alone does not survive deletion.
Start with two rank-two projectors in dimension three and classify their
Schur pair's changing invariants. A replacement orbit description is missing.
2. Find an actual request producer with a laminar family and price a complete
shared-header caller. The conditional counts identify possible sharing but
supply no physical savings. Start with one fixed producer's complete rank tree;
selection, dispatch, restoration and stock remain obligations.

## Related work and credit

This package was produced by Nick Petalas. It builds on Nick Petalas's
[#4246](https://github.com/CrocSwap/integer-mult-bounds/pull/4246), exact head
`a2d99d73bf21b39fbb0a9a88917424ff26c2e63c`, for the orthogonal law, its zero
criterion and Schur-orthogonality lemma; and
[#4228](https://github.com/CrocSwap/integer-mult-bounds/pull/4228), exact head
`bb25dcedb5bbbacd3c35359eb6b5488b087bcde6`, for equal-fiber counting and
single-request Schur deletion. These are mathematical dependencies, not runtime
imports or declared foreign Git-history dependencies.
[#4239](https://github.com/CrocSwap/integer-mult-bounds/pull/4239) is the
rank-one orthogonal predecessor.
[#4240](https://github.com/CrocSwap/integer-mult-bounds/pull/4240), exact head
`9f9c89ed75e9fdae6b6762925b080fb308824858`, counts nonorthogonal rank-one
families at one stage; this result counts full chains with nested higher ranks.
Cinna Davis's #4100 BIT.md supplies the request context. Apache-2.0.
