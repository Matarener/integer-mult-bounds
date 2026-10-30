# Stable backing at the actual CRT row consumer

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.

## Proposition and inherited hypotheses

Fix the admitted PR5625 domain: ell>=2; a power-of-two number of axes;
h_i in {ell-1,ell}; pairwise coprime 2<=s_i<2^h_i; arbitrary padded
coordinates; one fixed aligned node of size n=2^level; and eight distinct
protected dirty words with legal heads. Put P=1+sum of node widths,
H=max of right-child widths, and S=2+sum of right-child widths+n/2.
For every finite legal row sequence, the adapter in this package reuses the
same backing for each numerical and ROM/query ownership role, preserves the
PR5625 current-state row semantics, and retires every owned role after each
row. Retained work is exactly staging capacity plus the sum of the historical
capacity of each role. This is a source-relative ownership theorem: the
numerical Entry, RowEntry, ROM compiler and query correctness/retirement
contracts of the pinned predecessors are hypotheses. No selected-frontier
assumption, native admission, complete key, or multiplication theorem is proved.

The fixed node, precision, finite alphabet and compiled topology do not change.
The caller supplies pairwise distinct blank backing and obeys single-owner
use of the Workspace. External mutation of its Python emulator objects and
failure recovery are outside this valid-execution theorem. Runtime numerical
values are never inspected, serialized, or decoded by the new adapter.

## Exact source seams and complete ownership map

query.py is the pinned PR5496 RowQuery source with precisely the six substitutions
in SEAMS.json. verify.py reconstructs that file byte for byte from the frozen
input and seam table. Those substitutions add an explicit Workspace parameter,
begin/end ownership calls, an Entry facade, and backing acquisition at the two
Tape constructor sites and ROM service dictionary. The body of every numerical
and ROM algorithm, result query, cleanup and source update is unchanged.
Entry.new_port is overridden through the documented subclass seam, without
patching a global constructor. Every setup write remains a source tape action.

| Stable role | Count | Original constructor and aliases | Retired head |
|---|---:|---|---:|
| numeric.guide, canonical_left, canonical_right | 3 | RowEntry's three entry.Port calls | 1 |
| numeric.word.8 through numeric.word.63 | 56 | Entry.word_storage(False); HostedWord.port aliases this same port | 1 |
| numeric.template | 1 | Entry.word_storage(True); arena.template.port aliases it | 1 |
| numeric.padded_left, padded_right, output | 3 | Entry's final three new_port calls; result.stream aliases output | 1 |
| rom.<REGS> | 44 | Unchanged ROM execute scratch dictionary | 0 |
| rom.arena, spool, layers, rom | 4 | ROM service dictionary; produced_layers/produced_rom Tape wrappers alias two of these | 0 |
| rom.h, modulus, selected_layer, offsets | 4 | Header Tape objects; service.update aliases their cells | 0 |
| query.coordinate, countdown, output | 3 | Physical joined query Tape constructors | 0 |

Thus 63 numerical +52 ROM +3 query roles =118 distinct backing objects.
The eight dirty words are borrowed, never acquired; source and staging are
separate. ROM emulator head dictionaries are finite-control configurations,
not extra cell backing. The unchanged execute returns every service head to
zero; the wrapper begins there. There is no hidden extra ROM list constructor.
Inactive rows call neither numerical nor ROM constructors, acquire zero roles,
and perform no tape work. Existing retired backing remains retained and billed.

## Reentry and historical-tail induction

Inductively suppose a role's full retained extent is blank after its prior use.
A numerical port is retired at head one. Reentry performs a paid unit move to
zero, a blank read, LEFT write and unit move to one. Fresh numerical entry uses
the same read/write/move except for the unnecessary reverse move. The original
Port constructor starts at zero, writes LEFT, and moves to one. Hence the new
entry has exactly the source's head and visible cells. All remaining setup
(guide, canonical streams, word slots, template and padded streams) is unchanged.

ROM/query roles are already at zero with blank backing. Each new wrapper merely
names that backing and starts its finite-control head at zero. Source microcode
rebuilds all headers/scratch and subsequently erases its current data. For each
role, compare execution on its historical blank extent to execution on a fresh
infinite blank tape. Each read sees the same symbol, each write changes the same
cell, and each unit move reaches the same position. Existing blank storage and
newly appended blank storage are indistinguishable to every source instruction.
No instruction reads capacity. Finite-control decisions and output therefore
agree step for step. Capacity can only grow. Old cells outside the current
visited extent stay blank; cells inside it are blank on retirement by the
inherited source cleanup contract. This handles a shorter canonical stream
after a longer one without a host clearing loop or truncation. Blankness of the
full historical extent is checked independently in the finite verifier.

The source has no scratch constructor beyond the mapped seams: RowEntry uses
three ports, Entry allocates 56 private slots, one template and three streams,
and the query creates exactly the displayed 55 physical ROM/query backings.
The verifier additionally compares the actual predecessor footprint to this
map and checks stable identities across all active rows.

## Current-state causality and source borrow

Workspace.begin rejects a second query while its first borrow is live. The
unchanged query recomputes numerical output from the current source on every
entry; no offset or prior result is cached. The unchanged retain_stream first
copies the result into staging. RowQuery.close erases the owned result and
retires Entry and RowEntry. Only then does Workspace.end release the borrow,
and the unchanged consume_into_source writes the staged right-child coordinate
bits into the same source. The valid caller must use this ordering. A guarded
source in the verifier rejects an actual write while the borrow is live, and
predecessor semantic mutations check omission of close and incorrect updates.

Induction using the predecessor row theorem proves equality to its logical
Caller permutation after each row, including idle and padded coordinates.
The source shape and entry head are unchanged, so the next query is admitted.
The inherited involutory row property makes reverse-order rows the inverse;
forward then reverse therefore restores the entire source and protected words.
This is not a proof for changing left-child epochs or changing node precision.

## Retained capacity and positive cost

Let c(r,t) denote the cells visited/retained by role r through row t and
C(r,t)=max_{u<=t} c(r,u), with initially one blank cell for a fresh acquired role.
A role keeps its one backing, so after any active prefix total owned backing is

    S + sum over the 118 roles r of C(r,t).

Before any active row only the supplied one-cell staging exists. The sum is
rolewise; max_t(sum_r c(r,t)) is not the retained sum. The crossed-peak control
(9,1), (1,9) distinguishes 18 retained cells from largest row total10.

A deliberately loose source-derived envelope, independent of row count, is:
57 numerical word/template roles each <=P+2; guide <=P+2; the other five
numerical streams each <=n(2P+4)+2. Canonical streams are no longer than padded
streams; each record has two P-bit fields and four delimiters. Numeric output
has at most n/2 records. Each of the52 ROM roles is bounded separately by

    B(P,H)=5P 2^H(H^2+3H+1)+2^H(4H-1)+48P+2H+104,

the inherited complete bank bound at maximal right height. This use of a bank
bound as an upper bound for *each single role* gives a loose52B, never a
replacement of sum-of-maxima by max-of-sums. Coordinate and countdown each
have capacity <=H+2 and query output <=S. Thus an explicit total envelope is

    2S +58(P+2)+5[n(2P+4)+2]+52B(P,H)+2(H+2).

It is intentionally not advertised as a sharp coefficient. The exact finite
receipt records all118 individual historical capacities.

All original setup, arithmetic, ROM, disposal, staging and source scans remain
charged by the predecessor's T_row. Relative to that allowance each numerical
acquisition adds a blank read and, on reuse, one reverse move: at most126 tape
actions per active row. Charge each first acquired blank cell positively, at
most118 total. A conservative per-active-row allowance T_row+4*63+118 covers
them. Role/alias/lease bookkeeping is bounded finite control on118 roles;
if counted separately, add a fixed compiled constant per active or idle call.
No host operation clears an input-sized region. Growing a tape uses the same
local write/move allocation semantics and retained capacity charge as the
source emulator. This is not a native runtime/allocator benchmark.
