# A finite period does not always escape the formal-stage obstruction

This theorem closes the proposed eight-field/nine-full order-seven escape
under the scalar-frame contract. It uses the shortest-query normal form
from PROOF.md. It does not exclude shorter periods, initialized work,
extra queries or ordinary frames that act noncentrally on native addresses.
COUPLED.md extends this theorem to every coupled query width through a
block Schur complement; the scalar proof below is retained in full.

## Theorem

Let n be positive and even. Take n+1 full calls on n fields, with the
rank-one square-zero queries and compatible rank-two stage projectors in
PROOF.md. All coefficients are in a commutative field of characteristic
zero. Let p>=n-1. If

    W_minus(z) = -W_plus(z)

holds at every p-th root of unity, then it holds for formal z.
The statement permits arbitrary constant scalar frames and any remaining
stage endpoint. It does not require diagonal monomial targets.

For n=8 and p=7, the exact formal-stage exclusion therefore rules out the
complete cyclic query condition as well. A special choice of target powers
cannot repair it. This is stronger than the earlier cyclic reduction
lemma, which left the balanced nine-call target open.

## Proof through query Gram matrices

At z=1 put the query tuple in the complete canonical form from PROOF.md.
Write R_i=u_i v_i and D_i=I+(z-1)P_i. Work first over the rational function
field. Define

    A_i = D_n ... D_(i+1),
    u'_i = A_i u_i,       v'_i = v_i A_i^(-1),
    G'(z)_ij = v'_i u'_j.

Moving the stage factors to the right shows that the query condition is
equivalent to the ordered product of I-2u'_i v'_i being -I. At each p-th
root the normal-form proof applies. Its rank-one matrix Z has diagonal
one, so its off-diagonal Gram values have the form

    G'(z)_ij = sign(i-j) a_i/a_j.

For adjacent indices, compatibility with P_(i+1) gives

    G'(z)_(i+1,i) = v_(i+1) D_(i+1) u_i = z.

Thus a_(i+1)/a_i=z, and at every p-th root

    G'(z)_ij = sign(i-j) z^(i-j).

For i>j factor out the left endpoint stage:

    G'(z)_ij = z v_i D_(i-1) ... D_(j+1) u_j.

After division by z, both sides of the required equality are polynomials
of degree at most i-j-1. For i<j, remove the right endpoint inverse stage
instead. After division by z^(-1), the corresponding equality is a
polynomial in z^(-1) of degree at most j-i-1. The inverse roots are the
same set of p distinct roots.

If |i-j|<=p, these polynomial degrees are less than p. Equality at all
roots is therefore the formal equality. Since p>=n-1, every entry except
possibly the pair (n,0) and (0,n) is now determined formally.

Normalize the Gram matrix by

    H(z) = diag(z^(-i)) G'(z) diag(z^j).

Every known off-diagonal entry is sign(i-j), and the diagonal is zero.
Write H_(n,0)=x(z) and H_(0,n)=-y(z). The preceding endpoint factorizations
give x in F[z^(-1)] and y in F[z]. Also rank(H)<=n, because G'=V'U' factors
through the n-dimensional main space.

For this (n+1)-by-(n+1) matrix, the exact determinant is

    det H(x,y) = x-y.

Here is a proof for every even n. The determinant is at most bilinear in
x,y. Its xy coefficient is a determinant of an odd-dimensional skew matrix
and is zero. At x=y=1 the matrix is skew, has kernel
(1,-1,1,...,1), and each even principal cofactor is one. The latter fact
follows by eliminating the first 2-by-2 block: the remaining skew sign
matrix is unchanged, and that block has determinant one. The adjugate is
therefore the outer product of the displayed kernel vector with itself.
The coefficients of x and y are 1 and -1. The constant is zero, because
the matrix is skew whenever x=y. This proves the formula.

Rank(H)<=n now forces x=y. But
F[z^(-1)] intersect F[z]=F. Hence both are constant. At z=1 each is one.
Thus every normalized Gram entry is the canonical skew sign entry, even
the two corners.

The leading n-by-n Gram block is invertible. The normalized vectors
z^i u'_i and rows z^(-i) v'_i therefore give a tuple conjugate to the
original canonical tuple over F(z). Its ordered transvection product is
-I. This is exactly the formal query condition. The proof is complete.

## The actual order-seven native stage has all seven characters

The predecessor's three-coordinate cell is V=R H_0, where H_0 is the real
Hadamard on coordinate zero and

    R |x_0,x_1,x_2> = i^(x_0+x_2)
        |x_0, x_0+x_1, x_1+x_2>.

Binary address additions are modulo two. Let U=V^(tensor 8). The literal
eight-by-eight Gaussian-integer computation in period_check.py gives

    V^7 = (1-i)/sqrt(2) I,
    U^7 = I,
    trace(U^k) = 1              for k=1,...,6,
    dim(U) = 2^24.

No floating arithmetic or unsigned-tableau phase convention is used.
The eighth tensor power removes the residual seventh-power phase.
For any positive column width f, let U_f=U^(tensor f). Its dimension is
(2^24)^f and every nontrivial power still has trace one. The Hilbert-Schmidt
Gram matrix of I,U_f,...,U_f^6 is

    ((2^24)^f-1) I_7 + J_7.

It is positive definite. Thus the seven powers are linearly independent.
Together with U_f^7=I, this proves that all seven characters occur at every
positive width. The stage is faithful for the polynomial test. Since the
central involution acts on a separate axis, both query characters can be
tested at each stage character.

Consequently the new theorem applies to that actual native component, not
only to an abstract quotient that might omit some stage characters. This
does not recertify a complete source call, physical route or native price.
It proves the component fact needed for the obstruction.

## Checks and the next open boundary

The checker verifies the determinant formula on 80 exact controls through
n=32, and reconstructs the literal cell phase and traces. The written
determinant proof is uniform; those finite controls are not its proof.
The identity stage fails the faithful-character control.

The short-interval quadratic discovery test by itself was unresolved.
The two-corner determinant argument supplies the missing implication.
The saved numerical period-seven search is now unnecessary evidence for
this excluded scope. It remains in the record as discovery history.

For n=8, period six lies outside the theorem. A three-block cyclic advance
has that period and permits rank-16 and rank-24 powers. Its full endpoint,
native binding and complete price remain open. More general noncentral
frames are also outside the proof. No kappa increase follows here.

The order-seven native cell is from Ali Romman's linked prior checkpoint.
The complete shortest-query model credits Cinna Davis and the retained
P104/native/controller lineage. New interval/Gram argument and literal
character check: Ali Romman with substantial OpenAI Codex assistance.
No independent human review or worldwide priority claim. Apache-2.0.
