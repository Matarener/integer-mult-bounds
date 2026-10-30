# The sharp concentration threshold for nearest-grid Gaussian dominance

This scoped proof was produced by Nick Petalas. Apache-2.0.

## Model and statement

Let \(s,t\) be integers with \(s<t<2s\), \(\rho=t/s=1+\theta\),
and use the physical Gaussian source's half-up convention

\[
q_j=\lfloor\rho j+1/2\rfloor,\qquad \beta_j=\rho j-q_j\in[-1/2,1/2).
\]

For real \(a>0\), define the original-coordinate coefficient at displacement
\(h\ne0\) by

\[
k_{i,h}(a)=\exp\{-a[(\rho h+\beta_i)^2-\beta_{i+h}^2]\}.
\]

The cyclic matrix \(N_{s,t,w}(a)\), for integer \(1\le w<s/2\), has diagonal
one and coefficient \(k_{i,h}\) at column \(i+h\pmod s\) for
\(0<|h|\le w\); all other entries vanish. Since \(\beta_{j+s}=\beta_j\),
this agrees with the source's signed cyclic displacement, including physical
period seams. It is an ideal matrix, before numerical coefficient errors.
The production concentration is \(a=\pi u\); here \(a\) is allowed to vary.

Write \(R_i(a)=\sum_{0<|h|\le w}k_{i,h}(a)\). For every \(a\ge1\),

\[
\boxed{R_i(a)\le e^{-2a\theta}+2e^{-2a}
                   +\frac{2e^{-6a}}{1-e^{-6a}}.}                 \tag{1}
\]

For even \(s\ge6\), \(t=s+1\), and \(2\le w<s/2\), the half-tie row
\(i=s/2\) also satisfies

\[
\boxed{R_{s/2}(a)\ge e^{-2a/s}+e^{-a(2+4/s)}+e^{-a(2+8/s)}.}  \tag{2}
\]

For this family there is a unique threshold \(A_{s,w}>0\) such that every
row is strictly diagonally dominant exactly when \(a>A_{s,w}\). Uniformly
over every allowed \(w\ge2\), as even \(s\to\infty\),

\[
\boxed{A_{s,w}=\tfrac12(\log s-\log\log s+\log2)+o(1).}        \tag{3}
\]

All logarithms are natural. In particular the leading concentration
coefficient \(1/2\), the subtractive log-log term, and the additive
\(\log2/2\) are necessary for a uniform continuous-concentration guarantee.
For integer \(u\), the least admitted value is
\(\lfloor A_{s,w}/\pi\rfloor+1\); its corresponding expansion has
\(O(1)\), rather than \(o(1)\), rounding uncertainty.

## Upper bound

The retained LOG-A-PHASE-SCHUR-AUDIT, section 1, already proves

\[
k_{i,-1}+k_{i,1}\le e^{-2a\theta}+e^{-2a(1+\theta)}.           \tag{4}
\]

We use that result as a premise. The new estimate concerns the farther
tail. Since \(\beta_{i+h}^2\le1/4\), for each positive \(h\ge2\),

\[
k_{i,h}+k_{i,-h}\le
e^{-a((\rho h+\beta_i)^2-1/4)}+
e^{-a((\rho h-\beta_i)^2-1/4)}.
\]

The right side is an even convex function of \(\beta_i\) on
\([-1/2,1/2]\). Indeed each summand's second derivative has the sign of
\(2a(\rho h\pm\beta_i)^2-1\), which is positive for \(a\ge1,h\ge2\).
Its maximum is therefore at an endpoint. Since \(\rho>1\), this gives

\[
k_{i,h}+k_{i,-h}\le e^{-ah(h-1)}+e^{-ah(h+1)}.
\]

Summing the positive convergent series and shifting the first index yields

\[
\sum_{|h|\ge2}k_{i,h}\le e^{-2a}
           +2\sum_{r\ge2}e^{-ar(r+1)}
\le e^{-2a}+\frac{2e^{-6a}}{1-e^{-6a}}.                        \tag{5}
\]

For the last inequality, successive exponents \(r(r+1)\) differ by at least
six for \(r\ge2\). Combine (4), (5), and
\(e^{-2a(1+\theta)}\le e^{-2a}\). A finite band only removes positive terms,
so (1) follows without an infinite-period identification or a tail-admission
assumption. The earlier \(5e^{-2a}\) tail coefficient is sufficient but
does not locate the additive transition constant.

## Lower bound

For \(t=s+1\), even \(s\), and \(i=s/2\), the actual nearest convention gives

\[
\beta_i=-1/2,\quad
\beta_{i+1}=-1/2+1/s,\quad
\beta_{i-1}=1/2-1/s,\quad
\beta_{i+2}=-1/2+2/s.
\]

Substitution into the coefficient definition gives exponents
\(2/s\), \(2+4/s\), and \(2+8/s\) at displacements \(+1,-1,+2\).
All three are retained for every \(w\ge2\). Dropping the other nonnegative
entries proves (2). The second farther entry matters: retaining only one
\(e^{-2a}\) contribution predicts an incorrect additive threshold.

## Threshold and its uniform asymptotics

Every off-diagonal exponent is positive because
\(|\rho h+\beta_i|\ge\rho|h|-1/2>1/2\ge|\beta_{i+h}|\).
Thus \(\max_i R_i(a)\) is continuous and strictly decreasing. At zero it is
\(2w>1\), and it tends to zero at infinity. This proves existence and
uniqueness of \(A_{s,w}\), including the strict endpoint convention.

Set \(L=\log s\) and, for any fixed real \(b\),

\[
a_s(b)=\tfrac12(L-\log L+b),\qquad e^{-2a_s(b)}=s^{-1}Le^{-b}.
\]

As \(s\to\infty\), \(a_s(b)\to\infty\), \(a_s(b)/s\to0\), and

\[
\frac{1-e^{-2a_s(b)/s}}{s^{-1}L}\longrightarrow1.
\]

In (1) the other leading contribution, divided by \(s^{-1}L\), is
\(2e^{-b}\); the remaining geometric tail divided by that scale tends
to zero. In (2), the two farther terms have sum

\[
s^{-1}Le^{-b}(e^{-4a_s(b)/s}+e^{-8a_s(b)/s}),
\]

whose normalized limit is also \(2e^{-b}\). Consequently (1) proves
dominance eventually whenever \(b>\log2\), and (2) proves failure
eventually whenever \(b<\log2\). Neither estimate depends on \(w\).
Sandwiching the threshold between these two concentrations, with \(b\)
arbitrarily close to \(\log2\), proves (3) uniformly in \(w\).
No sign at the exact choice \(b=\log2\) is asserted.

## Scope and predecessor credit

The matrix convention comes from Jose Manuel's PR3851 physical Gaussian
core. The nearest-neighbor estimate (4) comes from Vlado Vojdanovski's
retained phase-cell audit in the PR1673 lineage and its RaD/hipotures
predecessors. The new result is the matching concentration threshold,
using (5) and the three-entry obstruction. No predecessor computation is
replayed as a contribution.

This theorem varies concentration outside the unchanged production guard.
It does not prove a changed production caller, coefficient-error bound,
inverse implementation, complete signed invoice, or new multiplication
theorem or kappa. The selected frontier and all five assumptions remain.
The universal result is this written proof; the accompanying exact finite
checks corroborate its new formulas and detect missing-tail admissions.
