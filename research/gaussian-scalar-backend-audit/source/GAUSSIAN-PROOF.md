# Normalized Gaussian coefficients through the full logical circuit

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
Apache-2.0.

## 1. Domain and source boundary

For \(N=2^d\), rational \(c>0\), and rational \(|s|\le1/2\), write
\[
 k(u)=e^{-\pi c(u^2-2su)},\qquad T_{ij}=k(j-i),\quad0\le i,j<N.
\tag{1}
\]
I construct one dyadic offset table, a rational Toeplitz approximation
\(\widetilde T\), and the retained full logical circuit and its stored
inverse. For input norm at most \(R\ge1\), incoming grid \(F_0\ge0\) and
integer target \(t\ge1\), I prove error below \(2^{-t}\) against \(T\)
and \(T^{-1}\), respectively.

I extract the unchanged `Tsec` function from the retained
`capped-fusion-t74-k554/outer/check_gaugefree.py`, plus its adjacent calls:

```python
A = Tsec(n, g, s).astype(complex)
plan = M.full_plan(list(range(n)), A)
```

I substitute exact rational array operations and the symbolic scalar
\(g=\pi c\). Thus the source expression
`-g*(u-s)**2+g*s*s` cancels exactly before interval evaluation.
I preserve `u=j-i` and treat `.astype(complex)` as an exact type tag.
I substitute the certified exponential table for `np.exp` and the
completed `Full` factory for `M.full_plan`. I omit the surrounding
floating diagnostic loops. I bind the produced matrix and parameters
to the same offset receipts before invoking the compiler.

The scalar \(\alpha^{-1}\), broad diagonal gauges, narrow chirp similarity,
periodic assembly, and physical coefficient delivery require separate
budgets. I retain the distinction between this normalized logical call
and the complete Gaussian/multiplication construction.

## 2. Leading-section conditioning, including half shifts

I rederive the needed finite-cap estimate from Vlado's retained
`HOLES-AND-Q-LDU.md`, also used in our
[PR4193](https://github.com/CrocSwap/integer-mult-bounds/pull/4193).
Put \(\gamma=\pi c\), \(q=e^{-\gamma}\), \(z=q^2\), and
\[
 P_j=\prod_{r=1}^j(1-z^r),\quad P_0=1,\qquad
 {i\brack j}_z=P_i/(P_jP_{i-j}).
\]
For \(G_{ij}=q^{(i-j)^2}\), the retained finite identities give
\[
 G=L\operatorname{diag}(P_j)L^T,\quad
 L_{ij}=q^{(i-j)^2}{i\brack j}_z,\quad
 (L^{-1})_{ij}=(-q)^{i-j}{i\brack j}_z\quad(i\ge j).
\tag{2}
\]
For completeness, write \(G_{ij}=q^{i^2}(z^{-i})^jq^{j^2}\).
The Vandermonde determinant gives the leading minor
\(\Delta_n=\prod_{j=0}^{n-1}P_j\). Dividing the minor with rows
\(0,\ldots,j-1,i\) and columns \(0,\ldots,j\) by \(\Delta_{j+1}\) gives
\[
 q^{i^2-j^2}\prod_{r=0}^{j-1}
 \frac{z^{-i}-z^{-r}}{z^{-j}-z^{-r}}
 =q^{(i-j)^2}{i\brack j}_z.
\]
This proves the lower factor and pivots in (2); symmetry gives the upper
factor. To verify the inverse, use the finite identity
\[
 \sum_{r=0}^m(-x)^rz^{r(r-1)/2}{m\brack r}_z
 =\prod_{r=0}^{m-1}(1-xz^r).
\]
One proves it by induction using the Gaussian-binomial recurrence.
At \(x=1\), it equals zero for \(m>0\) and one for \(m=0\).
Substitution into \(L^{-1}L\) proves (2).

Let \(D_s[i,i]=q^{2si}\). Equation (1) gives \(T_n(s)=D_sGD_s^{-1}\).
At \(s=1/2\), each shifted lower-inverse column has absolute sum at most
\[
 \sum_{r=0}^{n-1}z^r/P_r=1/P_{n-1},
\]
since \(z^r/P_r=P_r^{-1}-P_{r-1}^{-1}\) for \(r\ge1\).
Each shifted upper-inverse entry is at most \(P_{n-1}^{-1}\);
each inverse pivot has the same bound. I multiply the three factors
to obtain \(|T_n(1/2)^{-1}_{ij}|\le P_{n-1}^{-3}\).
Transpose gives the negative endpoint. Using the appropriate endpoint
on each side of the diagonal then gives
\[
 |G^{-1}_{ij}|\le q^{|i-j|}P_{n-1}^{-3},\qquad
 |T_n(s)^{-1}_{ij}|
 \le q^{|i-j|+2s(i-j)}P_{n-1}^{-3}\le P_{n-1}^{-3}.
\tag{3}
\]
I expand the logarithm of the finite product and sum nonnegative terms:
\[
 -\log P_{n-1}
 \le\sum_{h\ge1}\frac1{h(e^{2\gamma h}-1)}
 \le\frac1{2\gamma}\sum_{h\ge1}h^{-2}
 =\frac{\pi^2}{12\gamma}.
\]
Consequently, for every leading size \(1\le n\le N\),
\[
 \|T_n^{-1}\|_1,\ \|T_n^{-1}\|_\infty
 \le nP_{n-1}^{-3}\le N e^{\pi/(4c)}=:Q_{\rm cap}.
\tag{4}
\]
I also have \(0<k(u)\le1\), because
\(u^2-2su\ge0\) for integer \(u\). Thus \(\|T_n\|_{1,\infty}\le N\).

## 3. Requested-precision interval evaluation

I use Mason Hale's retained `pi_interval`, `exp_negative` and
`inward_quantize` without changing their source. For rational \(f\ge0\),
integer \(J\ge16\) and \(h=2^{-J}\), those routines enclose
\(e^{-\pi f}\). I now bound their final enclosure width:
\[
 \operatorname{width}(E)\le512J^2h.
\tag{5}
\]
The Machin routine stops each arctangent series within
\(\lceil(J+16)/4\rceil\) terms. After outward rounding,
\(3\le\pi_L\le\pi_U\le4\) and \(W_\pi<3h\).
Rational coercion and multiplication give
\(W_X\le(3f+6)h\) and \(X_L\ge3f-4h\).

If \(X_L\ge J\), the source returns \([0,h]\); \(e>2\) proves enclosure.
Otherwise \(f<(J+1)/3\), \(W_X\le2Jh\), and \(X_U\le2J\).
The smallest range-reduction divisor \(a=2^k\) satisfies \(a\le32J\).
Because \(1/8\) lies on the working grid, the rounded interval
\(Y=X/a\) has \(0\le Y_L\le Y_U\le1/8\) and \(W_Y\le W_X/a+2h\).

The positive Taylor loop stops by \(\lceil J/3\rceil\) terms.
Its term upper endpoints are at most one. Their widths satisfy
\(d_n\le d_{n-1}/8+W_Y+4h\), hence \(d_n\le2W_Y+5h\).
Interval addition is exact; the source adds one grid unit for the tail.
Thus \(W_{\rm sum}\le J(2W_Y+5h)+h\).
The sum has lower endpoint at least one. After reciprocal enclosure,
the width is at most \(W_{\rm sum}+2h\), with endpoints in \([0,1]\).
Each subsequent squaring multiplies the width by at most two and adds
at most \(2h\). Therefore
\[
 W_E\le2JW_X+a(9J+5)h
 \le(292J^2+160J)h\le512J^2h,
\]
which proves (5). For unrestricted \(f\), I retain the \(f\)-dependence
of the intermediate \(X\) width before the shortcut.

For a requested coefficient error \(2^{-b}\), use
\[
 p=b+1,\qquad J=2p+32.
\tag{6}
\]
Equation (5) is at most \(2^{-p}\): check the inequality at \(p=1\),
then note that the ratio decreases as \(p\) increases.
Inward quantization on the \(p\)-grid adds at most \(2^{-p}\).
The returned exact rational receipt therefore bounds the coefficient
error by \(2^{-b}\). I store an exact one whenever \(f=0\).

To compute a rational conditioning allowance, let
\[
 a_Q=\lceil2/c\rceil,\quad J_Q=2a_Q+36,\quad
 [L,U]\ni e^{-\pi/(4c)},\quad \overline Q=N/L.
\tag{7}
\]
From \(\pi<4\) and \(e<4\), \(e^{-\pi/(4c)}>2^{-a_Q}\).
Equation (5) at \(J_Q\) gives width at most \(2^{-(a_Q+2)}\).
It follows that \(L>0\), \(L\ge(3/4)e^{-\pi/(4c)}\), and
\[
 Q_{\rm cap}\le\overline Q\le(4/3)Q_{\rm cap}.
\tag{8}
\]
The working precision \(J_Q=O(1+1/c)\) tracks the size of
\(\log Q_{\rm cap}\). I check positivity and the width bound before
using the reciprocal.

## 4. Truncation and the same rounded root

For integer \(W\ge0\), both signs satisfy
\(k(\pm n)\le e^{-\pi c n(n-1)}\). The ratio of successive terms for
\(n\ge W+1\) is at most \(e^{-2\pi c(W+1)}\). Hence
\[
 \sum_{|u|>W}k(u)
 \le\frac{2e^{-\pi cW(W+1)}}{1-e^{-2\pi c(W+1)}}.
\tag{9}
\]
I use outward upper endpoints in the numerator and ratio, and require
a positive lower denominator. For \(W=N-1\), the finite matrix has
no omitted offsets and I set its tail allowance to zero.

Choose
\[
 h_0=t+\left\lceil\log_2(8(R+1)\overline Q^2)\right\rceil,\quad
 \varepsilon=2^{-h_0},\quad
 b=h_0+\left\lceil\log_2(4(2N-1))\right\rceil.
\tag{10}
\]
I choose the first \(0\le W<N\) whose certified tail is at most
\(\varepsilon/2\), unless the caller supplies an explicit cutoff.
I reject an explicit cutoff that fails this test. The automatic search
terminates at \(N-1\).

I generate each retained offset once using (6), and reuse its value.
The sum of retained coefficient receipts is at most \(\varepsilon/4\).
Together with (9), this proves, for every leading section,
\[
 \|\widetilde T_n-T_n\|_1,\ 
 \|\widetilde T_n-T_n\|_\infty\le\varepsilon.
\tag{11}
\]
I check the actual receipts against \(\varepsilon/2\), retaining slack.
Before compiling, I compare the complete root to this table and check
the same immutable parameter tuple. A changed matrix cannot borrow
the old coefficient certificate.

Equations (4), (8), (10) give \(\varepsilon\overline Q\le1/2\).
The Neumann series, applied in both induced norms, proves
\[
 \|\widetilde T_n^{-1}\|_{1,\infty}\le2\overline Q,\qquad
 \|\widetilde T^{-1}-T^{-1}\|_2\le2\overline Q^2\varepsilon.
\tag{12}
\]
I use \(\|A\|_2\le\sqrt{\|A\|_1\|A\|_\infty}\) for the last step.
The inward coefficients lie in \([0,1]\), so
\(\|\widetilde T_n\|_{1,\infty}\le N\).
These real component bounds satisfy the stronger executable admission
in `FULL-PROOF.md` without a dimension-conversion loss.

## 5. Complete logical error and precision

I invoke `Full` on this exact \(\widetilde T\), with
\(\lambda_c=N\), \(Q_c=2\overline Q\), radius \(R\), incoming grid \(F_0\),
and circuit target \(t+1\). I use the actual circuit budget \(E_{\rm cir}\)
and actual kernel receipt \(E_{\rm ker}\le\varepsilon\). For independent
forward and inverse inputs of norm at most \(R\),
\[
 \begin{split}
 \|\operatorname{fl}(\mathcal Cx)-Tx\|_2
 &\le E_{\rm cir}+R E_{\rm ker}<2^{-t},\\
 \|\operatorname{fl}(\mathcal C^{-1}x)-T^{-1}x\|_2
 &\le E_{\rm cir}+2\overline Q^2R E_{\rm ker}<2^{-t}.
 \end{split}
\tag{13}
\]
Here \(E_{\rm cir}\le2^{-t-1}\). I invert the stored gates and reverse
their order. I charge rounding in each direction separately.

From (8) and the full-circuit theorem, the online word bound is
\[
 O(F_0+t+\log N+\log R+1/c).
\tag{14}
\]
The inherited depth is \(O(\log^4N)\), with \(O(N\log^4N)\) logical gates.
Coefficient generation uses finite integer/rational operations and the
termination bounds above. The interval argument sizes also depend on
the rational parameter descriptors. Dense root construction, exact Schur
preparation and checker inverses remain offline work; I make no fast
setup or physical tape-cost claim.

In the broad parameterization \(c=1/(\alpha^2\rho)\) with
\(\alpha^2\rho=O(\log p)\), (14) contributes \(O(\log p)\) through
conditioning. A complete raw Gaussian caller must still pay its
diagonal/scalar factors and comparison with the common rounded reference.

## 6. Evidence and attribution

I execute the unchanged function and two callsite statements, then the
completed full logical program. I compare against separately formed
scalar exponent tables at finer precision, using the same declared
Mason interval backend, and exact dense inverse elimination.
I charge the finer reference's residual error when checking (13).
I also compute exact leading-section inverses as finite admission checks.
These checks supplement the written all-size argument.

I include both half shifts, an interior negative shift, a near-half shift,
paid nonzero truncation, a 512-bit incoming vector, scalar execution and
two requested output precisions. Controls cover source orientation,
normalization, stale roots, missing pi, insufficient coefficient precision
and discarded incoming grids. I preserve the four prior complete receipts
and run the Gaussian check sequentially after the full check in the two
existing manifest slots.

I credit Mason Hale/PR2313 for the interval routines and existing dense
Gaussian/integer execution; Jeremy Kothe/IdeaOuter for the shifted source;
Vlado Vojdanovski/PR1673 for q-LDU and the recursive circuit;
Chafik Boukhalfa/PR628 for phases; Cinna Davis for the later caller;
and the classical Vandermonde, q-binomial and Neumann-series arguments.
Internal agents belong to our authoring process. Reviewers must assess
the universal proof independently of the finite receipts.
