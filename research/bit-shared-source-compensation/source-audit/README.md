# Actual shared-source packet with noncommuting address labels

The pinned phase-A word contains a common-source pair of rank-two queries
on helpers413/444 with noncommuting address labels. The queries themselves
act on distinct helper registers and commute as whole-register operations.
Their independent dirty payloads remain
separately demanded by the frozen public suffix. A concrete shared-source
fanout rewrite saves **four scalar ADDs**, with no change to recursive queries.
This is a verified constructive control, not a paid-query improvement or a
novelty claim for generic common-subexpression sharing.

Run from the owned checkout:

```sh
python3 research/bit-shared-source-compensation/source-audit/check_source_packet.py
```

Default execution emits complete deterministic JSON and changes no files.
`--output PATH` explicitly writes a receipt. `SOURCE-AUDIT.json` is the saved
receipt, including exact projectors, complete watched rows, all660 suffix
coefficient pairs, literal replacement records and defect controls. Record
numbers below are zero based in the **original** word.

## Pins and contract

Unchanged inputs come from `inputs/PREDECESSOR-PINS.json`: source commit
`8eefab699338b93400ca72ab22c6cf64352f7e05`, original package commit
`b628ba738802587a38e61affaa01fd188d0644f9`, scientific base
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`. Canonical decompressed WORD SHA256:
`3bca74a2a8427eb18e86566baa19de597f10d0bc40c30b7443febd499ee2189a`.
The checker imports no predecessor implementation and authenticates both
input containers and the canonical WORD. Construction credit remains with
the pinned predecessor lineage; substantial OpenAI Codex assistance,
Apache-2.0. Historical results retain their own premises.

The660 persistent inputs are independent: sources0..110, public targets
111..221, helpers222..659; slot660 is a private copy. Scalar identities are
checked over integers, then modulo two for the BIT boundary. Address
projectors are rational dyadic matrices, valid over every odd prime field.
An ADD requires equal declared frames; each ERASE requires its original
unchanged snapshot. Helpers413/444 enter atZERO and end atFULL, rank8; neither
is one of the five rank4 terminals.

The frozen `R438-zero-helper-Uinverse-five-rank4-terminal-v2` format uses
section32 helper cleanup by expanded original-source subtraction. It is
**not** the historical PR589 H4 syntax that literally reverses A/B z-writes.
Helper413 cleanup32036..32064 and helper444 cleanup32992..33032 read only
original source registers. This matters to the saving count below.

## Exact packet and available sources

|Record|Operation|Frame or rank charge|
|---|---|---|
|23318|MOVE source17,183→509|rank2|
|23325|444 += 17|509|
|23333|413 += 17|509|
|23405|MOVE413,509→390|rank2|
|23406|413 += 605|390|
|23407|MOVE413,390→517|rank1|
|23408|MOVE469,52→517|rank6|
|23409|413 += 469|517|
|23424|MOVE444,509→392|rank2|
|23425|444 += 369|392|
|23486|MOVE444,392→513|rank1|
|23488|474 += 444|513; first external read|
|23515|478 += 413|517; first external read|

At cut23339 both selected helpers are atframe509. In original independent
input columns, their complete integer rows are

```
C = x17 + x22 + x33 + x60 + x87 + x92
A = V413 = C + h413 - h469 - h605 + x67
B = V444 = C + h444 - h369 + x77 + x38.
```

The `(h413,h444)` coefficient minor is the identity, so A,B remain arbitrary
and independent even conditional on all original source values. A common
source does not promise identical inputs or clean scratch.

Source17 is exactly original `x17` atframe509 until before record24523,
where `17 += 33` first mutates it. The source remains atframe509 until
MOVE24883. It can support a paid, restored source tour in this window.
However C is not already a single available frame509 operand: original
source registers22,33,60,87,92 are atframes182,185,62,189,184 atcut23339.
Any use of that whole common sum must pay its actual assembly and transport.

Neither helper is touched in records23339..23404. Both selected queries can
therefore be advanced tocut23339 without adding abstract records. The
checker verifies the retiming, frame legality, exact end map and literal
inverse. Physical head/tape transport and phases are not established.

Let `F=P509`, `P=P390-F`, `Q=P392-F`. Exact rational geometry gives

```
rank(F)=4; rank(P)=rank(Q)=2;
P²=P; Q²=Q; PF=QF=0;
(PQ-QP)[0,1] = 1/8.
```

For actual address swaps `S(P)=[[I-P,P],[P,I-P]]`, the address commutator's
entry[0,1] is1/4. Thus these actual labels do not commute overQ or any odd
prime field. This is distinct from the unrelated helper222/helper254
rank-one pair. Matrix inequality detects noncommutation; it does not assert
a faithful representation for arbitrary group-algebra linear combinations.

## Public demand, helper windows and cleanup

ADD23406 requires the first output at390, and ADD23425 the second at392.
Changing those endpoints requires changing the affected continuation too.
Their first external deliveries are the retained-total writes in the table.
Inject independent perturbations `(a,b)` into413/444 atcut23339, or atcut23426.
The frozen scalar suffix, interpreted in its declared wire frames, yields
these exact integer coefficient pairs:

```
public111: (1,0)   public114: (0,1)
helper413: (1,0)   helper444: (0,1)
helper478: (1,0)   helper474: (0,1).
```

All660 output pairs are in the receipt. Thus the branches are not consumed
only as one sum: even public demand has a rank2 minor. Atcut23516, after
both deliveries, fresh perturbations of413/444 have no public effect but
still alter their individual restored helper outputs. This rules out
silently discarding a branch under the frozen suffix, not a jointly
redesigned suffix or all noncommuting constructions.

Helper413 first/last touches are4/32064, with path
`0→89→190→509→390→517→1`. Helper444 first/last touches are16/33032, with
path `0→79→509→392→513→1`. Their earlier ZERO-frame dirty deliveries to
public targets must also be preserved. Full replay checks all660 entrance
columns, every Boolean endpoint, integer source/helper restoration, all
frames, and all nine COPY/ERASE episodes.

## Constructive scalar control: phase-A 13 ADDs to9

This is section2 phaseA, records23325..23338, not the historical phaseB
frame509 optimization. Atcut23325 advance the existing MOVE371 from23332;
it crosses no read/write of371. All participating values are now at509. Put

```
a=V444, b=V413, u=V468, v=V371,
D=V17+V271+V293+V352+V470.
```

Original13 ADDs yield `a'=a+b+u+D`, `b'=b+v+D`. Replace them by

```
b += V17; b += V271; b += V293; b += V352; b += v; b += V470;
a += b; a += u; a -= v.
```

The final a is `a+b+v+D+u-v=a+b+u+D`. This is an all-input module identity
over every commutative ring, including arbitrary dirty helpers. Other source
values stay unchanged during the block and every ADD remains at509.

Original half-open range `[23325,23339)` has14 records, one rank2 MOVE and
13 ADDs. Replacement has10 records, that same MOVE and9 ADDs. Its exact
recipe is in `optional_scalar_fanout_seed.replacement_records`. Every old
suffix record `i>=23339` becomes index `i-4`, otherwise unchanged.
Full forward count is **36005→36001 ADDs**. The unchanged expanded
section32 cleanup remains exact because the integer prefix map is identical.
There are no13 matching inverse records in that cleanup; a35997-ADD forward
claim would be incorrect.

The literal inverse of the complete changed word reverses all records,
swaps MOVE endpoints and COPY/ERASE, and negates each ADD. Its changed
reverse range `[15588,15598)` replaces original `[15588,15602)`. Both original
and changed forward/inverse compositions are replayed on every independent
input column. Forward plus literal inverse saves8 ADDs across two complete
executions; forward alone saves4. Positive-prefix precision bounds are a
separate obligation, not inferred from equality of the signed integer map.

The wrong compensation sign gives the same Boolean map but a different
integer lift; this is an explicit defect control. Others cover deleting Q,
borrowing source17 without resetting its frame, dropping delivery23488,
collapsing labels and removing the independent dirty pivot.

## Baseline and remaining obligations

The minimal pair costs `2*T_2(q)`, paid profile `{2:2}`, rank mass4, with no
extra ADDs. Original source/fanout preparation `[23317,23339)` charges9
MOVEs `{2:5,3:4}`, rank mass22, and13 ADDs. Continuation transport, including
rank6 MOVE469 and the two rank1 promotions, remains charged and unchanged.
The complete original and scalar-control profiles are both

```
{1:1322,2:1342,3:79,4:39,5:102,6:11,7:18}
```

including9 rank7 COPY charges. This audit supplies no paid-query saving,
recursive moment improvement or newkappa. The [compensation proof](../algebra/SHARED-SOURCE-PROOF.md)
and [complete invoice](../INVOICE.json) cover the source-tour repair.
Any winning candidate must retain
both independent payloads, restore source17 before its next use and satisfy
both public demand columns, charging every correction, transport, retirement
and inverse. A redesigned suffix must establish the full public and restored
spectator boundary. Precision, physical execution and outer assembly remain
open if a paid saving is found. This is finite exact computation plus the
written all-ring scalar identity, not formal-kernel or native proof.
