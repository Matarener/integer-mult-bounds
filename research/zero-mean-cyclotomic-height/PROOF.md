# A zero-mean cyclotomic logarithm

This scoped written proof was produced by Nick Petalas. It supplies one new
Fourier estimate and substitutes it into Chafik Boukhalfa's
[PR #1025](https://github.com/CrocSwap/integer-mult-bounds/pull/1025).
The predecessor's resultant, cofactor and primitive-unit estimates are cited
premises. Their replay is not this contribution. Independent human and formal
proof-kernel review are unclaimed.

## The finite Fourier identity

Let r>=3 be an integer, zeta=exp(2 pi i/r), and define a real function on Z/r by

    F(0)=-log r,
    F(s)=log|1-zeta^s| for 1<=s<r.

All logarithms are natural. Normalize Fourier coefficients by

    Fhat(h)=(1/r) sum_s F(s) zeta^(-hs).

Then

    Fhat(0)=0,
    Fhat(h)<0 for 1<=h<r,
    sum_h |Fhat(h)|=log r.                                  (1)

The special value at zero is never used in a coefficient product. It is a
choice in the Fourier argument. No claim that it minimizes Fourier mass over
all choices of that value is needed or made.

For 0<=rho<1 put Lrho(s)=log|1-rho zeta^s|. The absolutely convergent
logarithm series and finite Fourier orthogonality give, for 1<=h<r,

    Lrho_hat(h)=-1/2 sum_(q>=0) [rho^(qr+h)/(qr+h)
                                    +rho^(qr+r-h)/(qr+r-h)],
    Lrho_hat(0)=(1/r)log(1-rho^r).

When h=r/2 the two congruence classes coincide and the displayed halves
correctly combine to one full term. Subtracting the mean and integrating
the geometric series gives

    -(Lrho_hat(h)-Lrho_hat(0))
       =1/2 integral_0^rho
          [x^(h-1)+x^(r-h-1)-2x^(r-1)]/(1-x^r) dx.          (2)

As rho tends to one, the left side tends to -Fhat(h). Indeed the s=0
summand cancels in the difference, all other summands converge, and
sum_(s=1)^(r-1) log|1-zeta^s|=log r, by evaluating
(X^r-1)/(X-1) at X=1. The same product proves Fhat(0)=0.

The numerator of the integrand in (2) is positive for 0<x<1. Its quotient
by 1-x equals

    N_h(x)=sum_(a=h-1)^(r-2) x^a
                  +sum_(a=r-h-1)^(r-2) x^a.

Thus its quotient by 1-x^r is N_h(x)/S_r(x), where
S_r(x)=1+x+...+x^(r-1). This extends continuously to x=1 and is positive
on the open interval. The integral is finite and strictly positive.
Consequently Fhat(h)<0. Fourier inversion at zero now gives
sum_(h!=0) Fhat(h)=F(0)=-log r, proving (1).

A second exact mass identity is

    sum_(h=1)^(r-1) N_h(x)=2 S_r'(x).

It makes the sum of the integrals in (2) equal to
integral_0^1 S_r'/S_r=log r. These are elementary finite identities;
no asymptotic equidistribution or irrational-rotation theorem is used.

## Averaged coefficient height

Use exactly PR #1025's polynomial and height notation:

    n=r-1, D=phi(r), ell=ceil(log2 r),
    a_(k,j)=product_(s=j+1)^n (1-zeta^(ks)),
    f_k(z)=sum_(j=0)^n a_(k,j) z^j=r P_k(z),
    H_k=sum_j |a_(k,j)|,

where k runs over the units modulo r. For this section r is a prime power.
Every suffix has s!=0, and multiplication by k preserves that fact. Fourier
inversion therefore represents log|a_(k,j)| using F without changing a
coefficient. Since Fhat(0)=0, the geometric-sum bound gives, simultaneously
for every suffix,

    log|a_(k,j)| <= sum_(h=1)^(r-1)
                          |Fhat(h)| 2/|1-zeta^(hk)|.

The same nonnegative right side also bounds the empty suffix, whose logarithm
is zero. Let M_k be the maximum of these logarithms. PR #1025 proves that,
for each nonzero h, the unit average of 2/|1-zeta^(hk)| is at most
2(1+log r). This uses prime-power unit reduction and d/phi(d)<=2 for
d=r/gcd(h,r), and is retained unchanged. Apply (1) to obtain

    average_k M_k <= 2 log r (1+log r).

There are r coefficients, so H_k<=r exp(M_k), and hence

    sum_k log H_k <= D [2(log r)^2+3 log r].                 (3)

This improves the predecessor's D[4(log r)^2+8 log r+2]. It averages a
pointwise bound on the maximum. It does not interchange a maximum and an
average or assert (3) at one chosen embedding.

## Uniform circle gap

For prime-power r, Ali Romman's PR #621 establishes the nonzero resultant
used in PR #1025. The latter's norm/cofactor cancellation implies

    |P_k(z)| >= 1/[2rn product_(a unit mod r) H_a^n], |z|=1.

This is the cited implication, including its normalization, and is not a
new resultant claim. Substitution of (3) yields

    |P_k(z)| >= exp(-n D [2(log r)^2+3 log r])/(2rn).        (4)

Write c=log 2. Since ell>=2, log r<=ell c and c<3/4,

    [2(log r)^2+3 log r]/c
        <= 2c ell^2+3ell
        < (3/2)ell^2+3ell
        <= 3ell^2.

The last difference is (3/2)ell(ell-2)>=0. Also 2rn<=2^(1+2ell).
The inherited coarse exponent, obtained from H_a<=2^r, remains available.
Taking the smaller valid exponent proves

    |P_k(z)| >= 2^-d_new,
    d_new=1+2ell+n D min(r,3ell^2).                         (5)

The predecessor's corresponding minimum uses 8ell^2. At r=4096,
ell=12 and D=2048, (5) is 3,622,993,945, versus the predecessor's
9,661,317,145. These are sufficient analytic gap exponents, not actual
word lengths, norm measurements or timing results.

## Exact finite corroboration and limits

The verifier checks the N_h polynomial identities at every r=2..96 and
1<=h<r. Its finite positive Abel sums also satisfy, exactly,

    1/2 sum_(h=1)^(r-1) sum_(q=0)^(m-1)
       [1/(qr+h)+1/(qr+r-h)-2/(qr+r)] = H_(mr)-H_m.

Here H_j is a harmonic number, unrelated to the coefficient height H_k.
The sum tends to log r. The script checks it at r=2..40, m=8,32 and
encloses log r by an exact rational atanh series. The truncation tail is
bounded geometrically, without binary floating point. Formal log(2),log(3)
DFTs at r=3,4,6 independently check the chosen diagonal, zero mean and signs.
Large dyadic budget cases test only integer exponent arithmetic.

The universal analytic result is the written argument above. The finite
checks do not prove it for every r. The primitive-unit estimate and the
nonzero resultant remain cited predecessor premises. Composite radices,
actual reduced-precision inverse execution, rounded preparation, common-label
compilation, dirty restoration, physical tapes/hosting, full transforms and
the multiplication theorem are outside this result. No new kappa or selected
frontier change is claimed. The proof does not claim that 3 is an optimal
dyadic coefficient or that this diagonal choice is optimal.
