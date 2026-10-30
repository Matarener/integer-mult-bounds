# A common Gaussian reference and anchored raw interior circuits

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
Apache-2.0.

## 1. Domain, source geometry and scope

Choose integers \(0<K<S\), \(T=S+K\), \(\theta=K/S\), \(\rho=T/S\),
\(\lambda=1/\rho\), and integer \(\alpha\ge1\). Put \(a=\pi\alpha^2\).
For integer \(j\), define
\[
 c_j=\lfloor\theta j+1/2\rfloor,\quad q_j=j+c_j,\quad
 \beta_j=\theta j-c_j\in[-1/2,1/2).
\tag{1}
\]
Then \(q_{j+S}=q_j+T\), \(\beta_{j+S}=\beta_j\), and each consecutive
target gap is one or two. I retain the original cells of constant \(c_j\)
inside \(0,\ldots,S-1\), including the original period cut.

The retained source definitions in `unconditional-batched-crt/PROOF.md`
and `BILATERAL-LDU.md` give the periodic narrow and broad maps
\[
 N_{ij}^{\rm per}=\sum_{\ell\in\mathbb Z}
 e^{-a[(\rho(j+\ell S)-q_i)^2-\beta_j^2]},
\quad
 M^{\rm per}_{k,q_j}=\alpha^{-1}\sum_{\ell\in\mathbb Z}
 e^{-(\pi/\alpha^2)(j+\ell S-\lambda k)^2}.
\tag{2}
\]
The narrow normalization uses the column's \(\beta_j^2\).
I embed the narrow map on selected target coordinates and add identity
on holes, with zero selected/hole cross entries. For the broad map I
add identity hole columns and retain Gaussian outputs at hole rows.
I retain \(\alpha^{-1}\); the older half-scaled convention belongs to
a different caller.

I construct one rational reference for each map and execute raw
constant-phase block restrictions with a certified reference error.
An admitted block has dyadic size \(n\), \(2n\le S\), lies inside one
original cell and period, and has consecutive selected target coordinates.
The outer caller must also enforce its cap, reserved strips and separator
geometry. I do not implement that carving, boundary arithmetic or physical
delivery in this package.

The later caller uses \(\theta\in[1/(4p^2),1/p^2]\),
\(\alpha=\lceil\sqrt{(4/\pi)\log(16p)}\rceil\) and \(n\le B=p^{\xi+o(1)}\),
\(\xi<1\). The formulas below apply to the broader finite domain (1);
I do not infer primality, the outer parameter checks or a multiplication
theorem from these block computations.

## 2. Positive coefficients at requested relative precision

I use Mason Hale's outward intervals and the width result from
`GAUSSIAN-PROOF.md`: at \(J\ge16\), the returned enclosure of
\(e^{-\pi f}\), \(f\ge0\), has width at most \(512J^2 2^{-J}\).

For \(0\le f\le F\), relative precision \(b\ge1\), set
\[
 L=\lceil8F\rceil,\qquad P=L+b+3,\qquad J=2P+32.
\tag{3}
\]
Since \(\pi<4\) and \(e<4\), \(w=e^{-\pi f}\ge2^{-L}\).
The width bound at \(J\) is at most \(2^{-P}\).
If \(\ell\) is the lower interval endpoint, store
\(\widehat w=2^{-P}\lfloor2^P\ell\rfloor\). I obtain
\[
 0\le w-\widehat w\le2^{1-P},\qquad
 (1-2^{-b-2})w\le\widehat w\le w,\qquad \widehat w>0.
\tag{4}
\]
The stored numerator is at least \(2^{b+2}\). I store the exact reciprocal
when needed; its relative error is at most \(2^{-b-1}\).
Both the value and reciprocal have numerator/denominator heights at most
\(P+1\). I use certified lower approximations rather than assume that
I can determine an irrational exponential's exact downward rounding.

For an absolute error \(2^{-b}\), I use the earlier producer with output
grid \(b+1\) and working grid \(2(b+1)+32\). That producer may return zero
for a sufficiently small kernel entry. I use (3) for weights and gauges
that require a positive reciprocal.

## 3. One fixed rounded reference

Choose source halfwidth \(w\) with \(2w<S\), broad physical halfwidth \(W\)
with \(2W<T\), and entry precision \(b_e\ge8\). The immutable description
\((S,K,\alpha,w,W,b_e)\) determines all entries. I generate coefficients
by global address and reuse them across windows. I compute selected,
phase and beta coordinates on demand. To test whether target coordinate
\(k\) is selected, compute \(j=\lfloor\lambda k+1/2\rfloor\) and check
\(q_j=k\). A selected \(q_j\) satisfies
\(|\lambda q_j-j|\le\lambda/2<1/2\), which proves this lookup.
Construction and block queries do not enumerate the entire axis.
Explicit hole listings and the small-period checker do enumerate their
requested geometry; I make no physical carve-cost claim for those lists.

For the narrow reference, prepare once
\[
 w_j=e^{-a(1/4-\beta_j^2)/\theta},\qquad
 G_h=e^{-a\rho h^2}.
\tag{5}
\]
Use (3) for the weights with \(F=\alpha^2/(4\theta)\), \(b=b_e+4\).
Use absolute error \(2^{-b_G}\) for a symmetric kernel table, where
\[
 L_{\rm ratio}=\lceil8\alpha^2w\rceil,\qquad
 b_G=b_e+L_{\rm ratio}+4.
\tag{6}
\]
Set \(\widehat G_0=1\). For each source pair \(i,j\), retain the unique
lift \(j'=j+\ell S\) with \(|j'-i|\le w\), if one exists:

- Set the diagonal to one, removing its nonzero aliases.
- Without a retained lift, set the entry to zero.
- For \(\ell=0\) and \(c_i=c_j\), use exactly
  \(\widehat w_i\widehat G_{j-i}/\widehat w_j\).
- Across cells or the original period cut, use a certified lower
  approximation to the corresponding term of (2).

I preserve the original cut even when lifted phases agree.
This gives the retained narrow weight-ratio structure.
Within one cell, \(\beta_j-\beta_i=\theta(j-i)\), so
\[
 (w_i/w_j)G_{j-i}
 =e^{-a[(\rho(j-i)+\beta_i)^2-\beta_j^2]}.
\tag{7}
\]
For retained offsets, \(w_i/w_j\le e^{a|j-i|}\le2^{L_{\rm ratio}}\).
The relative weight loss is at most
\(\eta=2^{-b_e-6}\). The ratio changes by at most \(2\eta\) relatively;
the ideal entry in (7) is at most one. Kernel error contributes at most
\(2^{L_{\rm ratio}+1}2^{-b_G}\). Thus the retained entry error is at most
\[
 2\eta+2^{L_{\rm ratio}+1-b_G}
 \le(5/32)2^{-b_e}<2^{-b_e}.
\tag{8}
\]
The cross-cell/cut entries satisfy the same allowance through the
absolute producer.

For the broad reference, retain the unique lift with
\(|q_j+\ell T-k|\le W\), evaluate its exponential in (2), and divide by
the exact rational \(\alpha\). Otherwise set the selected-column entry
to zero. Add identity hole columns. I round broad entries by global
address. This is a fixed entrywise reference; I do not claim equality
with the older audit's factorwise-rounded broad matrix. The later
`GAUSSIAN.md` interface permits a distinct circuit approximation when
the norm comparison with its fixed reference is paid.

The narrow physical circular halfwidth is at most \(W_N=2w+2\);
the broad halfwidth is \(W\). A common physical allowance can take
\(\max(W_N,W)\).

## 4. Global row and column error, including aliases

For narrow offsets \(h\ne0\),
\[
 (\rho h+\beta_i)^2-\beta_{i+h}^2\ge h^2-|h|.
\]
For a fixed row or column, the source indices and windings enumerate
integer offsets without repetition. Therefore both discarded row and
column sums are at most
\[
 E_N^{\rm tail}
 =\frac{2e^{-\pi\alpha^2w(w+1)}}{1-e^{-2\pi\alpha^2(w+1)}}.
\tag{9}
\]
This allowance includes removed diagonal aliases, since \(2w<S\).

For broad \(d=q_j+\ell T-k\),
\[
 j+\ell S-\lambda k=\lambda(d+\beta_j),\qquad
 |d+\beta_j|\ge |d|-1/2.
\]
Distinct selected lifts occupy distinct integer target positions. For a
fixed selected column, rows and windings enumerate integer differences.
Both tails are consequently at most
\[
 E_M^{\rm tail}
 =\frac{2}{\alpha}
 \frac{e^{-\pi(W+1/2)^2/(\alpha^2\rho^2)}}
 {1-e^{-2\pi(W+1)/(\alpha^2\rho^2)}}.
\tag{10}
\]
Identity hole columns contribute no error. Combining (8)–(10), in both
induced norms I obtain
\[
 E_N=E_N^{\rm tail}+(2w+1)2^{-b_e},\qquad
 E_M=E_M^{\rm tail}+(2W+1)2^{-b_e}.
\tag{11}
\]
I evaluate these as rational upper bounds, using upper interval endpoints
for the numerator and geometric ratio.

The chosen working grid is
\(J=2(b_e+\lceil8\alpha^2\rho^2\rceil+16)+32\).
Writing \(A=\alpha^2\rho^2\ge1\), this gives \(J\ge16A+80\ge96\).
The broad denominator's true gap is at least
\(6/(A+6)\ge96/(J+96)\); its enclosure width is at most
\(2^{9-J/2}\), which is smaller for \(J\ge96\).
The narrow ratio has true gap greater than \(1-e^{-6}\).
Thus the outward denominator checks have positive margins on the
entire declared domain.

For a nonwrapping, constant-phase block with \(2n\le S\), the retained
local lift is zero. Equations (8)–(10) also bound omissions from its
unperiodized ideal raw block directly. Hence (11) bounds that block's
reference error. I use this direct argument in the raw circuit theorem;
the periodic global comparison alone would not establish it.

## 5. A conditioning certificate for the same narrow reference

The retained nearest-neighbor argument bounds the total off-diagonal
narrow row mass, including nonzero diagonal aliases in its tail, by
\[
 \rho_0=e^{-2a\theta}+5e^{-2a},\qquad a\ge1.
\tag{12}
\]
For the nearest two terms, use the target gaps in \(\{1,2\}\) and their
phase restrictions to obtain
\(e^{-2a\theta}+e^{-2a(1+\theta)}\).
For \(|h|\ge2\), sum \(e^{-a(h^2-|h|)}\) in both directions to obtain
less than \(4e^{-2a}\). This proves (12) in the present parameter range.

I compute the rational lower bound
\[
 d=1-\overline{e^{-2a\theta}}-5\overline{e^{-2a}}-E_N.
\tag{13}
\]
When \(d>0\), the actual rational narrow reference has diagonal one,
row gap at least \(d\), and row norm at most \(2-d\). Hole identity
coordinates preserve this statement. If (13) is nonpositive, I return
no global conditioning certificate; the reference itself remains defined.

All principal restrictions inherit the gap and the original circular
coordinates. Write such a restriction as \(I-E\).
Then \(\|E\|_\infty\le1-d\), and each column of \(E^k\) can reach at
most \(\min(T,2kW_N+1)\) physical positions. The Neumann series gives
\[
 \|(I-E)^{-1}\|_\infty\le d^{-1},\qquad
 \|(I-E)^{-1}\|_1
 \le d^{-1}+2W_N(1-d)d^{-2}.
\tag{14}
\]
I keep the circular metric in this support argument; an arbitrary
linear reindexing would not preserve the same bandwidth.
Equation (14) concerns the narrow reference. I claim no arbitrary
principal inverse bound for the global broad reference.

## 6. Anchored raw factors

For an admitted interval \(I=[L,L+n)\), let
\(m=L+(n-1)/2\), \(\beta_m=\theta m-c_L\), and \(t_i=i-m\).
The narrow ideal restriction is
\[
 N_I=D T D^{-1},\quad
 D_i=e^{\pi\alpha^2\theta t_i^2},\quad
 c_T=\alpha^2\rho,\quad s_T=-\beta_m/\rho.
\tag{15}
\]
Here \(T_{ij}=e^{-\pi c_T[(j-i)^2-2s_T(j-i)]}\).

For broad selected rows/columns, the target center is \(m+c_L\);
its centered offsets still equal \(t_i\).
Set \(\delta=\beta_m/\rho\), \(v=\lambda\theta/\alpha^2\).
The exact ideal block is \(A T B\), where
\[
 \begin{split}
 c_T&=\lambda/\alpha^2,\quad s_T=-\delta(1-\theta),\\
 A_i&=\alpha^{-1}
 e^{\pi[-\delta^2/\alpha^2+v(\lambda t_i^2+2\delta t_i)]},\\
 B_i&=e^{-\pi v(t_i^2+4\delta t_i)}.
 \end{split}
\tag{16}
\]
Expanding the exponents gives
\(\alpha^{-1}e^{-(\pi/\alpha^2)(j-\lambda q_i)^2}\).
I verify that rational identity before compiling.
The normalized kernel already absorbs its shift normalization;
I add no further \(e^{-\gamma s_T^2}\) scalar.

Both shifts lie in \([-1/2,1/2]\).
Let \(F_g\) bound the absolute rational coefficients multiplying \(\pi\)
in the two diagonals. The exact conservative allowance
\[
 G=\alpha\,2^{\lceil8F_g\rceil}
\tag{17}
\]
bounds \(A,B,A^{-1},B^{-1}\).
Use the normalized theorem's \(\overline Q\) and set
\(H=\max(n,\overline Q)\), \(Q_{\rm raw}=G^2H\).
Thus \(H\) bounds \(T,T^{-1}\), and \(Q_{\rm raw}\) bounds the inverse
of the ideal raw block.

## 7. One stored forward/inverse program and one grid

For target \(\tau=2^{-t}\), radius \(R\ge1\), choose
\[
 \delta_g=\frac{\tau}{24GH(R+1)},\quad
 b_g=\left\lceil\log_2(4G/\delta_g)\right\rceil,\quad
 R_*=2G(R+1),\quad
 t_*=t+\lceil\log_2(16G)\rceil.
\tag{18}
\]
Generate each decay coefficient through (3) at relative precision \(b_g\),
and use its exact reciprocal for growth. Multiply exact rational
prefactors separately. By (4) and (17), both stored diagonal errors
and the errors of their exact reciprocals are at most \(\delta_g\).
For the narrow similarity I store one chirp and its reciprocal.

Compile the normalized circuit at radius \(R_*\), target \(t_*\), and
one data grid
\[
 F\ge F_0,\quad
 F\ge t+\lceil\log_2(24nGH)\rceil,
\tag{19}
\]
also satisfying the child's own required grid. Its incoming-grid
dependence is a maximum, so I can compute (19), declare it as the
child's incoming precision, and retain that same grid throughout.

The complete forward program is
\(\widehat B;\mathcal C;\widehat A\).
For its inverse I invert the stored gates and reverse their order:
\(\widehat A^{-1};\mathcal C^{-1};\widehat B^{-1}\).
Each diagonal layer has rounding norm at most \(r=n2^{-F}\).
The rounded input diagonal fits radius
\((G+\delta_g)R+r\le R_*\).
For either direction, telescoping the three stages gives
\[
 E_{\rm raw}
 \le2G E_{\rm norm}+3GH\delta_g R+3GHr<3\tau/8,
\tag{20}
\]
where \(E_{\rm norm}\le\tau/(16G)\).
This includes the input diagonal's error before the inverse amplifies it.

Let \(E_{\rm ref}\) be the appropriate allowance in (11). Require
\[
 E_{\rm ref}\le
 \frac{\tau}{8(R+1)Q_{\rm raw}^2}.
\tag{21}
\]
Otherwise the raw caller rejects that fixed reference. Equations (11),
(16), and the Neumann resolvent identity give
\(\|M_{\rm ref}^{-1}\|\le2Q_{\rm raw}\) and inverse comparison error
at most \(2Q_{\rm raw}^2E_{\rm ref}\).
Thus the complete forward/inverse errors against the same rational
reference restriction are bounded by
\[
 E_{\rm raw}+R E_{\rm ref}<\tau,\qquad
 E_{\rm raw}+2R Q_{\rm raw}^2E_{\rm ref}<\tau.
\tag{22}
\]
I check the reference description and exact restriction again before
execution. A changed page cannot reuse the earlier preparation snapshot.

### Uniform construction for a requested cap and accuracy

I also supply `Reference.for_cap`, which chooses one reference before
any block requests. Given a dyadic cap \(B\), \(2B\le S\), radius \(R\)
and target \(t\), set
\[
 F_*=1+\alpha^2\theta(B^2+B+1),\quad
 G_*=\alpha2^{\lceil8F_*\rceil},\quad
 H_*=2\overline Q(B,1/(\alpha^2\rho)),\quad Q_*=G_*^2H_*.
\]
Equations (15)–(16), \(|t_i|\le B/2\) and \(|\beta_m|\le1/2\) show
that \(F_*\) bounds both raw exponent ranges. The factor-two margin
in \(H_*\) covers the normalized allowance for either family and any
\(n\le B\): each local allowance is at most \(4/3\) of its exact
finite-cap upper bound. Thus \(G_*,H_*,Q_*\) dominate the local budgets.

Let
\[
 e=t+\left\lceil\log_2(8(R+1)Q_*^2)\right\rceil,\qquad
 A=\alpha^2\rho^2.
\]
Choose integers
\[
 w=\left\lceil\sqrt{(e+5)/(3\alpha^2)}\right\rceil,\qquad
 W=\max\{\lceil A\rceil,\lceil\sqrt{A(e+5)/3}\rceil,2w+2\},
\]
and \(b_e=e+3+\lceil\log_2(2\max(w,W)+1)\rceil\).
I compute the square-root ceilings through integer arithmetic.
If \(2w\ge S\) or \(2W\ge T\), I reject the period/cap/accuracy request.

For legal cuts, both geometric ratios are below \(\exp(-6)<1/64\).
The true tail numerators are at most \(2^{-e-5}\), since \(\pi>3\)
and \(\exp(1)>2\). The working-grid width is at most
\(2^{-b_e-23}\). Therefore each rational tail allowance is less than
\(2^{-e}/4\); each coefficient row/column allowance is at most
\(2^{-e}/8\). Consequently both errors in (11) are below \(2^{-e}\),
which satisfies (21) for all admitted blocks of size at most \(B\)
and radius at most \(R\). I check the actual rational inequalities
before returning the reference.

The chosen broad width is
\(O(\alpha^2\rho^2+\alpha\rho\sqrt e+w)\).
In the later caller's regime, \(t+\log R=O(p)\), \(\alpha^2=O(\log p)\)
and \(\theta B^2\log p=o(1)\), so \(e=O(p)\),
\(w=O(\sqrt{p/\log p})\) and
\(W=O(\sqrt{p\log p}+\log p)\).
These widths fit the retained bandwidth order. The original axis
lengths must still pass the explicit period checks.

## 8. Setup, online widths and remaining work

Full-cell weights use
\[
 P_{\rm weight}=\lceil2\alpha^2/\theta\rceil+b_e+7
 =O(b_e+\alpha^2/\theta).
\tag{23}
\]
Under the later caller's parameters this is \(O(b_e+p^2\log p)\).
If \(a\le16\lceil\log_2p\rceil\), \(\theta\ge1/(4p^2)\), \(p\ge2\),
and \(b_e=Cp\), its retained setup allowance
\(Cp+64p^2\lceil\log_2p\rceil\) exceeds (23).
The kernel grid (6) adds \(O(\alpha^2w)\), which is \(o(p)\) at the
intended bandwidth. Increasing the fixed precision constant absorbs
that allowance.

I keep full-cell weights and reference ratios in offline preparation.
Online gauges use only the anchored exponent range \(F_g\).
Combining (17)–(19) with the completed normalized theorem gives
\[
 O(F_0+t+\log n+\log R+1/c_T+F_g+\log\alpha)
\tag{24}
\]
bits for coefficients, data records and gate temporaries.
I add two parallel scalar layers and \(2n\) gates.
For internal headroom I use the child's bound at radius \(R_*\) and
the final bound \((G+1)(HR_*+E_{\rm norm})+r\).
The verifier checks the resulting signed-grid and temporary allowances.

For capped blocks in the later parameter range, \(F_g\) is bounded by
the anchored quadratic/linear range, while \(1/c_T=O(\log p)\) on the
broad side. These are local online bounds. I leave the carve, complete
Schur/boundary program, coefficient delivery, simultaneous tensor layout
and tape costs outside this receipt. The broad boundary Schur factor
requires application; the narrow inverse caller needs its separate solve.

## 9. Verification and attribution

I check a complete finite periodic reference against three explicit
windings plus analytic bounds for omitted windings, in both induced norms.
I check actual row gaps, a principal inverse crossing a phase boundary
and a hole, retained cuts, physical support and overlapping pages.
The exponential comparisons share Mason's declared interval backend.
The written series bounds cover the infinite tails.

I execute broad/narrow raw blocks with positive and negative center
phases, reverse the same stored program, and compare rounded outputs
with exact rational reference matrices and separate inverse elimination.
Controls cover underfunded tails/coefficients, zero setup weights,
stale pages, hole completion, normalization and inverse wrapper order.
Increasing reference setup precision changes the reference while
leaving the independently allocated online circuit unchanged.

I credit Vlado Vojdanovski for phase-cell references, q-LDU and circuits;
Jeremy Kothe/IdeaOuter for shifted raw identities; Mason Hale for interval
arithmetic and earlier Gaussian execution; Chafik Boukhalfa for phases
and fine-prime setup work; Cinna Davis for the later caller and comparison
contract; and classical Neumann-series and diagonal-scaling methods.
Internal agents belong to our author process. Independent reviewers
must assess the universal proof separately from the finite receipts.
I retain ToikY's separate scalar-backend audit in
[PR4220](https://github.com/CrocSwap/integer-mult-bounds/pull/4220),
head `5cf23ba47a28b78a98eb0665177b5030e65c01b9`, at our completed
normalized source `66b95cc916552f487203be14fd99a7aea0bdd78e`.
That audit excludes the raw/reference argument presented here.
