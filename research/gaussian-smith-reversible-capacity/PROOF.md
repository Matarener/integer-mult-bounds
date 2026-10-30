# Sharp clean capacity for reversible Gaussian overwrite

This contribution was produced by Nick Petalas. Apache-2.0.

## Contract and predecessor results

Let pi=1+i, R_P=Z[i]/(pi^P), N=2^n, and
F(x)=C tensor n times x over R_P, where C=[[i,1],[1,i]].
Both n and P are nonnegative integers. R_0 is the singleton ring.

Ali Romman's [PR #5821](https://github.com/CrocSwap/integer-mult-bounds/pull/5821),
head `c137f338117e8a88816ce254efe3b1494809711f`, proves the response-image
information formula

    D(n,P) = sum_(j=0)^n binom(n,j) max(P-2j,0).

It leaves reversible truncation and cleanup explicitly open in README question 4.
Its source is Dugongue's [PR #5815](https://github.com/CrocSwap/integer-mult-bounds/pull/5815),
head `f0fcda576df410dc15cd5b8183d4f74d284eba2b`, which supplies

    C = S diag(1,pi^2) T,
    T(a,b) = (a-i*b,b),    S(a,b) = (i*a,a+b).

These are cited predecessor results, not claims of this contribution. Their
tensor factors T_n and S_n are permutations of R_P^N. The diagonal factor at
label u is multiplication by pi^(2|u|). The new result below concerns a
destructive reversible interface, unlike the predecessor's source-preserving
array computation. No predecessor census, precision theorem or invoice is
replayed as the deliverable.

## Theorem

Consider any permutation on a public field R_P^N, c initially zero bits, and
an arbitrary finite borrowed dirty field B. For every x and every initial
dirty value b, require the final public field to equal F(x). All auxiliary
outputs must stay within those c bits and B. Allow arbitrary reversible
mixing, nonlinear operations, and changes to the dirty field.

The exact minimum c is

    K(n,P) = NP - D(n,P)
           = sum_(j=0)^n binom(n,j) min(2j,P).

A permutation attaining c=K can return B unchanged. This is a logical
reversible-encoding theorem, without a gate-count, running-time or tape claim.
The initially zero bits become retained output information. They are not
promised clean again at the end.

### Necessity, including arbitrary dirty workspace

Restrict the permutation to the allowed input slice where the c bits are zero.
There are 2^(NP)|B| distinct inputs in that slice. The required output field
has 2^D possibilities by the cited theorem. The remaining fields have at most
2^c|B| possibilities. Injectivity therefore requires

    2^(NP)|B| <= 2^D 2^c |B|,

and hence c>=NP-D. This argument permits the borrowed field to change. Requiring
its restoration cannot weaken the bound. It also permits an arbitrary finite
nonbinary B. Arbitrary initially unknown states do not supply clean capacity.

### Sufficiency by explicit permutation

Every element of R_P has a unique P-bit pi-adic representation

    z = sum_(t=0)^(P-1) d_t pi^t,    d_t in {0,1}.

Successive reduction modulo pi and exact division by pi prove uniqueness.
For a diagonal exponent 2|u|, put e=min(2|u|,P), q=P-e.
Write its P input bits as a q-bit low part l and an e-bit high part h.
Allocate e initially zero bits a. Apply the bit permutation

    (l,h,a) -> (a,l,h),

where the first e+q=P output bits are the public coordinate and the last e
bits are the auxiliary coordinate. When a=0, the public coordinate represents
pi^e*l modulo pi^P, exactly pi^(2|u|)*z. The high part h retains the lost
information. For arbitrary a, this remains a permutation, with literal inverse

    (a,l,h) -> (l,h,a).

If e=P, the entire public coordinate is swapped with its clean field. If e=0,
the step is the identity. Thus zero raw precision and zero tensor depth also
have valid endpoints.

First apply T_n to the public field. Apply these disjoint coordinate
permutations, using a total of sum_u min(2|u|,P)=K clean bits. Finally apply
S_n to the public field. Tensoring the cited factorization proves that a zero
auxiliary input gives F(x). Composition proves a permutation on every public
and auxiliary state, not just on the allowed zero slice. Leave B untouched.
To invert, apply S_n inverse, the inverse coordinate permutations, and T_n
inverse. This construction attains the lower bound.

## Consequences and scope

For normalized precision p with the predecessor's raw exponent P=p+n,

    K = sum_j binom(n,j) min(2j,p+n).

In particular, if p>=n, all exponents are unsaturated and

    K = sum_j binom(n,j) 2j = n 2^n.

At p=n>0, the sharp initially clean capacity is half the public raw input
bit count, since that input has 2n 2^n bits. The attaining auxiliary output
retains those n 2^n bits.

For n>0 and P>0, K>0. A reversible host cannot complete this overwrite and
reset all nonpublic fields while retaining only the rounded modular response.
If the c clean bits must finish zero, the output-count bound has factor one
in place of 2^c, and contradicts injectivity whenever K>0. Even allowing the
dirty field to change cannot repair that deficit.
Restoring the auxiliary to zero requires preserving or recovering additional
input information, changing the output contract, or permitting irreversible
erasure. An exact unrounded invertible response is a different contract.

The predecessor preserves the original source. That source already retains
the information lost by F, so this overwrite lower bound does not apply to
its source-preserving compute-copy-uncompute route. This result neither
invalidates that route nor prices its additional passes.

The all-size statement rests on this written argument and the cited Smith
and image theorems. The checker verifies new finite reversible augmentations,
including nonzero auxiliary states, inverse recovery, every individual lost
bit, and dirty-capacity inequalities. It does not reestablish the predecessor's
image theorem by counting its outputs. Physical reversible primitives, their
gate and tape costs, reusable clean restoration, the five selected framework
assumptions and any kappa improvement remain open here.
