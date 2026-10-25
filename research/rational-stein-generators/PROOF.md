# Rational bounded generators at the dirty-shear interface

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
Apache-2.0.

I refine the coefficient generator in Vlado Vojdanovski's
`SHALLOW-TOEPLITZ.md`, Sections 5–6. The author already gives a
polynomial-time route through rational Gram–Schmidt and approximate
square-root normalization. I replace that normalization with exact dyadic
scaling and bind the resulting rational rows to the retained macro order.
I do not claim that irrational normalization invalidates the original proof.

I write \(E\in\mathbb Q(i)^{m\times m}\), \(m\ge1\), with rank \(r\).
All vector norms and unqualified operator norms are Euclidean. I distinguish
a coefficient **row** \(a\) from its adjoint column \(a^*\).

## 1. Exact rational generators with bounded magnitude

Process the columns of \(E\) in order by exact Gram–Schmidt. Skip a residual
only when it is exactly zero. Denote the nonzero mutually orthogonal residuals
by \(v_j\), and write \(n_j=v_j^*v_j>0\). Choose the least dyadic \(c_j=2^{e_j}\)
such that \(c_j^2\ge n_j\). Equivalently,
\[
n_j\le c_j^2<4n_j.
\]
We can find this integer exponent by rational squared comparisons.
Define
\[
g_j=v_j/c_j,\qquad a_j=(c_j/n_j)v_j^*E.
\]
Then all entries lie in \(\mathbb Q(i)\), and
\[
g_ja_j=\frac{v_jv_j^*}{v_j^*v_j}E.
\]
The orthogonal projectors sum to the identity on the column space of \(E\).
Thus
\[
\boxed{E=\sum_{j=1}^r g_ja_j,\qquad
\|g_j\|_2\le1,\qquad \|a_j\|_2<2\|E\|_2.}
\]
The last inequality follows from
\(\|v_j^*E\|_2\le\|v_j\|_2\|E\|_2\) and \(c_j<2\|v_j\|_2\).
A tiny nonzero residual therefore need not cause a large emitted coefficient.
The zero matrix gives an empty generator list.

For \(E=T-ZTZ^T\), where \(Z\) is the nilpotent lower shift,
\[
T=\sum_{k=0}^{m-1}Z^kE(Z^T)^k
 =\sum_j L(g_j)U(a_j).
\]
We obtain the first identity by finite telescoping; the second follows by
expanding each outer product. \(L\) uses a first column and \(U\) a first
row. We apply no additional conjugation to \(a_j\).

The source prose sometimes uses an adjoint column \(h=E^*g\), in which case
the upper Toeplitz row is \(h^*\). The numerical source stores
`vals[j] * Vh[j, :]`, which already is a row. I follow that executable
convention. For \(T=\left[\begin{smallmatrix}a&i\tau\\0&a\end{smallmatrix}\right]\),
\(a=\tau=1/16\), the Stein displacement has first row \((a,i\tau)\).
Conjugating that emitted row changes the desired operator.
This convention check does not establish a failure for the real Gaussian caller.

## 2. Admission to the retained generator macro

Let
\[
\ell(a)=\sum_k(|\Re a_k|+|\Im a_k|),\qquad
\Gamma=\min\{2^e:2^e\ge\max(1,2\ell(a))\},\qquad
P=I+U(a)/\Gamma.
\]
Then \(\|U(a)/\Gamma\|_1,\|U(a)/\Gamma\|_\infty\le1/2\).
Hence \(\|P\|_2\le3/2\), \(\|P^{-1}\|_2\le2\), and its diagonal coefficient
has modulus at least \(1/2\). Its inverse is a finite upper triangular
Toeplitz series, with rational complex coefficients.
For dyadic \(m\), these are the norm hypotheses of the retained triangular
child. The generator and macro matrix identities hold for arbitrary \(m\);
I do not extend the child's dyadic scheduling contract to other sizes.

On disjoint banks \((x,y)\), execute the source's four macros:
\[
x\gets Px,\quad y\gets y+\Gamma L(g)x,\quad
x\gets P^{-1}x,\quad y\gets y-\Gamma L(g)x.
\]
Substitution gives \(x_{\rm out}=x_{\rm in}\) and
\[
y_{\rm out}=y_{\rm in}+\Gamma L(g)(P-I)x_{\rm in}
=y_{\rm in}+L(g)U(a)x_{\rm in}.
\]
No zero-initialized bank is required. Summing the completed generator shears
therefore applies \(y\gets y+Tx\) while restoring arbitrary dirty \(x\).
The dyadic division that constructs \(P\) must allocate a fresh coefficient
vector; modifying the original row would change the final compensation.

## 3. Macro prefixes and child boundaries

Put \(B=\|E\|_2\), \(A_k=\sum_{j<k}L(g_j)U(a_j)\), and
\(\alpha=2rmB\). Since
\(\|L(g)\|_2\le\sqrt m\|g\|_2\) and
\(\|U(a)\|_2\le\sqrt m\|a\|_2\), we have \(\|A_k\|_2\le\alpha\).
Let \(K=\max_j\Gamma_j\sqrt m\), with \(K=0\) for an empty list.

Before term \(k\), the four successive global prefixes are
\[
\begin{pmatrix}P&0\\A_k&I\end{pmatrix},\quad
\begin{pmatrix}P&0\\A_k+\Gamma L(g)P&I\end{pmatrix},\quad
\begin{pmatrix}I&0\\A_k+\Gamma L(g)P&I\end{pmatrix},\quad
\begin{pmatrix}I&0\\A_{k+1}&I\end{pmatrix}.
\]
Block-triangular inversion and the preceding norm bounds give, for their
norms and inverse norms,
\[
C_{\rm macro}=2+2\alpha+2K.
\]
For example, the second prefix has inverse lower-left block
\(-A_kP^{-1}-\Gamma L(g)\), so we need no product of \(r\) large shear bounds.
Completed generator contributions add in \(A_k\).

By Cauchy–Schwarz,
\(\ell(a)\le\sqrt{2m}\|a\|_2<2\sqrt{2m}B\).
The least-power-of-two choice gives
\(\Gamma<2\max(1,2\ell(a))\le2+8\sqrt{2m}B\).
Consequently
\[
\boxed{C_{\rm macro}
\le2+4\sqrt m+4rmB+16\sqrt2\,mB
\le2+4m+4rmB+32mB.}
\]
The verifier uses the rational final expression with a row/column norm
upper bound on \(B\), and checks a stronger Frobenius upper estimate for
each executed prefix and inverse prefix.

If a separately verified child implementation has prefix and inverse-prefix
bound \(H\), one unfinished child combines with an already bounded macro
prefix through \(HC_{\rm macro}\). This does not certify the child's bound.
In particular, the replay here replaces `triangle_plan`, `toeplitz_shear`
and `inverse` by exact matrix callbacks. I do not report FFT/butterfly
execution or their internal prefixes.

## 4. Explicit polynomial preprocessing height

For a rational real component, define height as the maximum binary length
of its reduced numerator and positive denominator. Suppose all input
components have height at most \(b\ge1\). A conservative bound for the
generator preprocessing and finite \(P^{-1}\) coefficients is
\[
\boxed{\mathcal B=4096(m+1)^6(b+1).}
\]
This bounds coefficient encodings; it is not a proposed online word width.

Here are explicit estimates, including nearly dependent columns. Take
the product \(D\) of the \(2m^2\) component denominators and put \(A=DE\).
Then \(D\le2^{2m^2b}\) and the Gaussian-integer components of \(A\)
have magnitude below \(2^H\), where
\[
H=(2m^2+1)b,\quad J=2H+2m+2,\quad
T_0=m(J+m)+1,\quad V=T_0+J+H+2m+4.
\]
For any independent subset \(A_S\), entries of \(A_S^*A_S\) have
complex modulus below \(2^J\). The determinant expansion, with
\(k!\le2^{m^2}\), bounds its determinant and cofactors by \(2^{T_0}\).
The determinant \(d\) is a positive integer.

Each full or partial Gram–Schmidt residual has the form
\[
v=\frac{z}{Dd},\qquad
z=dA_j-A_S\operatorname{adj}(A_S^*A_S)(A_S^*A_j).
\]
We can bound the components of \(z\) and the common denominator \(Dd\)
by \(2^V\). This also controls intermediate residual vectors: subtracting
the first accepted orthogonal residuals projects onto the span of an
independent subset of original columns.

Write \(Z_0=\sum_i|z_i|^2\), \(W=2V+2m+2\), \(C_0=V+m+2\).
The squared norm \(Z_0/(D^2d^2)\) has numerator/denominator heights at most
\(W\). For a nonzero residual,
\(2^{-V}\le\|v\|_2\le\sqrt{2m}\,2^V\), so the exponent of \(c\)
has absolute value at most \(C_0\). The components of \(g=v/c\)
have height at most \(V+C_0+1\).

For the coefficient row, cancel before estimating:
\[
a=\frac{c}{\|v\|_2^2}v^*E=\frac{cd\,z^*A}{Z_0}.
\]
Thus its components share a denominator and have height at most
\(R=3V+3m+6\). This avoids an assumed lower bound on the nonzero singular
values of \(E\).

The norm estimate gives
\(\ell(a)<4m^{3/2}2^b\), so the exponent of the adaptive \(\Gamma\)
is at most \(b+2m+5\). Put \(H_P=R+b+2m+7\).
The \(P\) coefficients have a common integer denominator and
Gaussian-integer numerators of component height at most \(H_P\).
If \(P(z)=a(z)/d_0\), its inverse coefficient of degree \(n<m\) has form
\[
u_n=\frac{d_0b_n}{a_0^{n+1}},\qquad
|b_n|\le2^n(\sqrt2\,2^{H_P})^n.
\]
The finite composition expansion gives the displayed numerator estimate.
Rationalizing the Gaussian denominator bounds the component heights by
\(I_0=2mH_P+3m+4\).

For operation bounds, retain the common-denominator invariants.
Residual component denominators divide \(Dd\); dot-product partial sums divide the
product of two vector denominators; inverse-series partial sums at degree
\(n\) have Gaussian denominators dividing \(a_0^n\), with rationalized
denominator \(|a_0|^{2n}\). Reduced `Fraction` storage preserves those
divisibility statements. Raw cross-products in a scalar update, followed
by gcd reduction, and dyadic squared comparisons fit \(16S\) bits, where
\[
S=H+J+T_0+V+W+C_0+R+H_P+I_0+m+b+1.
\]
For \(t=m+1\), \(b_1=b+1\), the respective estimates are
\[
H\le2t^2b_1,\ J\le5t^2b_1,\ T_0\le6t^3b_1,\ V\le12t^3b_1,\
W\le25t^3b_1,\ C_0\le13t^3b_1,\ R\le38t^3b_1,\
H_P\le40t^3b_1,\ I_0\le81t^4b_1.
\]
Summing gives \(S\le150t^4b_1\), hence
\(16S\le2400t^4b_1<\mathcal B\).
There are polynomially many scalar operations. With schoolbook arithmetic
and gcd reduction, \(O(m^4\mathcal B^3)\) bit operations and
\(O(m^2\mathcal B)\) coefficient-storage bits suffice.

The executable records observed component, named-norm and final-scale
heights during generator extraction. It does not instrument every internal
`Fraction` temporary; the universal intermediate bound relies on the proof.
Its exact matrix callbacks verify macro identities; I do not claim that
their generic Gaussian elimination is the proposed online implementation
or that its temporary allocation follows the coefficient-vector storage bound.

## 5. Actual caller and proof boundary

The retained full Toeplitz recursion gives shear Stein rank \(O(\log N)\).
This replacement emits exactly that rank, with generator norms at most
twice the source's orthonormal bounds. Its adaptive \(\Gamma\) admits
the same near-identity triangular child. Therefore it preserves the
source's \(O(\log^3 N)\) shear depth and \(O(\log^4 N)\) full depth,
conditional on the retained child constructions.

For the full recursion, leading-section inverse bounds control contiguous
Schur quotients. The parity recursion inside \(P\) can use noncontiguous
principal sets; it needs its own \(\|P-I\|_{1,\infty}\le1/2\) argument.
I do not substitute leading-section conditioning for that near-identity
hypothesis.

At PR4100 `GAUSSIAN.md:102–117`, rational reference Schur matrices provide
the inputs, while bounded coefficients and prefix norms determine later
data precision. This package makes the generator stage exact over
\(\mathbb Q(i)\) and removes a fixed numerical rank threshold from that
stage. FFT roots, approximate child gates, rounding across the complete
circuit, physical coefficient delivery and the outer theorem remain
separate obligations.

## 6. Source-bound finite evidence

I authenticate the original Python sources before parsing or executing them.
I execute `check_exact_algebra.py`'s Schur walk with one collection call
after its \(K,L,S\) calculation; I preserve its rank/displacement assertions
under optimized verifier execution.

From `lowdisp_shear` I extract the seven statements beginning with
`p = h / gamma`, preserving their child-call order and
`source[::-1]` convention. I replace SVD and scale selection by the
rational producer, and replace numerical children by exact matrix callbacks.
I check both generator identities, exact rank, bounded norms/heights,
the complete macro endpoint, inverse-prefix identities and a norm envelope.
I retain the macro AST hash in the receipt.

A \(2^{-200}\) pivot lies below the source replay's fixed SVD threshold,
but is nonzero in the new producer. Omitting it changes the exact endpoint.
This is a precision-sensitive control, not a claim that the predecessor
violated its stated floating tolerance. Other controls reverse the complex
row convention, omit compensation or source restoration, and reject zero
normalization and floating input.

I credit Vlado Vojdanovski/PR1673 for the Schur producer, bounded-generator
compiler and original preprocessing proof, and Cinna Davis for the later
Gaussian caller. The earlier core review already discusses offline versus
online precision. I retain classical Gram–Schmidt and structured-matrix
attribution, and claim no worldwide novelty for dyadic normalization.
