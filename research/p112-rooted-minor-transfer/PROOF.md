# Marked support transfer descends to minors

## Definition and contraction lemma

Let E,F be independent vectors over an old field K, with a finite indexed
query family Q_i. A marked support transfer assigns independent e,f and
arbitrary query images q_i over a new field L, subject to both marked
orientations of these implications for every query-index subset S:

    E outside span(F,Q_S)  implies e outside span(f,q_S),
    E in span(Q_S)         implies e in span(q_S).             (1)

The old and new fields need not agree. Query images may depend on the
entire configuration and have arbitrary ambient dimension. This is the
same implication contract as PR3583. It does not require preservation of
unmarked dependences or that an image be a graph endpoint difference.

**Lemma.** Delete any query indices. Also choose a disjoint finite set C
of indices to contract, provided the old marks have independent images
in V/span(Q_C). Every marked support transfer of the original family
induces one for the surviving old queries in V/span(Q_C).

Proof. Deletion just restricts the index subsets in (1). Write
U=span(Q_C), u=span(q_C), and use bars for the corresponding quotient
classes. The assumption implies E outside span(F,Q_C) and F outside
span(E,Q_C). Applying the two source implications at S=C gives

e outside span(f,q_C) and f outside span(e,q_C). These two exclusions
make e-bar and f-bar independent in the new quotient. They also make
both nonzero. This independence must be established before using the
quotient as a new transfer target.

For a surviving index subset S,

    E-bar outside span(F-bar,Q-bar_S)
      iff E outside span(F,Q_S,Q_C),
    E-bar in span(Q-bar_S)
      iff E in span(Q_S,Q_C).

Apply (1) to S union C, then pass the resulting source exclusion or
reader containment to the new quotient. Do the same with E and F
interchanged. The resulting implications are exactly (1) for the
contracted family. No assumption about the dimensions or dependences
among the new q_i was used. This proves the lemma.

The contrapositive is useful: a nontransferable marked minor excludes
transfer on every marked extension from which it is obtained. Arbitrary
query contraction is not permitted when it identifies or kills a mark.
For example, contracting Q=E-F makes the old marks equal. Its original
family transfers identically over the same field, but those quotient
marks cannot satisfy the definition. This explains the independence
hypothesis rather than silently omitting it.

## Terminal-rooted graph obstruction

Let K have characteristic different from two. Take independent E,F,G
and one independent vector X_v for each nonterminal vertex of a finite
graph. Three prescribed terminals have potentials

    P_0=0,  P_a=E+G,  P_b=F+G.

Each oriented edge uv supplies query P_v-P_u. Retain three additional
queries g=G, d=E+F, t=E+F+G, and mark E,F. Edge orientation does not
affect any query-subset span. Parallel edges, loops, unused vertices
and additional edges do not affect the sufficient condition below.

A **terminal-rooted K3,2 minor model** consists of five pairwise disjoint
nonempty connected vertex sets B_0,B_a,B_b,B_H,B_K, with terminal 0,a,b
in B_0,B_a,B_b respectively, and at least one graph edge between every
one of the first three sets and each of the last two. The terminals
are prescribed on the three-vertex side. An unrooted K3,2 minor alone
is not the hypothesis of this theorem.

**Theorem.** This configuration has no marked support transfer to any
characteristic-two field, in any ambient dimension, whenever the graph
has a terminal-rooted K3,2 minor model. The images may depend arbitrarily
on the whole graph.

Choose a spanning tree inside each branch set and let C be the union of
its edge indices. Delete all other edges except one of the six required
links. Ignore vertices outside the five branch sets; their unused
potential directions impose no additional condition. Contract C.

The following coordinate elimination works over every field. In each
root branch, a tree edge expresses a nonterminal potential in terms of
its parent potential. Successively eliminate leaves, with coefficient
+1 or -1. This leaves the terminal potential as that branch's common
potential. In each hub branch, retain one free representative potential
H or K and eliminate the other potential coordinates in the same way.
There are no equations between different branch sets. There is at most
one prescribed terminal in each tree, by disjointness and root placement.
Consequently E,F,G,H,K are independent in the quotient. In particular
E,F stay independent, as required by the contraction lemma. This is a
field-independent elimination, not an inference from modular tests.

Orient the six retained links to obtain

    H, E+G-H, F+G-H, K, E+G-K, F+G-K.

Together with g,d,t these are exactly the nine queries of PR3583.
Any transfer of the graph would therefore induce one for that minor,
contradicting the retained all-characteristic-two obstruction in
[predecessor/PROOF.md](predecessor/PROOF.md). This is an actual inherited
mathematical premise. Its original source, exact bytes and credit are
recorded in ORIGINS.json, and its seven integral separators and fourteen
reader identities with denominator dividing two are rechecked here.
The new proof does not claim independent human or formal acceptance of
that premise.

## Consequences and boundary

Every graph obtained by subdividing any or all six edges of the original
K3,2 any finite number of times has such a rooted minor. Assign each
path's internal vertices to the branch set at one endpoint, contract all
but its last edge, and retain that edge as the required link. Thus long
paths, extra edges and more general connected branch sets cannot repair
this support-transfer method. This closes the subdivision/minor gap left
explicitly open by PR3583 without searching an unbounded graph family.

The result is a sufficient obstruction. It does not characterize all
transferable graphs, prove that K3,2 is edge-minimal, exclude every cycle,
or show that the absence of this rooted minor is sufficient for transfer.
It does not prove a literal support-tariff minimum or carry PR3583's
42-port factorization to every graph. A support-transfer obstruction is
not a counterexample to a universal pair-reader tariff floor.

The original coverage-law task is changed to this released proof-method
question. Family decision: retain this obstruction and stop. No native
construction or dependent optimization round follows. Query acquisition,
coefficient execution, dirty restoration, frames, hosting, precision,
stock, all-size/compiler admission, complete consumers, both supplier
invoices and the full multiplication theorem remain unproved here.
No new kappa or selected-frontier change is claimed.

## Finite verification and its limits

The verifier checks ten explicit minor models, including the original
six-edge graph, each individual one-edge subdivision, all six edges
doubled, unequal path lengths up to three, and a branched model with extra
chords and an unused vertex. A rooted-minor certificate is checked before
constructing the old geometry. The implementation derives the contracted
spanning forest and an explicit quotient projection independently of any
subset predicate result.

For each model, the projection kills the contracted forest, has the
complementary rank over Q,F2,F3,F5, preserves independent quotient marks,
and maps the nine retained queries to the original configuration. Every
one of the 512 surviving query subsets is then checked in both marked
orientations over Q,F2,F3, for both the reader predicate and the source
exclusion. F2 is an algebraic quotient control, not an old-field instance
of the obstruction. Integer elimination and modular elimination use
different row updates. RESULT.json records the complete ordered predicate
stream hashes and dimensions.

The finite checks do not prove the all-field or all-graph quantifiers.
The contraction lemma, tree elimination and inherited obstruction above
supply those quantifiers. The mutation controls reject malformed minor
certificates, lost source binding, incorrect projection and a false
receipt through the actual optimized command. Independent human and
formal proof-kernel review are unclaimed.

Credit retains Nick Petalas's PR3583/3573 and their actual-reader lineage,
Philippe Van Velzen's expanded identity, and ctoth's coverage question.
The new result is the marked contraction lemma and its terminal-rooted
forbidden-minor consequence. Apache-2.0.
