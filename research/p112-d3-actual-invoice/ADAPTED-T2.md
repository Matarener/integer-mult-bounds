# All adapted t=2, d=3 actual invoices

Prepared by conorholds with substantial OpenAI Codex assistance. Apache-2.0.
This completes the adapted branch, using the
same exact actual-basis contract and inherited inputs.

## Result

All adapted t=2,d=3 actual profiles are excluded under raw sum at most 72
and putative invoice I<=64. There are fifteen candidate actual inside
profiles. Nine containing a high member transfer to actual-profile lemmas;
the six all-low profiles close below. The final three closures use the
full-root-minus-excluded-label bound and [DOUBLE-SEVEN.md](DOUBLE-SEVEN.md).
All inherited geometry and the actual-basis contract are declared in
DEPENDENCIES.md. No minimum actual basis or distinct arbitrary inside
correction indices are assumed.

## Exact ledger and complete actual-profile list

Assume a bad invoice I<=64, adapted r=0, d=3, t=2 and raw sum<=72. RAW-SHAPE
gives dim T=5 and cost(T)>=29. There are five actual inside members forming
a basis of T, and five actual outside members of weight eight/nine. Write
Sigma for their inside sum, c9 for the outside-nine count, and
eta=Sigma-cost(T)>=0. Then

    raw = Sigma+40+c9,
    cost(T)+eta+c9 <=32,
    n_c >= Sigma-24+c9.

In particular cost(T)<=32. A minimum T-basis has a seven: otherwise deletion
of one coordinate gives the excluded four-six d>=2 family. Deleting a seven
leaves four low pieces with code intersection at least two and cost<=25.
Through cost 24 their surviving intrinsic profiles are 7771,7772,7773. At
cost 25 the only further candidates are 7774,7765,7666: with one seven the
other three must all be six; with two sevens the remaining sum is11; with
three sevens the last weight is4. The intrinsic7755/7764 exclusions remove
the smaller two-seven alternatives. Thus the exact candidate minimum list is

    77771 (29), 77772 (30), 77773 (31),
    77774,77765,77666 (32).

The first four have a one-dimensional threshold space below seven, generated
by their final member of rank1,2,3,4 respectively. Nonzero vectors on that
line retain its rank. It cannot be omitted from an actual basis of sum<=32,
since five members of weight>=7 would cost 35. The ordered actual weights
dominate the greedy minimum weights. Hence all actual possibilities are:

| Minimum T | Actual sum | Actual inside profiles |
|---|---:|---|
|77771|29|77771|
|77771|30|87771|
|77771|31|97771,88771|
|77771|32|98771,88871|
|77772|30|77772|
|77772|31|87772|
|77772|32|97772,88772|
|77773|31|77773|
|77773|32|87773|
|77774|32|77774|
|77765|32|77765|
|77666|32|77666|

Outside-nine counts satisfy c9<=32-Sigma. The corresponding bad-invoice
correction thresholds are 5+c9,6+c9,7+c9,8 at Sigma=29,30,31,32.

## Nine high-containing profiles already reduce to actual-profile lemmas

Remove one actual high member Q of weight eight/nine from the five-member
inside basis, and call the remaining four-member span L'. For all nine such
profiles, dim(C intersect L')=2: dimension gives at least two; if it were
three, killing the two largest remaining coordinates would leave seven plus
the small member, of capacity at most 40, below distance53. Thus C+L'=S.

The six actual coordinate functionals outside L', including Q, have
independent restrictions to C by actual coordinate evaluation. All six have
weight eight/nine. The correction rule and invoice are unchanged. The
following are therefore literal actual-profile applications, not assertions
that L' equals the global threshold space:

| Adapted actual profile | Remove | Four-member profile | Written exclusion |
|---|---:|---|---|
|87771|8|7771|D2 minimum 7771, actual eta0 proof|
|97771|9|7771|same; the nine is an outside member|
|88771|8|8771|new T2 actual 8771 proof|
|98771|9|8771|same, with an outside nine|
|88871|8|8871|new T2 actual 8871 proof|
|87772|8|7772|D2 minimum 7772, actual eta0 proof|
|97772|9|7772|same; the nine is outside|
|88772|8|8772|new T2 actual 8772 proof|
|87773|8|7773|D2 minimum 7773 actual proof|

The D2 proofs cited here use the displayed actual low profile, the
two-dimensional code intersection, independent outside restrictions and the
actual correction count. A basis of L' in the three D2 rows is itself a
minimum basis: any cheaper four-piece basis would violate the inherited
intrinsic lower/profile bounds, or the known threshold dimensions inherited
from the original T. In fact the relevant kernel and correction arguments
can be read directly from those displayed profiles without a minimum-L'
normalization. Rank-nine members are counted but never given a rank-eight cut.

## Common four-seven lemma for a small piece on at most three sites

Suppose the actual low profile consists of four sevens A1,...,A4 and a small
piece u with at most e<=3 support sites. Let D=C intersect T have dimension
three. Any three of the four seven-coordinate restrictions on D are
independent: their joint kernel would leave one seven plus u, below 53.
Thus all are nonzero, all pair-kernel lines are distinct where required,
and corrected seven indices are distinct active frame axes. Every pair
kernel word uses two sevens plus u, at most 72+e<=75 sites; both seven
coefficients in that word are nonzero.

Let q be the number of corrected sevens and k the number of active frame
axes in D. The following configurations are impossible:

- q=4 and k<=6. Killing two corrected coordinates leaves at most four
  axes, hence a root/frame by four-axis rigidity. It cannot be frame, since
  both remaining corrected seven coefficients are nonzero at distinct
  matched axes. Thus k=6 and every pair-kernel root has the two remaining
  corrected axes plus the same two unmatched axes. Six distinct incidence
  blocks would contain that fixed pair, while a pair belongs to only three
  blocks in S(3,4,8).
- q=3 and k<=6. Kill two corrected coordinates. A frame kernel would be
  matched to the remaining corrected seven; its target cover is at most
  20+32+e<=55<56. Therefore all three such kernels are nonframe roots.
  Four-axis rigidity forces k=6 and their root blocks contain the same
  three unmatched axes plus three different corrected axes, contrary to
  the uniqueness of a block through a triple.
- q=2 and k<=5. The joint kernel of the two corrected coordinates is a
  frame line, since it has at most three axes and at most 75 support sites.
  On the two-plane E_a obtained by killing either corrected coordinate,
  the three pair-kernel lines are distinct roots, so form an A2
  plane containing that frame line. Such a plane has exactly four active
  axes, forming an incidence block. Consequently k=5 and the blocks of
  E_a and E_b are respectively the active D axes minus a and minus b.
  Their intersection has size three, impossible for distinct S(3,4,8)
  blocks.
- q=1 and k<=4. Kill its corrected coordinate. In the resulting two-plane,
  the three pair-kernel words have at most three axes and at most 75 sites,
  so would be three distinct frame lines in a plane.
- q=0 and k<=3. The same last contradiction applies after killing any
  seven coordinate; there is no need for that coordinate to be corrected.

The lemma uses no extension of G4 and does not assume a finite coefficient
classification. The incidence and A2 facts are explicitly retained in D1/D2.

For 77772, u has exactly two sites and is uncorrected. A bad invoice needs
n_c>=6+c9, so k<=2+q-c9. Every q is excluded by the lemma (or by exceeding
the five available outside corrections). This closes 77772.

For 77771, n_c>=5+c9 gives k<=3+q-c9. The lemma excludes every possibility
except

    q=4, c9=0, exactly one corrected outside member, k=7.

If k<=6 the first part would still exclude it. Thus the only surviving
77771 boundary has raw 69, n_c=5 and I=64, and all four inside sevens are
corrected at four distinct active axes.

## Closure of 77666

Here n_c>=8 and c9=0. The two seven-coordinate restrictions on D are
independent: otherwise their common kernel has dimension at least two in
the three six-pieces, and killing one further six coordinate leaves a
nonzero word in two sixes, capacity 40<53. Their joint kernel is therefore
a line h, covered by the three six-pieces. Its support is at most 60<70,
so h is root/frame.

If all five inside members were corrected, at least three outside axes
would be corrected, giving k<=5. The two corrected seven indices are
distinct, so h has at most three axes and is frame. Every six coefficient
in this frame word is nonzero, since two sixes cover at most 40 sites.
All three corrected sixes would be matched to h, whose target capacity
would be at most 3*12=36<56. Therefore at most four inside members are
corrected and k<=4.

If h were now a nonframe root, it would occupy all four active D axes.
Neither seven could be corrected: each has a nonzero restriction on D
but vanishes on h, while a frame coordinate active on D cannot vanish on
this full-support root. At most three inside corrections would remain,
forcing five outside corrections and k<=3, a contradiction. Thus h is
frame. All three six coefficients are nonzero; any corrected six is
matched to h and reduces the target cover to at most 12+20+20=52<56.
None is corrected. The total correction count is then at most 2+5=7<8.
This closes 77666.

## Closure of 77765

Again n_c>=8 and c9=0. The three seven-coordinate restrictions form a
basis of D*: a joint kernel would leave the six and five, at most 32 sites.
The three pair-kernel lines are independent normal directions; each word
is covered by seven+six+five, at most 68<70 sites, hence is root/frame.

If all three sevens were corrected, at least three outside axes are
corrected even when both intermediate members are corrected, giving k<=5.
Each pair-kernel kills two distinct corrected axes and is therefore frame.
These three distinct frame lines span D, the full coordinate three-plane.
In each frame expansion the remaining seven has nonzero coefficient
(six+five has capacity 32) and is matched to that frame. Its target cover
is at most 20+20+12=52<56. Thus not all three sevens are corrected. In
particular at most four inside members are corrected, so k<=4.

If any pair-kernel root were nonframe, it would use all four active D
axes. Its two killed seven coordinates could not be corrected, leaving
at most three inside corrections and forcing k<=3, impossible. Hence
all three pair-kernel lines are frame and span the full three-frame D.

In each frame-kernel expansion both intermediate coefficients are nonzero:
omitting the six leaves7+5 of capacity 48<53; omitting the five leaves
frame-target capacity 32+20=52<56. A corrected frame row vanishes on at
least two of the three frame axes, so neither intermediate member can be
corrected. Reaching n_c>=8 would then require all three sevens corrected,
already excluded. This closes 77765.

## Reduction of 77773 to two residual cases

If its rank-three member is corrected, it has exactly three support sites;
if it has only three sites but is uncorrected, the same support bound holds.
In either event the four-seven lemma applies. When corrected,
n_c>=7+c9 yields k<=2+q-c9; when uncorrected it gives the still stronger
k<=1+q-c9. Thus these cases close. Any survivor must have an uncorrected
rank-three member supported on all four available sites.

The pair-kernel capacity is then exactly 76, where the <=75 rigidity step
breaks. Four corrected sevens nevertheless close: killing any pair leaves
at most three active axes and a word of support<=76. It cannot be frame
because both remaining corrected seven coefficients are nonzero. It must
be a two-axis 76-site normal. Equality forces both included sevens to have
36 sites, the small piece four, and those supports to be pairwise disjoint.
Doing this for every pair forces all four seven supports pairwise disjoint,
giving4*36+4=148 sites in a112-site set.

Consequently q<=3. Counting then narrows any survivor to one of:

    c9=0, q=2, five outside corrections, k=3;
    c9=0, q=3, four outside corrections, k=4.

For the second statement, if q=3 and k<=3 (including c9=1), the three
pair-kernel words obtained by killing two corrected sevens must be frame
words matched to the third. Each cover has bound 20+32+4=56, so equality
forces the same uncorrected seven to contain32 sites from each of two
different frame targets. Their common set has size24, forcing at least 40
support sites, above its capacity 36. Thus k=4 and exactly four outside
corrections are necessary. The q=2 case has k=3 because D has dimension
three. The following arguments now exclude both residuals; they are not existence claims.


## Final closure of 77773

### A. The corrected support bound is analytic

Write `U(A)` for the binary span of the live support labels of a piece A.
The source
`research/p112-six-seven-supplement/PROOF.md`, Section 2,
proves that a rank-seven label space contains at most 36 **full** E8 root
labels. This includes the eight frame labels, before puncturing. Explicitly,
its leading-one section is an affine six-space. The signed quadratic
calculation gives at most 32 root points when its polar rank is four and
at most 36 when its polar rank is six; smaller affine sections obey the
same bound. The source table is expressly headed "Full-root support size
at most," and only afterward observes that the bounds survive puncturing.

If A is corrected at frame index a, then `z_a` belongs to `U(A)`. This is
a full-root label outside the live set and outside `supp(A)`. Therefore

    |supp(A)| + 1 <= |{full root labels in U(A)}| <= 36,

and hence

    A corrected, w(A)=7  ==>  |supp(A)| <= 35.                 (1)

This argument depends only on binary root labels, not on the coefficient
field. It also remains valid if further frame labels lie in `U(A)`; those
only lower the possible live support size.

For later use, a normal with exactly two nonzero frame coordinates has
at least 76 live nonzeros. This is the retained two-axis bound in `D1.md`
and `D2.md`. It also follows directly from the retained frame-neighborhood
data: the two exclusive neighborhoods contribute 32+32 sites, while on
the common 24 sites the two frame pairings have ratio +1 and -1 on 12
sites each. A nontrivial combination can cancel at most one of these two
classes, giving at least `64+12=76`. Thus this lower bound is valid over
every characteristic-zero field, including generic coefficient ratios.

### B. Actual coordinate facts

Let the five actual inside pieces be `A_1,A_2,A_3,A_4,u`, where all four
`A_i` have rank seven and u has rank three and exactly four support sites.
In the residual case u is uncorrected. Let

    D = {h : C_h belongs to T},  dim_K D = 3,

and write `lambda_i(h)` and `lambda_u(h)` for their actual coordinate
functionals in the expansion of `C_h` in this inside basis. Every actual
outside coefficient is zero on D, so these are the actual codeword
expansions, with no change of low basis.

Every three of `lambda_1,...,lambda_4` are independent: a nonzero joint
kernel vector would have its codeword supported on the remaining seven
and u, at most `36+4=40<53` sites. In particular, each pair has a
one-dimensional joint kernel. On that line the two remaining seven
coefficients are both nonzero; otherwise three seven coordinates vanish.

If `A_i` is corrected at a, then `lambda_i` is a nonzero scalar multiple
of the frame coordinate `h_a` on D. Its restriction is nonzero, so a is
active on D. Distinct corrected sevens have distinct indices, since any
two of these four coordinate restrictions are independent. Distinctness
is derived here for this particular family, not postulated globally.

Combining (1) with the uncorrected-seven capacity 36 gives the useful
consequence:

    A pair-kernel word using one corrected seven, one other seven,
    and u has at most 35+36+4=75 nonzero live sites.             (2)

The upper bound allows arbitrary overlaps, zero u coefficient, and
cancellation. It is an upper bound on the union of the actual supports;
no disjointness conclusion is needed.

### C. Two corrected sevens and a full three-frame normal space

The first residual has exactly two corrected sevens, five corrected
outside members, and three active normal axes. Call the corrected pieces
A and B, matched at distinct axes a and b, and the uncorrected sevens
Q and R. Since D has dimension three and has only three active axes,

    D = span_K{f_a,f_b,f_c}

for the remaining active axis c.

Take a nonzero h in `ker(lambda_A) intersect ker(lambda_Q)`. Its actual
expansion uses B, R, and u, and its B coefficient is nonzero by the preceding actual-coordinate facts.
Since A is corrected at a, `h_a=0`; thus h has at most the two active
axes b and c. The expansion has at most 75 support sites by (2). A
two-axis normal would have at least 76 sites, so h is a frame direction.
Its B coefficient is a nonzero multiple of `h_b`, so necessarily

    ker(lambda_A) intersect ker(lambda_Q) = K f_b.              (3)

Apply the same argument to `ker(lambda_A) intersect ker(lambda_R)`.
Its expansion uses B, Q, and u, again including the corrected B with
nonzero coefficient. It follows that

    ker(lambda_A) intersect ker(lambda_R) = K f_b.              (4)

Equations (3)--(4) give a nonzero vector in the common kernel of
`lambda_A,lambda_Q,lambda_R`, contradicting their independence. This
excludes the first residual.

### D. Three corrected sevens and four active normal axes

The second residual has three corrected sevens, four corrected outside
members, and four active normal axes. Call the corrected pieces A, B,
and C, matched at distinct axes a, b, and c. Write d for the fourth
active axis and Q for the remaining uncorrected seven. Then

    D is a three-dimensional subspace of span_K{f_a,f_b,f_c,f_d}.

Take a nonzero h in `ker(lambda_A) intersect ker(lambda_B)`. Its actual
expansion uses C, Q, and u; the C coefficient is nonzero. Its a and b
frame coordinates vanish, so it has at most the two active axes c and d.
By (2) it has at most 75 live nonzeros. The two-axis lower bound forces
h to be a frame direction, and its nonzero C coefficient forces it to
be `f_c`. Thus `f_c` belongs to D.

Killing A and C in the same way gives `f_b` in D, and killing B and C
gives `f_a` in D. The three independent frame lines span the
three-dimensional D, so

    D = span_K{f_a,f_b,f_c}.

Axis d is therefore inactive, contradicting the residual hypothesis of
four active axes. This excludes the second residual.


## Final closure of 77771

### A. A uniform root-neighborhood bound

Write V=L/2L, with nondegenerate alternating polar form B, and put

    beta((tau,x),(sigma,y)) = tau*sigma+B(x,y).

This bilinear form on the nine-dimensional label space is nondegenerate:
its radical has tau=0 by pairing with (1,0), and then x=0 by
nondegeneracy of B. For a root line v define

    W_v = ker beta(ell(v), -)
        = {(tau,x) : tau+B(v,x)=0}.

The full-root labels in the leading-one section of W_v are exactly
the nonself neighbors of v. The self line v is outside W_v. A rank-seven binary
space H inside W_v has at most 32 full root labels: its affine
six-section is contained in B(v,x)=1, and predecessor Section 4,
equation (10), gives root counts 24, 28, or 32. This bound applies to
ALL such H, without assuming a large residual first. A rank-six space
has at most 20 full roots by the global capacity.

Suppose H has rank seven, contains an excluded frame label z_i, and
the axis f_i is a nonself neighbor of v. Thus z_i belongs to W_v.
There are two bounds for live root-word support covered by H:

* If H is not contained in W_v, then H intersect W_v has rank six
  and contains z_i. It covers at most 19 LIVE nonself neighbors.
  Adding the possible live self line v gives at most 20 sites of
  Off(v).
* If H is contained in W_v, its at most 32 full roots include z_i.
  It covers at most 31 LIVE neighbors and cannot cover the self line.

The forced excluded label is essential to these 20/31 bounds.

### B. Apply the bounds to all six pair kernels

The preceding adapted reduction leaves 77771 only when all four actual
sevens A_1,...,A_4 are corrected at four distinct active frame axes,
the unit u has one live support site, and D=C intersect T has dimension
three. Every three seven-coordinate restrictions a_i on D are
independent. Set H_i=U(A_i), of binary dimension seven, containing
its matching excluded label z_i.

For each pair i,j, kill the other two seven coordinates on D. This
gives a nonzero line h_ij and an actual expansion

    C_hij = alpha_i A_i+alpha_j A_j+gamma u,

with both alpha_i and alpha_j nonzero. The two-seven-flat union lemma
bounds the two FULL root sections by 68 sites. Since a corrected flat
contains an excluded frame label, their LIVE union is at most 67;
adding u gives at most 68, strictly below 70. The retained root-rigidity
theorem therefore makes h_ij a scalar root direction. Because the
two distinct matched corrected axes i,j are active in h_ij, it is a
nonframe root. Its live code support has exactly 53 sites, and each
of z_i,z_j is a nonself neighbor label of that root.

Apply the preceding root-neighborhood bounds to H_i,H_j and this root v_ij. If either flat were not
contained in W_vij, the other flat would cover at most 31 live sites
(or at most 20 if it too were not contained). The unit then permits
at most

    20+31+1 = 52 < 53

sites in the actual root-word cover. Hence BOTH H_i and H_j are
contained in W_vij, for every one of the six pairs.

Neither H_i nor H_j contains the live SELF root label of v_ij, since
both lie in W_vij. Evaluating the actual kernel expansion at that site
therefore forces the unit u to be nonzero there: the root word itself
has nonzero self evaluation. Thus the unit's sole support site must
equal v_ij, for every pair i,j.

Fix i and choose two different partners j,k. Their kernel lines are
distinct: equality would kill three seven coordinates, contradicting
their independence. The corresponding root lines v_ij and v_ik are
therefore distinct live sites, both forced into the unit's one-site
support. Contradiction.

Thus the actual 77771 bad-invoice branch is excluded.


## Final closure of 77774

### Contract and elementary reductions

Let the actual inside basis of T be Q1,Q2,Q3,Q4,u, with ranks 7,7,7,7,4.
Put D=C intersect T, of dimension three. The five actual outside members
have weight eight: raw sum is 32+40=72, so c9=0. A bad invoice I<=64 needs
at least eight actual corrections.

Every three seven-coordinate functionals on D are independent: a nonzero
common kernel would leave only the fourth seven and u, on at most 44 sites,
contradicting distance 53. In particular every pair kernel is a line, and
both of the two remaining seven coefficients on that line are nonzero.
Corrected seven indices are consequently distinct, and active on D.

The five outside restricted duals are independent, by restriction of
Ann(T) to C and C+T=S. Thus their corrected frame indices are distinct and
inactive on D. Write q for the number of corrected sevens, epsilon for
whether u is corrected, and k for the number of active frame axes of D.
Then

    q+epsilon >=3,       3<=k<=q+epsilon.

The second inequality uses at least 8-q-epsilon distinct corrected outside
axes. Thus only q=3,4 when epsilon=0, and q=2,3,4 when epsilon=1, need
consideration.

The global rank-seven capacity 36 in the source is a FULL 120-root-line
capacity. A corrected seven's binary flat contains at least its excluded
frame label, so its LIVE support has at most 35 sites. Likewise corrected
u has at most seven live sites. For every frame neighborhood N_i, a
corrected seven has at most 20 target sites and corrected u at most four:
their binary spans contain some frame label z, while EVERY neighborhood
hyperplane W_i excludes EVERY frame label. Their intersections with W_i
therefore have ranks at most six and three respectively. These bounds do
not require that the correction be matched to target i.

### Case q=4, for either correction status of u

Here k<=5. Kill two corrected seven coordinates. Both remaining corrected
coefficients are nonzero at distinct axes, while the normal has at most
three active axes. A nonframe such normal needs at least 76 live sites.
The double-seven lemma gives a shorter direct contradiction:
the two remaining corrected sevens contain two distinct excluded labels,
so their live union has at most 66 sites. Adding u supplies at most
eight, leaving at most 74 sites, below the minimum 76 for the kernel
normal on two or three active axes. This argument does not need the
intermediate reduction k=4 or the pair-union count.

### Case q=3 and u uncorrected

There must be five corrected outside members, so k=3 and D is the full
coordinate three-plane. Write A for the uncorrected seven. For each of
the three active frame axes i, the actual frame expansion uses only its
matched corrected seven, A, and u. Consequently

    |supp(A) intersect N_i| >=56-20-8=28.

Their sum is at least 84. Every site belongs to at most two of these
three neighborhoods unless it is in their common intersection, which
has eight sites by the retained S(3,4,8) frame incidence. Thus the sum
is at most 2|supp(A)|+8<=80, contradiction.

### Case q=2 and u corrected

Five outside members must be corrected, so k=3 and D is the full frame
three-plane. Name the two corrected-seven axes a,b, and the remaining
axis c. Name the uncorrected sevens A,B. Their coefficients in C_fc are
both nonzero, by independence of every triple of seven coordinates.

If u is not corrected at c, its coefficient in C_fc vanishes. The 56-site
frame cover by A+B forces both seven flats into W_c: otherwise their
target capacities total at most 20+32=52. Hence both pieces are supported
inside N_c. Choose i from {a,b} different from u's correction index.
In the expansion of C_fi, the 32 sites N_i minus N_c can then be covered
only by its matched corrected seven, with target capacity at most 20.
Contradiction. This includes a correction index inactive on D.

It remains that u is corrected at c. In C_fc, its target capacity is at
most four. If neither A nor B were inside W_c, total target capacity
would be at most 20+20+4=44. Thus, say A is supported inside N_c.
Outside N_c the C_fc expansion, whose B coefficient is nonzero, gives

    supp(B) minus N_c subset supp(u) minus N_c.

In the expansion of C_fa, u has zero coefficient, A vanishes outside
N_c, and the other corrected seven has zero coefficient. The 32 sites
N_a minus N_c must therefore lie in the matched corrected seven (at
most 20 target sites) and B outside N_c (at most seven sites). This
would give 32<=27, contradiction.

### Case q=3 and u corrected

Write Q_a,Q_b,Q_c for the corrected sevens, at their distinct active
axes, and A for the fourth seven. We have k<=4. For each i in {a,b,c},
kill the other two corrected coordinates; call the resulting kernel
normal h_i. Its i coordinate and its Q_i coefficient are nonzero.

Each h_i has at most two active axes and is covered by Q_i,A,u. The
double-seven corollary bounds this cover by 67+7=74 sites. Therefore
h_i must be the frame axis i: a genuine two-axis normal needs at least
76 sites. The u coefficient cannot vanish, since the frame target cover
by Q_i+A alone has capacity at most 20+32=52<56. Hence u's corrected
axis must be i, for EACH of the three distinct indices a,b,c. This is
impossible, and closes the last case.


## Conclusion

Every one of the fifteen necessary actual profiles is excluded. Hence the
adapted t=2,d=3 budgeted invoice is at least 65. Together with PROOF.md's
nonadapted branch this proves the complete t=2,d=3 budgeted theorem, which
is used before the correction-pair merge in the t=3 argument. Geometry
remains a written proof supported by the declared finite replay.
