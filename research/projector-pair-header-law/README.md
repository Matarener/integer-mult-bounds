# Joint header law for nonorthogonal rank-one requests

This scoped counting proof gives the exact fraction of complete headers that
pass every first-pivot guard of an arbitrary finite family of rank-one
requests. The family need not be orthogonal or even distinct. For two requests
it gives an explicit law for each of seven simultaneous types. This answers
open question 1 of #4239. No new kappa or multiplication theorem is claimed.

## Result and interface

Let F be a finite field of order q and m >= 2. Write each rank-one idempotent
on F^m as `P_i = u_i v_i`, with u_i a column, v_i a row and `v_i u_i = 1`.
Request i passes header G in GL_m(F) when `(G P_i G^-1)[0,0] != 0`. This is
the interface of #4239; at rank one it is the guard of the retained
`controlled_normalizer.py:prepare` after its column reversal, whose executable
domain is odd q and rank < m. Results for q even are outside that domain.

For index sets S, T of the family, let `r_U(S)` be the rank of
`{u_i : i in S}`, `r_V(T)` the rank of `{v_j : j in T}`, and `mu(S,T)` the rank
of the Gram block `[v_j u_i]` with j in T and i in S (zero if S or T is
empty). Put `D = (q^m - 1) q^(m-1)`.

**Theorem 1 (any family).** The fraction of headers passing all k requests is
N/D, where

```text
N = sum over S,T subsets of {1..k} of (-1)^(|S|+|T|)
      * [ q^(2m-1-r_U(S)-r_V(T)) - q^(m-1-mu(S,T)) ].
```

The law depends only on these rank data. For a pairwise orthogonal family,
r_U(S)=|S|, r_V(T)=|T| and mu=|S ∩ T|, and the sum factorizes to #4239's
`J(q,m,k)`.

**Theorem 2 (two requests).** Let P != Q. Then PQ = (v_P u_Q) u_P v_Q and
`tr(PQ) = (v_P u_Q)(v_Q u_P)`. Write y = q-1. The joint count N is:

| Type | Condition | N |
|---|---|---|
| equal | P = Q | `y q^(m-2) (y q^(m-1) + 1)` |
| same image | im P = im Q, ker P != ker Q | `y q^(m-2) (y^2 q^(m-2) + 1)` |
| same kernel | ker P = ker Q, im P != im Q | `y q^(m-2) (y^2 q^(m-2) + 1)` |
| orthogonal | PQ = QP = 0 | `y^2 q^(m-3) (y^2 q^(m-2) - 1)` |
| one-sided | exactly one of PQ, QP is 0 | `y q^(m-3) (y^3 q^(m-2) + 1)` |
| generic | distinct images and kernels, tr(PQ) not in {0,1} | `y q^(m-3) (y^3 q^(m-2) + q + 1)` |
| degenerate | distinct images and kernels, tr(PQ) = 1 | `y q^(m-2) (y^3 q^(m-3) + 1)` |

The "equal" row is the single-request count of #4227/#4228. The orthogonal
row is #4239's k=2 case. The other five rows are new. The generic law does
not depend on the value of tr(PQ). Conversely tr(PQ)=1 holds in four types
with three different laws, so the trace alone does not determine the joint
law. The generic type needs q >= 3, and the degenerate type needs m >= 3.

Consequences. Every count except one is positive. The exception is the
orthogonal pair at q = 2, m = 2, already found in #4239. So any two distinct,
non-orthogonal rank-one requests share a passing header over every finite
field and every m >= 2. At q=3, m=3 the counts out of D=234 are 114
(single), 78 (same image or kernel), 44 (orthogonal), 50 (one-sided), 56
(generic) and 54 (degenerate). Against the independent value
114^2/234 ≈ 55.54, the same-image, same-kernel and generic pairs are positively
correlated there, and the other three types negatively.

## Proof

### 1. Scalar pairs

For a header G put `a = e_1^T G` (a row) and `b = G^-1 e_1` (a column), so
a b = 1 and `(G P_i G^-1)[0,0] = (a u_i)(v_i b)`. Every pair with a b = 1
occurs for exactly `|GL_(m-1)(F)|` headers, and there are D such pairs. This
equal-fiber step is #4239's step 1 and is credited there. The verifier also
checks it directly by complete conjugation on four small domains.

### 2. Inclusion-exclusion

Request i fails when `a u_i = 0` or `v_i b = 0`. Expand the product of the
indicators `[a u_i != 0][v_i b != 0]` over i. The term for (S,T) counts the
pairs with a b = 1, a in A = {a : a u_i = 0 for i in S} and b in
B = {b : v_j b = 0 for j in T}, with sign (-1)^(|S|+|T|).

Here dim A = m - r_U(S) and dim B = m - r_V(T). Let rho be the rank of the
pairing (a,b) -> a b on A x B. In adapted bases this pairing is
`a_1 b_1 + ... + a_rho b_rho`. The number of pairs with value one is therefore

```text
q^(dim A - rho) q^(dim B - rho) (q^rho - 1) q^(rho-1) = q^(dim A + dim B - rho - 1) (q^rho - 1),
```

which is zero when rho = 0. The left radical of the pairing is
A ∩ span{v_j : j in T}. A row `t = sum c_j v_j` lies in A exactly when
`t u_i = 0` for i in S. So the radical has dimension `r_V(T) - mu(S,T)`, and
`rho = m - r_U(S) - r_V(T) + mu(S,T)`. Substituting gives
`dim A + dim B - rho - 1 = m - 1 - mu(S,T)`, and the term becomes the bracket
in Theorem 1.

For an orthogonal family the u_i are independent, the v_i are independent and
the Gram matrix is the identity. The double sum then factorizes coordinatewise:
the first part gives `q^(2m-1) (1 - 1/q)^(2k)` and the second gives
`q^(m-1) (-(1 - 1/q))^k`. Their difference is `D J(q,m,k)`.

### 3. Two requests

Write c = v_P u_Q and d = v_Q u_P, so the Gram matrix is [[1, c], [d, 1]].
PQ = c u_P v_Q is zero exactly when c = 0, and QP is zero exactly when d = 0.
If im P = im Q then u_Q = lambda u_P, so c = lambda and d = 1/lambda; the
same holds for equal kernels. Hence in the first three rows c d = 1.

Put x = 1/q. The first part of Theorem 1 factorizes as
`q^(2m-1) f_U f_V`, where `f = 1 - 2x + x^r` for the rank r of the pair:
`(1-x)^2` at rank two and `1-x` at rank one. The second part is
`q^(m-1) g`, where

```text
g = sum over S,T of (-1)^(|S|+|T|) x^mu(S,T) = -1 - 2x + x^[c!=0] + x^[d!=0] + x^delta,
```

with delta = 2 when cd != 1 and delta = 1 when cd = 1. Terms with S or T empty
sum to -1. The four single-entry blocks give `2x + x^[c!=0] + x^[d!=0]`. The
four one-by-two blocks each have rank one, because they contain a diagonal 1,
and give -4x. The full block gives x^delta. Then
g = (1-x)^2 (orthogonal), -x(1-x) (one-sided), -(1-x)(1+x) (generic) and
-(1-x) (cd = 1). Evaluating `N = q^(2m-1) f_U f_V - q^(m-1) g` for each type
gives the table. The equal row is the k=1 case of Theorem 1.

A generic pair needs nonzero c, d with cd != 1, which is impossible over F2.
A degenerate pair needs a singular 2 x 2 Gram matrix between two independent
images and two independent kernels. At m = 2 these images and kernels are dual
bases, so the Gram matrix is invertible. At m >= 3 take u_P = e_1,
u_Q = e_2, v_P = e_1 + e_2 and v_Q = e_1 + e_2 + e_3 (as rows). Then c = d = 1,
and the images and kernels are distinct. The ordered-pair census below finds
every type that its domain admits.

## Evidence and reproduction

[verify.py](verify.py) is standard-library only and has no subprocesses.

- **Ordered-pair census.** For each of (q,m) = (2,2), (2,3), (2,4), (3,2),
  (3,3), (4,2), (4,3) and (5,2), it lists every rank-one idempotent, tests it
  against every scalar pair, and checks the joint count of every ordered pair
  against its Theorem 2 type. The largest case, q=4 and m=3, has 336
  idempotents and 112,896 ordered pairs. Each type found is also checked
  against Theorem 1's general formula.
- **Complete GL census.** For (2,2), (2,3), (3,2) and (4,2) it conjugates
  every idempotent by every invertible header, checks the equal pair fibers and
  compares every ordered pair with `|GL_(m-1)|` times Theorem 2.
- **Larger families.** With fixed seed 4239, it draws 40 families of three or
  four requests for each of eight (q,m,k) domains up to q=5, m=4. Half reuse an
  earlier image or kernel, so singular rank data occur. Each direct scalar-pair
  count must equal Theorem 1.
- **Controls.** Six checks reject independence on a generic pair, treating
  tr(PQ)=1 as one type, merging one-sided and orthogonal pairs, a corrupted
  count, integer arithmetic modulo four in place of F4, and a generic F2 pair.

F4 arithmetic uses F2[x]/(x^2+x+1). The case lists and counts are in the
generated [RESULT.json](RESULT.json), which also binds the exact bytes of every
package file and of the two pinned sources in [SOURCES.json](SOURCES.json).
No predecessor verifier is imported.

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/projector-pair-header-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/projector-pair-header-law/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/projector-pair-header-law
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/projector-pair-header-law --check-source-history
```

Expected marker: `PASS_PROJECTOR_PAIR_HEADER_LAW` followed by the case totals.
To regenerate the receipt, pass `--write-receipt PATH` with a new path outside
the checkout.

The verifier uses fixed case lists, no recursion and bounded loops; the
structured-request draw stops after 1,000 attempts. Every check raises an
explicit exception and stays active under `-O`. Managed Python allocation is a
documented Power of Ten rule 3 deviation: the interpreter allocates during these
bounded scans, and the fixed case sizes bound live application state.

## Limitations

- Rank one only. Higher-rank requests use leading-pivot guards that are not
  products of two linear forms, and are not covered.
- Finite fields only. #4239 gives an equal-lift argument for fixed families
  over Z/p^w; that extension is not re-proved or claimed here.
- These are algebraic header counts. Finding, emitting, dispatching or returning
  a shared header is not priced, and no actual request stream is shown to have
  any of these types. The pinned BIT.md counts per request; nothing here alleges
  an error in that recurrence.
- The finite census covers m <= 4 and q <= 5. Theorems 1 and 2 are written
  proofs for every finite field and m; human and proof-kernel review are not
  claimed.

## Open next questions

1. What is the joint full-guard law for nonorthogonal requests of rank
   greater than one? The orthogonal arbitrary-rank case is claimed separately
   in the handoff thread. Start with two rank-two requests at m = 3 or 4 over
   F3, combining #4228's Schur-complement recurrence with the
   inclusion-exclusion used here.
2. Does an actual producer emit a request family whose rank data make one
   shared header useful? Pin one producer, read off its image/kernel ranks and
   Gram blocks, and price the complete shared-header caller.

## Credit

Produced by Nick Petalas. The interface, scalar-pair reduction and orthogonal
law are from #4239 (`research/projector-joint-header-density`), and the
single-request densities from #4227 and #4228. The guard follows the retained
source527 / commdata2338 / Jose Manuel / Ross Richardson
`controlled_normalizer.py` lineage and Cinna Davis's #4100 BIT.md. New work is
Apache-2.0.
