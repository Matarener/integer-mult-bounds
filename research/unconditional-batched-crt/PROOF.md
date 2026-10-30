# Complete outer composition

Author-submitted construction, 2026-10-19. This document collects the exact
algorithm, setup, rounding and costs, using the supporting arguments indexed
in README.md and AUDIT.md. It asserts an unconditional mathematical theorem;
independent acceptance or formal verification is not asserted. A passing
numerical ledger alone would not establish it.

The proposed exponent is

    kappa = .00173097911567079247276057.

All parameters below are fixed rational numbers. There is no parameter
depending on an unverified conjecture, RAM operation or unpriced oracle.

## Sizes, setup and elementary fallback

For n<4 use elementary multiplication. Otherwise put b=ceil(log2 n) and
nominal p=6b. Let T be the
power of two in [4n/b,8n/b), and choose a power-of-two axis count
d=Theta(p^epsilon), epsilon=1-10^-30. Split log2 T among d integer widths
ell or ell-1, assigning a maximal-width axis r=2^ell to axis0. Store axes
in order (d-1,...,0), so axis0 is the innermost, contiguous coordinate. Then

    V=Tp=Theta(n), ell=Theta(p^(1-epsilon)),
    d*ell=Theta(p), r=2^o(p).

Select distinct odd primes s_i just below t_i=2^(ell or ell-1), with
theta_i in [1/(4p^2),1/p^2]. The unconditional prime-counting estimate
and search argument in GAUSSIAN supply these eventually.
Their product S satisfies T/2<S<T and is coprime factor by factor.

All asymptotic inequalities invoked in the auxiliary constructions have
effective sufficient tests: minimum widths, room for reserved fields,
core divisibility, cutoff sizes and explicit rational or interval bounds.
If a required finite test fails, use elementary multiplication. The
proofs show these failures occur for only finitely many input lengths.
This gives one uniform algorithm; a non-effective prime-existence oracle
or an input-specific family of machines is not part of the construction.

All precomputation over a full one-axis range costs
d*2^O(ell)*poly(p)=2^o(p)=o(V). Local core/page computations have fixed
polynomial complexity and are amortized by complete superpolynomial
microbox payloads. Inputs to the established O(N log N) integer
multiplier have O(rp) or O(p) bits; it is independent of this construction.

## Address isomorphism

Let P_i=product_{j<i}s_j. The input digit coefficient indexed by
k=sum_i a_i P_i is sent to coordinates

    y_i = k P_i^-1 mod s_i.

This is the coefficient isomorphism from cyclic convolution of length S
to tensor cyclic convolution. The inverse is the unique k satisfying
k=P_i y_i mod s_i for every i; the homomorphism
on exponents sends k to (k P_i^-1 mod s_i)_i. It preserves addition
modulo S, independently of the mixed-radix notation used to enumerate k.

Increasing ordinary k is exactly the physical mixed-radix order with
axis0 fastest. Insert padded zeros in that order in one scan. Keep this
physical axis order throughout the CRT and scalar tensor operations.
The balanced CRT uses arbitrary-source controls, so it does not require
the older full axis reversal that placed every control before its target.
The maximal axis0 will be the polynomial suffix below. This is a choice
of notation and layout at input, not an uncharged permutation of data.

CRT implements this map and its inverse as padded-cube
permutations, using the balanced CRT tree and reversible conditional
rotation switches. Its target validity and globally valid source set are
preserved at the completed endpoint. Three conversions (two inputs and
the final coefficient array) have total cost

    O(V p^(1-a2) ell^2 polylog(p)),
    a2=.001733394791695384296.

This replaces the older O(Vd) implementation. A coordinate-bit gather
alone is not used as a substitute for these nonlinear modular shifts.

## Synthetic convolution without the old prefix-slot overhead

Use the normalized simultaneous butterfly H0=[[1,1],[1,-1]]/2 from
COMPLEX at each FFT level on the currently active
axis bits. Its constructor restores original address order after each
layer and borrows only complete unselected spectators. Thus no active
prefix slots are processed one at a time and no dK full-array overhead
from the older layout is retained. The last level may have fewer active
axes; the same bound, or the elementary bound at bounded width, applies.

Work over R=C[y]/(y^r+1), with scalar axis0 packed as the r
coefficients of a polynomial record. The normalized FFT has at most ell
levels. At each level the twiddles from different axes combine into one
recordwise multiplication by y^E. Compute E modulo2r with polynomial
encoded arithmetic once per polynomial record. Its r coefficients form
a superpolynomial payload, so this preparation is absorbed by a scan.
Multiplication by y^E is one cyclic split/merge plus the exact wrap signs.
After each completed contraction round, truncate once toward zero.

Forward transforms may retain their bit-reversed frequency order. The
opposite procedure reverses that exact order; pointwise products commute
with the common retained permutation. There is no separate global sort.
Each transform costs O(V ell d^(1-q) polylog(p)).

The exact signed Kronecker packing in upstream section06 computes each
normalized polynomial product in O(rp log(rp)). The signed centered-digit
recovery, wraps, shifts and component layout are part of this cost.
Over T/r records, this is O(V(ell+log p)). The cyclic-to-negacyclic twist
uses the diagonal y^k coefficient multiplier exp(pi i k/r); its inverse
undoes the wrap sign, so it gives normalized scalar cyclic convolution
(f*g)/T. There is no use of the new multiplier inside its own recurrence.

Explicitly, put M=T/r. After the two normalized forward transforms, form
their pointwise ring product divided by r, apply the opposite transform,
and multiply exactly by M. The identity

    M F_plus((F_minus f)(F_minus g)/r)=(f*g)/(rM)

follows from F_minus(f*g)=M(F_minus f)(F_minus g) and
F_plus F_minus=I/M. The final M shift has O(p) bits and costs one scan.
It can amplify numerical error by M<2^p, already allowed in the error
budget below. The twist is applied to both inputs and inverted on output;
its r-th power is -1, exactly canceling each negacyclic wrap sign.

## Chirp tables: eliminating another d-factor scan

The middle resampling transform has quadratic chirp

    a(x)=product_i exp(-pi i s_i x_i^2/t_i).

In exact notation the middle map is

    Q F_t u = conjugate(a) *pointwise
              [a *cyclic (conjugate(a) *pointwise u)] / T,
    (Qv)_x = v_(-s_i x_i)_i.

The coefficient of u_z on the right is T^-1 exp(2pi i sum_i s_i x_i z_i/t_i),
as required. Each t_i is even, so a is periodic on the target rectangle.

Do not regenerate this by scanning d descriptors at every scalar record.
Precompute each one-axis table to the common working precision, using
polynomial-time elementary numerical routines at each of its t_i entries.
All tables together have subexponential size and setup cost as above.
Their values have modulus at most1 after toward-zero component truncation.

Enumerate the tensor in lexicographic order. Cache the product for every
prefix of axes. On an odometer carry, recompute precisely the changed
suffix of those cached products, then emit the full product. No division
by a possibly zero rounded entry is used. If every radix is at least2,
the total number of recomputed factors per emitted record is bounded by
sum_{j>=0}(j+1)/2^j, a constant. In the actual radices it is smaller.

All t_i differ by at most a factor two. Store their tables and cached prefixes on sequential tapes in
axis order. The innermost table is scanned once and rewound per cycle;
an outer carry may traverse the corresponding full intervening pages to
reach its next table entry. If t_min=min(t_i), a carry across j axes
costs O(j*t_min*p) such travel and occurs at most O(T/t_min^j) times.
Summing j*t_min/t_min^j for j>=1 gives a uniform constant when t_min>=2.
This bounds table head travel by O(p) per coefficient on average,
including return and cleanup. Cached product updates use the
established O(p log p) multiplier and O(p) working words. Thus each
chirp or twist diagonal costs O(V polylog(p)), not O(Vd).

Each emitted chirp is obtained from at most d rounded factors and d
rounded products along its prefix chain; its pointwise error is
O(d 2^-P) at P working fractional bits. It does not accumulate through
the total number T of records. Applying the phases and the normalized
scalar convolution therefore realizes the permuted normalized Fourier
transform Q F_t with error at most 2^O(p)2^-P.

## Exact Gaussian and source-transform identity

For one axis, indices on u are periodic modulo s. Define the two maps by

    (S_gauss u)_k = alpha^-1 sum_(j in Z)
                    exp(-pi alpha^-2 (j-sk/t)^2) u_j,
    (T_gauss u)_k = sum_(j in Z)
                    exp(-pi alpha^2 (tj/s-k)^2) u_j.

Put q_j=floor(tj/s+1/2), beta_j=tj/s-q_j,
(Cv)_j=v_(q_j), (Du)_j=exp(pi alpha^2 beta_j^2)u_j,
(P_su)_j=u_(tj), and (P_tv)_k=v_(-sk). Thus N=C T_gauss D
has its principal diagonal term equal to one. The discarded diagonal
aliases and finite-band perturbations are charged in GAUSSIAN.md. These
definitions agree with upstream Section 07, but its old separation and
execution bounds are replaced by GAUSSIAN.md's proofs at theta=Theta(p^-2).

For one axis the Gaussian Poisson identity is
T_gauss P_s F_s=P_t F_t S_gauss. It holds for every positive alpha and
coprime s,t; the old lower bound on theta was used to establish an inverse
estimate, not this identity. The new narrow row-gap proof supplies that
inverse at theta=Theta(p^-2). With N=C T_gauss D,

    P_s F_s = D N^-1 C P_t F_t S_gauss.

For clarity, Poisson summation on the narrow Gaussian's j-sum gives
the kernel (alpha*t)^-1 sum_{m in Z}
exp(-pi*alpha^-2*(l+s*m/t)^2) exp(-2pi*i*s*k*m/t) at input residue l.
Expanding P_t F_t S_gauss and writing its target index as -m modulo t
gives the same absolutely convergent sum. The factor exp(-2pi*i*k*l)
is one for integer k,l. No inequality involving theta enters this identity.

Normalize the completed S_gauss and D N^-1 C factors by dyadic powers
of p so they are contractions. GAUSSIAN implements their
grouped tensor products, with unselected holes treated explicitly and
an accumulated compensating scale 2^gamma, gamma=O(d log p)=o(p).
The source transform is therefore R F_s, R=product P_si, with its
opposite-sign version R F_s^+ obtained by complex conjugation.

Reference truncation and coefficient rounding perturb the exact Gaussian
maps by exponentially small errors, with polynomial inverse bounds.
The finite-section/core corrections, shifted interior circuits, banded
boundary factors and restored sparse schedules all have the error and
online precision bounds proved in GAUSSIAN.md. Their completed normalized
maps are contractions on arbitrary numerical errors, including hole errors.
The uncompleted log amplification is o(p). There are polynomially many
levels/groups per coefficient. Allowing even the full array dimension in
all norm changes costs at most2^O(p), since T=2^Theta(p).

Consequently choose one fixed sufficiently large C and working precision
P=Cp plus the explicit o(p) guards. Increase the Gaussian truncation
bandwidth by the corresponding fixed constant. Every complete source
transform then has absolute coefficient error less than 2^-4p for
bounded disk inputs, at O(p) bits per scalar record. This includes the
chirp tables, synthetic transforms, normalized polynomial products and
the final exact scale2^gamma. No unknown numerical cancellation is used
to discard significant bits; keep signed O(p)-bit headroom throughout.

## Recovering the exact product

Read radix-2^b digits of the n-bit operands, pad to cyclic length S, and
scale by 2^-(b+2). Their entries have magnitude<1/4. Let u,v be the
resulting tensors after the CRT address map. Their exact source transforms
are U=RF_s u and V1=RF_s v. Because R is a multiplicative index
permutation, F_s^+ R=R^-1 F_s^+, whence

    (R F_s^+)(U*pointwise V1)=(u*cyclic v)/S^2.

The three computed transforms and one rounded pointwise product have
error at most a fixed multiple of2^-4p on these bounded inputs. They
stay well inside the unit disk. Multiply grid numerators exactly by
S^2*2^(2b+4). Since S<T<2^b eventually, the factor is<2^(4b+4).
For p=6b the resulting error tends to zero and is strictly<1/2 beyond
an effective fixed cutoff. Rounding each real part to the nearest integer
therefore recovers its unique exact convolution coefficient.

If Ndigits=ceil(n/b), then S>T/2>=2n/b>2Ndigits-2; cyclic wrap cannot
affect the ordinary product. Its coefficients satisfy
0<=c_j<=Ndigits(2^b-1)^2<2^(3b). Apply the inverse padded CRT permutation
to these fixed-width integer records. The carry recurrence
k0=0, dj=(cj+kj) mod2^b, k_{j+1}=floor((cj+kj)/2^b) has
0<=kj<Ndigits*2^b<2^(2b). A sequential carry scan and one reversal produce
exactly the promised 2n output bits, including leading zeros. These scans
and exact p-bit scale multiplications cost O(V polylog(p)).

## Paid powers and proposed conclusion

Let b_root=.001730979115670792472760579929302792893760378764,
q=b_root-10^-28, a_eff=(b_root+q)/2, beta=1-3*10^-30,
xi=epsilon(1+q)-3/32+10^-30, eta=10^-32. Use core exponent400 and halo48.
The costs, after dividing by V and omitting polylog(p), have powers

| Operation | power |
| --- | --- |
| synthetic transform layers | 1-epsilon*q |
| global coordinate routing | 1-a_eff |
| grouped Gaussian circuits | epsilon-q*beta |
| group coordinate routing | epsilon-a_eff*beta |
| group scans | epsilon-beta |
| Strassen boundary | epsilon-xi+29/32 |
| per-visit union movement | epsilon+1/2-xi |
| exact polynomial products | 1-epsilon |
| batched CRT | 1-a2+2(1-epsilon) |
| conservative halo arithmetic | epsilon+beta+144-400 |
| conservative halo metadata | epsilon+50-400 |
| cached scalar phases, pointwise products and recovery | 0 |

The exact rational ledger bounds every power strictly below1-kappa.
It also checks the stopped complex moment, room for complete spectators,
membership arithmetic, fractional-shift precision, core/halo separation
and all dimension gaps. The smallest listed cost slack is positive, so
every fixed logarithmic factor can be absorbed. Setup is o(V), and the
fixed finite initial range changes only the implicit constant.

The BIT construction supplies the already completed ordinary primitive;
CRT and COMPLEX discharge their calls to it; GAUSSIAN binds its conditioning,
compiler and sparse-window premises; the present composition fixes the
address isomorphism, scalar phases and exact recovery. Together these give
one fixed finite-tape multiplication machine with time
O(n(log n)^(1-kappa)), for the displayed kappa and every input length.
The source and validation boundaries of this written proof are in AUDIT.md.
