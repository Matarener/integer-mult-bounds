# Exact operator and construction proof

Write Q for the common one-axis Gaussian, D for the fresh complement,
R=DQ, and use **H(T)=diag(T,Q^-1 T Q)**. Every actual physical L_i is a
real signed permutation commuting with R, including its absolute phase at
every positive field width. It need not commute with Q or D separately.
Scalar owner coefficients act once; physical address words tensor lift.

## Scalar full120 data

The pinned M has120 rows of squared norm4 and M^T M=60 I8. Put C=MM^T/4.
Thus C^2=15 C and rank C=8. The explicit15-cube partition supplies the
actual native scalar K with K^2=I, K^T=K, KM=-M, and KC=CK=-C.
For A=I-C,

```
E  = K A^-1 = K + C/14,
Ei = E^-1   = K + C.
```

`modes120.py` checks all 14400 entries of both inverse products and of the
actual native K/C compatibility. For T=[M|N], the selected112 columns of N
are actual three-root kernel relations and the first8 rows of T^-1 are
M^T/60. The exact in-place words for T and T^-1 use 7042 ADD,84 SCALE and 91
SWAP each, with no owned fields or paid Gaussian. The program replays both
words, checks both inverse matrices, and checks every kernel condition.

E is executed as physical L normalization, T^-1, SCALE -1/14 on the first8
coordinates, T, K, and L^-1. Ei replaces that scale with -14. These negative
modal scale signs differ from the positive E eigenvalue1/14. The actual
base macro independently replays every emitted elementary code operation
and K output-scratch operation in the common chart, all 14400 entries for
each code. The physical operator is consequently the block matrix
L_i^-1 E_ij L_j. This argument does not commute L_i through Q.

For odd3 define, on the three distinct selector coordinates,

```
Cg = (C1 C2+C1 C3+C2 C3-C1 C2 C3)/2,
Kg = (K1+K2+K3-K1 K2 K3)/2.
```

Cg is zero on fewer than two modal coordinates. It has eigenvalue225/2
on 21504 coordinates with two modal factors and eigenvalue-1350 on 512
coordinates with three. On all these coordinates at least two K factors
are-1; hence Kg=-I there, Kg^2=I everywhere, and Kg Cg=-Cg. In particular,

```
Eg  = Kg + (2/223) C_active2 - (1/1351) C_active3,
Eig = Kg + Cg.
```

The executable code uses A^-1 modal scales -2/223 and1/1351, or A modal
scales -223/2 and1351. The global physical chart is the actual pinned U25
orthonormal basis of the raw27-bit equal-block-parity space. Recoding each
selector repeats the120-field elementary word for each of120^2 fixed
other selector pairs. This is43200 batches per direction, with no tensor
power of owner coefficients. Actual physical L_i are the normalized
q-tuple signed Clifford words of the pinned whole-family constructor.

Kg has76 nonzero coefficients per row, with absolute row and column sums7.
It is applied in each actual 512-owner product cube by allocating512 zero
outputs, accumulating all76 terms per output, then swapping into mains
only after all original inputs have been read. Old main values now in
owned scratch are cleared. This scratch is reused between product cubes.
The base version uses the15 actual8-cubes, four terms per row, and 8 scratch.

## Original-ground query and backward adapter

The owned query reads original ground Y before any backward precode:
normalize L, recode T^-1 on selector axes, COPY all active coordinates,
restore T and L^-1, and pay one full R on each retained mode. To scatter
R C Y into X, normalize/recodify X, add each queried mode times its actual
eigenvalue, and restore. This gives exactly L^-1 T diag(lambda) R T^-1 L Y
= R C_phys Y because L and the scalar owner code commute with R.

No q-support span is used to discount these queries. There are 8 full H9
queries at base and 22016 full H25 queries for odd3. Query fields are owned
temporaries and are cleared after their last scatter. The mode copy is
not counted as a productive original input or a helper contribution.

The actual source-Y native companion is

```
B_K = [[D,-R K],[0,D]].
```

Apply ordinary Ei to Y before B_K. Add -R C Y_original into native X, then
apply ordinary Ei to X. Since K Ei+C=I, the result is

```
WB = [[Ei D, -Ei R],[0,D Ei]] = H(Ei) B0.
```

The second diagonal entry is **D Ei**, not an assertion that H(Ei)'s
second bank is ordinary Ei: Q^-1 Ei Q D = Q^-1 Ei R = D Ei. We only use
[Ei,R]=0. Gathering after preY(Ei) would instead query C Ei Y=14 C Y at
base; this timing error is explicitly rejected. The same spectral
calculation separates the two nonzero global eigenvalues.

## Actual source checkpoint, inverse and linear transpose

The base and cube512 checkpoint compilers consume actual native B event
lists. All Y are source-only, with a single unchanged physical ADD
contact each. Each actual contact is read4 times at base or76 times in
the odd3 cube. Reverse the source-only unary Y pass, and at its contact
COPY that actual Y state into one owned cache. Continue the source inverse
until complete. Reverse X events using these cached contacts, then CLEAR
them after their final ADD read. No original source is assumed reusable
after its overwrite. The free noncommuting-operator replays prove both
inverse orders and the entire owned transpose on all 240/1024 rows.

For the E inverse schedule, first precode X by E. Execute only that actual
native inverse Y pass with contact acquisition; Y now equals Ei times
original Y. Code Y by E to recover original ground Y. Gather/query this
original Y and scatter **+R C Y** into X. Finish the actual inverse X pass
using the retained native contacts, then clear contacts and mode fields.

At the operator level this inverse is

```
WB^-1 = [[D^-1 E, Q E D^-1],[0,E D^-1]].
```

All address primitives have an exact linear transpose: P transposes to its
inverse, D/X and every Gaussian child are symmetric, scalar phase is
unchanged. ADD swaps source/target with the same scalar. The adjoint of
owned CLEAR initializes a zero field; the adjoint of COPY adds the owned
field into the original source and clears the owned field. These are
linear transposes over complex numbers, not Hermitian adjoints.
Every inverse Gaussian child is implemented by its positive child followed
by the ordinary X mask, with absolute phase one at every width.

Put J=diag(Q^2,I). The forward emitted boundary is

```
WF = diag(D^2,D^2) J (WB^-1)^T J^-1
   = [[E D,0],[D E Q^-1,D E]] = H(E) F0.
```

For the first diagonal block, D^2 Q^2 E D^-1 Q^-2=E D because E commutes
R^2. The other two blocks follow directly. Thus the forward word uses the
same paid profile as backward and includes all needed ordinary boundaries.
The small noncommuting-Q fixture independently verifies the full matrices,
all phases and owned lifecycles for all three actual spectral values.

## Three fresh stages and the outstanding terminal

Use three disjoint fresh complements and common Q in F/B/F order. Codes
from one stage commute with the other stages' fresh D operations. The
typed H bookkeeping gives the retained word E3 Ei2 E1. After the standard
signed swap and ordinary positive inverse code, the endpoints are

```
negative original X: Q^-1 (E3 Ei2 E1) D123,
positive original Y: D123 Q.
```

The global positive endpoint is a true H73. Ordinary inversion of the
negative code on its outside cannot be moved through Q. The actual small
64-column three-stage fixture rejects that invalid Gaussian endpoint.
The negative decoder is UNKNOWN, so the conditional two-half target grant
is not an actual caller admission. This package claims no new kappa.
