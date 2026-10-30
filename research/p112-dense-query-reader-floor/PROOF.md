# Dense two-indicator queries retain the actual-reader floor

## Statement

Use the selected 112 binary port labels and Tekalign's PR3370 partition into
sixteen even orthonormal groups. Each consecutive pair in a group is a complete
plane. An alternating half of a group contains one port from every plane.
Choose two distinct alternating-half indicators a,b. Their supports are disjoint.
Their groups G_A,G_B have sizes m_A,m_B and may coincide.

For a scalar vector v, let cl(v) contain both ports of each plane touched by a
nonzero entry. Arithmetic in coefficients is over an arbitrary field F. Charge
an actual reader u and source query q by the binary rectangular rank

    C(u,q) = rank_F2 Gram(cl(q),cl(u)).

Suppose a finite list realizes

    aa^T + bb^T = sum_i u_i q_i^T,
    q_i = x_i a + y_i b,

where every nonzero query has both x_i and y_i nonzero. Readers are arbitrary;
they may cancel outside the target. Query count, direction count, repetitions,
scalars, signs and denominators are unrestricted. Zero queries can be discarded.
Then

    sum_i C(u_i,q_i) >= 2 max(m_A,m_B) >= m_A+m_B.

This closes the dense case with arbitrarily many directions in PR3429's
longer-list question. The lower bound is attained for the two halves of one group over
every field with more than two elements. For different groups, this note does
not claim that 2 max(m_A,m_B) is attainable. Over F2 there is only one dense
projective direction in this pair span, so no such list realizes the rank-two
target. The implication is valid but vacuous there.

## Every target port needs at least two active readers

Fix p in supp(a). Comparing the p-th rows of the exact operator identity in
the independent basis a,b gives

    sum_i u_i(p) (x_i,y_i) = (1,0).

If no reader is active, the left side vanishes. If exactly one reader is
active, its second coordinate is nonzero because both u_i(p) and y_i are
nonzero in a field. Neither possibility equals (1,0). At least two readers
are therefore nonzero at p. At a port in supp(b), the same argument uses the
first coordinate of the target (0,1). This is an all-field support argument;
no reduction of F-valued coefficients modulo two occurs.

## Each reader pays for the planes it touches in either target half

Every nonzero query has source closure G_A union G_B. For a reader u_i define

    d_A(i) = 2 |{p in supp(a) : u_i(p) != 0}|,
    d_B(i) = 2 |{p in supp(b) : u_i(p) != 0}|.

Because a contains one port from each plane of G_A, its active ports select
exactly d_A(i) distinct complete-plane coordinates in cl(u_i). Restrict the
source rows of Gram(cl(q_i),cl(u_i)) to G_A and the reader columns to these
coordinates. Orthonormality of G_A makes these columns independent. Thus

    C(u_i,q_i) >= d_A(i).

The same restriction to G_B proves C(u_i,q_i) >= d_B(i). This remains true
when the groups coincide, and when other reader entries lie outside both
groups. Those entries cannot decrease rank.

The two-active-reader property gives

    sum_i d_A(i) >= 2 m_A,
    sum_i d_B(i) >= 2 m_B.

Summing each rank inequality separately proves the asserted 2 max(m_A,m_B)
floor. A more detailed inequality, useful for individual invoices, is

    sum_i C(u_i,q_i)
      >= (sum_i d_A(i) + sum_i d_B(i) + sum_i |d_A(i)-d_B(i)|) / 2
      >= m_A+m_B + sum_i |d_A(i)-d_B(i)| / 2.

It follows directly from C(u_i,q_i) >= max(d_A(i),d_B(i)). The proof uses
actual reader support, rather than query self-Gram costs or a binary assignment
of projective directions. Four or more dense directions cause no new case.

## Attainment and a whole-matrix consequence

For the two halves of one group G of size m and any t in F other than 0,1,
choose

    q_1 = a+b,       u_1 = (t a-b)/(t-1),
    q_2 = a+t b,     u_2 = (b-a)/(t-1).

Expanding gives u_1 q_1^T + u_2 q_2^T = aa^T+bb^T. Every coefficient of each
query and each reader on these halves is nonzero. Each closure is G, so each
term costs m and the total is 2m. This establishes uniform sharpness without
claiming an optimizer for every different-group pair.

Disjoint replacements of literal indicator pairs by lists satisfying this
theorem cannot reduce the literal total 224. Each replacement costs at least
its removed m_A+m_B bill. Untouched terms retain their original bills.
This is an additive-tariff statement, not a native program or supplier.

## Exact predecessor comparison

PR3383 at 8892cef50eee2700f1d531874c8f304a891cdf20 bounds a different quantity,

    tau(q) = rank_F2 Gram(cl(q),cl(q)).

It proves the sharp whole-K total 224 for every finite spanning list in the
literal row space. It does not involve actual reader vectors. Adding untouched
indicators embeds the present pair realization into a whole-K factorization,
but its conclusion only bounds sum tau(q_i). A reader on one plane can have
C(u,q) smaller than tau(q), so that conclusion does not transfer termwise.
PR3398 makes the distinction explicit with its 218 self-cost, 244 actual-reader
example. The present replay includes a literal partial-reader witness for
C < tau. It is not an exact factorization or a lower-cost construction by itself.

PR3429 at ffd6d6a9060e12fe7b7854f90aca7f8aa4ca211d proves the actual-reader
floor for at most three projective directions, including axes. Its abstract
four-direction limitation concerns its support-dominated binary-map method.
The direct two-cover proof here removes the direction limit for dense queries
and requires no pending predecessor theorem or code. Lists mixing axis queries
with four or more nonaxis directions remain outside this note.

## Verification and limits

The written argument proves the universal theorem. The finite replay checks
all 496 literal pairs and all reader-support subsets within their target halves,
plus exact rational realizations with 2,4,7 directions and cancelling outside
readers. The two-coefficient operator checks cover all 112 rows in the independent
a,b basis and hence imply the entire 112-by-112 operator identity. A separate
implementation checks the same geometry and pointwise argument over finite
fields. These are author checks. Independent human and formal proof-kernel
review are unclaimed.

Mixed axis/nonaxis longer lists, external query dimensions, changed fitting
matrices and shared native operations remain open. Acquisition, coefficient
execution, frames, dirty restoration, hosting, stock, precision, all-size and
compiler hypotheses, both supplier admissions and the outer multiplication
transfer are not supplied. No improved kappa or selected-frontier change follows.
