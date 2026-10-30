# Sharp conditioning price of signed rank transport

This proof was produced by Nick Petalas. Apache-2.0.

## Statement

Use Jeremy Diviney's PR #836 model and signed rank potential, with a finite
group G, W independent arbitrary-input roles, a symmetric subadditive metric
r on G, arbitrary invertible complex scalar mixing and paid left row
multiplications by h of price c >= r(h). A free group call has r(h)=0.
Every prefix S is invertible in Mat_W(C[G]). Its faithful left regular matrix
is denoted A(S), and K(S)=||A(S)||_2 ||A(S)^(-1)||_2 >= 1.

For every paid call on row i, immediately before that call,

    |Delta Phi| <= c (K(S)+K(S)^(-1))/2.                 (1)

The constant in (1) is sharp at every real K >= 1, already for two roles
and G=C2. Sharpness is local: it does not assert that a complete cheaper
endpoint exists.

If a complete endpoint has constant metric m_j on the formal support of
each input column j, put M=sum_j m_j. If its paid prices sum to s>0, then

    M <= sum_k c_k (K(S_k)+K(S_k)^(-1))/2.              (2)

In particular, if M>s, at least one paid prefix satisfies

    K(S_k) >= M/s + sqrt((M/s)^2-1).                  (3)

For M=9 and eight unit-price calls, this is

    K(S_k) >= (9+sqrt(17))/8 > 41/25.

The rational lower comparison is strict because sqrt(17)>103/25,
as 17*625=10625>10609=103^2. PR #836's norm-product diagnostic gives
only K(S_k)>=9/8 through its stated K_i<=K(S_k) comparison. The new
threshold is a necessary condition in the same finite-group formal model.

## The spectral inequality

For any invertible finite complex matrix A and unit vector e, put

    R=e*AA*e, L=e*(AA*)^(-1)e,
    a=sigma_min(A)^2, b=sigma_max(A)^2.

Here stars mean conjugate transposes, and e* denotes the row corresponding
to the column e. In a spectral basis, R and L are weighted averages of
lambda and lambda^(-1) on [a,b], using the same nonnegative weights summing
to one. Since (lambda-a)(lambda-b)<=0,

    lambda+ab/lambda <= a+b,
    R+ab L <= a+b,
    4ab R L <= (R+ab L)^2 <= (a+b)^2.

Taking square roots gives the classical Kantorovich bound

    ||e*A||_2 ||A^(-1)e||_2 <= (K+K^(-1))/2.          (4)

Indeed the first norm squared is R and the second is L, since
A^(-*)A^(-1)=(AA*)^(-1). Equality for a<b requires equal spectral weight
on the minimum and maximum eigenvalues of AA*. The scalar inequality,
spectral theorem and Kantorovich bound are classical; the application and
attaining formal register family below are the contribution.

## Applying the inequality to the formal coefficients

Write S_ij=sum_g a_ij(g)[g] and (S^(-1))_ji=sum_g b_ji(g)[g].
PR #836 proves, for the actual formal inverse,

    p_ij(g)=Re(a_ij(g)b_ji(g^(-1))),
    sum_(j,g) p_ij(g)=1,
    Delta Phi=sum_(j,g)(r(hg)-r(g))p_ij(g).

The metric hypotheses imply |r(hg)-r(g)|<=c. Thus

    |Delta Phi| <= c sum_(j,g)|a_ij(g)b_ji(g^(-1))|
                <= c sqrt(R_i L_i),
    R_i=sum_(j,g)|a_ij(g)|^2,
    L_i=sum_(j,g)|b_ji(g^(-1))|^2.

In the left regular representation, [g] sends e_x to e_(gx). Fix the
address 1 and role i. The corresponding matrix row lists a_ij(x^(-1)),
while the inverse column lists b_ji(x). Hence their squared norms are
exactly R_i and L_i. This uses a faithful representation, with no
identification of dependent concrete frame matrices with formal coefficients.
Apply (4) to this matrix row and inverse column to obtain (1).

PR #836 also proves that scalar mixing and metric-zero calls preserve Phi,
that Phi(I)=0, and that the stated full endpoint has Phi=M. Sum (1) over
the paid calls to get (2). The function (K+1/K)/2 increases on [1,infinity).
Consequently the largest paid-prefix K has (K+1/K)/2 >= M/s. Solving the
quadratic gives (3). The finite word has finitely many paid prefixes, so
the maximum exists. Dirty restored columns may have m_j=0; they are still
independent inputs in the full regular matrix.

## A family attaining the local constant

Let G={1,t}, t^2=1, and r(1)=0,r(t)=1. For v>=1 put

    a=(v+v^(-1))/2, b=(v-v^(-1))/2,
    B=[[a,b],[b,a]], D=diag([1],[t]),
    S=D B D=[[a[1],b[t]],[b[t],a[1]]].

This is a legal prefix: two row-t calls and one invertible scalar mixer
produce it. All role inputs remain independent; no clean state is used.
Its inverse has a on the diagonal and -b[t] off the diagonal, because
a^2-b^2=1. In the faithful regular representation, D is orthogonal and
B has positive eigenvalues v and 1/v, each repeated twice after lifting.
Thus K(S)=v^2. Before multiplying the first row by [t], the two nonzero
pairings on that row are a^2 at 1 and -b^2 at t. The call therefore gains

    Delta Phi=a^2+b^2=(v^2+v^(-2))/2=(K+K^(-1))/2.

This proves equality in (1) for every K>=1 by taking v=sqrt(K). The
exact executable fixtures use rational v; irrational parameters belong
to the written theorem, not the finite rational enumeration. The same
prefix has Phi=-2b^2, and the next prefix has Phi=1. It has no promised
full constant-rank endpoint. Neither its gain nor its conditioning is
evidence for an eight-call solution.

## Scope and predecessor credit

PR #836, Jeremy Diviney, supplies the signed rank potential, its transport
identity, endpoint normalization and original nonunitary search diagnostic.
Those are cited inputs; this package does not replay the predecessor word
examples or audit their counts. Nir Ailon supplies the retained
forward/inverse-potential context. Credit eumemic #288, Swapnil Jain and
the retained register/frame lineage; littleBro #680/#705 supplies the
predecessor's finite Clifford context. No predecessor code is imported.

The result uses finite groups, complex coefficients and full invertible
arbitrary-input words. An infinite-group extension, restricted-input clean
ancillas, nonfaithful concrete representations, a physical word, complete
supplier, paid physical invoice, compiler, precision/tape, stock, analytic
recovery and a multiplication exponent are outside scope. Independent
human and formal proof-kernel review are unclaimed.
