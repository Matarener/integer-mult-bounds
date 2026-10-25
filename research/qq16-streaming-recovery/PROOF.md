# Streaming complete QQ16 recovery inside nine existing output banks

## Statement and boundary

The primary construction hosts its eight persistent full-cover query sums and
one reusable work bank in **nine deferred Z_U output banks**, requiring **zero
additional owned banks**. Its complete local bill is **224 H1 children, 448
wrappers, 352 maps and 26,944 scalar allowance**, with 416 CLEARs and 3,813 word
events. Only nine output definitions move. The changed future block has no
owner-private body; the whole-word private peak stays 16.

We first prove the standalone nine-owned-bank streaming schedule, then prove
its explicit output-bank hosting transformation. Both words are regenerated;
the standalone variant is also replayed independently as a comparison. The
hosted variant is the published `WORD.json` and primary `RESULT.json` invoice.


## Standalone nine-bank reference

For the pinned full decoder, the future-query correction can be evaluated with
**eight owned full-cover query banks and one reusable owned full-cover work
bank**, replacing PR3985's 112 simultaneous owned temporary arrays. The whole
word still returns all 224 original x0/y0 arrays in F17. It leaves all 224
current X/Y inputs borrowed and unchanged, with X entering in F17 and each Y_p
in the source's F17 C_qp^(-1) frame. The initial Y normalization and complete
inverse suffix remain present and paid.

The complete local bill is 224 H1 children, 448 native wrappers, 352 cover maps,
1,920 unit ADDs, 896 quarter ADDs and 425 CLEARs: scalar allowance 26,962.
Compared with PR3985 this removes 103 owned temporary banks, 111 CLEARs and
222 scalar allowance. It does not establish a physical tape count or a new κ.

All nine new banks can enter with arbitrary content. Their first use is CLEAR,
and each returns zero in identity frame before the inverse-B1 checkpoint.
They require exclusive ownership only during the changed block. The eight
query banks are **full-cover owned storage**, not owner-private scratch carried
across a native call. Peak private scratch for the complete word remains 16 in
the unchanged F0 inverse; the changed future block has no private body.

## Ordered operator identity

Retain the canonical PR2707/PR2681 source conventions. For each port p, let
M_p be the actual stage-2 affine cover map, including its source-derived
translation, and C_qp its rank-one native line. Let T_p be the ordered owner
routing operator. The inherited full phase identity is

    C_qp^(-1) M_p F17 = F16 T_p,

where F16 is the common frame on axes 9 through 24. Its inverse is the actual
source-ordered inverse map after C_qp; the affine inverse translation is not
silently dropped. The checker compares all 73 phase coordinates at every ADD.

At the changed-block entrance W_p = F17 u_p. The needed future query is

    q_k = sum_(p in U+T) R[k,p] T_p u_p,        k = 0,...,7.

There are 104 query ports and eight response ports A, with disjoint supports.
The required update is

    W_p <- F17 (u_p - T_p^(-1) sum_k R[k,p] q_k / 4),    p in A.

Every U+T output remains unchanged. There is no commutation of different owner
operators in this identity.

Initialize Q_0,...,Q_7 to zero in F16. For each p in the source order U+T:

1. Clear reusable D in F17 and copy W_p to D.
2. Apply M_p and then C_qp^(-1) to D.
3. For every nonzero R[k,p], add R[k,p] D to Q_k.

After processing the first j source ports, induction gives

    Q_k = F16 sum_(p among first j) R[k,p] T_p u_p.

The statement holds for arbitrary routed arrays: the maps are the original
ordered maps, each sum is in the same exact frame, and every use of D occurs
before its next CLEAR. At j=104 the eight banks contain the full required
query. The source and query loops have exchanged order; exact addition permits
this exchange. A former floating-point evaluation order is not preserved.

For each of the eight response ports p, clear D in F16 and form
`-sum_k R[k,p] Q_k/4`. Apply C_qp and the actual inverse M_p, then add D to W_p.
The query banks remain unchanged during all eight responses. Finally clear D
and all Q banks in identity frame. The result at the block exit equals the
materialized correction exactly, so the unchanged full suffix has the same
224 outputs.

The checker also computes exact rational row ranks: the query matrix on U+T
has rank eight, as does the response matrix on A. Thus the materialized query
has eight independent components. In a fixed-dimension linear query-only
summary interface, its rank precludes fewer than eight independent full-cover
summary fields. This is not a universal workspace lower bound: rereading
sources, recomputation, changed encodings and output-bank hosting are outside
that restricted observation. In particular no nine-bank optimality is claimed.

## Pebbling and lifetime ledger

The 104 aligned query copies are intermediate values, not output obligations.
Once one copy has contributed to the eight running sums it is dead and D may
be overwritten. Responses need only the eight completed sums and one staging
bank. This is a constructive pebbling schedule for the existing linear map;
it changes the intermediate storage contract without extra native recomputation.

Zero-based event positions in the complete 3,822-event word are:

| Bank | First CLEAR | Final CLEAR | Frame while retained | Native calls during allocation |
|---|---:|---:|---|---:|
| Q0 through Q7 | 1714 through 1721 | 2619 through 2626 | F16 | 112 each |
| D | 1722 | 2618 | F17/F16 through the stated maps | 112 |

The next event, 2627, begins the preserved 112-instruction Z update; the
inverse-B1 checkpoint follows at 2739. `RESULT.json` records each
bank separately. All first uses initialize arbitrary dirt; all final uses
clear the owned field to zero/identity. No borrowed X/Y, output Z/W or private
F/G array is silently aliased. The prefix and suffix have no Q/D references,
so their ownership interval can be restricted to this block. Physical
allocation, placement and release costs remain unknown.

## Hosting the nine roles in deferred output banks

Choose the first nine U ports in the pinned source order and injectively assign
Q0,...,Q7,D to their Z output banks. The generator independently checks every
reference before the first post-query Z update. For each chosen Z_p,
there are exactly two references before this cut: its initial `CLEAR Z_p current` and `ADD Z_p X_p 1`.
It is neither read nor updated anywhere else before that cut. These
are exact source def-use facts, not an assumption that all output banks are
free. Selected T outputs have live prefix uses and are rejected by this census.

Delete the nine original two-instruction output definitions from the prefix.
Execute the streamed block with the injective aliases. Every role's first use
is still its paid CLEAR, so arbitrary output-bank dirt is initialized. After
the final response, restore the nine original definitions, in order, before
the first preserved Z update. All X fields are still borrowed, unchanged and in F17, so
these deferred definitions produce exactly the original Z values and frames.
The unchanged suffix therefore sees its original full boundary.

The standalone roles' nine terminal zero/identity CLEARs are unnecessary in
this hosted contract: each same owned bank is immediately reinitialized by
the charged output CLEAR/X-copy. Remove those terminal clears, not the output
initialization. The temporary roles no longer have a separate zero-return ABI;
their obligation is the correct owned output state, which is checked at the
checkpoint and full-word exit. No borrowed storage is erased.

The source census, exact alias map, role first/last uses and output-redefinition
events are all recorded in `RESULT.json`. All old owned-output and borrowed
input dirt/restoration checks remain enabled. This construction uses only nine
deferred U outputs, unlike the parallel materialized-copy hosting approach's
104 deferred output definitions. The parallel agent supplied the output-lifetime
insight; this package derives its own nine-bank def-use proof and executes no
sibling code.

## Complete primitive bill and access obligations

| Charge | PR2707 | PR3985 | Nine external banks | Hosted stream |
|---|---:|---:|---:|---:|
| H1 children | 336 | 224 | 224 | 224 |
| Native wrappers | 672 | 448 | 448 | 448 |
| Cover maps | 464 | 352 | 352 | 352 |
| Unit ADDs | 1808 | 1920 | 1920 | 1920 |
| Quarter ADDs | 896 | 896 | 896 | 896 |
| CLEARs | 312 | 536 | 425 | 416 |
| Scalar allowance | 25840 | 27184 | 26962 | 26944 |
| Owned output banks | 224 | 224 | 224 | 224 |
| Additional owned full-cover banks | 0 | 112 | 9 | 0 |
| Whole-word private peak | 16 | 16 | 16 | 16 |


Scalar allowance is 8 times unit ADDs plus 12 times quarter ADDs plus 2 times
CLEARs. The streamed block has 560 ADDs and 129 CLEARs: eight initial Q clears,
104 query D clears, eight response D clears and nine terminal clears. The
materialized block had 240 CLEARs. No native call, wrapper or map is erased by
calling it a relocation. The nine-bank word also removes the old future-private
begin/end markers, giving 3,822 events rather than 3,935. Output-bank hosting
then removes nine terminal clears, giving 3,813 events and scalar allowance
26,944. Relative to PR3985 the total reduction is 120 CLEARs / 240 scalar
allowance and all 112 additional owned banks.

For an explicit abstract scalar-access protocol, execute one complete cover
pass per ADD or CLEAR. If a bank has N scalar entries, read both operands and
write the destination on each ADD; write the destination on each CLEAR. The
standalone nine-bank block has **689 scalar passes, 1120N scalar reads and 689N scalar
writes**, in addition to 112 native calls and 112 cover maps. These counts
assume no fusion or cache credit. They count scalar-array accesses, not bit
operations or tape-head steps, and do not price native/wrapper/map traffic. In the hosted block, including
the nine moved output definitions, the counts are 698 scalar passes, 1138N
reads and 698N writes. The prefix loses 18 passes, 18N reads and 18N writes;
thus the whole-word delta versus nine external banks is nine fewer passes and
9N fewer writes, with the same read count. These are exact for the declared
scalar-access protocol, not head-motion bounds.

| Obligation | Status |
|---|---|
| Exact full-output map and native frames | Proved under the retained source contracts; checked on the whole word |
| Named primitive invoice and nine output-bank role lifetimes | Constructive, exact |
| Declared scalar-pass read/write count | Exact for the stated access protocol |
| Physical placement, seeks, traversal, instruction control and return | Unknown |
| Bit encoding, precision, intermediate range and rounding error | Unknown |
| Outer invocation incidence, productive-family stock and idle coverage | Unknown for this changed module |
| Both all-depth supplier caps and improved κ | Not established |

The change exchanges 104 simultaneous materialized copies and an owner-private
query sweep for persistent query banks and serial full-cover access. Fewer
banks do not imply cheaper head movement. PR2722 and PR2794 price different
fixed scalar words and access layouts; their tariffs are not imported here.
Likewise no numerical budget or κ gain is inferred merely from fewer banks.

## Evidence and limits

The verifier authenticates all 22 canonical runtime files before executing the
credited PR2707 loader or PR2681 algebra. It regenerates the canonical full word
and the PR3985 comparison word, checking every event against the narrowly
retained pending-head WORD data. No unmerged executable is imported.

It replays the complete new word on independent current X/Y symbols and on
independent original x0/y0 symbols forwarded through F0/B1. It checks the
intermediate inverse-B1 checkpoint, all final arrays/frames, arbitrary owned
and private dirt, borrowed restoration and all nine hosted output reconstructions. The standalone nine-bank word is
also replayed with its separate zero/identity-return requirement. The adapted
signed native checker covers both signs on all 112 ports and 512 columns
(114,688 columns), binds all 224 occurrences and rejects an incorrect negative
wrapper translation. The source algebra is reused, not claimed code-disjoint.

Controls reject missing dirty clears, reuse without initialization, premature
query clearing, native/map errors, missing output reinitialization/restoration, borrowed-output alias,
and private scratch held across a native call. Whole-word, typed-receipt,
retained-comparator and canonical-source integrity are checked separately.
Finite symbolic replay supports the ordered linear proof; it is not a complete
physical supplier, rounded implementation or formal-kernel verification.

## Open next questions

1. Bind the unchanged 224-output ownership contract to an actual outer caller.
   This package eliminates extra query-bank allocation but does not establish
   the caller's 224 output banks, their geometry or terminal consumption.
2. Choose one concrete bank layout and access protocol, then price all 689
   scalar passes (698 in the hosted block including moved definitions), plus native/map/wrapper transitions and head returns. Compare
   the total to the materialized implementation before expanding construction.
3. If a complete caller budget permits it, bound the changed accumulation
   order's intermediate magnitudes and rounding defects. Exact algebra alone
   does not transfer a previous rounded-error estimate.

## Attribution

Credit ywz65 / PR2707 for full F17 normalization and its native word; Arham
Tahir / PR2681 for the ordered inverse and retained algebra; the QQ16/native,
geometry and supplier lineage credited in those sources; and Chris R /
Clear1nsight with OpenAI assistance / PR3985 for the rectangular correction.
The current change is the explicit persistent-query/reusable-work schedule,
its nine-output deferral and hosting proof, exact storage/scalar delta, and
verification. Credit the parallel output-lifetime agent for the deferred-output
observation and the coordinating agent for this bounded composition proposal;
all work is within the disclosed Codex-assisted session. Streaming linear
sums and pebbling are standard methods, not newly claimed mathematical tools.
PR2722 (Nick Petalas) and PR2794 (Arham Tahir) are distinct access predecessors.
Substantial OpenAI Codex assistance is disclosed. Apache-2.0; no independent
human or proof-assistant review is claimed.
