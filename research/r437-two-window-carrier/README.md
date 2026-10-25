# R437: a paid two-window carrier exchange improves the local recursive moment

**Source-bound finite improvement; selected κ is unchanged.** This package
constructs an actual R437 word that escapes PR4005's fixed node509 boundary by
retaining a SOURCE87 contribution in helper467 until a later legal cleanup.
It preserves all 659 arbitrary input columns, H1–H5, all full SOURCE write
states, the nine COPY SOURCE rows and frames, and every final role. Its complete
local recursive profile replaces two rank2 children by one rank1 and one rank3
child. The recursive moment is strictly smaller for every `0<a<1`.

The improvement is paid: the word has **three more scalar ADDs per call**,
helper469 becomes a SOURCE77 relay, and all 437 helper banks remain. The exact
ordinary OQ4 host is rebuilt across all 288 calls and 125,856 helper-owner
occurrences. Its fixed owner/idle invoice gains `+288` rank1, `−576` rank2,
`+288` rank3 children with unchanged rank mass 1,808,352. The charged moment grid rises from0.001736646042038446578551 to
**0.001736690352456612377607** (about0.00255% relative); its rational
certificate is in HOST-RESULT.json. This is not a completed physical
supplier or a new selected κ: native source generation, physical caller cost,
stock and integration obligations remain explicit below.

## Construction and actual delayed cleanup

The input is ai-nanachi's PR3647 word at
`a24f9ff95c12fd0b6792e3f710569237efd72db2`, including the credited helper464 and
SOURCE77-carrier deletions. PR4005 at
`2b412fb33c983edc495576be692b0601c1d62241` excludes a fixed node509 output
contract in which borrowed banks return modulo the accessible source span.
Here helper467 retains a source contribution after the node and is repaired
inside a later, source-checked observation window. No target is read.

Indices below refer to the **old** word. Replace A229's SOURCE92 load into469
by `[79,469,[77]]` followed by `[94,444,[92]]`. Both SOURCE registers are still
at those respective frames. Remove old A1998's direct77 load into444. Replace
A1999–A2000 by:

```
[509,467,[413]]
[509,413,[444,17,271,293,352,371]]
[509,444,[467,469,17,271,293,352]]
```

Before the new node, the SOURCE rows of `(444,413,467,469)` are
`(e92,e87,e38,e77)`. Put `u=e17+e22+e33+e60`. The outputs are:

| Role | New SOURCE row | Obligation |
|---|---|---|
|444|`e92+e87+e38+e77+u`|Exactly the old output|
|413|`e92+e87+u+e67`|Exactly the old output|
|467|`e38+e87`|Retains87 until the later cleanup|
|469|`e77`|Paid replacement relay; no bank saving|

The three homogeneous updates on `(a,b,c)=(444,413,467)` are
`c+=b; b+=a; a+=c`. Their rows are `(1,1,1),(1,1,0),(0,1,1)`, an invertible
matrix. The existing external additions supply `u`,77 and67. Unlike the old
fixed-output contract, the third output retains an independent SOURCE87 row.

Helper467 has no later A observation and is not captured. SOURCE87's last
low-frame observation is old **B68**, `[189,188,[87]]`; its next use is its
first mutation at old **B283**, `[509,87,[92]]`. Insert
`[509,467,[87]]` immediately after B68, before B283. This clears the extra
SOURCE87 in467. Helper467 is already at509 and its next observation is B297
at509. SOURCE87 advances189→509 earlier but has the exact same frame path;
there is no intervening read that needs its old frame. All SOURCE rows now
rejoin their original future observations.

The helper's full DIRTY row need not rejoin at that point. We reconstruct D
from the complete new raw word and C as its literal reverse on non-target
destinations. Exactly 55 D rows change, and D gains one scalar ADD. Independent
Boolean-column replay and the full matrix replay both establish that every
SOURCE/helper returns to its arbitrary initial value and target i receives
its original value XOR SOURCE i. Full COPY DIRTY rows differ; equality is
claimed for their SOURCE rows and frames only.

## Complete local charge and fixed OQ4 hosting

Rational geometry gives dim509=4. Only two frame paths change:

| Role | Old path | New path |
|---|---|---|
|444|0,186,509,392,513,1|0,94,509,392,513,1|
|469|0,94,509,1|0,79,509,1|

Role444 replaces dimension increments `(2,2)` by `(1,3)`. Role469 exchanges
rank-one entry frames without changing its rank charges. All other paths,
including SOURCE87 and helper467, are unchanged. Both forward and reverse
streams have the following complete per-call profile:

| Rank | Old children | New children |
|---|---:|---:|
|1|1320|1321|
|2|1344|1342|
|3|77|78|
|4|43|43|
|5|102|102|
|6|11|11|
|7|18|18|

Both have 2,915 children and rank mass 5,113. Scalar ADDs change
D17982→17983, A2133→2133, B934→935, C2632→2633, with the same527 COPY-scatter
ADDs: total24208→24211. The cancellation-free row bound stays49347 forward
and changes1113998→1123650 in reverse. Thus precision/stock costs must not be
assumed identical merely because SOURCE write states and endpoints agree.

For fixed width64, W roles and288 calls, the exact recursive-moment delta is

```
288 * (1 + 3^(1-a) - 2*2^(1-a)) / (W*64^(1-a)) < 0,  0<a<1.
```

Strict concavity proves `1^p+3^p < 2*2^p` for `p=1-a` in `(0,1)`; at `a=0`
the rank mass is equal. This is a strict paid-profile improvement, not a bank
or source-count saving. The SOURCE77 relay is explicitly charged.

`host.py` regenerates the literal forward/reverse MOVE, ADD, COPY and ERASE
streams, verifies the old streams against the retained OQ4 template, checks
all 288 data/helper owner maps, full eight-coordinate helper slots, slot
non-overlap and temporal eligibility, and reconstructs every unpooled idle
remainder. It checks the retained old emitted-program digest and emits the
new digest. The logical CANDIDATE-TEMPLATE.json.gz payload is stored as17 chunks of at
most48KiB, with per-chunk and joined byte lengths/SHA256 in
CANDIDATE-TEMPLATE.json. The loader reconstructs the exact original gzip; its
content is compared byte-for-byte after
canonical decompression with this reconstruction. The new host has7,814,880
local emitted events versus7,814,016, exactly864 additional ADD events.

HOST-RESULT.json records rational lower/upper moment intervals at a new
24-decimal grid point and its successor, using the inherited charged bad-event
rank1 term `32*64^2*E/10^16`. This is a conditional moment threshold for this
fixed unpooled host and tariff. It does not transfer acceptance from PR3647,
prove the full current physical caller, or update the selected result. In particular,
applicability of the retained bad-event probability/precision tariff to this
changed word is an open obligation; the arithmetic bracket evaluates that
explicit conditional invoice, rather than proving its applicability.

## Losing control, evidence and scope

LOSING-CONTROL.json and its receipt preserve the first actual helper468
construction. It retains87 until old A2035, saves two scalar ADDs, but splits
rank6 into3+3. Its total delta is `(6,2,2) -> (3,3,3,1)`, strictly worse by
majorization. The winning construction changes the cleanup window to the
actual B68–B283 SOURCE87 interval and avoids that extra split. Both controls
are reconstructed during ordinary replay; neither is silently overwritten.

The mathematical pairing is reversible source/frame algebra with
**time-expanded network coding and majorization**. Canonical main is
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priorities revision6. Parent live
R437/open-PR overlap and the10:46UTC cache found no newer two-window node509
result; Discussion/closed-PR/code coverage remains partial. Selected
κ remains **0.001672660197076918**.

```
python3 -B scripts/research_package.py --package research/r437-two-window-carrier
```

The package checks retained SHA256/Git blobs, all636 rational frames, H1–H5,
all659 columns, exact chronology, paid profiles, both complete orientations,
all owner maps and rational moment brackets. `test_package.py` independently
replays659 Boolean columns and rejects nine semantic/frame mutants, including
cleanup before B68, after B283, and omitted cleanup with literal C regenerated.
An optimized Git-free subprocess rejects four corrupted/missing inputs and
four generated-template chunk mutations (changed bytes, missing chunk, reordered
parts and a wrong joined digest).
Ordinary verification never regenerates artifacts. Independent agent review
recomputed geometry with Fraction RREF and replayed both complete words.

| Obligation | Status |
|---|---|
|Exact scalar/frame word and arbitrary DIRTY restoration|Checked finite certificate and source-bound argument|
|Nine COPY SOURCE rows/frames, SOURCE writes, H1–H5|Checked; full COPY DIRTY equality is not asserted|
|Ordinary OQ4 owners, idle remainders and full paid rank profile|Rebuilt all288 calls and125856 owner occurrences|
|Strict local moment gain and charged rational root bracket|Proved/certified for the fixed invoice|
|Current pooled recompilation|Independent complementary audit, reported separately; not assumed by unpooled receipt|
|Native selector/source materialization, retained bad-event tariff applicability, physical stock, precision and complete caller cost|Still required; earlier SOURCE87 MOVE and larger reverse row bound must be charged|
|New selected κ or complete multiplication theorem|Not claimed|

## Open next questions

1. Integrate the exact word into the current replica-indexed pooled compiler,
   regenerate its source codebook and native requests, and price the complete
   physical caller. Start from this template and the exact early SOURCE87 MOVE;
   frozen old request identifiers are not automatically transferable.
2. Derive the changed reverse-prefix/stock coefficient and prove that existing
   charged precision/capacity envelopes cover it. Start with the full reverse
   row bound1123650 and the additional864 ADDs; these are concrete changes,
   not zero-cost metadata.

Credit ai-nanachi/PR3647 for R437 and the helper464 deletion; Ali Romman/PR1043
for the SOURCE77-carrier deletion; Sagar Thakrar/PR3700 and PR2423 for OQ4 and
independent checks; PR4005/Chris R for the source-quotient cut and explicit
changed-boundary handoff; mightyOil/PR1281 and Rohan Arun/PR3959 for packing and
pooled context; and eumemic, DreamingOfClouds, DaysSky, Crow, chafreaky and the
retained notices for the word, geometry, native, hosting and compiler lineage.
The host lowering, owner-invoice pattern and rational interval technique are
adapted from the credited PR3647/3700 invoice audit. New construction, proof
and checks by Chris R / Clear1nsight with substantial OpenAI Codex assistance.
Apache-2.0. No independent human or formal-kernel theorem acceptance is claimed.
