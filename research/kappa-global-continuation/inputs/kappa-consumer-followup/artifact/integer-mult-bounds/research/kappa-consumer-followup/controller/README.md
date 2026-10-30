# Changed controller and retained dirty helper contracts

This directory contains three executable finite certificates. It does **not**
contain a complete supplier admission or a new value of kappa.

The strongest local result is a pair of **dyadic, zero-repair words on both
actual PR3734 providers**. They retain the omitted centre's dirty helper term
and use a rank-eight involution on data plus helpers. Both orientations have
native profile `{1:2440,2:725,3:224,4:102,5:20}`, rank mass **5070**, and
**168592** real scalar primitives. They change the helper contract. Their
global terminal completion has not been constructed at a profitable price.

The literal T360 owner analysis explains what that remaining contract must
handle. An existing helper family is usually reused and eventually becomes
data in another replica. No replica has one physical family among its eligible
helper assignments in all nine calls. That is a statement about the current
literal allocation, not an impossibility theorem for changed allocations,
record moves, or consumers that track subsequent data operations.

## 1. Exact nine-stage bank factorization

`check_controller.py` extracts the actual `recipe()` function from
`research/nine-stage-prefix-audit-seed70/verify.py` and compares it with its
independent construction. Use bank order

`X0,Y0,X1,Y1,X2,Y2,X3,Y3`.

The ordinary product before the final signed exchange is the block matrix

\[
S=\operatorname{diag}\left(
\begin{pmatrix}0&-1\\1&0\end{pmatrix},\ldots,
\begin{pmatrix}0&-1\\1&0\end{pmatrix}\right).
\]

For the data-only involution contracts from the attached report, the modified
product factors as

\[
S M,\qquad M=E_8\cdots E_0,\qquad
E_j=I+(a_jb_j^T)\otimes(G_j-I).
\]

The exact vectors, in the input-normalized bank gauge, are:

| Stage | Image vector a | Query vector b |
|---:|---|---|
| 0 | X0 | X0 |
| 1 | X0 | X0+Y0 |
| 2 | X0−Y0 | −Y0+X1 |
| 3 | −X0+X1 | −Y0+X1+Y1 |
| 4 | −X0+X1−Y1 | Y0−Y1+X2 |
| 5 | X0−X1+X2 | Y0−Y1+X2+Y2 |
| 6 | X0−X1+X2−Y2 | −Y0+Y1−Y2+X3 |
| 7 | −X0+X1−X2+X3 | −Y0+Y1−Y2+X3+Y3 |
| 8 | −X0+X1−X2+X3−Y3 | Y0−Y1+Y2−Y3 |

Each has `b^T a=1`. The checker uses nine distinct noncommuting two-dimensional
involutions to check the complete product and the inverse application order
8 down to 0. Reversing that order is an effective negative control.

Before the signed exchange, physical X banks are in the common FULL gauge;
physical Y banks have FULL C_q^-1. The physical vectors are `S a` and
`b S^-1`. No one factor has both image and query wholly in the common FULL
banks. This rules out a free factor on bank support alone. It does not prove
any lower bound for a more elaborate native implementation.

This script certifies the scalar bank factorization. The exact per-port routes
and nonzero phase alignments are separately checked by the reconstructed
terminal-native certificate. The source's entry_X and entry_Y translations
agree, and likewise its exit translations; separate side labels alone do not
establish that equality. The all-stage phase verification is necessary before
using the displayed tensor factors as a physical terminal program.

## 2. An eight-ADD dirty record component

The original source-code involution is

\[
G=I+AR,\qquad A=12P-K,\qquad RP=I,\quad RK=14I.
\]

Thus `RA=-2I`, `G^2=I`, and `RG=-R`. In each of the eight serial query steps,
the local program already forms `q_k=R_k x` in the owned query accumulator.
Adding that value to one actual helper before scattering its A column gives

\[
(x,h)\longmapsto(Gx,h+Rx).
\]

This augmented map is its own inverse and differs from identity by rank eight.
The retained helper roles are

`224,225,227,229,231,232,233,234`.

Both providers start these helpers in I and end them in FULL. The forward code
captures at the FULL source exit; the backward code captures from Y at the I
entrance. All632 independent input columns pass, including the original dirty
helper columns. The changes are eight ADDs, costing64 real primitives per
invocation, with no new field and no new native child. The resulting local
bill is5078 native rank mass and179964 real scalar primitives.

These records are **h_initial+Rx**, not Rx. Neither their arbitrary initial
values nor subsequent native transports have been dropped from the claim.

An exact general completion identity makes that remaining debt explicit.
Suppose a separately owned record system really implements

\[
(x,h)\longmapsto(Mx,h+Lx),\qquad M=I+UL.
\]

Preinject `x += U h`; run the augmented circuit; then subtract `U h_out`
from its data output. The data is exactly x_initial. Subtract `L x_initial`
from the record output; this leaves `(I+LU)h_initial`, which must be inverted
on the record space. No initial helper snapshot is omitted. The initial U
map, final L map, and helper inverse all need native and physical prices.

For a single involutory update `E=I+UV`, `VU=-2I`, the helper inverse is just
negation. That algebra does not by itself supply compatible native entry and
exit gauges, a cross-call lifetime, or a zero-cost U or V map.

## 3. Zero-repair paired words retaining the actual dirty core

The cleaner construction in `dirty_core_component.py` keeps the dirty term
which the data-only code had separately removed. Let

\[
z=(x,h),\quad E z=x,\quad Q=[R,H],\quad
K_e=\begin{bmatrix}K\\0\end{bmatrix}.
\]

Omitting all eight centres from the actual forward word gives

\[
z'=z,\qquad y'=y+(E-KQ)z.
\]

The independently reconstructed H has support on106 helper roles in both
providers, all initially I and finally FULL. Its columns at

`224,225,227,229,240,241,256,257`

form an invertible dyadic minor. Its exact entries and inverse are recorded in
`evidence/DIRTY-CORE-RESULT.json`. Choose `P_e` supported on these eight helper
coordinates with `QP_e=I`. Since `E P_e=0` and `QK_e=14I`, set

\[
A_e=12P_e-K_e,\qquad D=I+A_eQ.
\]

Then

\[
QA_e=-2I,\qquad D^2=I,\qquad (E-KQ)D=E.
\]

The eight rank-one updates commute with one another because the off-diagonal
entries of `QA_e` vanish. Each can therefore be lowered with one cleared
serial query field. The complete forward raw core followed by D has contract

\[
F_D:(z,y)\longmapsto(Dz,\ y+EDz).
\]

Equivalently, for `q=Rx+Hh`,

\[
x'=x-Kq,\qquad h'=h+12P_Hq,\qquad y'=y+x'.
\]

Every scalar operation in D is on actual FULL exit fields. The forward target
needs no native phase repair. Only the eight selected helper pivots change;
the other400 arbitrary helpers retain their values.

The actual omitted backward word is the inverse transpose of the omitted
forward word. It sends

\[
z\longmapsto z-D^T E^T y,\qquad y\longmapsto y.
\]

Postapplying `D^T` to the FULL X/helper fields therefore gives

\[
B_D:(z,y)\longmapsto(D^Tz-E^Ty,\ y).
\]

This is exactly `F_D^(-T)`. The transposed rank-one code is explicit and
involutory. It changes106 helper roles, leaving302 helpers unchanged. It also
uses no replacement native children and no odd-denominator divisions.

This B contract differs from the older `(x-y,Gy)` contract. Its data and
helper defect cannot be substituted into the old nine-stage bank-only
certificate without deriving a new global factorization.

### Local verification and invoice

Both actual PR3734 providers pass:

| Check or invoice | Forward | Backward |
|---|---:|---:|
| Independent formal input columns | 632 | 632 |
| Native rank mass | 5070 | 5070 |
| Replacement native children | 0 | 0 |
| Added code ADD macros | 1299 | 1299 |
| Added code real scalar primitives | 12578 | 12578 |
| Complete real scalar primitives | 168592 | 168592 |
| Scalar triangle bound, ceiling log2 | 120 | 126 |
| Modified helper roles | 8 | 106 |

The checker independently verifies the full literal native frame chronology,
including entry and exit wrappers, owned work and zero-buffer lifetimes. It
propagates all632 columns over free noncommuting warp words and checks the
literal D and D^T programs twice. The scalar triangle bounds fit the inherited
192-bit cap. A complete changed global error and physical tape proof is still
required.

The local profile is `{1:2440,2:725,3:224,4:102,5:20}`. The eight H8 centres
have been deleted. This saves64 rank mass per call and576 across nine calls
before any consumer or owner repair is charged.

## 4. Actual T360 physical owner chronology

`check_retention_owners.py` first reruns PR3734's retained independent owner
audit on all1321920 literal helper roles. It then binds the eight dirty-core
helper pivots to their exact assignments in `FILL.json.gz`.

The physical family of a row `(time,helper,owner,child,port,offset)` is

\[
896\,owner+112\,(2\,pair(child)+side(child))+port.
\]

The exact current `ORDER.json`, `DISPATCH.json` and literal FILL define the
T360 clock. The template and plan retain some ancestral T37 descriptive
metadata; the audit uses their source recipe and child-to-family map, not that
ancestral clock.

Both providers have213 eligible I-to-FULL helpers. Their complete helper-width
inventory is `{4:26,5:2,6:18,7:53,8:96,9:213}`, whose width sum is **3278**.

For every one of360 replicas, the intersection of eligible physical families
across its nine calls is empty. More flexibly, the following table counts
calls whose existing helper idle window lasts until the capturing replica's
final local call. Each entry is out of360 calls at that stage.

| Stage | Some eight eligible hosts last to final call | All eight specified pivots last to final call |
|---:|---:|---:|
| 0 | 7 | 7 |
| 1 | 2 | 0 |
| 2 | 8 | 8 |
| 3 | 18 | 18 |
| 4 | 40 | 29 |
| 5 | 84 | 66 |
| 6 | 188 | 178 |
| 7 | 250 | 234 |
| 8 | 360 | 360 |

These counts are optimistic: intervening helper invocations and native frame
progress are allowed. At a window's close the owner's ordinary data or bridge
use resumes. Carrying a record past that point requires accounting for its
subsequent data mixing. Thus the current allocation is not an unchanged
private nine-stage record bank. The result does **not** exclude choosing
different hosts at each stage, moving records with a paid map, changing the
allocation, or designing a consumer for the full coupled physical state.

All25920 selected trajectories are retained in the compressed owner evidence.
Each gives the physical owner, child, port, compact native offset, window,
remaining native capacity, next helper use and later-use count.

## 5. Promoting Gaussian helper coordinates: an unclosed graph screen

The related symmetric Gaussian construction lives in the neighboring
`baseline/symmetric_extended.py`. It promotes16 source and16 target helper
coordinates and produces local128-port F/B contracts. This directory does not
claim its global admission.

Promoted I-to-FULL helper coordinates have local native progress9, while the
original ordinary ports have progress8 and norm-one line labels. Inserting one
rank-one boundary normalization per promoted X/Y coordinate costs32 H1 per
local invocation. The local profile then has mass5102. Exact arithmetic is

\[
3278-32\cdot9=2990,\qquad
5102-(256\cdot8+2990)=64.
\]

This reproduces the old64 local overhead; it does not by itself settle the
larger graph's value. For a constructed ordinary128-port, m=73 graph, the
formal global rank-mass screen would be

\[
1024\cdot73-[1024\cdot72+9\cdot64]=448.
\]

For a constructed mixed112 ordinary plus16 zero-label port graph at m=81,
with no local overhead, the corresponding screen would be

\[
1024\cdot81-[896\cdot80+128\cdot81]=896.
\]

Neither expression includes an encoded-terminal correction, an actual idle
allocation, or an analytic recurrence. They are arithmetic budgets, not
constructions. A genuine128-port four-pair graph uses1024 fields per replica.
The old360 replicas'322560 data families can instead be resliced into315 such
replicas, but the owner clock and routing must be rebuilt.

The zero-label port's interstage phase law remains unclosed. The old
norm-one-chart route fixes a nonzero line and swaps eight perpendicular axes;
it cannot simply be reused with q=0. In a shared-line presentation, odd powers
of that line need an explicit treatment. No universal impossibility claim is
made from this observation.

## Reproduce

From the `integer-mult-bounds` root in this workspace:

```sh
python3 -B research/kappa-consumer-followup/controller/check_controller.py
python3 -B research/kappa-consumer-followup/controller/dirty_core_component.py
python3 -B research/kappa-consumer-followup/controller/check_retention_owners.py
```

Each command prints a scoped PASS marker. Inputs default to the adjacent
`recovered-involutory` and `live-source` directories; explicit `--recovered`
and `--source` arguments are available for a relocated package.

`evidence/RESULT.json` records bank factors and the eight-ADD retained code.
`evidence/DIRTY-CORE-RESULT.json` records both zero-repair words and exact helper
minors. `evidence/OWNER-RESULT.json` records source hashes, the full parent
physical audit and lifetime census. The corresponding gz files contain the
complete emitted programs and selected owner trajectories.

Prepared with substantial OpenAI Codex assistance under the user's direction.
The PR3734 supplier, source-code predecessor, controller, physical owner audit
and native interpreter authors retain attribution. Apache-2.0. The paired
transpose proposal came from the concurrent baseline-invoice investigation.
