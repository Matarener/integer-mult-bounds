# Characteristic-two transfer for two-port queries and disjoint marks

This package proves a support-preserving transfer under a stated common-recovery
premise. The gain-graph facts are proved below; the quantified graph and gauge
argument has a separate mathematical audit in [INDEPENDENT-PROOF.md](INDEPENDENT-PROOF.md).
The exact scripts check the literal P112 expansion and focused finite controls,
not a machine-formal theorem. No selected bound changes.

For the distinct coefficient-space theorem and the seven-query bridge
consequence, see [SCALAR-DEMAND-AND-BRIDGE.md](SCALAR-DEMAND-AND-BRIDGE.md).

## Statement

Let A_1,...,A_m be pairwise disjoint nonempty sets of scalar ports, and let c_j=sum_{v in A_j} e_v. Put M=sum_j c_j c_j^T. Suppose M=Q R exactly over Q, every query column of Q has at most two nonzero entries, and for every j the vector c_j is recoverable over Q using only

    S_j = intersection_{v in A_j} supp(R[:,v]).

Then there is a field F of characteristic2 (and, by specialization, a finite such field can be chosen) and an exact factorization M=Q'R' over F with support(Q')=support(Q) and support(R') contained entrywise in support(R).

The hypothesis on S_j is satisfied if all actual reader columns belonging to each mark are equal, or merely have equal supports. It is automatic when the nonzero columns of Q are linearly independent, because the target columns M[:,v] for v in A_j are equal and Q is injective on query coefficients. Zero query columns can be discarded or retained as zero.

The indicator marks may have any sizes. Thus the statement includes all ordinary paired P112 targets, the three-copy residual-bearing target and the exceptional J singletons. It does not assert preservation of all matroid ranks. It does not cover arbitrary dependent queries with incompatible actual reader-support intersections.

## Select independent recoveries

For each j choose a column basis inside Q_{S_j}, recover c_j in that basis, and delete zero recovery coefficients. Call its remaining support T_j. Each T_j is independent and T_j is contained in S_j. Different marks may use different bases; no common query basis is assumed.

Normalize each two-coordinate query as a gain link e_u-g_e e_v with g_e nonzero rational; normalize a one-coordinate query as the unit column e_u (a halfedge). Scalar normalization preserves all supports and can be absorbed into readers. In each connected component of an independent support T_j, the link graph is a tree, a tree with one halfedge, or an unbalanced unicyclic graph without a halfedge. This follows because connected links need at least n-1 edges while independence permits at most n columns. A square unicyclic gain-incidence block is nonsingular exactly when its oriented cycle gain product is not 1. A tree with a halfedge is nonsingular over any field with nonzero gains.

Every nonempty T_j component meets A_j: otherwise its active independent columns would give a nonzero combination with zero output. If an ungrounded tree component meets A_j in only one vertex, its nonzero switching annihilator forbids that singleton demand. Therefore every ungrounded tree component meets A_j in at least two vertices. This is the only restriction needed on the mark's size or shape.

### Gain-incidence rank facts used above

An oriented nonzero two-port column is normalized as e_u-g e_v. A left
annihilator z obeys z_u=g z_v along each link. In a connected tree these
equations determine every z_v from one root value, and all coordinates are
nonzero if the root value is nonzero. Thus the tree has row rank n-1. A
unit column forces its incident coordinate of z to zero, hence all of z to
zero on that connected component; a tree plus one unit has rank n. An
additional link closes a cycle and requires the root value to equal itself
times the oriented cycle gain product. If that product is not 1, z is zero,
so an unbalanced unicycle also has rank n. This includes a parallel digon.

Conversely, a connected independent query component with n vertices has
at most n columns, while its links require at least n-1 columns for
connectivity. Therefore the possibilities are exactly a tree with no unit,
a tree with one unit, or a unicycle with no unit. The last one must be
unbalanced for independence. Nonempty components with one vertex are handled
by the unit case; zero query columns play no role. These elementary facts
apply to arbitrary nonzero gains, not just signed incidences.

## A common base gain assignment

Use the characteristic-two rational-function field

    F = GF4(t_e : one independent indeterminate per two-port query).

Orient the global query links once and replace each link u->v by e_u-t_e e_v. Use e_u for a halfedge. Every simple cycle has nontrivial holonomy: its oriented product is a nonconstant Laurent monomial in distinct edge variables, hence cannot equal1. This includes a parallel digon, whose edges have different indeterminates. Therefore every selected unicyclic component stays full-row-rank, as does every selected grounded tree. Query supports are unchanged. No prescribed field size, cycle enumeration or coefficient search is needed.

## One vertex gauge satisfies every tree recovery

For each ungrounded tree component C of a selected T_j, let z^C be a nonzero switching annihilator of its base gain-incidence block. Every entry z^C_v is nonzero. Under the global row gauge

    Q' = diag(p_v) Q_base,

that tree's annihilator becomes z^C_v/p_v. Therefore its desired restricted mark is in the column span exactly when

    sum_{v in A_j intersect C} z^C_v/p_v = 0.

The sets of marked vertices appearing in these equations are pairwise disjoint. Within a mark, distinct support components are vertex-disjoint; across marks the A_j are disjoint. A marked vertex can occur as an unmarked vertex of another support, but then its target coordinate is zero and it contributes nothing to that other equation.

Each equation has at least two variables. Choose nonzero target values t_v with sum zero in GF4: for an even number use pairs (1,1); for an odd number at least 3 use (1,omega,omega^2), where omega^2+omega+1=0, and pair the rest. Set p_v=z^C_v/t_v on that equation's marked vertices. Set all unassigned p_v to1. These choices are consistent and nonzero. They make every tree recovery feasible simultaneously.

Row scaling preserves query supports and every cycle holonomy. All selected grounded or cyclic support components remain full-row-rank and require no additional equation. Thus every mark c_j is recoverable using T_j after this one global gauge. Put one such recovery into each reader column v in A_j; since T_j is contained in S_j, this only deletes old reader incidences. Set outside-target reader columns to zero. The resulting endpoint is Q'R'=M over F, proving the claim.

## Optional finite-field specialization

The construction uses only finitely many rational functions. After choosing the finitely many recoveries, collect all nonzero denominators and all numerators whose nonvanishing is required to retain query supports and the selected full-rank minors. Their product is a nonzero polynomial over GF4. It has a nonzero value at some tuple over the infinite algebraic closure of GF4; that finite tuple lies in a finite extension of GF4. Specializing there preserves the endpoint identities and support inclusions. This is an existence corollary, not an efficient field-size bound, and the tariff proof does not require it.

## Exact P112 consequence

The 57 canonical target indicator vectors have pairwise disjoint scalar supports and together cover 112 ports. Their marks include paired, singleton and one residual-bearing three-copy case. The physical tariff is the binary rank of the complete source/read group pairing rectangle. Extending F2 to any characteristic-two field F preserves the rank of these binary matrices; deleting scalar supports cannot enlarge their whole-group closures or ranks. The existing retained I334 expansion therefore gives invoice at least 334 for any decoder satisfying this theorem's support-intersection premise. Local replacements inherit their original local invoice as a floor by appending unchanged canonical terms.

### Why the complete-group expansion gives the claimed floor

For each scalar port p, let G(p) be its complete physical group, with ordered
binary labels q_a for a in G(p). Expand a scalar matrix entry N[p,r] into the
block N[p,r] (q_a dot q_b) indexed by a in G(p), b in G(r), where the dot
product is computed over F2 and then embedded in the coefficient field.
This defines a linear expansion L(N). The replay checks every one of the
334^2 entries of L(M), obtaining exactly I334. It also checks all physical
groups are orthonormal and the 57 marks partition all 112 ports with sizes
three singletons,53 pairs and one triple. The canonical term charges are
3 H3+53 H6+H7=334; the residual-bearing mark is {9,39,55} and costs 7.

For a transferred rank-one term x y^T, its expanded matrix is obtained from
the binary Gram rectangle on the complete source and reader group unions
by row/column duplication and diagonal multiplication by entries of x,y.
Thus rank_F L(x y^T) is at most the binary rank tariff of those complete
unions. The binary rectangle has the same rank over F as over F2: a nonzero
minor remains nonzero under a field extension, and all larger minors remain
zero. Rank subadditivity in L(M)=sum L(x_i y_i^T)=I334 gives

    334 <= sum_i rank_F L(x_i y_i^T) <= transferred invoice.

Preserved source supports and shrinking reader supports imply transferred
invoice <= original invoice. This proves the stated334 floor under the
transfer theorem's premises. No coefficient sizes, denominators or native
arithmetic are being priced by this scalar tariff model.

To apply this literal-two-port floor locally, append the canonical terms
outside the changed marks, with one necessary refinement: split the residual
three-port query into its ordinary pair and residual unit, both retaining
the same three-copy reader. Their exact charges are 6 and1, so the total
residual charge remains 7 while every completion query has at most two ports.
Subtracting those explicit completion costs from 334 gives the original
local canonical invoice as a floor; for three
ordinary paired marks this is18. Extra zero-target reader columns can be
set to zero during transfer and cannot decrease the original invoice.

For independent nonzero queries, common recovery is automatic. For dependent
queries it is a genuine condition on this endpoint-preserving theorem, as
the failed-intersection control shows. But failing that premise does not
escape the invoice floor: the uniform strict-fit theorem in [PROOF.md](PROOF.md) covers
all literal one-/two-port query families by allowing free fitting entries
to change. This companion is retained for its stronger preservation of the
specified endpoint, not as an open loophole in the strict-fit result.

## What is and is not inherited from literature

Signed/gain incidence ranks and switching are standard graph representation facts (the signed specialization is described in Thomas Zaslavsky, [Signed Graphs and Geometry](https://people.math.binghamton.edu/zaslav/Tpapers/sggm.pdf), Theorems3.1 and3.5-3.6). The half-integral coefficient lemma of Bolker-Zaslavsky is not used in this arbitrary-gain proof. The common vertex gauge, formal independent gains, support-intersection premise and P112 invoice mapping above are local deductions. This note should not be described as a global matroid representation theorem or an unrestricted rational lower bound.
