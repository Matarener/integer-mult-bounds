# The fixed signed quotient and its entire sign family

This is a written proof using finite, exact prefix and suffix certificates.
The specific signed word is independently replayed over the integers and F2.
The family statement below follows from a linear factorization; it is not an
enumeration of its \(2^{47}\) members or a formal-kernel proof.

## Domain and inherited contract

There are 111 sources \(x\), 111 arbitrary targets \(y\), 429 arbitrary dirty
helpers \(h\), and one private register. The public order is \(x,y,h\), with
global indices \(0,\ldots,650\); private register 651 enters and exits at zero.
Every public coordinate is independent. All COPY episodes require a cleared
private register, an immutable physical source and an ERASE of that original
snapshot at its own cut.

The parent is [PR3645](https://github.com/CrocSwap/integer-mult-bounds/pull/3645)
at `99b901c9b5ac70cf441b3d7e585cc7b8744b5359`. Its original R438 input is pinned
at `12fa8c5c844be21bfefb38a19503fbd867a11244`, with identical bytes at scientific
base `20ecf2891d80b5acf18d980b2164fb44ea7faa90`.
The exact source identities are in
[SOURCE-DEPENDENCIES.json](frozen/reviews/integer/SOURCE-DEPENDENCIES.json).
The complete parent construction ancestry and native copied-total ADDRESS
interface remain inherited, with their stated limits.

The checker rederives \(R\) from the actual retained source coefficients after
raw phases D and A, and \(K\) from the actual raw scatter lists. It checks these
against the frozen matrix input. Let \(W\) equal \(K\) with physical rows 0,1,2
zeroed. Then

\[
 A=I+WR,\qquad \operatorname{rank}_{\mathbb F_2}(A-I)=9.
\]

Both binary inverse identities are checked. The binary contract is

\[
 (x,y,h)\longmapsto(Ax,y+Ax,h),\qquad
 (x,y,h)\longmapsto(A^{-1}x,y+x,h)
\]

in the forward and literal inverse orientations.

## The fixed signed endpoint

The candidate differs from the parent in exactly 23 coefficients, each changed
from \(+1\) to \(-1\), among its 47 phase-23 source ADDs. Every other record and
every boundary field agrees. Both words have 16,102 records, 13,223 ADDs, 2,873
MOVEs, and three COPY/ERASE pairs. Their complete paid profile is

\[
 \{1:1298,\ 2:1342,\ 3:79,\ 4:44,\ 5:93,\ 6:11,\ 7:9\},
\]

with 2,876 paid children and rank mass 4,989. Coefficient changes alone do not
improve this invoice.

The independently computed integer endpoint is

\[
 F(x,y,h)=(A_{\mathbb Z}x,\ y+T_{\mathbb Z}x+E_{\mathbb Z}h,\ h).
\]

Every helper is restored literally. The source has no target or helper
dependence; the target self block is identity. Reduction modulo two gives
\(A_{\mathbb Z}\bmod2=T_{\mathbb Z}\bmod2=A\) and \(E_{\mathbb Z}\bmod2=0\).
The inverse is

\[
 F^{-1}(x,y,h)=
 (A_{\mathbb Z}^{-1}x,\
  y-T_{\mathbb Z}A_{\mathbb Z}^{-1}x-E_{\mathbb Z}h,\
  h).
\]

This formula follows from the displayed triangular form and the checked
two-sided integer roundtrip; it does not identify the integer target map with
the binary map.

In particular, the signed word has
\(A_{\mathbb Z}[0,0]=-23\), \(T_{\mathbb Z}[0,0]=-125\), and
\(E_{\mathbb Z}[0,4]=2\). Taking \(x=y=0\) and \(h=e_4\) therefore changes
target 0 by 2 while restoring that dirty helper. It is not an integer pure
source shear. The parent values in the first two entries are \(-21,-121\);
its entire \(E_{\mathbb Z}\) is unchanged by the sign variant.

The dense integer endpoint hashes, including the zero private output row,
are:

| Word and orientation | SHA256 |
|---|---|
| Parent forward | `fb1a055931d7344c66e958e8a73a18b6fdcaa48eac97dada7bcfd204c5847d4c` |
| Parent inverse | `f40e143c64a0a04c93643d2f910b35321e496c59fb3a37f84c16bd0ec6771214` |
| Signed forward | `e153a170456b6aa06022234ccb1d7cdbed64a6703b8e6ed3257cd794d299b079` |
| Signed inverse | `de9764a5d03a609ff8f71cbda97c74cb713bfc8cd1c29bea00843c39d1852eba` |

Each hash encodes 652 rows of 651 signed decimal entries, comma separated,
with LF after every row. Full block hashes and entry witnesses are retained
in [CHECKS.json.gz](frozen/reviews/integer/CHECKS.json.gz); the checker can
emit every nonzero endpoint entry with `--endpoint-out`.

## A fixed transfer certificate for all quotient signs

The 47 phase-23 records form the contiguous interval
`[15228,15275)`, in zero-based indexing. Thus the fixed prefix has 15,228
records and the fixed suffix has 827. The nine quotient coordinates are

\[
 p=(0,1,2,4,8,9,14,30,59).
\]

Let \(U:\mathbb Z^9\to\mathbb Z^{111}\) embed these coordinates, and let
\(P_3:\mathbb Z^3\to\mathbb Z^{111}\) embed target rows 0,1,2.
Let \(Q_\varepsilon\) be the integer 9-by-9 product of the existing 47 ordered
elementary ADDs with coefficients \(\varepsilon_i\in\{-1,+1\}\).
Every such \(Q_\varepsilon\) has determinant one, an integer inverse, and the
same reduction modulo two.

Two exact certificates describe the fixed context.

1. At the prefix cut, the nine quotient values are \(Bx\), for an explicit
   integer matrix \(B\) of shape 9-by-111. There is no target or helper
   dependence. Its columns at the nine selected positions satisfy
   \(BU=I_9\).
2. Propagating a nine-dimensional perturbation on those coordinates through
   the complete fixed suffix gives source perturbation \(U\), target
   perturbation \(P_3L\), and zero perturbation on all helpers and the private
   register, where

\[
 L=
 \begin{pmatrix}
 1&0&0&0&1&1&1&1&1\\
 0&1&0&1&1&1&1&1&0\\
 0&0&1&1&1&0&1&0&0
 \end{pmatrix}.
\]

The first three columns of \(L\) form \(I_3\).
The complete reader \(B\), both transfer hashes, and the determinant-one
minor of \(L\) are retained in the receipt. The suffix transfer was computed
on all nine independent perturbation columns. It explicitly verifies each
COPY and original-snapshot ERASE, including zero private values at both cuts.
The full word independently verifies every frame and snapshot lifetime.

Take any two quotient choices \(Q_0,Q_1\), and put
\(\Delta Q=Q_1-Q_0\). Immediately after the quotient, their difference is
\(\widehat U\Delta QBx\), with \(\widehat U\) embedding the source coordinates
in the full public/private state. Applying the fixed suffix certificate gives

\[
 \boxed{
 \Delta A_{\mathbb Z}=U\Delta QB,\qquad
 \Delta T_{\mathbb Z}=P_3L\Delta QB,\qquad
 \Delta E_{\mathbb Z}=0.
 }
\]

All other public blocks are unchanged. These are integer matrix identities,
so they hold over every commutative ring by interpretation of the coefficients.
The legal snapshot conditions also hold for every choice: the fixed suffix
never mutates an open snapshot source or the private copy, and the transfer
identities preserve its zero/restore cuts.

This proves the following for the entire \(2^{47}\)-member sign family:

- Every source depends only on \(x\); source differences are supported on the
  nine selected source rows.
- Target differences are supported on physical target rows 0,1,2.
- The target self block remains identity; \(E_{\mathbb Z}\) is unchanged and
  even; all 429 arbitrary helpers and the private boundary are restored.
- Every quotient, hence the source code, is an invertible integer
  elementary-matrix product. Reduction modulo two preserves the parent's
  complete binary contract.
- The ordered gate destinations, frame paths, immutable snapshots and paid
  histogram are unchanged.

Over \(\mathbb Q\), injectivity of \(U,P_3\) and the right inverse \(BU=I_9\)
give the exact identities

\[
 \operatorname{rank}(\Delta A_{\mathbb Z})
   =\operatorname{rank}(\Delta Q)\le9,\qquad
 \operatorname{rank}(\Delta T_{\mathbb Z})
   =\operatorname{rank}(L\Delta Q)\le3.
\]

For the particular signed witness versus its parent,
\(\det(\Delta Q)=1024\). Thus its source delta has rank 9. Since \(\Delta Q\)
is invertible over \(\mathbb Q\) and \(L\) has rank 3, its target delta has
rank 3. Those exact ranks apply to this pair; another sign pair can have
smaller rank, including zero.

The same difference formula describes any substituted 9-by-9 integer
quotient matrix. Its invertibility, binary endpoint and implementation cost
would require their own hypotheses; that algebraic extension does not supply
a 47-ADD circuit for arbitrary matrices.

## Exact scalar prefix norms and attaining inputs

For a fixed orientation let \(M_t\) be the 652-by-651 integer coefficient
matrix after prefix \(t\), with the private input fixed at zero. MOVE preserves
scalar values, ADD applies its signed row operation, COPY duplicates the
source row, and a validated ERASE clears the private row. Induction gives the
exact scalar operator at every cut.

For real scalar inputs,

\[
 \|M_t\|_{\infty\to\infty}
   =\max_i\sum_j |(M_t)_{ij}|.
\]

The upper inequality is the triangle inequality. For a row attaining the
maximum, choose input \(u_j=\operatorname{sgn}((M_t)_{ij})\), with zero for a
zero coefficient. Then \(\|u\|_\infty=1\) and the selected output equals the
row's sum of absolute coefficients. The receipt supplies the entire concrete
sign vector and selected coefficient row, and a separate scalar replay
checks attainment.

| Word | Forward maximum | Literal inverse maximum |
|---|---:|---:|
| Parent | 34,285 | 5,839,860 |
| Signed quotient | 80,639 | 239,014 |

For the signed forward word, global register 1 after record 15,885 attains
80,639. For the signed inverse, global register 220 after processing original
record 5,651 in reverse order attains 239,014. Every record index is zero
based. All four parent/candidate maxima have complete attaining witnesses.

The isolated quotient maxima are 442 forward / 75 inverse for the parent
and 7 forward / 9 inverse for the signed quotient. Improvement of that small
block does not imply that both complete-word maxima improve: the complete
forward maximum increases.

## Coverage and open implications

The finite computation reconstructs every integer and F2 public input column
in both orientations, two integer roundtrips for each word, all helper and
target blocks, every frame visit, all paid children, and exact snapshot cuts.
Unbounded Python integers and exact integer rank operations are used.
The all-sign theorem is the written linear consequence of the finite fixed
prefix/suffix certificates.

The scalar cancellation bound is not a bound for an unproved native vector
realization with address-dependent operators. No theorem on native child
errors, rounded cleanup, precision reserves, physical ownership, source
access, storage, tape costs, terminal decoding, recursive callers or joint
outer assembly follows here. The historical PR589 precision formulas have
not been transferred to this changed source interface. No new supplier or
kappa admission, unrestricted sign optimum, or formal-kernel verification
is claimed.
