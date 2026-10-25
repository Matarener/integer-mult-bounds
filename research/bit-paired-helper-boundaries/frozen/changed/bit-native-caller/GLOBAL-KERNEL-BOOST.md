# Exact common-plane helper kernel construction

The local construction is exact, but its old CLEAN variant cannot retain a
positive uncovered dividend in a uniform common-prefix bank caller. No new
kappa is asserted.

Scientific pin: `20ecf2891d80b5acf18d980b2164fb44ea7faa90`. The two producers
read only pinned predecessor words. Every output is in this lane.

## Literal helper transformation

Let D be the actual111-by-R binary helper-to-target dirty matrix. It has
rank111 for both the R429 FULL box and old R438 CLEAN box. Choose111 original
pivot columns. Each remaining column j is the XOR of a specified set I_j of
pivot columns. Write

`S=I+sum_(j dependent,i in I_j) E_(i,j)`.

Since every destination i is a pivot and every source j is dependent, the
off-diagonal part has square zero over the integers. All setup ADDs commute,
and replacing their signs gives the literal integer inverse. D*S modulo2 has
unchanged pivot columns and zero dependent columns.

Give each dependent helper entrance E, keep each pivot entrance ZERO, and
retain FULL exits. Execute initial compensation only from pivot columns at
ZERO. Lift pivots to E, execute S at common E, and replace every later old
frame f by its actual rational span(f,E). Execute S^-1 at FULL. Every forced
public climb is in the emitted word. The dependent helpers are never read at
ZERO.

For an arbitrary physical helper u, its logical entrance variable is
`h=D_E^-1 u`. All public dependence on h cancels. Thus the physical helper
residual is `D_FULL D_E^-1`; interpreting arbitrary dirt this way does not
require an executed entrance query. A chronological owner implementation
must route that paired residual. Our coordinate E has a literal coordinate
permutation route for E-perp. Requiring the predecessor's ZERO logical-dirt
identification instead would add the removed entrance queries; that is an
additional restriction rather than an intrinsic price of this contract.

## Exact finite results

For E=span(e0,e1), `global_kernel_boost.py` emits the R429 FULL variant:

- 318 width6 helpers and111 width8 helpers, zero private fields;
- H={1:1184,2:1254,3:108,4:89,5:7,6:9}, mass4461=5097-636;
- all651 binary VALUE columns, exact integer source/helper restoration and
  literal inverse;
- unchanged source rank1 entrances/FULL exits and target ZERO/FULL cuts.

`old_kernel_boost.py` emits the old R438 CLEAN variant:

- 327 width6 helpers and111 width8 helpers;
- all nine copied totals paid, with tariffs6,6,6,6,5,6,6,5,6, sum52;
- one zero private field reused for the nine snapshots and literally erased;
- H={1:1170,2:1254,3:108,4:94,5:13,6:16}, mass4539;
- all660 binary VALUE columns, integer source/helper rows, literal inverse;
- 83 old target caps enlarged to FULL, with every changed public path saved.

The two scripts reconstruct semantic dirty columns independently. In the old
word they also compare the semantic result to every literal original
compensation column. No syntactic dirty-support count substitutes for that
test.

## Actual rational ADDRESS moves

For every used joined frame U, the receipts include a rational basis, its
Gram determinant and the exact orthogonal projector P_U. Every MOVE checks
nesting, `P_U P_E=P_E=P_E P_U`, and the idempotence and exact rank of
`W=P_U-P_E`. A stored invertible rational matrix C obeys

`C diag(I_rankW,0) C^-1=W`.

Consequently the complete16-by-16 ADDRESS identity is

`diag(C,C) D_coord(rankW) diag(C^-1,C^-1)=D_W=D_U D_E`.

This is a symbolic exact matrix proof covering every ADDRESS column, rather
than a scalar-rank tariff substitution. Finite excluded primes are2,3,5.
Some joined projectors have odd denominators. These explicit GL adapters do
not silently import a narrower orthogonal/dyadic recursive-query compiler;
compatibility with the chosen conditional native alphabet, its scalar scans,
source access and tape invoice remains a separate admission obligation.

## Why the old hybrid does not give a dividend

Let epsilon_p=1 if E is not contained in target cap K_p. With
`N=D_Pp`, `N^2=I`, and fresh cap progress G, the normalized per-port map is

`F_epsilon=[[I,0],[N^(1-epsilon),N^epsilon]]`.

Each epsilon1 target FULL lift is already paid locally. The epsilon0 ports
are the only potential unpaid common-rank ports. For the seven leading
coordinate E choices of ranks1 through7, the exact pair
(remaining cap ports,total copied-total query rank) is

`(56,56),(28,52),(12,44),(11,35),(3,27),(2,18),(1,9)`.

Even granting one unpaid common output per remaining cap port per call,
rank1 gives zero available deficit and ranks2 through7 give negative
deficit. Equivalently, in a bank-GL caller put d=N+I, d^2=0. Every hybrid
query contributes one rank-one bank coefficient to the linear d term.
Obtaining N on n banks requires a sum of rank-one matrices equal to I_n,
so k>=n. No chronological helper-owner assumption is needed for this
necessary rejection.

For clarity, the three-call F/B/F seed has maps

`epsilon0: [[0,N],[N,0]]`,

`epsilon1: [[I+N,N],[I,I+N]]`.

The epsilon1 matrix squares to N I2, but using that extra word does not
remove the already paid FULL target exposure. This is not a positive caller.

## Selective variants and source snapshot control

`selective_boost_screen.py` computes a causal OR propagation model. An E
promotion propagates across a scalar gate below E and stops once the old
frame contains E. This allows changed later public source paths. It also
permits a nonzero compensation residual at common E on cold target ports,
provided those target promotions have no additional exposure.

All162 leading-coordinate planes of ranks1-4, and all120 actual E8 root
lines plus153 actual rank2 frames, have zero kernel on their zero target/COPY
exposure helper set, even after the stated cold-target quotient. This is a
finite scoped screen, not an obstruction to retimed words or other planes.
The single exposure-mask cohorts in the native screen have best rank-mass
saving-7; unions of exposure classes were not enumerated.

Isolating immutable A-phase source reads with snapshots gives additional
kernel nominations. The cheapest tested example is helper pair444,474 at
live root77 (frame79), whose remaining exposure is source57. Source57 never reaches that
root during its immutable A phase. At its relevant rank1 read, a snapshot
must climb to span(P57,P77) and return before erasure, costing two rank1
queries. The helper saves only one entrance rank. That corridor increases
rank mass by1 and is not promoted to a supplier.

Reproduce with `python3` and `python3 -O`, adding `--write` only to regenerate
this lane's saved receipts:

```sh
python3 global_kernel_boost.py --rank 2
python3 old_kernel_boost.py --rank 2
python3 selective_boost_screen.py
python3 selective_boost_screen.py --native
```

No chronological owner, rounded suffix-error, full source/tape or all-size
outer theorem is supplied by this package. The underlying R438, E8 and R429
word ancestry retains its original authorship. This lane supplies the
changed entrance basis, exact joined word, paired residuals, actual ADDRESS
charts and explicitly scoped negative caller screens. Substantial OpenAI
Codex assistance; Apache-2.0.
