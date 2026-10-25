# Independent review of the polarized H_ab local native interface

The emitted **one-direction 25D local side module passes** this review.
This is an interface result, not a complete productive Gaussian caller,
new kappa, leaderboard improvement, or upstream scientific acceptance.
The independent checker does not call the author's `module.py`,
`frame_tools.py`, or `check.py` calculation. It reuses the pinned primitive
Pauli compiler, and implements a fresh exact sparse amplitude evaluator,
literal-program interpreter, subspace checks, phase checks and accounting.

## Literal geometric partition

The 64 pinned rational channels have exactly four distinct pairs (S,R)
of binary eight-dimensional source/read spans. Each pair has sixteen
channels and 128 literal source fields and 128 literal reader fields.
The four source sets partition all 512 source ports, and the four read
sets partition all 512 reader ports. For every port all incident channels
have exactly the same pair. All pairings S by R vanish. The two 512-field
sets are disjoint. No field identification or loss of independent input
is used.

The explicit 25-vector raw-27 orthonormal basis has Gram I25; every actual
port is recovered from its 25 coordinates and has norm one. This binds
the physical coordinates to the original labels rather than to an
abstract orthogonality graph. The rank-one coefficients are pinned to
the separately verified exact H_ab = -C_ab tensor (I-K tensor K)/2
factorization, including the polarization's factor 1/2.

## Universal native-conjugation phase proof

Here products are written in operator order: the rightmost factor acts
first. Let R be the product of the one-axis Gaussian gates

    C = ((1+i) I + (1-i) X)/2.

For an invertible binary G, put A=G^{-1}, let a_j be its jth column,
Q=I+A^T A, and K_G=D_Q P_G. The diagonal convention is precisely that of
the pinned compiler: linear coefficient alpha_j=Q_jj in {0,1}, and
quadratic coefficient 2 Q_jk for j<k. Write w_j=wt(a_j) and

    d_j = floor(w_j/2) mod 2.

For every binary y, the XOR weight expansion modulo four gives

    wt(Ay) = sum_j w_j y_j
             - 2 sum_{j<k} (a_j dot a_k) y_j y_k mod 4.

The higher intersections have coefficients divisible by four.
Furthermore alpha_j=(1+w_j) mod 2, so alpha_j+w_j=1+2d_j mod 4.
The quadratic terms therefore cancel exactly:

    q_Q(y) + wt(Ay) = wt(y) + 2 d dot y mod 4.

Set a=(1-i)/2. The literal, absolutely normalized inverse-Gaussian column
is R^{-1}|0>=a^n sum_x i^{wt(x)}|x>. After the literal permutation and
diagonal this identity gives

    K_G R^{-1}|0> = Z_d R^{-1}|0>.

No unspecified scalar is introduced. On one axis R Z R^{-1}=-Y=-i XZ,
so the full conjugation has the exact zero column

    (R K_G R^{-1})|0> = (-i)^{wt(d)} |d>.

The conjugation is monomial universally: ignoring only Pauli phases,
R^{-1} sends the Z Lagrangian to {(z,z)}; K_G sends (z,z) to (Gz,Gz)
because QG=G+A^T; R sends this to {(0,Gz)}. Thus it sends every Z Pauli
to a signed Z Pauli. The exact signed tableau and this one absolutely
normalized column determine the complete monomial operator. For the
four actual G matrices, the independent checker verifies the emitted
signed tableaux and the zero columns of their compiled monomial words.
All four have offset 20455680 and phase exponent 2 modulo four.

## Actual factor chronology and phases

Write F_r^G=K_G R_[0,r) K_G^{-1}. The common physical S8 frame is
Phi=F_8^G. The source entrance L is its actual canonical line frame.
Choose a flag beginning with q and spanning S8, and write its native
matrix as K_s. The source-entry emitted word has operator

    B K_s R_[1,8) K_s^{-1} A,
    A=F_1^{G_s} L^{-1},   B=Phi (F_8^{G_s})^{-1}.

The intervening native frames cancel literally, leaving Phi L^{-1}.
All 512 A and B factors are independently checked monomial operators
with both exact signed tableaux and fresh sparse absolute-column phases.
Every paid child has exactly seven axes.

The source exit is

    (R K_G R^{-1}) R_[8,25) K_G^{-1} = R Phi^{-1}.

The equality follows from R_[8,25)=R R_[0,8)^{-1}; the native full
conjugation's absolute phase is proved above. It is charged as H17.

Reader entrance is the defining word Phi, charged H8. Each reader
endpoint flag V begins with the identical ordered S8 basis, spans its
actual q-perp hyperplane, and has dimension 24. With native K_v, the
reader exit is

    K_v R_[8,24) K_v^{-1} A,
    A=F_8^{G_v} Phi^{-1},

which is F_24^{G_v} Phi^{-1}. All 512 A factors are independently
checked with exact signed tableaux and absolute phases, and every child
has sixteen axes. The actual endpoint frame word is supplied per reader.

These are exact one-copy Clifford identities including absolute phases.
They therefore tensor-lift columnwise for every positive address width.
In particular an emitted one-copy phase -1 remains its actual tensor
phase (-1)^f; it has not been discarded from a projective tableau.

## Same-frame row interpretation and owned lifecycle

The independent interpreter processes all 15,116 literal events and
checks the old chart of every transition and the common chart of every
ADD. The owned C0 has zero logical row at every zero-retag and every
CLEAR_ZERO; the latter four clears remove no remaining source data.
For each channel the source gather is undone after the readout.

At the end all 512 independent source logical rows are unchanged and
their physical chart is the standard full R25. Each of the 512 reader
rows is exactly its own independent y plus the pinned H_ab source row,
with its explicit q-perp endpoint frame. C0 returns to exact zero at
ground. All 1,024 original input columns are retained in these checks.

The independently recomputed complete paid profile is

    512 H7 + 512 H8 + 512 H16 + 512 H17.

The ordinary literal count is 13,056 ADD, 5,632 D, 5,632 P,
2,048 X, 2,048 phase, eight zero-retags and four already-zero clears.
There is one owned zero scratch cell, no independent helper input,
no helper target credit and no independent Gaussian COPY service.

## Exact finite-module growth constants

At every literal event, measure the exact rational logical row against
the original independent entrance fields. The maxima are:

| Role | Maximum row coefficient l1 | Maximum dyadic denominator exponent |
| --- | ---: | ---: |
| Source | 1 | 0 |
| Owned C0 | 5 | 4 |
| Reader | 53/8 | 6 |

The reader's intermediate maximum is 53/8, not the final-row bound six.
It first occurs at zero-based event 3182 in the pinned word. The cache's
maximum five first occurs at event 324. Every physical chart and all
monomial/Gaussian substeps are unitary. Hence if each independent
entrance field has l2 norm at most M, every source, C0 and reader field
has norm at most M, 5M and (53/8)M respectively at all module events and
unitary substeps. These finite constants do not by themselves supply
the accumulated rounding-error or precision bill of a complete caller.

## Boundaries of the result

The source canonical line services are **supplied entrances** and must
be paid and connected by a complete caller. The coupled reader endpoint
is not an autonomous Gaussian job on independent y. No reader target
credit may be inferred until its H_ab source contribution is removed
within the actual caller.

The 20D embedding is a separate correct finite-geometry aid. Its radical
has dimension eight and its literal span has dimension twelve, giving
the rigorous minimal nondegenerate ambient lower bound 12+8=20. Its
written rank256 fitting classification and F^2=4F argument are sound.
These facts do not connect local full20 to global full25 at zero cost.

The controller's reciprocal H-only word proves logical common-chart
chronology for 2,048 original inputs in either dimension. It explicitly
has not compiled its own standard-child phases. The one-direction
literal phase compilation reviewed here does not silently fill that
separate gap for every controller frame or both dimensions.

No compatible K-core chronology, full-global-H schedule, full fitting
decoder, productive whole-caller invoice, finite precision/compiler
admission, kappa improvement or upstream acceptance is proved here.
Even granting the two source/target jobs in an isolated H-only module
as independent would leave the usual concavity penalty from splitting
each into smaller Gaussian children; this local word alone is not a
standalone winning producer.

## Final read-only review receipt

The final scientific PROGRAM payload digest is
`497ab37cf2b4c55883d860458bb58d946f685fd55d344fb2b29fcb727b6033b9`.
The reviewed `module.py` digest is
`26a042a4817ef6862ade58b97bfad5a989d9d856ec94b7ff024c991a8da13d30`.
Python 3.12 normal and optimized read-only runs of `review.py` both pass,
with byte-identical stdout. Three additional independent literal mutation
controls reject an invisible-tableau phase i, a wrong S8/R8 coframe
(transport rank four), and an omitted final source-uncompute ADD.

`review.py --package PATH` reads a module package without modifying it.
Its default package is the script's own directory and its default receipt
is `INDEPENDENT-REVIEW.json` within that package. `--receipt PATH` can
select a separate existing receipt. Only explicit `--write` authors a
receipt. The scientific comparison excludes gzip environment metadata.
There are no absolute runtime filesystem dependencies.
