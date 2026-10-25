# A joint compensator at a prepared two-axis P104 cut

## Scope and changed premise

The retained caller separately makes both Gram shears into identity shears,
then pays an endpoint correction. Here we ask for one compensator after the
raw two-axis product, with the same named data owners. We combine elementary
symplectic shear factorization with operator algebra of physical Clifford
charts. No external payload encoding or local Q/D consumer is changed.

The theorem starts at an explicitly **prepared cut**. It assumes a chronological
producer has delivered the raw logical product in the displayed charts. The
canonical copied-center caller supplies the chart and endpoint convention;
it does not supply a completed P104 row/column implementation at this cut.
In particular, port-dependent interstage frame alignment, opposite orientation,
global owners and both helper-bank completions remain obligations. No free
interstage adapter is inferred from the scalar product below.

Let A=G/2 be the 104-port canonical Gram matrix, A_r=A tensor I and
A_c=I tensor A on N=104^2 data positions. Let U(Q)=[[I,Q],[0,I]] and
S(Q)=[[I,0],[Q,I]]. The raw product is

    M = U(-A_c) S(A_r) = [[I-A_c A_r,-A_c],[A_r,I]].

For each position use the original physical line U_ij, T_ij=C_Uij, full
operator F=C_I and E_ij=F T_ij^-1. Write T for the diagonal family and K=T^-1.
These translation-based rank-one operators commute with common F. Define
Gphys=diag(F,FK). The prepared entrance to this repair is

    Gphys M (T^-1 x,y),

and the retained final endpoint before the inherited phase/sign/bank wrappers
is Gphys J(T^-1 x,y), where J=[[0,-I],[I,0]]. Indeed the retained extra lower
correction changes (-Fy,FT^-2 x+Ey) into (-Fy,FT^-2 x). Thus J, rather than
U(-I)S(I), is the appropriate joint target when that correction is absorbed.

## Unique joint map and a division-free three-layer factorization

Since M is invertible, the unique linear compensator on these fixed fields is

    C = J M^-1 = [[A_r,A_r A_c-I],[I,A_c]]
      = U(A_r-I) S(I) U(A_c-I).

Direct multiplication proves both identities without assuming A_r and A_c
commute. This avoids eigenprojectors and all division by 13. It is an exact
identity for arbitrary data, including kernel payloads.

Three is the minimum number of upper/lower two-bank unipotent shear layers
in this restricted alphabet. Two layers of the same orientation combine into
one. A product U(Q)S(R) has lower-right block I, and S(R)U(Q) has upper-left
block I. C has neither diagonal block equal to I. The explicit factorization
attains three. This statement permits arbitrary coefficients in each layer,
but excludes extra banks, nontrivial diagonal operations, free permutations,
changed input/output coding and fusion into the producer. It is not a native
child lower bound or a lower bound on arbitrary algorithms.

Physical conjugation, retaining the order of the port-dependent T, gives

    Cphys = Gphys C Gphys^-1
          = [[A_r,(A_r A_c-I)T],[K,K A_c T]]
          = U((A_r-I)T) S(K) U((A_c-I)T).

Neither T(A_c-I) nor A_c is a replacement for the final displayed block.
Common F cancels, while K A_c T generally cannot be simplified to A_c.
The verifier checks these statements in a free noncommutative algebra with
only TK=KT=I; a separate Gaussian-integer matrix implementation checks varying
charts that fail to commute with each axis. Both dirty-helper banks are
extended by identity **through the repair**; completion of their previous
physical paths is part of the prepared-cut premise.

## Spectral diagnostic, without donating spectral projections

The canonical roots give A^2=13A and tr(A)=104, so A has eigenvalues 13 with
multiplicity 8 and 0 with multiplicity 96. On the four joint spectral sectors,
C is [[a,ab-1],[1,b]] and

    det(C-I)=2-a-b.

The determinants are 2,-11,-11,-24 on dimensions 9216,768,768,64.
None vanishes. Therefore rank(C-I)=2N=21632, and the compensator fixes no
nonzero common-chart payload. Similarity by Gphys preserves the zero fixed-space fact on
physical arrays; the information rank is multiplied by the address dimension. This rules out omitting the joint map on a proposed unchanged
spectral sector. It does not price the map in native rank units. The rational
projectors A/13 are a proof device, not an admitted Gaussian-dyadic primitive.

## Explicit physical copy route and full conditional gate

Read the three factors right to left. For an upper layer, copy one E-chart
donor into owned private storage, apply its T to obtain the F-chart field,
halve that private copy, and perform the signed unit additions prescribed by
one column of 2(A_axis-I). Erase only the owned copy after its final read.
The persistent donor is unchanged. A has diagonal 1 and 4992 off-diagonal
signed halves, so no diagonal addition remains. Repeat across 104 fibers.
For the middle layer, copy each F-chart first-bank value, apply K, and add it
to the matching E-chart second-bank value. Erase the private copy. All
arbitrary dirty persistent roles are unchanged, and one sequential temporary
array suffices. Erasure uses the inherited owned-copy disposal semantics;
this is not a claim of reversible uncomputation to zero.

Each T or K is one rank-one C or inverse C with the retained phase wrappers.
The written route has 32448 positive rank-one copy transforms, 1049152 unit
array additions, 21632 private-copy halves, 32448 each of private creation,
copy and erasure, and peak additional width one array. There are no restoring
doubles because only dead private donors were halved. This is a constructive
ideal operation invoice at the prepared cut, not a native compiler replay or
an implementation-runtime comparison with #3940/#3894. The scalar support and
all local donor columns are independently recounted from canonical roots.

For the conditional #3954 inventory m=81, W=36608, N=10816, grant all 208
bare channels mass 2368 and persistent progress at most 2312, including the
unproved opposite orientation. Keep the same all-role endpoint, equal volume
1/W, residual rank tariff at least net persistent progress and ranks <=81.
Then remaining progress is 81W-N-208*2312=2473536. Before ANY joint repair,

    bare lower bill = 208*2368+2473536 = 2966080,
    capacity        = 81W             = 2965248,
    excess          = 832.

This is the correction-only changed-premise specialization of the prior gate,
not a new universal P104 barrier. Even free repair fails under these hypotheses.
The explicit repair changes no persistent chart and contributes 32448 more
rank units, giving lower bill 2998528 and excess 33280. Scalar, preparation,
interstage alignment, phase/routing/control/tape, finite width/precision and
recovery costs remain additional nonnegative costs, not zero. Private storage
must be admitted in the complete volume/holding model. Granting it free already
fails. Fully paid extra persistent banks cannot remove this numerator gap.
For 0<=a<1, (r/81)^(1-a)>=r/81, so this favorable native bound also fails every
such moment. No runtime total or all-size supplier is claimed.

More generally, for a legitimately changed local profile with mass M_loc and
persistent progress cap P_loc, put d=M_loc-P_loc. Under the same global
endpoint/initial-credit hypotheses its necessary zero-parameter gate is
C_joint < N-208d. A hypothetical d=0 profile would allow less than 10816 repair
units, while this explicit 3N route still fails by 21632. No such profile or
prepared producer is established here. A different completed local endpoint
must rebind its progress and physical preparation, not inherit P_loc=2312.

If a genuinely changed bare implementation saves s rank units per call with
the SAME persistent progress and ownership assumptions, specialization gives
C_joint < 208s-832 before any further costs. For s=7 this
requires C_joint<624; the present route does not meet it. This is a diagnostic
for changed proposals, not evidence that such a saving or producer exists.
Stop dependent native construction for the present contract. The useful next
step is a producer/repair fusion that changes that actual bill and supplies the
missing physical chronological cut, rather than applying the spectral rank as
a native tariff or treating the three-layer word as inexpensive by default.
