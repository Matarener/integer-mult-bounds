# The R429 code in the actual nine-stage BIT caller

This is a finite exact counterexample and two explicitly restricted repair
screens. It supplies no successful routed decoder, supplier admission or
positive kappa. The complete current coded word, its expected receipt and its
proof are frozen under `inputs/`; their original scientific pin is
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`.

The question is whether the three-COPY R429 word can replace the local calls
of the pinned `global_k.py` recipe while preserving the required public BIT
endpoint. The answer for direct substitution, even with a terminal free
decoder, is no. The failure is on public data, independent of helper dirt.
This conclusion does not exclude a changed caller with paid native repairs.

## The exact local and caller contracts

There are 111 arbitrary source fields, 111 arbitrary target fields and 429
arbitrary dirty helper fields. One private field starts and ends zero.
The frozen forward word has binary VALUE endpoint

    F_A(x,y,h) = (A x, y+A x, h),

and its literal inverse is

    F_A^-1(x,y,h) = (A^-1 x, y+x, h).

Sources enter at their actual distinct rank-one port lines and finish at
FULL. Target p enters at zero and finishes at the cap orthogonal to port p.
Every surviving helper is restored in logical coordinates and makes its
declared full physical progress. These physical endpoints are part of the
contract; helpers are not restored to their original ADDRESS arrangement.
Over the integers the literal source code is unimodular and the target
contract is only asserted modulo two. No integer endpoint or rounded cleanup
bound is inferred from the binary formulas below.

The checker replays every frozen record on all 651 independent ordinary
columns, including the private lifetime comparisons. It reconstructs A and
its actual inverse independently. The exact scalar facts are

    order(A)=28, rank(A-I)=9, rank(A^2-I)=8,
    identity rows of A = {0,1,2}.

The controller has four public pairs and uses the exact `recipe(4)` extracted
from the pinned source. With pair `(x_p,y_p)`, its local scalar actions are

    forward: (x,y) -> (A x, y+A x),
    reverse: (x,y) -> (x+y, A^-1 y).

Bridges and the final pair exchanges are unchanged. All 888 public scalar
columns are replayed. A second computation over the Laurent ring
`F2[a,a^-1]` constructs the entire 8-by-8 bank matrix; substituting `a=A`
must agree with the first computation entry by entry. The full Laurent
matrix and all nine chronological scalar endpoint hashes are in
`RESULT.json`. The final scalar defect has rank **63**. Setting A to I
restores all 888 columns. Replacing the literal inverse by A changes the
actual caller and is rejected as an equivalent endpoint.

In particular, let only the initial target of the last pair, y3, be nonzero.
It is never read by an earlier local call. It reaches reverse stage 7 and
forward stage 8, followed by the backward bridge chain and final exchanges.
The resulting scalar output is

    x0=x1=x2=x3=(A+A^-1)y3,   y3=A y3,
    y0=y1=y2=0.

These are complete arbitrary-field coefficient identities, not tests of a
single binary input. The first residual has rank eight. Already constant
VALUE arrays therefore disprove direct substitution irrespective of ADDRESS
routes or precision choices.

## Actual chronological ADDRESS operators

The following notation denotes operators on binary VALUE arrays induced by
ADDRESS permutations. It does not identify differences of VALUE permutation
operators with differences of their ADDRESS matrices.

Let N be the diagonal rank-one exchange on the actual port roots. Let G0
exchange each port's original seven-dimensional cap, and let Gs, s=1,...,8,
exchange the fresh seven-dimensional coordinate block of stage s. Then

    Fs=N Gs,    T=N G0 G1 ... G8,

where T is the required full 64-dimensional parent exchange. The Gs and N
commute. For s>0 the actual source route rho_(s,p) fixes the port root and
interchanges its core cap with fresh block s. Its cap isometry has columns
from the pinned native chart. Write

    A_s = diag(rho_(s,p)) A diag(rho_(s,p))^-1.

A_s is HEAD/TAIL-separated. It commutes with Fs and with every Gt, t != s.
The latter statement includes G0: conjugating the old cap by rho_s makes it
the same fresh coordinate block for every port. A_s generally does not
commute with N. These are the native route relations already distinguished
in the credited C511 interface proof; no order-511 fact is transferred to
the order-28 code.

The actual physical forward and role-swapped inverse are

    B_s = [[Fs A_s N, 0], [Gs A_s N, Gs]],
    R_s = [[Gs, Fs], [0, Gs A_s^-1]].

The inverse formula uses Fs A_s=A_s Fs. No step moves A_s through N.

Let L6=G0...G6. On the untouched entering last target, the state before
stage 7 is `(0,L6 y3)`. Applying the two local calls gives

    R7:  (F7 L6 y3, G7 A7^-1 L6 y3),
    B8:  (T A8 y3, (G0...G8)(A8+A7^-1)y3).

For example, `N F7=G7`, and A8 commutes with G7 and L6. These are the
commutations needed in this calculation. The final backward bridges copy
the second component to all four source banks. After final exchanges and
factoring off the required full parent T, the last-target column is

    x0=x1=x2=x3=N(A8+A7^-1)y3,   y3=A8 y3,
    y0=y1=y2=0.                                      (1)

This is the native counterpart of the preceding Laurent column.

## One integral native impulse and the free-decoder obstruction

The actual roots at ports 0 and 3 are `2e0` and `2e3`, and the reconstructed
code has `A[3,0]=1`. Give the initial last target at port 0 one VALUE impulse
with

    HEAD=e59, TAIL=0.

Axis 59 is the third coordinate of fresh stage-8 block 57,...,63.
The checker reconstructs the actual two port charts from the frozen full
120-root geometry using the upstream Weyl breadth-first route convention.
It verifies their cap isometries and rho squares exactly. The actual
root-zero chart has cap columns e1,...,e7, so

    rho_(8,0)e59=e3,   rho_(8,3)e3=e3.

Every stage-7 chart fixes e59. Consequently the A8 term in (1), at output
port 3, sends the input to HEAD=e3; the following N sends it to

    output port 3: HEAD=0, TAIL=e3, VALUE coefficient 1.       (2)

The A7^-1 term keeps its entire input on HEAD=e59 and TAIL=0, so it cannot
cancel (2). There is only one A8 coefficient path from the chosen input
port to output port 3. Earlier stages cannot contribute another path:
the initial y3 was untouched until stage 7.

This witness uses only integral displayed coordinates and survives in every
odd ADDRESS field. It is also stable under cap-gauge changes: replace e59
by the fresh-block vector `a_0^T e3`, where a_0 is the root-zero cap
isometry. Then `rho_(8,0)(a_0^T e3)=e3` and the same argument applies.
Changing latent bases for the factorization A-I does not change A[3,0].

Let U denote VALUE arrays supported on TAIL=0 across all public banks and
ports. Scalar mixing and HEAD/TAIL-separated ADDRESS routes preserve U.
Every invertible decoder made from these operations, and its inverse,
preserves U, so it induces an invertible map on the quotient by U.
The nonzero quotient output (2) cannot be erased by such a decoder.
The decoder may mix every bank and port; invertibility is what prevents
a nonzero quotient class from disappearing.

This is a terminal free-alphabet obstruction. It does not prohibit a
decoder that makes further native exchanges, accesses another observation
cut or changes the earlier caller word.

## Why scalar involutivity does not fix the inverse-kernel mismatch

Appending the literal source inverse at local FULL costs 1,499 additional
scalar ADDs and no additional native query rank. It makes the physical
source-preserving local shear

    B'_s = Gs [[I,0],[A_s N,I]].

Its literal inverse with exchanged public roles is

    R'_s = Gs [[I,N A_s],[0,I]].

At one fixed stage, involutivity of A_s would make `N A_s` the inverse of
`A_s N`. Consecutive caller stages use A7 and A8, which are differently
routed operators. The last-pair column of the source-restored variant,
after factoring off T, is instead

    x0=x1=x2=x3=N(A8 A7+I)y3,    y3=A7 y3.              (3)

Choose y3 so that its port VALUE vector is `A^-1 e0`, all at HEAD=e59 and
TAIL=0. A7 acts as the scalar A on this fresh block and hence produces
the single port-zero impulse above. The identity contribution in (3)
stays on the fresh block and has zero TAIL. The A8 contribution again
gives (2). This argument needs only invertibility, so it also excludes
the proposed scalar-involutive repair of this unchanged caller whenever
the code retains that off-diagonal edge.

It does not exclude a newly built physical inverse kernel which uses the
previous stage's routed operator. Such a kernel is not supplied by the
same local scalar code at the next fresh stage and needs its own complete
literal word and cost.

## Two priced, restricted repair screens

First consider restoration to the original local shear before entering the
unchanged caller, using exactly nine independent scalar latent readers and
one common-cap completion per reader. Reconstructing the original retained
totals gives the actual rank-nine R and K. The R429 code satisfies

    A-I=W'R,    W'=K with physical rows 0,1,2 set to zero.

Both W' and R have rank nine. Thus every minimal nine-reader factorization
has nine independent output directions in the column space of W'. The
checker enumerates all 511 nonzero directions over F2 and computes their
actual root-support rank over the rationals:

| Root-support rank | Number of directions |
| --- | ---: |
| 7 | 12 |
| 8 | 499 |

The twelve rank-seven coefficient vectors are

    135,185,205,208,238,336,349,415,425,437,503,507.

The original nine rows of RK are an independent rank-seven basis. In the
declared common-cap tariff, where one completion must cover the root span
of its output direction, every reader therefore costs at least seven:
the repair rank is at least **63 per restored local call**. This is a
necessary price, not an emitted endpoint decoder. Actual capped-target
access and restoration can cost more. For a positive power exponent,
`Phi_b(7)=7(64/7)^b > 7`, so the tariff only increases.

The parent budget screen leaves less than 58.383 tariff units per coded
call at the requested 10-percent target. A per-call repair in this exact
minimum-basis common-cap class cannot meet that budget. This is not a
bound for a single shared decoder after all nine calls, overcomplete
readers, ADDRESS-dependent readers or a different native query alphabet.

Second, suppose one changes the source code to a routed code C commuting
with N, while retaining the clean map J on every target row outside a
small set P. Each unchanged off-diagonal entry `J[p,q]=I`, p != q, would
force

    Np C[p,q] = C[p,q] Nq,  hence Np=Nq.

The actual port projectors are all distinct. The checker supplies one
noncommuting off-diagonal edge and an exact unequal projector entry for
**each of the 111 rows of J**. Thus no row of J can remain unchanged in
an N-commuting code. In the prior one-snapshot-per-repaired-row interface,
this requires at least **111 rank-one snapshots**. In particular the
three-row repair does not survive a free replacement of its off-diagonal
identity coefficients by root-intertwining ADDRESS routes.

This second count covers that physical-row repair interface. A combined
repair with different output directions or a changed clean factory is a
different construction and is not lower-bounded by 111 here.

## Construction search boundary and exact local inverse decoder

The cheapest concrete exact endpoint repair found algebraically for one
physical coded call is the decoder identity

    B_clean B_A^-1 = [[A^-1,0],[N(A^-1+I),I]].

It separates the source inverse from the missing target operation but
does not implement the latter cheaply. Its rank-nine scalar factorization
does not make nine native queries sufficient at rank one: N acts at each
destination's different cap. Conversely, merely rebasing the nine latent
readers cannot lower the preceding common-cap support floor below seven.

The requested next step is therefore a new, explicitly charged routed
realization of that operator or a changed coupled caller. No favorable
upper bound was found. The calculation must not be turned into either a
63-unit universal lower bound or a zero-cost scalar decoder.

One tempting chart-sharing mechanism has an already known paid failure.
For `H_p=rho_(t,p)rho_(s,p)`, one has `H A_s H^-1=A_t`, but H also
transports the completed fresh block Es to future block Et. Therefore

    H^-1 D_Et H D_Es = D_Es D_Es = I,

where the required combined progress is `D_(Es+Et)` of rank fourteen.
The equality follows from orthogonal cap isometries: rho_s sends a vector
in Es to the core cap and rho_t sends that core vector to Et. Thus the
specific alignment/query/unwind word loses both seven-dimensional advances
on each affected family. It cannot be billed as sharing two completed
native advances. This is the prior R429 calculation retained in
`inputs/R429-PHYSICAL-CODE-REFERENCE.py.txt`, whose word hash matches this
package; it is credited rather than claimed as new. Its larger commutant
and orbit searches are not run here or used as proof premises.

## Reproduction, controls and remaining obligations

Run from any working directory:

    python3.12 -I -B -Werror /absolute/path/to/composition/check_composition.py

The checker needs only the standard library. It authenticates all runtime
inputs by SHA256, reads the frozen coded word, executes the pinned recipe
and compares `RESULT.json` without writing. `--output PATH` explicitly
emits a recomputed receipt. It rejects an incorrect inverse and deletion of
the actual code edge used by the native witness. The identity-code control
restores all 888 public scalar columns. Normal and optimized runs should
emit identical receipts.

The finite all-column replays, all-511 rational census and exact native
witness are separate from the written operator and free-decoder arguments.
There is no formal-kernel proof. The original local helper/COPY restoration
is retained; no new chronological owner schedule, rounded child-error
bound, physical source/tape implementation or joint complex/BIT transfer
is supplied. A positive result still needs those obligations.

Credit the retained R438 word and transport/rehosting lineage, the frozen
R429 three-source-snapshot construction, and the C511 mutable-source
interface/observation work for its physical inverse and freshness lessons.
The historical R429 physical-code source supplies the chart-alignment
coverage-debt predecessor. The old sources are copied as references, not
executed or treated as certificates for the changed caller. This note contributes the exact
nine-stage R429 column, fresh-stage last-pair witness and restricted repair
screens. Prepared with substantial OpenAI Codex assistance; Apache-2.0.
