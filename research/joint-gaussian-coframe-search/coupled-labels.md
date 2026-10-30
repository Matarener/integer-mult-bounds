# Coupled helper endpoints and transported coframe menus

## Both helper endpoints may change

Use the complete signed objective J=paid moment minus productive moment. After aggregating terms on each variable pair, let a pair table have interaction

    q_ij=e00+e11-e01-e10.

It is submodular exactly when q_ij<=0. Paid common-anchor distance tables have nonpositive q. A productive helper table enters with a minus sign and may have positive q when both of its endpoints vary. It cannot be discarded or treated as two independent upgrades.

**Theorem 1.** Complementing one binary variable changes the sign of every incident interaction. Thus the complete energy is reducible to minimum cut by variable complements if, in the graph of nonzero interactions, every cycle contains an even number of positive interactions.

**Proof.** Exchanging rows or columns of a two-by-two table changes q to -q. Choose a complement bit epsilon_i for each variable. Require epsilon_i xor epsilon_j=1 when q_ij>0, and zero when q_ij<0. Choose one bit in each connected component and propagate these equations along a spanning tree. A non-tree edge is consistent exactly when the xor around its cycle is zero. This is equivalent to the stated even-positive-edge condition. All resulting interactions are nonpositive, so Theorem 4 of coframe-cut.md applies, with transformed unary terms and the same complete target invoice. QED.

This is the classical signed-graph switching argument applied to the actual paid/productive energy. Its application must use aggregated interactions: two source records on the same pair may cancel or change a sign.

**Theorem 2.** Suppose S is an explicit set of variables whose deletion leaves a switchable interaction graph. The exact minimum over the original family is the minimum of at most 2^|S| ordinary cut problems.

**Proof.** For each assignment on S, substitute its bits into every table. A table with one remaining variable becomes unary and a table with no remaining variable becomes constant. The other pair interactions are unchanged and are switchable by assumption. Solve their cut problem exactly. Every full assignment occurs in exactly one branch, so taking the best branch gives the exact global minimum. QED.

A small such S is a useful computational target. No claim that it is small in the retained source is made. Choosing all variables always gives a finite exact procedure, while a discovered small set gives a concrete speed advantage.

## Common-anchor expansion moves

An eligible vertex may have a finite menu of explicit Clifford charts. At a current assignment H_i, fix one common proposed anchor H_star and allow each vertex either to keep H_i or move to H_star. All paid identity-transport tables are submodular by the metric triangle inequality. Helpers with one varying endpoint are unary; helpers with two varying endpoints are handled by Theorems 1–2.

**Theorem 3.** The optimal simultaneous common-anchor expansion is computed by one cut under the unary-helper hypotheses, or by the stated finite collection of cuts under Theorem 2. Repeating strict improving moves through a finite menu terminates.

**Proof.** The binary expansion has exactly the four distance entries in coframe-cut.md. Its triangle inequality proves submodularity. The complete target terms are included by the preceding signed construction. Strict decrease forbids revisiting a complete assignment; there are only finitely many. QED.

This theorem gives the best move for the selected anchor, not a claimed approximation factor or global optimum over a larger multi-label problem. An unavailable anchor at a vertex means fixing its bit at zero. Every allowed transition must also satisfy the recursive rank cap.

## Fixed logical Clifford transports

Some instructions, such as an actual thin query, are not free native letters and must retain their logical Clifford R_e. With source coframe H_u and destination coframe H_v, execute

    H_v R_e H_u^(-1).

Its Gaussian rank is

    d(Lambda_u, S_Re^(-1) Lambda_v).

This follows by the same intersection argument as Lemma 2 of coframe-cut.md. All four binary costs must be computed for this actual twisted distance. A triangle inequality for the untwisted problem does not automatically prove that table submodular.

**Lemma 4.** A common anchor Lambda_star invariant under S_Re makes this paid binary table submodular.

**Proof.** Its 11 entry is zero. Its 10 and 01 entries are the powered distances from the two old endpoints to the same anchor, after applying S_Re where appropriate. Invariance and the triangle inequality bound the 00 entry by their sum. QED.

This is a sufficient test on an explicit anchor and explicit transport. A shared invariant Lagrangian is not assumed to exist for all actual caller instructions.

## Concentrate transport into cycle edges

There is another way to organize fixed logical transports without changing them. Regard the instruction-incidence graph as an oriented graph with symplectic transport R_e on edge u -> v. Choose a spanning forest. Set K at each root to identity and along a forest edge set

    K_v = R_e K_u.

Use the inverse equation when traversing an edge backward. For each vertex write its candidate inverse Lagrangian as Lambda_v=K_v L_v.

**Theorem 5.** In these transported coordinates, the rank cost on edge e is

    d(L_u, T_e L_v),
    T_e=K_u^(-1) R_e^(-1) K_v.

Every forest edge has T_e=I. Only non-forest edges can retain nontrivial cycle transport.

**Proof.** Symplectic maps preserve intersection dimensions. Apply K_u^(-1) to both arguments of d(K_u L_u,R_e^(-1)K_v L_v). The displayed expression results. The defining equation for a forest edge makes its residual identity. QED.

Use actual Clifford words, not only their symplectic labels, to specify K and every new lift. All phases, final normalizers and word lengths remain in the finite physical recipe. This change of variables does not execute a cost-free K at runtime.

**Corollary 6.** For a binary common-anchor expansion in the L coordinates, choose a set S meeting every nontrivial residual edge and every bivariate helper target edge. After fixing S, every remaining paid pair is an untwisted metric table and every remaining helper target is unary. The complete optimum is obtained by at most 2^|S| cuts, provided every branch satisfies the physical and rank legality conditions.

**Proof.** Every exceptional edge has a fixed endpoint, so it is at most unary. The other paid edges have T_e=I and are submodular. Apply Theorem 2, or directly enumerate the assignments on S and solve the remaining cuts. QED.

The number of non-forest edges is E-V+components before ignoring trivial residuals. This gives a transparent finite branching bound, not evidence that a particular source has low cycle rank. Compress identical variables and aggregate parallel source records before choosing the forest.

## Use in the Gaussian program

There are now three concrete families: freeze nonordinary native endpoints and optimize safe fibres; specialize the universal native letters to identity and pay their metric transitions; or retain fixed logical transports and move their complexity to explicit cycle edges. All three return actual complete words by the re-gauging theorem. None identifies two independent inputs, hides a Gaussian in an ordinary gauge, or credits the same helper twice.

The mathematical ingredients are standard metric, graph-cut and gauge-switching arguments. The new contribution is their explicit joint use with the source's full signed Gaussian bill and recursive legality constraints. Compare against prior work before claiming project-wide novelty. Credits follow README.md and the retained transported-frame and symplectic source lineage.
