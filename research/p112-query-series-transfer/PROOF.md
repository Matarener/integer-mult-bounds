# Query series expansions preserve the reader floor

## Claim and boundary

Fix independent marked vectors A_1,...,A_k and an ordered finite query list
Q=(Q_1,...,Q_t) over a field F. Suppose another configuration over a
characteristic-two field L has independent marks A'_1,...,A'_k and satisfies,
for every query subset S and every mark j, the two implications

    A_j outside span({A_h:h!=j}, Q_S)
        implies A'_j outside span({A'_h:h!=j}, Q'_S),       (source)
    A_j in span(Q_S) implies A'_j in span(Q'_S).           (reader)

Call these the marked transfer conditions. They concern spans, not the old
numeric coefficients or every subset rank.

The conditions are closed under any finite sequence of the following
operations on unmarked queries, with the same operation performed in both
configurations:

- Parallel duplication replaces Q_e by two copies Q_e,Q_e.
- Series splitting replaces Q_e by Q_e+z,z in V direct-sum Fz. All other
  queries and marks have zero z coordinate. The new direction z is independent
  of the entire previous ambient span. Use a new independent direction at
  each series split.

Subsequent operations may split either descendant of an earlier query.
The theorem also covers configurations with the same indexed matroid as an
expanded configuration, since its hypotheses and conclusion use only spans.
In particular, invertible ambient transformations and nonzero individual
column scalings are allowed. Marks stay fixed as indexed elements; splitting
a target element is outside the theorem.

Apply this closure to the non-Fano two-mark transfer of PR3506. Every literal
pair realization whose augmented query/target configuration belongs to this
query-series/parallel family obeys the original complete-plane reader floor,
with no bound on term count or augmented rank. This is a new infinite-family
extension of that premise. It is not a classification of arbitrary six-term
configurations, a global P112 decoder floor, or a supplier theorem.

## The subset reduction proves closure

Let T be the set of queries after one rewrite and let S be any subset of T.
Collapse S to an old query subset c(S) as follows. Keep unchanged queries.
For parallel duplication include old e exactly when at least one copy is
in S. For series splitting include old e exactly when both descendants are
in S.

For every old ambient vector v, and any fixed old marked subset H,

    v in span(H, T_S) iff v in span(H, Q_c(S)).           (1)

For a parallel pair this is immediate. For a series pair, the coefficients
of Q_e+z and z must sum to zero because v and H have zero z coordinate.
If both are present their combinations give precisely the old multiples of
Q_e. If only Q_e+z is present its coefficient must be zero; if only z is
present its coefficient must be zero. The same argument holds in
characteristic two, where subtraction equals addition. It does not assume
that Q_e is independent of the remaining queries.

Apply (1) first over F and then over L. Taking H to be all other marks proves
the source implication after the rewrite. Taking H empty proves the reader
implication. The marks remain independent, because they are unchanged in a
larger ambient space. Finite induction proves the theorem for arbitrary
rewrite depth, including mixed and nested series/parallel rewrites. This
induction, rather than a finite search, proves the unbounded claim.

The independent direction is essential to this argument. Replacing Q_e by
Q_e+w,w with w already in the ambient span need not satisfy (1). For example,
Q_e=(1,0), w=(0,1), old target v=(1,1), H empty, and S containing only Q_e+w
makes the left side true while c(S) is empty. This is a scope counterexample
to dropping the new-direction hypothesis, not a cheaper decoder.

## Retained non-Fano premise

Use the seven ordered columns

    P0=E, P1=F, P2=G, P3=E+F, P4=E+G, P5=F+G, P6=E+F+G.

Over characteristic other than two the six three-point lines are
013,024,056,125,146,236; the triple 345 is independent. Mark any two columns;
the other five are queries. PR3506 supplies three GF4 configurations:

| Representative marks | Change to the displayed columns over GF4 |
| --- | --- |
| 0,1 | Replace P3 by (1,1,w) |
| 0,3 | Retain every binary column |
| 3,4 | Replace P5 by (0,1,w) |

Here w^2+w+1=0. The 24 permutations of the complete quadrangle's vertices
{0,1,2,6} act on its three opposite-edge matchings {3,4,5}. They preserve the
six lines and are transitive on the six vertex/vertex, twelve vertex/matching
and three matching/matching pairs. Thus the three rows cover all 21 marked
pairs. For each subset of the other five columns both marked transfer
conditions hold. The two independent checkers recheck all these implications,
not an assertion that the entire non-Fano matroid has a GF4 representation.
The implication predicates depend only on old ranks, so they hold for every
representation of this indexed non-Fano rank pattern over any field.

The exact predecessor proof and template bytes are retained in this package.
SOURCE-CLOSURE.json records the originating PR, commit, path, Git blob and
SHA256. They are inherited mathematical premises, not comparison-only data.
The new proof restates the premise and both programs recheck its finite part.
No replay needs a foreign Git object or network access. PR3513's seven-point
classification is comparison and handoff context only; no classification
claim from it is used.

A non-Fano minor remains after any sequence of unmarked query rewrites.
Delete a redundant parallel copy or contract the added z column of a series
pair to undo the last rewrite. Consequently these expanded configurations
remain outside full characteristic-two matroid representability. To see the
base obstruction directly, normalize P0,P1,P2 to axes. The first two lines
force P3 proportional to E+F and P4 proportional to E+G after rescaling axes.
Lines 056,146,236 then force P5 proportional to F+G and P6 proportional to
E+F+G. In characteristic two P3+P4+P5=0, contrary to independence of 345.
Thus this closure application is not an instance of PR3505's sufficient
full-representability condition.

## From span transfer to the literal bill

Partition n indexed binary labels into positive even groups, each with binary
Gram matrix I. Pair consecutive ports of each group into complete Gram-I2
planes. Let a,b be two distinct alternating-half indicator vectors, from
groups of sizes m_A,m_B, which may be the same group. Their supports are
disjoint. Cross-group binary pairings are unrestricted. For an actual scalar
vector x, let cl(x) contain both ports of every plane touched by its nonzero
support. Charge a term u q^T by

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

Suppose over F that

    aa^T+bb^T = sum_i u_i q_i^T,                            (2)

and its augmented query/target configuration admits marked transfer to L.
Queries and readers in (2) can have arbitrary values on external ports and
arbitrary external directions. Repeated, zero and cancelling values are
allowed whenever the marked transfer hypotheses hold.

For a source port r on a, the old coordinate functional takes values 1 on a,
0 on b, and 0 on every query with q_i(r)=0. Hence a is outside the span of b
and those zero queries. The source condition gives an L-linear functional
f_r with those same prescribed values on the new marks and zero queries.
At a b port exchange the marks; outside both supports take f_r=0. Set
q'_i(r)=f_r(Q'_i). Every old query zero remains zero.

At a reader port p on a, equation (2) expresses a as a combination of exactly
those q_i with u_i(p)!=0. The reader condition supplies a combination for A'
using only those indices; use its coefficients as u'_i(p). Do the same for b,
and use zero coefficients outside the target supports. Thus every old reader
zero remains zero, even if old external reader values cancelled. Applying
f_r to this reader equation proves the literal identity (2) over L for the
new factors. Both supports shrink term by term. Plane closure is monotone,
so each new rectangular Gram rank is at most its old charge.

Let K be the sum v v^T over all alternating-half indicators of the partition.
Expand its scalar entry (p,r) to that scalar times the binary 2-by-2 Gram
block between the complete planes at p,r, now interpreted in L. The result
is I_(2n). Its diagonal blocks are I2. Distinct planes in one group are
orthogonal, and mates of a plane lie in different indicators, so every
other scalar-supported block is zero. An expanded term u'_i(q'_i)^T has
L-rank at most C(u'_i,q'_i), by row/column selection, repetition and scaling
through its binary Gram rectangle. A binary matrix has the same rank over
F2 and its characteristic-two extension L.

Append the untouched original indicator terms to the transferred pair. Their
bill is 2n-m_A-m_B. Rank subadditivity for I_(2n) therefore gives

    sum_i C(u_i,q_i) >= sum_i C(u'_i,q'_i) >= m_A+m_B.

Disjoint pair replacements inside the stated family preserve the complete
baseline floor 2n, including 224 on a 112-port partition. There is no claim
that a fixed expanded non-Fano dictionary attains the floor.

## A literal rank-four six-term control

WITNESS.json gives six query and reader columns on four scalar ports. Its
queries are the non-Fano list marked at P0,P1, with query P2 split once.
Both factor ranks are exactly four, and their product is diag(1,1,0,0).
Thus the example genuinely reaches the rank-(4,4) six-term boundary left by
PR3513. It is not silently reduced to a rank-three actual factor.

Take binary labels 1,2,4,8 in groups {0,1},{2,3}. Direct complete-plane Gram
ranks for its six terms are 2,0,4,4,2,2, totaling 14 against the pair floor 4.
The zero-charge term connects orthogonal groups. It must still be present in
the literal operator. The value 14 is a checked example, not a minimum for
this dictionary and not a useful saving. The theorem covers arbitrary
physical supports realizing the same augmented rank pattern, rather than
just this four-port control.

## Evidence and remaining obligations

verify.py uses rational and GF4 elimination. independent.py computes base
rational ranks by minors, collapses expanded subsets by (1), and computes GF4
span membership by all linear functionals and a downward subset transform.
The finite suite covers all 21 base marked pairs, every one-step split and
parallel duplication, and mixed two-step rewrites at the three representative
pairs, including splitting the newly appended descendant. RESULT.json binds
the ordered finite output. test_controls.py runs optimized real CLIs on
private regular copies with deliberate corruptions and preserves positive
runs before and after restoration.

The unbounded result is the written closure induction. Independent human and
formal proof-kernel review are unclaimed. Arbitrary rank-four configurations,
series splits of marks, nonindependent added directions, different fitting
matrices, masked identities, larger-target non-Fano transfers, changed closure
rules and shared physical operations are separate. No native acquisition,
coefficient execution, dirty restoration, frame/hosting/precision/stock,
compiler/all-size admission, complete consumer, supplier or outer
multiplication theorem is supplied. No new kappa or selected-frontier change
is claimed.

Credit remains with Philippe Van Velzen's expanded-identity argument, ctoth's
coverage question, and the retained actual-reader lineage of PR3414, PR3463,
PR3472, PR3489, PR3491, PR3505 and Nick Petalas's PR3506/PR3513 handoffs. The
series/parallel closure argument and its rank-four application are the new
contribution here.
