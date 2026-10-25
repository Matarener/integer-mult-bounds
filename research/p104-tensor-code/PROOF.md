# One dyadic code across both P104 axes

## Question and exact scope

PR3961 found that separately chosen row and reversed-column residual encodings
need not match. This package changes that premise: use **one invertible code on
all 21,632 data fields**, kept through both logical stages. The code is explicit,
dyadic, determinant one, preserves every independent syndrome/payload coordinate,
and has fixed X/Y return slots. It never divides by 13 or projects away a kernel.

The canonical native-channel proof supplies the exact uncorrected endpoint
`Y += A X`, where `A=Gram/2`, sources and all 72 dirty helpers restored. The
retained copied-center caller requires an identity shear, followed by an inverse
identity shear and its physical correction/wrappers. Therefore the uncorrected
Gram experiment below is a **changed intermediate protocol**, not that completed
caller. Its scalar savings for repeated Gram pairs are not full-caller savings.
We derive the missing identity corrections explicitly rather than price them zero.

## Dyadic triangular congruence and a global payload code

Order the eight pivot ports `0,1,3,6,22,31,93,103` before the other 96. The pinned
fixture reconstructs `B` with 384 signed-half entries and `BB^t=12I_8`. Put

```
U = [ I  B ]       P = [ I  0 ]       A = U^t P U.
    [ 0  I ]           [ 0  0 ]

U^-1 = [ I -B ]    M = U U^t = [ 13I  B ]
       [ 0  I ]                   [ B^t  I ].
```

All these U changes and inverses are over `R=Z[i,1/2]`; `det U=1`. Write
`U_r=U tensor I`, `U_c=I tensor U`, and similarly for A/P/M. On two 104 by 104
banks define

```
L = U_r U_c^-t,
C = diag(L,L^-t),
Xhat=L X,     Yhat=L^-t Y.
```

Row and column operators commute because they act on different port factors.
Neither code changes the bank names nor uses PR3882's cross-bank Pi permutation.
This is a replacement protocol; it cannot be inserted after the old literal
Pi occupancy without an additional derived and paid bridge.

For lower and upper uncorrected Gram shears,

```
S_r = [I 0; A_r I],     R_c = [I -A_c; 0 I],

C S_r C^-1 = [I 0; P_r M_c I],
C R_c C^-1 = [I -M_r P_c; 0 I].
```

For example,
`L^-t A_r L^-1=(U_r^-t A_r U_r^-1)(U_c U_c^t)=P_r M_c`.
The upper identity follows from `U_c^-t A_c U_c^-1=P_c`.
The same C occurs at both sides of the internal boundary: there is no row-code
to column-code transition there. This is an exact Gaussian-dyadic logical
protocol, including arbitrary real and imaginary input components.

All data are retained. In one axis, a kernel input `(-B z,z)` becomes `(0,z)`
under U, so zero query does not mean zero payload. The decoder restores this
input exactly. Both 72-per-fiber auxiliary banks may be appended as independent
identity blocks. No helper initialization, erasure, borrowing or return is used
by this scalar code. Their required physical completion remains separate.

## Physical operator order and fixed returns

Let `G_0,G_1,G_2` be the actual all-role chart maps at the entrance, shared
interstage cut and exit of a proposed implementation. The retained caller gives
`G_0=diag(T,I)` and `G_2=diag(F,E)` on data, with `E=F T^-1`; its actual
intermediate owner/chart schedule is not supplied for this changed P104 protocol.
Define the physical coding map at a cut by

```
C_t = G_t C G_t^-1.
```

For a physical first stage `W1=G_1 S_r G_0^-1` and second stage
`W2=G_2 R_c G_1^-1`, the exact coded replacements are

```
W1hat = C_1 W1 C_0^-1 = G_1 C S_r C^-1 G_0^-1,
W2hat = C_2 W2 C_1^-1 = G_2 C R_c C^-1 G_1^-1.
```

For the retained data entrance and exit charts specifically,

```
C_0 = diag(T L T^-1, L^-t),
C_2 = diag(L, T^-1 L^-t T),
C_2^-1 = diag(L^-1, T^-1 L^t T).
```

Here F is common to every port and commutes with scalar port coefficients and
the positive T family. For instance, the X entry block has matrix coefficient
`T_i L_ij T_j^-1`; it is not a free scalar L_ij read across unequal charts.
At a genuinely common FULL cut, `G=diag(F,F)` and `C_t=C`; this is a useful
special case, but does not supply the missing intrinsic-source entrance.

Their internal factors cancel in their displayed order. Port-dependent T need
not commute with U or L; no such commutation is used. The independent checker
uses noncommuting chart matrices as a control. Entry coding `C_0` and final
decoding `C_2^-1` restore the original named physical X/Y slots. Helpers are
identity blocks in C; their G maps are retained, not silently completed for free.

These formulas specify a physical changed-caller contract. They do **not**
provide legal native recipes, shared ownership, a concrete G_1, paid cross-port
routes, or an actual adjacent completed P104 pair. Applying the bare scalar C
in physical storage would generally be wrong. Native lowering must implement
these ordered conjugates or derive an equivalent paid schedule.

## Constructive scalar words and their complete comparison

All counts in this section assume a common full chart, arbitrary Gaussian-dyadic
payloads, and temporarily writable donors restored after each sweep. A U or
U^-1 sweep halves 96 nonpivot donors, performs 384 signed unit ADD/SUBs and
restores by doubling. A transposed sweep uses eight pivot donors. There are no
fresh scratch arrays, cross-bank swaps, or discarded payloads.

To encode both banks, execute four sweeps across 104 fibers each. Decode by
reversing and negating the sweeps. To apply `P_r M_c`, only eight pivot row fibers
are active: transform the source by `M=UU^t` (two sweeps), add its 104 fields
to the target row, and reverse the two sweeps. Apply `M_r P_c` analogously on
eight pivot column fibers. Every modified source is restored before the next
stage. An explicit uncoded reference computes `A=U^t P U` by a query sweep,
eight pivot deliveries, a B^t delivery, and inverse query sweep for each of
104 fibers. It is a specified constructive comparator, not an optimal word.

| Exact scalar word | Unit ADD/SUB | Halves | Restoring doubles |
|---|---:|---:|---:|
| Global entry plus exit code | 319,488 | 43,264 | 43,264 |
| One coded **uncorrected Gram** pair | 26,240 | 3,328 | 3,328 |
| One uncoded reference Gram pair | 241,280 | 41,600 | 41,600 |

For k repeated identical uncorrected Gram pairs, encoded ADD cost is
`319488+26240k`, compared with `241280k`; halve and double counts are each
`43264+3328k`, compared with `41600k`. One pair costs 104,448 more additions.
The first integer k giving savings in all three columns is k=2, saving 110,592
additions and 33,280 halves and doubles each. This example demonstrates what
an amortized common code can remove: repeated query traversals on 96 nonpivot
fibers, with all entry/exit work charged. An actual repeated physical consumer
has not been identified. Other uncoded factorizations can amortize as well;
no scalar optimum, runtime speedup or native rank saving follows.

## Identity completion restores a full-dimensional obligation

Let `N=M^-1=U^-t U^-1`. The corrected identity shears require

```
C [I 0; I I] C^-1 = [I 0; N_r M_c I],
C [I -I; 0 I] C^-1 = [I -M_r N_c; 0 I].
```

Hence the omitted lower/upper side terms are
`(N_r-P_r)M_c` and `M_r(N_c-P_c)`. Since
`N-P=U^-t (I-A) U^-1`, and A has eigenvalues 13 (multiplicity eight) and
zero (multiplicity 96), `I-A` is invertible. Each global side term therefore
has full rational rank **10,816**. That is algebraic rank, not a native-child
cost lower bound. In particular, compressing the Gram query to eight pivot
coordinates does not complete the required identity shear on the other 96
independent payload coordinates.

The complete physical bill remains

```
entry/exit native code + coded Gram stages + identity-side completion
+ copied-center physical endpoint correction and wrappers
+ dirty-helper completion + ownership/holding/routing/control
+ precision/recovery/admission costs.
```

Only the formal scalar code/Gram terms above are constructively counted here.
Every other displayed term is unresolved; none is zero by default. Reusing
PR3954's unchanged 208 mass-2576 local calls and progress assumptions retains
its 44,096 excess before added code costs. Replacing those words by this code
changes their native profile and needs a newly derived full gate. The scalar
k=2 comparison does not certify such a gate. Stop dependent native expansion
until one physical repeated consumer and its complete allowance are specified.

## Why a free 13-eigenvalue split is invalid over the dyadic ring

The congruence does not give a dyadic similarity to `13P`. Reduce R into F_13
by `i -> 5` and `1/2 -> 7`. Invertible matrices over R remain invertible after
this reduction because their inverses reduce too. The Gram matrix satisfies
`A^2=13A` but has rank eight modulo 13: `V=[I B]` is surjective and V^t
injective, so `A=V^t V` has rank eight even though its square is zero.
Consequently `A_r A_c=A tensor A` has rank 64 modulo 13 and is nonzero.

For any invertible bank-separate code `(Xhat,Yhat)=(Q X,R Y)`, the two shear
coefficients become `R A_r Q^-1` and `Q A_c R^-1`; their product is similar
to `A_r A_c`. They cannot both become scaled coordinate projectors
`alpha P_r`, `beta P_c` with `alpha beta=169`: that product reduces to zero
modulo 13, contradicting rank 64. The product 169 is forced if these are the
claimed nonzero spectral blocks. This obstruction covers bank-separate
R-invertible codes and this specific full spectral-normalization target.
It does not prohibit all joint codes, general bank-mixing programs, paid
non-dyadic primitives, or other changed graphs. Our explicit U code succeeds
by retaining the nontrivial M couplings.
