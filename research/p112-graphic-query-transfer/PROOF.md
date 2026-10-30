# Cyclic single-port networks preserve marked support transfer

## Result and scope

PR3524 proves closure for series and parallel rewrites of unmarked queries.
This note allows an arbitrary finite two-terminal graph, whose edges reuse
internal directions and may contain a Wheatstone bridge. The new theorem is
a rank-one interface lemma. It closes cyclic sharing inside one query port,
with no term-count or augmented-rank bound. Sharing directions between two
old query ports or splitting a marked target remains outside the theorem.

Let A_1,...,A_k be independent marked vectors and Q_1,...,Q_t unmarked
queries over F. A second configuration over L has independent marks A'_j
and queries Q'_i. Assume for every query subset S and every j that

    A_j outside span(A_h for h!=j, Q_S)
       implies A'_j outside span(A'_h for h!=j, Q'_S),     (source)
    A_j in span(Q_S) implies A'_j in span(Q'_S).          (reader)

These are marked support-transfer conditions. They preserve only the stated
implications, not all ranks. The relevant application has characteristic L=2.

## General rank-one interface lemma

Replace an unmarked query Q_e by columns

    T_i = lambda_i Q_e + w_i in V direct-sum W.

The internal space W is independent of the entire old ambient space V.
For each subset S of new indices define rho_F(S) to mean

    (1,0) in span_F {(lambda_i,w_i): i in S} in F direct-sum W.

For any old subset of queries B, old marked subset H and old vector v,

    v in span(B,H,T_S)
       iff v in span(B,H,Q_e when rho_F(S) holds).        (1)

Indeed, projecting onto W forces the selected coefficients to sum to zero
in W. Their surviving coefficient on Q_e is either always zero, or its
possible values form all of F. The latter case holds exactly when rho_F(S)
holds. This also proves (1) when Q_e=0. No independence of Q_e from the
other old queries is required.

Perform the same indexed replacement over L with an internal space W'
independent of the old L ambient space. If rho_F(S)=rho_L(S) for every S,
use (1) over both fields. With H all other marks it transfers the source
condition. With H empty it transfers the reader condition. The old marks
stay independent. Thus marked support transfer is preserved. Finite
induction permits any finite number of replacements, including replacements
of newly introduced edge queries. Every attachment needs fresh internal
space relative to its current ambient space.

## Graphic networks have field-independent rho

Take any finite undirected multigraph with distinct terminals s,t. Orient
its edges arbitrarily. Assign potentials

    z_s=0, z_t=Q_e, z_v=new independent basis vector for each internal v.

For each edge uv oriented from u to v use T_uv=z_v-z_u. Loops are zero
queries; repeated edges are permitted. Make the same construction over L,
where subtraction becomes addition if characteristic L=2.

For every edge subset S, rho(S) is exactly s-t connectivity in that subset.
If a path exists, sum its signed edge columns to obtain Q_e, or the formal
(1,0) before substitution. Conversely, suppose s and t are disconnected.
The functional that is 1 on potentials of vertices in t's connected
component and 0 on all others annihilates every selected edge difference
but takes value 1 on the formal terminal vector. This excludes its span
over every field. Therefore (1) uses one common connectivity predicate.
Disconnected graphs, cycles, arbitrary orientations and dangling components
need no extra hypothesis. There is no finite graph-size bound in the proof.

## A genuine extension beyond read-once series/parallel collapse

Use four vertices s,t,a,b and edge order

    sa, at, sb, bt, ab.

The five columns are H, Q_e-H, J, Q_e-J, J-H. Their minimal connecting
edge sets are {0,1}, {2,3}, {0,3,4}, {1,2,4}. Their minimal disconnecting
edge cuts are {0,2}, {1,3}, {0,3,4}, {1,2,4}.

Each list has a connected co-occurrence graph on the five edge variables.
A nontrivial read-once monotone formula has an AND or OR at its root, with
disjoint nonempty variable sets in the two children. At an OR root each
minimal true set lies in one child, so true-set co-occurrence is disconnected.
At an AND root each minimal false certificate lies in one child, so cut
co-occurrence is disconnected. Both contradict the displayed lists. All
five variables are essential. Thus this exact connectivity predicate is
not the AND/OR read-once predicate produced by series/parallel rewriting
of a single old query. This distinguishes the new single-port attachment
from the prior operation history. It does not assert a classification of
all abstract matroids obtainable by differently relabeling the base.

## Application to the non-Fano literal pair tariff

Use the inherited non-Fano two-mark configurations and three GF4 templates
from PR3506, retained and restated by PR3524. Their exact mathematical proof
sources and runtime template file are pinned in SOURCES.json and declared
as export inputs in VERIFY.json. SOURCE-CLOSURE.json records their original
origins. The new checkers recheck all finite implications at the three
representative marked pairs. The inherited quadrangle symmetry covers all
21 pairs. We do not assume full characteristic-two representability of the
non-Fano matroid.

PR3524's support-transfer argument applies to any configuration satisfying
the marked conditions. Briefly, let aa^T+bb^T=sum_i u_i q_i^T be a literal
pair operator. For each source coordinate on a or b, its coordinate
functional separates that mark from the other mark and every zero query.
The source implication supplies such a functional over L, preserving every
query zero. For each reader coordinate, the operator expresses its target
mark in the span of queries at nonzero reader positions. The reader
implication supplies coefficients supported on those positions, preserving
every reader zero. Coordinates outside both targets can be set to zero.
Applying the source functionals proves the new literal operator over L.

Let each positive even binary-label group have Gram matrix I. Close every
scalar support to the complete Gram-I2 planes it touches, and charge

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

The support shrink above cannot increase this rectangular rank. Expanding
the full alternating-half indicator identity plane by plane gives I_(2n)
over L. Each expanded term has L-rank at most its binary rectangle charge.
Appending the untouched indicator terms of total charge 2n-m_A-m_B and
using rank subadditivity gives

    sum_i C(u_i,q_i) >= m_A+m_B.                          (2)

Consequently (2) holds after arbitrary finite graphic substitutions into
unmarked queries of any non-Fano marked pair, with arbitrary actual readers,
external directions, term count and augmented rank. This is an algebraic
support floor. No physical COPY program or complete supplier is supplied.

## Literal cyclic control and limits

WITNESS.json fixes a nine-term operator on six scalar ports. Both actual
factors have rank five. It replaces the unmarked G query at marks E,F by
the five-edge network above, and has endpoint diag(1,0,1,0,0,0). Its labels
are six mutually orthogonal binary unit vectors paired into three planes.
Both checkers verify the literal product and all rectangular charges. The
bill is a losing control against m_A+m_B=4, not a claimed optimum or saving.

The theorem is the written projection/path/cut argument. Finite graph and
marked-pair checks do not substitute for its unbounded proof. Independent
human and formal proof-kernel review are unclaimed. Cross-port internal
sharing, marked-target rewrites, arbitrary non-graphic field-sensitive
interfaces, masked identities and changed plane closure remain separate.
Acquisition, coefficient execution, dirty restoration, frames, hosting,
precision, stock, compiler/all-size admission and complete consumers remain
unproved here. No new kappa or selected-frontier change is claimed.

Credit stays with Philippe Van Velzen's expanded-identity argument, ctoth's
coverage question and the actual-reader lineage through PR3414, PR3463,
PR3472, PR3489, PR3491, PR3505 and Nick Petalas's PR3506/PR3513/PR3524.
The rank-one interface lemma, arbitrary graphic closure and cyclic control
are the contribution of this package.
