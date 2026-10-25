# Rounded Gaussian factor words on ordinary finite cores

I join the shared references and raw interior circuits of
[RAW-GAUSSIAN-PROOF.md](RAW-GAUSSIAN-PROOF.md) to the retained carve and
boundary program. I prove a maximum-norm error bound for a complete
finite narrow inverse or broad forward word. I use exact rational
preparation and one online data grid.

## Domain and claim

Fix the `Reference` geometry: integers \(S>K>0,\alpha\ge1\),
\(\theta=K/S,\rho=1+\theta,\lambda=\rho^{-1}\), source half-cut \(w\)
and target half-cut \(W_b\). Use its immutable rational narrow or broad
reference. Choose an ordinary half-open target window \([a,b)\)
with complementary length at least \(W\), where
\[
 W\ge2w+2\quad\hbox{(narrow)},\qquad
 W\ge W_b\quad\hbox{(broad)}.
\]
I retain the original period cut, phase labels and hole conventions.
The shortest connection across the omitted complement has distance at
least \(W+1\); consequently no periodic corner survives inside this
window. I also check its ordinary bandwidth against \(W\).
Write \(Q\) for the principal reference matrix on this finite window.

Choose a positive dyadic cap \(B\) with \(2B\le S\), a rational
input bound \(Y_0\ge1\), target \(t\ge1\), and incoming grid \(F_0\ge0\).
For complex data I use
\[
 \|x\|_*=\max_{i,j}(|\Re x_{ij}|+|\Im x_{ij}|).
\]
The column index ranges over the declared RHS columns. Real
absolute-row-sum bounds act on this norm without a dimension factor.

For narrow execution require the same reference's certified gap \(d>0\).
For broad execution require \(E_M Q_{\rm ideal}\le1/2\), with
\(Q_{\rm ideal}\) defined below. For either direction require the
reference accuracy needed by each raw child at the amplified radius
and target below. `Core` rejects an underfunded fixed reference before
preparing its Schur pages. `allocated_reference` supplies a sufficient
allocation before the user chooses a window.

Under these hypotheses I execute the retained six-call word and obtain
\[
 \|\widehat x-Q^{-1}x\|_* \le 2^{-t-1}
 \quad\hbox{(narrow)},\qquad
 \|\widehat x-Qx\|_* \le 2^{-t-1}
 \quad\hbox{(broad)}.                                      \tag{1}
\]
I state these bounds against the finite rational reference. I do not
include a core/halo approximation in (1).

## Carve and exact reference pages

I extract the unchanged `carve` function from the pinned
`check_capped_gauges.py`. I apply it to each clipped run of consecutive
selected coordinates with one original phase. I retain holes as
boundary coordinates. For a run of length \(L\le6W\), the source
chooses only boundary coordinates. Otherwise it keeps the first \(W\),
sets \(R=L-2W\), and while \(R>4W\) chooses an interior length
\[
 \min(B,2^{\lfloor\log_2(R-W)\rfloor}),
\]
followed by \(W\) boundary coordinates. It finishes with its residual
and final boundary strips. I retain this order, including a possible
coalesced terminal boundary group of \(6W\).

Each interior has a positive dyadic length at most \(B\). Consecutive
interiors have more than \(W\) coordinate distance, so I obtain
\[
 Q=\begin{pmatrix}A&B_0\\ C_0&D\end{pmatrix},
 \qquad A=\bigoplus_i A_i .
\]
Here \(B_0,C_0\) are the original reference couplings; the cap \(B\)
has no relation to the coupling symbol \(B_0\). I prepare
\[
 F=D-C_0A^{-1}B_0                                      \tag{2}
\]
from exact reference entries and exact interior inverses.
I never substitute rounded online inverse applications into (2).
An eliminated interval touches at most \(W\) retained neighbors on
each side. Their compressed separation is at most \(2W-1\).
Original couplings cannot increase their separation under deletion.
Thus the compressed boundary half-bandwidth obeys \(b_F\le2W-1\).

The source carve permits \(B\le W\). I require \(B>W\) only for the
extra claim that each chosen interior exceeds \(W\). The finite
fixtures exercise the former domain and record `cap_exceeds_band=false`.

## Exact chronology and factor norms

I extract the source `seq` assignment from `check_union.py`. Its
narrow inverse chronology is
\[
 A^{-1}\text{ on }I;\quad E_{-C_0};\quad
 F^{-1}\text{ on }J;\quad A\text{ on }I;\quad
 E_{-B_0};\quad A^{-1}\text{ on }I.                       \tag{3}
\]
I use the original couplings in the two shears. I reverse the source
labels in (3) and exchange forward/inverse labels to obtain the broad
forward chronology
\[
 A\text{ on }I;\quad E_{B_0};\quad
 A^{-1}\text{ on }I;\quad F\text{ on }J;\quad
 E_{C_0};\quad A\text{ on }I.                            \tag{4}
\]
Direct multiplication with (2) proves both endpoints without assuming
that the broad factors in (4) have inverses. In particular,
I apply the broad \(F\); I require no broad \(F^{-1}\).
The two middle calls act on disjoint banks and form one direct-sum
factor, giving five factors in either word.

For the narrow reference, diagonal one and row gap \(d>0\) give row
norm at most two. During elimination, triangle inequalities give
\[
 \operatorname{gap}'_i\ge\operatorname{gap}_i+
 |a_{ik}/a_{kk}|\operatorname{gap}_k,\qquad
 \operatorname{sum}'_i\le\operatorname{sum}_i-
 |a_{ik}/a_{kk}|\operatorname{gap}_k .
\]
Therefore \(A_i,F\) retain norm at most two and gap at least \(d\).
At a largest component of \(x\), the gap inequality gives
\(\|Fx\|_*\ge d\|x\|_*\), and likewise for \(A_i\).
I may take
\[
 \mathcal K_N=\max(3,d^{-1})
\]
for the five exact factor norms.

For the broad reference, inward coefficient rounding and the Gaussian
lattice-sum bound \(1+\sigma\) give both row and column sums at most
three. This includes the identity on hole columns. To bound the
ideal interior inverse, put \(r=(B-1)/2\), \(v=\lambda\theta/\alpha^2\)
and
\[
 F_g=\max\left\{
 \alpha^2\theta r^2,\
 {1\over4\alpha^2\rho^2}+v(\lambda r^2+r/\rho),\
 v(r^2+2r/\rho)\right\}.
\]
The anchored identities in RAW-GAUSSIAN-PROOF.md and
\(|\delta|\le1/(2\rho)\) bound the absolute exponents of both diagonal
families by \(F_g\). Choose a certified positive
\(q\le e^{-\pi F_g}\), put \(G=\alpha/q\), and use the earlier
cap-wide conditioning certificate
\[
 H=\overline Q(B,\lambda/\alpha^2),\qquad Q_{\rm ideal}=G^2H .
\]
It bounds the actual ideal kernels and their inverses for either
family, including smaller interiors and closed half shifts. It need
not dominate each independently computed certificate's upper endpoint.
Neumann perturbation at \(E_MQ_{\rm ideal}\le1/2\) gives
\(\|A^{-1}\|_\infty\le2Q_{\rm ideal}\). From (2),
\[
 \|F\|_\infty\le3+18Q_{\rm ideal},\qquad
 \mathcal K_M=3+18Q_{\rm ideal}.
\]
Since \(Q_{\rm ideal}\ge1\), this also bounds both shears, \(A\) and
\(A^{-1}\).

## One radius, reference allocation and data grid

Write \(\mathcal K\) for the appropriate factor bound and set
\[
 Y_*=6\mathcal K^5Y_0,\quad
 e={2^{-t}\over10\mathcal K^4},\quad
 R_D=\lceil\sqrt B\rceil Y_*,\quad
 t_D=t+\lceil\log_2(20\mathcal K^4)\rceil.                 \tag{5}
\]
Each interior vector at radius \(Y_*\) has Euclidean norm at most
\(R_D\). The raw contract gives Euclidean error below
\(2^{-t_D}\le e/2\); conversion to maximum complex-l1 error costs at
most \(\sqrt2\), hence remains below \(e\).

For a noncircular reference allocation, I first enclose
\[
 d_0=1-\operatorname{upper}(e^{-2\pi\alpha^2\theta})
       -5\operatorname{upper}(e^{-2\pi\alpha^2})
\]
and require \(d_0>0\). Before preparing a reference, I choose
\(\mathcal K_*=\max(3,2/d_0,4+32Q_{\rm ideal})\) and compute (5)
with this bound. I call `Reference.for_cap` at target at least
\[
 \max(t_D,\lceil\log_2(2/d_0)\rceil,
             \lceil\log_2(2Q_{\rm ideal})\rceil,1).
\]
I check the resulting \(E_N\le d_0/2\), actual certified \(d\ge d_0/2\),
and \(E_MQ_{\rm ideal}\le1/2\). The reference allocator's conservative
cap-wide gauge also dominates the raw children's requirements.
Thus \(\mathcal K_*\) funds both later directions without selecting
the window or computing its Schur complement. I reject periods too
short for the allocated cuts, as in the earlier reference contract.

For a fixed reference, `Core` constructs each raw probe at \((R_D,t_D)\)
and rejects inadequate reference precision. It then sets one grid
\(P\) to the maximum of \(F_0\), the raw children's grids and the
sparse/boundary requirements below. Reinstantiation at incoming grid
\(P\) preserves that same \(P\), because the child allocations use a
maximum with their incoming precision.

## Prepared boundary execution

For narrow \(F\), choose the auxiliary integer
\[
 p=\max(W+1,\lceil\sqrt{1/(16d)}\rceil).
\]
This \(p\) is an envelope parameter for the boundary theorem, not an
assertion about the source construction's original precision parameter.
Then \(d\ge1/(16p^2)\) and \(b_F<2p\). Choose a dyadic block width
\(\max(1,b_F)\le w_B\le4p\).

I prepare exact ordinary banded \(F=LU\). Gap and row-norm preservation
give positive pivots at least \(d\), \(\|U\|_\infty\le2\), and
\[
 \|L\|_\infty\le1+2b_F/d\le65p^3,\quad
 \|L^{-1}\|_\infty\le32p^2,\quad
 \|U^{-1}\|_\infty\le1040p^5.                            \tag{6}
\]
The last two follow from \(L^{-1}=UF^{-1}\) and \(U^{-1}=F^{-1}L\).
Consecutive triangular inverse pages equal principal blocks of the
full triangular inverse. I pad the final page by identity.

I retain PR4186's rounding adapter and the underlying block/Strassen
program byte for byte. I prepare rounded factor pages and rounded
inverses of the **exact** consecutive diagonal blocks. During execution
I replace the source inverse callback with a sequential reader of
these prepared inverse pages. I check the next rounded diagonal page
against its expected value. The callback performs no inverse.
The retained adapter's rounding of an already dyadic subdiagonal page
preserves its value; its multiplication, addition and output-rounding
sites remain unchanged. This proves value equivalence with the retained
rounding adapter evaluated on exact reference factors. In the finite
comparison I cache exact inverse evaluations for that baseline.
I replace only its diagnostic matrix digest with binary rational hashing.

I restate the needed residual argument to avoid an unchecked dependency
on the sibling PR's proof. Let \(\eta=2^{1-P}\). For exact diagonal
block \(A_0\) and subdiagonal \(B_1\), the prepared pages obey
\(\|\Delta D\|,\|\Delta B\|\le w_B\eta\). The source executes
\[
 v=\operatorname{rnd}_P(y-\widehat B_1x_{\rm prev}),\qquad
 x=\operatorname{rnd}_P(\widehat Dv).
\]
With rounding errors \(u,f\), the exact residual is
\[
 A_0x+B_1x_{\rm prev}-y
   =A_0\Delta Dv-\Delta Bx_{\rm prev}+u+A_0f.              \tag{7}
\]
For \(a\ge\|A_0\|,\ b_0\ge\|B_1\|,\ Q_T\ge\|T^{-1}\|\), define
\[
 c_0=aw_B+2a+1,\qquad c_1=w_B[a(b_0+1)+1].
\]
If \(w_B\eta\le1,\eta c_0\le1,Q_T\eta c_1\le1/2\), (7) gives
\[
 X\le4Q_TY,\qquad
 \|\widehat x-T^{-1}y\|_*
 \le Q_T\eta(c_0+4Q_Tc_1)Y .                            \tag{8}
\]
I derive \(X\) by absorption from the completed residual, rather than
assuming the exact-state bound for rounded data.

Substitution of (6) gives per-pass error constants at most
\(2^{28}p^{11}\) for \(L\) and \(2^{30}p^{11}\) for \(U\).
The guard \(\eta\le2^{-21}p^{-9}\) suffices for both absorptions.
The first output has magnitude at most \(2^7p^2Y_*\).
After reversing both axes for the upper pass and restoring row order,
I obtain
\[
 \|\widehat x-F^{-1}y\|_*<2^{40}p^{16}\eta Y_* .           \tag{9}
\]
The two contributions are at most \(2^{39}p^{16}\eta Y_*\) and
\(2^{37}p^{13}\eta Y_*\).
Real/imaginary RHS packing preserves (7)-(9): the pair of component
truncations already costs at most \(\eta\) in complex-l1 norm.

For \(q_e=t+\lceil\log_2(10\mathcal K^4)\rceil\), I require
\[
 P\ge q_e+41+16\lceil\log_2p\rceil+\lceil\log_2Y_*\rceil .
\]
Then (9) is at most \(2^{-q_e}\le e\), and the absorption guards hold.

## Sparse stages, total error and finite storage

For a row with at most \(s\) coefficients, I round the exact real
coefficients once, accumulate products exactly, then truncate both
completed output components. At input radius \(Y_*\), this costs at
most \(\eta(sY_*+1)\). I use \(s=2W+1\) for original coupling rows
and \(s=2b_F+1\) for broad Schur rows. It suffices to require
\[
 P\ge1+\left\lceil\log_2{(sY_*+1)\over e}\right\rceil .
\]
I compute each shear's updated bank from the prior bank values and
commit the completed rows before the next stage.

Let \(E_j\) denote the discrepancy after \(j\) exact factors.
Equations (5), (9) and the sparse bound give
\(E_{j+1}\le\mathcal K E_j+e\).
The two middle calls update disjoint banks, so I use their maximum
error, with no extra summand. Thus
\[
 E_5\le5\mathcal K^4 e=2^{-t-1}.
\]
The corresponding magnitude recurrence keeps each actual factor input
and the intermediate middle state below \(Y_*=6\mathcal K^5Y_0\).
This induction justifies the input envelopes used for the local bounds.
The number of interiors and RHS columns does not enter this maximum norm.

For sparse arithmetic, inward coefficient rounding cannot increase an
absolute row sum. The allowance \(16(\mathcal K+1)Y_*\) covers products,
partial accumulators and completed shears. PR4186's exact Strassen
scratch argument bounds both boundary passes by \(2^{46}p^{16}Y_*\):
at depth \(d\) each operand has at most \(2^d\) root terms, while each
return combines at most four child products. The conservative per-pass
allowance is \(128w_B^4Q_T^2(b_0+1)Y\).
Products use the \(2P\)-grid and additions preserve it.
I take the maximum of these bounds and each raw child's temporary
bound, retaining its rational coefficient-height charge.

For \(n_J\) boundary rows and \(k\) complex RHS columns, each triangular
pass uses
\[
 (2\lceil n_J/w_B\rceil-1)\lceil2k/w_B\rceil
 \quad\hbox{products of size }w_B,\qquad
 7^{\log_2w_B}\quad\hbox{scalar products per product}.
\]
I retain the ceiling tariff for partial row and RHS batches.
I keep exact Schur formation, LU, inverse-page generation and checker
oracles outside the online arithmetic counts. I make no fixed-tape or
complete setup-cost claim from their host-language implementation.

## Evidence, credit and remaining scope

`verify_core.py` checks exact reference residuals after the narrow
boundary stage and complete inverse word; division by the certified gap
converts those residuals to error bounds. For broad execution it compares
the complete result with the exact reference product. It checks each
stage against its actual current input, chronological continuity, input
grids and measured arithmetic widths.

I credit Vlado Vojdanovski's retained carve, factor word, block program,
Strassen implementation and gap-preservation argument. I reuse our
PR4186 residual analysis and the earlier PR4205 raw/normalized circuits,
with the predecessor credits in README.md. I add the shared-reference
core integration, prepared-page lowering and one composed error budget.
Internal analysis agents contributed to the author process.

Reviewers still need to assess this quantified proof. The finite receipt
does not establish arbitrary-size execution. I leave periodic corner
treatment, the core/halo comparison, tensor composition, physical page
delivery and the complete multiplication theorem open. I also make no
claim that the narrow and broad programs form a stored global inverse pair.

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
Apache-2.0.
