# Exact paid-history minimum for arbitrary targets in the full-Pauli model

This contribution was produced by Nick Petalas. Apache-2.0.

## 0. Model and source

The model is the one in JoyboyBrian's
[PR #5482](https://github.com/CrocSwap/integer-mult-bounds/pull/5482)
(`research/pauli-twisted-history-threshold/PROOF.md`, pinned in
SOURCES.json). Let K=Q(i), X=[[0,1],[1,0]], Z=diag(1,-1), and fix a positive
width f. Put V=(K^2)^tensor f, P=X^tensor f, C=Z^tensor f and
R=span_K{I,P,C,PC}. A field is a row (A_1,...,A_N) in End_K(V)^N, meaning
sum_v A_v w_v for N independent whole-field inputs w_v. Ordinary operations
are left multiplication by elements of R, K-linear row combinations, COPY
and CLEAR. Each paid call returns one additional row. The initial history
is I0=R^N. After returns t_1,...,t_m every available field lies in

    M = I0 + R t_1 + ... + R t_m,                          (0)

because ordinary operations preserve this left R-module and each return
adjoins one row. #5482 proves (0) and the predecessor facts used below:
P^2=C^2=I, PC=(-1)^f CP, and dim R=4. We cite these. We do not recheck them.

The new question is the predecessor's own open boundary: it "does not
classify arbitrary Pauli-nonordinary matrices." Here the requested outputs
are H_j e_(v_j) for q distinct owners v_j and **arbitrary** H_j in End_K(V),
up to ordinary background. Equivalently H_j e_(v_j) lies in M.

The **history minimum** m*(H_1,...,H_q) is the least m for which returns
t_1,...,t_m exist with every H_j e_(v_j) in M. Every #5482 program satisfies
(0), so m* is a lower bound on its paid returns. The returns achieving m*
below are explicit rows. Whether one native paid operator applied to one
current field can produce them is a separate question, which this package
does not decide (Section 5).

## 1. Structure of R

**Even f.** P and C commute, so R is commutative, with four orthogonal
idempotents

    E_(e,h) = (I + eP)(I + hC)/4,   e,h in {+1,-1},

summing to I. They satisfy E_chi r = chi(r) E_chi for the character chi of R
with chi(P)=e and chi(C)=h. So E_chi R = K E_chi. Each E_chi has trace
2^(f-2), because P, C and PC are traceless for f>=1.

**Odd f.** PC=-CP. Put e11=(I+P)/2, e22=(I-P)/2, e12=(I+P)C/2 and
e21=(I-P)C/2. Since C(I-P)=(I+P)C, these satisfy the matrix-unit relations
e_ab e_cd = delta_bc e_ad. Thus R is isomorphic to M_2(K). Every left
R-module is semisimple and isomorphic to S^d for the two-dimensional simple
module S. As a left module R is isomorphic to S^2. On V, R acts as
S^(2^(f-1)), so every nonzero element of R has rank at least 2^(f-1).

## 2. Theorem 1: the exact minimum for arbitrary targets

For a target H define its **nonordinary invariant**:

* even f: the profile Pi(H) = {chi : E_chi H is not in K E_chi};
* odd f: the excess s(H) = (dim_K(R + R H) - 4)/2, an integer in {0,1,2}.

**Theorem 1.** For distinct owners and arbitrary H_j,

    even f:  m* = max_chi #{ j : chi in Pi(H_j) },
    odd f:   m* = ceil( (s(H_1) + ... + s(H_q)) / 2 ).

*Lower bound, even f.* Left multiplication by E_chi is R-linear because R
is commutative. Apply it to (0):

    E_chi M = (+)_v K E_chi e_v + sum_k K E_chi t_k,

so dim(E_chi M / E_chi I0) <= m. The vectors E_chi H_j e_(v_j) lie in
E_chi M. Modulo E_chi I0, the j-th one is nonzero exactly when chi is in
Pi(H_j). Distinct owners occupy distinct coordinates, so these vectors are
independent. Hence m >= #{j : chi in Pi(H_j)} for every chi.

*Lower bound, odd f.* M is a left R-module and each R t_k is a quotient of
R, so dim(M / I0) <= 4m. The module W = I0 + sum_j R H_j e_(v_j) lies in M.
By distinct coordinates, dim(W / I0) = sum_j dim((R + R H_j)/R) =
2 sum_j s(H_j). So 4m >= 2 sum_j s(H_j).

*Attainment, even f.* For each chi list the owners with chi in Pi(H_j) as
j_(chi,1), j_(chi,2), .... For k = 1,...,mu, with mu the stated maximum, put

    t_k = sum_chi E_chi H_(j_(chi,k)) e_(v_(j_(chi,k)))

over the characters whose list has a k-th entry. Orthogonality gives
E_chi t_k = E_chi H_j e_(v_j) for the k-th owner j of chi. Then

    H_j e_(v_j) = sum_chi E_chi H_j e_(v_j).

Each term is either E_chi t_k for some k or, when chi is not in Pi(H_j), an
element c E_chi e_(v_j) of I0. So every target lies in M.

*Attainment, odd f.* The quotient W / I0 is isomorphic to S^d with
d = sum_j s(H_j). The space e11 (W / I0) has dimension d. Choose lifts
y_1,...,y_d in e11 W, independent modulo I0. For each pair put
t = y_a + e21 y_b. Then e11 t = y_a and e12 t = e11 y_b = y_b, so R t contains
both. An unpaired y is used alone. These ceil(d/2) rows generate W modulo I0.

**Consequences.** At even width the per-owner count q is forced exactly when
one character is nonordinary for every owner. At odd width it is forced
exactly when at most one owner has excess one and none has excess zero.
Neither holds for arbitrary nonordinary targets. The tensor-power
corollaries below give explicit families where they fail.

The #5482 family (aI+bX)^tensor f, with ab(a^2-b^2) != 0, has excess 2 at
odd f>=3 by its equation (2). At even f its profile contains (+1,+1) by its
Section 3. So Theorem 1 gives m* = q there, consistent with that result.

## 3. Corollary 2: every tensor square

Let f=2 and H=M tensor M for M in M_2(K). For a 2x2 matrix B, let psi_B be
the row vector with psi_B[(x,y)] = B[x,y]. A direct expansion gives

    psi_B^T (M tensor N) = psi_(M^T B N)^T.

The rows psi_I, psi_X, psi_Z and psi_J, with J=XZ, are left eigenvectors of
(P,C) for the characters (+1,+1), (+1,-1), (-1,+1) and (-1,-1). Each E_chi
has rank one, so E_chi H is in K E_chi exactly when psi_B^T H is a multiple
of psi_B^T. Hence

    Pi(M tensor M) = { B in {I,X,Z} : M^T B M is not in K B },     (1)

and the singlet character never occurs, since M^T J M = det(M) J.

**Lemma.** If M^T B M is in K B for two distinct B in {I,X,Z}, then M is in
K{I,X,Z,XZ}.

*Proof.* Write M=[[a,b],[c,d]]. Then

    M^T M     = [[a^2+c^2, ab+cd], [ab+cd, b^2+d^2]],
    M^T X M   = [[2ac, ad+bc], [ad+bc, 2bd]],
    M^T Z M   = [[a^2-c^2, ab-cd], [ab-cd, b^2-d^2]].

*{I,Z}:* ab+cd = ab-cd = 0, a^2+c^2 = b^2+d^2 and a^2-c^2 = d^2-b^2.
Then ab=cd=0, b^2=c^2 and a^2=d^2. If b=0 then c=0 and M=a diag(1,+-1).
Otherwise a=d=0 and M=b[[0,1],[+-1,0]], which lies in K{X,XZ}.

*{I,X}:* ac=bd=0, ab+cd=0 and a^2+c^2=b^2+d^2. If a=0 then cd=0. If also
c=0, then b^2+d^2=0 and bd=0 force M=0; otherwise d=0 and c^2=b^2. If a!=0,
then c=0, b=0 and a^2=d^2. Every case lies in K{I,X,Z,XZ}.

*{X,Z}:* ac=bd=0, ab=cd and a^2-c^2+b^2-d^2=0. If a=0 then cd=0. With c=0,
b^2=d^2 and bd=0 force M=0; with d=0, b^2=c^2. If a!=0, then c=0, b=0 and
a^2=d^2. Again M lies in K{I,X,Z,XZ}. QED.

Conversely, a Pauli matrix sigma satisfies sigma^T B sigma = +-B for every
Pauli B, so a projectively Pauli M has empty profile.

**Corollary 2.** If no M_j lies in K{I,X,Z,XZ}, then every profile has two
or three of the characters I, X and Z, and

    m*( M_1^tensor 2, ..., M_q^tensor 2 ) >= ceil(2q/3).

*Proof.* The profiles have total size at least 2q over three characters.
The bound is attained. 2I+X, 2I+Y and 2I+Z have profiles {I,X}, {X,Z} and
{I,Z}. Take owners of these three types in numbers a, b and c with
a+b+c=q, as equal as possible. The largest character count is
q - min(a,b,c) = ceil(2q/3). For q=3 this gives two returns for three
owners, whereas the per-owner count is three.

## 4. Corollary 3: every rank-one target at width at least three

Let M = u w^T with u,w nonzero. Put U = u^tensor f, so H = U (w^tensor f)^T
and every element of R H has rank at most one.

**Tensor-power lemma.** If v_1,...,v_n in K^2 are pairwise nonproportional
and f >= n-1, then v_1^tensor f,...,v_n^tensor f are linearly independent.
*Proof.* Suppose sum_i c_i v_i^tensor f = 0. Pair it with g_1 tensor ... tensor g_f,
where the g_t are linear forms. Choose forms vanishing at each v_k with
k != i, and pad with forms nonzero at v_i. The result is c_i times a
nonzero number, so c_i = 0.

Call u a **Pauli eigenvector** if u is an eigenvector of X, Z or XZ. If u is
not one, then u, Xu, Zu and XZu are pairwise nonproportional. For instance,
Xu proportional to Zu would make u an eigenvector of ZX, which is
proportional to XZ. By the lemma, RU = span{U, PU, CU, PCU} has dimension 4
for f>=3. If u is a Pauli eigenvector sigma u = lambda u, then sigma^tensor f
fixes the line of U. Then RU = span{U, tau U} for a second Pauli tau, of
dimension 2 by the lemma.

**Odd f>=3.** Nonzero elements of R have rank at least 2^(f-1) >= 4 > 1, so
R intersect RH = {0} and dim(R+RH) = 4 + dim RU. Therefore

    s(u w^T tensor power) = 1 if u is a Pauli eigenvector, else 2.

So q rank-one owners whose u_j are Pauli eigenvectors need exactly
ceil(q/2) returns in the history minimum. For example, two owners with
targets E11^tensor f need one.

**Even f>=4.** E_chi has rank 2^(f-2) >= 4, and E_chi H = (E_chi U) w^T has
rank at most one. Hence E_chi H lies in K E_chi only when E_chi U = 0, and
Pi(H) = {chi : E_chi U != 0}. If u is not a Pauli eigenvector, then
E_chi U = (1/4) sum_r chi(r) r U is a nonzero combination of four
independent vectors, so all four characters occur. Otherwise exactly two
occur:

| u | profile |
|---|---|
| X-eigenvector (1,+-1) | {(+1,+1), (+1,-1)} |
| Z-eigenvector e_1 or e_2 | {(+1,+1), (-1,+1)} |
| XZ-eigenvector (1,+-i), f = 0 mod 4 | {(+1,+1), (-1,-1)} |
| XZ-eigenvector (1,+-i), f = 2 mod 4 | {(+1,-1), (-1,+1)} |

*Proof for the table.* For an X-eigenvector PU = U, which kills e=-1.
(I+hC)U is nonzero because U and CU are independent. The Z case is
symmetric. For u=(1,+-i), PC U = lambda^f U with lambda^f = (-1)^(f/2), so
only characters with eh = (-1)^(f/2) can survive. For such a character a
direct expansion gives (I+eP)(I+hC)U = 2U + (h + e(+-i)^f) CU, which is
nonzero.

So when f = 0 mod 4, all Pauli-eigenvector rank-one profiles share (+1,+1),
and q such owners need q returns. When f = 2 mod 4, the three types give
the same ceil(2q/3) sharing as Corollary 2.

## 5. Scope and limitations

* m* is the exact minimum of the one-row-per-return history count of
  #5482. The lower bound applies to every #5482 program. Attainment uses
  explicit returned rows, and Theorem 1 does not show that a native paid
  operator applied to one current field produces them. #5482's own upper
  bound has the same kind of hypothesis: each requested H_j must be an
  available paid primitive.
* Corollaries 2 and 3 cover every tensor square and every rank-one tensor
  power at f>=3. Invertible non-Pauli M at f>=3 is **not** classified here.
  The verifier finds full invariants (excess 2, or all four characters) for
  the tested invertible cases at f=3,4,5. Those are finite observations, not
  a proof.
* No paid-call bound for a physical caller, no recursive profile and no κ
  change follow. Nonlinear programs, approximation, multiple outputs per
  call and changed geometry are excluded, as in #5482.

## Credit

JoyboyBrian's PR #5482 supplies the model, the history-module inclusion (0),
the algebra facts it proves, and the q-call theorem for (aI+bX)^tensor f.
That package credits Chris R / Clear1nsight, the PR5425/PR5446 history
authors and Ali Romman's PR5450, and those credits carry over. Theorem 1,
the module decomposition, the width-two classification, the rank-one
classification and the sharing constructions are new here. The algebra
used is classical: matrix units, semisimple modules and tensor-power
independence.
