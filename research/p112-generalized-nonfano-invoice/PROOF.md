# One generalized non-Fano five-target mechanism: exact identity, wrong invoice

This note tests ONE explicit algebraic construction supplied by the literature
agent from Das--Rai, arXiv:1609.05815, Section IV after equation(44), q=4.
No coefficient, embedding, or reader-choice sweep is performed. The network
coding identity is credited to that source; its present full-triad invoice
audit is local research and supplies no improved decoder or bound.

## The exact identity

Let a,b1,b2,b3,b4 be five distinct canonical target columns. Put B=sum_i bi,

    y0=a+B,  yi=a+B-bi (i=1,...,4),  yB=B.

Then each bi=y0-yi. There are two displayed readers for a:

    a=y0-yB,
    a=(y1+y2+y3+y4-3yB)/4.

The query relation is

    4y0-y1-y2-y3-y4-yB=0.

Use the first reader at one scalar copy of a and the second at the other.
Use y0-yi at every scalar copy of bi. For a with a residual third copy,
either displayed a reader may be used there. Each reader column reconstructs
its corresponding target, so the six rank-one terms give exactly

    aa^T + sum_i bi bi^T.

`verify.py` checks all100 entries on ten abstract scalar copies
over exact fractions, and finds source rank5 and reader rank6. The division
by4 is essential to this displayed algebra over Q; the argument is not an
entrywise reduction modulo2.

## Exact complete-group masks

Write Ua for the complete binary support of a, and Ui for that of bi.
Let L and R be the physical triads at the two a copies, and V=sum_i Ui.
The source and reader support spaces are exactly:

| Term | Source space | Reader space |
|---|---|---|
| y0 | Ua+V | L+V |
| yi | Ua+sum_(j!=i) Uj | R+Ui |
| yB | V | Ua |

The exact invoice is the sum of the six rectangular pairing ranks of these
spaces. Addition denotes a binary space sum, not direct sum. Repeated-role
axes cause physical groups to coincide; one must take the corresponding
unions, not count duplicate groups as additional dimensions. Since different
canonical targets have disjoint scalar supports, their nonzero query
coefficients do not cancel at a scalar port.

In abstract group order aL,aR,b1L,b1R,...,b4L,b4R and term order
y0,y1,y2,y3,y4,yB, the checked masks are

    source: [1023,1011,975,831,255,1020],
    reader: [1021,14,50,194,770,3].

These masks are a transparent exact invoice formula; they are not six scalar
rank charges. The physical cost remains rank_F2 of COMPLETE group pairings.

## Structural rejection for every five ordinary target choice

Let H_i=E_(2i+1)+E_(2i+2), i=0,...,17, be the ordinary pair spaces. Each has
dimension6 and Gram identity. The independent checker authenticates the
physical labels and cover, constructs their annihilators directly, and gives

* each H_i^perp has seven nonzero vectors;
* among511 nonzero ambient vectors, the numbers lying in0,1,2,3 pair
  annihilators are respectively395,107,8,1; none lies in4;
* among153 pairs of distinct roles,142 have zero common nonzero annihilators
  and11 have exactly one.

Consequently ANY TWO distinct pair roles span dimension at least8, and ANY
FOUR span the complete nine-dimensional ambient space. This is a fixed
incidence verification, not an embedding-cost optimization.

Every ordinary paired role contains only three canonical scalar target axes.
Any four distinct ordinary targets therefore touch at least two pair roles.
Each of the SIX source queries above contains at least four distinct targets.
Their complete source spans S_t all have codimension at most1 in F2^9.

For any binary source and reader spaces,

    rho(S,T)=dim(T)-dim(T intersect S^perp)
            >=dim(T)-codim(S).

The y0 reader contains the four b targets, so its reader span has dimension
at least8. Each yi reader contains Ui of dimension6, and the yB reader
contains Ua of dimension6. Therefore, without any detailed pricing,

    total invoice >= (8-1) + 4(6-1) + (6-1) = 32.          (1)

The five untouched ordinary targets cost30. Thus this specified mechanism
cannot improve their bill, even when several targets are different axes of
the same paired role. For FIVE DISTINCT roles the four-role saturation
premise makes all sources full9, giving the stronger simple floor

    total invoice >= 9 + 4*6 + 6 = 39.

The bound32 also holds if one selected target is the residual-bearing axis.
Delete the residual scalar port from both factors first. The resulting
ordinary ten-port identity is unchanged, and each tariff can only decrease.
The original five-target baseline is then31, still below32. This argument
does not depend on which displayed a reader was assigned to the residual
copy. It also works when both remaining a copies use the same reader,
because y0 always reads all b copies, yi always reads bi, and yB always
reads a with a nonzero coefficient.

## Why the hoped-for four-unit saving fails geometrically

For the exact source and reader spaces define the annihilator benefit

    Z=sum_t dim(R_t intersect S_t^perp).

The invoice is exactly sum_t dim(R_t)-Z. A four-unit improvement on an
ordinary baseline30 would require Z>=sum dim(R_t)-26>=12. But these actual
sources give Z<=6. This isolates the missing geometry: the query sums are
already so large that the readers have at most one invisible direction each.
The characteristic-dependent cancellation does not provide enough physical
annihilator benefit to offset that cost. Four successful units per block
would help the global38-unit gap only if enough compatible blocks existed;
this direct construction supplies none.

## J cases and the complete scope of this specific reader assignment

If the hub a is one of the final unpaired J axes, it has only one canonical
scalar copy, so the specified two-copy reader switch is unavailable. Choosing
either displayed reader for that one port, with the stated fixed b readers,
leaves every reader constant on each canonical target's support. Both factor
families then lie in the canonical span. The existing arbitrary-term
canonical-span theorem applies: after adjoining the untouched targets, a
58-term decomposition costs at least334+2, so its local invoice is at least
its old baseline plus2. This is a scope application of
`p112-rational-decoder-gate/CANONICAL-SHARP-PROOF.md`, not a new theorem.

If a is ordinary and k of the bi are J axes, where1<=k<=3, write B0=30-3k
for the original bill before adding a possible residual line. The following
analytic extension was derived by the parent and independently audited here.
It uses two further fixed physical premises, checked from annihilator
intersections rather than embedding prices:

* J plus any ordinary pair has dimension at least7: the dimensions9,8,7 occur
  respectively7,9,2 times among the18 roles.
* An ordinary triad from a DIFFERENT role plus an ordinary paired space has
  dimension at least7. All612 ordered choices were checked; their dimension
  histogram is {7:46,8:318,9:248}.

If every ordinary target is in the same pair H, every query source contains
H. The y0 reader contains H because there is at least one ordinary bi
(k<=3). Every ordinary yi reader contains H, as does the yB reader. These
terms cost at least6 each. For a J target bi, its yi source and reader both
contain the a-right triad R, so that term costs at least3. Thus

    C >= 6 + (4-k)*6 + k*3 + 6 = B0+6.                    (2)

If the ordinary targets occupy at least two roles, the y0 source has
dimension at least8, while its reader contains an ordinary bi pair plus J
and has dimension at least7. Its tariff is at least6. The yB source contains
an ordinary bi pair plus J and has dimension at least7; its reader contains
the six-dimensional a pair, so its tariff is at least4. The k J-middle
terms still cost at least3 from their common a-right triad.

Every ordinary middle term costs at least5. If its source retains at least
two ordinary roles, source dimension>=8 and reader dimension>=6 prove this.
Otherwise every remaining ordinary target lies in a's role H. The removed
bi belongs to a different role, since the entire target set occupied at
least two roles. The source contains H+J, of dimension>=7, and the reader
contains Ui plus the foreign a-right triad, also of dimension>=7. Rank-nullity
again gives tariff>=7-(9-7)=5. Consequently

    C >= 6 + 5(4-k) + 3k + 4 = 30-2k = B0+k.             (3)

There is at most one residual-bearing selected target. Deleting its residual
port reduces neither of the paired-triad premises used in(2)-(3), and the
original baseline is at most B0+1. Since k>=1, these cases cannot improve it;
the weakest k=1 residual bound allows a tie, not a saving.

For this last assertion the reader assignment is exactly the one defined
above: the two ORDINARY partner-triad copies of a receive the two different
readers; an optional third residual copy may receive either. This guarantees
the a-right incidence in every middle reader after residual deletion. Putting
the sole five-term a reader on the residual line instead is a different
assignment and is not silently covered by(2)-(3).

Together with(1) and the hub-J canonical-span application, this closes this
specified six-query/five-target mechanism on every choice of the fixed
canonical targets. No embedding or reader-choice sweep is used.

## Relation to earlier hub work

The earlier external-star theorem has queries of the form
a_j+alpha_j*c and a compensating common reader. It proves a floor for that
specific rank-one perturbation architecture. The present construction has
different query rays and a port-dependent choice between two a readers;
I have not proved it is an instance of that theorem. The earlier two-hub
K3,2 investigation retains seven independent reader-support premises per
mark and has a different rank/port architecture. Its failure to embed is
not used here. The present rejection rests entirely on the explicit identity
and literal span premises above. No broad old-hub closure is asserted.

## Reproduction and status

    python -I -O -Werror -B research/p112-generalized-nonfano-invoice/verify.py

The checker is standalone standard-library code, reads only the two pinned
physical inputs, and writes no files. It checks the exact coefficient identity,
source and reader masks, factor ranks, and the pair/J/foreign-triad annihilator
premises. The displayed analytic inequalities are the written proof; the
checker also checks their small integer accounting table.
It ran successfully in approximately0.3 seconds. The literary source was
identified by another agent; the algebra and physical premises were derived
and checked independently here. Human mathematical review is unclaimed.
