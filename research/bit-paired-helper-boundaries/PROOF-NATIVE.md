# Three fixed helper-kernel words and their paired native residuals

This proof covers the frozen ten-entrance R429 word, the common coordinate-E2
R429 word, and the common coordinate-E2 old CLEAN R438 word. It establishes
their literal local signed and binary maps, costs, and rational ADDRESS
identities. It does not supply a chronological owner construction, a compatible
all-size native compiler, rounded/tape admission or a new kappa bound.
Substantial OpenAI Codex assistance; Apache-2.0.

## Domains and fixed inputs

Every ordinary source, old target and helper has an independent entrance
column. The two R429 words have 651 arbitrary integer scalar inputs, comprising
111 sources, 111 targets and 429 helpers, with no private allocation. The R438
word has 660 arbitrary integer inputs, comprising 111 sources, 111 targets and
438 helpers. It additionally uses one initially zero private cell, reused for
nine COPY/ERASE lifecycles. A zero frame is not a zero value.

Signed scalar lifts are over the integers. Clean target behavior and the
native arbitrary-dirt interpretation below are over binary VALUE arrays.
ADDRESS matrices are rational; the two common-E2 constructions specialize to
fields of characteristic outside {2,3,5}. The ten rank-one paired residuals
are dyadic and specialize to odd characteristic. This distinction is material:
integer source/helper restoration is exact, but integer target helper
coefficients are generally nonzero and even.

The inputs are the pinned R438 source, the pinned R429 FULL compensation word,
and the three emitted words and their saved geometry. The independent checker
does not import a producer utility. It reconstructs semantic dirty maps from
signed replay, consumes the emitted words directly, and derives projectors
from independent integer-root bases. Exact input pins are in `RESULT.json`.

## Semantic dirty columns and the integer basis change

Let D be the helper-to-target binary dirty map with the initial compensation
ADDs omitted. The independent calculation initializes every helper with a
separate integer column, executes the whole uncompensated word including
every old COPY/ERASE, and reduces its target coefficients modulo two. For the
R429 FULL word, D has size 111 by 429; for the old CLEAN word it has size
111 by 438. Both have binary rank 111. Every column agrees with its literal
original compensation column. Thus the construction uses the actual semantic
dirty map, not a count of syntactic incidences.

For the global constructions, scan original helper columns in their fixed
order, retaining an independent column whenever possible. There are 111
pivot helpers. Each dependent column j has a unique expansion in these
original pivot columns:

    D_j = sum_(i in I_j) D_i     over F2.

Low-pivot dense elimination independently reconstructs all selected pivots and
expansions, and matches every emitted helper-basis ADD. Set

    N = sum_(j dependent, i in I_j) E_(i,j),   S=I+N.

Every destination i is a pivot and every source j is dependent. These sets
are disjoint, so N^2=0 over the integers. The basis ADDs commute, S is
unimodular, and S^-1=I-N is realized by negating their coefficients. The
emitted inverse lists are checked literally. This identity also proves that
permuting commuting setup gates is an equivalent construction.

Right multiplication by S leaves the pivot columns of D unchanged and kills
all selected dependent columns modulo two. The verifier checks every entry
of the new compensation against D S. All its ADDs are at ZERO and read only
helpers whose declared entrance frame is ZERO. The changed basis has

    R429 E2: 318 dependent helpers, 12,756 setup ADDs and 12,756 inverse ADDs;
    R438 E2: 327 dependent helpers, 11,389 setup ADDs and 11,389 inverse ADDs.

The integer kernel statement is N^2=0; the dirty cancellation D S is a
binary statement. No integer equation D S=0 is asserted.

## Ten actual rank-one entrances

The selected R429 helpers, in construction order, are

    242,467,462,469,463,464,367,401,444,470.

Their actual first frames are, respectively,

    7,29,49,52,54,56,65,76,79,94.

Seven have zero D column. The remaining three have the same D columns as
helpers 233,360,385, respectively; these columns have weights 19,17,18.
The setup gates are

    233 += 242,   360 += 367,   385 += 401,

each at the genuine common first frame for that pair. The three companion
first MOVEs are advanced and retained. The selected ten helpers are instead
supplied at their rank-one frames, so their ten ZERO-to-rank-one MOVEs are
deleted. The complete initial compensation is D S modulo two. The three
inverse basis ADDs occur at actual FULL common frames after cleanup.

The checker verifies the entire inherited scalar sequence, its common frames,
the changed starts, and the exact multiset of MOVEs: it is the original
multiset with precisely those ten rank-one queries removed. Source and target
cuts remain unchanged. The six basis ADDs are included in the word; no new
recursive query or private cell is used.

## The two global E2 words and the old snapshots

Let E=span(e0,e1). Dependent helpers enter at E, pivot helpers enter at ZERO,
and all helpers end at FULL. Initial compensation uses only pivot helpers at
ZERO. All helpers are then brought to the genuine common E setup cut, and S
is executed. Every later original scalar frame f is replaced by span(f,E).
All forced public climbs are emitted and paid. Finally S^-1 is executed at
FULL. The independent checker matches every inherited ADD's operands, sign,
chronological position and joined frame; it also matches every inherited
COPY/ERASE to its joined source/private frames and every declared final frame
to the old final frame joined with E.

The R429 FULL variant retains its original source rank-one entrances, source
FULL exits, target ZERO entrances and target FULL exits. In the old R438 word,
the target exits change from K_p to K_p+E. Exactly 83 become FULL and 28 remain
at their original rank-seven cap. All 222 public frame paths, including every
rank along them, are checked against the saved paths.

The old word still pays for all nine copied totals. Their helper sources are
471 through 479. A copied source at U+E is read into the one fresh zero private
field at E, with tariff dim(U+E)-2. The source cannot be modified while its
snapshot is live. Each scatter is at the genuine common E frame. ERASE checks
the exact original snapshot and restores the private cell to integer zero
before reuse. Forward and reversed lifecycles are both checked. The nine
tariffs are

    6,6,6,6,5,6,6,5,6,   with sum 52.

The two tariff-five sources are helpers 475 and 478 at frames 514 and 517;
the other seven source frames are FULL. The private frame is 636, the actual
coordinate E2 frame. This is one sequentially reused zero field, not nine
free snapshots or nine simultaneously available private fields.

This billing uses the predecessor's nested COPY/ERASE contract: the COPY has
the stated rank-difference tariff, and its matching ERASE closes the immutable
snapshot. The finite review checks that interface's premises and does not
independently admit an all-size COPY implementation.

## Complete signed and binary operators

The verifier uses dense signed rows, starting with all independent ordinary
input columns, and executes each literal emitted word. Every MOVE has the
declared current frame, strict nesting, and exact positive rank difference.
Every ADD uses distinct registers at the same actual frame. Every source and
ordinary helper output row is exactly its original integer unit row. Every
target retains exactly its own old-y coefficient and no other old-y input.
The private row, when present, is exactly zero.

Modulo two, the full map in every case is

    (x,y,h) -> (x,y+x,h),

with the private zero restored. The endpoint integer operator has form I+T,
where only target rows of T are nonzero and every target input column of T
is zero. Hence T^2=0 and its exact inverse is I-T. A separate literal reversed
replay, starting from arbitrary identity columns and a zero private cell,
matches every entry of I-T. This proves both inverse compositions over the
integers, rather than checking only parity or an inverse on clean helpers.

Each R429 orientation compares 423,801 entries. Each R438 orientation compares
436,260 entries, including the private row. The forward maxima of the complete
prefix row L1 norm are 874, 8,770 and 31,416, respectively. The target matrices
have 6,497, 36,182 and 44,884 nonzero even helper coefficients, respectively.
These provide explicit evidence that the clean target map is only a binary
VALUE claim. Signed targets are preserved with their actual integer lift.

## Complete local bill

| Fixed word | H by query rank | Mass | ADDs | Ordinary helper residuals | Private peak |
|---|---|---:|---:|---|---:|
|Ten rank-one entrances|{1:1396,2:1342,3:79,4:44,5:93,6:11,7:9}|5087|12884|10 width7 +419 width8|0|
|R429 common E2|{1:1184,2:1254,3:108,4:89,5:7,6:9}|4461|34620|318 width6 +111 width8|0|
|R438 CLEAN common E2|{1:1170,2:1254,3:108,4:94,5:13,6:16}|4539|34643|327 width6 +111 width8|1|

The histograms include every literal MOVE and every paid COPY. They are
independently regenerated, including ADD counts and prefixes. The ten-entrance
histogram equals the pinned R429 FULL histogram minus 10 H1. The complete
coverage checks are

    5087 = 111*(7+8) + 419*8 + 10*7,
    4461 = 111*(7+8) + 111*8 + 318*6 = 5097-318*2,
    4539 = 111*7 + 28*7 + 83*8 + 111*8 + 327*6 + 52.

Equivalently, the old CLEAN baseline mass is 5,121 with original COPY sum 63,
and 4539 = 5121 - 327*2 + 83 + (52-63). No old target cap or copied-total
tariff is retained for free after its frame changes.

## Actual rational ADDRESS implementations

For every used frame U, choose independent integer root rows B. The independent
projector is

    P_U = B^t (B B^t)^(-1) B.

It is compared entrywise with the saved projector. Its span, dimension,
symmetry, idempotence, RREF basis and saved Gram determinant are independently
checked. The two words use the same 434 actual frames. Their MOVE/COPY pair
sets contain 1,589 and 1,599 pairs; the former is a subset of the latter, so
1,599 distinct pairs cover both complete words. There are 160 used frames
whose projectors have odd denominators.

For each nested pair A subset U, P_U P_A=P_A=P_A P_U. Thus

    W=P_U-P_A,   W^2=W,   rank W=dim U-dim A.

For the supplied invertible rational C, the verifier checks both inverse
products and

    C diag(I_rankW,0) C^-1 = W.

Writing D_P=[[I-P,P],[P,I-P]], every one of the 16 ADDRESS columns is checked
in the identity

    diag(C,C) D_coord(rankW) diag(C^-1,C^-1)
        = D_W = D_U D_A.

This includes every copied-total source/private pair, whose nested difference
has the paid COPY rank. It is not a substitution of scalar rank for an
unverified ADDRESS operator.

Both the independently selected integer-root Gram determinants and the saved
rational bases/projectors/GL inverses have exceptional prime factors only
2,3,5. Away from these characteristics, the root bases keep their rank, the
Gram inverses and GL charts are defined, and the exact matrix identities
specialize. The exclusions are a sufficient set for these explicit charts;
no minimal-exclusion theorem is claimed.

These C matrices are rational GL adapters. Odd denominators really occur.
They therefore do not establish compatibility with an orthogonal/dyadic
recursive-query alphabet, an allowed all-size compiler, scalar scan costs or
a physical tape implementation. Those remain admission obligations even
though the complete finite matrix identities hold.

## Paired physical helper contract

For a helper supplied physically as u at entrance E, define its logical dirt
to be h=D_E^-1 u. This is a coordinate description of an arbitrary input, not
an executed entrance query. Since the literal non-target scalar row is h at
exit U, the actual physical output is

    D_U h = D_U D_E^-1 u.

Over binary VALUE arrays the target coefficients of this arbitrary logical
dirt cancel. Consequently the paired contract is independent of an external
choice of dirt value. Integer target dirt need not cancel, as noted above.
An owner must route the physical pair (E,U); using only the exit width or
requiring the former ZERO-coordinate interpretation would be a different
contract.

Here U=FULL. For each of the ten actual rank-one entrances, the checker
verifies all 16 ADDRESS columns of

    D_FULL D_E^-1 = D_(E-perp),   rank(E-perp)=7.

For common E2 the residual is the coordinate width-six interchange. The
literal coordinate permutation with row order (2,3,4,5,6,7,0,1) maps E-perp
to the first six axes; its conjugation is checked. The 111 pivot helpers
retain ZERO/FULL residual width eight. These paired residual identities do
not themselves supply chronological helper owners or a bank caller.

## Defect controls and limits

For each fixed word, removing its actual inverse basis causes an arbitrary
dirty-helper column to leak into another helper. Removing one matching setup
and inverse basis pair while retaining the new compensation exposes odd
target dirt. Restoring a selected helper's old ZERO entrance fails an actual
typed frame check. In the old word, deleting an actual ERASE fails the next
snapshot lifecycle check. A one-entry perturbation of a residual projector
fails an explicit ADDRESS column. Each control changes the candidate and is
checked against its intended failure predicate.

This review does not search other common planes, other ranks or partitions.
The seven-coordinate hybrid census, bank lower bound and chronological owner
result are separate mathematical obligations. Nothing here admits a positive
full caller, rounded suffix-error bound, all-size source/tape realization,
unconditional multiplication theorem or new kappa value.

The historical `GLOBAL-KERNEL-BOOST.md` section “Selective variants and source
snapshot control” is expressly outside this result. Its finite selective
screens, exposure-mask searches and proposed snapshot corridor are not
replayed or certified here. Their preservation as historical text supplies no
additional theorem to this three-word package.
