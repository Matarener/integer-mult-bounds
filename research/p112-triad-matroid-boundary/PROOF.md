# Gauge, transfer and five-term triple boundary for the fixed triad mask

Exact scoped results on the fixed PR2757 full-group mask. These results do
not cover fits of higher matrix rank and do not change the selected bound.
The normal form is prior work in `p112-rational-decoder-gate/RANK-TIGHT-PROOF.md`;
the point here is its explicit conjugacy consequence and the resulting precise
scope of newer fixed-matrix transfer theorems.

## Hypotheses and source geometry

Use the 37 orthonormal triads G1,...,G37 and residual line G0 in the pinned
CANDIDATE.json, SHA256
`dc5fbe51f9cd3a14361256ac136736bffb18971d0247b891accf0d2ee060d06b`.
Each scalar port in Gg carries the entire binary physical space Eg. An
off-diagonal block Kg,h is allowed only if Eg is orthogonal to Eh; diagonal
blocks are cI with the SAME c!=0. All coefficients are rational.

Let I consist of the 19 odd groups, dimension 57. Let J consist of the residual
line and 18 even groups, dimension 55. The literal binary geometry has:

1. No orthogonal pair of distinct odd groups; hence KII=cI57.
2. The allowed odd neighbors of each even group 2i are {2i-1}, except group 24
   has {3,23}. The residual line has odd neighbors {15,27}.
3. E4 is not orthogonal to E24, and E0 is not orthogonal to E28.
4. E0 is orthogonal to E15 and E16.

The independent checker reconstructs these facts from the literal nine-bit
labels. They are the exact geometry needed for the normal form, rather than
an assumption that all matched pairs are isolated in the original mask.

Normalize c=1 by dividing K and one factor family by c. This changes neither
factor supports nor charges. Write K=[I A; B D]. Assume rank_Q(K)=57.
Block Gaussian elimination implies D=BA. No rank assumption on the number
of rank-one terms in a chosen factorization is made.

## The extra odd-neighbor couplings vanish

At even group 4, the only possible term in its diagonal BA block is

    B4,3 A3,4 = I3.

Thus both matrices are invertible. The forbidden blocks K4,24=K24,4=0 give

    B4,3 A3,24 = 0,      B24,3 A3,4 = 0,

so A3,24=B24,3=0. Group24 now also has just its matched odd neighbor23.
For every matched pair Oi=G(2i-1), Vi=G(2i), i=1,...,18, define

    Ai=K[Oi,Vi],      Bi=K[Vi,Oi].

The corresponding diagonal BA equations give Bi Ai=I3, hence Ai,Bi are
invertible and Bi=Ai^-1. No symmetry of K is assumed.

For group 28 the same argument gives B28,27 and A27,28 invertible. Because
the residual/28 blocks are forbidden,

    B0,27 A27,28=0,      B28,27 A27,0=0.

Therefore B0,27=A27,0=0. Let a=A15,0 be a3-by 1 column and b=B0,15 a1-by 3 row.
The remaining residual diagonal equation is ba=1. In particular both are
nonzero. The residual's only nonzero possible off-diagonal blocks are now

    K15,0=a,   K0,15=b,
    K16,0=B8 a,   K0,16=b A8.

Every other even/even or residual/even entry of D is determined by BA.
There are no remaining free entries in D: the rank 57 Schur equation already
fixes it, even at positions where the original strict mask would allow freedom.
The last odd group G37 is an isolated identity block.

Conversely any invertible rational Ai and any rational a,b with ba=1 give
this rank 57 fit. Its only nonzero off-diagonal blocks are between physically
orthogonal groups listed above, so it is legal under the full original mask.

## Explicit block-diagonal conjugacy

Choose a desired residual axis r in {0,1,2}, and let er be its coordinate vector.
Because ba=1, choose an invertible rational3-by 3 matrix T whose column r is a
and whose other two columns form any basis of ker(b). Then

    T er=a,       b T=er^T.

Equivalently P=T^-1 satisfies Pa=er and bP^-1=er^T.
This is constructive: choose p with bp!=0; the two vectors
ej-(bj/bp)ep for j!=p form a basis of ker(b). Insert a as column r.
Independence follows by applying b to a putative column relation.

Define an invertible112-by 112 block-diagonal rational matrix S, respecting
the physical groups, as follows:

    S0=1; S37=I3;
    SOi=I3 and SVi=Ai for i!=8;
    S15=P and S16=P A8.

Then the paired off-diagonal blocks of SKS^-1 are identities. The residual
blocks become er and er^T, on both G15 and G16, and its diagonal remains1.
Thus

    SKS^-1 = Kr = Rr Rr^T,

where Rr repeats each of 18 three-coordinate latent blocks into its two paired
triads, places the final three coordinates in G37, and places latent coordinate
21+r in G0. These57 columns are disjoint nonzero indicator vectors.

This uses conjugation, not a congruence. A nonsymmetric rank 57 fit generally
needs different transformations on the two rank-one factor families.

## Every term keeps exactly the same physical charge

For ANY finite rational factorization K=sum_t ut vt^T, set

    u't=S ut,       v't=S^-T vt.

Then Kr=sum_t u't (v't)^T. Each block Sg and Sg^-T is invertible, so ut is
zero on an entire group exactly when u't is, and the same holds for vt,v't.
Consequently both complete binary support spans, their rectangular pairing
matrix, and the tariff of each term are unchanged. This applies to arbitrary
denominators, asymmetric factors, arbitrary term counts, exterior directions,
zero terms, and cancellation outside the fitting matrix's row/column spaces.
The inverse transformation has the same property.

Individual scalar-coordinate supports may change. The conclusion depends on
charging COMPLETE physical groups, and need not hold for singleton-label cost.
No physical implementation of the rational gauge is asserted or charged: this
is an exact change of variables used to transfer lower bounds, not a proposed
native preprocessing operation.

## The two residual-axis conventions

The literal `p112-rational-decoder-gate/CANDIDATE.json` has its residual in
factor 21, support {9,39,55}; this is r=0. The six-mode package instead defines
the canonical residual at latent column 22, support {23,62,55}; this is r=1.
Both use exactly the same physical groups G15={9,23,33}, G16={39,62,110}.

Simultaneously swap coordinates0 and 1 within G15 and G16, leaving all other
groups unchanged. The resulting block permutation S satisfies

    S K0 S^-1 = K1.

Therefore both canonical matrices have the same set of achievable whole-group
tariff totals. For a theorem restricted to particular exterior directions,
those directions must be transformed too: an axis 0 exterior direction becomes
axis 1 under this swap. The six-mode theorem must NOT silently keep its
exterior direction fixed while moving the residual axis.

## Exact transfer of the characteristic-two obstruction

Fix one such gauge S for an arbitrary rank 57 fit. Its canonical factors pull
back to two generally different distinguished target lists

    alpha_j=S^-1 rj,       beta_j=S^T rj,
    K=sum_j alpha_j beta_j^T,

where rj are the 57 disjoint columns of Rr. They are gauge-adapted targets,
not the original literal indicator columns in the ungauged coordinates.

If the labelled column matroid of [v_t; beta_j] is representable over any
characteristic-two field, so is the matroid of [S^-T v_t; rj], since an
invertible rational coordinate map preserves every indexed-subset rank.
Likewise [u_t; alpha_j] is equivalent to [S u_t; rj].

The source-zero/reader-span transfer in Nick Petalas' PR3505
`p112-matroid-reader-transfer/PROOF.md` only needs the disjoint canonical
target indicators. It works here without an even-group hypothesis. Expansion
by each complete physical port Gram block sends Kr toI334: all off-diagonal
nonzero entries join orthogonal group spaces, and each diagonal contributes
I3 orI1. Each expanded term has rank at most its binary whole-group tariff
over every characteristic-two extension. The same support-preserving
transfer and rank subadditivity therefore give

    sum_t tariff(ut,vt) >=334.

Hence any rank 57 fit admitting a decoder of cost<334 requires BOTH augmented
gauge-adapted configurations to be nonrepresentable over EVERY
characteristic-two field. This is a necessary escape from this sufficient
obstruction, not a sufficient criterion for a saving. The gauge is chosen
explicitly; changing its target basis may change the augmented matroid, so
no basis-independent characterization is claimed.

The334 floor is sharp in this representable class: the pulled-back canonical
indicator factorization has unchanged charge334 and trivial duplicate-target
augmented matroids. The proof transfers the lower bound with all tariffs
unchanged; it does not charge a gauge as a native algorithm.

## Scope of other fixed-K exclusions

Any lower bound for a class of canonical factorizations transfers to the
inverse image of that EXACT class under (u,v)->(Su,S^-T v). Thus a four-query,
three-target non-Fano exclusion for canonical columns transfers to those
gauge-adapted target triples of every rank 57 fit, with arbitrary pulled-back
readers. It does not cover all factorizations of those fits unless the
canonical theorem itself covers all factorizations. Similarly a fixed
six-mode subspace exclusion transfers only to the corresponding two
gauge-transformed source/reader subspaces.

All higher-rank fits remain outside this gauge theorem: a nonzero Schur
complement prevents this normal form. No universal P112 decoder obstruction,
cost<=296 construction, native supplier or improved kappa follows.

## Credit and verification boundary

The exact cover, rank 57 normal form, complete-group tariff and cost 334 are
flyingviper's PR2757 and its credited predecessors, including Cinna Davis,
Sagar Thakrar, ctoth, Adam Gall, Jeremy Diviney and Philippe Van Velzen.
PR3505's characteristic-two support-transfer method is Nick Petalas' work;
the expanded-identity method is retained predecessor work, not a new argument
claimed here. Tekalign's PR3370 supplies the plane comparison fixture only.

These are written proofs and exact arithmetic corroboration with separate AI-agent checks,
not independent human review or formal proof-kernel verification.


## Every four-term replacement of three canonical terms has the original floor

Fix the canonical residual convention r=0. For any three distinct columns
a,b,c of R0, let T=aa^T+bb^T+cc^T. The original tariff B is the sum of the
complete dimensions attached to their scalar ports; each column contributes
6, except the residual-bearing column 21 contributes7 and each of the three
G37 singletons contributes3.

**Theorem.** For every t<=4 and arbitrary rational 112-vectors ui,qi satisfying
T=sum_i ui qi^T, the actual whole-group tariff is at least B. Equality is
attained by the original three terms. Queries and readers may have arbitrary
ambient coefficients, zeros, repetitions, exterior directions and cancellation.

Rank(T)=3. Sylvester's inequality gives rank(U)+rank(Q)<=t+3<=7, while each
factor rank is at least3. One side therefore has rank 3; transpose the symmetric
target if necessary. Binary rectangular pairing rank is invariant under
transposition, so this does not change the bill. The query span is now exactly
span(a,b,c), since it contains the target row space and both have dimension 3.

The augmented query/target configuration has at most seven indexed points and
rank 3. Nick Petalas' inherited seven-point theorem, in the declared
`p112-five-term-reader-floor/PROOF.md`, proves that either its full subset-rank
pattern is representable in characteristic two, or its seven distinct rays
form the non-Fano configuration. Both complete classification implementations
and all their runtime data are explicit live replay inputs. The first exhausts
extensions through 7 points; the second independently exhausts8,390 labeled
line systems. There are23 simple rank 3 types:22 have the displayed GF16
representations and one is non-Fano. Zero/parallel elements are restored after
simplification. Configurations with fewer than7 simple points extend generically
and then restrict, as proved in the inherited source. This classification and
its proof are prior work, not a new result of this package.

The representable branch follows the support-transfer proof above, applied to
the selected three target columns. The expanded target is diagonal with rankB,
so every transferred factorization costs at leastB. Both supports only shrink.

For non-Fano use the seven projective points

    E,F,G,E+F,E+G,F+G,E+F+G.

Their six dependent lines are 013,024,056,125,146,236. All rational realizations
are projectively equivalent: send three quadrangle vertices to the axes, the
fourth to(1,1,1), then take the prescribed opposite-side intersections. Its24
automorphisms have four independent marked-triple orbits represented by
(0,1,2),(0,1,4),(0,3,4),(3,4,5), of sizes4,12,12,1. The new package's separate
MMM checker reconstructs every orbit from all 5,040 point permutations and
verifies their 29-element union.

For the middle two orbits, PR3538 gives normalized query columns and binary
replacements:

    marks014: (-1,0,1),(1,1,0),(-1,1,1),(0,1,1)
       maps to (1,0,1),(1,1,0),(1,1,1),(0,1,1);
    marks034: (-1,1,0),(-1,0,1),(-2,1,1),(-1,1,1)
       maps to (1,1,0),(1,0,1),(0,1,1),(1,1,1).

These maps shrink query coordinate supports and preserve every target-axis
span request from each of the 16 query subsets. The separate checker uses
exact rational elimination and binary elimination to check all 96 requests,
finding 14 and 15 true premises. Thus each actual reader port can express its
target axis using only its previous active queries. Outside the targets take
all new reader values zero. The exact target and both support inclusions follow,
so the expanded-rank floor applies independently of the physical geometry.

Projective equivalence can scale targets and queries independently. Multiply
all ports of targetj by its nonzero target scale to form diagonalD; leave other
ports fixed. D commutes withT. Rescale queries and inverse-rescale readers,
using q'i=Dqi/ti and u'i=ti D^-1 ui. This preserves the target and all supports.
Therefore the normalized representatives cover arbitrary rational coefficients.

Only the two remaining marked orbits require the new triad geometry.

### VVV: arbitrary affine readers

For queries a+b,a+c,b+c,a+b+c, every solution is

    u12=(a+b-c-w)/2, u13=(a-b+c-w)/2,
    u23=(-a+b+c-w)/2, u123=w,

with arbitrary ambient rational w. This follows by solving the three target
coefficient equations, and substitution proves exactness. At an A port the
reader-support masks, in term order12,13,23,123, are

    w=0:1110, w=1:0011, w=-1:1101.

For B they are 1110,0101,1011; for C they are 1110,1001,0111. Other w values
make all four entries nonzero, so w=0 shrinks support. Outside the targets,
w=0 deletes every reader entry. Every such specialization remains exact.
Thus all ambient rational readers reduce to the three choices per target port.
This algebraic reduction is credited to PR3527 and its retained predecessor.

### MMM: arbitrary affine readers

After absorbing a factor 2, the queries are a+b-c,a-b+c,-a+b+c,a+b+c. Every
solution has

    u1=(a+b)/2-w, u2=(a+c)/2-w, u3=(b+c)/2-w, u4=w.

At an A port the two critical values w=0 and 1/2 give masks1100 and 0011;
at B they give 1010 and 0101; at C they give 0110 and 1001. Other values make
all four entries nonzero, so choosing zero shrinks support. Outside the targets
zero deletes all readers. All four queries touch the union of the three target
group closures. This exhaustive affine reduction is credited to PR3538.

### Complete finite triad computation

Each canonical column contains exactly one port from each of its touched
physical groups. Permuting selected ports within a group preserves every
source/reader closure, even when multiple selected columns touch that group.
Therefore the tariff problem depends only on the multiset of its three
group-support signatures. Iterating all 57 choose3 triples gives 1,519 classes
whose multiplicities sum to 29,260; no presumed geometry symmetry is used.

The primary checker unions reader-presence patterns inside each physical group,
retaining every assignment's multiplicity. It combines these group states and
computes rectangular ranks from raw Gram columns. The independent checkers
enumerate literal port choices directly, with their own full-group row-rank
calculation. They compare EVERY signature's original bill, multiplicity and
two minima to RESULT.json, not only the aggregate histograms.

The exact minimum-excess histograms over literal triples are

    VVV {0:31,1:96,2:231,3:2484,4:141,5:141,6:306,7:4302,8:2646,9:18882},
    MMM {0:18,1:1,2:54,3:18,4:138,5:144,6:2535,7:342,8:5607,9:20403}.

The census covers 1,260,711 VVV assignments and 101,736 MMM assignments per
signature representatives. Group-state coalescence reduces the primary's
states to 1,036,693 and 100,992 without discarding assignments. All minima are
at least the original bill. Literal doubled-operator witnesses recheck all
112 squared entries and actual tariffs, including residual-bearing equalities.

This settles both non-Fano orbits. Combined with the inherited classification,
representable case and two selective maps, it proves the four-term theorem.
The untouched original three-term factorization supplies sharpness for every
triple, regardless of whether the restricted VVV or MMM family attains it.

## Every five-term replacement of three canonical terms has the original floor

**Theorem.** For any three distinct canonical columns a,b,c, let
T=aa^T+bb^T+cc^T and let B be their original whole-group invoice. Every
rational factorization T=sum_i u_i v_i^T with at most five terms has invoice
at least B. Equality is attained by the original three terms. Arbitrary
ambient factors, denominators, exterior directions, zeros and cancellation
are allowed.

The four-term theorem above is a necessary foundation for the merge branch.
The new five-term proof has two further finite obligations, set out in
[MATROID-PROOF.md](MATROID-PROOF.md) and [COST-PROOF.md](COST-PROOF.md).
Their complete registered replays, rather than catalogue counts alone, are
part of this theorem's evidence.

First pad to five terms. Sylvester's inequality bounds the sum of factor
ranks by eight, so one side has rank three or four. Transpose if necessary.
Its five query columns and the three independent targets form an eight-point
matroid of rank three or four, with full-rank query complement. Complete
modular-cut enumeration, including loops and parallels, gives all 325 and
940 abstract types respectively. Enumerating every admissible target marking
and quotienting query permutations, target permutations and transpose gives
9,377 paired support-request classes.

For each mark j, a source active set S is feasible exactly when target j is
not in the span of the other two targets and the inactive queries. A reader
active set R is feasible exactly when target j lies in the span of R. Both
conditions depend only on subset ranks. Choosing their linear functionals
and query expansions independently at every physical port preserves the
exact product T. Minimal feasible sets therefore cover every rational
factorization without imposing any coefficient alphabet. For an actually
represented matroid, the support optimization is exact; including additional
abstract matroids is a conservative relaxation.

Of the support classes, 8,329 transfer to explicitly verified characteristic-
two representations and 347 have only Ingleton-violating provenance. Every
actual nonexcluded marking of 22 more classes has a proportional source or
reader pair, so merging reduces to the four-term theorem. The universal
marking check matters: one reducible representative of an unrelated abstract
matroid would not suffice. Literal finite-field support-containment witnesses
close another 544 classes. All 135 remaining classes are priced.

All 29,260 target triples and all six target orders are represented by 1,519
unordered physical signatures and 9,114 ordered signatures. Their 45 distinct
target/group-incidence types have entrywise lower-envelope tariff tables.
Pricing all 135 classes against all 45 envelopes closes 6,015 of 6,075 cells.
A low envelope value is only an optimistic exception; no one physical
geometry need attain the entrywise minima simultaneously.

For the 60 exceptions, enumerate every corresponding actual geometry and
identify equal complete tariff tables. There are 7,542 distinct tables,
covering 8,466 ordered signature geometries and 27,304 class/table jobs.
Every exact minimum is its original invoice. The separate annihilator-based
physical-rank calculation and support optimizer agree on all envelope entries
and every final job. Thus the optimistic exceptions supply no saving either.
This proves the stated five-term theorem. Its sharpness comes from retaining
the original three terms, not from claiming every restricted abstract class
has a rational realization.

## Transfer to every rank 57 fit and final limits

Apply the exact gauge to any rank 57 fit and use its gauge-adapted target lists
alpha_j,beta_j. Replacing any three terms alpha_j beta_j^T by at most five
arbitrary rational rank-one terms transforms to the just-proved canonical
triple problem without changing any tariff. Its bill is at least the original
three-term bill. Disjoint such replacements, retaining all other canonical
terms, therefore cost at least 334. This does NOT bound an arbitrary global
factorization, an arbitrary target basis, or a fitting matrix of higher rank.

The scientific code and proof discharge only these finite and linear-algebra
obligations. Six-term triples have nine augmented elements and are not
classified here. Larger or overlapping replacements remain open. No
acquisition, native coefficient execution, frames, restoration, hosting,
storage, precision, all-size supplier or outer-theorem obligation is silently
assigned zero cost. The target 296 and the selected bound remain unreached.
