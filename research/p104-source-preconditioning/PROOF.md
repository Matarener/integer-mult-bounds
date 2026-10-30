# Source-preconditioner rank at the fixed P104 covers

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance,
including mathematical source-analysis agents. Apache-2.0.

## Statement and contract

I fix the PR1972/1991 P104 channel, its ordered 104 ports and original X/Y
frame paths. Write M=G/2 for its scalar source-to-target increment and
C=I-M. I use the PR2981 departure and arrival covers, and grant the complete
pool of 2,309 compatible endpoint pairs from PR3259. I retain arbitrary
independent helper dirt, unread targets and equal-frame linear transfers.
Each helper follows one increasing full flag. I grant source and target
snapshots without their original chronological restrictions.

I allow an invertible scalar source preconditioner U over Q, R or C before
the channel. It leaves X'=UX in the original source frames and leaves no
additional source-dependent state for the correction. During the channel
and correction, X' remains immutable. I permit source restoration afterward.
The correction may use the granted helper pool, but it may not read Y,
descend a helper, change a frame at fixed dimension or use other correlated
storage, including source-dependent intermediate values of the old channel's
helpers. These are the retained support-model hypotheses, not a claim about
every P104 program.

**Theorem.** If such a correction completes the original identity shear,
then rank(U-I)>=4. In particular, at least four rank-one updates are needed
in any factorization of U into matrices differing from identity by rank one.
I do not assert that rank four is sufficient.

For the narrower implementation class that realizes each source update
with its own charged H2 conversion, the retained optimistic 208-unit-helper
price already exceeds one at the selected complex saving. I exclude that
implementation class at that benchmark. I do not infer a tariff for an
arbitrary joint native realization from the matrix rank alone.

## Why the one-shear candidate was plausible

PR3259 certifies dcharb78's pooled one-hop cut: only C[71,102]=-1/2 is
missing among the 4,992 nonzero entries. Put E=e71 e102^T. Since E^2=0,

    U=I-E/2, V=U^-1=I+E/2, D=V-M=C+E/2.

Thus D has 4,991 nonzeros and passes that pooled necessary test. The
conditional identity is (M+D)U=I; I restore sources with V after their
last correction read. This algebra assumes a complete D corrector. It
does not construct one.

I verify a native implementation of the new source boundary. After applying
the source's Gram isometry, the physical masks of X71 and X102 are a=121
and b=296. The compressed masks 22 and 415 are not physical coordinates.
The required conversion is

    C_a C_b^-1 = (I-iX_a+iX_b+X_(a+b))/2.

Choose the binary chart Q whose columns begin with a,b and then complete
a basis. Its rows are (5,8,16,35,65,131,1,256,2). In execution order I use

    X_b; P_Q^-1; C_e0; C_e1; P_Q.

This is one H2 call with monomial wrappers. The image of a basis vector
has four nonzero entries, so a standalone monomial/C circuit needs total
C-rank at least two. I restrict that lower bound to this circuit grammar;
I do not include arbitrary linear-combination or fused preparations in it.

Before the intrinsic entry adapters, I COPY X102 to owned scratch, apply
the conversion, ADD it with coefficient -1/2 into X71, then CLEAR the
owned scratch. After the original entry adapters, I can use their inverse
and forward wrappers around the same bridge to obtain Gamma_71 Gamma_102^-1.
All final X source charts are the common FULL chart, so the final inverse
uses one scalar ADD(+1/2), with no extra positive child. I keep X' immutable
until the correction has finished reading it.

The signed Pauli action and exact phase determine the complete nine-axis
bridge. I also check all 512 basis columns and tensor depths 1,2,3. The
tensor lift uses one rank-2f child at depth f; the scalar coefficient remains
-1/2. The retained native operators and their all-size realization keep
their original proof scope.

The stronger support result below rules out the required D despite this
valid boundary. For example, D[3,2]=1/2 remains required and unreachable.

## Pooled path-compression lemma

I extend PR3252/3259's dependency-path and same-dimension compression arguments
to one virtual helper for the whole path, using the complete endpoint pool.

For departure label a, let L_a be its one-dimensional line and A_a its
two-dimensional departure plane. For arrival label b, let B_b be its
seven-dimensional arrival space and H_b its eight-dimensional cap. I grant
every pair (a,b) with A_a contained in B_b. A helper of that type has fixed
frames L_a,A_a,B_b,H_b at dimensions 1,2,7,8; between them it may follow
any nested flag.

Consider a nonzero source-to-target coefficient path. Source-dependent
helper initial values and target reads are absent, so the path starts at
a listed source snapshot V and ends at a listed target snapshot W. Along
the path, transports increase the actual frame and scalar edges preserve
it. Therefore V is contained in W. This argument orders frames along one
dependency path; it assumes no global dimension order for the program.

Write s=dim V and t=dim W. If s=t, then V=W and I grant the direct
equal-frame source-to-target contact. Otherwise 1<=s<t<=8.

If s>=2, take the departure a of the source-reading helper. If s=1,
take the first helper encountered at dimension two along the path. Fill
skipped dimensions with the actual full flags. The latter choice preserves
the source line: L_a=V. For s=2, A_a=V; for s>2, A_a is contained in V.

If t<=7, take the arrival b of the target-writing helper. If t=8, take
the last helper encountered at dimension seven before the final ascent
to dimension eight. The latter choice preserves the target cap: H_b=W.
For t=7, B_b=W; for t<7, W is contained in B_b.

The chosen departure and arrival cuts occur in the right order, since
max(2,s)<=min(7,t). Nestedness gives A_a contained in B_b, so the complete
pool contains the recombined pair (a,b). Its interval admits both V and W.
The prescribed endpoints together with V contained in W form a nested
partial flag. Extend bases between successive spaces to obtain one full
flag. One virtual helper can read at V and write at W in the untimed
relaxation.

Consequently I can test pooled support by the following exact criterion:

    V=W, or V contained in W and one compatible helper interval
    admits both V at dimension s and W at dimension t.

The reverse implication constructs only an untimed support path. It may
carry helper dirt into the target and need not belong to a simultaneous
matching. Pooling is essential: the recombined pair need not occur in any
chosen matching. Dimensions zero and nine cannot participate between a
positive-dimensional source read and a target write of dimension at most
eight.

## A four-column certificate

I check sources S=(0,1,2,3), all 104 target paths and all compatible helper
types using the criterion above. I obtain no support on the 16 entries
R by S, where R=(4,6,8,39). Since R and S are disjoint,

    M[R,S] = (1/2) [[1,-1, 0,1],
                    [0, 0, 1,0],
                    [0, 0,-1,1],
                    [1, 0, 1,0]].

Its determinant is 1/16. I reconstruct the doubled roots from the pinned
fixture and check this determinant by rational elimination and the 24-term
integer permutation formula.

For a separate check I use PR3252's unchanged full-memory acquisition,
relay, delivery and antichain operations. I provide an explicit bounded
model with 2,309 helpers and four sources; I leave the predecessor's
208-helper Model class unchanged. Its proof quantifies over finite helper
collections. I retain its cap of 16 memories and its exception on capacity
failure. The observed peak is two. I carry old memories, relay only old
state, and grant complete untimed reads.

Both methods agree on all 416 support entries. Their per-source target
bitmasks are

    0x15088a1021120142242d061684
    0x1504102110011204022d109084
    0x1b0000480c4084800021001083
    0x2a889524212d01425a52a06020.

The direct helper criterion imports no memory-transfer or pruning operation.
The two methods share authenticated frame/endpoint construction; I do not
describe them as independent human or proof-kernel review. I enumerate four
source columns, not all possible preconditioners or helper flags.

## Rank conclusion

Set V=U^-1. Completing the identity shear forces D=V-M. The missing
support block forces D[R,S]=0, hence V[R,S]=M[R,S]. Because R and S are
disjoint, (V-I)[R,S]=M[R,S], which has rank four. Thus rank(V-I)>=4.
The identity V-I=-V(U-I) gives rank(U-I)=rank(V-I)>=4.

For square matrices P,Q,

    PQ-I=(P-I)Q+(Q-I),
    rank(PQ-I)<=rank(P-I)+rank(Q-I).

Induction shows that a product of k rank-one updates differs from identity
by rank at most k. Therefore no three-update preconditioner can complete
this fixed-cover correction. I grant its inverse restoration for this rank
argument, so charging restoration cannot weaken the conclusion.

## The separate-shear price test

I use PR2920's favorable 208-unit-helper screen: m=73, 832 live families,
nine invocations, unchanged centre charge 56 and fractional rank-51 idle
packing. Its local profile is

    {1:2946,2:58,3:86,4:104,5:48,6:24,7:8,8:8}.

The 208 unit flags contribute 1,872 H1 occurrences. For k separately paid
H2 source conversions, I add k at rank two and add 2k to the centre/mass
charge. I grant no idle displacement from this new work. Local mass is
4240+2k, total mass is 6712+2k and idle mass remains 2472.

At the selected complex saving
a=67018507072324140917/40000000000000000000000, the credited exact interval
engine gives the following outward rational bounds with denominator 10^18:

| Extra H2 | Lower moment | Upper moment |
|---:|---:|---:|
|0|0.998896243881670160|0.998896243881670161|
|1|0.999194400107331118|0.999194400107331119|
|2|0.999492556332992075|0.999492556332992076|
|3|0.999790712558653033|0.999790712558653034|
|4|1.000088868784313991|1.000088868784313992|

I grant ideal packing and omit routing, scalar work and other unknown costs
in this necessary screen. Four separately charged conversions already fail
the selected benchmark. More such conversions only increase the moment.

I add no extra H7 restoration surcharge. PR2479 already supplies a same-profile
ordinary physical dual with owned zero accumulators and nonzero discard.
Extra H7 return work belongs to a stronger private-storage contract. The
rank-four certificate alone does not imply four H2 calls for a joint or
fused preparation. Such a realization, changed covers, target reads, helper
descents or additional correlated state require their own contracts and bills.

## Research decision

I stop the independently charged source-shear construction route under these
fixed covers. Its cheap one-shear boundary is valid, but the stronger support
condition requires at least four update dimensions and the stated separate
tariff loses even under favorable packing. I do not launch a matching or
coefficient search for that rejected implementation class.

I leave broader joint preparation and changed source/consumer contracts open.
I have constructed no complete correction, global supplier or new exponent,
and I leave the selected frontier unchanged. The source theorems, native
semantics and physical/analytic transfer retain their original evidence status.
