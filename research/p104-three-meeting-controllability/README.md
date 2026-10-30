# The three specified helper680 meetings cannot realize the split with invertible local scalar transforms

**Local-only exact scoped obstruction; no new κ.** The added meeting at
event15468 really supplies new source rows, but does not finish this split.
For each of the three predecessor encodings, any number of ADD/SCALE operations
at the three specified meetings fails, even when their coefficients are arbitrary
rationals. This closes a changed three-meeting interface, rather than extending
the predecessor's finite two-meeting coefficient census.

The scientific source remains [PR5718](https://github.com/CrocSwap/integer-mult-bounds/pull/5718)
at `a1534ac45401c9a9c80c07aa65c89e00e33594f8`, claiming conditional κ
`.00311024570`. It was merged as an archive on October26; merging does not
admit its claim. Canonical main was refreshed to
`de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision8. The selected
conditional κ remains `.00310045`, with the five retained framework assumptions.
Current selection, review and reproduction are resolved through
`certificates/selected-result.json`; the selected cold replay was not run here.

## Exact scope

The input basis, retirement and cut are the three encodings1196,1199,1200 in
the frozen predecessor contact list. The first cut is after13920 or13922 at
frame1049. We allow a full invertible rational linear transform on **all** fields
then sharing that frame:8 fields at13920,9 at13922. This includes the retired680,
fresh continuation z, and the fields omitted from the predecessor's six-role
search. The intermediate meeting is after15468, frame1075, roles479/527/z.
The last meeting is after16651 on the source schedule, frame164, roles685/z,
or after16652 on the checked retiming, with roles153/685/z.

Here z has exploration label753. An emitted new public input would use index744
and shift owned labels, as the inherited constructor does.

At the first meeting we require a GL map on its resident fields. Every finite
ADD and nonzero SCALE word on these fields has that property, including neutral,
nonmonotone, long and non-dyadic words. At later meetings we grant arbitrary
linear transforms, including singular maps. We also grant arbitrary rational
terminal normalization within each actual final frame. Thus this is a **necessary
relaxation of the specified ADD/SCALE construction domain**, not a sufficient
constructible class or a physical implementation.

Outside these meetings the literal source word is fixed. The sole alternative
schedule is the predecessor's independently rechecked advancement of source
MOVE16655 (`153,659→164`) to just after16649. All753 source columns, frames,
owned lifetimes and bills agree. Other schedules, other cut bases, additional
meetings, new native queries, and extra retained/transported owned fields are
outside the obstruction. In particular, an effective singular first transform
implemented with additional owned storage is not covered merely by calling it
a local scalar transform. Its complete custody, restoration and costs need a
new model.

## Controllability certificate

Let `a_r` be the row in first-meeting field r after its arbitrary invertible
transform. The rows `a_r` are independent. Exact formal-row propagation through
the source gives two independent combinations:

| Encodings | X | L |
| --- | --- | --- |
|1196, cut13920|`a_z`|`a_z-a682+a683-a684-a686`|
|1199/1200, cut13922|`a_z+a682`|`a_z+a683-a684-a686`|

The two coefficient rows have rank2 before and after every invertible first
transform. Full coefficient receipts are in `results/obstruction.json`.

At the second meeting the actual continuation is `L+A`, while479 and527
contain fixed source rows A and B. The first transform does not change A or B.
We therefore grant the new continuation

```
Q = w L + a A + b B
```

with arbitrary rational w,a,b. Changed479/527 have no propagation into the last
meeting or final output153. At that last meeting the two helper rows are

```
z   = C + Q
685 = (C - Q)/2,       C = a685 + C0.
```

The row N in153 is unaffected by either earlier transform. The exact endpoint
before the last transform is `t + X - L - A + Q`, where
`t=e153+e41` is the required main target. Granting arbitrary last-meeting
transformations further relaxes its possible endpoint to

```
t + X - L - A + k C + ell Q + g N.
```

On the original schedule153 is not a last-meeting source; granting N anyway
only enlarges that model. All identities use the **changed** earlier rows,
not stale baseline rows. Formal propagation checks every coefficient, and
noncommuting literal dyadic fixtures independently check the three-stage identity.

Output153 is the sole final field at frame164, so terminal normalization can
only multiply its row: the displayed expression must equal `lambda*t`.
The frozen rows have these successive private-coordinate probes:

- N has coefficient−1 at input44; A, B, C0, t and first-meeting rows have none.
  Thus g=0.
- Input153 then forces lambda=1.
- C0 has coefficient1/2 at input22; A, B, t and first-meeting rows have none.
  Thus k=0.
- Input479 forces `ell*a=1`; input527 forces `ell*b=0`.

The remaining first-meeting equation is

```
X + (ell*w - 1) L = 0.
```

This contradicts the rank2 certificate for X,L. No length or coefficient search
is needed. The checker establishes these identities for all three encodings
on both schedules, using8 or9 independent first rows and5 independent external
directions. The contradiction already uses one required main endpoint; dropping
other independent-output constraints only makes the relaxation more favorable.

## Why a broader span test was insufficient

`relax.py` first grants independent correction tensors at each meeting, with
source spaces enlarged by every earlier meeting that can reach it. Their ranks
are8/10/11 or8/10/12 at cut13920, and9/11/12 or9/11/13 at cut13922. The exact
linear membership equations are consistent in all six cases. Each retimed case
even has a frozen rational witness with all independent final target rowspaces
and full ranks in this overly permissive model. Such a tensor witness need not
factor into temporally compatible local matrices. The source-bound identity
above retains that missing coupling and rejects the physical ADD/SCALE domain.
No witness from this relaxed model is counted as a construction.

## Controls and invoice

The emitted predecessor positive, helper708 on PR5713, passes the exact scalar,
frame, ownership and target audit on all753 arbitrary columns. Its generic
normalizer costs225,210 scalar units, versus the published source221,474;
this is an inherited positive control, not a new improvement.

Controls reject wrong chronology, inaccessible source153 at the intermediate
meeting, a wrong frame, a legal-frame ADD corrupting the new independent target,
and an illegal retiming across a role touch. A deliberately singular first map
can satisfy output153, but loses independent input683 even when every final
frame is pooled. This explains why discarding an independent target cannot
evade the certificate. A separate control checks linear quotient reduction.

`results/invoice.json` reconstructs the literal whole18-call source:66,348 paid
jobs,12,976 productive fields and rank surplus760. The local paid bill is

```
2184 H1 + 459 H2 + 495 H3 + 92 H4 + 159 H5 + 22 H6 + 15 H7.
```

The proposed allowance remains `Delta paid=0` and
`Delta targets=18(H4+H5-H9)`. It is favorable for every `0<t<1`, but **no new
target credit is earned**. Source local scalar cost is221,474; the retiming
adds zero. Input basis plus retirement would cost16/32/24 scalar units for
the three cuts. No new local program, terminal normalizer, new-helper allocation
and route schedule, cleanup or recursive bridge was implemented. Their unknown
costs are not zero. No complete caller, native-phase, compiler, ordinary-admission,
precision/tape, BIT compatibility or outer replay was run for a new construction,
because no construction survives the necessary scalar test.

## Reproduction

The package is self-contained, uses the Python standard library, and preserves
the predecessor files unchanged under `vendor/`. `SOURCES.json` pins their exact
bytes and Git provenance. `MANIFEST.json` covers the complete package; receipt
comparison is semantic JSON, without compressed-container regeneration.

From this worktree root:

```sh
python3 -B research/p104-three-meeting-controllability/verify.py
python3 -O -B research/p104-three-meeting-controllability/verify.py
```

Both commands replay the full six-case tensor relaxation, all six exact
obstructions, the known constructive positive, rejection controls, changed-state
fixtures and complete invoice. They require no Git, network or absolute
predecessor path. `VALIDATION.json` records actual environments and results.
This is exact rational source analysis, without formal-kernel or independent
human acceptance.

## Open next questions

**Expansion decision: stop the three specified meetings.** Longer ADD/SCALE
words, SCALEs and larger coefficients at these meetings cannot fix this class.
This does not establish an obstruction for helper680 with arbitrary topology.

The smallest changed-interface question is whether one additional actual
contact can supply a second independent first-meeting combination, or can
change the protected singleton153 endpoint. Begin by extracting its causal
transfer and testing whether the rank2 contradiction still follows; do not
restart a coefficient census. Any added paid bridge must be compared with the
entire18(H4+H5−H9) target allowance before construction. Additional owned memory
needs explicit lifetime, delivery, restore and erasure rules. No next construction
round is justified solely by this handoff.

Cross-call paid-answer reconstruction belongs to the separately assigned chat
and was not investigated here. No helper440 cache search, helper695 fixed-route
search or PR5440 native mismatch replay was performed.

## Significance for researchers

The added intermediate meeting passes crude availability tests but still cannot
separate two independent temporal source combinations using this interface.
The exact obstruction removes both coefficient and program-length limits from
the earlier failure while keeping its physical source, cuts and final target
fixed. A useful next question must change information delivery or the boundary,
rather than enlarge the same scalar alphabet.

Credit [flyingviper](https://github.com/flyingviper)'s PR5718,
[Ali Romman](https://github.com/AliRomman)'s PR5713/5708 and all retained native,
helper, controller, compiler and analytic authors in `vendor/NOTICE`.
The local predecessor is commit `1f51164a1dba5b9cb7639d3b760d2a0660931f63`,
`research/p104-joint-neutral-search`; its earlier information-reuse and
multi-meeting reports are credited in `SOURCES.json`. Prepared for
[zxv](https://github.com/zxv) with substantial OpenAI Codex assistance, without
subagents. Elementary linear algebra and tensor propagation are standard.
Apache-2.0. No public post, PR, merge, closure or selected-frontier edit was made.
