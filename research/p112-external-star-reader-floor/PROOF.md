# One shared external query cannot lower the indicator reader bill

## Statement

Let n ports carry binary labels. Partition them into groups of positive even
size, each with binary Gram matrix I. Consecutive ports in each group form
complete Gram-I2 planes. Its alternating halves define disjoint scalar
indicator vectors v_i. Put K = sum_i v_i v_i^T.

For a vector x, cl(x) contains both ports of each plane touched by a nonzero
entry. The actual source-to-reader tariff is

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

Select any k distinct indicators a_1,...,a_k. Let m_j be the size of a_j's
complete group. Over any coefficient field F, choose arbitrary alpha_j in F
and an arbitrary vector c on all n ports. Consider the exact identity

    sum_j a_j a_j^T
      = sum_j a_j (a_j + alpha_j c)^T - (sum_j alpha_j a_j) c^T.

Then the complete additive reader bill satisfies

    sum_j C(a_j, a_j + alpha_j c) + C(sum_j alpha_j a_j, c)
      >= sum_j m_j.

The bound is sharp when zero coefficients or c=0 are allowed. No independence
or support restriction on c is needed. In particular, this covers an external
c and k+1 independent queries. Opposite halves of the same group are allowed.
The bill counts the compensating term even when it is zero.

For the literal P112 labels and PR3370 partition, applying such replacements
to disjoint subsets of indicators cannot lower the whole-K tariff of 224.
The universal statement is conditional on the stated orthonormal geometry,
which the replay checks directly for the literal fixture.

## A binary replacement preserves every old zero

Set beta_j=1 when alpha_j is nonzero and beta_j=0 otherwise. Define a binary
vector d port by port. A port belongs to at most one selected indicator. If
it belongs to a_j, set d(p)=1 exactly when alpha_j is nonzero and

    1 + alpha_j c(p) = 0 in F.

At every other port, set d(p)=0. Thus supp(d) is contained in supp(c).
Consider the same star identity over F2, with beta,d replacing alpha,c.
The jth query is a_j + beta_j d. Its support is contained in the old query's.
To check this, suppose an old query vanishes at p.

- If p belongs to a_j, alpha_j is nonzero and d(p)=1 by definition, so the
  new query is also zero.
- If p does not belong to a_j, the old query value is alpha_j c(p). Its
  vanishing means alpha_j=0 or c(p)=0. In the former case beta_j=0. In the
  latter case d(p)=0, because a cancellation equation cannot hold at c(p)=0.
  Again the new query is zero.

The compensating readers have exactly the same support. Disjointness of the
a_j supports prevents cancellation between their nonzero coefficients, so

    supp(sum_j beta_j a_j) = supp(sum_j alpha_j a_j).

All other readers are unchanged. Every new binary source/reader rectangle is
therefore a submatrix of its old binary rectangle. Deleting rows or columns
cannot increase rank, so the binary replacement costs no more than the
original F-valued star. This argument does not assert a field homomorphism.
It uses only zero constraints and the exact same star algebra.

## Expanded identity supplies the lower bound

Expand each scalar port to its two complete-plane coordinates. Replace the
scalar entry M_pq by M_pq times the binary 2-by-2 Gram block between those
planes. This is F2-linear. The expansion of K is I_(2n). Diagonal scalar
entries give I2; off-diagonal entries within an alternating half join
different orthogonal planes, and every other scalar entry is zero.

An expanded binary term u q^T factors through the rectangular binary Gram
matrix between cl(q) and cl(u), with repeated/scaled rows and columns.
Its rank is at most C(u,q). Append all untouched indicator terms to the
binary star replacement. Rank subadditivity then gives total cost at least
2n. Each untouched indicator term costs its full group size. Their total
is 2n-sum_j m_j, which proves the claimed star floor. The original F-valued
bill is no smaller by the support comparison above.

This is the expanded-identity argument of Philippe Van Velzen and PR3345.
The contribution here is the cancellation-bit reduction for an arbitrary
number of selected indicators and one shared external perturbation.

## A second support transfer and an external equality fixture

The primary checker also constructs a support-preserving replacement over
GF4=F2[w]/(w^2+w+1). Keep beta as above. At a port in a_j, map c(p) to 0 if
it is zero, to 1 if alpha_j is nonzero and 1+alpha_j c(p)=0, and to w
otherwise. Outside the selected supports, map zero to zero and nonzero to w.
This preserves the support of every query, c and the compensating reader
exactly. The star identity holds over GF4, and binary matrix rank is unchanged
by this field extension. This proves the same bound with equal support bills.
The separate checker instead uses the binary support-dominating reduction
above and imports none of the primary arithmetic.

There is a concrete four-independent-query equality example outside PR3414's
two-target scope. Take literal indicators a=v_0, b=v_2, e=v_4 and a port p
in a with a-e_p nonzero. Set alpha=(1,0,0) and c=-e_p. Queries are a-e_p,
b,e,-e_p, with readers a,b,e,-a. Their four nonempty supports are disjoint,
so they are independent over every field. The first and last source plane
sets partition a's group, giving total bill m_a+m_b+m_e. The replay prices
these actual rectangles. This equality example uses one active arm. It does
not claim equality for every external c or every all-nonzero alpha list.

## Exact overlap and scope change

PR3414, at 7b698dc958695d0a788327ddf8866b10a59e4c37, proves every independent
three-query realization of a literal two-indicator target over every field,
with arbitrary seed values and support. Its PROOF.md and README were read in
full before synthesis. The initial two-target external-star idea was already
covered and is not a new result. If that seed lies in the pair span, PR3463
at 194518404309c76b542e57efa52c0ed6e57cc48c covers it instead. No proof gap
in either source is asserted. Their exact proof hashes and public heads are
comparison receipts in SOURCES.json. They are not replay dependencies or
publication-ancestry pins; both pending commits remain outside this branch.

The uncovered continuation is k>=3 target indicators with k+1 terms and an
external query dimension. Neither predecessor quantifies over this target
and query domain. The present proof treats one explicit rank-one common
perturbation architecture, for arbitrary k and any even orthonormal partition.
It does not prove a bound for arbitrary four-query pair realizations or
arbitrary jointly recoded triples. Concurrent worker-3 research on three
target-span indicators with subset-sum query rays has a different query
domain and is not used here.

## Evidence and limits

The written zero-preservation and rank arguments prove the universal claim.
Finite fixtures corroborate the literal source binding, both transfers and
actual tariffs. They do not establish a native implementation. No supplier,
new kappa or selected-frontier change is claimed. Acquisition, coefficient
execution, frames, dirty restoration, ownership, hosting, stock, precision,
all-size/compiler admission and outer multiplication transfer remain open.
Independent human and formal proof-kernel review are unclaimed.
