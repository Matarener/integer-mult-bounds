# One coefficient of the unfactored J cleanup

This result concerns the diagonal-continuation prefix with its actual
`F J` public/output gauge. It does not undo the two factories separately,
does not change the source codes, and does not credit a coupled helper
matrix as independent stock. The caller lane owns the literal physical
prefix and original-column binding. The algebra below states the exact
interface required for the gate.

Take `q>=2`, `n=2q+2`, `k=2q+1`, `m=4q+4`, and any chunk `f>=1`.
All operators are the actual Gaussian-dyadic operators of the frozen
`EVEN-PARITY-SOURCE.json`. In particular

    N=N0, N^2=-I,
    J_f=i^(f+1) Z product_bit(C_(p0+p1) C_(q0+q1)), J^2=-I,
    A=N^-1 J, B_s=P_s A,
    Q1=J^-1 B1 J, F=product_(j=1..k) Nj.

`P_s` is the actual whole-plane ADDRESS swap `(0,s)`. No source code
`B_s` is removed or replaced by the corresponding `P_s`.

## The joint inverse has a single Clifford coefficient

Let `(t0,k0)` be the two original pivot inputs. Put

    K = [[B2+Q1-I, I-B2],
         [Q1-I,       I]].

The exact terminal pivot rows, in current order `(U,V)`, have homogeneous
matrix

    H = diag(Du,Dv) [[K_row2],[K_row1]],
    Du=(B_(2q)...B4) B3 J,
    Dv=(-1)^(q-2) (P_(2q+1) N)...(P5 N).

The full matrix also includes its arbitrary public-reader block `L`.
It is essential that `L` is retained. Reordering publics before pivots,
the physical prefix is

    diag(F,...,F) [[diag(J,...,J),0],[L,H]].

The output contract asks for `F J` on each original independent input.
Thus the pivot part of its unique linear cleanup is, before the common
`F` conjugation,

    [ -J H^-1 L diag(J^-1,...,J^-1),   J H^-1 ].

This equation accounts for every public column. It does not specialize
the public inputs to zero.

Writing `d=B2^-1(y1-y2)`, the equations `y=K x` give
`x1=Q1^-1(y2+d)` and `x2=x1-d`. Therefore

    (K^-1)_11 = Q1^-1 B2^-1.

The coefficient from the **current V field to the output on original t0**
is consequently the single Clifford operator

    C = F J Q1^-1 B2^-1 Dv^-1 F^-1.                  (1)

It is independent of `L`. Joint scheduling of the core, the factories
and the readers cannot replace this coefficient while retaining the
same complete input/output map. Additional dirty banks restored to
their entering values do not change it. Left monomial output gauges
only permute and rescale its rows, preserving their support sizes.

The producer checks the core inverse in both orders over a free
noncommutative operator algebra. It then checks all six original
columns of an arbitrary-public-coupling fixture with eight independent
noncommuting `L` coefficients. Reversing the order of `Q1^-1` and
`B2^-1` is rejected on those columns.

## Exact arity and phase for every q and f

The identities `B_s J=P_s N` and `J B_s^-1=N P_s^-1` are phase-exact.
They reduce (1) to

    C = F A^-1 P1^-1 N P2^-1 Dv^-1 F^-1.            (2)

Consider one p or q half and one bit coordinate. Write `S(Gamma)` for
the binary X shear and write a permutation to its right. Then

    N: Gamma=e0 e0^T,
    J: Gamma=(e0+e1)(e0+e1)^T,
    A: Gamma=e0 e1^T+e1 e0^T+e1 e1^T.

The product `A^-1 P1 N P2` has left shear
`e0 e1^T+e1 e0^T` and permutation `P1 P2`. The left native support of
`Dv` is the distinct odd fresh planes `5,7,...,2q+1`. Taking its inverse,
then multiplying by `P1 P2`, puts that support on plane2 and the odd
fresh planes up to `2q-1`. Finally conjugating by `F` adds the two
diagonals at common0 and final fresh `2q+1`. Thus the left shear of C is

    [[1,1],[1,0]] on planes(0,1),
    [1] on plane2,
    [1] on each odd fresh plane5,7,...,2q+1,
    zero on the remaining planes.

The first block has rank2. The other `1+(q-1)` diagonal blocks are
disjoint, so the rank is `q+2` on each half and bit. Hence

    native arity(C) = (2q+4) f.                     (3)

This is an all-q rank proof. The producer independently extracts the
actual Clifford's `Gamma=B P^-1` and checks this entire matrix, rather
than only its rank, for `q=2..12`, `f=1,2`.

The actual global phase is also retained. After bit regrouping,
`N_f=i^(1-f)N_1^tensor(f)`, `J_f=i^(1-f)J_1^tensor(f)`, and `A` has
no extra phase. The sign in `Dv` is once per field, so

    Dv_f=i^((3q-5)(1-f)) Dv_1^tensor(f),
    C_f=i^((6-3q)(1-f)) C_1^tensor(f).               (4)

The producer verifies (4) in the exact phase-sensitive tensor algebra
for all four chunk residues, at `q=2,3,4`; the displayed factor count
proves it for every q and f. Actual signed tableaus and independent
Gaussian column amplitudes also verify the unsimplified and simplified
operators. No f1-only phase extrapolation is used.

## A native-rank/ADD support tariff for the complete tail

This paragraph is a circuit-model statement with explicit primitive
costs. It is **not** an assertion that a bounded-in-f scan count is a
default hypothesis of the selected multiplication theorem.

For any matrix `T`, let `s(T)` be its maximum number of nonzero entries
in a row. Exact Gaussian cancellations can only decrease this number.
For any rectangular composable matrices,

    s(T U) <= s(T) s(U).

Apply this to the full bank-by-address linear operator, including every
extra dirty or private bank. Physical monomial ADDRESS maps, conditional
bank/address permutations, nonzero Gaussian pointwise scales and phase
maps have row support1. A literal binary ADD scan
`dst += coefficient * monomial(src)` has row support at most2. A native
rank-r Fourier child on one bank, with arbitrary physical monomial
adapters, has row support exactly `2^r`.

A Clifford with binary B-rank r has exactly `2^r` nonzeros in **every**
row. One proof uses the stabilizers of `U^dagger |y>`: the n-r independent
Z stabilizers constrain an affine support of dimension r, and the X
translations act transitively there. All amplitudes have the same
nonzero magnitude. This applies to C with its mandatory actual phase.

Let the tail use actual native arities `r_1,...,r_h` and `S` literal
binary ADD primitives. Starting from the identity input matrix, the
maximum final row support is at most `2^(sum r_j+S)`. Its required
V-to-original-t coefficient already has `2^((2q+4)f)` nonzeros in each
row by (3). Consequently every such complete tail satisfies

    sum_j r_j + S >= (2q+4) f.                      (5)

This includes arbitrary Gaussian ADD coefficients, arbitrary monomial
controllers depending on f, any number of arbitrary extra dirty banks,
and their exact restoration. Initially zero private rows also do not
break the induction. The output coefficient is a submatrix of the full
operator, so it cannot have more support than a full row. No comparison
of only a two-bank intermediate product is used.

An operator-valued bridge with a sum of monomial terms must expose its
binary ADD primitives or charge its actual row branching. It is not one
free scalar ADD merely because its formula is compact. A native child
wrapped as an additive query must likewise expose its delivery ADD;
the query itself here is the one-bank Fourier transform.

If the total native arity is `R f` and `S=o(f)`, (5) gives `R>=2q+4`
asymptotically. In particular the prefix's positive-deficit requirement
`R<2q` fails in that regime, even for an unfactored core/reader cleanup.
More generally, any `R<2q` requires

    S >= (2q+4-R) f > 4f.                           (6)

Equation (6) leaves a paid O(f)-scan construction open. Whether growing
full-volume scans fit the selected supplier's outer allowance is the
parent's separate source-bound transfer obligation. Partial scans,
local fusion and changed contraction/precision models must be priced
under their actual volume and are not excluded merely by calling them
scans.

## Exact scope and constructive escape

This gate covers the given initial K core, the given diagonal recurrence,
and the actual `F J` targets on the original independent columns. It
does not cover a different initial core or changed input right charts,
different full-native target operators, coupled partial-helper endpoints,
nonlinear encodings or a different primitive alphabet. Merely renaming
the two coupled factory rows as independent stock is not such a change.

One concrete reopening must alter the Schur inverse coefficient
`Q1^-1 B2^-1` before the large Dv suffix is formed, or replace the
terminal owner contract so that output on original t0 is not required to
be `F J t0`. A cross-cut delivery/core rewrite that changes that exact
original-column equation is a material new construction; a larger
monomial alphabet only inside a cleanup of the fixed map is still
subject to (5).

The result is written all-parameter mathematics with finite exact
corroboration and explicit source pins. It is not a formal-kernel proof,
an admitted all-size supplier, a precision/tape construction or a new
kappa claim.
