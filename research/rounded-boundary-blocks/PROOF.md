# Explicit rounded block residual at the narrow Gaussian boundary

I instantiate the rounding handoff in the retained
`radical_reduction_ultra/README.md`, section3, for PR4100's
\(\delta\ge1/(16p^2)\) narrow-reference gap. I use its exact two-product
block order and seven-product multiplication. I retain the earlier
diagonal-dominance, generic Strassen and qualitative residual arguments;
my contribution supplies explicit page-error, absorption and temporary
constants at this caller.

## 1. Reference and geometry

Let \(p\ge1\) be an integer. Use one exact rational narrow reference
\(H=I-E\), with \(\|E\|_\infty\le1-\delta\) and
\(\delta\ge1/(16p^2)\). First take a finite principal section in its
ordinary linear order. Eliminate separated contiguous cell interiors
and let \(F\) denote the remaining boundary Schur matrix.

For an original half-bandwidth \(W<p\), an eliminated interval couples
only its at-most-W retained neighbors on each side. Their compressed
rank separation is at most \(2W-1\). Original couplings cannot gain
rank separation after compression. Thus the boundary half-bandwidth
is \(b\le2W-1<2p\). Retain the separation that makes the eliminated
interiors independent. Arbitrary removal sets or unhandled cyclic
corner couplings do not establish this ordinary-band interface.

Choose a power-of-two block width \(w\) with
\(\max(1,b)\le w\le4p\), and consecutive blocks. Every triangular
factor of scalar bandwidth b is block bidiagonal in this order.
Reverse both rows and columns to apply the lower solver to an upper
factor; reverse RHS and answer rows as well.

## 2. Exact factor bounds, with predecessor credit

The retained Schur audit proves preservation of the row gap and row
sum. For completeness, eliminating pivot k in row i gives
\[
 \operatorname{gap}'_i\ge\operatorname{gap}_i+
 |a_{ik}/a_{kk}|\operatorname{gap}_k,\qquad
 \operatorname{sum}'_i\le\operatorname{sum}_i-
 |a_{ik}/a_{kk}|\operatorname{gap}_k.
\]
These follow from the triangle and reverse-triangle inequalities;
no sign condition on the off-diagonal entries is needed.
Consequently F has row gap at least \(\delta\), row norm at most2,
and pivots of modulus at least \(\delta\). At a largest component
of x, \(\|Fx\|_\infty\ge\delta\|x\|_\infty\), so
\(\|F^{-1}\|_\infty\le\delta^{-1}\).

Use exact natural-order scalar LU, \(F=LU\), with unit diagonal in L.
Elimination preserves the scalar lower/upper bands. Each row of U
has norm at most2. Each row of L has at most b off-diagonal
multipliers, each of modulus at most \(2/\delta\). Thus
\[
 \|L\|_\infty\le1+2b/\delta\le65p^3,\qquad
 \|U\|_\infty\le2.
\]
From \(L^{-1}=UF^{-1}\), \(U^{-1}=F^{-1}L\),
\[
 Q_L:=32p^2\ge\|L^{-1}\|_\infty,\qquad
 Q_U:=1040p^5\ge\|U^{-1}\|_\infty .
\]
I use these conservative bounds instead of transferring the older
physical solver's \(1/(16p)\) constants unchanged.

For a consecutive triangular diagonal block A, \(A^{-1}\) equals
the corresponding principal block of the full triangular inverse.
Therefore \(\|A^{-1}\|_\infty\le Q_L\) or \(Q_U\). An arbitrary
nonconsecutive subset need not satisfy that block identity.
Padding the last block by identity and the RHS by zero preserves
these bounds after replacing any inverse bound by its maximum with1.

## 3. Fix the rounding order and coefficient pages

Analyze with unbounded rational/integer carriers first. Let
\(\eta=2^{1-P}\). Componentwise signed truncation to the P-grid has
complex \(\ell_1\) error at most \(\eta\). The implementation applies
the same real factor pages to real and imaginary RHS components.
The reference and coefficient pages here are real. Use their induced
absolute-row-sum norm. For complex RHSs use the maximum complex
\(\ell_1\) entry norm over rows and columns. The same row-sum operator
bound applies to that vector norm.

For a block row with exact diagonal A and subdiagonal B, generate
\[
 \widehat B=B+\Delta B,\qquad
 \widehat D=A^{-1}+\Delta D,\qquad
 \|\Delta B\|_\infty,\|\Delta D\|_\infty\le w\eta.
\]
Compute inverse pages from the **exact reference blocks**, then round
the resulting inverses. Inverting a rounded A requires another bound.
Exact reference LU and inverse generation are setup operations.

Execute the actual two-product order
\[
 v=\operatorname{rnd}_P(y-\widehat Bx_{\rm prev}),\qquad
 x=\operatorname{rnd}_P(\widehat Dv).                 \tag{1}
\]
Keep additions and multiplications inside each Strassen product exact.
The first row has no preceding block. Last row/RHS blocks use only
temporary zero/identity padding, as in the retained program.

## 4. Uniform residual and absorption

Write the two rounding errors in (1) as e and f, each bounded by
\(\eta\). The exact residual against the original block row is
\[
 r=Ax+Bx_{\rm prev}-y
   =A\Delta Dv-\Delta Bx_{\rm prev}+e+Af.              \tag{2}
\]
Let \(a\ge\|A\|_\infty\), \(b_0\ge\|B\|_\infty\),
\(Q\ge\|T^{-1}\|_\infty\), \(Y=\max(1,\|y\|_{\max})\), and
\(X=\|\widehat x\|_{\max}\) over the entire finite solve.
If \(w\eta\le1\), define
\[
 c_0=aw+2a+1,\qquad c_1=w[a(b_0+1)+1].
\]
Equation(2), together with
\(\|v\|_\infty\le Y+(b_0+w\eta)X+\eta\), gives
\[
 \|T\widehat x-y\|_{\max}\le\eta(c_0Y+c_1X).          \tag{3}
\]
Each block row has this same bound. No sum over the number of blocks
appears in the maximum residual.

If
\[
 \eta c_0\le1,\qquad Q\eta c_1\le\tfrac12,
\]
then \(X\le Q(Y+\eta c_0Y+\eta c_1X)\), hence
\[
 X\le4QY,\qquad
 \|\widehat x-T^{-1}y\|_{\max}
 \le Q\eta(c_0+4Qc_1)Y.                             \tag{4}
\]
I derive X from the completed residual; I do not assume beforehand
that rounded states satisfy exact-state bounds. The rounded recurrence
terminates on unbounded carriers, so this absorption also bounds each
stored block before I choose its finite word width.

## 5. Substitute the fine-prime constants

For L use \(a,b_0\le65p^3,\ Q\le32p^2,\ w\le4p\). For U use
\(a,b_0\le2,\ Q\le1040p^5<2^{11}p^5\). Then

| Pass | \(c_0\) allowance | \(c_1\) allowance | \(Q(c_0+4Qc_1)\) allowance |
|---|---:|---:|---:|
| L | \(2^9p^4\) | \(2^{15}p^7\) | \(2^{28}p^{11}\) |
| U | \(2^4p\) | \(2^5p\) | \(2^{30}p^{11}\) |

The common sufficient guard
\[
 \eta\le2^{-21}p^{-9}                               \tag{5}
\]
implies \(w\eta\le1\) and both absorption inequalities for both passes.
For initial \(Y_0=\max(1,\|\mathrm{RHS}\|_{\max})\), the forward
result has magnitude at most \(2^7p^2Y_0\). Propagating its error
through exact \(U^{-1}\) and adding the second-pass error gives
\[
 \boxed{\|\widehat x-F^{-1}\mathrm{RHS}\|_{\max}
       <2^{40}p^{16}\eta Y_0},\qquad
 \boxed{\|\widehat x\|_{\max}\le2^{20}p^7Y_0}.         \tag{6}
\]
Indeed the two error contributions are at most
\(2^{39}p^{16}\eta Y_0\) and \(2^{37}p^{13}\eta Y_0\).

For target \(2^{-q}\), \(q\ge0\), it suffices to take
\[
 P=q+41+16\lceil\log_2p\rceil+\lceil\log_2Y_0\rceil.
\]
This also implies (5). If the older prescribed \(P=32768p\) is used
and \(Y_0\le2^p\), (6) is below \(2^{-32710p}\) for integer \(p\ge1\).
This is an arithmetic guarantee for the stated reference/factor
contract, not a proof that every Gaussian caller satisfies it.

## 6. Exact Strassen scratch and signed words

At recursion depth d, each operand entry is a sum/difference of at
most \(2^d\) root entries. For \(w=2^\ell\), leaf operands are bounded
by w times their root entry bounds. A leaf product has at most
\(w^2\) times the root product bound. At each return the retained
seven-product schedule combines at most four child products, so a
conservative bound for any product temporary is \(w^4\) times the
two root entry bounds.

From (4), \(Q\ge1\), \(w\eta\le1\),
\[
 \|v\|_{\max}\le6Q(b_0+1)Y,\qquad
 \|\widehat D\|_\infty\le Q+1\le2Q.
\]
Therefore \(128w^4Q^2(b_0+1)Y\) covers the exact products, component
sums and RHS scratch in a pass. The two-pass substitutions above give
\[
 \text{all arithmetic temporary magnitudes}\le2^{46}p^{16}Y_0 .
\]
Both input operands of an online product lie on the P-grid. All its
internal additions preserve that grid; products and their recombination
lie on the \(2P\)-grid. A signed component width
\[
 2P+\left\lceil\log_2(2^{46}p^{16}Y_0)\right\rceil+2
\]
therefore covers the largest temporary numerator. This is O(p) when
\(P=O(p)\) and \(\log Y_0=O(p)\). I do not round within the Strassen
recursion or leave an uncharged error term there.

## 7. Batching and the following dense stage

For n rows and R RHS columns, one triangular pass makes
\((2\lceil n/w\rceil-1)\lceil R/w\rceil\) matrix products.
Each product uses \(7^{\log_2w}\) scalar products. The complete
allowance is
\[
 O(\lceil n/w\rceil\lceil R/w\rceil w^{\log_2 7}).
\]
The simplified \(O(nR w^{\log_2 7-2})\) tariff requires \(n,R\ge w\);
retain the ceiling expression for edge-only cases.

Round pages once from the exact factors and read them sequentially
for each RHS batch. Retain one previous solved block and the current
block. Depth-first Strassen needs a bounded number of matrices per
level; their sizes decrease geometrically. Fixed work tapes can
serialize the parked arrays and continuation state. Quadrant movement
and rounding scans cost \(O(w^2)\) per product level and fit its
arithmetic allowance. Page generation and the original field
transposition remain separate charged setup/layout operations.
The verifier uses host matrices to check this numerical order; it
does not certify a physical tape refinement.

Equation(6) supplies the previously unspecified rounded boundary-output
envelope. A bounded number of such factors per axis contributes
\(2^{O(g\log p)}\) over g axes. Thus the following dense compiler
can use an explicit logarithmic height contribution of
\(\log_2Y_0+O(g\log p)\), under the same finite-section geometry and
factor hypotheses. Keep the analytic reference error and other dense
stages in the outer error budget.

The broad forward Schur map \(D-CA^{-1}B\) is applied, not inverted.
This proof supplies no inverse bound for that broad map or for
arbitrary broad principal sections.

## Evidence and attribution

I preserve the retained `block_solve`, recursive `mul` and their order.
An authenticated adapter rounds only factor/inverse pages, completed RHS
updates and solved blocks. It preserves source assertions under `-O`
and measures actual leaf multiplications, padding, page count and
temporary dyadic width. Independent ordinary elimination and matrix
products supply reference solutions and residuals.

The finite checks cover fifteen boundary systems, sixty real triangular
passes representing complex RHSs, near-gap blocks, a Schur-complement
case, partial row blocks and partial RHS batches. All fifteen cases
have nonzero rounding error. The checks do not replace the quantified
proof.

I credit the source authors' diagonal-dominance and generic product
arguments, the prior unbatched physical Gaussian solver, and the
classical stability literature. In particular, Brent's
[matrix-multiplication analysis](https://maths-people.anu.edu.au/~brent/pub/pub002.html)
and Higham's [block-LU analysis](https://eprints.maths.manchester.ac.uk/1259/)
precede this caller-specific work. I claim no new general stability
theorem, selected exponent or full multiplication theorem.
