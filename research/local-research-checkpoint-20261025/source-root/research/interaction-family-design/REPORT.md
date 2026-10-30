# Interaction-family design: geometry and producer costs must be chosen together

Douglas Colkitt, with OpenAI Codex assistance. October 9, 2026. Apache-2.0.

**No new supplier or multiplication exponent. This design pass finds a
missing restriction on the attractive hypothetical budget and rejects a
concrete alternative scalar identity. A broad matrix search is not yet
justified.** The selected conditional witness remains
`κ=0.000661885549259598`.

The [shared-core preparation](../shared-core-blocks/REPORT.md) established
an arithmetic target and a conditional rank-r cover. It did not provide
labels, a scalar identity, or a producer attaining its histogram. Here we
couple those missing parts before choosing an expensive search.

**Follow-up:** the [bounded boundary-readout round](../boundary-readout-sixteenth/REPORT.md)
has now tested deferred cleanup and direct nonzero-frame target readout.
Neither supplies a cheaper recursive profile. Its endpoint obstruction
permits crossing the intermediate invocation boundaries; neither proposal
is an outstanding construction target.

## 1. The precise model being screened

There are v scalar source labels, with rank-r idempotent address labels in
dimension d. A scalar central matrix C has diagonal one. Its noncentral
correction is `I−C` (the same as `I+C` over F2). For every off-diagonal
nonzero entry of C, the corresponding pair of address idempotents must
mutually annihilate. Define the undirected graph G by the union of the
two directed supports. Let `k=rank(C)` **in the scalar field**.

For the producer-cost screen, further assume a factorization through
separate scalar central channels. Each used channel is assembled at a
frame containing the address blocks of its source support, then copied
to frame zero for readout. Every such nonempty support has dimension at
least r. There are at least k used channels, so

`L_aux ≥ kr`.

This is a conservative-source-span copied-center contract, not a universal
lower bound on implementing C. Reusing storage does not erase the paid
reads; a construction that changes their frame transitions or permits
different source evolution must be analyzed separately. The separate-bank
version also has `R≥k`. The screen does not assume that rank is a complete
description of the producer: actual source spans, scalar work and restoration
can make its cost much greater.

Moment comparisons below retain zero entrance gauges and minimum-rank data
paths. Nonzero gauges need their actual histogram, as in the preceding
report. Arbitrary rational frame networks, different boundary contracts and
non-conservative cancellation producers are outside these exclusions.

## 2. Two structural screens for a proposed interaction graph

### Short odd cycles restrict block rank

Suppose `U_0,...,U_(2j)` are the images of rank-r idempotents around an odd
cycle of length `2j+1`. Both neighbors of a vertex lie in its kernel, which
has dimension `d−r`. Thus

`dim(U_i ∩ U_(i+2)) ≥ 3r−d`.

The Grassmann distance `δ(U,V)=r−dim(U∩V)` obeys the triangle inequality
on r-dimensional subspaces. Following the even-indexed path from U_0 to
U_(2j) gives distance at most `j(d−2r)`. Its endpoints are adjacent and
disjoint, so their distance is r. Consequently

**`r/d ≤ j/(2j+1)`.**

This works over either address field and does not require self-adjoint
idempotents. At `r/d=9/19`, the graph can have no odd cycle shorter than
19. Merely removing the seven-clique is insufficient. Exact coordinate
cycle controls attain equality; they certify the inequality's sharpness,
not useful noncommuting circuits.

Even with no auxiliary roles or loss, the zero-gauge bare data moment at
the bit target 0.08 fails throughout `0≤r/d≤1/3`: its concave function has
both endpoint values above one. Hence every target-capable graph in this
specified model is at least triangle-free. Near-half rank is needed for
the *one-auxiliary-per-label* budget, not for every possible role inventory.

### Sparse interaction can force expensive central rank

An independent set of G induces an identity principal submatrix of C.
Therefore `k≥α(G)`. If G is triangle-free, each neighborhood is independent,
so every vertex has degree at most k. Greedy coloring then uses at most
k+1 colors; one color class has at least `v/(k+1)` vertices. Thus

**`v≤k(k+1)`**, and **`k≥min{q:q(q+1)≥v}`**.

These bounds apply even to nonsymmetric C and over any scalar field.
They do not compare ranks across fields. A verified coloring with q colors
also gives the useful screen `k/v≥1/q`.

The elementary triangle-free Ramsey induction improves the port bound to
**`v≤f(k):=k(k+3)/2`**. Indeed, if an independent set has size at most k,
each neighborhood has at most k vertices. Nonneighbors of any vertex have
independence number at most k−1. Starting with f(0)=0, induction gives
`v≤1+k+f(k−1)=f(k)`. This bound is still far from sharp in general.

Combining geometry and the copied-center contract:

`λ := L_aux/(vd) ≥ (r/d)(k/v)`.

High odd girth alone is not enough. A low-colorable graph can have excellent
near-half-rank labels and still force an unaffordable copied central map.
In particular, bipartite and cycle-colorable candidates should be checked
here before attempting rational matrix synthesis.

### Centers of minimum width cannot mix distinct source images

There is a further source-span restriction. Let K be the number of used
copied scalar channels, and b the number whose source span has dimension
strictly greater than r. Then `L_aux≥rK+b`. Each of the other K−b channels
is supported entirely on a single class of labels having the same source
image. Two labels in such a class cannot mutually annihilate, so the
principal central matrix on the class is an identity matrix.

For a class touched by a width-r channel, let K_g count those channels.
Its size is at most `K_g+b`, by restricting the central factorization to
that identity submatrix. There are at most K−b touched classes. The
remaining vertices receive central contributions only through the b wider
channels; their central principal matrix has rank at most b and still has
triangle-free support. The Ramsey bound limits them to `f(b)=b(b+3)/2`
vertices. Summing gives the stronger joint condition

**`v≤K(b+1)−b(b−1)/2`, `0≤b≤K`, `L_aux≥rK+b`.**

This does not require K independent channels, and can be stronger than
substituting scalar rank alone. The checker minimizes this integer relaxation
over K and b exactly. It uses a binary search for the least b at each K,
and stops when rK is already no smaller than the best loss. The scope remains
literal conservative source spans and copied readout.

## 3. Candidate A: change the central/side support of the working identity

**Mechanism.** Start from the bit incidence identity on triples,
`C_ST=|S∩T| mod 2`, and change which off-diagonal coefficients are routed
through the central map. Concretely, a support mask gives

`C'_ii=1`, `C'_ij=mask_ij C_ij`, and `C'+(I+C')=I` over F2.

Restricting to a selected subfamily of triples is a second, more structured
version. Refactor C' over F2, then implement its side correction with the
required block annihilations. An arbitrary mask preserves the displayed
scalar identity, but **does not preserve low rank, the incidence producer,
or a characteristic separation**. Those become explicit acceptance tests.
Regrouping the old correction without changing its coefficient support does
not remove any pairwise annihilation obligation in this support model.

**Why consider it.** It retains a precise identity, an inherited dirty-input
completion pattern and a known producer starting point. The output sought
is a changed coefficient matrix and paid circuit, not just a favorable graph.
It lies outside the fixed-support/fixed-boundary frame optimization already
closed in earlier audits. A modern block-core compiler is still required.

**Immediate exact experiment, now completed.** Test the proposed
`d=19,r=9,v=250,R=250,L=19` budget against the two screens above. Triangle
freeness forces `k≥16`, so copied centers alone require `L≥144`.
The optimistic raw bit moment with that loss is **at least 1.0091494922**.
Thus no support mask or choice of rational block labels in this copied-center
model can realize that attractive 250-port histogram.
The stronger source-span/Ramsey screen requires loss at least **209**, giving
moment at least **1.0141299377**.

This corrects no arithmetic in the preceding preparation: its histogram
still passes. It shows why a histogram is weaker than a feasible local core.

**Scale necessary for a larger attempt.** At `r/d=9/19`, `ρ=R/v=1` and
bit saving 0.08, the ideal zero-gauge moment allows only

`λ < 0.005176757665...`, hence `k/v < 0.010928710626...`.

The graph must have chromatic number at least 92 and odd girth at least 19.
Combining the integer rank/port and loss inequalities requires **at least
8,327 ports**. If we retain the illustrative loss ratio `λ≤1/250`, the
minimum rises to **13,974 ports**, with k at least 118 at that first scale.
Accounting also for the widths of individual central source spans raises
that last necessary scale to **33,908 ports**, using the elementary Ramsey
bound as well. These remain weak necessary
bounds, not constructions or sufficiency; the large graph, compatible
blocks and actual producer have not been supplied.

**Decision.** Do not launch a small-label kernel search or random edge-mask
search at the 250-port budget. Keep support redesign as the primary mechanism,
but require a structured scalable formula and a producer-cost certificate
before expanding it to thousands of ports. A high-girth mask with a large
central rank fails the purpose of the experiment.

## 4. Candidate B: a different characteristic-sensitive identity on folded cubes

**Explicit family.** For odd `q≥5`, take vertices `F2^(q−1)` with generators
the coordinate unit vectors and the all-ones vector. Let A be their Cayley
adjacency matrix and `C=I+A`. The side correction A gives `C+A=I` over F2.
This is a different scalar relation from triple incidence.

The q commuting involutory shifts give `C²=(q+1)I=0` over F2. For q=5,
C has binary rank 6 but rational rank 16, checked by exact elimination.
Thus this seed has a real field-dependent rank gap, not just a routing gap.
Its odd girth is q: an odd closed walk reduces to an odd subset of generators
with zero sum, and their only nonempty dependence is the set of all q.

**Completion proposal.** Factor C in the binary field, use the side edges
for A, and apply the inherited dirty-response subtraction, forward read,
literal inverse and cleanup. That proposes an all-role local word conditional
on compatible blocks and actual frame paths. No block representation or
competitive completion is asserted here; the following lower bound makes
constructing one unnecessary for this producer model.

**Exact central-rank cost.** Put D=q−1. For every even `D≥2`,

`rank_F2(C_D)=2^(D−1)−2^(D/2−1)`.

Here is a direct recurrence proof. Split off the last two coordinate bits
and write `E=I+Σ_(i≤D−2) S_i`, `B=Π_(i≤D−2) S_i`, so E²=B²=I and EB=BE.
The four-by-four block matrix is

```
[ E  I  I  B ]
[ I  E  B  I ]
[ I  B  E  I ]
[ B  I  I  E ].
```

Pivot on the identity in block position (1,2). The residual is, with
`F=E+B=C_(D−2)`,

```
[ 0   F  EF ]
[ EF  F   0 ]
[ F   0   F ].
```

Factoring the commuting F, elementary invertible block operations turn
the coefficient matrix into `diag(I,I,0)`. For example, use the 1 in its
first row/second column, subtract that row from the second row, then use
the 1 in the third row/third column to eliminate E from the second row.
Thus `rank(C_D)=2^(D−2)+2 rank(C_(D−2))`; the base C_2 is the all-ones
four-by-four matrix of rank one. This proves the formula. Independent binary
elimination checks q=5,7,9,11. Rational eigenvalues are
`1+D−2w+(−1)^w`, with multiplicity `binom(D,w)`; rational invertibility is
not claimed for every q.

**Rejection before frame search.** For all q≥5, `k/v≥3/8`. Hence the
separate copied-center model has `ρ≥3/8` and `λ≥3t/8`, where t=r/d≤1/2.
Grant minimum data cost, ideal packing and free side roles. At `ρ=3/8`,
the resulting optimistic moment is concave in t. At t=0 and t=1/2 its
bit values are respectively **1.0918668996** and **1.0510355403**; both
complex values also exceed one. Extra ungauged roles have cost `3^s>1`
per role and cannot repair a failure by increasing the denominator.

**Decision.** Reject this entire folded-cube family with the specified
copied-center compiler for the two target savings. Do not search its block
matrices. Larger odd girth and a genuine rank gap did not make central
readout affordable. This is not an exclusion of a different producer for
these graphs or all characteristic-dependent identities.

## 5. What the design pass recommends next

The most useful next question is **whether the producer can change the
copied-center cost**, before investing in a large interaction-family search.
Joint support and role-stock design remains useful, but reducing stock alone
does not rescue the first smaller-block diagnostic below. Any reduction must
come from an actual accumulation or completion schedule; it cannot be inserted
into the denominator for free.

For orientation, this alternative *unimplemented* local inventory passes
the raw moment test:

`d=5,r=2,v=1000,R=200,L_aux=100,L_data=0`, zero gauges,

`H={5:220}`, `D=T={3:1000}`.

Its complete profile has `m=15,W=2200,Δ=3700`; raw moments at 0.08 and
0.075 are **0.9990555745** and **0.9917100095**. The graph must still be
triangle-free, but 5-cycles are now allowed. The central rank floor is 32,
using only the weaker degree bound; the Ramsey bound raises it to 44.
The joint source-span screen actually requires **loss at least 123**, exceeding
the proposed 100. Even granting ideal packing of that corrected loss, the
bit moment is **at least 1.0013385689**. Thus this alternative also fails
the copied-center model. It is a rejected arithmetic diagnostic, not a new
target claimed to be feasible. This is exactly the kind of attractive
histogram-only proposal the design process is meant to catch.

The proposed next bounded round should use the following gates, in order:

1. **Specify a scalar identity and its required support.** Supply C and its
   factorization, or a different explicit circuit relation. Check independent
   sets, neighborhoods, short odd cycles and any available rational-lift
   obstruction. Do not select a graph on visual appeal alone.
2. **Specify the source-support producer and independent stock together.**
   List the support of each copied center and each reused original target.
   Compute the real support-span losses, not merely `kr`. Start with the
   supported terminal-accumulation interface; any new internal reuse needs
   its own arbitrary-dirty-input and cleanup proof. Do not reopen the retired
   clean-aggregate or matched-encoding model under unchanged assumptions.
3. **Only then synthesize exact block labels.** Start from a parametrized
   noncommuting family, check both directions of annihilation, form type,
   all common gate frames and the entire child histogram. A small instance
   must demonstrate an actual mechanism, not merely an attractive rank ratio.
4. **Expand only after a paid profile survives.** Set a one-round stop after
   at most two specified identity/producer pairs. If neither has a plausible
   complete budget, return to the producer/completion architecture rather
   than increasing an unconstrained matrix-search budget.

Candidate A remains the more useful lead because it starts with working
algebra and a producer to modify. However, this pass has **not selected a
surviving concrete interaction family**. Both briefed small options fail
before matrix synthesis. Stop the proposed broad family search here.

The next experiment, if authorized, should present a literal modification
to a working producer that avoids a separate conservative-span copy to zero
for each central channel, and charge its readout, changing data frames and
arbitrary dirty restoration. Alternatively it must give a scalable algebraic
family with enough advantage to pay these costs. A retained nonzero readout
frame or shared readout is only a proposed mechanism until it passes those
checks; neither has been constructed in this pass. Do not launch more generic
kernel searches or claim that fewer scalar additions would suffice.

This is a recommendation to change the mechanism under examination, not a
claim that κ=1/16 is near. No goal loop or long search was started.

## 6. Literature boundary, validation and provenance

Bukh and Cox give fractional Haemers representations and characteristic
separation constructions. Their p=2 subset construction returns the triple
incidence mechanism already in this project; their block formalism does
not supply a paid completed producer. These observations motivate screening
the scalar and geometric sides together, not importing a graph parameter
as a multiplication supplier. See their [paper, sections 2 and 4](https://arxiv.org/html/1802.00476v2).
The elementary screens and folded-cube calculations above were derived in
this pass; no priority claim is made for these graph or rank facts.

`audit.py` uses exact binary/rational elimination and rational power
enclosures. Nine tests include all 4,096 diagonal-one directed binary
four-by-four supports, a triangle counterexample to dropping the triangle-free
hypothesis, brute-force integer-scale controls, independent rational
elimination of the 16-vertex folded cube, grouped-channel controls on all
three-by-three binary central matrices, and replay of the saved certificate.

```sh
python3 -B research/interaction-family-design/audit.py --check research/interaction-family-design/certificate.json
python3 -B -m unittest discover -s research/interaction-family-design -p 'test_*.py'
make selected-record-check
```

The selected supplier and all production verifiers remain unchanged. The
analytic-domain, generic-basis, all-size, precision and fixed-tape obligations
from the preceding preparation remain open for any new target-scale supplier.
