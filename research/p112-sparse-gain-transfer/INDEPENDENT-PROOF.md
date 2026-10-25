# Independent audit: disjoint-mark two-port transfer

This is a separate proof audit of the scoped deductions in this package.
It does not attribute them to a literature theorem. No coefficient or
geometry search is involved. The standalone `independent.py` authenticates
the two repository-relative scientific inputs directly and uses no scratch
files or producer code.

## Stronger strict-fitting transfer

Let M be any rational strict fit on the authenticated mask: every scalar
diagonal is1 and every off-diagonal entry outside a free physical-group
pair is zero. Suppose M=Q R and every query column has at most two nonzero
scalar coordinates. There is a characteristic-two strict fit M'=Q'R' with
the same query supports and entrywise smaller reader supports. It need not
equal M on the allowed free entries. Neither query independence nor a
common-recovery hypothesis is required here.

For each actual reader column p, choose a basis among its active queries
that represents M[:,p]. Normalize its nonzero two-port columns as gain
links and its one-port columns as unit queries. Each connected basis
component is a tree, a tree with one unit query, or an unbalanced unicycle.
Keep only the component containing p. All other components contribute
only allowed free output positions and may be deleted. The p-component
contains p because its output there is1.

Give every global link a separate indeterminate over F2 and retain the
same scalar support. Every selected unicycle remains unbalanced over the
common rational-function field: its holonomy is a nonconstant Laurent
monomial. A grounded tree or unbalanced unicycle has full row rank, so
the p-component can then recover e_p by using a subset of its old queries.

Otherwise the p-component is an ungrounded tree. Its original switching
annihilator has no zero coordinates. Consequently its original output,
which is1 at p, is nonzero at some other vertex b. Strict fitting forces
(b,p) to be an allowed free position. The generic-gain tree has a switching
annihilator z with every entry nonzero and recovers
e_p-(z_p/z_b)e_b. This output has diagonal1 and no forbidden nonzero entry.
The new reader remains supported in the selected old-query subset.

These choices use one common generic query matrix and are independent
across reader columns. They therefore give the claimed strict fit.
Zero query columns may be left zero; repeated or parallel links cause no
problem because they have distinct indeterminates. The same proof applied
to the transpose covers a factorization whose reader factors are all
at most two-port.

For the literal P112 mask, the whole-group expansion of EVERY strict fit
is I334. Diagonal scalar entries expand to own orthonormal group blocks;
forbidden off-diagonal entries are zero; every allowed free group block
has identically zero binary pairing, so its arbitrary scalar coefficient
disappears. The independent checker verifies these coefficient identities
for all111,556 expanded entries and recomputes the complete free-pair list
from literal group labels. This is stronger than testing chosen values of
the free entries. Rank subadditivity then gives total whole-group tariff
at least334 over the characteristic-two field and hence for the original
factorization. It is not a bound for unrestricted source/reader factors.

The bound also applies if one common groupwise change of payload basis
makes every source query (or every reader factor) two-port. Precisely, let
D be block diagonal with an invertible rational block on each physical
group, and replace M,Q,R by D M D^-1,D Q,R D^-1. Each own block stays the
identity; each forbidden group block stays zero; free blocks remain free.
An invertible local map preserves whether each complete group restriction
of a factor is zero, so every tariff is unchanged. This is a common
similarity with dual reader changes, not unrelated left and right gauges.

For a local literal-two-port replacement, completion by unchanged canonical
terms needs one explicit refinement. The residual-bearing canonical source
has three ports. Split it into its ordinary two-port pair and its one-port
residual unit, retaining the same full three-copy reader on both terms.
Their sum is the original rank-one term. The two complete-group tariffs are
respectively6 and1, independently replayed from the labels, so its total
charge7 is unchanged. All other canonical queries already have at most two
ports. Thus an untouched residual term can be included without violating
the literal query-sparsity premise. In the coefficient-space corollary,
unchanged canonical columns are coefficient-singletons and need no split.

The sparse-splitting budget consequence also follows without a coefficient
search. Split each arbitrary source vector into disjoint scalar chunks of
size at most two, retaining its original reader. For each term the full
group rank of the union is at most the sum of the chunk ranks, even when
the chunks touch overlapping physical groups. Thus the increase delta_t
is nonnegative and the exact endpoint is unchanged. Applying the strict-fit
theorem to the refined factorization gives C+sum(delta_t)>=334 for EVERY
such choice of partitions. Hence C<=296 needs at least38 total splitting
overhead on both the source-side and transposed reader-side tests. This is
only a necessary test; no optimized partition or achievable saving is claimed.

The following exact-endpoint arguments are additional corollaries with
different hypotheses. Their shared-recovery condition is unnecessary for
the stronger strict-fit lower bound above, but is retained when asserting
that the endpoint itself, including its free entries, is unchanged.

## Exact disjoint-mark endpoint

Let the target columns be disjoint-support indicators c_j, with endpoint
M=sum c_j c_j^t. Every source query has at most two nonzero scalar entries.
For each mark require that c_j lie in the rational span of queries in the
intersection of all actual reader-column supports belonging to that mark.
Choose an independent recovery there and discard any zero coefficients.

Each connected selected query component is an ungrounded tree, a tree with
one unit query, or an unbalanced unicycle without units. This follows from
column independence and the graph's edge count. No zero-coefficient target
component is needed. An ungrounded tree has a switching annihilator with
every coordinate nonzero, so it cannot recover a mark with exactly one
vertex in that component. Every such component has at least two marked
vertices. This argument works for arbitrary nonzero rational link gains;
it does not require signs or half-integral coefficients.

Give each global query link its own indeterminate over GF4. A simple cycle's
gain product is a nonconstant Laurent monomial, so every selected cycle is
unbalanced over F=GF4(t_e). This includes parallel digons, whose two edge
variables are distinct. Grounded trees are full row rank over any field
with nonzero gains.

For each selected ungrounded tree let z be its nonzero switching row. After
row scaling by p_v, its mark is recoverable precisely when the sum of
z_v/p_v on its marked vertices is zero. These variable sets are disjoint:
different components of one recovery are vertex-disjoint, and different
marks have disjoint supports. Vertices used only as unmarked internal
vertices of another recovery do not enter that recovery's equation.

Every equation has at least two variables. Nonzero values with zero sum
exist over GF4 for every such cardinality: pairs of 1's, or a triple
1,omega,omega^2 followed by pairs. Set p_v to z_v divided by its chosen
value and all other p_v to 1. The single global row gauge preserves query
supports and cycle holonomy, satisfies every tree equation, and leaves all
grounded/cyclic components full row rank. Hence each mark has a new recovery
within its selected support, which lies inside every old reader support
for that mark. Repeating the new recovery on those columns proves the exact
endpoint and entrywise reader-support inclusion.

Nothing in this proof requires a finite field. If desired, finitely many
rational functions may be specialized in a sufficiently large finite
extension of GF4 while avoiding their nonzero denominator and required
minor polynomials. This is an existence statement, not a field-size or
native implementation claim.

The supplied independent replay authenticates the literal P112 data and
checks that its 57 marks partition all 112 scalar ports, with sizes
{1:3,2:53,3:1}. Expanding each scalar coordinate to the complete physical
group space gives I334, entry by entry. A lifted rank-one term has rank at
most the binary pairing rank of its complete source/reader group unions.
Binary-matrix ranks remain the same over every characteristic-two extension.
Thus rank subadditivity gives an invoice at least 334 after the transfer,
and support shrinkage gives the same lower bound for the original invoice.

For independent nonzero query columns the common-support hypothesis is
automatic: equal target columns have unique equal query coefficient
vectors. For dependent queries it is a genuine extra premise. The replay
includes an exact dependent-query example whose mark-reader supports have
an intersection that cannot recover the mark. This example makes no saving;
it only protects the scope distinction. Another control uses a three-copy
mark and arbitrary-gain tree that fails ungauged characteristic-two recovery
but is recovered exactly after a GF4 vertex gauge.

This exact-endpoint transfer alone does not cover arbitrary dependent
queries without common recovery. The stronger strict-fit transfer above
does cover such two-port queries by allowing free entries to change. Neither
result excludes general queries with three nonzero scalar coordinates.

## Separate coefficient-space corollary and bridge application

The coefficient-space corollary and bridge deduction were also audited
independently.
For Q=C A with at most two nonzero entries per A-column, injectivity of C
makes every actual reader demand a singleton e_j in coefficient space.
Each independent active recovery graph is then grounded or unbalanced
unicyclic, since an ungrounded tree cannot recover a singleton. Generic
characteristic-two gains keep all such supports full row rank at once.
There is no reader-support intersection requirement in this corollary.
Disjoint supports of the C-columns ensure that changing nonzero A entries
does not change the physical scalar query supports.

For the declared six triangle queries plus bridge c0, the one-dimensional
kernel and one particular exact reader have identical entries in the three
corresponding triangle-query row pairs. This remains true for every exact
reader R0+k z^t, including ambient zero-target columns. Coalescing each equal
reader pair preserves the endpoint and cannot increase tariff, by binary
pairing-rank subadditivity. The resulting four queries are
c0+c1,c1+c2,c2+c0,c0, so the coefficient-space corollary gives invoice at
least18 for the entire bridge-reader family. The earlier36/39 invoices are
only particular controls; no optimum or attainability claim is made.

The portable replay independently builds the six triangle queries, bridge,
particular reader, and null vector. Rank6 proves that the null vector spans
the entire query kernel. The equalities of the particular-reader rows and
null-vector entries prove the three repeated-row identities for arbitrary
reader parameters, rather than only for a tested parameter value. A further
exact rational control includes an ambient zero-target column and replays
the coalesced endpoint. Altering one nonzero reader coefficient or a kernel
sign is detected. The checker also verifies a grounded singleton recovery,
the three-copy GF4 gauge, and the literal residual term's whole-group charge7.
The strict-fit control explicitly changes a free coefficient, preserves
every forbidden zero and diagonal, and retains query/reader supports. A
parallel-digon control verifies that the cyclic case includes multigraphs.

The machine checks establish these finite premises and controls. The
quantified gain assignment and graph arguments above remain written proofs;
the receipt does not claim a machine-formal proof of them. Default replay is
read-only and compares `INDEPENDENT-RESULT.json`; `--write-receipt` is the
explicit regeneration option. Both normal and optimized Python use explicit
exceptions, so disabling assertions does not bypass checks.
