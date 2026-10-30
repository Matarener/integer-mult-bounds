# Arbitrary mixed pair queries: four-direction reduction and sharp literal tariff

## Exact statement and model

Fix the 112 binary labels in the pinned `DATA-PHASES.json` and the sixteen
orthonormal groups in Tekalign's PR3370 certificate. Consecutive ports of each
group form its complete planes. The two alternating halves of each group give
32 disjoint indicator vectors. Choose two distinct indicators `a,b`, from
groups `G_A,G_B` of sizes `m_A,m_B`. They may be the two halves of one group.

For any scalar vector `v`, `cl(v)` is the union of the complete planes touched
by its nonzero coordinates. The coefficient field `F` is arbitrary. The tariff
is **binary rectangular rank**, irrespective of `F`:

    C(u,q) = rank_F2 Gram(cl(q),cl(u)),
    Gram(P,Q)[p,q] = parity(label[p] & label[q]).

Consider any finite exact realization

    aa^T + bb^T = sum_i u_i q_i^T,    q_i = x_i a + y_i b.

The `u_i` are unrestricted vectors on all 112 ports. They can have cancellations
outside the target. Query count, repetitions, projective directions and
coefficients are unrestricted. Then

    sum_i C(u_i,q_i) >= m_A + m_B.

The two literal axis terms attain equality over every field. Thus disjoint
pair replacements of the literal 32-query factorization cannot reduce its
224 copied-rank total. This is not a statement about all factorizations of the
whole fitting matrix, recoding across three or more indicators, different
planes, block payloads, rank distributions, or physical supplier cost.

The proof consists of a general algebraic reduction plus the exhaustive,
source-bound finite rank certificate for this literal geometry. The finite
certificate alone is not a formal proof of the quantified reduction or of a
multiplication theorem. The algebra below requires no pending predecessor
lemma and never reduces `F`-valued coefficients modulo two.

## 1. Normalize the two axes

Drop zero queries. A query with `y_i=0` can be rescaled to `a`, absorbing its
nonzero scalar into `u_i`. Merge all such readers by addition. Do the same for
`b`. The support of a merged reader lies in the union of its old supports.
For a fixed source, rank on that union is at most the sum of the old ranks.
Therefore these operations do not increase the tariff. The remaining queries
are dense: both coefficients are nonzero and their source closure is
`G_A union G_B`.

At a port outside `supp(a) union supp(b)`, the required output row is zero.
Set every reader there to zero. This preserves the operator and cannot enlarge
any closure or rank.

At a target port, if the reader of the **correct** axis is nonzero, set that
coefficient to one and every other reader at that port to zero. The row now
has its required value, and no reader support grows. After this operation each
target port has one of three states:

| State | Axis readers at the port | Required number of active dense readers |
| --- | --- | --- |
| 0 | Correct axis only | 0 |
| 1 | Wrong axis only | At least 1 |
| 2 | Neither axis | At least 2 |

For state 1, the wrong axis cannot alone deliver the target axis. For state 2,
a single dense direction cannot be an axis. These facts hold over every field.
They are necessary support constraints; no presumed independence of a long
query list is used.

## 2. Replace arbitrarily many dense readers by two layers

Let `U` be a subset of the target ports and define

    r(U) = rank_F2 Gram(G_A union G_B, cl(U)).

This is a nonnegative monotone submodular function. Indeed it is the dimension
of the span of the column blocks belonging to the touched planes. The span for
`U intersect V` is contained in the intersection of the two spans; the span for
`U union V` is their sum. The dimension identity gives submodularity even when
two target ports belong to the same plane.

For any finite list of supports `U_1,...,U_t`, let `h(p)` count how many contain
`p`. Submodular uncrossing gives

    sum_i r(U_i) >= sum_{j>=1} r({p : h(p)>=j}).                 (1)

Here is a finite proof, not an appeal to a solver. Insert one set `S` into the
nested layers of the previously inserted sets. Replace the first layer `L`
and carried set `S` by `L union S` and `L intersect S`, keeping the union as the
new layer and carrying the intersection to the next layer. Submodularity
never increases the sum. After the last layer, append the carried set. For
each element this increments its number of layer memberships by exactly one
if it belongs to the inserted set; the layers remain nested. Induction proves
(1). Empty layers cost zero.

Let `d(p)` be the state 0,1,2 from section 1, and put

    S_1 = {p : d(p)>=1},    S_2 = {p : d(p)=2}.

Since `h(p)>=d(p)`, monotonicity and (1) imply

    total dense-reader tariff >= r(S_1)+r(S_2).                (2)

Together with the two axis readers, this reduces the unbounded problem to
three states per target port. It is not the termwise binary-direction mapping
used in PR3429, so that mapping's four-direction counterexample does not apply.

The bound (2) is constructively attainable for each state assignment when
`F` has more than two elements. Choose `t != 0,1` and use only queries
`a`, `b`, `a+b`, `a+t b`. At state 0 use the correct axis. At state 1 use
coefficient 1 on `a+b` and -1 on the wrong axis. At state 2 use these reader
coefficients on the two dense queries:

| Required row | Reader for `a+b` | Reader for `a+t b` |
| --- | --- | --- |
| `a^T` | `t/(t-1)` | `-1/(t-1)` |
| `b^T` | `-1/(t-1)` | `1/(t-1)` |

All indicated coefficients are nonzero. Thus the dense supports are precisely
`S_1,S_2` and the axis supports are precisely those prescribed by the states.
This constructs a dominating realization with at most four directions.
Over F2, merge its only dense direction `a+b` as well; state 2 cannot then
occur, and at most the three available directions suffice. The lower bound
(2) holds without this attainment observation.

## 3. The complete literal finite certificate

For distinct groups there is exactly one target port in each of their planes.
Set `k=(m_A+m_B)/2`. A state string in `{0,1,2}^k` determines axis reader sets
`A_d,B_d` and the two dense layers. Its exact bill is

    rank Gram(G_A,cl(A_d)) + rank Gram(G_B,cl(B_d))
      + rank Gram(G_A union G_B,cl(S_1))
      + rank Gram(G_A union G_B,cl(S_2)).                       (3)

`verify.py` enumerates **all** 120 unordered distinct group pairs and every
state string. There is no search heuristic, cutoff or sampled exclusion. The
rank tables use integer Gaussian elimination over F2. For every state, (3)
is at least `m_A+m_B`; the all-zero state attains it. `RESULT.json` records the
full gap histogram and equality count for each pair, plus a hash of all three
rank tables, rather than only reporting a minimum.

| Group-size sum | Distinct group pairs | States per pair | Minimum bill |
| --- | ---: | ---: | ---: |
| 16 | 55 | 6,561 | 16 |
| 14 | 22 | 2,187 | 14 |
| 12 | 34 | 729 | 12 |
| 10 | 6 | 243 | 10 |
| 8 | 3 | 81 | 8 |

There are **435,456** states in total. Choosing the other alternating half of
either group does not change any closed plane, source closure, rank table or
state constraint. Each group pair therefore covers all four indicator pairs:
480 pairs are covered by this census.

For the remaining 16 pairs, both indicators are halves of the same group `G`.
Every nonzero query closes to `G`. Orthonormality implies that its tariff is
twice the number of planes touched by its reader. On each plane the two target
rows are the independent coefficient vectors `(1,0)` and `(0,1)`, so at least
two query terms must be active somewhere on that plane. Summing the resulting
four units per plane gives `2|G|=m_A+m_B`. This completes all 496 indicator pairs.

## 4. Independent computational route and limits

`independent.py` does not import this checker or predecessor code. It expands
nine-bit labels into binary vectors and performs row elimination on explicit
matrices. For every ternary demand, it independently minimizes over **every
next dense support**, recursively decreasing the total demand. Positive rank
and support monotonicity allow any overcoverage to be removed; the recurrence
therefore covers arbitrary finite support lists. It checks all Bellman results
against the two-layer expression and reproduces every pair's complete receipt.
This separately checks the finite use of uncrossing; it does not replace its
written unbounded proof. Pointwise tests over F2,F3,F5 exercise both axes and
up to four dense directions.

The primary verifier also builds 120 exact integer four-query operators
(`t=2`), including 40 nonzero outside-reader cancellation rows, and checks every
112-by-112 entry. Its sampled operator fixtures supplement the exhaustive rank
census; they are not themselves an exhaustive factorization search.

No native acquisition, scalar coefficient execution, frame change, dirty
restoration, hosting, precision, stock or complete recursive invoice is
constructed or priced here. Those are unknown costs, not zero costs. The
negative conclusion is specific: **mixed pair recoding cannot lower this
copied-rank sum**. Equal or larger rank mass could have a different recursive
rank distribution; that possibility and complete supplier gains are not
excluded. The selected frontier, bit supplier, and inherited all-size/compiler
and analytic obligations are unchanged. **No new κ.**
