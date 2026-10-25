# Exact borrowed-dirty restoration repays the rectangular saving

This package tests one reversible-computation repair of PR3985's storage
obligation. It removes the need for 112 additional exclusively owned
full-cover temporary arrays, but the fixed-query-frame implementation costs
976 H1 in the complete decoder. That exceeds the conditional 553-H1 screen
of PR3976. One bounded pivot costs 352 H1 and is dominated in native and
additional-owned storage counts by the original 336-H1 PR2707 decoder.
Neither construction improves the known full-recovery implementation.
This is a scoped stop, not an ancilla lower bound or a global impossibility.

## Source boundary and changed ownership contract

The canonical PR2707 word, credited to ywz65 and Arham Tahir's PR2681,
recovers all 224 original x0/y0 outputs in F17 from 224 borrowed current X/Y
arrays. PR3985 replaces its future-logger block with a rectangular correction:
104 query ports J=U union T are read, and eight disjoint A ports are changed.
That 224-H1 full decoder uses 112 additional owned arrays, initially arbitrary
and cleared on entry/exit. We retain its precise rectangular operator.

Write A_p=C_qp^(-1) M_p, including the actual affine map translation, so
A_p F17=F16 D_p. Here F16 is the coordinate product on axes 9 through 24;
D_p is the ordered owner action. At entry W_p has logical u_p in F17. Define

    q_k = sum_(p in J) R[k,p] D_p u_p,
    L_p(q) = sum_k R[k,p] q_k/4.

The required update is W_p <- W_p - D_p^(-1)L_p(q), for p in A, with every
J output unchanged. Query/response support disjointness permits uncomputing
q after changing A. No commutation of distinct owner actions is assumed.

We borrow eight full-cover banks Q_k and one S, each with arbitrary independent
content and entry frame F16. They may be changed temporarily but must return
with exactly their original content and frame. They are distinct from current
X/Y, all output W/Z arrays, and private scratch. These nine auxiliaries are mutable borrowed workspace; the original224 current
X/Y inputs remain frozen. None of the nine may be cleared. This is
an explicit local availability premise; no actual global provider of these
nine banks, their alignment, their ranges or physical access is established.
Private scratch inside unchanged source blocks remains owned and paid under
the inherited contract, with peak 16. The change removes the 112 D arrays,
not every owned or private resource in the complete decoder.

## A dirty query increment with fixed query-source frames

Suppose S contains arbitrary s in F16 and W_p stays in F17. To increment
Q_k by R[k,p]D_p u_p, execute the following for all nonzero R[k,p]:

1. Q_k -= R[k,p] S.
2. Apply A_p^(-1) to S, then S += W_p, then A_p to S.
3. Q_k += R[k,p] S.
4. Apply A_p^(-1) to S, then S -= W_p, then A_p to S.

The two Q updates cancel the old s. At the second update S has logical
s+D_p u_p in F16. Its last three operations return it to s in F16. W_p
is never a destination. All additions occur in equal full phase frames.
There are four native lines and four full-cover maps per query port.
Replacing both Q-update signs reverses the query increment while again
restoring S. Query compute and uncompute therefore cost 8*104=832 H1.

This is the reversible dirty-ancilla principle specialized to the literal
routed native operators: an unknown workspace contribution is subtracted
before computation and added after it, then the workspace computation is
undone. The compensation and both inverse paths are paid explicitly.

## Paired dirty responses

For each response port p, a response visit with sign t does:

    S += L_p(Q); A_p^(-1) S; W_p += t S; A_p S; S -= L_p(Q).

It returns S and changes W_p by t D_p^(-1)(s+L_p(Q)). Each visit costs two
native lines and two maps. Execute a positive visit for all eight A ports
before computing q, and a negative visit for all A after Q has become Q+q.
Their difference is exactly -D_p^(-1)L_p(q): both the arbitrary S dirt and
arbitrary original Q dirt cancel. Then uncompute q using the unchanged J
sources. This restores every Q and S content and frame. The 16 visits cost
32 H1. No private query accumulator survives across native recursion; Q/S
are explicitly borrowed full-cover resources throughout.

The future block thus costs 832+32=864 H1. The unchanged prefix and F0
inverse suffix contribute 112, for **976 complete-decoder H1**. The frozen
WORDS and RESULT give every event and the full map/wrapper/scalar invoice.
No borrowed CLEAR appears anywhere in the replacement block.

Its complete invoice is976 H1,1952 wrappers,1104 cover maps,3488 unit ADDs,
992 quarter ADDs and296 owned/private CLEARs:40400 scalar allowance under
the source tariff8/unit ADD,12/quarter ADD,2/CLEAR. The pivot below costs
352 H1,704 wrappers,480 maps,2240 unit ADDs,992 quarter ADDs and296 CLEARs,
for30416 scalar allowance. Maps and wrappers still need physical tariffs.

## Bounded pivot and comparison with the original decoder

The fixed-frame query preservation premise is stronger than requiring the
owned outputs to be correct at return. In one bounded pivot, align each of
the 104 query W arrays in place, add its contribution to Q, and retain that
aligned frame until Q is uncomputed. Then return W to F17. This pays only
two native lines/maps per query port, or 208, while the same paired responses
cost 32. Its complete decoder costs **352 H1** and restores all nine borrowed
arrays. It never changes the final output contract.

This is not promoted as a new improvement: the original canonical PR2707
already costs 336 H1 and needs no additional owned D arrays. The pivot adds
16 native calls and nine borrowed banks. The primary checker preserves the
original as an explicit comparator. The 976-H1 failure is restricted to the
literal fixed-query-frame dirty-copy strategy, not all dirty-workspace
strategies. The 352-H1 result supplies no optimality or storage lower bound.
A separate parallel dead-output aliasing construction is outside this package
and is neither an executable nor a scientific dependency.

## Verification and native scope

Canonical inputs are authenticated before inherited code executes. The
canonical source word is regenerated. Each proposed complete word is checked
on 224 independent original inputs forwarded through F0/B1 and on 224
independent current X/Y symbols against the source's ordered inverse formula.
The nine borrowed dirt symbols are independent in both executions. The
intermediate inverse-B1 checkpoint and all final outputs/frames are checked;
all borrowed X/Y and Q/S content and phase frames must return exactly.

Repeated scratch use would accumulate redundant phase terms. The interpreter
merges identical parity vectors modulo4, drops zero terms and checks equality
of the entire phase polynomial before and after each compaction. This is an
exact representation reduction; the frozen words and their operations do not
change. The interpreter adapts PR2707's exact routed algebra and complete modulo-four
phase comparisons on all 73 coordinates. Signed native kernels are checked
for both signs on all 512 local columns for all 112 ports; every new native
occurrence is bound to one checked signed recipe. The114688 column tests check
the recipe basis; they are not976 independently new native kernel proofs. This is credited reuse,
not a code-disjoint proof of the inherited primitives. The source native
identities and tensor extension give the same conditional arbitrary-array,
positive-tensor-length interpretation as the predecessor. No finite replay
is claimed to establish physical routing, recursive tariffs or precision.

Controls omit the old-dirt response, query uncompute, scratch subtraction,
affine payload shift, or correct response sign, and attempt an illegal CLEAR
of a borrowed query bank. They must fail. For a concrete dirty witness, take Q0=constant1, all other Q/S and all J
inputs zero. Omitting the first response leaves future W0=-1/4 even though
the desired query is zero; owner permutations fix constants. RESULT pins
that port and coefficient. These controls distinguish a truly
restored dirty workspace from a computation that happened to start clean.

## Budget decision and reopening condition

PR3976's retained exact receipt gives a 553-H1 native-only cap for one proposed
module at each first-B1 cut (16 sites per 144 calls), under unchanged W=896/9,
centre64 and ideal rank51 remainder completion. This package reuses that
conditional screen, rather than deriving a new moment or assuming actual
consumer admission. The fixed-frame word exceeds it by **423 H1**, with all
physical costs still favorably ignored. The cheaper pivot's native count is
below that cap but is dominated by the original decoder; passing a screening
cap would not pay its placement or establish a new supplier.

Stop this exact borrowed-dirty substitution. Reopen only with a named native
or scalar cancellation, genuinely available workspace, and a complete
restoration contract that changes this comparison. Dirty ranges and rounded
cancellation errors need new bounds; exact cancellation does not authorize
transferring an earlier precision guarantee. The actual global provider
remains gauge44, and no new kappa, family coverage or centre credit is claimed.

## Credit

The reversible compute/uncompute and dirty-baseline subtraction idea is
standard reversible linear algebra; the new contribution is its source-pinned
QQ16 native realization, complete restored-state checks and failed cost
comparison. Credit ywz65 PR2707; Arham Tahir PR2681; Ali Romman and the retained
QQ16/native/geometry lineage; PR3985's rectangular cut and owned-copy result;
and PR3976's conditional incidence/cap. New work Chris R / Clear1nsight with
substantial OpenAI Codex assistance, Apache-2.0. Source notices are preserved.
