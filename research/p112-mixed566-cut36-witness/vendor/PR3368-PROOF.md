# Mixed 5,6,6 shortening through one common cut of 35

Let R be the fixed 112 nonframe E8 root lines with the canonical leading-one
nine-bit labels. Over any characteristic-zero field K, let

    C = {(r dot h)_(r in R) : h in K^8}.

The binary support rank of a vector is the F2 rank of the labels of its nonzero
coordinates. Let pi_S delete ONE arbitrary common coordinate set S.

Conditional theorem. For |S| <= 35 and arbitrary residual vectors q1,q2,q3
with binary support ranks at most 5,6,6 respectively,

    dim_K(pi_S(C) intersect span_K(q1,q2,q3)) <= 1.

The pieces may overlap, be dependent, and have arbitrary coefficients. Their
support-rank restrictions apply only after deletion. This extends PR3353's
sufficient common-cut bound 34. It establishes neither sharpness nor a caller.

## Inherited premises

SOURCES.json pins five live inputs from canonical main
6f100d4bb5083f8c35d96fd95a539811c62f245c. Their authentication does not prove
their mathematics. The following premises remain conditional.

* PR3299, retained as p112-mixed566-cut32/PROOF.md, supplies the global live
  capacities 12 and 20, the E6 live-union lower bound 78, rank-six E6 joint
  incidence 32, the singleton argument, and the characteristic-zero parabolic
  normalization. The standard real Weyl-chamber theorem remains inherited.
* PR3325, retained as p112-mixed566-cut33/PROOF.md, supplies rank-five plus
  rank-six full-axis union at most 28, rank-five concentration at ten axis
  labels, small-fiber rank-five capacity eight, and PR3292's rank-six live
  capacity eighteen after four orthogonal frame punctures. A full small D6
  fiber has twelve roots. These results include arbitrary ambient support
  spaces and full-root closure where used.
* PR3324, retained as d6-axis-concentration14/PROOF.md, supplies rank-six
  concentration at fourteen full-axis labels. It also supplies the bulk
  decomposition used in the separate check below. A full D6 axis consists of
  one exceptional root a and 32 bulk roots spanning a binary seven-space W.
  The exceptional label lies outside W, and W has no other full E8 roots.
* The retained e8-a2-joint-incidence20/PROOF.md proves full-E8 rank-five E6
  joint incidence 20. This strengthens the older bound 22 used by PR3353.
  Taking live subsets and deleting coordinates preserves its inequality.

The new finite contribution is the near-axis lemma below and its composition
with these bounds. Historical capacity, concentration, pair-union and E6
proof replays are unrun. Geometry.py is the only executed predecessor source.

## Normalize a hypothetical two-dimensional intersection

Choose two independent restricted codewords in the piece span, and lift them
to c_h,c_k in C. Extend the pieces by zero on S. Let U be the union of the
full live supports of c_h,c_k, T=U minus S, and N=|T|. If M_i is the whole
residual support size of piece i, including coordinates outside U, then

    |U| <= |S| + M1+M2+M3 <= 35+12+20+20 = 87.

At least 25 live roots annihilate both lifts. Their rational span Z has rank
at most six, also over K by characteristic-zero rank invariance. Every full
root in Z annihilates both lifts. A generic real vector perpendicular to Z
avoids every other root hyperplane. The inherited Weyl-chamber argument makes
the roots in Z a parabolic subsystem. Rank-at-most-five parabolics have at
most 20 lines; other rank-six types have at most 21. Thus Z has rank six and
the normal plane has type E6 or D6. In particular it has a rational basis.
The replay checks all 56 five-node and 28 six-node faces at the new 25-zero
threshold. This is finite evidence for the inherited classification argument.

A fixed two-by-three coefficient matrix expresses the restricted codewords
in the pieces. At a site of T where only q_i is nonzero, the nonzero
evaluation pair lies on the projective line of column i. Thus all J_i
singleton sites of one piece belong to one projective fiber. Zero columns
have no singleton sites. This permits cancellations and coefficients outside Q.

The two bounds used below are

    2N <= sum_i(M_i+J_i),
    J_i >= N - sum_(j != i) M_j.

The first counts each nonsingleton site at least twice. The second counts
sites not covered by the other two pieces. Support outside T can only weaken
these inequalities, so it creates no additional assumption.

## E6

The sharper rank-five incidence 20 gives the strict contradiction

    86 = 2*(78-35) <= 2N <= 20+32+32 = 84.

The older bound 22 would leave equality at this cut. The improvement here
uses the retained sharp E6 lemma, whose discovery and proof retain their credit.

## A new full-D6 near-axis lemma

For an ordered orthogonal root pair a,b, let F_a,F_b be its two disjoint
33-root large projective fibers and U_full its 90-root nonzero union.
Let A have binary rank at most five and contain at least nine roots of F_a,
but also a full E8 root outside F_a. Let B_a,B_b be arbitrary rank-at-most-six
root supports confined to F_a,F_b. If each B has more than sixteen roots,
then

    |(A union B_a union B_b) intersect U_full| <= 45.

Here A may be replaced by its full-root binary closure, which only enlarges
the union. Nine leading-one labels cannot have binary rank at most four,
since that affine section has at most eight points. They therefore span A's
entire five-space. In particular this five-space lies in span(F_a), a binary
eight-space. This is why no ambient support space is omitted by the census.

The primary check enumerates all 97,155 five-spaces in this eight-space by
their unique reduced-echelon annihilators. Exactly 60 distinct full-root
closures have at least nine roots on F_a and another root outside F_a.
Each has exactly nine axis roots and twelve full roots in total.

For either axis, intersect an arbitrary rank-six ambient support space with
the axis eight-space and extend to a six-space there. This enlarges its axis
support. Enumerating all 10,795 six-spaces gives exactly sixteen distinct
sections larger than sixteen, each of size twenty. Comparing the 60 near-axis
closures against all 16*16 pairs gives 15,360 unions. Their maximum coverage
is 45, and each of the sixty individual maxima is 45. RESULT.json records the
closure digests and a literal rank-five witness.

The check also reconstructs all eight simple-reflection permutations. The
graph of each permutation on nine-bit root labels has binary rank nine,
equal to the domain label rank, so it is an invertible linear label map.
The canonical ordered pair reaches every one of the 7,560 ordered orthogonal
pairs. Root supports, ranks, outside-axis status and the full nonzero union
are preserved. Therefore the finite lemma holds for every ordered pair.
No fixed-frame transport assumption is needed for this full-root statement.

The separate reconstruction uses all 35,960 four-root subsets of the 32-root
bulk of F_a. For a nonconcentrated five-space with nine axis roots, its
intersection with the bulk seven-space has dimension at most four. It must
contain the exceptional root and exactly eight bulk roots. Those eight roots
span dimension four by the leading-one bound, so a four-root basis appears
in this enumeration. Adjoining the exceptional label recovers the same sixty
full closures. All 127 hyperplanes in each bulk seven-space recover the same
sixteen large rank-six sections. Concentration14 justifies this latter
contained-space reduction for sections with more than sixteen roots. This
implementation agrees on all closure digests and the bound45. It shares the
authenticated geometry and small coordinate helper; it is not an independent
audit of the root model or the inherited transport theorem.

## D6 union 82

The exact live D6 unions are 82,84,85,86,88. The budget87 excludes 88.
For union82, N>=47. Initially J2,J3>=47-12-20=15, so their singleton fibers
are large axes and concentration14 confines their entire supports there.
Each axis has four orthogonal frame punctures, explicitly checked on all
896 ordered axes of this type. Its live rank-six capacity is eighteen.

Now J1>=47-18-18=11. Small-fiber capacity eight and concentration10 confine
the rank-five piece to a large axis too. If it is alone, coverage is at most
12+29=41. If a rank-six piece is alone, coverage is at most 18+28=46.
All three on one axis cover at most29. Thus N<=46<47.

## D6 union 84

Here N>=49, so J1>=9 and J2,J3>=17. All singleton fibers are large, and both
rank-six pieces concentrate. If the rank-five piece concentrates too, the
inherited pair-union bound gives total coverage at most48, below49.

Otherwise it has at least nine singleton sites on one large axis and some
support outside that axis. If both rank-six pieces occupy the same axis,
they and the rank-five piece cover at most33+12=45. If either rank-six piece
has at most sixteen support sites, total coverage is at most12+16+20=48.
In the remaining case the two rank-six supports occupy different axes and
each has more than sixteen sites. The new full-D6 near-axis lemma bounds
coverage inside the full nonzero union, hence also inside its P112 subset,
by45. Every case contradicts N>=49. The rank-five piece need not concentrate.

## D6 unions 85 and 86

The retained sizes are at least50 and51. Singleton lower bounds are
respectively 10,18,18 and 11,19,19. All singleton fibers are large, and all
pieces concentrate. If all pieces occupy one axis, coverage is at most33.
If the rank-five piece is alone it is at most12+33=45. Otherwise it is at
most20+28=48. Thus 48<50 and 48<51 finish these branches and the theorem.

## Scope, limits and credit

This is a conditional support/code theorem with new exact finite D6 evidence.
It is not a finite search failure or proof-kernel formalization. The separate
implementation is internal computational corroboration, not human review.
No sharpness, literal caller, full C5, global decoder floor, physical/native
program, frames/restoration/hosting, consumer invoice, supplier admission,
all-size multiplication theorem, new kappa or selected-frontier change follows.

At cut36 the E6 inequality becomes84<=84 and the union82 two-axis bound
becomes46<=46. These are limits of this proof, not counterexamples. An actual
coefficient-compatible equality configuration or a new exclusion is needed.

Credit Nick Petalas's PR3353/3325/3299/3295/3324/3292 and retained sharp A2
incidence20 proof, PR3278/3269/3267/3260/3262, David Arias's quadratic model,
DreamingOfClouds/PR3154, joaqcoo and the root-simplex/E8/P112 source lineage.
Frozen predecessor files and selected science are unchanged. Apache-2.0.
