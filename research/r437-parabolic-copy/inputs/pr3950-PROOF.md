# Uniform rank-seven COPY: a constructive reduction and its full relative bill

Chris R / Clear1nsight, with substantial OpenAI Codex assistance.

**Status.** The algebraic reduction below is uniform, including every local-ring
cover class. The caller and cost theorem is conditional on explicitly named
completed backends. It gives a larger, fully displayed relative bill. It does
**not** establish R437's inherited cheap rank-seven tariff, implement an encoded
physical compiler for the new schedule, or independently discharge the universal
C0/B1 source arguments. Those are substantive remaining obligations, not facts
inferred from the checks. Section 8 gives the resulting stopping decision.

The split-projector/common-chart argument is credited to alephnan/PR1627,
eumemic's GL local-ring lineage, and Jose Manuel/PR2234. The selected complete
caller is David Arias/PR2753 and Jose Manuel/PR2809; the ordinary backends and
fast-primitive composition are Jose Manuel/PR2899/2915. Generic conjugation and
Gaussian elimination are not claimed as new mathematics. This contribution
specializes and bills a fixed-support determinant-normalized reduction at the
actual R437 COPY boundary, including arbitrary dirt, weighted ancestors and
the reverse-order adapters that a rank-only argument would omit.

## 1. Quantified address and ownership domain

Fix one odd prime q and w>=1. Put R=Z/q^w and A=q^w. Source-admissible large
primes are required when importing the selected backend time/stock theorems;
the algebra alone works for every odd q. Let m=64, r=7, n=64f+delta,
f>=1 and 0<=delta<64. One complete selected low packet has shape

    [Z physical prefixes][U unused fresh rows]
    [B][A^n head][G][A^n tail][S],
    v = Z U B G S A^(2n).

Z,U,B,G,S are independent positive complete extents. In a parent invocation
Z=C H, H=q^(4096(w-1)). The prefixes retain **physical ordinals**, including
repeated or correlated field values; they are not a set of distinct headers.
Every incoming Boolean payload is arbitrary. In particular it may be the
complete dirty capture in PR3936, with input 340 present. No SOURCE/helper
projection, clean-input restriction or independence of payloads is allowed.

For each prefix and column j, let a_(i,j) be the incoming diagonal units.
They can depend on the source-bound ancestor program and j, but not on body
addresses or fresh unused rows. Let g be the complete invertible cover matrix
over R at that prefix. Let P be the rank-seven rational projector of the
literal capture, embedded into the first eight of m coordinates. Section 7
binds all nine projectors to the exact R437 input.

Write E=diag(I_7,0_57), Q=g P g^-1, H_j=diag(a_(0,j),...,a_(63,j)). In
reflected tail coordinates the requested address map is

    D(Q) = [[I-Q,Q],[Q,I-Q]],
    D_H(Q) = diag(H_j,I) D(Q) diag(H_j^-1,I).

The physical reflected tail sends the partner of head (i,j) to tail
(m-1-i,f-1-j), with the peeled delta and external G left in the middle.
Thus the central E map is exactly one **reversed** interchange of width 7f;
it is not an ordinary scalar swap on one representative address.

The output contract is: preserve borrowed source, program, directory and
Counts; return a distinct owned stream f_in composed with the complete
requested address permutation; preserve every spectator and physical prefix
ordinal pointwise; reset borrowed heads; restore owned scratch before reuse.
At the guarded ERASE the caller clears the owned output, charging that scan.
Successful execution is the contract. Interruption recovery is not asserted.

## 2. Kernel normalization removes diagonal scaling from the factor alphabet

The retained projectors have dyadic entries and satisfy P^2=P. Their rational
characteristic polynomials specialize to t^57(t-1)^7, so reduction modulo q
has rank seven even for q=7; trace modulo q is not a rank test. As in PR2234,
choose seven independent columns of P modulo q and 57 independent columns
of I-P. Lift those columns to R and concatenate them into B_P. Then

    P B_P = B_P E,   det(B_P) is a unit.

This follows because their residue-field image/kernel spaces are a direct
sum. Unit determinant over the local ring implies invertibility, and hence
P=B_P E B_P^-1. The same selected column labels work for every precision w
at this fixed prime. They are source/compiler data, not payload-dependent
advice. The proof does not require symmetry of Q or g^-1=g^T.

Set T=g B_P, S_h=H_j T and S_t=T. Both are invertible. For either S, multiply
its first kernel column (column 7, zero based) by det(S)^-1. Call the result
U. Thus U=S Z_S, det(U)=1 and Z_S changes only a kernel coordinate of E.
The two independent kernel scalings, on head and tail, commute with D(E):
D(E) fixes each of these kernel coordinates. Consequently

    K=diag(U_h,U_t),
    K D(E) K^-1 = D_H(Q).                                  (1)

Normalizing an image column independently on the two banks would generally
change the weighted swap. The unused kernel column is essential to (1).
This proves a complete matrix identity over R for every admitted g and all
unit ancestor weights. It uses neither a good-leading-minor assumption nor
an exceptional-class probability. Its new costs are billed below; this is
not permission to delete the original fallback charge from R437's invoice.

## 3. A fixed-support word of elementary shears

For U in SL_d(R), d>=2, the reference compiler emits exactly

    L_d = 3d(d-1)/2 + d(d-1) + 6(d-1)
        = (d-1)(5d+12)/2

elementary factors. Their ordered (target,source) pairs are independent of
U, q, w, the prefix and the column. Zero coefficients remain emitted and paid.

At Gaussian column j, the invertible remaining residue-field block has a
nonzero entry in that column, hence a unit pivot over R. Select its first
row k. For **every** candidate k>j emit

    E_(j,k)(s), E_(k,j)(-s), E_(j,k)(s),
    s=1 if k is selected, and 0 otherwise.

The selected triple is a signed row exchange, of determinant one; the other
triples are identities. Then emit one elimination shear for every i!=j,
including a zero shear if the entry is already zero. Previous diagonal
columns stay diagonal because the pivot row is zero in them. The reduction
G U=D is diagonal, and det(D)=1. This proves the first two terms of L_d.

For each i<d-1, the diagonal pair diag(b_i,b_i^-1) on (i,d-1) is six shears:
w(b_i) w(-1), where

    w(a)=E_(i,k)(a) E_(k,i)(-a^-1) E_(i,k)(a).

Their product gives D, since b_(d-1)=product_(i<d-1) b_i^-1. Reverse the
elimination factors and negate their coefficients to obtain U=G^-1 D.
This proves both correctness and the last term of L_d. `factor_sl` records
chronological **left** actions; `word_matrix` multiplies them in that order.
For pullbacks, the stream operation order is the reverse matrix factor order.
The inverse word is again formed by reversal and negation, not by reusing
the forward word. These conventions are part of the statement.

At d=64, L=10458. The two banks and both conjugation directions have 4L=41832
factor slots. The numerical coefficients can vary across columns, while their
support remains fixed. Therefore a caller can process one factor across all
f columns, recomputing its scalar from the authenticated header and encoded
column index. It need not keep f matrices or a data-sized operation trace.
All determinant, inverse and coefficient preparation remains charged work.

This is an algebra compiler and an effective finite-control construction
argument. The Python reference uses host integers for the exact ring algebra;
it is **not** an implementation of that encoded physical compiler.

## 4. Whole-packet caller, chronological restoration and fresh stock

Use this successful-call sequence on fixed owned roles:

1. Clone the complete borrowed source into an owned current stream.
2. Apply K^-1 to its addresses using the elementary factor word.
3. Invoke one complete reversed interchange on the first seven image blocks
   and their reflected tail partners.
4. Apply K, return its complete output into the private role, and release
   every intermediate after its last reader.
5. Keep that private output unchanged throughout the literal read-only COPY
   window. At the existing transported equality guard, clear it and reset
   its owned port before reuse.

The displayed sequence is address-vector order; its pullback implementation
uses the corresponding reversed factor schedule so its output is f_in
composed with K D(E) K^-1. Induction on completed source-preserving primitive
returns proves this for arbitrary functions. The source may itself be any
correlated XOR of earlier dirty inputs. Equation (1) then supplies exactly
the complete map required by PR3936; matrix rank alone would not suffice.

The central child is **outside** the prefix loop. Its three spectators are

    B'=B, G'=G A^(114f+2delta), S'=S,
    child width=7f, fresh rows=U, frozen physical prefixes=Z.

Their product with A^(14f) is exactly the original complete packet volume v.
The injection preserves each peeled atom and the external G, not just the
product of their cardinalities. The child receives the entire packet with
all Z prefixes. It cannot deduplicate equal header values or make Z separate
coarse calls. The requested child weight is one after conjugation; the caller
must bind that request and preserve its frozen program/directory context.
We do not assert that the present `SelectedBinding` has been replaced by this
new schedule or that an arbitrary reset of its source program is legal.

For the inherited compatible stock, let W=28416,
N=|GL64(F_q)|, H=q^(4096(w-1)), M=lcm(28416,28425)=269241600, K0=MNH and
D(n)=0 below 64, otherwise 1+D(42 floor(n/64)). A parent row count
t K0^D(n) gives U=t*9475*K0^(D(n)-1). Since 7f<=42f<n,
D(7f)<=D(n)-1; the required child divisor K0^D(7f) divides U. It is crucial
that U is a fresh row coordinate, not U*B or a cardinality reconstructed from
the transformed payload. Ordinary adapter interchanges below require their
own stock-free completed contract, rather than spending this U again.

Returned source identity, program identity, width, depth, complete prefix
count, three extents and successor label belong to the continuation contract.
The PR2809 fixed-role protocol parks and restores them before the parent
resumes. Its implementation and universal refinement remain dependencies;
we have not independently proved them by checking this matrix reduction.

## 5. The reverse-order adapters and a complete relative time inequality

Let b(v,u) bound a completed same-q **ordinary** interchange of two adjacent
or separated blocks of u atoms, preserving the full intervening spectator.
Its bit/radix width is u*w; B1/B2 have the conditional form

    b(v,u) <= C_B v (u w)^p + E_B,  p=1-a_B.

Let t(v,7f,w) bound the completed reversed central child on the exact stock
and shape above. Neither function is an oracle of zero cost. Both include
their numerical work, output, full restoration, and input-head returns.

A shear whose source is physically earlier than its target is a complete
ordered ADD pass, performed for each column with that column's generated
coefficient. For the reverse direction, first ordinary-interchange its two
**whole f-atom blocks**, perform the now-ordered column ADDs, then interchange
the blocks back. The block swaps preserve internal column order; they do not
replace the central reversed child. This costs two b(v,f) calls per reverse
factor. The coefficient depends only on saved prefix/index metadata, so it
can be evaluated after the payload block swap without reading changed body
values. Both ordinary calls act on the entire packet, with all Z prefixes.

Head and reflected-tail words have the same support but opposite physical
order. In each head/tail pair exactly L factor slots are reverse-order,
including zero coefficients. The inverse pair contributes another L. Thus
the complete paid schedule has

    one reversed child of width 7f;
    41832*f ordered scalar ADD passes;
    41832 ordinary block interchanges of width f;
    one initial complete clone and one final guarded disposal.

In addition there are at most 41832*f+41832+1 intermediate output releases,
one after each completed primitive. These are genuine scans. They fit the
linear term below and do not erase arbitrary borrowed state. This accounting
does not add a second reversed uncompute: the owned clone is transformed and
later cleared. Conversely it does not make any linear release free.

Let gamma be the total cost of evaluating the actual header/index-dependent
unit weights, determinant-normalized factor coefficients and projected Counts,
including all work erasure. Do not substitute a constant for gamma outside
its admitted domain. Complete ordered ADD, copying, rewinding, transfers and
disposal give the relative inequality

    C_COPY(v,n,w) <= t(v,7f,w)
       +41832*b(v,f) + C_q*v*(41832*f+41832+3) + gamma.       (2)

Source/directory production and owner gather/route/scatter occur in the outer
caller and are **additional**. They are not eliminated by (2). If they are
included in the definition of a complete requested episode, append their
actual producer and return charges to its right side. The existing same-q
ordinary backend has no binary-padding volume factor at this interface.

Equation (2) is a bound for all positive spectators, not a measured simulator
runtime. Under the imported canonical root/history coupling and polynomial
coefficient-preparation argument, gamma and Count setup can be absorbed into
the local C_q*v*(f+1) allowance. Without that argument retain gamma, E_B and
the actual encoded widths explicitly. This new package does not independently
re-prove the source callback's universal polynomial bound.

The resulting simplified **conditional** bound is

    C_COPY <= t(v,7f,w) +41832*C_B*v*(f*w)^p
                              +C'_q*v*(f+1).              (3)

All terms in (3) are present; there is no bad-class multiplier on the added
ordinary term. This is a different proposed implementation from the original
good/fallback construction and cannot inherit its invoice without a new proof.

## 6. Storage, exact arithmetic and successful cleanup

Let S_R,S_B,S_A denote each completed backend's maximum **owned** visited-cell
span, excluding its borrowed current input but including output, templates,
numerical work, markers and parking. Let M_coef be this reduction's numerical
and control storage, also including blank-but-visited backing. One conservative
full bound, including the original borrowed source and owned current stream, is

    S_COPY <= 2v + S_R(v,7f,w) + S_B(v,f*w) + S_A(v)
                  + M_coef + F_q.                         (4)

The backends execute sequentially, so their active contents can instead use
the maximum of their owned live-content bounds. For **visited physical cells**,
separate backend tape inventories are safely added as in (4). Replacing their
sum by a maximum needs a proved shared-pool realization; cleanup alone does
not unvisit tape cells. No factor f, Z or recursion depth multiplies their
sequential inventories. The factor scalars can be recomputed per header and
column using constant-size matrices; no length-f coefficient array is required.
If the backend reserve and metadata absorption premises give O_q(v)+F_q,
(4) has that same form, with a new constant. It does not establish a numerical
constant or fit the complete machine into nine reserved family packets.

All address arithmetic is exact in Z/q^w. Inverses are requested only for
units; P's dyadic denominators are units at odd q. Determinant normalization
and scalar elimination introduce no floating approximation or fractional-bit
rounding. Payloads remain Boolean. This local observation supplies no global
integer-product recovery, complex-side numerical, or interrupted-macro
restoration theorem. Borrowed data stay intact throughout successful calls;
owned work closes through the named backend contracts and explicit releases.

## 7. Source binding and finite checks

The retained word is PR3647 at a24f9ff95c12fd0b6792e3f710569237efd72db2,
as byte-bound in PR3936 commit 125f5afad680ef128e386fa58e76eef5fadaa5d6.
Its nine retained centres are 470..478. Replaying frame assignments through
sections D and A derives the actual capture frames 510..518. The new checker
reconstructs their projectors directly from the root rows; it imports no
predecessor executable. It checks 45 modular contexts over q=3,5,7,11,
including precision two, nonorthogonal high matrices and weighted ancestors.
A full ambient-64 case has a deliberately zero leading seven-by-seven minor
yet still compiles. This tests a case excluded by the usual leading-minor
good branch, without implying that the new physical tariff is cheap.

A complete 81-address small cube checks arbitrary Boolean data across repeated
physical-prefix labels and independent spectators. It is a function-model
check, not selected GL64 payload execution. The independent checker obtains
the rank-seven projectors from the one-dimensional rational nullspaces, rather
than the producer's orthogonal elimination, and independently counts the fixed
factor support and its physical order.

Normal/optimized equality and actual exported CLI source/result/missing/symlink
controls are separate from the algebra checks. They cannot turn an unimplemented
physical compiler or inherited source theorem into independent validation.
CI3936 was checked first: run 39202988286, plan and registered replay both
completed successfully, including its unchanged-input check. That CI replays
the earlier package, not this all-parameter proof.

## 8. Admission decision and smallest remaining task

The requested inherited cheap rank-seven bound is **not closed** by this route.
The extra term in (3) is not t(v,7f,w), and the rank label seven does not pay it.
For a diagnostic use the retained R437 scalar target
c_R=1736646042038446578551/10^24, the root scaling w approximately e^c_R,
and n approximately e. A claimed local allowance O(v*(n+w^p)) has leading
power v*e. The new ordinary term has power v*e^((1+c_R)*p).
For the pinned original B1 rate a1=(17/10000)(1-17/10000), and even the stronger
B2 rate a2=(17/10000)(1-(17/10000)^2), exact arithmetic gives

    (1+c_R)*(1-a1)-1 > 0,
    (1+c_R)*(1-a2)-1 > 0.

Thus those **available upper bounds** do not justify absorbing this term
into that allowance with an input-independent constant. This is not a lower
bound on actual runtime, not a counterexample to the original good/fallback
algorithm, and not an impossibility theorem for a different COPY realization.
It is a failed cost implication for this generic replacement schedule.

Continue only after binding a cheaper reverse adapter, sharing it inside an
actual child/consumer, or supplying an affordable different factorization.
Start with one nonzero reverse factor, its generated coefficient and the exact
source-preserving complete-packet interface. Preserve the full return, scratch,
preparation and disposal bill. Separately, independently review C0/B1's universal
source/refinement arguments before treating the conditional composition as a
physical supplier proof. No selected result or frontier is changed here.
