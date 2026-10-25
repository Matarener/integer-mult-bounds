# Source-consuming E adapters with one full-Gaussian query per spectral mode

This is a local positive construction and a typed three-stage caller. It is not a completed Gaussian supplier or exponent improvement. In particular its negative E-coded terminal remains unresolved.

## Operators and ordinary recodings

Let Q be the positive Gaussian on the common central line, D the positive Gaussian on24 fresh axes and R=DQ. The phase-complete whole-K native module has

    F_K=diag(D,D)L(K Q^-1),
    B_K=diag(D,D)U(-Q K),
    K^2=I, K^T=K, [K,R]=0.

Here K is the full physical owner/address code, including the real signed normalizers L_i, not the scalar owner matrix alone. Put C=F_3(C_base) in the same physical similarity, A=I-C, E=K A^-1. Then K C=-C and K commutes A. The actual C eigenvalues are0,98,-1078, so A is invertible. K,A,E are real symmetric and commute R. Every E evaluation is an explicit finite ordinary owner recoding; it is not a Gaussian child. Its rational denominators and rounding are charged ordinary arithmetic.

Write H(T)=diag(T,Q^-1 T Q). For any same-stage invertible X commuting K, with E=KX, direct block multiplication gives

    postX(E) F_K preY(E) = H(E) diag(D,D)L(X^-1 Q^-1),
    postX(E^-1) B_K preY(E^-1) = H(E^-1)diag(D,D)U(-Q X^-1).

For X=A^-1 the residual coefficient is A, so a low-rank C correction suffices. This is different from treating the original H=F_3(B)-F_3(C) correction as a scalar-separated native bank.

## Backward correction from actual original inputs

Before any precode or native operation overwrites Y, copy its nonzero C modal coordinates into owned fields. Apply R to those mode fields. Between B_K and its postX(E^-1), scatter -R C Y_original into X. The complete corrected map is

    W_B=H(E^-1) B_0,
    B_0=diag(D,D)U(-Q).

Indeed the uncorrected adapter has upper right -R E^-1 A, and the scatter contributes -R E^-1 C. Since A+C=I, their sum is -R E^-1. The mode acquisition uses the original physical ground-chart Y; no QY or other Gaussian input is supplied for free.

Here is the explicit global rank factorization used by the query. The pinned112-by8 root-mode matrix M satisfies M^T M=56I. Its eight columns span the base C eigenvalue14 space. `modes.py` emits a rational104-column kernel basis N and T=[M,N], together with T^-1. For y, its first8 coordinates are M^T y/56 and its104 remaining coordinates are the free coordinates of y-M(M^T y)/56. The emitted863 ADD,8 SCALE,7 SWAP word realizes each of T and T^-1 in place; every112-by112 entry is checked.

In the three owner selector coordinates, use T tensor T tensor T. C has eigenvalue98 on the three sectors with exactly two8-dimensional active coordinates and one104-dimensional kernel coordinate, total19968; eigenvalue-1078 on the all-active sector, dimension512. There are therefore20480 nonzero modes. The explicit structured algorithm is:

1. Apply each ordinary physical L_i to original Y_i. Apply the emitted T^-1 word on each owner axis and every fixed pair of other owner indices.
2. COPY the20480 nonzero modal coordinates into distinct owned zero fields. Invert the owner recoding and each L_i, restoring original Y before any native/precode overwrite.
3. Apply one full R25 Gaussian to each owned mode field.
4. Normalize the existing X bank by L_i and T^-1, ADD the signed eigenvalue-weighted mode outputs at the nonzero coordinates, restore T and L_i^-1, and CLEAR the owned modes after their final read.

Scalar owner recodings commute with the common R. Every L_i commutes R exactly, including phase. Thus this algorithm adds -R C Y, at all positive field widths, with precisely20480 paid H25 children. Mode inputs are actual linear combinations of original inputs. These paid calls are not also counted as independent productive helper outputs.

The E code uses the same modal basis, scaling sectors by1/(1-lambda) or1-lambda, followed by the literal block-diagonal K_odd owner recoding. For each512-port cube, the latter uses its76-per-row coefficients in512 owned output fields, then SWAPs completed outputs with main fields and clears the old main values now in owned scratch. No main source is overwritten before its last source read. The512 scratch fields are reused between cubes. The structured loops define all operations without serializing hundreds of millions of repeated scalar instructions.

## Forward orientation without a free thin query

A direct prequery C Q^-1 X would need a new source-extraction argument. Instead construct an actual inverse of W_B and transpose that linear program.

Undo the postX(E^-1) by E. In the actual B_K word, every ADD has source Y and target X; no ADD modifies Y. Every one of its512 root-case Y fields is read at one unchanged physical common-frame contact,76 times. Execute all inverse Y operations first and COPY that contact value once per Y into owned scratch. This completes the actual inverse source path, obtaining E^-1 Y_original; apply ordinary E to recover Y_original. Now recompute R C Y_original by the same modal query, undo the scatter on X, and execute all reverse X operations and reverse ADDs using the saved physical Y contacts. Clear each owned contact after its final read. This computes W_B^-1, using the same native Gaussian profile and20480 H25 queries. It does not assume a scratch-containing word is invertible gate by gate.

`checkpoint.py` parses the actual canonical B root512 program. It authenticates all38912 ADDs and512 source contacts, emits the inverse paths and owned lifecycle, and checks both composition orders against identity on all1024 independent main operator rows over a free algebra of arbitrary independent noncommuting invertible native event operators. It then transposes the actual owned inverse program and checks all operator entries. Each native inverse gate has an emitted literal monomial inverse or paid-path inverse; C_axes^-1=C_axes X_axis_mask exactly, with no omitted scalar phase.

Transpose this independently constructed inverse program. Reverse instruction order, transpose each monomial/paid map, send ADD(target,source,c) to ADD(source,target,c), send an owned COPY to an accumulating ADD followed by clearing its old adjoint, and send discarded owned scratch to fresh zero adjoints. This is linear transposition with clean owned fields, not inverse execution of CLEAR. Each coordinate Gaussian is symmetric; transposition leaves its rank unchanged. The generic root512 replay checks this rule on all operator entries. The exact small fixture also checks original-input acquisition, all absolute phases and every entry of the resulting complete main matrix.

Put J=diag(Q^2,I), an ordinary X-mask operation. Then

    diag(D^2,D^2) J W_B^-T J^-1 = H(E) F_0,
    F_0=diag(D,D)L(Q^-1).

To see this, H(E^-1)^-T=diag(E,Q E Q^-1). Conjugation by diag(D^2,D^2)J=diag(R^2,D^2) sends this to H(E), since E commutes R and therefore R^2. The remaining factor is the usual exact raw-dual boundary conversion. All boundary powers are monomial. Thus both orientations have the same paid profile

    {8:v,9:v,15:v,16:v,25:20480}, v=112^3.

The old native H helper banks and their fragmented main paths are absent. Native monomials, mode recodings, contact COPY/CLEAR, all scalar arithmetic and precision remain real ordinary work.

## Three distinct fresh stages and the unresolved terminal

Let each stage have its own24 fresh axes and the same central Q. Each E_s commutes D_s Q and fixes other fresh axes. For H0=diag(I,Q), the corrected forward and backward maps become

    H0^-1 diag(E_s D_s,E_s D_s)L(I)H0,
    H0^-1 diag(E_s^-1 D_s,E_s^-1 D_s)U(-I)H0.

The three-call word F_1,B_2,F_3 has no IDLE or thin query. Adjacent H0 cancel; the scalar LUL is a signed swap. Keeping the actual ordinary final signed swap gives the two exact main endpoints

    Q^-1 B_E D_123,
    B_E D_123 Q,
    B_E=E_3 E_2^-1 E_1.

An ordinary B_E^-1 postdecoder turns the positive half into independent H73 jobs on its original inputs. The negative half remains specified by its actual coupled operator. `n3.py` emits the corresponding owned three-fresh-stage small word and checks every column of its64-by64 exact complex-rational main matrix, including phases and positive output decoding. The naive B_E^-1 negative decoder is rejected.

The same fresh-stage commutation premises permit the existing coded-caller IDLE algebra, with each chronological E code installed around an already-paid IDLE. That observation does not insert or grant any additional IDLE. The concrete N3 word used in the numerical screen needs none.

If, only as a conditional screen, both halves were independent H73, the paid profile of3 full calls would be3v copies of ranks8,9,15,16 plus61440 H25. At a=.003027288235, its remaining signed moment is enclosed by an explicit rational log/exp Taylor calculation near +.04382074131724228 per port per local call. The earlier22016-feature variant gives +.01675342557712707. These are conditional margins, not accepted target credits. If the negative half merely became H71, the complete moment would already fail even before these extra queries. No free H71 decoder is sought here.

## Precision, storage and scope

All ordinary coefficients and basis words are explicit rationals. Elementary ADD has field-l2 norm at most1+abs(c), SCALE at most max(1,abs(c)), COPY at most2, CLEAR at most1; paid coordinate Gaussians and signed monomial maps have norm1 at every width. The explicitly finite instruction counts therefore give a finite operator-norm amplification constant, independent of field width, **relative to an additive-error ABI measured in field-l2 norm**. This is not a fixed extra-bit bound for coordinatewise fixed-point arithmetic. A vector with N coordinates and coordinate error at most epsilon can have l2 error sqrt(N)*epsilon; N grows with the physical field dimension. The coordinatewise rounding-to-l2 conversion, Gaussian-service error ABI, outer error allocation and bit-precision cost require separate proofs. Divisions by56,97,1079 and other fixed rational coefficients must be implemented and charged; they are not exact-real oracles. A complete outer TM, routing and storage admission is not supplied here. PRECISION-SCOPE.md states this gate explicitly. The source-contact inverse uses v owned fields in addition to the20480 query modes and the reusable512 scalar-code scratch; these fields are never credited as independent Gaussian outputs.

The negative E terminal, its ordinary or paid decoding, and the full productive Gaussian invoice are UNKNOWN. Adding low-rank C changes the fitting-path hypothesis, so the proper-K terminal support cap cannot be silently reused as an E impossibility theorem. Conversely, full support of E paths is not an autonomous Gaussian certificate. No kappa, formally adopted algorithm or repository acceptance is claimed.

Credits retain the whole-K phase compiler, CrocSwap repository/native/controller/Clifford lineage, Ali Romman's odd-E8 geometry and the existing coded caller. New work here is Apache-2.0 and has substantial OpenAI Codex assistance. The worker reviews and exact replays are not proof-kernel or independent human acceptance.

The ordinary upper bills in MODES.json treat CODE(E) and CODE(E^-1) as explicitly realized ordinary linear macros. Their transposes may use the same recoder because each matrix is real symmetric; they need not literally reverse the scratch implementation. The query/source-contact portions are transposed with the explicit owned rules. The unified upper bill conservatively dominates both orientations. For one T/T^-1 pair let G be the product of the displayed elementary norm bounds. Disjoint owner batches form a direct sum, so each full axis pass has the same bound, rather than requiring its product over112^2 independent batches. A whole gather/scatter query has prefix field-l2 norm bounded by2*1079*G^6; the conservative CODE prefix bound is8*1079*G^3. The recorded binary logarithm upper bounds describe operator-norm amplification only. They are not fixed extra-bit offsets for coordinatewise rounding and do not establish TM precision costs.
