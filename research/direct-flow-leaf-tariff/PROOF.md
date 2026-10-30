# The power-tariff transition of the fixed direct-flow leaves

## Statement and inherited inputs

This is a scoped proof about the historical raw-p7 leaf measure. It does not
establish a complete multiplication theorem, a full-flow invoice or a new κ.
The leaf model and inventory are Ryanson Jonathan / pinterbanget's
[PR #4467](https://github.com/CrocSwap/integer-mult-bounds/pull/4467).
DLamdata's [PR #6118](https://github.com/CrocSwap/integer-mult-bounds/pull/6118),
at `6310550e932de70243fc2aaab6f4885688b6fe21`, proves saturation of its
conditional log-deficit. We use its tilted nonlattice local-limit framework as
a cited mathematical input, without replaying its certificate or claiming its
source-law derivation as new work. The new result is the complete real-power
moment asymptotic, including its critical and divergent regimes.

Let

```
P = {1:37305, 2:10695, 3:3360, 4:1530, 5:300,
     8:1464, 16:448, 32:448, 48:448},       m = 121,
Z(s) = sum_r P[r] r^s,                    mu(s) = (log Z)'(s),
a = log 5,                               mu(alpha) = a,
lambda = t-alpha > 0,                    sigma^2 = (log Z)''(alpha).
```

The theorem holds for **every fixed real t > alpha**. Its intended application
uses the raw-p7 crossing exponent `t` of #4467/#6118. We inherit, rather than
recertify, #6118's numerical identification of that exponent. No numerical root
or onset estimate is needed for the result below. Since `P` has positive mass
at 1 and 48, `mu` is strictly increasing from 0 to log48; hence alpha exists
uniquely and sigma is positive. The support contains 1, 2 and 3, so the log-rank
law is nonlattice, as in #6118.

For each fixed integer `G >= 0` and real `delta in [0,a]`, put
`N=m exp(Ga+delta)` and define the fixed-depth leaf measure below. At the closed
endpoint `delta=a`, **keep this G**: this is a fixed-depth extension, not a
recalculation of the floor. For actual integer ranks `N >= m`, instead select
`G=floor(log_5(N/m))` and `delta=log(N/m)-Ga in [0,a)`; that selects the original
leaf model from this family. Let `c_G(rho)` be the weighted count
of ordered G-tuples of paid ranks with product rho, retaining `m*rho <= N`.
Each tuple has weight the product of its P multiplicities. The leaf multiset
has `c_G(rho)*P[r]` leaves at rank `ell=r*rho`, using **every** terminal r,
without truncating the terminal rank again. This is the inherited #4467 leaf
model, separated from the other exit components by #6118.

For any fixed real shift u, define its normalized power tariff

```
M_G(u,delta) = sum_ell L_N(ell) ell^(t+u)
              / (N^u sum_ell L_N(ell) ell^t),
A(u) = m^(-u) Z(t+u)/Z(t),       v = lambda+u.
```

**Theorem.** Uniformly over `delta in [0,a]` (and therefore along every integer
rank sequence as `G -> infinity`), the following three regimes hold:

1. If `v > 0`, then

   `M_G(u,delta) -> A(u) lambda/v`.

2. If `v = 0`, then

   `M_G(u,delta) ~ A(u) lambda sigma sqrt(pi/2) sqrt(G)`.

3. If `v < 0`, put

   `R(u) = [Z(t+u)/Z(alpha)] exp(-v a)`.

   Then `R(u)>1` and

   `M_G(u,delta) ~ A(u) lambda sigma sqrt(2*pi*G) exp(-v delta) R(u)^G`.

Here `~` means the ratio tends to one, uniformly in delta. The exponent
threshold is exactly `t+u=alpha`. The boundary offset disappears from the first
two leading terms but survives in the third.

## 1. Exact finite identity

Give each prefix step the probability `p_s(r)=P[r]r^s/Z(s)`. Set
`S_G=sum_i log R_i`, `B=Ga+delta`, and `Y=B-S_G`. Expectations `E_s` refer to
independent prefix steps with law p_s. The independent, untruncated terminal
step has law p_t. Weighting the leaf multiset by ell^t therefore gives exactly

`M_G(u,delta) = A(u) E_t[exp(-uY) | S_G <= B]`.                 (1)

For any real v define the finite quantity

`J_G(v,delta)=E_alpha[exp(-vY) 1_{Y>=0}]`.

Changing the prefix measure from t to alpha in numerator and denominator of
(1) cancels `(Z(alpha)/Z(t))^G exp(lambda B)`. Thus, for every finite G,

`M_G(u,delta) = A(u) J_G(lambda+u,delta)/J_G(lambda,delta)`.    (2)

The denominator is positive because the all-ones prefix is admissible. In
particular `M_G(0,delta)=1` exactly. No asymptotic interchange or extra terminal
barrier occurs in (1) or (2).

## 2. Positive tilt

We use the following standard consequence of the nonlattice interval local
limit theorem, in the precise form used in #6118 §§3–4:

`J_G(w,delta) ~ 1/[w sigma sqrt(2*pi*G)]`, for each fixed w>0. (3)

For clarity, the inputs to (3) are explicit. Under p_alpha, the centered
variable `log R-a` has zero mean, positive finite variance sigma^2 and a
nonlattice law. The uniform interval local limit theorem gives convergence of
the scaled measure near any bounded delta to Lebesgue measure divided by
`sigma sqrt(2*pi)`. It also bounds the scaled probability of every unit interval
by a constant. Integrating exp(-w y) on y>=0 follows by compact step-function
approximation and the summable tail `sum_{j>=J} exp(-w j)`. Atoms at the barrier
are negligible by the same interval theorem with arbitrarily small fixed
interval width. These facts give uniformity in bounded delta and the constant
`integral_0^infinity exp(-wy)dy=1/w`.

This use requires no strong nonlattice condition and claims no convergence
rate. The classical input is C. Stone, *A local limit theorem for nonlattice
multi-dimensional distribution functions*, Ann. Math. Statist. 36 (1965),
546–551, Corollary 1, equation (7):
[DOI](https://doi.org/10.1214/aoms/1177700165). We cite the source-relative
specialization in #6118; we do not assert an independent audit of that paper.

Apply (3) at w=lambda and w=v>0 in (2). Their ratio tends to lambda/v,
proving regime 1. Weak convergence to the exponential law alone would not
justify its negative-u part: (3) supplies the necessary tail control.

## 3. The critical tilt

When v=0, `J_G(0,delta)=P_alpha(S_G<=Ga+delta)`. The ordinary central limit
theorem gives

`J_G(0,delta) -> 1/2`                                       (4)

uniformly in bounded delta. Indeed the standardized endpoint is
`delta/(sigma sqrt(G)) -> 0` uniformly, and the normal distribution is
continuous at zero. Divide (4) by (3) at w=lambda in (2). The resulting
constant is `A(u) lambda sigma sqrt(2*pi)/2`, giving regime 2.

## 4. Below the critical exponent

For v<0 put beta=alpha+v=t+u. A second exact change of measure gives

`J_G(v,delta) = exp(-v delta) R(u)^G P_beta(S_G<=Ga+delta)`.   (5)

The signs and offset in (5) follow directly from
`p_beta(tuple)/p_alpha(tuple)=(Z(alpha)/Z(beta))^G exp(v S_G)`.
Since beta<alpha and mu is strictly increasing, `mu(beta)<a`. The weak law of
large numbers gives `P_beta(S_G<=Ga+delta)->1`, uniformly for delta in [0,a].
For example, the complementary event is contained in `S_G/G>a`, whose
probability is at most `Var_beta(log R)/(G(a-mu(beta))^2)` by Chebyshev.
Strict convexity of log Z gives

`log R(u)=log Z(beta)-log Z(alpha)-(beta-alpha)a > 0`.

Divide (5) by (3) at w=lambda in (2) to obtain regime 3.

## 5. Consequence and scope

The normalized leaf tariff has a finite limit precisely when `t+u>alpha`;
it grows as sqrt(G) at equality and exponentially in G below it. Thus a finite
mean log-depth does not authorize substituting an arbitrary power tariff or
exchanging that tariff with the limiting exponential law. The finite limit
above the threshold is explicit, including the independent terminal-rank
factor `Z(t+u)/Z(t)`.

This settles the leaf component only. Relative source, boundary and leaf
masses, their joint normalization, a total refined-induction ceiling, explicit
finite-depth error bounds, physical delivery and every supplier-admission
obligation remain open. The fixed historical raw-p7 law is not the selected
#6030 invoice. Neither the three regimes nor their finite checks change κ.

New proof produced by Nick Petalas. Credit DLamdata (#6118) for the saturation
framework; Ryanson Jonathan / pinterbanget (#4467/#4465/#4459) for the leaf law
and diagnostics; zxv (#4436) for the direct flow; Cinna Davis / 1337isnot1337
(#4405) for refined induction; Jacob Alan Sussman for the lockstep compiler;
and Stone for the classical local limit theorem. Apache-2.0.
