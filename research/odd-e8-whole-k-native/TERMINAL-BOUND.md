# A scoped terminal support bound for distinct fresh fitting codes

This lemma concerns one coded terminal cohort and a fixed finite ordinary
decoder. It is not a lower bound for all callers or all ordinary algorithms.
It applies to the old real orthogonal normalizers as well as the new
characteristic-perpendicular simple-transvection gauges.

Let e be the central unit vector, Q its positive C gate, and let the fresh
stage coordinate blocks be disjoint and orthogonal. Put D equal to the
product of their positive coordinate Gaussians, and G=DQ, on n=1+d axes.
At stage s, a real signed linear monomial L_i,s=P_(G_i,s) Z_(h_i,s), with
binary G_i,s^T G_i,s=I, centralizes that stage's full Gaussian exactly and
has linear part sending e to the actual norm-one port q_i,s. It acts
only on the central axis and its own fresh block. Every scalar K edge
used at the earliest chronological stage obeys q_i,s dot q_j,s=0.
Signed affine variants are also covered if they have these same signed
pure-X Pauli-image and exact centralization properties. Merely being a
real orthogonal permutation of the whole address space is insufficient.

Each stage code has owner block

    C_s[i,j] = K_s[i,j] L_i,s^-1 L_j,s.

At positive field width f the owner scalar K_s[i,j] is applied once and
the address monomial is tensor-lifted f times. Expanding a finite codeword
B=C_last ... C_first gives finitely many owner/address paths c M. Every
c is a product of actual owner coefficients, never a tensor-powered c^f.
Every address path M is a real orthogonal monomial commuting with G:
each local normalizer centralizes its own D_s Q and fixes the other fresh
blocks, so it centralizes their total product DQ exactly.

Write A for the linear part of the first chronological path factor
L_i,s^-1 L_j,s. Orthogonality gives

    e dot A e = q_i,s dot q_j,s = 0,       (A e) dot (A e) = 1.

Thus the first factor sends e to a norm-one vector entirely in its fresh
block. Every later distinct-fresh factor fixes this vector and its Pauli
sign. Consequently every full path satisfies

    M X_e M^-1 = (-1)^epsilon X_v,
    v dot e=0,  v dot v=1.

This argument uses neither a special choice of normalizer nor a universal
braid relation. In the new simple-transvection gauge one additionally has
v=q_(initial owner,first stage) and epsilon equal to that owner's explicit
normalizer sign. The support lemma does not require this stronger formula.

For bare coordinate C gates, conjugating C_e^-1 by this signed Pauli image
gives the exact identity, including absolute scalar phase,

    M Q^-1 M^-1 = i^(-epsilon) C_{-(-1)^epsilon}(v).

Here C_+(v)=((1+i)I+(1-i)X_v)/2, and C_-(v)=C_+(v)^-1.
Indeed a negative Pauli image gives C_-(-X_v)=-i C_+(X_v).
Using D=GQ^-1 and exact commutation of M with G,

    Q^-1 M D
      = i^(-epsilon) G C_-(e) C_{-(-1)^epsilon}(v) M.

The two norm-one directions e and v are orthogonal. Both signs of a C gate
have the same symplectic tableau. The X block of the displayed Gaussian
part is I+ee^T+vv^T; its kernel is exactly span(e,v), so its Gaussian rank
is n-2=d-1. The remaining M is monomial and does not change row support.
At width f its row support is exactly 2^((d-1)f). The absolute phase lifts
as i^(-epsilon f).

Therefore a B expansion with T terms has, for its physical negative
terminal Q^-1 B D, row support at most T*2^((d-1)f). Scalar cancellations
can reduce this support. The lemma does not identify the coded sum with
an autonomous rank-(d-1) Gaussian job.

A fixed finite ordinary linear template made of owner scalar operations,
address monomial maps, and A ADD instructions can at most multiply the
expanded monomial-path count by 2^A. Such left/right adapters cannot turn
this single cohort into an autonomous Gaussian of larger fixed rank as
f tends to infinity. More generally the same conclusion holds if the
total expanded monomial-term count is T(f)=2^o(f). Subexponential *operation
count* alone is not enough: O(f) ADDs may already create exponentially
many expanded paths. Arbitrary nonlinear ordinary algorithms are outside
this statement.

There is also an approximation version within this same decoder grammar.
A rank-r Gaussian target row has 2^(rf) entries of equal squared magnitude
2^(-rf). If the decoded row has at most S nonzero entries, its Euclidean
error from that target row is at least sqrt(max(0,1-S/2^(rf))), regardless
of the coefficients chosen on the S entries. With
S<=T*2^((d-1)f+A), row error at most delta<1 therefore requires

    A >= (r-d+1) f - log2(T) + log2(1-delta^2).

Recovering two missing ranks requires at least 2f-O(1) whole-field ADDs,
even for fixed nontrivial accuracy. This is a whole-field linear decoder
operation bound. It does not by itself prove a general TM time lower
bound or settle alternative subfield, mixed-cohort or nonlinear schemes.

An optional postdecoder B^-1 has the same conclusion. For the actual
whole K, every C_s is real orthogonal, so B^-1=B^T. Its path coefficients
are the original real coefficients, while its address paths are M_a^-1.
The term M_a^-1 Q^-1 M_b D has, after moving the total G, two removed
directions

    u=M_a^-1 e,        v=M_a^-1 M_b e.

Their dot product is e dot M_b e=0 and both have norm one. Its two
conjugation phases are retained separately; the total one-copy phase is
-epsilon_(M_a^-1)-epsilon_(M_a^-1 M_b) modulo four. The scalar multiplier
is c_a c_b, applied once at every f. If a different scalar code is merely
invertible, its inverse coefficients must be computed rather than copied;
its inverse support is not automatically fitting. The single-path proof
above already covers any fixed ordinary inverse adapter and avoids that
extra assumption. If the earliest code stage itself uses an inverse,
that inverse's actual nonzero support must satisfy the fitting premise.
Whole K is an involution, so its inverse has precisely its original
fitting support.

The actual test enumerates all nonzero base-eight-cube coefficient paths
at one, two and three fresh stages in both central-line orbits, represented
by original vectors 52 and 199. These give 1,344 signed-tableau and rank
checks at n=9,17,25. It retains every path's coefficient, linear map,
linear sign, removed directions and scalar phase in TERMINAL-PATHS.json.gz.
For every one-stage path it also checks three full sparse columns,
including the zero column, independently with Gaussian-integer arithmetic:
192 absolute-phase comparisons. TERMINAL-RESULT.json is the read-only receipt.
These finite checks corroborate the displayed generic proof; they do not
replace its all-width argument.

The published verifier also binds the premise directly to all 38,912
nonzero scalar edges and 512 normalizers in the committed 25-dimensional
K-PROGRAM, including 12,800 weight-mod-four sign coefficients. Its actual
811 distinct central images all have norm one and central bit zero. An
executed diagonal-edge control violates this property; omitting a required
normalizer sign violates exact full-Gaussian centralization. These checks
do not expand every multi-stage whole-K path. The generic proof handles
those paths from the verified edge and fresh-stage premises.

For a normalized target Gaussian of rank r>d-1, every row has 2^(r f)
entries of equal magnitude. A candidate linear decoder with at most
T*2^(A+(d-1)f) supported entries in that row therefore has row l2 error at
least

    sqrt(max(0, 1-T*2^(A-(r-d+1)f))).

Even a fixed error tolerance delta<1 thus requires
A >= (r-d+1)f-log2(T)+log2(1-delta^2). Recovering the original full rank
r=d+1 requires at least 2f-O(1) whole-field ADDs in this grammar. This
does not turn that ADD count into a complete Turing-machine lower bound,
and does not cover arbitrary nonlinear rounded algorithms.

Stage overlap changes a real premise. A later monomial may then move the
first fresh image back toward the central axis. But overlapping stages
can also change the Gaussian target rank, invalidate commuting-fresh
factorization, or make an old IDLE require new work. An experiment on
that changed premise must bind the actual chronological stage product,
all IDLE implementations and the complete productive Gaussian profile.
Recovered central rank alone is not a paid construction. Mixed-cohort
decoding, arbitrary ordinary algorithms and such changed-stage protocols
remain outside this lemma.

## Caller source, predecessor credit and the next changed premise

The negative endpoint is the operator Q^-1 B_i D_i derived in the
"Complete typed coded caller" section of the pinned canonical
[GAUGE.md](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/coded-native-caller/GAUGE.md).
This is a specialization gate for that named endpoint, not a new replay
of its complete FULL/IDLE caller. Whole K is an involution, so an inverse
K stage retains its fitting support. An arbitrary fitting scalar matrix
need not have a fitting inverse.

The signed orthogonal normalizers and their phase convention are retained
from Dugongue and Dillon Amburgey's coded-native work, including
[PHYSICAL.md](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/coded-native-caller/PHYSICAL.md).
Credit Ali Romman's odd-E8 family, Cao Yifan's native construction and the
native/Clifford/compiler lineage already credited by this package. The
support-counting method has predecessors in the coupled-tail support floor
and terminal papers [#5065](https://github.com/CrocSwap/integer-mult-bounds/pull/5065),
[#5408](https://github.com/CrocSwap/integer-mult-bounds/pull/5408), and
[#5111](https://github.com/CrocSwap/integer-mult-bounds/pull/5111).
Those works lower-bound support or ADDs of prescribed postdecoders; this
appendix upper-bounds the support of the proper-K negative endpoint and
compares it to higher-rank Gaussian jobs. No new general support method or
global literature-priority claim is made.

For example, a same-stage product E=K(I-F_C)^-1 need not have fitting
support and is outside the transversality premise. A native readout before
the final Q^-1 or a changed paid query/caller can also change the problem.
Each requires an actual interface and complete cost; this appendix grants
none of these missing operations for free.

Prepared for THU New Media Research Center with substantial OpenAI Codex
assistance, including separate AI-worker proof/implementation reviews.
Apache-2.0. This is written mathematics with finite corroboration, not
formal-kernel or independent human acceptance. No new kappa is claimed.
