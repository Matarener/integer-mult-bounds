# A one-query obstruction for the changed two-carrier gate

The current carrier map is

\[
C_f=\begin{pmatrix}Q_f-I&N_f\\Q_f&0\end{pmatrix},
\]

on two arbitrary independent banks, each of physical dimension
\(M\). Here both \(Q_f\) and \(N_f\) are
unitary and nonmonomial in the **physical** coordinate basis. For the
actual admitted primal and dual reflections,
\(Q_f=N_iR_jN_i^{-1}\) or \(N_iS_jN_i^{-1}\), each has native arity
\(2f\), and the actual common native \(N_f\) also has arity \(2f\).
No original-input reader or initialized bank is assumed.

Suppose one unary query, on bank0, implemented this map between free
invertible endpoints. Equivalently,

\[
C_fG_f=F_f\operatorname{diag}(U_f,I).
\]

The second column of the right side is free. Writing the second column
of \(G_f\) as \((g_0,g_1)^T\), the bottom equation is
\(Q_fg_0\in\mathcal A_f\). Once this forces \(g_0=0\), the top equation
is \(N_fg_1\in\mathcal A_f\). If this also forces \(g_1=0\), then
\(G_f\) is singular. A query on bank1 instead leaves the first column
untouched and gives exactly the same contradiction. The argument does
not depend on \(U_f\), its rank, its phase or its native recipe.

## Fixed finite uniform tensor endpoints

Let \(H\) be a fixed finite set of distinct rays of invertible physical
monomial base matrices. Its members act at sizef by their tensor powers;
scalar Gaussian phases may be absorbed into arbitrary scalar
coefficients. Let \(\mathcal A_f\) be their linear span. The endpoints
may have arbitrary coefficients depending onf.

If a base matrix \(Q\) is nonmonomial, no \(Qh\), for \(h\in H\), is
proportional to a physical monomial: right multiplication by a monomial
only permutes and rescales columns. The rays \(Qh\) are also distinct
from each other. Thus the two finite ray sets \(QH\) and \(H\) are
disjoint. Distinct nonproportional vectors have linearly independent
tensor powers for every sufficiently large degree. An explicit proof
chooses, for each rayi, a product of linear forms that kills every other
ray but does not kill rayi; multiplying by another nonvanishing linear
form raises this separating polynomial to any larger degree. For at
most \(2|H|\) rays, degree \(2|H|-1\) suffices.

Consequently \(Q_fg_0\in\mathcal A_f\) implies \(g_0=0\) for every
sufficiently largef. The same holds for \(N_f\). This excludes a
one-query factorization valid for allf in this endpoint algebra. It
holds separately in every Gaussian phase residue, and allows arbitrary
f-dependent scalar endpoint coefficients. It uses independence of
tensor rays, rather than linear independence of the matrices atf1.

This theorem covers finite groups of uniform tensor physical monomials
and their full group-algebra GL endpoints. It does not, by itself,
cover a sequence of growing nonuniform controllers whose support is
not contained in one fixed finite base-ray set.

## Arbitrary physical monomial controllers: an actual scan bound

There is an independent argument that allows nonuniform controllers.
For any unitary matrixQ with maximum entry modulus \(\mu\), and any
nonzero vectorx, Cauchy's inequality gives

\[
|\operatorname{supp}x|\,|\operatorname{supp}Qx|\ge\mu^{-2}.
\]

Indeed every output coordinate has modulus at most
\(\mu\sqrt{|\operatorname{supp}x|}\|x\|_2\); summing its square over
the output support and using unitarity proves the claim.

Assume every physical column of each endpoint block has support at
most \(K_G\) or \(K_F\), respectively. Apply this inequality separately
to every physical input column of \(Q_fg_0\) and \(N_fg_1\). If

\[
K_GK_F<\min(\mu_{Q_f}^{-2},\mu_{N_f}^{-2}),
\]

both vectors must vanish, so the same untouched-column contradiction
applies. Therefore a one-query factorization requires the reverse
weak inequality.

The accompanying exact Gaussian calculation conjugates the actual
one-bit X-character monomials by the64-point Walsh matrix. ForN and
all18 primal/dualQ operators, every physical column has exactly4
nonzero entries, all of modulus1/2. All64 columns are independently
checked orthonormal with integer Gaussian arithmetic. The native
tensor recipes give \(\mu_{Q_f}=\mu_{N_f}=2^{-f}\) exactly. Hence

\[
K_GK_F\ge 2^{2f}.
\]

A physical bank ADDRESS or Pauli monomial preserves column support.
Each scalar bank ADD can at most double the support of a full bank
column. If the endpoint words use \(a_G\) and \(a_F\) such ADDs, then
\(K_G\le2^{a_G}\), \(K_F\le2^{a_F}\), and necessarily

\[
a_G+a_F\ge2f.
\]

This proves that no fixed number of actual dyadic scalar ADD/ADDRESS/
Pauli bridges gives a one-query all-size implementation ofC. It permits
a growing \(O(f)\) ADD word; it does not silently declare those scans
free.

The helper extension permits any finite number \(h\) of additional
restored identity banks, each also of dimension \(M\), with the single
query acting on one \(M\)-dimensional bank. All unqueried columns have zero entries in
both carrier rows. Their input subspace has dimension \((h+1)M\), but
their image under \(G\) lies in the helper rows, of total dimension \(hM\).
Thus \(G\) cannot be injective. This argument allows arbitrary independent
dirty inputs in every helper bank; it does not assume zero helpers.

For variable helper dimensions of total \(K\), the same dimension step
works whenever the query width \(w\le M\), provided the preceding
carrier-row vanishing applies to every unqueried physical column:
the unqueried input dimension is \(2M+K-w\ge M+K>K\), while its image
is confined to the \(K\) helper coordinates. No claim here permits an
arbitrarily larger single queried helper bank. The restriction on
query width is essential to this dimension argument.

## Scope, attribution and remaining obligations

The root supplied the untouched-column argument and its independent
support-uncertainty refinement. The native worker supplied the actual
single-query primal/dual recipes, exact Gaussian phases and arities.
The present composition check supplies the full current-column proof,
the all-size tensor/sparsity arguments and the independent actual-base
Gaussian certificate. These are written proofs supported by finite
exact calculations, not formal-kernel proofs.

This result closes the one-query version of this particular changed
localC gate under the stated endpoint contracts. It does not establish
a full-caller stock floor for the enlarged reflection grammar or rule
out a different jointly compensated caller. No positive five-query
two-bank caller, owner allocation or asymptotic improvement is claimed.
