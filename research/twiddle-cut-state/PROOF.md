# Exact state complexity at physical twiddle cuts

This is an author-written proof for arbitrary finite parameters. Independent human and formal proof-kernel review are unclaimed. The executable uses explicit finite limits and corroborates the argument; it does not prove its unbounded quantifiers.

## The source function and the reader contract

Let ell>=2, 1<=K<ell, and let D>=1 axes have lengths ell or ell-1 bits. In round 0<=h<ell let I be the participating axes, d=|I|, and write

    beta_i = x_(i,h),   k_i = sum_(v<h) 2^v x_(i,v),
    S = sum_(i in I) beta_i k_i modulo 2^(h+1),
    E = -2^(ell-h) S modulo 2^(ell+1).

The pinned transform source, equation combined-twiddle and its named-slot argument, supplies this interpretation. Its physical layout extracts long-axis top bits, then low bit planes b-1,...,0, where b=(ell-1) mod K. It then orders the remaining width-K chunks by descending chunk and increasing axis. The pinned canonical circuit proof derives this same order and narrow modulus. Those two source texts are actual mathematical premises; circuit.py is the retained layout comparison oracle used by the replay. All are retained canonical-main inputs in SOURCES.json.

Consider a deterministic reader of this one physical address, from left to right once. It must eventually output the exact complete E, in either direction. At the specified cut, include in its state every input-dependent value that can affect its later behavior, including work-tape contents, head positions, finite control, and any readable early output. Require that no input-dependent information has escaped as irrevocable early output before the cut. A producer that writes the header after reading the address satisfies this condition. A write-only early-output protocol is a different contract. Rereading the prefix, supplying a prefix-dependent program, randomized error, and interaction with a consumer are also outside this model. Immutable shape information does not distinguish prefixes of the same shape.

For a fixed shape and cut, associate each prefix with its exact function of the remaining suffix. Distinct such functions must reach distinct states: if two prefixes reached one state, the identical suffix would produce identical output, contradicting a suffix on which their functions differ. Conversely these functions themselves are equivalence-class labels, so their number is the exact minimum number of distinguishable states *at this cut*. This converse is an abstract state-count statement. It gives no efficient transition encoding, tape implementation, or total-machine memory upper bound. The bit lower bound is ceil(log2 N), equivalently bit_length(N-1).

Multiplication by 2^(ell-h) is injective from residues modulo 2^(h+1) to its image modulo 2^(ell+1); negation is a bijection. Counting residual S functions therefore counts residual E functions for both directions.

## Canonical cuts, including the extracted low prefix

There is a canonical cut for every round.

- At h=ell-1, cut just after the extracted long-axis top bits. Only long axes participate. All their lower bits remain unread. Use effective parameters a=0,t=h.
- At h<b, cut just after prefix bit plane h. All lower participating bits remain unread. Use a=0,t=h.
- At b<=h<ell-1, cut after the whole group of D width-K chunks containing h. Put t=b+K floor((h-b)/K) and a=b. The prefix already contains bits 0,...,a-1, and the containing chunk and earlier chunks contain t,...,h-1. Exactly bits a,...,t-1 are unread and relevant. Bits above h are irrelevant to this round.

These are literal cuts in the source's MSB-first physical order, for mixed long/short axes as well as homogeneous shapes. They do not assume that named low bits are physically late. In the third case with m long axes, the prefix extent is

    m + D*b + D*K*((ell-1-t)/K).

The quotient is an integer. In the second case its extent is m+D*(b-h); in the first it is m. source_cut implements these extents. The remaining unrelated slots do not change residual-function counts because every relevant suffix assignment extends to a complete suffix.

If h=0 or d=0, the function is identically zero and N=1. If t=a and h>0, no relevant bit remains unread. Each axis term beta_i*k_i ranges over every integer in [0,2^h-1], so their sums fill [0,d*(2^h-1)] before reduction. Thus

    N = min(2^(h+1), d*(2^h-1)+1)                 when t=a.

This includes a final chunk that has consumed every relevant slot. Branch vectors then cease to distinguish residual functions.

## Exact count when a<t

Assume d>=1 and 0<=a<t<=h. Put

    R=2^a,  L=2^t,  M=2^(h-t),  H=2^(h+1)=2LM.

For a fixed prefix, write the unread bits of axis i as u_i in [0,L/R-1]. The prefix determines beta=(beta_1,...,beta_d) and a constant C, and its residual function is

    C + R * sum_i beta_i*u_i modulo H.

Different pairs (beta,C) yield different functions. Set every u_i to zero to distinguish unequal C. For equal C and unequal beta, set one differing u_i to 1 and the others to zero. This changes the outputs by R, which is nonzero modulo H. Here a<t is essential because u_i=1 must be available.

For a fixed beta of Hamming weight j, every active axis contributes to C an independent member of

    T = {s + L*z : 0<=s<R, 0<=z<M}.

Inactive axes contribute zero. Each prefix slot is free, so every such choice is reachable, including arbitrary independent active branch bits. The possible unreduced sums are precisely the intervals

    [L*z, L*z + j*(R-1)]   for z=0,...,j*(M-1).

This follows because the sums of j integer intervals [0,R-1] and [0,M-1] fill [0,j*(R-1)] and [0,j*(M-1)], respectively, and the low and high choices are independent. Define A_j=j*(R-1).

If A_j<L-1, these intervals lie within separate stride-L bands. Reducing modulo H identifies z only modulo 2M. The consecutive z range meets exactly min(2M,j*(M-1)+1) such bands, each containing A_j+1 residues. If A_j>=L-1, consecutive intervals touch or overlap and their union is the full integer interval from zero to j*((M-1)*L+R-1). Its reduction has the lesser of H and that endpoint plus one residues. Hence the exact number of constants for a fixed weight-j branch vector is

    c_j = min(2M, j*(M-1)+1) * (j*(R-1)+1),    if j*(R-1)<L-1;
          min(H, j*((M-1)*L+R-1)+1),             otherwise.

The formula includes j=0. Distinguishability of (beta,C), reachability of every counted constant, and the binomial number of weight-j vectors give the exact answer

    N(d,h,a,t) = sum_(j=0)^d binom(d,j) c_j.      (a<t)

This is a finite closed sum with d+1 terms, not a search over addresses. Together with the degenerate cases above, it classifies every canonical source cut.

## A simpler sharp form without extracted low bits

When a=0 and 1<=t<=h, R=1. If M=1 then every c_j=1 and N=2^d. If M>=2, the weights j=0,1,2,>=3 give respectively 1,M,2M-1,2M constants. Therefore

    N = 1 + d*M + binom(d,2)*(2M-1)
        + (2^d-1-d-binom(d,2))*2M.

Consequently the exact cut-state bit requirement is

    d,                  if h=t;
    h-t+1,              if h>t and d=1;
    h-t+2,              if h>t and d=2;
    d+h-t+1,            if h>t and d>=3.

For the last line, N<2^(d+1)*M because not all branch vectors have 2M constants. For d=3, N=11M-2>8M. Writing N_d for the closed form gives N_(d+1)-2N_d=(d+1)M-1+d(d-3)/2>0 for d>=3, so N_d>2^d*M follows inductively. This proves the ceiling exactly, including power-of-two boundaries. The d=1 and d=2 cases give N=M+1 and N=4M directly.

## Why the physical low prefix matters

For ell=6,K=2, one long and one short axis, and h=4, the source order is

    (0,5),(0,0),(1,0); (0,4),(0,3),(1,4),(1,3); (0,2),(0,1),(1,2),(1,1).

The cut after the first chunk group has d=2,a=1,t=3. Its c_0,c_1,c_2 are 1,4,9, so N=18 and five state bits are necessary. Pretending the extracted low bits were still unread gives only eight states. Keeping only the branch vector gives only four states. Both simplifications lose distinguishable suffix functions.

A larger actual mixed shape has ell=8,K=3, twelve axes with three long and nine short, and h=5. The cut after the first group has a=1,t=4,d=12. The formula gives N=114439 and seventeen state bits, whereas the final S accumulator has only six bits. For j<=12 the disjoint-band formula applies, with c_0=1,c_1=4,c_2=9 and c_j=4(j+1) for j>=3. Summing gives 4*2^12*(12/2+1)-3-4*12-3*binom(12,2)=114439. This is an exact theorem instance, not a fully enumerated large physical replay.

These bounds include all input-dependent state, not just a named accumulator. They do not rule out O(d+h) memory, a reader that rereads its address, a compact tape program, or any existing supplier. In particular PR3550's supplied-program machine is outside the read-once contract. No defect is alleged in the source's polynomial fixed-tape computation, which never promised a tiny read-once state.

## Evidence and remaining boundary

RESULT.json records exhaustive suffix-function counts from the literal source exponent on every address in each admitted small physical fixture. The independent physical-slot construction is compared with authenticated circuit.py. Separate literal modular Minkowski sums test both interval regimes, including touching bands, wraparound and empty terms. Wide exact-integer checks corroborate the simplified count and sharp bit formula. Optimized CLI controls reject lost low-prefix information, lost binomial multiplicity, a missing constant endpoint, a wrong ceiling, a wrong physical cut, source corruption/absence and a changed receipt.

This result is a lower bound and exact abstract state classification. It implements no address producer or consumer, supplies no physical transition/storage tariff, and avoids no restoration work. Program compilation, address enumeration, signed packet/layer joins, dirty workspace, spectators, head movement, complete physical caller, native/root/ordinary refinement, outer recovery and supplier admission remain open. No kappa or selected-frontier change follows. A future implementation must retain or reread the classified information and pay its complete costs. This package does not expand into that construction round.
