# Effective preparation of the full Gaussian cell

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0.
The exact source and q-LDU identities are retained from JoyboyBrian's PR5479
and its Gaussian predecessors. This is a written proof with exact finite
corroboration. It is not independent human or formal proof-kernel acceptance.

## Source and result

Let p be an integer at least 16. Use the actual source parameters

```
alpha = ceil(sqrt((4/pi) log(16p))),
1/(4p^2) <= theta <= 1/p^2,  rho = 1+theta,
N = floor(1/theta),        b = pi/alpha^2,
K[k,i] = alpha^(-1) exp(-b(i-(k+1/2)/rho)^2),  0 <= i,k < N.
```

The preparation algorithm takes the source integer alpha and rational theta
as inputs. Source-prime selection and the computation of alpha remain upstream
work. Their cost is not set to zero. Write
`mu(M)=max(||M||_1,||M||_infinity)`. This norm is submultiplicative and bounds
the operator 2-norm.

The following finite bound holds for every stated p and theta:

```
mu(K^(-1)) <= B = 5 p^6.
```

For every integer t>=0, the supplied algorithm constructs one banded dyadic
matrix A and one dense dyadic matrix R with

```
mu(A-K) <= delta,
mu(R-K^(-1)) <= 2^(-t),     mu(R) <= 2B.
```

It gives exact interval and integer-residual certificates. Its preparation
cost is polynomial in N, t, log(p) and the bit length of theta. All matrices,
intermediate rational numbers and numerical proposals are charged below.
No physical native call or selected-kappa improvement is inferred.

PR5479's eventual p^(2+eta) bound is asymptotically sharper. The new guard is
explicit from p=16 and is sufficient for certified reference preparation.
It is not a stronger asymptotic inverse theorem.

## A finite inverse guard

The retained source identity sets gamma=b/rho and
`P(gamma)=product_(r>=1)(1-exp(-2 gamma r))`. Every checkerboard inverse entry
has the form `alpha exp(E_ij) F_ij`, where

```
0 <= F_ij <= P(gamma)^(-3),
E_ij <= b/4 - gamma theta (i-j)^2.
```

For i<=j the last inequality uses j^2-i^2 >= (j-i)^2. For i>j, reflect both
indices as in PR5479. Its offset delta is in [1,2); the extra cross term has
the favorable sign. Thus the same inequality holds. These are exact finite
identities; no limit or finite-product replacement is used.

For a>0, monotonicity of exp(-a x^2) gives
`sum_(d in Z) exp(-a d^2) <= 1+sqrt(pi/a)`. Apply this to each row and column
of the absolute inverse. The result is

```
mu(K^(-1)) <= alpha exp(b/4) P(gamma)^(-3)
                         (1+alpha sqrt(rho/theta)).                 (1)
```

The source's decreasing-integrand argument gives
`P(gamma)^(-3) <= exp(pi^2/(4 gamma)) = exp(pi alpha^2 rho/4)`.
We now make all remaining constants effective.

Put u=log(p). For p>=16, `8/3 < log(16) <= u` and `log(16p)<=2u`.
The source ceiling gives
`alpha < sqrt(8u/pi)+1`. It follows that alpha<=sqrt(p): at p=16,
`sqrt(8 log(16)/3)+1 < sqrt(8)+1 < 4`; the difference
`exp(u/2)-sqrt(8u/3)-1` is increasing for u>=log(16), because its derivative
is at least `2-1/2`. Also alpha>=3, b<1 and rho<=257/256.
Using `3<pi<22/7`,

```
pi alpha^2 rho/(4u)
 < (257/256) (2+sqrt(2pi/u)+pi/(4u))
 < (257/256) (2+25/16+5/16)
 = 7967/2048 < 4.
```

Thus the product factor is at most p^4. Further,
`exp(b/4)<2` and `sqrt(rho/theta)<(17/8)p`. Equation (1) gives

```
mu(K^(-1)) <= 2 p^(9/2) + (17/4) p^6
            <= (137/32) p^6 < 5 p^6.
```

The implementation also checks the sufficient inequalities alpha^2<=p and
`exp(pi alpha^2 rho/4)<=p^4` by exact intervals. These guards admit the actual
source ceiling; they can also admit other well-conditioned alpha values.
The finite fixtures separately check the exact source ceiling. The algorithm
does not silently choose a different alpha.

## A sharper guard for actual preparation

The polynomial guard ensures an effective uniform contract. The executable
also computes a sharper rational upper bound from (1). It encloses
`q=exp(-2gamma)` from above. Outward integer recurrences bound every q power
and bound the finite product from below. Stop only when the geometric tail
`q^(m+1)/(1-q)` is at most 2^(-32). The elementary product inequality
`product(1-u_j) >= 1-sum(u_j)` then gives a positive lower bound for the
entire infinite product. This charges the tail, rather than replacing the
infinite product by its partial product.

A lower bound for exp(-b/4) bounds exp(b/4) from above. An integer square-root
calculation gives a rational upper bound for sqrt(rho/theta), with denominator
2^32. Substitution in (1), followed by an integer ceiling, gives B_q. Use
`B=min(5p^6,B_q)` for every subsequent bit and band choice. Both inputs to
this minimum are proved upper bounds. The product interval uses
`64+16 bit_length(p)` working bits. In the production regime gamma is
Theta(1/log p), so the required term count and interval work are polynomial
in log p. The source's product lower bound and these guard bits keep the
rounded product positive. For an explicit termination bound, alpha^2<=p and
rho<=257/256 give 1-q>3/p. The interval and grid errors are at most three
units in the working grid, so the upper ratio has gap at least 1/p. Within
4p^2 steps its geometric tail, including rounded-power error, is below
2^(-32). The cumulative product error is at most
`20 p^4 2^(-work) < p^(-4/3)/2`; the source product bound gives
`P(gamma)>=p^(-4/3)`. Thus the product stays positive for every p>=16.
These conservative bounds suffice even without the sharper logarithmic
production estimates. This reduces the large excess in the uniform
polynomial guard without a numerical norm estimate.

## Bandwidth and entry rounding

Let G=ceil(log2 B), Q=t+2G+4 and choose the least integer w with

```
w >= alpha,             30 w^2 >= 7 alpha^2 (Q+3).
```

Set m=min(N,2w+1), L=Q+ceil(log2 m)+2 and U=t+G+ceil(log2 N)+4.
Keep entries with |i-k|<=w and round each to a multiple of 2^(-L), with a
certified entry error at most 2^(-L). Set the other entries to zero.

The source displacement from the diagonal is
`(k theta-1/2)/rho`, whose absolute value is at most 1/2 because k<N.
The omitted absolute row sum and column sum are therefore bounded by

```
(2/alpha) sum_(d>=w+1) exp(-b(d-1/2)^2)
 <= (2/alpha + alpha/(pi(w+1/2))) exp(-b(w+1/2)^2)
 < exp(-b w^2) <= 2^(-(Q+3)).                           (2)
```

The first inequality uses the first term and the Gaussian tail integral.
The strict coefficient bound uses alpha>=3, w>=alpha and pi>3.
The last step uses pi>3 and log(2)<7/10. It remains valid when the band
covers the whole cell, since then the omitted sum is zero.
There are at most m rounded entries per row and column. Consequently

```
delta = m 2^(-L) + 2^(-(Q+3)) <= (3/8) 2^(-Q).          (3)
```

In particular B delta<1/8, so A is invertible and
`mu(A^(-1)) <= B/(1-B delta) < 2B`. A shifted Gaussian sum is at most its
maximum plus its integral. It gives
`mu(K) <= 1/alpha+rho < 3/2`; hence `mu(A)<2`.

The width is `O(sqrt((t+log p) log p))`. It becomes
`O(sqrt(p log p))` when t=O(p), as in the source's common-reference accuracy
regime. No capped RawGaussian API admission follows from that order bound.

## Exact coefficient intervals

The code encloses pi with Machin's identity and alternating rational sums.
The identity follows from
`tan(4 atan(1/5))=120/119` and
`(120/119-1/239)/(1+120/(119*239))=1`, with the angle in (0,pi/2).
Each alternating remainder lies between its partial sum and the sum with
the next term. Outward dyadic rounding retains this enclosure.

To enclose exp(-x), x>=0, divide x by 2^k until z<=1. Compute the positive
Taylor sum for exp(z) on an outward-rounded integer grid. If the last term
is T_n, the omitted tail is at most `3 T_n z/(n+1)`: after the next term,
the ratios are at most 1/(n+2). Invert the positive interval, then square
it k times with outward rounding. The code checks the final width and
increases the working grid if needed. Each step encloses the exact value.
The Taylor remainder decreases factorially. The cumulative rounding width
is `O(2^k n/2^work)`, so work polynomial in the requested bits and k suffices.
All divisions use integer floor or ceiling, not a floating-point error model.

For retained entries, x=pi z with rational z. Evaluate the two pi endpoints
and use monotonicity. The derivative bound
`z exp(-pi_low z) <= 1/(e pi_low) < 1` controls pi uncertainty uniformly in z.
The chosen pi and exponential guard bits make the resulting entry interval
narrower than half an output grid step. Rounding its midpoint to the nearest
grid value therefore has error below one step. The code checks that both
interval endpoints lie within the claimed step for every retained entry.

## Inverse preparation and the decisive certificate

First compute a 60-digit Decimal elimination proposal, with row pivoting.
Round its entries to multiples of 2^(-U). This proposal is untrusted.
The verifier multiplies integer numerators to compute every entry of AR-I,
and computes the exact absolute row and column sums. Accept only if

```
epsilon = mu(AR-I) <= 2^(-(t+G+3)),
mu(R) <= 2B,
B (delta mu(R)+epsilon) <= 2^(-t).                      (4)
```

If the proposal or its certificate fails, use exact rational elimination
with row pivoting and round the exact inverse to the same grid. This is a
complete algebraic algorithm, not a numerical assumption. All intermediate
fractions are computed and charged. Invertibility guarantees a nonzero pivot
at each column after row exchanges.

The exact path always passes. Its rounding error has mu-norm at most
`N 2^(-U)/2 <= 2^(-(t+G+5))`. Since mu(A)<2, its residual is strictly below
the first bound in (4). The inverse-norm guard follows from (3), and the
last error bound has strict slack. In particular (3) and the first two
bounds in (4) imply an error at most `(11/64)2^(-t)`.

For every accepted proposal, independently of how it was obtained,

```
K^(-1)-R = K^(-1) ((I-AR)+(A-K)R).
```

This exact identity proves (4)'s error bound and retains the multiplication
order. The error bound holds for every input vector, not only
for a sampled payload. It also bounds the operator 2-norm.

## Preparation resources and exact scope

Let H be the binary length of the rational theta descriptor. Formation uses
`O(N min(N,w))` certified exponential entries, with polynomial work in
H, t and log(p) per entry. The executable currently stores the forward
matrix densely, including its zero entries. It also stores the dense inverse.
No sparse-memory saving is claimed for that implementation.

For the exact completion path, integer forward coefficients have O(L) bits.
Every reduced elimination fraction is a ratio of minors. The determinant
bound gives `O(N(L+log N))` bits per numerator and denominator. Thus exact
preparation uses O(N^3) rational operations on numbers of that size and
`O(N^3(L+log N))` working bits. With school arithmetic this gives
`O(N^5(L+log N)^2)` bit work, up to the usual integer-arithmetic logarithmic
factors. The fixed-precision proposal adds O(N^3) Decimal operations before
that worst-case cost. The final arrays use `O(N^2(t+log p))` bits, plus
dimensions and the source descriptor. All these are positive costs.

This constructs a common numerical reference and its inverse table. It does
not place them in a native supplier, emit a reversible dirty circuit, pay a
whole multiplication caller, or establish page delivery, tape movement,
stock reuse, preparation amortization or outer recovery. A physical consumer
must use this same reference and charge those operations. The source's
p^10 analytic inverse allowance is compatible with the finite guard, but
its complete API is not admitted here. No new kappa is claimed.

## Verification boundary

The verifier rebuilds complete 256-column and 299-column cells. The latter
uses p=17, alpha=3, theta=601/599-1, with literal prime checks, and retains
N=floor(599/2)=299. It certifies two requested accuracies on that geometry.
All retained coefficients have exact intervals and all inverse-residual
entries are computed with integers. An independent rational Taylor sum
checks the exponential enclosure on a bounded set of arguments. Exact
inverse completion is checked on separate small matrices with a row exchange.
The large cells use certified Decimal proposals; a large exact-completion
run is not claimed. Mutants reject an altered inverse, omitted forward
coefficient, incomplete cell, wrong parameter domain and failed guard.
