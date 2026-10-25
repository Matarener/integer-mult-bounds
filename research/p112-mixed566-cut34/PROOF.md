# Mixed 5,6,6 shortening through one common cut of 34

Let R be the fixed 112 nonframe E8 root lines with the canonical leading-one
nine-bit labels ell(r). Over any characteristic-zero field K, set

    C = {(r dot h)_(r in R) : h in K^8}.

The binary support rank of a vector is the F2 rank of the labels at its
nonzero coordinates. For ONE arbitrary common set S of coordinates, pi_S
deletes those coordinates.

Conditional theorem. If |S| <= 34 and q_1,q_2,q_3 are arbitrary vectors on
R minus S with binary support ranks at most 5,6,6, respectively, then

    dim_K(pi_S(C) intersect span_K(q_1,q_2,q_3)) <= 1.

Coefficients, overlaps and dependence among the pieces are unrestricted.
Only the residual supports are constrained. This improves PR3325's sufficient
common-cut threshold 33 by one. Sharpness and actual caller applicability are
not established.

## Inherited premises and credit

SOURCES.json pins the following canonical-main proofs at baseline
6f100d4bb5083f8c35d96fd95a539811c62f245c. They are live authenticated inputs.
Authentication preserves exact hypotheses and attribution; it does not prove
their mathematics or supplier admission.

* PR3299, retained as p112-mixed566-cut32/PROOF.md, supplies the
  characteristic-zero normal-plane reduction, the singleton-incidence
  argument, global P112 rank-five/six capacities 12/20, and E6 joint bounds
  M+J <= 22/32 with live union at least 78. Its inherited geometry, capacity,
  transport and standard real Weyl-chamber premises remain conditional.
* PR3325, retained as p112-mixed566-cut33/PROOF.md, supplies full D6-axis
  rank-five plus rank-six union bound 28. It also records rank-five
  concentration at 10, small-fiber rank-five capacity 8, small-fiber size 12,
  and PR3292's rank-six live capacity 18 after FOUR orthogonal punctures.
  These remain inherited premises. Its original local union census is not
  rerun or claimed as new here.
* PR3324, retained as d6-axis-concentration14/PROOF.md, supplies full-axis
  rank-six concentration at 14, for arbitrary ambient support spaces. The
  previous threshold 18 does not suffice at the new boundary. This uses the
  full-root closure statement, not an assumption about only P112 sites.

The source proofs retain PR3295/3292/3278/3267/3260/3262/3269, David Arias's
quadratic model, DreamingOfClouds/PR3154, joaqcoo and E8/P112/root-simplex
credit. PR3325 owns the earlier cut 33 theorem and pair-union lemma. PR3324
owns concentration 14 and its sharpness. No predecessor result is re-claimed.

## Normalize a hypothetical two-dimensional intersection

Take two independent restricted codewords in the piece span and lift them
to c_h,c_k in C. Let U be their full live evaluation union and T=U minus S,
with N=|T|. Extend each piece by zero on S. Let M_i be its entire residual
support size, including sites outside U. The capacity bounds give

    |U| <= |S| + M_1+M_2+M_3 <= 34+12+20+20 = 86.

At least 26 live roots annihilate both lifts. Their rational span Z has rank
at most six, since rational matrix rank is unchanged over a characteristic-zero
extension. Every full root in Z also annihilates both. A generic real vector
perpendicular to Z avoids all additional root hyperplanes. The inherited
Weyl-chamber reduction makes the roots in Z a parabolic subsystem.

Rank-at-most-five parabolics have at most 20 root lines. Among rank-six
parabolics, those other than D6 and E6 have at most 21. Thus Z has rank six
and the common normal plane has type D6 or E6. This also proves that it has
a rational basis over K. The new finite replay checks the 26-zero threshold
against all 56 rank-five and 28 rank-six standard parabolics. The standard
Weyl-chamber theorem and source normalization implications remain inherited.

A fixed two-by-three coefficient matrix expresses the restricted codewords
in the q_i. A site in T where only q_i is nonzero has nonzero evaluation
pair proportional to column i, so all such singleton sites lie in ONE
projective fiber. A zero column has no singleton sites. This remains valid
with cancellations and coefficients outside Q.

## E6 is still strictly excluded

Write J_i for the number of singleton sites of piece i in T. Counting each
nonsingleton site at least twice gives, with the inherited E6 incidence bounds,

    88 = 2*(78-34) <= 2*N <= sum_i(M_i+J_i) <= 22+32+32 = 86.

This contradiction uses whole piece supports, including sites outside U.

## D6 singleton bounds

For D6, the full fixed-frame union sizes are 82,84,85,86,88. The budget 86
retains exactly 82,84,85,86. The 86 case is new at this cut and is included.
The literal replay reconstructs all 3780 unordered orthogonal root pairs.
Their union histogram is 448,2688,448,168,28 in that order. At union 82 each
large axis has 29 live roots, obtained from 33 by four pairwise orthogonal
frame punctures. All 896 ordered axes of that union type are checked.

Let c=(12,20,20). Every site of T is covered by some piece. Those sites not
covered by the other two pieces are singleton sites of piece i. Consequently

    J_i >= N - sum_(j != i) M_j >= c_i - (52-N).

This elementary covering bound permits support outside T, overlaps, arbitrary
coefficients and cancellations. It is also the singleton consequence of
PR3299's exact nonnegative-deficit identity.

## D6 union 82, the new equality refinement

Here N>=82-34=48, so J_2,J_3>=16. A small fiber has at most 12 roots, so
both rank-six singleton fibers are large axes. PR3324's threshold 14
concentrates each whole piece support into its large axis. Four-puncture
capacity 18 now gives

    48 <= N <= M_1+M_2+M_3 <= 12+18+18 = 48.

All these inequalities are equalities. In particular, the refined covering
bound gives J_1 >= N-M_2-M_3 >= 12. Equivalently, equality leaves no overlap
or piece incidences outside T. A small fiber has rank-five capacity 8, so the
rank-five singleton fiber is large. Its 12 singleton sites exceed the inherited
concentration threshold 10. Thus all three entire supports lie on two axes.

One axis receives at most one piece, contributing at most 18; the other has
only 29 live sites. Hence N<=47<48, already a contradiction. The replay also
uses the inherited pair-union 28 lemma to record the stronger bound 46: if a
rank-six piece is alone the other rank-five/rank-six pair covers at most 28;
if the rank-five piece is alone the bound is 12+29=41; if all pieces share
one axis it is 29. The stronger 46 is unnecessary for this branch's strictness.

This is the new implication. Applying only the original capacities leaves
J_1>=8 and does not justify rank-five concentration.

## D6 unions 84,85,86

The required retained sizes are at least 50,51,52. The singleton bounds are
respectively at least (10,18,18), (11,19,19), (12,20,20). Rank five exceeds
small-fiber capacity 8 and reaches concentration 10. Rank six exceeds
small-fiber size 12 and reaches concentration 14. Thus each entire support
lies on one of the two large axes.

If all pieces occupy one axis, they cover at most 33. If the rank-five piece
is alone, the two-axis coverage is at most 12+33=45. Otherwise a rank-six
piece is alone, and the rank-five/rank-six pair on the other axis covers
at most 28, giving 20+28=48. Therefore

    |U|=84: N <= 48 < 50 <= N,
    |U|=85: N <= 48 < 51 <= N,
    |U|=86: N <= 48 < 52 <= N.

The eight axis assignments are checked separately for each case. Together
with E6 and union 82, these contradictions prove the conditional theorem.

## Evidence, limits and Open next questions

The new checks cover the exact branch arithmetic, literal plane/puncture
inventory, 26-zero normalization counts and source binding. A separate checker
constructs the root inventory without predecessor imports and checks all 4693
support-size triples after the rank-six refinement. Only (12,18,18) can cover 48.
Neither implementation re-proves the inherited global capacities, concentration,
pair-union 28, four-puncture 18, E6 incidence or Weyl-chamber premises.

At cut 35 the E6 inequalities meet at 86, and the particular union 82 equality
argument no longer follows from N>=47. These are limits of this proof and
its controls, not a counterexample or sharpness claim. A different refinement
may close them. The next useful question is cut 35 with its complete union
inventory and literal coefficient realization, or a current caller whose
actual one-common-cut contract needs 34. No additional construction round is
reserved by this package.

No new caller exclusion, full C5, global decoder floor, physical/native
program, dirty restoration, consumer invoice, supplier admission, all-size
multiplication theorem, selected-frontier or kappa change is established.
Historical heavy suites, selected cold replay, Lean, Docker and human or
proof-kernel review are unrun. This is a conditional geometric side result
under the revision 6 decoder card, not a supplier meeting its 5% gate.
