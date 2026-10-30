# A uniform production-scale Gaussian boundary limit

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
This is a scoped written theorem with exact finite corroboration, not a
formal-kernel or independent-human proof acceptance.

## Quantifiers and exact source

Let h=sqrt(theta), rho=1+theta, N=floor(1/theta), and n=N-1. For
0<=k,i<N use the unchanged full-cell broad source matrix

    K[k,i]=alpha^-1 exp(-b(i-k/rho-1/(2rho))²), b=pi/alpha².

There is no band truncation. Put S=diag((-1)^i), A=S K^-1 S,
P(t)=product_{r>=1}(1-exp(-2tr)), a_b=alpha exp(b/4) P(b)^-3,
and s=sqrt(b)*h. Split the indices at floor(N/2). Embed each left index
as the normalized indicator of [si,s(i+1)) in the first L² half-line;
embed right index i as the corresponding indicator at n-i in the second.
Call this isometry U_s. Let T have kernel
exp(-(y²-x²)) 1{x<=y} on L²(0,infinity).

Uniformly for

    h -> 0,                 h^(1/5) <= b <= 1,             (1)

we prove

    || U_s (s A/a_b) U_s* - (T direct-sum T) || -> 0.      (2)

The retained half-line proof establishes ||T||=1/2 using the maximal
first-order operator -d/dx+2x and its Dirichlet adjoint; we retain that
endpoint-domain result. Thus (2) gives the uniform relative asymptotic

    ||K^-1||₂ = (1+o(1)) alpha exp(b/4)
                         / (2 sqrt(b theta) P(b)^3).     (3)

This extends the predecessor's fixed-alpha theorem to a specified joint
regime. The first retained source case remains alpha=3,theta=1/400,N=400;
that small fixture need not satisfy the eventual domain (1). Source geometry
is checked exactly, not used as evidence that an asymptotic quantifier holds.

The actual PR4100 setup is alpha=ceil(sqrt((4/pi)log(16p))) and
1/(4p²)<=theta<=1/p². It satisfies (1) eventually, uniformly in theta.
Here p tends through positive integers, logarithms are natural, and the
ceil and floor in the displayed source are retained. This is the untruncated
full cell, not a claim that the existing capped RawGaussian API accepts it.

## Relative q-product lemma

Retain the exact q-LDU identity, credited through #1673, #4193, #5103 and
#5150 and the pinned half-line theorem. Set gamma=b/rho, Q=exp(-2gamma),
P_j=product_{r=1}^j(1-Q^r), P=P(gamma). For i<=j define L=N-1-j and

    F_ij=sum_{r=0}^L Q^r P_(j+r)/(P_i P_(j-i+r) P_j P_r).

Then A_ij=alpha exp(E_ij)F_ij, with

    E_ij=b(theta*j-1/2)²/rho²-gamma*theta*(j²-i²).         (4)

For i>j reflect both indices: i'=n-i,j'=n-j, with i'<j'. The coefficient
F is invariant under that reflection and the exponent is

    E_ij=b(theta*j-1/2)²/rho²
          -gamma*theta*((j'+delta)²-(i'+delta)²),
    delta=1/theta-n in [1,2).                            (5)

In either orientation E_ij<=b/4. These are exact finite identities.
For m>=1 put

    eps_m=Q^(m+1)/((1-Q)(1-Q^(m+1))).

If i>=m, j-i>=m, and L>=m, then

    exp(-4 eps_m) <= P³ F_ij <= 1.                       (6)

Here are the details that avoid the predecessor's exponentially poor
absolute constants. Write R_j=P_j/P. For j>=m,

    0<=log R_j=sum_{r>j}-log(1-Q^r)
       <=Q^(j+1)/((1-Q)(1-Q^(j+1)))<=eps_m.

The positive weights w_r=P Q^r/P_r sum to one, since
Q^r/P_r=1/P_r-1/P_(r-1) for r>=1. Moreover
sum_{r=0}^L w_r=P/P_L=1/R_L>=exp(-eps_m). Now

    P³ F_ij=sum_{r=0}^L w_r R_(j+r)/(R_i R_(j-i+r) R_j).

Each numerator is >=1 and each of the three denominator factors is
<=exp(eps_m), proving the lower bound. For the upper bound,
P_(j+r)/P_j<=1, P_i,P_(j-i+r)>=P, and sum Q^r/P_r<=1/P.
This also proves P³F<=1 outside the good region. No finite product is
silently substituted for P, and the whole r-sum is essential.

For b<=1, h<=1/2, gamma>=b/2. Logarithmic differentiation gives

    d log P(t)/dt = sum_{r>=1} 2r/(exp(2tr)-1)
      <= 2/(1-exp(-b))³ <=16/b³,       gamma<=t<=b.

Consequently, with

    k=exp(48 h²/b²)-1,

we have 1<=P(b)^3/P(gamma)^3<=1+k. On the good cells,

    |P(b)^3 F_ij-1| <=4(1+k)eps_m+k.                    (7)

Everywhere 0<=P(b)^3 F_ij<=1+k. The derivative bound follows from a
convergent geometric majorant, so differentiation under the sum is valid.

## Uniform operator estimate

Choose R>=1, J=floor(R/s), m>=1, and assume s<=R/2,
2J<=N, J>=m, and N-J>=m+1. Retain the left upper-triangular J-square
and right strictly-lower J-square, assigning the diagonal only once.
Their images lie in the two different half-line summands.

In the upper remainder j>=J, j²-i²>=(j-i)J. Each row sum and each
column sum of sA/a_b is at most

    (1+k)s sum_{d>=0} exp(-s² J d/rho)
       <=(1+k)(s+rho/(sJ)) <=(1+k)(s+4/R).

We used rho<=2 and sJ>=R/2. Reflection gives the same estimate on the
lower remainder. This includes middle and cross-edge entries. The
continuum remainder has norm at most 2/R per summand by the analogous
row/column integral; using a sum instead of a maximum only enlarges
our bound. A safe combined discrete/continuum tail allowance is

    4(1+k)(s+4/R).                                     (8)

On each retained square, x=s(i+u), y=s(j+v), 0<=u,v<=1. The exponent
bound in the pinned half-line proof, with its window radius replaced
by R/sqrt(b), gives

    |E_ij - (b/4-(y²-x²))| <= D,
    D=12(R+1)² h.                                      (9)

Indeed its bound is 12b(R/sqrt(b)+1)²h, at most (9) when b<=1.
The same calculation covers the reflected offset delta in [1,2).
Both exponents after subtracting b/4 are nonpositive, hence exp has
Lipschitz constant one on their range.

Cells with i<m or j-i<m occupy at most 2msR area per corner. Their
kernel difference is at most 2(1+k); triangle and Hilbert-Schmidt bounds
give 8(1+k)sqrt(ms(R+1)) for both exceptional regions. Diagonal cells
include the possible cell crossing of x=y and the strict lower convention.
On the remaining two squares, (7)-(9) give the operator bound
2R[4(1+k)eps_m+k+(1+k)D]. Therefore

    || U_s(sA/a_b)U_s*-(T direct-sum T) ||
    <=4(1+k)(s+4/R) + 8(1+k)sqrt(ms(R+1))
       +2R[4(1+k)eps_m+k+(1+k)D].                      (10)

The embedded finite operator is zero on the orthogonal complement of
its step-function range. The argument compares its integral kernel on
all of both half-lines; it does not omit that complement.

## One simultaneous choice for the entire regime

Take R=h^(-1/10), m=ceil(h^(-1/5)/b), J=floor(R/s).
Under (1), for all sufficiently small h uniformly in b:

* s<=h and s>=h^(11/10); thus R/s>=h^(-11/10),
  J<=h^(-6/5), while N=floor(h^-2). Hence 2J<=N.
* m<=2h^(-2/5), so J>=m and N-J>=m+1 eventually.
* ms(R+1)<=4h^(3/5): use m<=h^(-1/5)/b+1,
  s=h sqrt(b), b>=h^(1/5), and R+1<=2h^(-1/10).
* Q<=exp(-b); bm>=h^(-1/5). Thus
  eps_m<=4b^-1 exp(-h^(-1/5))
        <=4h^(-1/5)exp(-h^(-1/5)).
* k<=exp(48h^(8/5))-1, and RD<=48h^(7/10).

All terms in (10) tend to zero uniformly. In particular the R times
exponential tail vanishes, Rk=O(h^(3/2)), and (8) is O(h^(1/10)).
This proves (2) without exchanging two unquantified limits.

## Production polynomial conditioning, with ceilings preserved

Put l=log(16p). The actual alpha satisfies
sqrt(4l/pi)<=alpha<sqrt(4l/pi)+1, hence b is comparable to 1/log p.
Since h in [1/(2p),1/p], eventually h^(1/5)<=b<=1 uniformly.
To bound the product, f(x)=-log(1-exp(-x)) is positive decreasing, so

    -log P(b)=sum_{r>=1} f(2br)
          <=(1/(2b)) integral_0^infinity f(x)dx
          =pi²/(12b).

The integral follows by the positive exponential series and
sum_{k>=1}1/k²=pi²/6. Therefore P(b)^-3<=exp(pi alpha²/4).
For sufficiently large p, (2) bounds the normalized norm by one, giving

    ||K^-1||₂ <= alpha²/(sqrt(pi)*h)
                    exp(b/4+pi alpha²/4)
       <= 2p alpha²/sqrt(pi)
                    exp(b/4+l+sqrt(pi*l)+pi/4).          (11)

For every fixed eta>0, the right side is <=p^(2+eta) eventually.
This is a uniform polynomial upper bound, with the asymptotic coefficient
still given exactly by (3). We do not replace its product by an unproved
large-alpha formula, nor assert a sharp p-power lower bound here.
In particular a p^10 allowance eventually dominates this *exact full-cell
inverse norm*. A rounded or truncated reference would additionally need
its own perturbation bound (for example ||K^-1|| ||Delta||<1); this proof
has not admitted such a reference or its circuit.

## Decision, costs and next obligations

The fixed-alpha restriction is removed for the actual production scale.
A full-cell conditioning objection based solely on taking alpha to infinity
is therefore resolved for this exact kernel. Existing capped-section
conditioning arguments remain separate, and no existing program is changed.

The theorem constructs no coefficient producer or inverse-application
algorithm. Common rational reference formation, truncation, grid rounding,
all circuit prefix bounds, coefficient/page storage and physical delivery,
tape movement, preparation amortization and integer recovery retain their
costs and proof obligations. No charge is assigned zero; no runtime,
complete multiplication theorem, supplier admission or new kappa follows.

Open next questions: bind a specified rounded full-cell reference using
(11) and its actual entry-error invoice; then determine whether any concrete
inverse consumer can exploit the guard while paying all preparation and
physical costs. An arbitrary-section or different-endpoint theorem requires
fresh geometry; the present N, phase and reflection domain must not be dropped.
