# Fusing late FULL delivery with residual-based dirty cleanup

## Result and predecessor boundary

This is one explicit composition of two existing local constructions:
PR3981's late FULL delivery (`cdb7dcf3f7e5f860714a1b12df4c7a5157d8ae3d`)
and PR3943's compressed Q cleanup
(`2cba526a4ebe0ef6c3c0143498adcf67dca97941`). The source-preserving variant also uses PR3940's frozen fused tail
(`51ba88c007cfbcc3d9cf22dd321f5224be3a5bb1`). The encoded correction is PR3882's
frozen builder (`9d56eeedbed5e3e9bbbc8c189d66f14cf15b6067`, publication head
`d76586303e7036baa74f8deb2155038290174ffd`). The contribution is the source-bound
fusion and its complete invoice, not a new discovery of either ingredient.

The measurable target is fewer than 5472 unit ADDs with the same native mass
2520 and exact old endpoint. The construction achieves **4704 unit ADDs**,
with the same **2616 halves, 2616 doubles, and native mass 2520**. All 280
independent input columns, all 72 arbitrary dirty helper returns, and the
complete endpoint rows and formal frames are preserved. A second actual source-preserving consumer falls from5856 to5088 unit ADDs
with2712 halves/doubles and the same native mass2520. This is a finite
Gaussian-dyadic module identity, not a new multiplication theorem or kappa.

## Literal source extraction and the fusion cut

Use the original 4058-event native-channel witness. Its final 416 events,
zero-based indices 3642 through 4057, are exactly

    Q_k += D[k,i] X_i,

with 52 nonzero coefficients per query, all ±2, at FULL. Extract D from these
literal events. In the PR3882 pivot order
`J=[0,1,3,6,22,31,93,103]`, set `T=D[:,J]`. The full exact matrix T is in
RESULT.json; it has 32 nonzero entries, all ±2. For the actual Gram block
`A=[[I,B],[B^t,B^t B]]`, direct exact multiplication gives

    D = T [I B].

This is checked against PR3943's unchanged T, but the cleanup coefficients
are independently re-extracted from the main-branch witness. The verifier
also checks the state produced by the actual PR3981 schedule, rather than
assuming a possible query preparation.

Remove the last 416 cleanup events from PR3981's generated word. Its remaining
prefix includes all original public transports, its 104 retimed Y lifts, and
all 416 late Q-to-Y deliveries. Each query was quartered for these unit reads
and then doubled twice, restoring its value before the next step. At this
precise cut all 280 roles are FULL and their normalized rows are

    X=x,   Y=v=y+Ax,   Q=h-Dx,   G=h_G,   Dhelpers=h_D.

Here h, h_G and h_D are independent arbitrary dirty inputs. They are not zero
or source-dependent promises. The two meanings of D (cleanup matrix and
register-family name) are distinguished above and in the verifier.

## Chronology and reversible linear algebra

Execute the actual PR3882 tail **without its initial 104 lifts**, because the
prefix has already performed them. Its reads and writes are confined to X,Y.
Writing `q=x_J+B x_N` and `w=x+y`, its endpoint is

    X_J=q,   Y_J=w_J,   X_N=w_N,   Y_N=v_N.

The residual donors X_J and query recipients Q remain FULL; X_N and Y_J
occupy their indexed target hyperplanes. Q still equals h-Dx. Execute the
actual PR3943 consumer: for each nonzero T[k,b], add the signed X_J donor to
Q_k twice. This uses 64 unit ADDs, no scratch, no scaling, no transport, and
leaves every donor unchanged. Since

    Tq = T(x_J+B x_N) = Dx,

it restores Q to h. The tail did not touch G or delivery helpers, so all 72
dirty returns hold simultaneously. Every data endpoint equals PR3981 followed
by the original correction after its old cleanup. The verifier compares all
280 rows, including the retained residuals, rather than only the sum slots.

The ordering is essential. Late Q-to-Y delivery must finish while the live
queries still carry their source contribution; the quartered donors must be
restored; the correction must then create the actual residual q before Tq is
read. Running Tq cleanup earlier uses x_J rather than q. Running the old Dx
cleanup after the correction attempts reads from consumed/non-FULL X_N.
Neither incorrect reordering is silently admitted.

## Source-preserving fusion at the actual PR3940 internal cut

The unchanged `fused(J,N,B)` builder from PR3940 supplies a stronger matched
source-preserving comparison than returning after the encoded exit. Its104
initial Y lifts are again already present in the late-delivery prefix. Its
remaining program is the actual sequence

1. Pivot stream: X_J becomes q and Y_J becomes w_J; X_N remains x_N.
2. Scatter `Y_N -= B^t q`, leaving Y_N=y_N. Each temporary half of a pivot
   donor is restored by the builder's corresponding double.
3. Inverse pivot stream: `X_J -= B x_N`, restoring x_J.
4. `Y_N += X_N`, producing w_N; drop all104 Y to their indexed hyperplanes.

Insert the same64-unit Tq cleanup **between steps2 and3**. Its exact internal
cut is1360 tail operations after the removed104 lifts. The verifier compares
the literal prefix against the frozen `pivot_stream + scatter` builders,
checks every X_J donor equals the same exact q row as in the encoded variant,
and checks all donors and Q recipients are FULL. It also checks Q still equals
h−Dx. This excludes both reading a still-halved pivot and reading after the
inverse stream has destroyed q. All X/Y operations otherwise remain unchanged.

The matched baseline is the entire actual3981 word with its original Q cleanup,
followed by this same3940 fused tail. The new whole word preserves its280 rows
and frames, including every X_i=x_i at FULL, every Y_i=x_i+y_i in H_i, and all72
dirty returns. Its chronological native subsequence is literally equal to
that baseline's. The correction's scalar counts are1632 ADDs and200 each
half/double:768 pivot-stream ADDs,384 scatter ADDs,384 inverse-stream ADDs,
and96 sum ADDs. Therefore the complete matched invoices are

| Source-preserving module | Unit ADDs | Halves | Doubles | Native mass |
|---|---:|---:|---:|---:|
| Late delivery + old cleanup + actual3940 fused tail |5856|2712|2712|2520|
| Late delivery +3940 tail with internal Tq cleanup |5088|2712|2712|2520|

This saves another768 ADDs under the same comparison convention, with no
additional native work. Relative to the encoded fused result, source preservation
costs384 additional ADDs and96 each half/double in these particular words.
It does not require the192-native post-encoding return adapter. The later
comparison with that adapter is context and an actual integration check;
neither alternative is claimed optimal over all source-preserving programs.
Moving the cleanup after step3 instead breaks all8 Q dirty returns, as an
additional whole-word negative control confirms.

## Physical contract and inherited native evidence

Each new schedule has **exactly the same chronological native transport
subsequence** as its matched reference (3981 plus3882 or plus3940), including every retimed lift and the
correction's final drops. This is a literal ordered-event equality, not an
inference from an equal histogram. No lift, descent, chart adapter, private
register, or role change is added. The new 64 reads are scalar additions in
a common FULL chart. The independent evaluator verifies every arithmetic
entrance and every nested transport entrance and positive dimension tariff.

With the inherited invariant `physical_r=Gamma_frame(r)*logical_row_r`,
these scalar identities hold for arbitrary address functions over
`Z[i,1/2]`. The old source and target chart operators retain exactly their
existing meaning. In particular, equality of frame spans is not being used
to donate an unproved physical basis change: the native event sequence itself
is unchanged. PR3981's 104 lift recipes were bound to the ordered canonical
bases from the native certificate and checked for signed Pauli action and
exact phase. That phase evidence is inherited here, not freshly replayed.
PR1991's full historical native realization and the final PR3882 physical,
owner, global, precision and all-size qualifications remain as stated there.
The PR3940 source-preserving tail likewise retains its stated native/admission
qualifications. The present new verifier independently checks the complete scalar/frame
composition; it does not claim a fresh native recipe audit.

## Complete matched invoice

Both sides use the same explicit scalar lowering: for an old coefficient
p/2^s, halve its donor s times, perform |p| signed unit ADDs, then double it
s times. New late-delivery batching and the correction's already batched
scalings remain literal. This is a valid upper bound, not a scalar optimum.

| Complete module | Unit ADDs | Halves | Doubles | Native mass |
|---|---:|---:|---:|---:|
| PR3981 + old cleanup + correction | 5472 | 2616 | 2616 | 2520 |
| Fused prefix + early correction + Tq cleanup | 4704 | 2616 | 2616 | 2520 |
| Difference | -768 | 0 | 0 | 0 |

The removed 416 coefficients ±2 cost 832 unit ADDs and no scaling. Their
replacement has 32 coefficients ±2, implemented by 64 unit ADDs. Thus the
saving is exactly 832−64=768, with no unpriced return or donor restoration.
All finite scalar counts are recounted from the actual joined event lists.
The retained native profile is
`{1:1282,2:58,3:86,4:104,5:48,6:24,8:8}`. Its rank sum is 2520.
There is no private allocation, copy, or erase.

For an actual source-preserving downstream contract, the verifier also
appends PR3943's unchanged return adapter to the fused word. It restores
all X_i=x_i at FULL and all Y_i=x_i+y_i in their indexed hyperplanes, with
all 72 dirty helpers restored. This adapter adds its already-known 960 unit
ADDs, 104 halves, 104 doubles and native mass192. The complete returned module
therefore costs **5664 unit ADDs, 2720 halves, 2720 doubles and native mass2712**.
This is an integration check of the actual inherited consumer, not a new
192 lower bound or a claim that it is the cheapest source-preserving correction.
The direct PR3894 I−A correction has a different consumer; its own complete
matched scalar comparison and any optimality claim remain outside this result.
The internal-cut3940 variant above is the actual source-preserving improvement
proved here, with native2520 rather than this adapter route's2712.

## Global gate and bounded stopping rule

Under the unchanged favorable corrected two-axis contract of PR3954, calls
number208, per-call endpoint progress is2312, and the anchor allowance is10816.
Scalar fusion changes none of those native quantities. The necessary gate
remains

    208*(2520-2312)-10816 = 32448 > 0.

Thus the retained complete native bill remains2997696 over denominator2965248.
This local scalar improvement does not reopen that native gate or justify
further dependent kappa optimization. Newly proposed one-axis/global completion
contracts are separate research tasks; this package neither prices nor admits
them. No selected-frontier change, universal obstruction, global owner theorem,
or all-size admission is claimed.

## Verification and controls

The frozen PR3981, PR3943, PR3882 and PR3940 source exports are byte-identical to their
recorded original Git blobs, with explicit source-head and SHA256 metadata.
Only their named schedule/geometry builders are reused. A new sparse Fraction
interpreter evaluates the actual joined words and formal frames on all 280
independent columns. It separately checks cut states, actual residual donors,
D=T[I B], data outputs, dirty returns, scalar lowering, and native subsequence.

Eight semantic mutants reject: omitted compressed cleanup, cleanup before q
exists, reuse of old cleanup after source consumption, double cleanup, omission
of one unit update, failure to restore a quartered dirty donor, and correction
before late delivery, plus source-preserving cleanup after q has been
restored to x_J. Separate actual optimized CLI processes first validate
each private fixture and then reject Boolean/float receipt types, duplicate
keys, false savings, changed/missing source, or changed frozen tail bytes.
Read-only official exports are preserved; only private test copies become
writable. Assertions removable by Python optimization are not used to enforce
these checks.
