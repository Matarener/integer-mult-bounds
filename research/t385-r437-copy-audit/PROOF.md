# R437 complete-stream COPY applicability and its cost boundary

This is an application audit in the ideal exact-stream model, with a new
source-bound implementation of the checks. The model, gauge argument and
rank-seven correction are credited to alephnan's PR1627 and the earlier
PR540 framework; PR2088 and the selected COPY separation/two-copy physical
audits already distinguish complete operators from their ranks. No new
all-size compiler, supplier admission or unconditional multiplication theorem
is proved here.

## 1. Exact object and hypotheses

The R437 input is PR3647 at
`a24f9ff95c12fd0b6792e3f710569237efd72db2`. Both literal local instruction
lists are reconstructed from the retained WORD and compared in full against
the OQ4 hosted template. There are 659 persistent inputs: 111 SOURCE, 111
TARGET and 437 arbitrary dirty helper functions. The selected PR589 word is
retained only to reconstruct the earlier capture rows and compare dirt.

Let K have characteristic other than two, let the address domain be
`X = K^64 × K^64`, and let M be the F2 vector space of **all** functions
`X -> F2`. An initial physical input may be any member of M; different
inputs may be correlated. Boolean XOR coefficients and address coefficients
in K are different fields. We do not identify them.

For a rational symmetric frame projector P, define

    D_P = [[I-P, P], [P, I-P]].

The checker reconstructs all 636 projectors from literal root vectors by exact
orthogonalization, checks idempotence and trace, and checks `D_P² = I`.
Every resulting address entry is dyadic. Thus the exact matrix identities
specialize to every such K. The rational characteristic polynomial of a
rank-r idempotent is `t^(8-r)(t-1)^r`; this identity also specializes, and
an idempotent is diagonalizable with eigenvalues 0 and 1. Its rank remains r.
In particular the nine COPY frames have rank seven in every permitted K;
D_P itself is an invertible 16-dimensional address map, not a rank-seven
Boolean matrix.

The displayed 16-by-16 maps act on the local eight coordinates in each half
and extend by identity on all exterior coordinates. The input functions
remain arbitrary on the **full** address domain. At stage s the inherited
gauges include a common exterior projector E_s. Its factors commute with
local maps and cancel in every relative transport. For reflected calls,
`D_(I-P_a) D_(I-P_b) = D_Pa D_Pb`; the two local full-swap factors also
cancel. Hence both literal orientations use the checked local relative maps.
This is the inherited common-chart realization premise, not a new proof that
a uniform tape compiler implements those charts.

## 2. Universal function simulation

An interpreter term `(i,A)` denotes the entire arbitrary initial function
`f_i composed with A`. A row is an XOR of such terms. Actual MOVE transport
right-multiplies every A by its relative address map. Common-frame ADD XORs
the complete rows. No dirty column, exterior coordinate, or frame action is
silently omitted. This is distinct from testing one finite address grid.

Equivalently, if a physical row is f with gauge Gamma, define its decoded
row to be `c = f composed with Gamma`. MOVE from a to b sends

    f -> f composed with Gamma_a composed with Gamma_b^-1,

so c is unchanged. Equal-frame ADD adds decoded rows. A fresh COPY into a
blank owned private row at ZERO copies the decoded row by the same relative
transport. For a retained center at frame P, that transport is its actual
D_P, in either orientation.

ERASE is accepted only if the private row equals the **current** center
transported by that same complete map. This is a chronological equality for
all inputs, not merely equality after eventual cleanup. R437 never writes or
moves the center inside its COPY window and never writes the copied row;
all readers are the designated ZERO-frame targets. Its guard therefore
holds, and the owned private row may be returned to blank. The checker also
verifies every full endpoint, rather than trusting this schematic induction.

For local source ray S and complementary target K=I-S, the physical endpoint
has source transported by D_K, target transported by D_K plus source
transported by the full local swap, and helpers transported by the full local
swap. This follows from the checked decoded map `x'=x, h'=h, y'=y+x` and
`D_S D_K = D_I`. Both literal directions reproduce the expected operator
rows on all 659 input function symbols. Equal formal operator expressions
remain equal after substituting any correlated functions for those symbols;
independence is a verification device, not a physical freshness assumption.

## 3. The actual changed dirt and a discriminating weaker contract

The first, second, third, fifth, eighth and ninth forward captures keep their dirty
support after surviving-register renumbering. The former center 475 loses
old helper 470 and now has 62 rather than 63 dirty columns. Former centers
477 and 478 replace old helper 464 by surviving helper 340; their dirty counts
remain 46 and 43. The complete maps, SOURCE rows, COPY ranks and target
incidences remain fixed. These facts are credited to the original R437
capture note and PR3700; this checker rederives them and exercises the
physical pullbacks of the current construction.

There is a small source-bound counterexample to a **weaker**, label-specific
COPY contract. At current center 475/frame 515, take input function340 to be
the constant-one function, with every other initial function zero. The new
complete capture is one. Restricting COPY to the old capture's surviving
named dirty subset omits 340 and returns zero. The transported ERASE guard
then fails. The same issue occurs at center 476/frame 516. This is not a
counterexample to R437's explicitly universal contract, nor an allegation
that an existing implementation performs this projection. It proves why
clean SOURCE rows, dirt counts, or an older named-label audit cannot by
themselves discharge the current complete-stream implication.

The executable controls also reject dropping all helper dirt, replacing the
map by a full swap, using a different rank-seven map, ignoring MOVE address
actions, aliasing the private family with a dirty persistent family, and
omitting the linear disposal charge. They remain active under `-O`.

## 4. Physical ownership and scope of composition

The private owner is family 28416 at the invocation's common cover class d.
Every persistent owner in all 288 call descriptors has family strictly below
28416. Family tags therefore separate the private stream from SOURCE,
TARGET and hosted dirty inputs for every d, regardless of correlated values.
The template reserves nine private families; this word has only one explicit
live copied stream. No new private family is added.

The checker binds each of 125856 helper owner occurrences to its literal
slot and reconstructs its pending-axis support from the actual idle levels.
Within each invocation, helpers sharing a physical family have distinct
support charts; active data families are disjoint from hosted helpers.
The injectivity argument for those orthogonal charts is the inherited
PR1627 construction. The prior PR3883 transition audit independently checks
the complete chronology and residual suffix geometry; we do not rebrand that
coverage as a new whole-hosting proof.

Once a complete call returns its private stream blank, sequential invocation
permits reuse at every stage/replica/cover class. This addresses the explicit
copied stream. It does **not** prove that a recursively implemented COPY
child's scratch or parked tape fits in the eight other reserved families.

## 5. Complete local bill versus an implementation cost theorem

The literal local bill in each orientation is:

| Item | Count / charge |
| --- | ---: |
| Persistent arbitrary input functions | 659 |
| MOVE events | 2906 |
| Ordinary scalar ADDs, including dirty compensation and cleanup | 24208 |
| Scatter ADDs, already included above | 527 |
| COPY / ERASE episodes | 9 / 9 |
| Recursive COPY rank mass | 9×7 = 63 |
| Peak explicitly live copied streams | 1 |
| Complete local recursive rank mass | 5113 |
| Cancellation-free positive bound, forward / reverse | 49347 / 1113998 |

A complete-stream COPY operates on one stream, not separately on each dirty
symbol appearing in its linear description. If a source-preserving rank-r
COPY implementation costs `C_r(V)` and uses child scratch `S_r(V)`, then an
episode with k target reads costs that implementation **plus** k scalar stream
ADDs, complete private-stream disposal, routing/descriptor handling and any
required precision/recovery work. The copied value occupies one owned stream
in addition to `S_r(V)` and control storage. The model does not imply a bound
on C_r or S_r merely because D_P is a known matrix.

The retained convention charges one rank-seven child for each COPY and
linear complete-private-stream disposal for its paired ERASE. Guarded equality
licenses disposal of the owned copied output; it does not license erasure of
original/helper dirt. An implementation using another recursive transform to
uncompute instead would require another charge. We neither assume that
alternative is necessary nor assume its cost is zero.

Across 288 local calls, the actual counts are 2592 COPYs, paid COPY rank mass
18144, and 2592 linear disposal episodes. The checker rederives the whole
paid profile from the literal slots and residual suffixes, including all
903456 edges. It retains the existing source/MOVE/COPY J coefficient 2002560,
ordinary ADDs/bridges, high-digit, stock, compiler, route selectors, matrix,
prefix and disposal terms. Prefix/coefficient widths remain 177 bits, charged
192; two-level width 393 is charged 512; ROW 18355 is below 20161. The bad-class
bound 98682 is retained under the131072-per-edge overcharge and bad fraction
10^-16. No further root calculation is needed for this applicability audit.

Those coefficient formulas and their implementation interpretations are
**inherited bounds**. Recomputing their integers does not derive a new tape,
routing, scratch, precision or volume-normalization theorem. The precise
remaining handoff is to bind C_7(V), S_7(V), owned output and linear disposal
to an actual uniform caller on arbitrary complete streams and then prove
that caller's time, storage and recovery inequalities. Neither finite matrix
identities nor nine reserved family tags supply that missing implementation.
