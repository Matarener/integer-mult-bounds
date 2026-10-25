# Three copied source pivots for the actual R438 local word

This is a finite, source-pinned local construction over F2, an exact signed
integer lift, and a conditional native cap calculation. It is neither a formal
kernel proof nor a complete recursive supplier or multiplication theorem.

## Registers, frames and endpoint

The final word has 111 sources x, 111 arbitrary targets y, 429 arbitrary dirty
helpers h and one owned private copied field. All 651 public input columns are
independent. Its construction first uses the 438-helper, 660-column source
word and then deletes nine literally unread physical families as proved below. The private field is zero outside its immutable snapshot
lifetimes. Sources enter at their actual port lines P_p, targets and helpers at
frame zero. Sources and helpers finish at FULL; target p finishes at its actual
cap K_p=P_p-perp. These are the original R438 boundary frames.

For the explicit invertible binary matrix A constructed below, the new forward
endpoint is `(x,y,h) -> (Ax,y+Ax,h)`. Its literal inverse is
`(x,y,h) -> (A^-1 x,y+x,h)`. The source endpoint is changed. Original theorems
requiring an unchanged source cannot be applied without proving the new caller
contract. Complemented physical backward-call interpretation and the complete
compiler remain separate obligations.

## Delete centres and rebuild the zero-frame compensation

Replay D then A of the actual pinned word. The nine retained helper totals are
`R x+T h`, with R of shape 9-by-111. Let K be the actual 111-by-9 scatter matrix.
No original gate reads a target. The complete row masks of M=RK are
`507,135,238,349,185,437,205,503,425`. Both M and R have rank 9, while
N=I+M has rank 6.

Delete the nine centre COPY/ERASE episodes and their target scatters. Over F2,
this changes the original target `y+x` by `KR x+KT h`. Replace its original
zero-frame compensation by `D_new=D_old+KT`. Duplicate helper-to-target gates
cancel at frame zero: 5,758 ADDs replace 18,030. Every original public frame
visit is retained, including empty-source visits. The resulting clean-centre
word has endpoint `(x,y,h) -> (x,y+Jx,h)`, where J=I+KR and rank(J)=108.
The verifier derives R,K,J from the literal original word and checks every
public input column; it does not assume a model scatter matrix.

## An invertible source code with three actual repaired target rows

Let C0 be a basis of the left nullspace of N, with emitted row masks
`39,193,272`. Let P select physical target coordinates 0,1,2 and S=RP.
The 3-by-3 matrix C0 S is invertible. Define

```
B0 = (C0 S)^-1 C0.
```

Thus B0 S=I and B0 N=0. Let D be rows 0,1,2 of K. Delete these rows
from K to form W=K+PD, and define

```
Y = N + S D,           A = I + W R,          Q = P B0 R.
```

The actual row masks of Y are `10,373,282,165,176,405,356,145,166`, of rank 9.
A fixes kernel(R) and induces the invertible map Y on the quotient identified
by R: RA=YR. Thus A is invertible. Equivalently, if Ax=0 then YRx=0, so
Rx=0 and Ax=x=0. Both matrix inverse identities are also checked finitely.
Rows 0,1,2 of A are exactly their identity rows. Since B0Y=D,

```
QA = P B0 R A = P B0 Y R = P D R,
(I+Q)A = I + (K+PD)R + PDR = I+KR = J.
```

After the full-frame source code, z=Ax and the target is y+Jx. Adding Qz
therefore gives y+Ax over F2. Q has exactly three nonzero physical rows,
0,1,2. The actual source-code rank is rank(A-I)=9; small target support does
not imply small source-code rank.

Three repaired target rows are minimal in this declared class. For any
invertible A, rank(A+J) >= rank(A)-rank(J)=3. A correction supported on r
physical target rows has rank at most r. This excludes r<3 for this fixed
clean-centre J and invertible source recoding, not arbitrary suppliers.

## Literal source code and one snapshot per repaired row

Normalize R on actual source coordinates `0,1,2,4,8,9,14,30,59`. Commuting
CNOTs replace those coordinates by a query basis. In this basis A has an
invertible 9-by-9 query block and fanout to the other source coordinates.
Gaussian elimination synthesizes the small block with 47 CNOTs. The ordered
code uses `474 prepare + 504 fanout + 47 quotient + 474 inverse prepare`,
or 1,499 ADDs, all at FULL. It uses no extra helper or private field.

For each nonzero row q=Q[p], choose a source index t with q[t]=1. All source
fields are at FULL. Add each z_i with i!=t and q[i]=1 to z_t. The prepared
field is exactly `sum_i q[i] z_i` over the integers: its original z_t is one
of the required terms, not an unknown extra offset. Copy this actual source
into the cleared private field at target p's cap, add it to target p, and
ERASE the copy while the physical source is unchanged. Undo the preparation
in reverse order with negated ADD coefficients. Every source is restored
exactly to its value before this episode.

The chosen pivots are 0,1,2. Their preparations use 59,53,60 ADDs; their inverse
preparations use the same counts. Including three scatters gives 347 repair
ADDs. Only one private snapshot is live at a time. No dirty helper is touched
by these three repair episodes. The six-copy dirty-helper variant is retained
only as explicit reconstruction ancestry; it is not the final construction.

## Integer and native boundaries

The signed word negates the actual factory cleanup, source unpreparation and
repair unpreparation ADDs. Literal reversal negates every ADD coefficient.
The complete 651-column integer replay establishes source `A_Z x`, every
helper exactly h and the private field zero. The target is
`y+T_Z x+E_Z h`, where `T_Z mod2=A` and E_Z is even. Target correctness is
asserted modulo 2, not as integer equality to y+A_Z x. The reverse source is
`A_Z^-1 x`. Full integer roundtrip is checked separately; A is not assumed
involutive. Wrong unpreparation signs preserve parity but change the integer
source, and are rejected independently.

For each actual rational E8 line vector u with squared norm 4, the checker
constructs P=uu^t/4 and K=I-P. It binds the actual entrance frame to P and
target frame to K, including all 222 bindings. For
`D_U=[[I-U,U],[U,I-U]]`, exact rational multiplication proves
`D_I D_P=D_K` and `D_P^2=I` on all 16 columns, for all 111 ports (3,552 checked
columns). Hence the FULL-to-cap copied-total residual is D_P of rank one,
under the inherited native ADDRESS/copied-total interface. Source and target
port labels need not agree: the physical source is FULL at the cut.

The independent ordered-word audit checks common frames for every ADD,
monotone containment and rank for every MOVE, actual source COPY, immutable
source throughout each snapshot, exact ERASE and endpoint frames, in both
directions. These local identities do not establish a full physical native
compiler, rounded implementation or recursive hosting theorem.

## Delete nine literally unread physical families

In the signed three-copy word, precisely the old helper indices 471 through
479 are never read as ADD sources or COPY/ERASE sources. The independent
checker discovers this set by scanning every record. The only operations on
these fields are 72 ADD destinations and 36 MOVEs, with paid profile
`27 e1+9 e5`. The same no-read property holds in the literal inverse.

Delete these nine physical input/output families, discard their destination
operations, and renumber every remaining operand in order, including the
private field from 660 to 651. No remaining value or frame depends on a
removed family. Induction through the literal word therefore identifies the
new execution with projection of the original execution, forward and inverse.
The constructor also checks exact integer endpoint projection, and the
independent checker compares the entire projected record list and both
boundary arrays before replaying all 651 independent columns. Every one of
the remaining 429 arbitrary helpers is restored exactly. The deleted families
are absent from the contract; they are not retained with unpaid endpoints.
A mutant that reads a discarded field is rejected before projection.

This removes another 72 local rank units and 72 ADDs. It does not establish a
72-unit hosted saving: under the incumbent width-8 whole-family accounting,
returning nine families to idle-owner children adds `9*8=72` rank units per
local call at beta=0 (648 across nine calls). Thus that returned idle obligation
cancels the pruning reduction at this mass level. Changed chronological owners,
stock and complete higher moments remain outside this package. The local
132-unit reduction below must not be read as a net global gain.

## Complete local invoice

| Item | Pinned R438 | This word |
|---|---:|---:|
| Sources / targets / dirty helpers | 111 / 111 / 438 | 111 / 111 / 429 |
| Owned private fields / maximum live copies | 1 / 1 | 1 / 1 |
| ADDs | 24,248 | 13,223 |
| MOVE children | 2,909 | 2,873 |
| COPY / ERASE pairs | 9 | 3 |
| COPY ranks | 9 times 7 | 3 times 1 |
| Paid children | 2,918 | 2,876 |
| Rank mass | 5,121 | 4,989 |

The complete profile is `{1:1298,2:1342,3:79,4:44,5:93,6:11,7:9}`.
Its exact change is `-9 e7-24 e1-9 e5`, saving 132 rank units per local invocation.
The ADD invoice is `5758 compensation + 5619 clean factory/cleanup + 1499
source code + 347 repair`. No chronological owners, native allocation,
private reservation, code restoration or final decoder cost is removed from
a global bill by this local calculation.

The exact signed prefix row norms are 34,285 forward and 5,839,860 inverse.
They are checked local arithmetic facts only. A new global perturbation/rounding
proof and precision reserve are required before using them in a supplier.

## Verification and remaining conditions

`reconstruct.py` regenerates the complete ordered word from the two pinned live
sources through the declared section and signed ancestry. The registered
verifier compares the full decompressed payload with `WORD.json.gz`. Only
validated source-location metadata and validated same-run compressed-parent
identities in signed/pruned ancestry are normalized. Every record, sign, frame, schema and register count
is compared. Immutable source and frozen word files retain exact byte hashes.

`check.py` imports no producer. Its separate sparse integer interpreter checks
all 651 columns in both directions and the roundtrip, actual R/K/J, source
inverse, all dirty restoration, all target parity, complete profile and exact
rational native caps. Eleven ancestry fault checks and seven independent controls
cover missing compensation/unpreparation, mutable snapshots, wrong inverse
code, wrong integer signs, FULL-copy rank, a corrupt section query and a read of a deleted family.

Open global obligations include composition of the changed source interface,
terminal code removal at the actual caps, physical helper/owner/access and
storage schedules, rounded cleanup and precision, recursive caller contracts,
and a full joint complex/BIT outer transfer. This local result supplies none
of those admissions and claims no new kappa.
