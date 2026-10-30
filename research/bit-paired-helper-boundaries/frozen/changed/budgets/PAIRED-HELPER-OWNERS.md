# Arbitrary dirt at a paired entrance and dedicated whole-bank owners

Scientific pin `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
This is a conditional algebraic hosting lemma, not a new supplier or kappa.
It uses the dedicated cover-bank model of the retained PR386 BIT geometry.
It does not apply automatically to a public-family pending-window allocation.

## The entrance is a coordinate interpretation

Suppose a literal BIT word is checked for every independent logical source,
target and helper input, with helper h entering at E and leaving at U.
Suppose its complete logical helper row is h and its public output has zero
coefficient on h over F2. Write D_E,D_U for the actual ADDRESS operators.
Given an arbitrary physical helper array u, set h=D_E^-1 u in the proof.
There is no instruction to execute D_E on u. The word then has physical map

    u -> D_U D_E^-1 u,

and its public output is independent of u. This also holds for correlated
entering arrays, since the independent-column identity holds pointwise for
every joint input. For the nested BIT pair E subset U, the residual is exactly
D_(U intersect E-perp), of rank dim(U)-dim(E).

If instead one insists that the old ZERO-frame logical h must be the same
physical array u, implementing a new E interpretation by an explicit D_E
does cost a query. That is an extra identification, not a universal requirement
of a paired arbitrary-dirt contract. A useful caller must still host the actual
residual and pay all ADDRESS adapters, accesses and private work.

## A dedicated cover-bank construction

Let m be at least the complete local footprint, including spectator axes.
All source/target families are separate from these ordinary helper banks.
Let the finite cover group G contain each required ADDRESS adapter and act
on doubled BIT addresses by diag(g,g), so it centralizes D_I_m. For the
coordinate residuals below, the original orthogonal cover already contains
the required coordinate permutations. A physical family is a pair (bank,g),
with g in G; distinct cover classes mean distinct stored physical families.

For each role j in one bank, choose disjoint coordinate blocks I_j. The
role's exact residual must be conjugated to D_Ij by an explicit adapter Pi_j.
At local cover invocation d, assign the role to physical family

    (bank, g=d Pi_j^-1).

This gives a bijection between the d invocations and g owners for each role.
Require Pi_j != Pi_k for distinct roles in the same invocation and bank.
Then g differs as well, so two such helpers do not alias a physical family.
Different banks, and all public families, are disjoint by construction.

At any fixed physical owner g, the assigned endpoint actions are the
conjugates by g of the disjoint block interchanges D_Ij. Their product is the
interchange on their union, independently of their chronological order.
Each invocation accepts the actual arbitrary array produced by all preceding
ones. Add and charge a native padding query on the uncovered coordinates.
The final action is D_I_m, which commutes with every common ADDRESS chart.
Run each entire local call before beginning the next; no intermediate helper
state is exposed to another invocation. The source-call order is preserved.

The unused spectator coordinates in a role's *local* footprint need not form
a globally reserved untouched block of the owner. They can lie in another
role's residual block. The exact endpoint acts as identity on those spectator
coordinates, and the next invocation accepts arbitrary correlated input.
No simultaneous reuse of one physical family is permitted by this argument.

For a concrete coordinate example, let m=36 and residual width6 with a
two-axis entrance E, giving local footprint8. Split the owner into six
successive width6 blocks. Pi_j is a cyclic shift by6j, mapping the residual
axes to block j and the two entrance axes to the first two axes of block j+1
(indices cyclic). These six permutations are distinct. All six residuals
are disjoint and fill36; no spectator padding query is needed. The local
two spectator axes are nevertheless present in every invocation. This is a
cover-bank construction, not a claim that six roles fit an unrelated
public-source window or that a helper may be used twice simultaneously.

For the checked coordinate-E2 word, there are318 width6 and111 width8 roles
per call. At m36, using12 replicas makes all dedicated groups integral:
636 width6 banks with six roles each;333 width8 banks with four roles each.
The latter each pay a rank4 padding query. Thus per call/replica the ordinary
stock is318/6+111/4=323/4 and padding histogram is(111/4) H4.
The local helper rank mass is318*6+111*8=2796; adding padding111 gives
2907=36*(323/4). This checks only the helper-bank part of an invoice.

## Scope and missing integration

The local dirty-column identity and native residual must be established
before this lemma applies; a nullspace dimension or narrower span is not
enough. Every Pi must preserve the actual allowed cover and have a paid
implementation. The local footprint, simultaneous-family exclusion and
separate public/private stock are hypotheses. Public source windows,
pending prefixes and recycled data owners require their own literal
allocation. The lemma does not admit rational GL internal queries into a
narrower recursive alphabet, establish precision/tape bounds, or repair the
global E2 hybrid's failed public-coverage budget.

The stabilizer worker independently reviewed the coordinate interpretation,
cover assignment, spectator overlap and integer bank counts. Its centrality
hypothesis clarification is incorporated above. The finite cyclic-cover
fixture `paired_owner_fixture.py` checks all72 coordinate columns for each
of six owners, all36 assignments and three actual defect controls; it is
separate from the written arbitrary-cover argument.

Credit the retained PR386 dedicated whole-block cover-bank construction and
the paired-entrance/terminal lineage in PR2857 and PR2908. The present
derivation applies arbitrary-input coordinate interpretation to the new
literal BIT kernel words and makes the spectator-overlap condition explicit.
Substantial OpenAI Codex assistance; Apache-2.0. All work remains local.
