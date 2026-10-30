# A finite-depth exponential envelope for the direct-flow leaf deficit

This is a scoped written proof. The classical Berry–Esseen inequality is an
external theorem. The exact verifier checks the finite numerical hypotheses
and the rational constants below. It is not a formalization of this proof.

## 1. Law and result

Use Ryanson Jonathan / pinterbanget's PR #4467 paid law

```
P = {1:37305, 2:10695, 3:3360, 4:1530, 5:300,
     8:1464, 16:448, 32:448, 48:448}
W = {5:420, 6:270, 7:840, 8:1395, 9:3195,
     25:448, 41:448, 57:448, 121:224}.
```

Write Z(s)=sum_r P_r r^s and mu(s)=Z'(s)/Z(s). Let t be the invoice
root sum_k W_k k^t=Z(t) in [0.9973,0.9974], and let alpha be the unique
solution mu(alpha)=a=log(5). Put lambda=t-alpha. PR #6118 supplies the
qualitative saturation theorem, its sharper parameters and the exact
identification of the leaf measure. They are predecessor results.

Let R_i be iid with p_t(r)=P_r r^t/Z(t), S_G=sum_i log(R_i),
B_G=G a+delta, and define the unconditioned difference Y_G=B_G-S_G.
Conditioning is written explicitly wherever it is used.

**Theorem.** For every integer G>=11000, every delta in [0,log(5)], and
all real x>=0,

    Pr_t(Y_G>=x | S_G<=B_G) <= min(1, 5 exp(-lambda x)).

Consequently, for all L>=0,

    E_t[(Y_G-L)_+ | S_G<=B_G] <= (5/lambda) exp(-lambda L),
    E_t[Y_G 1_{Y_G>=L} | S_G<=B_G]
        <= 5 (L+1/lambda) exp(-lambda L).

These are finite-depth tail and truncation-error bounds, uniform across the
whole lockstep level. They are a partial answer to PR #4467 open question 2.
They establish neither the Bahadur–Rao asymptotic nor its error term,
and give no rate of convergence to Exp(lambda), no full-flow share or ceiling,
and no new kappa. The law is historical, rather than the selected P104 law.

## 2. A quantitative tilted-normal lemma

Let q(r)=P_r r^alpha/Z(alpha). Under q, X=log(R) has mean a, variance
sigma^2>0 and third absolute centered moment rho. Set b=(14/25) rho/sigma^3.
Berry–Esseen gives a Kolmogorov distance at most b/sqrt(G) between
Y=B_G-S_G and a normal variable Z with mean delta and variance G sigma^2.
The constant 14/25=0.56 is deliberately conservative. For example,
[Shevtsova, arXiv:1111.6554v1](https://arxiv.org/abs/1111.6554v1), abstract
and Corollary 1, proves an iid constant below 0.4756. Only the weaker 0.56
bound is used here. No nonlattice local-limit or finite-depth asymptotic
expansion is needed for this lemma.

If two distribution functions are within epsilon and f has finite total
variation and vanishes at both infinities, integration by parts bounds the
difference of their expectations by epsilon times the total variation of f.
For f_x(y)=exp(-lambda y) 1_{y>=x}, x>=0, that variation is
2 exp(-lambda x). The bound remains valid at atoms, by taking one-sided
limits of distribution functions against the continuous normal CDF. Thus,
with c=1/(sigma sqrt(2 pi)),

    sqrt(G) E_q[f_x(Y)] <= exp(-lambda x) (c/lambda+2b).       (1)

Indeed, the normal density is at most c/sqrt(G) everywhere. If

    sigma sqrt(G) >= a+1/lambda,

then for every 0<=delta<=a and 0<=y<=1/lambda its normal density is at
least c exp(-1/2)/sqrt(G). Integration on that interval gives

    sqrt(G) E_q[f_0(Y)]
      >= c exp(-1/2) (1-exp(-1))/lambda - 2b.                (2)

Whenever the right side is positive, division of (1) by (2) is legitimate.
For every ordered tuple, p_t(tuple)/q(tuple) is

    (Z(alpha)/Z(t))^G exp(lambda B_G) exp(-lambda Y).

Its common factor cancels under conditioning. Therefore E_q[f_x]/E_q[f_0]
is exactly the desired conditional tail. This change of measure, including
its direction and normalization, holds at finite G.

## 3. Explicit constants for this law

The verifier establishes the following coarse intervals with exact rational
series. It does not reproduce PR #6118's high-precision parameter receipt.

    0.9973 < t < 0.9974,
    0.9898 < alpha < 0.9899,
    7/1000 < lambda < 8/1000,
    7/5 < sigma < 3/2,
    a < 2,
    |log(r)-a| < 5/2 for every supported r.

The last bound implies rho <= (5/2) sigma^2, hence b<=1. Also
5/2 < sqrt(2 pi) < 8/3 implies 1/4<c<2/7. Elementary exponential
series give exp(-1/2)>3/5 and 1-exp(-1)>3/5. Consequently (2) exceeds

    (1/4)(3/5)(3/5)(1000/8)-2 = 37/4,

whereas the coefficient in (1) is below

    (2/7)(1000/7)+2 = 2098/49 < 5(37/4).

The normal-window premise follows for G>=11000 from

    ((2+1000/7)/(7/5))^2 = 25704900/2401 < 11000.

This proves the tail inequality. The elementary pi bounds can be weakened
to 25/8<pi<32/9; the familiar rational bounds 3.14<pi<22/7 suffice.
Their truth is a standard mathematical input, not an output of the verifier.

The endpoint signs certify a root t by continuity. Its uniqueness on the
stated interval follows from a strictly positive derivative of
sum W_k k^s - sum P_r r^s, also enclosed by the verifier. The strictly
positive variance makes mu strictly increasing, so alpha is unique.

## 4. Truncation and the actual leaf observable

Integrating the tail from L to infinity proves the positive-part bound.
The identity E[Y 1_{Y>=L}]=L Pr(Y>=L)+E[(Y-L)_+] proves the second bound,
including L=0 and distributions with atoms. A convenient mean bound is
E[Y] <= (1+log(5))/lambda, obtained by integrating min(1,5 exp(-lambda x)).

For rank N, PR #6118 identifies G=floor(log_5(N/121)),
delta=log(N/121)-G log(5), and an independent terminal rank R with law p_t.
Its actual leaf depth is log(121)+Y_G-log(R). The terminal rank remains
unconditioned. For G>=11000, clipping Y_G at L changes the mean actual leaf depth
by at most (5/lambda) exp(-lambda L). This is a deterministic error bound
for that truncation, not a bound on distance to the limiting mean.

## Credit and limits

The finite-depth envelope, its explicit threshold and truncation constants
are produced by Nick Petalas. Ryanson Jonathan / pinterbanget supplied the
law, diagnostic and quantitative open question in PR #4467. DLamdata's
PR #6118 supplied the saturation proof and the precise leaf-measure statement.
zxv supplied the direct flow, Cinna Davis the refined induction, and Jacob
Alan Sussman the lockstep compiler. Berry–Esseen, change of measure and the
bounded-variation expectation estimate are classical ingredients.

The result does not discharge any of the selected record's five assumptions.
No selected supplier, complete flow, physical word, native theorem, numerical
induction ceiling or complete multiplication theorem is checked here.
Independent human and formal proof-kernel review are unclaimed. Apache-2.0.
