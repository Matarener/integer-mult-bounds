# The exact boundary for shared-port graphic query attachments

## Claim

A graph attached to several old query potentials reduces to differences of
terminal potentials within each connected component. It does not generally
reduce to a subset of the old queries. This proves a precise replacement
criterion for marked support transfer. For two old query ports, a single
additional difference-query test is necessary and sufficient for every finite
three-terminal attachment to preserve a fixed pair of transfer configurations.

For the three displayed non-Fano configurations inherited from PR3506/PR3524,
exact checks over Q and GF4 admit 13 of the 30 choices of two old query ports.
The other 17 choices fail that fixed transfer. The admitted choices give an
infinite family of pair-reader lower bounds, with no graph-size or term-count
bound. The failed choices do not exclude a different transfer map or prove a
cheaper decoder. Characteristic zero is the old coefficient-field scope of
this application. No all-odd-characteristic extension is asserted.

## Marked transfer and the graph intersection lemma

Let V be a vector space over a field F, with independent marks A_1,...,A_k
and unmarked queries Q_1,...,Q_t. In a second space over L, use independent
marks A'_j and indexed queries Q'_i. The inherited two conditions are, for
every query subset B and mark j,

    A_j outside span(A_h for h!=j, Q_B)
        implies A'_j outside span(A'_h for h!=j, Q'_B),    (source)
    A_j in span(Q_B) implies A'_j in span(Q'_B).          (reader)

Choose some old query ports to replace. A finite undirected multigraph has
terminals indexed by 0 and those ports. Assign terminal potentials z_0=0
and z_i=Q_i. Assign each internal vertex a fresh basis vector, independent
of all V and of the other internal vertices. Orient every edge arbitrarily
and use its potential difference z_v-z_u as a new query. Unreplaced old
queries and marks stay in V. Loops and repeated edges are allowed. Use the
same indexed graph over L, with Q'_i and fresh independent internal vectors.

For an edge subset S, define D_F(S) to be the span in V of all z_i-z_j
whose terminal vertices lie in the same connected component of S. Then

    span_F(edge queries in S) intersect V = D_F(S).      (1)

For the forward inclusion, express a vector in V as a linear combination
of selected edges. At every internal vertex the signed sum of incident
coefficients is zero, because its independent potential has coefficient
zero. Within each connected component the sum of all vertex coefficients
is zero. Its remaining terminal coefficients therefore sum to zero, so
their contribution is a combination of terminal differences within that
component. A component without terminals contributes zero. Conversely, a
signed path sum realizes each terminal difference in its component.
These arguments hold over every field and do not require independent
terminal potentials. They also apply when terminal 0 is isolated.

For any old query subset B and any span H of old marks, projection onto the
internal space now gives the stronger formula

    span(Q_B,H,edge_S) intersect V = span(Q_B,H,D_F(S)).  (2)

Apply (2) over both fields. The source and reader conditions after attachment
are exactly their versions with D_F(S) and D_L(S) appended to the unreplaced
query subsets. Thus only the terminal partition induced by S matters. Checking
the conditions for every terminal partition suffices for every finite graph
on these terminal potentials. It is also necessary if all finite attachments
are allowed: join terminals in each desired block by a tree and leave other
blocks disconnected. This is an exact partition criterion, not the assertion
that graph incidence regularity alone supplies marked transfer.

## The two-port test

Replace two queries Q_e,Q_f. There are five partitions of {0,e,f}. Their
old-ambient contributions are respectively

    0; span(Q_e); span(Q_f); span(Q_e-Q_f); span(Q_e,Q_f).

Four cases are already covered by the original marked conditions. The only
additional obligation is the configuration consisting of the unreplaced
queries and the single query Q_e-Q_f, mapped to Q'_e-Q'_f. It must satisfy
both conditions for all its query subsets. This is both necessary and
sufficient for transfer through every finite three-terminal graph.

The three-edge star has one new hub H and new queries

    H, Q_e-H, Q_f-H.

Its edge subsets realize all five terminal partitions. Therefore an exhaustive
star-subset check is equivalent to the difference-query criterion and to
transfer for every finite graph on these three fixed terminal potentials.
The claim concerns one attachment to the stated base. A subsequent attachment
needs a fresh check of the criterion in its resulting configuration.

This explains why the single-port result cannot be applied twice with one
shared H. In the second application H is no longer independent of the full
current ambient space. The surviving direction Q_e-Q_f is a new obligation.

## Exact non-Fano application

Use the ordered rational points

    P0=E, P1=F, P2=G, P3=E+F, P4=E+G,
    P5=F+G, P6=E+F+G.

For marks 0,1, the GF4 template changes P3 to E+F+wG. For marks 0,3 it
uses the displayed binary columns. For marks 3,4 it changes P5 to F+wG.
Here w^2+w+1=0. All other displayed columns are unchanged. These exact
templates, the original proof and the retained support-to-tariff argument
are live pinned inputs in SOURCES.json and VERIFY.json. SOURCE-CLOSURE.json
records their canonical and original origins. Both checkers recheck every
base source/reader implication before any attachment.

The admitted unordered port pairs are exactly the following.

| Fixed marks | Compatible old query ports |
| --- | --- |
| 0,1 | {2,3}, {3,4}, {3,5}, {3,6} |
| 0,3 | {1,5}, {1,6}, {2,4}, {2,5}, {4,6}, {5,6} |
| 3,4 | {1,5}, {1,6}, {2,6} |

Each row has ten possible unordered query pairs. RESULT.json records every
case, its source/reader failure counts, and the first failure in the explicit
six-query star order. The order is the three unreplaced points in increasing
index, then H,P_e-H,P_f-H. Subset masks use bit i for query i. The primary
compares all 64 star subsets and the reduced difference-query test. The
independent implementation compares integer minor ranks with all GF4 linear
annihilators. They agree on all 30 cases. The original symmetry reduction
does not automatically cover the other 18 marked pairs for this question,
because differences depend on the chosen representatives and scalings.

For a concrete failure, mark E,F and attach at G,F+G, ports 2,5. The old
subset with mask 49 consists of D=E+F, G-H and F+G-H. It spans E since

    D + (G-H) - (F+G-H) = E.

Over GF4 the corresponding old-ambient span is span(E+F+wG,F), which does
not contain E. This is a reader failure, despite the common graphic network
and the valid original two-mark transfer. It refutes unrestricted closure
under these shared-port substitutions of the supplied configurations.

## Consequence for the literal pair bill

For each admitted placement, (2) proves marked transfer for every finite
attachment. Apply the inherited support argument to any literal operator

    aa^T+bb^T = sum_i u_i q_i^T

whose augmented indexed query/mark configuration has that rational rank
pattern. The coefficient field may be any characteristic-zero field. Queries,
readers and external directions are otherwise arbitrary within that pattern.
The transferred characteristic-two factors preserve every old zero in both
factors, so complete-plane rectangular binary Gram ranks cannot increase.

In the inherited model, binary labels are partitioned into positive even
orthonormal groups. Close supports to the complete paired Gram-I2 planes and
charge each term by the F2 rank of the query/reader Gram rectangle. Expanding
the full alternating-half indicator identity over GF4 gives I_(2n). Its rank
is 2n. Each transferred term has rank at most its charged binary rectangle.
The untouched indicator terms cost 2n-m_A-m_B. Rank subadditivity therefore
gives the pair bill sum_i C(u_i,q_i)>=m_A+m_B. This uses actual reader
supports, with arbitrary term count and augmented rank. It is a scoped
algebraic floor, not a construction or a universal decoder floor.

## Literal failed-map control and remaining obligations

WITNESS.json fixes six queries at the failed 2,5 attachment and six readers
on four scalar ports. Both actual factors have rank four, and their product
is diag(1,1,0,0). With orthogonal binary labels 1,2,4,8 and groups {0,1},
{2,3}, the complete-plane rectangle charges are 2,4,2,2,2,2. The total 14
loses against the pair baseline 4. It is not a claimed minimum or saving.
No universal conclusion follows from the 17 fixed-map failures.

The graph-intersection and partition statements are the author-written
unbounded proof. Exact finite programs certify the displayed application,
not every finite graph by enumeration. They also check all 1,024 edge
subsets on five vertices with three terminals and two internal vertices.
Independent human and formal proof-kernel review are unclaimed.

Other transfer maps, other marked pairs/scalings, odd characteristics,
simultaneous larger port sets, masked identities and changed support closure
remain open. Acquisition, coefficient execution, dirty restoration, physical
frames and hosting, precision, stock, all-size/compiler admission and a
complete consumer are not supplied. No new kappa or frontier change follows.

Credit remains with Philippe Van Velzen's expanded-identity argument, ctoth's
coverage question, the actual-reader lineage through PR3414/3463/3472/3489/
3491/3505, and Nick Petalas's PR3506/3524/3535 boundary and handoffs. The
multi-terminal reduction, exact two-port compatibility test and its scoped
application are the contribution here.
