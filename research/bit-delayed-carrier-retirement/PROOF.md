# Delayed source50 delivery and complete carrier retirement

This proves an exact stream-operator substitution for the frozen R438 word.
It includes the complete local query invoice. Physical caller admission and
the global multiplication bound are not conclusions of the proposition.
All record indices refer to the immutable 38,927-record comparator.

## 1. Domain and the changed obligation

There are 660 ordinary registers: sources0..110, public targets111..221 and
arbitrary dirty helpers222..659. Register660 is the single private COPY
function, initially and finally zero. Each ordinary value is an arbitrary
Boolean-valued function on \(K^8\times K^8\), where \(K\) has odd characteristic.
ADD is XOR; literal signs also define an integer lift for the audit.

The construction retains the original rank-two queries on helpers413 and444.
It changes the downstream input into413 and its associated dirt compensation.
The fixed complete-join hypothesis of PR4179 is therefore not used to exclude
this word. Neither a one-query realization of that pair nor an unrestricted
query-sharing theorem is claimed.

Write \(x=x_{50}\) and \(z=h_{469}\). The relevant old leaf is

| Original record | Operation |
|---:|---|
| 53 | `413 -= 469`, at ZERO, before source50 enters469 |
| 20255 | `469: ZERO -> 52`, rank1 |
| 20256 | `469 += 50`, at52 |
| 23408 | `469: 52 -> 517`, rank6 |
| 23409 | `413 += 469`, at517 |
| 33619 | `469: 517 -> FULL`, rank1 |
| 33620 | `469 -= 50`, at FULL |

Apart from its initial target compensation, 469 has no other scalar reader.
Its value at the old delivery is exactly \(z+x\). The subtraction at53
injects \(-z\) into413's entrance state.

## 2. Reconstructible edit recipe

Delete original records

```
53, 20255, 20256, 23408, 23409, 33620.
```

Delete every section10 ADD with source469: exactly55 records. All other
section10 records retain their order.

Remove records23405,23406,23407,23515,24189,24190,24515 from their old
locations. Immediately **after original23889**, insert:

```
24189: target178 MOVE 0 -> 52, rank1
24190: target178 += source50, frame52
24515: source50 MOVE 52 -> 509, rank3
new:   helper413 += source50, frame509
23405: helper413 MOVE 509 -> 390, rank2
23406: helper413 += helper605, frame390
23407: helper413 MOVE 390 -> 517, rank1
23515: helper478 += helper413, frame517.
```

Immediately **before original33619**, insert the one new query

```
helper469 MOVE ZERO -> 517, rank7.
```

Retain33619, its original rank-one completion from517 to FULL. Every
unspecified record remains in its original relative order.
The new source ADD has section2; the new terminal query has section32.
These annotations do not change the operator semantics.

Helper469 is retained, holds arbitrary dirt and keeps its full width-eight
endpoint. It is not deleted as a physical register or replaced by clean
storage. Its revised itinerary has ranks7,1, rather than1,6,1.

## 3. Availability at the actual cut

Target178's final private-port read is23865. The corresponding COPY episode,
owned by476, closes at23889. Target178 has no later COPY read. Its next
original operations are precisely24189/24190, so moving them to the closed
cut preserves all earlier scatter reads.

Source50's only intervening use before its original24515 arrival is that
target178 read. Its next reader is24516, at509. After performing the
advanced target178 read, the existing paid source50 MOVE can therefore
advance to the cut. Source50 is still exactly its original \(x_{50}\).
Frame52 is contained in509; the move has its original rank3.

Helper413 finishes its509 prelude at23338. Its earlier outgoing reads are
20742 into391 and23329 into444. Its remaining modified tail can wait at509.
Helper605 stays unchanged at390 throughout the delayed read. Helper478 has
reached517 at23513; its read of296 at23516 commutes with the delayed read
of413, since neither read changes either source.
The delayed delivery finishes before478's first COPY at23947.

The new packet runs between the ERASE23889 and the COPY23890.
No private COPY is live during any new or moved recursive MOVE.
The original and changed words both have this property. All nine COPY
source snapshots remain unchanged until their matching ERASE.

These are literal source-window assertions, verified by the record replays.
They require no commutation between the pair's address projectors.
In particular \(P_{52}\le P_{509}\le P_{390}\le P_{517}\).
The transported source contribution follows the same total address map:
\[
D_{P_{517}-P_{390}}D_{P_{390}-P_{509}}D_{P_{509}-P_{52}}
=D_{P_{517}-P_{52}}.
\]
Only these nested increments commute; helper444's other rank-two label
does not enter this identity.

## 4. The complete compensation pullback

Let \(D_{t,h}\) be the coefficient of helper \(h\) in target \(t\)'s section10
compensation, expressed in the state **after** the section30 prelude.
These coefficients are0 or1.

Deleting53 changes the state at the end of that prelude by

\[
\Delta v_{413}=z,\qquad
\Delta v_{444}=-z,\qquad
\Delta v_{391}=-z,
\]

with every other row unchanged. The latter two terms come from the subsequent
actual entrance gates using413; they cannot be omitted from the pullback.
Both implementations derive the effect from the pinned word.

Consequently the public difference from retaining the old compensation is
\(\delta_t z\), where

\[
\delta_t=D_{t,413}-D_{t,444}-D_{t,391}.
\]

The complete111-target table has:

| \(\delta_t\) | \(D_{t,469}\) | Targets |
|---:|---:|---:|
| 1 | 1 | 20 |
| 0 | 0 | 40 |
| -1 | 1 | 35 |
| -2 | 0 | 16 |

Thus \(\delta_t\equiv D_{t,469}\pmod2\) on every target. Removing all55 old
reads of469 cancels the public error over the VALUE field \(\mathbb F_2\).
No public target is ever used as a source in the stream, so this public
compensation cannot introduce an unexamined non-target error.

The \(-z\) changes in391 and444 disappear at their raw reads of413,
records20742 and23329. The remaining \(+z\) in413 is canceled by replacing
its old \(z+x\) delivery from469 with the direct \(x\) delivery:

\[
z+x-(z+x)=0.
\]

This is an integer identity on independent \(z,x\).
All later consumers see the original decoded helper413 value.
Helper469 no longer loads \(x\) and no longer subtracts \(x\); its decoded
row is exactly \(z\). Its rank7 plus retained rank1 terminal transports give
the original FULL endpoint. All other source/helper rows and final frames
agree with the comparator exactly over the integers.

The Boolean candidate changes the public integer lift by \(-2z\) on51
targets and by zero on60. It is therefore not claimed to preserve the entire
signed public matrix. The predecessor itself only has a clean public shear
modulo2.

For a stronger control, replace the original coefficient \(D_{t,469}\)
by \(D_{t,469}-\delta_t\). That is2 on51 targets and0 on60.
Delete the old55 reads and insert102 **unit** `target += 469` reads at ZERO,
just after original19794. This variant preserves every one of the660 integer
output rows and uses the same query itinerary. Coefficient2 is never counted
as one unit ADD.

## 5. From decoded columns to actual address operators

For each rational orthogonal projector \(P\), define the address involution

\[
D_P(u,v)=((I-P)u+Pv,\;Pu+(I-P)v).
\]

All636 projectors in the frozen geometry have dyadic entries. The independent
inverse-Gram audit verifies symmetry and idempotence, all2393 nested frame
pairs used by the candidate and their relative address identities.
For \(P\le Q\),
\[
D_P D_Q=D_{Q-P},\qquad \operatorname{rank}(Q-P)=\dim Q-\dim P.
\]
The rational identities specialize to every odd characteristic. Each
idempotent's rank is preserved, for example by its dyadic characteristic
polynomial \(t^{8-r}(t-1)^r\); no finite-address quotient is treated as faithful
to a formal group algebra.

For the physical payload \(f_i\) at frame \(P_i\), write
\(c_i=f_i\circ D_{P_i}\) for its decoded function. A nested MOVE transports
the physical payload by the stated relative address involution and preserves
\(c_i\). A common-frame ADD acts pointwise on decoded functions. A COPY
transports its source into the private frame. Its exact decoded snapshot and
unchanged owner make the later ERASE legitimate.

Induction over the literal stream gives precisely the scalar matrix audited
on all660 independent columns. Therefore the Boolean matrix equality and
identical entrance/final frames imply equality of the actual public operators
for **arbitrary functions**, including correlated dirty inputs. The exact
integer non-target equality gives the same helper residual operators.
In particular469 ends with its original \(D_I\) physical residual;
decoded restoration is not physical identity.

This is a written framed-replay proof and finite exact verification. It
does not claim a fresh tape/compiler run or a formal-kernel certificate.
The general simulation principle is credited to PR540 and its PR589 extension;
the five-terminal source already uses this semantic interface.

## 6. Complete price and recursive progress

Every query except the two retired early469 queries and the one replacement
has the same charged rank. The retained final rank-one call is included.
Hence the complete histogram change is

\[
\Delta H=e_7-e_6-e_1.
\]

For \(\alpha=1-b\in(0,1)\), strict subadditivity gives
\(7^\alpha<6^\alpha+1\), so
\[
\Delta\text{cost}
=m^b(7^{1-b}-6^{1-b}-1)<0.
\]
At \(b=0\) the difference is zero: rank mass5101 is unchanged.
The exact interval evaluation in `check.py` uses rational atanh-series log
bounds, positive exponential series and explicit remainder bounds. It proves
the quoted strict decimal interval at \(m=64,b=1/500\).

The largest query rank stays7, below the local parent dimension8.
The saving is valid also at \(m=8\), or under an admitted larger ambient
parent. A single rank8 terminal call would give a larger abstract tariff
saving, but could request same-size recursion in dimension8. It is
**not** the construction certified here.

The full counts are2912 queries, rank mass5101,35947 unit ADDs and9 guarded
COPY/ERASE pairs. The scalar count is
\(36005-55-4+1=35947\):
four old scalar events are removed and one direct source read is inserted.
The signed-public control adds102 reads to that result.

All438 helper roles and their ordered widths are preserved:433 width8
and5 width4. Only469's ordered MOVE itinerary changes. Retimed source50,
target178 and helper413 keep their original ordered frame itineraries.
The query saving does not rely on a changed entrance width, discarded dirty
direction or an unpaid idle-axis return.

## 7. Limits and failed adjacent extension

A matched complete local tariff is established. Actual chronological
owner/controller admission, physical access and routing, rounded-child error
cleanup, all-size reserve/storage and joint outer assembly remain open.
The finite majorant diagnostics do not cure the predecessor's existing
precision/admission gaps. No new kappa follows.

The common source92 leaf470 is a different adjacent opportunity. Under the
same retained reader schedule, target128 must read478's COPY at23959 before
its source92 read at24100. Advancing source92 to509 before both helper
deliveries would reverse that dependency: the478 COPY already requires413.
A fully restored source92 tour adds two rank-two queries; its total delta
`H4+2H2-H3-H1` is positive. This rejects that explicit route, not every
changed COPY reader or every jointly processed dirty pair.

Apache-2.0. Ross Richardson, with substantial OpenAI Codex assistance and
separate AI construction, compensation and exact-geometry reviews.
