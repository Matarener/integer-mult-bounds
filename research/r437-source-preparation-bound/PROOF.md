# A monotone admission pass for the actual child-program producer

## Claim and source boundary

This is a source-bound optimization of `SelectedBinding.child_program` in the
retained physical caller. It executes the real `Callback` constructor, prime-power
and root-unit validation, chronological step arithmetic, `children.extend`, and
normal cleanup. The package-local adapter changes only admission's sequential
Program/Fields access. Frozen sources are unchanged; adoption is a separate decision.
It supplies a source-bound tape/word action ledger and candidate optimization for
this producer component of PR3983's Pi, not all preparation, coefficient
evaluation, payload execution, stock admission, or the complete multiplication bound.

The accepted-domain theorem assumes finite well-formed Program/field record tapes,
canonical fixed-width words with arithmetic margin, a fixed finite source vocabulary,
sufficient numerical slots, and valid child request labels supplied by the caller.
The field payload may be arbitrary: neither original nor adapted admission checks
all high digits or prepares matrices. Full raw-field shape, canonical digit values,
and actual selected specification supply remain upstream premises. The numerical
producer still performs its original prime-power, unit, history and code checks.

Write I,L for index/residue word bit widths, Q for the fixed source-code width,
h for parent history depth, and n=h+1 for internal admission. A root record has
r=2I+L+5 symbols; one step has c=Q+2I+90 symbols; a full 64-by-64 raw field has
F=Q+2+4096(L+1) symbols. Let P=r+hc and D=r+(h+1)c. Lengths exclude LEFT and the
adjacent blank. All formulas below count actual calls to Tape/Word read, write
and unit step, including rewind. They do not equate Python runtime, AST execution,
object allocation, or a macro dispatch with a primitive finite-state transition.

## Why the original admission is quadratic

`Program.step(j)` invokes `seek_record` from LEFT through the root and j-1 steps;
`Fields.check_code(k)` invokes the same procedure through k full fields. Every
call returns the tape head to position 1. Callback admission requests program
steps 1,...,h and field slots 0,...,h, then separately checks the end positions.
No coefficient evaluation or payload is needed for this repeated work to occur.

For the complete original child-program producer the Program tape invoice is

    reads = 8r+1 + h(3r+2I) + c[3h(h+1)/2+5h] - h(h+1)/2
    writes = 0
    moves = 6r+10 + h(2r+2) + c(h²+5h).

The Fields tape invoice is

    reads = (3F-1)n(n+1)/2 + n(2Q+4) + 3
    writes = 0
    moves = F*n(n+1) + n(2Q+6) + 4.

For example, seeking field k, decoding its code and rewinding costs
(3kF-k+2Q+4, 0, 2kF+2Q+6). The final end check costs
(3nF-n+3, 0, 2nF+4). Their sums give the Fields formula.
For Program, `root` costs (3r-4,0,2r+2), step j costs
(3r+(3j-1)c+2I+1-j,0,2r+2jc+2), final end checking costs
(3P-h+2,0,2P+4), and extension's source copy costs
(2r+3hc+3,0,2P+4). These sum to the stated complete invoice.

Thus a claim of linear work in serialized input length for this original admission
is false when history is a variable. This is a statement about this producer's
repeated scans, not a universal lower bound on source validation or multiplication.

## Adapter and semantic invariant

`forward_fields.py` authenticates the complete normalized ASTs of the admission
method and Program.root/step, in addition to the verifier's full source hashes.
Its exact transformations are:

1. Each of the two chronological `Fields.check_code` call sites consumes the next
   field; the two leaf/internal `end` sites check the current blank and rewind.
2. Program.root parses the original root body and advances across its final
   RECORD_END instead of rewinding. Program.step retains positive-level checking,
   its exact finite/word parsers and final delimiter check, removes the initial
   seek, and advances across its final delimiter instead of rewinding.
3. The final program seek is removed; its original BLANK assertion and rewind
   remain. A temporary Program view is installed only around admission and restored
   in `finally`. Subsequent `weight`, `extend` and random-access operations see the
   original Program object. No borrowed tape or numerical word is copied into a
   Python integer as part of the adapter's execution.

After j historical iterations, the program cursor stands immediately after step
j (after ROOT for j=0), and the fields cursor immediately after field j-1 (at the
first field for j=0). The unchanged encoded `count`/`depth` loop selects the next
step and supplies the expected field code. The original step arithmetic, chronology,
rank, branch, reversal and proper-size predicates see exactly the same decoded
words as before. The next iteration preserves the invariant. At termination the
existing exact-program-depth assertion sees the same blank; leaf admission checks
h fields, while internal admission additionally consumes current field h and
checks h+1 fields. Both public heads return to 1. The root/program view is restored
on every exit; the original Callback abort path restores borrowed heads and words.

Induction therefore gives the same accepted relation and, after successful
child_program, the same returned bytes and numerical ownership. It is not a claim
of identical exception timing on every malformed tape. For malformed records an
adapter may discover missing termination earlier. The finite negative controls
check their named rejection and cleanup observations; they are not a proof of
transactional recovery under arbitrary interruption or allocation failure.

## Exact improved record bill and lifetime backing

The adapted complete producer has Program invoice

    reads = 5P+2hI+1, writes = 0, moves = 4P+8,

and Fields invoice

    reads = n(3F-Q-2)+3, writes = 0, moves = 2nF+4.

The new Program admission alone costs (3r+2hc+2hI-2,0,2P+4);
the unchanged extension source copy supplies the remainder. Each adapted field
check reads its Q-bit code, skips the rest through RECORD_END exactly once, and
the final rewind visits the complete prefix once. For leaf-only admission use
n=h in the Fields formula and omit extension/output from the Program invoice.

For both producers, creating the output costs exactly
(2D+1,D,2D+2). The two empty pending/value stacks contribute two reads and four unit moves to
Callback.close: each `empty()` performs one read and two moves on its top tape.
Their two reverse tapes remain at their initial positions.
All actual empty-stack work is explicitly measured; it is independent of h.
The verifier includes all seven record tapes in lifetime backing: parent Program
P+2, Fields nF+2, returned Program D+2, and four stack tapes of two visited cells.
Hence the producer record footprint is exactly

    P + D + nF + 14 cells.

The adapter adds no tape and no numerical word. This lifetime bound counts LEFT,
the adjacent blank, and cells visited after erasure; it is not live occupancy.
The returned Program remains owned by the caller. Its later copying and erasure
are separate preparation charges already exposed in PR3983.

## Numerical work and root/history coupling

Numerical context and chronological checks remain essential. A deliberately loose
source-derived envelope, valid for either producer's normal successful path, is

    U = 100000[(h+2)²(I+1) + (h+2)(I+1)² + (L+1)³]

Word read/write/unit-move actions. This is not a timing extrapolation. The following
sufficient bounds follow by counting the fixed-width loops in `words.py`:
zero/free/copy/compare/add/subtract or any fitting literal cost at most 100(b+1);
divmod at most 1000(b+1)²; times_small by <=128 at most 2000(b+1);
ring multiply at most 1000(b+1)²; inverse at most 10000(b+1)³.
The binary division loop has exactly b iterations. The Euclidean inverse has at
most 2b+1 quotient iterations, since every two nonterminal remainders decrease
by at least a factor two. The prime-power check has at most L quotient reductions.
These bounds include allocation initialization, operand rewinds, and freeing.

There are (h+1)(h+2) original seek-counter decrement iterations and 2h+3 seek
invocations. A seek's fixed numeric overhead costs at most 500(I+1), and each
counter decrement/zero-test/free costs at most 300(I+1). Thus all seek counters
cost at most 2000(h+2)²(I+1). These are absent in adapted admission.

One historical step has at most two index divisions, one <=128 multiplication,
two parsed index words, and fewer than twenty further linear word operations
(including the outer loop's count compare/increment, chronology compare and frees).
Using the displayed bounds, it costs at most 10000(I+1)². Root parsing, three
index literals, the outer loop's terminal test, extension (at most two divisions,
one bounded multiplication), five index append/read word scans, and final frees
cost at most 20000(I+1)². Therefore the entire non-seek index bill is bounded by
20000(h+2)(I+1)². Read/append word scans here charge their Word side; their record
Tape side is already priced above, so neither side is omitted or conflated.

The residue side consists of the root-word parse/compare/unit inverse plus
prime-power validation and normal freeing. The latter uses at most L divisions,
linear comparisons, one literal of the fitting fixed prime q, copies and frees.
The displayed primitive bounds give at most 20000(L+1)³ for this entire side.
Consequently the sharper aggregate bound

    2000(h+2)²(I+1) + 20000(h+2)(I+1)² + 20000(L+1)³

is already sufficient; U above leaves additional margin and is the bound checked
in the receipt. This argument counts loops from source rather than fitting U to
finite measurements. The adapter removes seek-related numerical work; unchanged
residue counts and chronological parsed-word traces are checked, not identical
index action counts.
Finite vocabulary checking and object/slot bookkeeping are not Word actions;
a finite-state implementation must add its fixed-source dispatch/slot tariff.

Inspection of the straight-line owned-word lifetimes gives a conservative bound
of 64 additional index words and 64 additional residue words above protected
entry ownership. This covers the root/depth/current words, two parsed step words,
division's quotient/remainder/scan/shifted temporaries, Euclid's live pairs and
multiply temporaries; these inner loops do not stack recursively. Four record
stack tapes remain empty during admission. For a reused arena with B already
created slots and p protected live slots, created slots never exceed max(B,p+64),
because free slots are reused before allocation. Include its template separately:
(max(B,p+64)+1)(b+2) backing cells, plus slot metadata and finite code tables.
This is an upper bound, not a claimed sharp physical reserve coefficient.

Every accepted history step shrinks its parent by at least a factor 21/32:
good rank <=42 yields child <=42*parent/64; pair/unit/half shrink further.
Since (21/32)²<1/2 and canonical root_size<2^(I-1), a positive h-step final size
implies h<2(I-1). For a successful extension final_size>=64, so h<2(I-7).
This is actual root/history coupling, not the assumption that a unit resets
serialized history. With fixed codec widths it absorbs the original quadratic
scan in an O(I²F+I³+L³) polynomial; the adapter improves the record component
to O(IF+I²+IQ+L), while the conservative arithmetic envelope remains O(I³+L³).
It does not alone compare this preparation bill to the original-width stock.

## Remaining obligations and credit

A completed caller bill must still add child_extents, read_prefix and actual raw
field/directory generation, geometry/context construction, coefficient weight
and matrix preparation, full physical role maxima, ownership/refinement tariffs,
and actual original-width stock. This package supplies no generated R437 catalogue
or GL64 production payload; its theorem applies to the actual generic producer
under admitted source specifications, and its synthetic and explicitly peer-derived projected-definition fixtures exercise
that acceptance path. The projected Q=6507 code/tag/low identities are checked
with canonical LowCodes, but source-plan/good-class reconstruction is not repeated. The new adapter is a candidate for adoption, not an installed shared change.

Credit Jose Manuel / jmbarrancoml for SelectedBinding and the physical caller;
David Arias/PR2753 and the retained controller, Program, Fields and child grammar
authors, including Nick Petalas and the encoded-word/continuation lineage.
PR3983 supplies the prior checkpoint and explicit Pi boundary. PR3936/3950/3967
and the R437/OQ4 source lineage supply the motivating caller context. New source
analysis, forward-only admission adapter and evidence: Chris R / Clear1nsight
with substantial OpenAI Codex assistance. Same-session AI review is distinct
from independent human or formal-kernel verification. Apache-2.0.
