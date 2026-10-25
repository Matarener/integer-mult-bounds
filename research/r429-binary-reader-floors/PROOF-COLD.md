# Arbitrary binary ten- and eleven-term cold-factor floors for R429

This proof concerns the fixed binary matrix `M = K R` from scientific pin
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. Both physical index sets are the
same ordered 111 unoriented E8 root lines in `READOUT-FLOOR.json`. The roots
have squared norm four. All matrix products and scalar-factor identities
below are over F2; every geometric rank and pairing tariff is over Q.

For a binary vector `c`, let `U(c)` be the rational span of the roots at its
nonzero coordinates, and write `d(c) = dim U(c)`. An exact scalar factorization

    M = sum_i b_i c_i^T

is charged

    T = sum_i tau(c_i,b_i),
    tau(c,b) = rank_Q(< , > restricted to U(c) x U(b)).

The theorem is `T >= 56` for every ten- or eleven-term factorization with
arbitrary binary `b_i,c_i`, including factors outside the retained code.
Zero terms are allowed and can be deleted. The independently rechecked
nine-term lower bound is 63. None of these bounds asserts an attaining
56-cost factorization.

This is a necessary tariff in a model charging separate scalar factors.
It does not construct or lower-bound arbitrary shared native circuits,
nonlinear or operator-valued readers, dirty-helper restoration, rounding,
owner schedules, source access or tape movement. There is no new kappa.

## Exact fixture and prior results

The source reconstruction gives rank `R = rank K = rank M = 9`,
`M = M^T`, and

    M[p,q] = (1 + <root_p,root_q>/2) mod 2.

Let `D = rowspace(M) = colspace(M)`, identifying rows and columns by the
common physical root order. Then `D = rowspace(R)` has 512 words, minimum
nonzero weight 48, exactly nine nonzero words with geometric rank seven,
and 502 with geometric rank eight. The nine rank-seven words are the
physical original readers `R_0,...,R_8`; their normals are the nine deleted
root lines, and these nine words are a binary basis.

The R429 live root list is exactly the PR555 fixture
`research/e8-bit-p111/data/bitE8mut-p111.json.gz`, including its order.
Its deleted indices in the full ordered 120-line list are
`[10,15,51,53,56,66,72,89,111]`. The affine matrix above is therefore the
PR555 matrix covered by Russell Seligmann's PR757. That prior establishes
the stronger value 63 for every term count with both individual factors
restricted to its fixed label code. The present ten/eleven-term floor 56
allows factors outside that code. The nine-term 63 result here is a
source-bound recheck of an existing result, not a new numerical bound.

Cody Harris's PR761 covers the different PR545 fixture, with deleted indices
`[39,52,57,71,76,78,103,109,114]`. Its live root set differs, so it is a method
antecedent rather than the exact fixture-binding premise. Joel Pulikkan /
GamingPuzzled's PR620 and the earlier E8 star/flat-capacity work are also
antecedents. The full-120, non-characteristic-two scalar-code results in
PR3755 have a different field and tariff and are not used as premises here.

## Elementary tariff facts

For subspaces `U,V <= Q^8`, the pairing rank is the dimension of the image
of `U` in `V*`, and consequently

    tau(U,V) >= dim U + dim V - 8.

If `V = Q^8`, this is exactly `dim U`. If `V = n^perp` is a hyperplane,
the tariff is `dim U - dim(U intersect <n>)`, allowing a discount at most
one. For two hyperplanes the tariff is six if their normals are orthogonal,
and seven otherwise. These are rational statements; no binary support
rank is substituted for a rational pairing rank.

When two target factors coincide, replace `b c_1^T + b c_2^T` by
`b (c_1+c_2)^T`. The new support is contained in the union of the old
supports, so `U(c_1+c_2) <= U(c_1)+U(c_2)`. Taking images in `U(b)*` shows

    tau(c_1+c_2,b) <= tau(c_1,b)+tau(c_2,b).

The transposed statement merges repeated source factors. Thus deleting zero
terms or merging duplicates never increases the tariff. Any resulting
nonzero factorization has at least nine terms, since `rank_F2 M = 9`.

## Complete low-span coset reduction

Every root-spanned real subspace intersects E8 in a parabolic subsystem.
One elementary justification is to choose a vector in its orthogonal
complement avoiding the finitely many extra root hyperplanes. Its vanishing
roots are exactly the roots in the given subspace. Move this vector into
a closed Weyl chamber. In a simple-root expansion, the nonnegative
coefficients of a positive root show that it vanishes exactly when its
simple-root support lies among the simple roots on the chamber walls.
This reduces the capacity question to the 256 subsets of an E8 simple basis.

For completeness, moving into the closed chamber only uses finiteness of
the Weyl action: maximize the inner product with a strictly dominant vector
over the finite orbit. A negative simple-root pairing would be increased
by reflection, contradicting maximality. The finite root input is closed
under reflections, spans dimension eight, and has an E8 simple diagram.

The independent exact check constructs a simple basis from all 240 signed
roots, verifies integral one-sign coefficients and the E8 diagram, and
checks all 256 subsets. The maximum number of root lines in dimensions
zero through eight is

    0, 1, 3, 6, 12, 20, 36, 63, 120.

Among flats of rank at most six, the only possibilities with more than
21 lines are rank-six E6 and D6, with 36 and 30 lines. For every relevant
simple subset the check finds its complementary root plane: A2 for E6
(three normal lines), and A1+A1 for D6 (two orthogonal normal lines).
Double orthogonal complementation recovers exactly the given subsystem.
Weyl transport therefore covers every embedding, rather than relying on
determinants alone. The maximum size of a rank-seven subsystem other than
E7 is 42; an E7 flat has a root normal and is one of the 120 root caps.

The primary `cold_cosets.py` certificate enumerates every A2 or A1+A1
normal plane in the actual full root set. Its distinct punctured flats
number 1120 and 3780. For each of these 4900 flats `S` and each of the 511
nonzero words `d in D`, it certifies

    rank_Q{root_p : p in supp(d) minus S} >= 7.

The implementation finds rank at least seven modulo 65537. A nonzero
minor modulo that prime is a nonzero integer minor, so it proves a rational
lower bound without assuming equality of modular and rational ranks.
The explicit two independent normals supply rank at most six for each
enumerated flat; its modular rank-six check supplies the lower bound.
The independent review rechecked the exhaustive-domain reduction and flat
counts, while the parent replay owns the 2,503,900 outside-rank checks.

It follows that each coset `z+D` contains at most one nonzero vector of
geometric rank at most six. Indeed, if two such distinct vectors `u,v`
occurred, `u+v` would be a nonzero D word. If neither supporting flat were
E6 or D6, their union would have at most 42 coordinates, contrary to
distance 48. Otherwise use the large flat as `S`; all of `supp(u+v)`
outside `S` lies in the other rank-at-most-six span, contradicting the
rank-seven certificate. No assumption on the type of the second flat
is required. In the zero coset there are no such nonzero vectors at all.

## Nine terms

For nine terms both factor lists are bases of D and are dual for the
nondegenerate coefficient form of M. Give each of the nine special
hyperplane directions its deleted-normal label. The exact coefficient
form has binary self-pairing one on each special label. Therefore a label
selected on both sides must occur in the same term: otherwise the dual
basis pairing would have to be zero there.

The finite coefficient and rational pairing checks also show that two
distinct special labels occurring together in a dual term have orthogonal
normals. Write `a,b` for the numbers of special directions on the two sides,
and `c` for the number of same-label paired terms. The complete tariff is

    72 - a - b + c.

Since the common selected labels are exactly those `c` paired labels,
`a+b-c` is the cardinality of a union of subsets of nine labels. Thus the
tariff is at least 63. The original special-target factorization attains
63. The review independently checked all 511 rational support ranks,
all 81 rational hyperplane pairings and the exact binary coefficient form.

## Ten terms

First delete zero terms; a nine-term outcome is already covered. For ten
nonzero terms write the target and source factor ranks as `s,t`. Both
are at least nine and Sylvester gives `s+t <= 19`, so the only possibilities
are `(9,9),(9,10),(10,9)`. In the first case all twenty vectors lie in D,
so every term costs at least six, giving 60.

By the exact symmetry of M, orient the other cases with ten independent
source vectors and rank-nine targets. The source span contains D with
one-dimensional quotient; coset uniqueness permits at most one low
source vector, where low means geometric rank at most six. Every other
source dimension is at least seven, so their dimension sum is at least 64.

If target vectors repeat, merge them and use the nine-term bound. Otherwise
at most nine distinct target vectors are special hyperplanes. Each allows
a discount at most one; all remaining targets span Q^8. This gives 55.
Equality 55 requires one source dimension one, the other nine dimensions
seven, and all nine special targets plus one generic full-span target.

A dimension-one binary reader is a single live coordinate, since the
root lines are distinct. If paired to a special target it has no discount:
its live root line differs from that target's deleted-root normal. At most
eight discounts remain, giving at least 56.

If the unit `e_a` is paired to the generic target, use the nine special
targets `B_i` as a basis and write their exact dual sources as `C_i`.
The generic target is `sum lambda_i B_i` with `wt(lambda) >= 2`, and exact
factor equality uniquely forces the other source vectors to be
`C_i + lambda_i e_a`. For all 111 units, exact rational projection ranks
and all 502 possible generic targets give minimum bill 63 for one unit
and 64 for the other 110. This excludes equality 55. Since the tariff is
integral, every ten-term factorization has tariff at least 56.

## The two-unit extension lemma

Fix units `e_a,e_b` and restrict the two factor spaces to
`D + <e_a>` and `D + <e_b>`. The complete unit-toggle census checks all
`111*511 = 56,721` vectors `d+e_a`, with `d in D` nonzero. Every support
has rank seven or eight. Each rank-eight claim has a full modular-rank
certificate; each rank-seven claim has a modular lower certificate plus
an explicit rational null normal. The independent review repeats this
census over F3, instead of the producer's F65537, and checks the normals.

Besides the nine old special code labels, the only possible code label
that acquires rank seven in this extension is `f_a = M[a,:]`. Its toggle
`f_a+e_a` is the cap perpendicular to the live root at `a`. Old special
labels may also be toggled exactly when the unit lies in their hyperplane.
The only nonzero low vector of the extension is `e_a` itself.

Project both extensions onto D along their unit directions. Rank M forces
at least nine terms with nonzero projected code part on both sides. Call
these high/high terms. Each costs at least six. If the whole tariff were
at most 55 there would be exactly nine such terms. At least one of their
two sides would have all geometric dimensions seven: a dimension-eight
factor on each side costs at least two above the baseline 54, whether
they occur in one term or two. Transpose if needed to choose the source side.

The nine source code parts form a basis selected from the ten possible
hyperplane labels. Across all 111 source units, deleting one of these ten
labels gives exactly 638 independent nine-label bases. For each basis,
the exact dual target code basis consists of nine distinct generic D
directions. In a target unit extension at most one such direction can
become a hyperplane, namely its `f_a`. Hence at least eight target spans
are full and the core tariff is at least `8*7+6 = 62`, a contradiction.
The independent check reconstructs all 638 dual bases, verifies every
full binary matrix identity and compares every recorded dual code mask.
No tail equation or choice of unit flags can bypass this necessary condition.

## Eleven terms

Delete zero terms and merge duplicates on either side. A reduction to nine
or ten terms already proves the claim. Otherwise both lists have eleven
distinct nonzero vectors. Sylvester leaves precisely

    (9,9), (9,10), (9,11), (10,9), (10,10), (11,9).

If one factor rank is nine, orient it as targets; its vectors lie in D,
and at most nine distinct hyperplane targets give one-unit discounts.
For source rank nine every term costs at least six, giving 66. For source
rank ten, coset uniqueness allows at most one low source, giving total
source dimension at least `1+10*7 = 71` and tariff at least 62.

For source rank eleven, the eleven source vectors are independent and
their span contains D with a two-dimensional quotient. There are at most
three low vectors, one per nonzero quotient class. With at most two low
vectors, source dimension is at least `2+9*7 = 65`, giving tariff at least
56. With three, their distinct nonzero quotient classes sum to zero.
Their actual sum is a nonzero D word, because a nonempty subset of the
eleven independent vectors cannot sum to zero. The union of the three low
supports has at least 48 coordinates. The rank-capacity table therefore
forces their dimension sum to be at least 11 (the capacity-level minimum
is attained by `(1,4,6)`). The other eight dimensions are at least seven,
giving tariff at least `11+8*7-9 = 58`.

It remains to consider factor ranks `(10,10)`. Each side has at most one
distinct low vector by coset uniqueness. If either side has no low vector,
at least ten terms are high/high and already cost 60. If the two low vectors
occur together in one term, again ten terms are high/high. Thus a putative
tariff at most 55 requires one low vector on each side at different indices:
nine high/high terms, one low-source/high-target tail and one
high-source/low-target tail.

Choose the code projection of each factor space `D + <z>` onto D along
its actual low direction `z`. Every high vector has nonzero code part,
and each low vector has zero code part. The nine projected high/high
terms alone therefore factor M and give two dual code bases. If the low
geometric dimensions are `a,b`, the two tail costs are at least `a-1,b-1`.
The nine-term core costs at least 54, so `a+b <= 3`. The unit/unit case
is excluded above; up to transposition only unit/rank-two remains.

A rank-two root support has at most three coordinates. If `z` has rank
two and `d in D` is nonzero, the support of `d+z` has weight at least 45.
If its rank is seven, it cannot fit a non-E7 rank-seven flat of capacity
42, so it lies in one of the 120 E7 caps. The complete `120*511 = 61,320`
near-cap check shows: for each deleted-root cap the unique D word with at
most three coordinates outside is its old special word, with none outside;
for each live-root cap it is `f_p`, with the sole outside coordinate `p`.
Every other outside support has size at least 18. Thus a rank-two extension
can create at most three generic hyperplane code labels, one for each
coordinate in `supp(z)`.

The two tails now cost at least one in total. A putative tariff at most
55 forces the nine core terms all to cost six, and hence both geometric
spans in every core term must be hyperplanes. Orient the unit extension
as sources. Its nine projected code parts are one of the 638 bases above,
whose nine dual target labels are all generic. The rank-two extension can
turn at most three of them into hyperplanes. This contradiction exhausts
the last rank case and proves the eleven-term floor 56.

## Evidence boundary

The argument quantifies over all binary factor choices of the stated term
counts through algebraic rank cases and a written root-flat reduction.
Its geometry and basis premises have complete finite certificates. The
primary replay must also pass the source reconstruction and the 2,503,900
coset-rank checks; the independent review deliberately does not duplicate
that heavy census. This is not a formal-kernel proof or an unrestricted
claim for twelve or more terms, a changed matrix, a different scalar field,
or a shared-cost circuit model.
