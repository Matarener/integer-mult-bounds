# Shifted Gaussian conditioning

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance.
Apache-2.0.

I use the normalized kernel

\[
k(u)=e^{-\gamma u^2+2\gamma su},\qquad
\Phi(w)=\sum_{u\in\mathbb Z}k(u)e^{-iuw},\qquad
\gamma>0,\quad |s|<1/2.
\]

Write \(\delta=1-2|s|\) and \(m=\Phi(\pi)\). The unit diagonal is \(k(0)=1\).
For the unnormalized kernel \(e^{-\gamma(u-s)^2}\), multiply symbol and
accretivity bounds by \(e^{-\gamma s^2}\), and inverse bounds by
\(e^{\gamma s^2}\). I use Euclidean vector and induced operator norms throughout.

I credit Jeremy Kothe/IdeaOuter and the PR1758 contributors for the product
and phase argument in `vendor/GAUGEFREE-INTERIORS.md`, Lemmas 3.1–3.3.
In Section 1 I make their minimum implication explicit. Vlado Vojdanovski
already used the unshifted Poisson estimate in `FORWARD-SMALL-A-AUDIT.md`.
I add the shifted uniform floor, its sharp exponential order, the
finite-section inverse limit, and the source-specific bounds in Section 5.
For the stronger finite-cap estimate I use Vlado's retained exact q-LDU
identities from `HOLES-AND-Q-LDU.md`, Section 2, and the finite-origin
Newton argument in `BILATERAL-LDU.md`. I claim the conditioning corollary
and caller substitution, not the factorization identities.

## 1. Exact minimum from the retained product argument

The Gaussian decay gives absolute convergence, including after multiplication
by any fixed power of \(|u|\). Put \(q=e^{-\gamma}\). By conjugation we may
take \(s\ge0\), and by periodicity and conjugation take \(0\le w\le\pi\).
Jacobi's product gives

\[
\Phi(w)=C\prod_{n\ge1}(1+a_ne^{-iw})(1+b_ne^{iw}),\quad
C=\prod_{n\ge1}(1-q^{2n}),
\quad a_n=q^{2n-1-2s},\quad b_n=q^{2n-1+2s}.
\]

We have \(1>a_n\ge b_n\ge a_{n+1}>0\), and summable deficits in the tails.
For \(f(r)=\arg(1+re^{iw})\), differentiation gives
\(f'(r)=\sin w/|1+re^{iw}|^2\ge0\). Finite sums telescope; convergence
then gives

\[
0\le-\arg\Phi(w)=\sum_{n\ge1}[f(a_n)-f(b_n)]\le f(a_1)<\pi/2.
\]

Consequently, using positive real factors,

\[
\begin{aligned}
\Re\Phi(w)
&\ge |\Phi(w)|\cos f(a_1)\\
&=C(1+a_1\cos w)
  \prod_{n\ge2}|1+a_ne^{-iw}|\prod_{n\ge1}|1+b_ne^{iw}|\\
&\ge C(1-a_1)\prod_{n\ge2}(1-a_n)\prod_{n\ge1}(1-b_n)
=\Phi(\pi)=m>0.
\end{aligned}
\]

At \(w=\pi\) we attain equality. Away from \(\pi\) modulo \(2\pi\),
we have \(1+a_1\cos w>1-a_1\). Since \(|\Phi|\ge\Re\Phi\), we obtain

\[
\min_w\Re\Phi(w)=\min_w|\Phi(w)|=m.
\]

I claim this minimum as an inherited corollary, not as a new phase method.

## 2. A shift-uniform floor with exponent \(1/4\)

I prove, for the entire stated domain,

\[
\boxed{\displaystyle
m\ge L(\gamma,s):=\delta\sqrt{\frac{\pi}{\gamma}}\,
e^{-\pi^2/(4\gamma)}.}
\]

First suppose \(0<\gamma\le4\). Poisson summation for the shifted Gaussian,
followed by pairing opposite odd frequencies, gives

\[
m=2e^{\gamma s^2}\sqrt{\frac{\pi}{\gamma}}e^{-\pi^2/(4\gamma)}
\left[\cos(\pi s)+
\sum_{r\ge1}e^{-\pi^2r(r+1)/\gamma}\cos((2r+1)\pi s)\right].
\]

For \(t=\pi/2-\pi|s|\in(0,\pi/2]\), use
\(|\sin(nt)|\le n\sin t\) for positive integers \(n\), obtained by summing
the \(n\) unit terms in the geometric formula for \(\sin(nt)/\sin t\).
For odd \(n=2r+1\) this gives

\[
|\cos((2r+1)\pi s)|\le(2r+1)\cos(\pi s).
\]

With \(q_P=e^{-2\pi^2/\gamma}\), bound the relative remainder by

\[
D\le\sum_{r\ge1}(2r+1)q_P^r
=\frac{q_P(3-q_P)}{(1-q_P)^2}.
\]

Here \(r(r+1)\ge2r\). Since \(\pi>3\) and \(e>2\),
\(q_P<e^{-4}<1/16\), whence \(D<47/225<1/2\).
Concavity gives \(\cos(\pi s)\ge\delta\); also \(e^{\gamma s^2}\ge1\).
Keeping \(1-D>1/2\) in the paired expression proves \(m\ge L\).

For \(\gamma\ge4\), put \(q=e^{-\gamma}<1/16\) and remove the first
near-unit deficit from the positive product:

\[
m=(1-q^\delta)
\prod_{n\ge1}(1-q^{2n})
\prod_{n\ge2}(1-q^{2n-2+\delta})
\prod_{n\ge1}(1-q^{2n-\delta}).
\]

The sum of the remaining deficits is at most
\((q+2q^2)/(1-q^2)\le6/85\). Apply
\(\prod(1-r_j)\ge1-\sum r_j\) to finite products and pass to the
convergent limit. Concavity in \(\delta\) also gives
\(1-q^\delta\ge\delta(1-q)\ge15\delta/16\). Thus

\[
m\ge\frac{79}{85}\frac{15}{16}\delta
=\frac{237}{272}\delta>\frac23\delta.
\]

For \(x=\pi^2/(2\gamma)>0\),

\[
\left(\sqrt{\frac{\pi}{\gamma}}e^{-\pi^2/(4\gamma)}\right)^2
=\frac2\pi xe^{-x}\le\frac2{\pi e}<\frac13<\frac49.
\]

This proves the remaining range.

For \(0<\gamma\le1\), compare with the retained simplified floor
\(L_{\rm old}=(1-e^{-\gamma\delta})e^{-\pi^2/(3\gamma)}\).
Since \(1-e^{-\gamma\delta}\le\gamma\delta\),

\[
\frac{L}{L_{\rm old}}\ge
\sqrt\pi\,\gamma^{-3/2}e^{\pi^2/(12\gamma)}>1.
\]

I restrict this dominance assertion to the stated range. For example, at
\(s=0\) and large \(\gamma\), the old floor approaches one and \(L\) approaches zero.
Reviewers can retain the maximum of the two valid floors.

The relative Poisson remainder tends to zero uniformly in \(|s|<1/2\);
so does \(e^{\gamma s^2}-1\). Therefore, as \(\gamma\downarrow0\),

\[
\frac{m}{2\cos(\pi s)\sqrt{\pi/\gamma}\,e^{-\pi^2/(4\gamma)}}\longrightarrow1
\quad\hbox{uniformly in }|s|<1/2.
\]

For a coarse bound on \(0<\gamma\le1\), use
\(e^{\gamma s^2}\le e^{1/4}<4/3\),
\(\cos(\pi s)=\sin(\pi\delta/2)\le(\pi/2)\delta<2\delta\), and \(D<1/2\).
Then \(L\le m\le8L\). Thus we capture both the small-scale exponential
coefficient \(1/4\) and the linear dependence on the shift gap.

## 3. Sharp uniform inverse constant for finite sections

Let \(N\) be a positive integer and \(T_N[i,j]=k(j-i)\), \(0\le i,j<N\). For
\(p_z(w)=\sum_{j=0}^{N-1}z_je^{ijw}\), direct integration and Parseval give

\[
\Re(z^*T_Nz)=\frac1{2\pi}\int_{-\pi}^{\pi}
\Re\Phi(w)|p_z(w)|^2\,dw\ge m\|z\|_2^2.
\]

Cauchy–Schwarz gives \(\|T_Nz\|_2\ge m\|z\|_2\), hence invertibility and
\(\|T_N^{-1}\|_2\le1/m\). In fact the inequality is strict for each fixed
\(N\): for every nonzero \(z\), its polynomial cannot vanish on an interval,
and \(\Re\Phi>m\) off \(\pi\). Compactness of the unit sphere gives a
strictly positive smallest eigenvalue for the Hermitian part minus \(mI\).
I use the Hermitian part for accretivity, not the eigenvalues of nonnormal \(T_N\).

To prove sharpness uniformly over \(N\), take \(x_{N,j}=(-1)^j/\sqrt N\).
For an integer shift \(u\), zero extension loses
\(\min(|u|,N)\) entries of this vector. The triangle inequality yields

\[
\|T_Nx_N-mx_N\|_2
\le\sum_{u\in\mathbb Z}k(u)\sqrt{\frac{\min(|u|,N)}N}
\le\frac{A}{\sqrt N},\quad
A=\sum_{u\in\mathbb Z}\sqrt{|u|}\,k(u).
\]

For \(n\ge1\), \(\sqrt n\le n\) and
\(n^2-2|s|n\ge n(n-1)\ge n-1\). Thus

\[
A\le2\sum_{n\ge1}ne^{-\gamma(n-1)}
=\frac2{(1-e^{-\gamma})^2}
\le A_0:=\frac{2(1+\gamma)^2}{\gamma^2}.
\]

The last step uses \(e^\gamma\ge1+\gamma\). Since
\(\sigma_{\min}(T_N)\le\|T_Nx_N\|_2\), we have

\[
\boxed{\displaystyle
\frac1{m+A_0/\sqrt N}\le\|T_N^{-1}\|_2<\frac1m,\qquad
\lim_{N\to\infty}\|T_N^{-1}\|_2
=\sup_{N\ge1}\|T_N^{-1}\|_2=\frac1m.}
\]

The limit also holds along dyadic \(N\). For \(\varepsilon>0\) and a
certified lower endpoint \(0<\underline m\le m\), any
\(N\ge(A_0/(\varepsilon\underline m))^2\) gives
\(\|T_N^{-1}\|_2\ge1/((1+\varepsilon)m)\). The verifier records such a
dyadic size descriptor for \(\varepsilon=1/8\); I do not execute those
large matrices or claim monotonicity in \(N\). This statement concerns fixed
\(\gamma,s\) and unrestricted sizes, not attainment within a caller's capped block.

## 3a. A finite-size bound through the half-shift endpoints

We can use the finite cap to avoid the loss as \(\delta\downarrow0\).
For this section allow \(|s|\le1/2\), including both endpoints, and let
\(N\ge1\) be an integer. With \(q=e^{-\gamma}\), \(Q=q^2\), put
\[
P_j=\prod_{r=1}^j(1-Q^r),\quad P_0=1,\quad
{i\brack j}_Q=\frac{P_i}{P_jP_{i-j}}\quad(0\le j\le i).
\]
I prove the finite bound
\[
\boxed{\displaystyle
|(T_N(s)^{-1})_{ij}|
\le \frac{q^{|i-j|+2s(i-j)}}{P_{N-1}^3}
\le\frac1{P_{N-1}^3},\qquad
\|T_N(s)^{-1}\|_2\le\frac{N}{P_{N-1}^3}
\le N e^{\pi^2/(4\gamma)}.}
\]
Unlike the uniform-over-all-sizes accretivity bound, this estimate remains
finite at the half shifts for a fixed \(N\).

Start from the source's exact finite factorization for
\(G_{ij}=q^{(i-j)^2}\):
\[
G=L\,\operatorname{diag}(P_j)L^T,\qquad
L_{ij}=q^{(i-j)^2}{i\brack j}_Q,\qquad
(L^{-1})_{ij}=(-q)^{i-j}{i\brack j}_Q \quad(i\ge j).
\]
For completeness, factor \(G_{ij}=q^{i^2}(Q^{-i})^jq^{j^2}\).
Vandermonde determinants give the leading minor
\(\Delta_n=\prod_{j=0}^{n-1}P_j\); the powers of \(q\) cancel.
The minor with rows \(0,\ldots,j-1,i\) and columns \(0,\ldots,j\),
divided by \(\Delta_{j+1}\), gives the stated \(L_{ij}\).
The positive pivots are \(P_j\), so symmetry supplies the upper factor.
To check the inverse, use
\({i\brack k}_Q{k\brack j}_Q={i\brack j}_Q{i-j\brack k-j}_Q\).
For \(n=i-j\), the product reduces to a nonzero scalar times
\[
\sum_{r=0}^n(-1)^rQ^{r(r-1)/2}{n\brack r}_Q
=\prod_{r=0}^{n-1}(1-Q^r).
\]
For \(n>0\) the product vanishes; for \(n=0\) it equals one. This is the
classical [finite q-binomial theorem, DLMF17.2.35](https://dlmf.nist.gov/17.2.E35).

Write \(D_s[i,i]=q^{2si}\). Then
\(T_N(s)=D_sGD_s^{-1}\), which proves invertibility for these finite
matrices without a positive symbol minimum. At \(s=1/2\), the absolute
entries of the shifted lower inverse are
\[
|(D_{1/2}L^{-1}D_{1/2}^{-1})_{ij}|
=Q^{i-j}{i\brack j}_Q
\le Q^{i-j}/P_{i-j}.
\]
Here \(P_i/P_j\le1\). Its column sums are at most
\[
\sum_{r=0}^{N-1}\frac{Q^r}{P_r}=\frac1{P_{N-1}},
\]
because \(Q^r/P_r=1/P_r-1/P_{r-1}\) for \(r\ge1\).
The shifted upper inverse has absolute entries
\({j\brack i}_Q\le1/P_{N-1}\), and each inverse diagonal pivot is also
at most \(1/P_{N-1}\). Multiplying the three finite factors gives
\[
|(T_N(1/2)^{-1})_{ij}|\le P_{N-1}^{-3}.
\]
The negative endpoint is the transpose, so it satisfies the same entry bound.

For \(i\ge j\), use
\((T_N(-1/2)^{-1})_{ij}=q^{-(i-j)}(G^{-1})_{ij}\);
for \(i<j\), use the positive endpoint instead. Thus
\(|(G^{-1})_{ij}|\le q^{|i-j|}/P_{N-1}^3\).
Conjugating by \(D_s\) proves the displayed entry estimate for the entire
closed shift interval. Bounding both row and column sums by \(N/P_{N-1}^3\)
gives the Euclidean norm bound.

Finally \(P_{N-1}\ge P_\infty>0\). Expanding the logarithm and summing
nonnegative terms gives
\[
-\log P_\infty
=\sum_{h\ge1}\frac1{h(e^{2\gamma h}-1)}
\le\frac1{2\gamma}\sum_{h\ge1}\frac1{h^2}
=\frac{\pi^2}{12\gamma}.
\]
This proves \(P_{N-1}^{-3}\le e^{\pi^2/(4\gamma)}\).
For strict shifts, reviewers may use the smaller of this finite-size
bound and \(1/m\). I do not claim an optimal finite-size constant or an
inverse algorithm with controlled intermediate precision from this norm bound.

## 4. Rounding, truncation and certificate interpretation

If an approximate kernel \(\widetilde k\) satisfies
\(\sum_u|\widetilde k(u)-k(u)|\le\varepsilon<m\), zero extension and
Young's inequality give \(\|\widetilde T_N-T_N\|_2\le\varepsilon\),
uniformly in \(N\). Therefore

\[
\Re(z^*\widetilde T_Nz)\ge(m-\varepsilon)\|z\|_2^2,\qquad
\|\widetilde T_N^{-1}\|_2\le\frac1{m-\varepsilon}.
\]

For a truncated kernel, charge both the omitted coefficients and retained
rounding error. For nonnegative integers \(W,R\), after \(|u|\le W\),
the two Gaussian tails obey

\[
\sum_{u>W}k(\pm u)\le
\frac{\exp[-\gamma((W+1)^2\mp2s(W+1))]}
 {1-\exp[-\gamma(2W+3\mp2s)]}.
\]

We derive this by bounding consecutive positive-term ratios by the first ratio.
At \(\pi\), retain \(R\) Jacobi factors of each kind and write their product
as \(P_R\). The omitted deficit sum obeys

\[
E_R=
\frac{e^{-\gamma(2R+2)}+
e^{-\gamma(2R+1-2s)}+e^{-\gamma(2R+1+2s)}}{1-e^{-2\gamma}}.
\]

For \(E_R<1\), \(P_R(1-E_R)\le m\le P_R\).
The verifier intersects this product enclosure with the direct alternating
series plus its two absolute tails. It also checks overlap with the Poisson
leading-term enclosure. Intersection corroborates consistency of formulas;
the explicit remainder bounds justify containment.

For each real rounded finite section, the verifier forms
\((\widetilde T_N+\widetilde T_N^T)/2-\underline m I/2\),
performs exact rational LDL elimination, checks positive pivots and
reconstructs the entire matrix. These are positivity certificates for the
specified finite matrices. For a complex rounded kernel we would need
conjugate transpose instead. The universal claims rely on Sections 1–3.
The `kernel_error_majorant` interval encloses the computed upper-bound
expression; its lower endpoint is not a lower bound on the actual error.
The finite-section inverse lower/upper fields concern the ideal matrix.
The separately named rounded inverse bound uses \(1/(m-\varepsilon)\).
The additional finite-cap fixtures use exact rational \(q\), including
both half shifts. I reconstruct the finite q-LDU and triangular-inverse
identities, check both products with the direct shifted matrix, and
check the entry decay and row/column bounds. These checks concern completed
inverses; they do not certify a physical implementation of the factorization.

I use precision-80 directed Decimal arithmetic for basic operations.
Python documents correctly rounded nearest `exp` and `sqrt`; I widen each
endpoint by one adjacent representable value. I enclose \(\pi\) through
Machin's identity and rational alternating series, and cosine through its
Taylor series with an explicit alternating remainder. I trap underflow,
subnormal values and invalid arithmetic. The checker rejects inconclusive
intervals; it never interprets a failed lower enclosure as a counterexample.
This contract trusts CPython Decimal and rational arithmetic, rather than a
formal proof kernel. See the [Python 3.12 Decimal documentation](https://docs.python.org/3.12/library/decimal.html).

## 5. Consequence for the actual broad Gaussian caller

In PR4100 `GAUSSIAN.md`, take \(p\ge2\) tending to infinity and use natural
logarithms. Fix \(0<\xi<1\), and take \(1\le N\le B\le p^\xi\), together with

\[
\frac1{4p^2}\le\theta\le\frac1{p^2},\quad
\rho=1+\theta,\quad\lambda=\rho^{-1},\quad
\alpha=\left\lceil\sqrt{\frac4\pi\log(16p)}\right\rceil,\quad
a=\pi\alpha^2,\quad b_0=\pi/\alpha^2.
\]

For a centered constant-phase interior use \(|\Delta|\le1/2\),
\(s=-\Delta(1-\theta)\), \(\gamma=b_0\lambda\), and \(|x|,|y|\le B/2\).
Then \(\delta\ge\theta\), so

\[
m\ge\theta\alpha\sqrt\rho\,e^{-a\rho/4}.
\]

The source's exact broad identity, including its raw \(\alpha^{-1}\)
normalization, gives

\[
K=\alpha^{-1}e^{-b_0\Delta^2}D_yT_N(k)D_x,
\]
\[
D_x(x)=e^{-b_0(1-\lambda)x^2-2b_0(\Delta+\lambda s)x},\qquad
D_y(y)=e^{b_0\lambda(1-\lambda)y^2+2b_0\lambda(\Delta+s)y}.
\]

The scalar \(e^{-\gamma s^2}\) from the unnormalized kernel cancels
the opposite constant in the separable gauge identity. These gauges are
positive real scalings. We must account for their inverse norms.
Since \(\Delta+\lambda s=2\lambda\theta\Delta\) and
\(\Delta+s=\theta\Delta\),

\[
G:=e^{b_0\Delta^2}\|D_x^{-1}\|_2\|D_y^{-1}\|_2
\le\exp\left[\frac{b_0}4+
b_0\lambda\theta\left(\frac{B^2}4+\frac{3B}2\right)\right].
\]

We get \(G=1+o(1)\), uniformly over the admitted \(\theta,\Delta,N,B\) at
fixed \(\xi\). Consequently

\[
\boxed{\displaystyle
\|K^{-1}\|_2\le Q_p:=
\frac{G}{\theta\sqrt\rho}e^{a\rho/4}
\le p^{3+o(1)}.}
\]

To justify the last exponent, use the actual ceiling formula:

\[
a\le4\log(16p)+4\sqrt{\pi\log(16p)}+\pi.
\]

Hence \(e^{a\rho/4}=p^{1+o(1)}\), while \(\theta^{-1}\le4p^2\).
The source's coarse \(a\le5\log(16p)\) alone would not give this exponent.
The ceiling term also prevents an \(O(p^3)\) conclusion from this argument.

For the actual finite cap, Section 3a gives the stronger bound
\[
\boxed{\displaystyle
\|K^{-1}\|_2\le Q_p^{\rm cap}:=
\alpha G N e^{a\rho/4}
\le p^{1+\xi+o(1)}\qquad (N\le B\le p^\xi).}
\]
Here \(\alpha=p^{o(1)}\), \(G=1+o(1)\) and
\(e^{a\rho/4}=p^{1+o(1)}\), uniformly over the admitted blocks.
This avoids the \(\theta^{-1}\) loss in the unrestricted-size symbol estimate.
At fixed \(\xi<1\), we obtain an inverse allowance below \(p^2\) eventually.
We can use \(\min(Q_p,Q_p^{\rm cap})\) in a perturbation argument.

For a raw operator perturbation of norm \(\varepsilon_p\) with
\(\varepsilon_pQ_p^{\rm cap}\le1/2\), the inverse bound becomes
\(Q_p^{\rm cap}/(1-\varepsilon_pQ_p^{\rm cap})\le2Q_p^{\rm cap}\),
preserving \(p^{1+\xi+o(1)}\).
A claimed truncation/rounding implementation must prove that premise.

I improve the source's loose \(p^6\) allowance for these capped interiors.
I do not assert optimality of \(p^{1+\xi+o(1)}\) for capped, gauged blocks.
The caller assigns holes, phase cuts and period cuts to the boundary, and
applies the broad Schur complement without inverting it. I retain those
restrictions. The shallow-circuit construction, coefficient-generation costs,
complete tensor error ledger and multiplication theorem need separate review.

## References and priority

For classical identities, see [NIST DLMF, theta products](https://dlmf.nist.gov/20.5)
and [theta transformations](https://dlmf.nist.gov/20.7).
Pasupathy and Damodar studied centered Gaussian Toeplitz matrices in
[*The Gaussian Toeplitz matrix*, Linear Algebra and its Applications 171
(1992), 133–147](https://doi.org/10.1016/0024-3795(92)90255-9).
I make no worldwide priority claim for Gaussian Toeplitz conditioning,
Poisson summation or approximate Fourier vectors. The bounded repository
overlap search and exact predecessor credits appear in README.md.
