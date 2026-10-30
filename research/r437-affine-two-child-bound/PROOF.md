# Two serial affine children cannot reach the cheap R437 COPY repair

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.

## Contract and the genuinely changed premise

PR4014 excluded affine translations from its one-child dependency proof and
explicitly left unequal two-child widths open. Here translations are allowed
and two child widths are arbitrary. The new result concerns a **serial affine
source pullback**. It does not include general multi-role, address-masked Boolean
circuits covered by the earlier linear-address one-child theorem.

Let R=Z/q^w for an odd prime q and w>=1. Fix one physical prefix, fresh-row and
spectator fiber. Its two banks have n=64f address digits each, f>=1; the physical
tail is reflected. A forward affine map is x -> Lx+t with L invertible lower
triangular and t arbitrary in R^(2n). This grants every unit diagonal and every
translation, including translations supplied by fixed header digits, for free.
All schedule and coefficients are payload-independent. There are no additional
source payload channels, arbitrary-address readers or payload-controlled global
branches. The final operation on every arbitrary Boolean source F is exactly
one pullback F(Ax+t). Cloning a source or retaining dirty helpers is harmless
only when the output remains this single serial pullback; using masks to combine
differently routed copies changes the contract.

The standard reversed child W_a swaps coordinate i with 2n-1-i for 0<=i<a,
and fixes the others. Any serial circuit with two such completed children has
linear part

                     A = L W_a M W_b R,                 (1)

where L,M,R are invertible lower triangular. Arbitrary affine offsets disappear
from this identity. Conversely, correctness for all Boolean F forces equality
of the address maps: a delta source separates distinct source addresses. Thus
a translation cannot repair a wrong linear part on the full address cube.
This argument uses the whole map, not PR4014's single-address orbit invariant.

## The two-child preserved-flag lemma

Work over any commutative ring; all diagonal entries below are units. Suppose a
target T fixes the first and last N coordinates, has no couplings between those
coordinates and the middle block, and its middle block is not lower triangular.
If a,b<=N, equation (1) cannot equal T.

For a matrix X and a cut p, write NE_p(X)=X[0:p,p:d], d=2n. For invertible lower
triangular L,R,

       NE_p(LXR) = L[0:p,0:p] NE_p(X) R[p:d,p:d].          (2)

Consequently NE_p is zero before multiplication exactly when it is zero after.
Take p=max(a,b). The target has NE_p(T)=0 because p<=N. Set X=W_a M W_b.
If a>b, select rows of X corresponding to original M rows d-a..d-b-1 and columns of X
corresponding to the SAME original indices. W_a sends these rows into 0..a-1;
W_b leaves these columns unchanged. The columns are >p-1, since a<=N<n. Their
principal M block is triangular with unit diagonal, with only row reversal.
Thus NE_p(X) contains an invertible (a-b)-square minor. If b>a, use original
M indices a..b-1: W_a leaves these rows in the first p rows and W_b sends their
columns into the final b columns. Again a triangular unit minor of size b-a
appears. Hence NE_p(X) cannot vanish unless a=b=t. Only a lower bound on the
minor size is asserted; NE rank need not equal |a-b|.

Partition the coordinates as t, d-2t, t, and let J reverse t coordinates. Write

     M = [ A0  0  0 ]        W_t M W_t = [ JFJ  JE  JDJ ]
         [ B   C  0 ]                      [  0    C   BJ ]
         [ D   E  F ]                      [  0    0  JA0J].

The target has zero NE blocks at cuts t and d-t. By (2), X has the same zeros,
so D=E=B=0. Its middle diagonal block is C, which is lower triangular.
The middle block of LXR is exactly L_middle C R_middle: terms from the first
block vanish because R is lower triangular; terms from the last block vanish
because X's upper off-diagonal blocks are zero. This product is lower
triangular, contradicting the target. This proves the lemma without passing to
a residue field, division by nonunits, an enumeration of GL or a size limit.

## Actual all-class rank-seven target and the width bound

Let P be any of the nine literal rank-seven split projectors in the retained
R437 source. Its all-class GL64 contract includes a conjugate Q whose image is
the last seven head axes, 57..63. PR4014 records the source-bound construction:
a basis of im(P) followed by a basis of ker(P), then a basis permutation.
That split-projector premise and the all-GL64 quantifier are inherited inputs;
this package does not infer production admission from finite small-prime tests.

For an arbitrary diagonal ancestor-unit matrix H=diag(h_i) on the head, the required map is

 D_H(Q) = diag(H,I) [[I-Q,Q],[Q,I-Q]] diag(H^-1,I),

with physical tail reflected and all f columns included. It fixes the first
and last N=57f physical coordinates and swaps the central 7f head/tail pairs
with unit weights. Its middle block has nonzero entries above the diagonal.
The lemma forces p=max(a,b)>N=57f. There is a stronger constraint when
both children are proper, a,b<n. Reduce the linear maps modulo q. For the
central target, NE_p(T) has rank max(0,p-N) whenever p<n: exactly the p-N
active head rows present in that prefix have independent weighted tail columns.
The same unequal-width unit minor used above survives modulo q, so (2) gives

                  |a-b| <= rank NE_p(T) = p-N.

Hence min(a,b)=p-|a-b|>=N. If recursive widths are a=k_1 f,b=k_2 f with
positive integer ranks, then

           min(k_1,k_2)>=57, max(k_1,k_2)>=58,
                         k_1+k_2>=115.                  (3)

This is necessary, not a construction attaining115. For arbitrary positive
integer address widths the conclusion is a+b>=114f+1; it is wrong to infer
115f without the integer-rank premise. In particular7f+1f,7f+7f,42f+42f,
and58f+1f cannot realize this target in the serial affine domain. The
rank inequality explains why a single very large child plus a cheap child
also fails; this is stronger than merely requiring one child wider than57f.

## Quotient refinement: total width at least121f

There is a further necessary bound. We know a,b>=N. Factor W_a=W_N V_s and
W_b=V_t W_N, where s=a-N,t=b-N and V_s,V_t are outer reversed swaps wholly
inside the middle2r coordinates, r=7f. They commute with W_N. Partition M into
N,2r,N blocks. In X=W_a M W_b, the two outer target-zero cuts force its
cross blocks to vanish. Specifically those blocks are invertible permutation
multiples of the lower off-diagonal blocks B,D,E of M, so B=D=E=0.
The induced middle equation is therefore

          L_mid V_s C V_t R_mid = weighted W_r,

where all three non-permutation middle factors are lower triangular. Reduce
modulo q. In NE_r(V_s C V_t), the first s rows have rank at most s. Each
remaining top-half row comes from a top-half row of the lower-triangular C;
after V_t its right-half support lies within the t columns moved from the
first t positions. These rows have rank at most t. The target has rank r
across that cut, so s+t>=r. Consequently

                    a+b >= 2N+r =121f.                 (4)

With positive integer recursive ranks and proper widths k_i<=63, this gives
k_1+k_2>=121; the boundary pairs are58+63,59+62,60+61 and reversals. These are
necessary candidates, not asserted constructions. Without the proper-child
restriction a full-width child changes the admissibility question.
A separate F2 example with n=3,r=2,N=1 and two width2 children attains2N+r=4;
it prevents extrapolating the bound into a claim that all proper pairs fail.
The independently authored checker retains the literal factors.

An all-class implementation with a fixed pair of child widths must handle this
class. An adaptive implementation may choose a different pair for this class;
we have not established its density among actual GL64 classes or lifts. The
result neither excludes three or more children nor masked multi-role synthesis.

## Favorable complete-profile gate before construction

The retained current pooled profile from PR4010 is
{1:380160,2:400877,3:22176,4:26592,5:29376,6:17375,7:26496,14:1,42:403}.
It has W=28416, rank mass1808352, deficit64W-mass=10272, and2592 COPY calls.
The earlier unpooled OQ4 profile has the same mass; profiles are kept distinct.

Replacing the incumbent single rank-seven COPY by any fixed serial affine
pair satisfying (4) adds at least114 ranks per COPY. Even optimistically charging
one rank58 and one rank63 and assigning ZERO cost to all other new work gives

 M_min(c) = (sum_r n_r(r/64)^(1-c)
             +2592[(58/64)^(1-c)+(63/64)^(1-c)-(7/64)^(1-c)])/28416.

For c>=0 and child widths<64, every rank term of the replacement profile is
at least its c=0 value. Thus M_min(c)>=M_min(0)>1. For the intended0<=c<=1 regime, concavity and monotonicity of x^(1-c)
make58+63 the favorable proper integer pair among those satisfying(4).
The verifier computes the
exact value21915/18944 from the retained profile; rank mass becomes2103840,
exceeding64W by285216. A width>=64 cannot be a proper
smaller recursive child and cannot rescue this gate. Larger proper children
only increase the c=0 mass; for c>1 the simple profile monotonicity still gives
its own c=0 lower bound, so no optimizing-width claim is needed there.

If only a fraction theta of COPY calls incurs this minimum replacement and all
others optimistically retain rank7, a necessary zero-exponent condition is
 theta <10272/(2592*114)=107/3078. At positive c, writing
 Delta(c)=(58/64)^(1-c)+(63/64)^(1-c)-(7/64)^(1-c), the necessary condition is
 theta < [1-M_old(c)] / [(2592/28416)Delta(c)] when Delta(c)>0.
This is a **hypothetical fixed58+63 invoice**, not a proved achievable algorithm
or a frequency estimate; actual larger child choices require their own Delta.

Every real bill also includes affine/header preparation, admitted source
production, coefficient evaluation, clone/mask/ADD scans, source preservation,
child CALL/RETURN, output transfer, all dirty readers, reset, erasure and head
return. Whole-run visited backing counts output, helper, child, coefficient and
parking inventories; erasure does not refund visited cells. These nonnegative
terms and supplier stock/precision bounds are unresolved. Since even the zero
version fails for the fixed schedule, no physical implementation is warranted.

## A constructive masked translation escape, with its actual count

There is no affine impossibility claim for general circuits. For any linear T
on a finite address group, let D=im(T-I). The exact identity

 F(Tx) = XOR_{d in D} [ (T-I)x=d ] AND F(x+d)             (4)

holds for every Boolean F: exactly one mask is active. Thus translations plus
address masks implement the target with zero children. For the weighted split
swap above, T-I has free image rank7f: each swapped pair contributes one free
coordinate even with arbitrary unit weights. Therefore |D|=q^(7fw).
For translation-only branches with fixed translations, this count is minimal:
each branch can supply F(Tx) only where its translation equals (T-I)x, and every
displacement in D occurs. Arbitrary source delta functions rule out borrowing
one displacement's bit for another. This branch-count lower bound does not
apply to affine lower-triangular branch maps, which have different linear parts.

A direct realization uses one zeroed output and one translated temporary:
produce F(x+d), scan and mask-XOR into output, erase temporary, repeat. The
source is borrowed unchanged; arbitrary dirty helpers can remain untouched;
the output is then shared with the incumbent readers. For V physical bits this
literal full-scan realization performs |D| full mask-XOR scans, processes
|D|V mask/source positions and erases |D|V temporary bits, in addition to the
|D| translation-production invoices and final head/owner return. Source,
output and reusable temporary occupy3V payload cells excluding metadata,
translation scratch, child inventories and numerical/parking storage. It is
not an O(Vn) realization: the branch count is exponential in fw for fixed q.
No unproved physical tariff for a translation is supplied. Sparse or fused
routing could evade the full-scan accounting but must specify and price its
new mechanism. This exact positive control explains the serial scope boundary.

## Evidence and stopping decision

The checker enumerates complete small lower-unitriangular middle factors and
uses north-east rank tables, not just the proof's zero predicate, to exclude
membership in the target lower-triangular double coset. Additional randomized
unit-diagonal local-ring cases check the explicit unit minors and block lemma.
An exhaustive affine translation/mask replay checks (4), arbitrary source and
unchanged dirty helpers; missing masks, missing unit weights and a corrupted profile receipt are failure controls. An
independent bit-packed enumeration checks all64^3 F2 three-factor words, finds
16960 distinct outputs and excludes the middle swap. A literal two-full-width
child identity is a positive scope escape. F2 is an algebra control outside
odd-prime supplier admission; the written theorem covers the admitted rings.

Stop the fixed serial affine two-child route, including its7+1 candidate.
Retain masked circuits, three-child words and proven adaptive density as open
changed hypotheses. No improved kappa, encoded supplier, full physical caller,
formal-kernel proof or selected-frontier change is asserted.
