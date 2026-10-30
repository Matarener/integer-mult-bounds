# The fixed R429 FULL-target compensation word

The statement concerns the frozen word with canonical SHA256
`895a359e33a7a9a9cb2c4a68acc9fcf624596d334a52381264ae498e0e55c847`,
at scientific pin `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
It has 651 ordinary registers in the order

    x_0,...,x_110, y_0,...,y_110, h_0,...,h_428.

All inputs are independent and arbitrary. The input frame of source `x_p`
is its actual E8 line `P_p`; all targets and helpers enter at ZERO. Every
ordinary register exits at FULL. The word has no private register or
COPY/ERASE record. This does not assert zero scratch inside the inherited
native implementations of its MOVE records.

The exact signed scalar endpoint is

    (x,y,h) -> (x, y + A x + E h, h),

where `A` and `E` are completely evaluated integer matrices satisfying
`A = I mod 2` and `E = 0 mod 2`. Thus the binary VALUE endpoint is

    (x,y,h) -> (x, y+x, h).

The integer target endpoint is not `y+x`. In the actual first target row,
the coefficient of `x_0` is 3 and that of ordinary register226 (helper4)
is 2. Exact source restoration, helper restoration and identity on old
target `y` hold over Z; source-to-target and helper-to-target residuals
vanish only in the indicated parity reduction.

## Literal construction and scalar identity

The predecessor is the frozen R429 word with canonical SHA256
`ebc33ee086f610c1fd540fa56bb99b2b96a768e4aed4a18defcb0e1f507fca89`.
Its gzip container SHA differs from another published container, so source
comparisons must distinguish compressed and canonical bytes. The parent
has identified this canonical predecessor with the word published in
PR3645. The current contribution does not claim that predecessor or the
old cap identities as new.

Delete the predecessor's source-code phases21–24 and its three private
repair episodes31–33, including their COPY/ERASE records. The resulting
signed bulk restores every source and helper over Z and has target block

    y -> y + B x + E h,

with `B = I + K R mod 2`. Here `R` is reconstructed by applying the raw
R438 D and A gates to all660 binary input columns and reading the nine
retained source rows; `K` is read from the actual scatter incidence.
All111 rows and all nine reader directions are retained in the check.

Append one explicit rank-one MOVE from each of the111 target caps to FULL.
At that cut all data sources and targets have the same FULL frame. For each
binary row `R_j`, choose the first supported source coordinate `p_j` and
execute:

1. Add each other supported source into `x_(p_j)`, with coefficient+1.
2. Add this temporary source total into every target selected by `K[:,j]`.
3. Reverse the preparation order with coefficient−1.

The total prepared over Z is the positive sum of the original source
coordinates in the support of `R_j`. The pivot includes its own original
coordinate, so no clean temporary assumption is used. Literal unpreparation
restores the pivot over Z before the next reader. In binary arithmetic this
adds exactly `K[:,j] R_j x`; summing all nine readers cancels the bulk's
`KR` defect and leaves `y+x`.

Over Z let `K_01` and `R_01` denote the zero/one lifts of these incidence
matrices. The exact update is

    A = B + K_01 R_01.

The independent checker compares every coefficient of this integer identity,
including the whole helper block E and the entire target self-block. It
does not infer the integer identity from a parity check.

The complete word has12932 signed ADDs:11377 inherited bulk ADDs plus514
preparation,527 scatter and514 unpreparation ADDs. It has2984 MOVE records,
including all111 new cap-to-FULL lifts. It contains no source code, target
precode, retained snapshot, private compensation field or terminal gauge.

## All-input verification and literal inverse

Every scalar operation is linear over Z. A dense651-by651 integer matrix
started at the identity therefore carries all651 independent source,
target and helper columns simultaneously. The independent checker uses
Python arbitrary-precision integer lists, importing no producer module or
producer utility. Every signed ADD is applied to a complete dense row;
every MOVE is handled by the separately checked frame chronology.

The final matrix is the signed shear above. Its nonidentity block squares
to zero, hence the complete integer inverse is `2I-F` when F denotes the
full forward endpoint matrix. Reversing the literal record order and
negating each ADD coefficient yields exactly that matrix, including every
even coefficient. Applying this literal inverse to the forward matrix
returns the651-by651 identity exactly.

The maximum row sum of absolute signed coefficients at every ADD prefix
is874 in both orientations. This is an exact bound for this signed scalar
normalization, and also bounds its endpoint rows. It is not the positive
envelope obtained by replacing subtraction with addition. In particular it
does not prove a rounded-child precision contract, suffix-error bound,
native intermediate growth bound or physical execution cost.

Three executed controls distinguish the required obligations:

- Omitting one actual compensation scatter changes the binary endpoint.
- Reversing one unpreparation sign breaks integer source restoration while
  leaving the entire binary endpoint unchanged.
- Omitting the target111 cap lift causes an actual subsequent ADD to fail
  its common-frame requirement.

The second control is essential evidence that the check sees signed errors
which would be invisible in an F2-only replay.

## Exact frames and new ADDRESS lift

All raw frame dimensions are recomputed over Q from their actual E8 roots.
For every MOVE the checker verifies the current frame, literal containment
of the smaller root set in the larger, and the positive exact dimension
increment. For every ADD it verifies both registers have the declared
common frame. The entire forward and inverse frame chronology, including
the final frames of all429 helpers, is checked.

The current word uses628 distinct ADD frames. Of its12932 ADDs,5758 use
ZERO,4147 use FULL and3027 use intermediate common frames. The historical
receipt's sentence saying every scalar ADD uses ZERO or FULL is false.
The correct statement is that every ADD uses its actual common frame and
all1555 newly added compensation ADDs use FULL. The old internal-frame
compiler remains an inherited contract.

For the actual norm-four root `q_p`, define the dyadic projector

    P_p = q_p q_p^T / 4,       C_p = I-P_p.

The entrance frame is exactly `im(P_p)` and the old target cap is exactly
`im(C_p)`, with ranks1 and7. For a projector P define the16-by16 ADDRESS map

    D_P = [[I-P, P], [P, I-P]].

Exact dyadic multiplication proves, separately for each actual root,

    D_I D_P = D_(I-P),       D_P^2 = I,
    D_I D_(I-P) = D_P.

The first two identities are the inherited cap facts:3552 ADDRESS columns
across111 ports. The last is the new cap-to-FULL lift identity:1776 further
columns. The checker reconstructs every projector from the original roots
and compares all entries; it does not substitute rank counts for operator
equalities. In any odd ADDRESS field,4 is invertible, `q_p^T q_p = 4`,
and `q_p` remains nonzero. Therefore P has rank1, its complement has rank7,
and these exact identities survive dyadic reduction. Untouched spectator
coordinates extend them by the identity.

These ADDRESS matrix identities induce the corresponding permutations of
binary VALUE arrays. ADDRESS linear algebra is not identified with VALUE
addition. The old native realizations of every internal MOVE, their chart
adapters and exceptional/fallback guards remain inherited premises. This
finite check does not execute an independent implementation over every
ADDRESS size or modulus.

## Physical endpoint and paid diagonalization

Under the inherited native frame convention, the physical residual on
source port p is `S_p = F8 D_(P_p)`, of native rank7. The physical target
residual is `T = F8`, of rank8. Converting the verified binary logical
shear to those physical frames gives the data VALUE-operator block

    [[S_p, 0], [S_p, T]].

This is a block over binary VALUE operators. It is not the full signed
integer endpoint matrix described earlier. The physical helper output is
`F8 h_j` for each ordinary helper, since its frame progresses from ZERO to
FULL. Logical restoration to the same helper symbol is not physical
identity restoration; a caller must account for that helper frame progress.

One additional common-FULL ADD `y_p <- y_p - x_p` per port diagonalizes
the binary block to `diag(S_p,T)`. All111 such ADDs are paid separately.
They are absent from the12932-ADD emitted shear word; the diagonalized
version has13043 ADDs. Over Z this postcomposition leaves the even residual
`(A-I)x+Eh`; it does not give an integer identity.

The complete paid child-rank histogram is

    H1=1406, H2=1342, H3=79, H4=44, H5=93, H6=11, H7=9.

Its mass is5097. Independently, the total frame progress is

    111*(8-1) + 111*(8-0) + 429*(8-0) = 5097.

Thus this local interface has zero excess rank mass relative to its actual
source, FULL-target and helper progress. The111 target lifts are already
included and cannot be dropped from a caller invoice. A zero local excess
does not imply a positive complete caller saving or an improved exponent.

## Scope

The result is an exact finite signed word, binary endpoint, explicit frame
chronology and local ADDRESS lift certificate. Arbitrary logical helper
inputs and arbitrary old targets are included. Native implementation of
old internal moves remains a named dependency. Global caller topology,
integral chronological helper hosting, complete recursive moments, rounded
precision, coefficient/source access, tape and head-return costs are not
supplied. No new kappa or selected-frontier change follows.
