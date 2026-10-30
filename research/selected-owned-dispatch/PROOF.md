# Fixed-tape signed-query suspension and return

This is a scoped physical refinement, not a whole selected-caller admission.
Mason Hale with substantial OpenAI Codex assistance. Apache-2.0. It combines the
unchanged PR5116 query tables with PR5356 `Stack` and PR5368 `return_output`.
The imported source bytes are authenticated against main
`de5ec2e7a6074068452f45b1a191b5c72832df4a`; `SOURCES.json` records them.
Predecessor authors are JoyboyBrian (query), Ali Romman (stack/output return),
David Arias (finite assembler/counter macros), and their retained source lineage.

## What the prototype actually implements

`prototype.py` runs a finite unary-depth call grammar on a fixed bank of23 tapes:
sixteen payloads, one control, one descriptor, four reusable staging/output
relays, and a supplied unary depth guide. Eight payloads expose the exact query
ports X,Y,Z,WD,MD,W,M,T; role8 is a genuinely separate empty return destination.
The push presence bitmap marks all nine roles occupied, including empty role8,
as required by the predecessor output-return ownership contract.
Remaining payload roles are unused but retained to use the exact predecessor
interface. No tape is allocated by `Dispatcher.run`, `descend` or `ascend`.

There is no host recursion or per-depth Invocation object. A fixed interpreter
executes the unchanged243/248 instruction tables. The descent and ascent loops
read the actual unary guide and actual control-frame END/BASE markers. A single
resume-phase bit is physically saved/restored by the predecessor stack.
`Stack.pop`'s returned observer sizes and heads are ignored. No dispatcher or
codec operation consults `Tape.head`, `Tape.cells`, a length or an absolute origin.
Those fields are inspected only by hardware and the external fixture oracle.

The child fixture is deliberately not a Gaussian implementation. Each descendant
starts with X=Y=the parent's preparedZ. The deepest completed child is identity
on its preparedZ. Thus with d nested edges, input x and root destination y,
the exact final root destination is y+(d+1)x. This makes mistaken returns or
phase dispatch observable. Assume all intermediate signed values fit p bits.

For completeness, define F_0(x)=x for the leaf's completed identity interval.
The query node one level above it has destination initially x, so its returned
Y is x+F_0(x)=2x. Inductively a descendant chain of j query nodes returns
(j+1)x. The root starts with destination y rather than x and therefore returns
y+(d+1)x. Negative real/imaginary components are included. It suffices that
each component of x, y, every jx for1<=j<=d+1, and y+(d+1)x lie in the signed
p-bit range. The unbounded-depth statement quantifies over every finite d
satisfying that headroom condition; p may be enlarged as d grows. A fixed p
does not permit arbitrary large d for a fixed nonzero input.

## Seven symbols inside binary continuation segments

Let c(a) be the three-bit big-endian encoding of a in{0,...,6}. A logical tape
whose materialized symbols are a0,...,a(l-1) has physical current segment

    physical LEFT, c(a0), ..., c(a(l-1)), physical BLANK...

Here a0 is the logical query LEFT2. The physical LEFT delimiter belongs only to
the continuation representation. Logical BLANK4 is the binary word100, never
the physical segment delimiter. Code111 is rejected. A query logical head is
the start of a codeword or the first physical BLANK at the frontier.

The stateless facade realizes:

- read: inspect exactly three bits, decode one of seven finite values, and
  return by three unit moves; a frontier BLANK reads as logical BLANK;
- write: replace the three-bit code at the current position, returning the head;
- step: move three physical cells. Before moving right across an unmaterialized
  frontier BLANK, first materialize c(BLANK), avoiding an interior physical hole.

An induction on operations preserves alignment and contiguous physical binary
body. Every logical read/write/step has the same logical effect as the retained
seven-symbol Tape ABI. The protected logical LEFT remains the query rewind
sentinel. Query programs never move left of it, so they never read a parked
ancestor. At a boundary the stack sees only a contiguous binary body and its
own distinct LEFT sentinel; its original proof applies without modification.

Read uses at most10 physical actions, write9, and unit step13. Hence an I-step
query table uses at most13I physical reads/writes/moves. Fixed program-counter
dispatch has only the243/248 instruction states; this is a finite-control
constant, not an input-sized decoded counter. The local PR5116 bound therefore
gives a conservative3328N+3328 physical-action bound for prepare+finish, before
the separately paid boundary and child. This is a seam bound, not the selected
outer tariff. All encoded erased cells remain in historical backing until the
physical segment's retirement; no reclamation credit is assigned.

The additional `interior_blank_roundtrip` test suspends an arbitrary seven-symbol
body containing a BLANK between still-live symbols. A real child writes30 bits
in its segment. Encoding logical BLANK as the physical delimiter loses parent
data and the rejecting control catches that exact failure.

## Paid descent and occupied-Z return

At the query child cut, every logical query port has its declared origin head.
Three fixed BASE staging tapes receive complete physical copies of preparedZ,
WD and MD, including their coded logical LEFT and RIGHT markers. The copied
sources return to the exact logical heads. Stack.push then parks all parent
query fields/counters and its one-bit resume descriptor. New child segments
reuse the same sixteen payload tapes at the fresh delimiters.

The Z staging word is copied into childX and childY; descriptors into childWD
and childMD. ChildZ/W/M/T receive only their coded LEFT markers; their old logical
bodies are blank. The staging tapes are physically erased and rewound before
descent continues. These are real sequential copies, not pointer rebinding.

On return, the unchanged `return_output` first copies childY to its dedicated
relay, then retires every child segment, pops and restores parent state, and
installs the saved output into reserved empty role8. Calling it directly with
parentZ would violate its ABI: Z is occupied. The prototype instead explicitly
erases the old parentZ binary body, copies role8 into Z, retires role8 and returns
Z to its logical origin. The parent then runs the unchanged finish table.

This preserves all parent query fields other than the intended Z update, all
descriptors/counters and their heads, and every ancestor byte. In particular,
the parent W/M unary counters survive the child and drive the exact ADD/ERASE.
The three staging fields and output relay are shared across depths, empty at
every handoff. Role8 is charged as an extra simultaneous return field.

The predecessor's complete matched boundary invoice applies with the actual
encoded lengths. All staging, Z replacement and role8 retirement scans are
additional positive charges. Copies and clears use only sequential traversals,
so their cost is linear in the physical bodies traversed and independent of
ancestor length. No numerical claim cancels these terms against an old tariff.

More explicitly, let Lz,Lp,Lm be the parent preparedZ, WD and MD encoded body
lengths, including their coded logical markers. Let L be the complete childY
output length. A binary copy of L symbols, with initial source/target head
offsets h_s,h_t, costs exactly8L+2h_s+2h_t+14 actions. Clearing a body of length
L from offset h costs5L+2h+7. Rewinding to the physical origin and then moving
to the logical query origin from physical head0 costs6. New coded LEFT setup
costs12. These formulas follow by counting the literal loops and their final
delimiter reads; no routine receives L or h as an input.

The additional staged-input and occupied-Z return work outside PR5368's matched
push/return invoice is exactly

    34 Lz + 21 Lp + 21 Lm + 13 L + 283.

The terms include the three pre-push staging copies, the two child copies ofZ,
both descriptor copies, four new logical LEFTs, staging retirement, physical
one-bit phase setup/consumption, Z replacement and role8 retirement. Add this
to the predecessor's exact invoice

    13 Hp + 4 Sp + 38 k + 18 d + 5 q + 2 A + 2 Hc + 5 W + 17 L + 61,

where k=16, d=1, q=0, A=7; Sp/Hp and W/Hc are the parent and child encoded
body-length/head-offset sums at their actual cuts. Here Hp=Hc=24. Child execution
and both query tables are separate, positive costs. `check_invoice.py` independently
measures27 actual source boundaries and checks this exact equality, including
all three dirty-prefix lengths. It uses hardware extents only as a test oracle,
never to drive the dispatcher.

## General statement supported by the code/proof

For any finite unary depth d, p>=2 and positive M, arbitrary signed root fields x,y
with sufficient headroom for y+(d+1)x and the descendant partial sums, the same
fixed-bank grammar returns that result; rootX and descriptors are preserved,
private logical bodies are blank, physical descendant segments/control/relay
bodies are erased, and all declared heads return. Proof is induction on d using
the codec invariant, the inherited stack/output theorem and the unchanged query
table theorem. No fixture bound on d enters the program or induction.

This grammar does not shrink child volume. Its live path therefore legitimately
uses O((d+1)N) backing, not O(N). The selected compiler's shrinking fields and
compiled inventory must be supplied before invoking a root-volume bound.
Repeated completed invocations use the same segment origins and fixed relays;
for an unchanged local size/depth envelope their physical high-water marks are
reused, rather than allocated afresh for each sibling.

An exact retained-backing statement is available without pretending that endpoint
length bounds erased interiors. For each of the sixteen payload tapes i, define
a_i(v) as its maximum encoded binary body length anywhere in invocation v,
including private work later erased and delivered role8 output. At each child
edge e let s_i(e) be its actual parked binary body length and h_i(e) its head
offset. Define o_i(root)=0 and o_i(child)=o_i(parent)+s_i(e)+1. Then

    E_i = max_v (o_i(v)+a_i(v)).

For the control tape, E_c is the maximum root-to-node sum of
sum_i h_i(e)+2*16+d(e)+3. Here d(e)=1 and each of the eight query heads has
offset3 while all other heads have offset0, so every frame is exactly60 symbols.
The shared descriptor extent is at most1. Each of the four fixed relays has
extent equal to its largest complete staging/delivery body over the entire
history, with no depth multiplier. The unary depth guide is borrowed input;
its pre-existing backing is retained and counted in K0.

For every physical tape j with initial origin b_j and entry capacity K_j, its
final capacity is max(K_j,b_j+E_j), exactly as in PR5404. Sum this coordinatewise
over all23 tapes. The proof applies to partial execution as an upper bound,
because writes during a push/copy are prefixes of the completed extent. This
includes all physical LEFT markers, encoded logical BLANKs, erased child work,
warm tails and role8. Every relay starts empty between uses, and siblings reuse
the same origins; a new completed invocation cannot create a new depth region
unless its actual extent envelope exceeds the previous high-water mark.

Capacity here means the modeled allocated `Tape.cells` backing, including erased
cells, not Python object/list allocator overhead. A read of the first unwritten
frontier can visit one cell beyond that backing. If a visited-address bound is
also desired for these routines, add at most one frontier cell per tape, hence23
in total; do not label the exact backing formula itself an exact visited-cell
formula. Neither quantity ignores warm entry capacity.

For equal p/M and bounded depth, **assume each initial encoded current body has
O(N) symbols**, as in the canonical encodings used by the fixtures. Physical
BLANK tails may have arbitrary retained capacity and are charged in K0. Under
this encoded-entry premise, the query's original all-width visited-span
bound and the constant3 encoding give a_i(v)=O(N), s_i(e)=O(N), and relay
extents O(N); therefore total backing is K0+O((d+1)(N+1)). No constant here
depends on dirty ancestor length or on the number of sequential reuses. To turn
this into the selected O(root-volume) theorem, its actual shrinking child shape
and production local peaks must be supplied; the prototype proves no such
production substitution.

This premise cannot be dropped by counting all old capacity once in K0.
One can append arbitrarily many coded logical BLANKs after a descriptor's RIGHT;
the logical query accepts it, but the staging copy traverses and copies those
physical binary codes at every descendant. Their cost then scales with depth.
For those valid noncanonical representations use the exact history formula
above with their actual extents. A physical BLANK tail stops a copy; a coded
logical BLANK does not. The semantic induction and exact length-based invoices
remain valid, but the O((depth+1)N) corollary requires the stated entry bound.

The retained `warm_tail_boundary.py` diagnostic supplies two descriptors with B
extra coded blanks after RIGHT. Relative to the canonical representation, at
depth d>=1 the exact deltas are `6B` entry cells, `6B(d+2)` final backing cells,
and `180Bd` actions. Two descriptors contribute three bits per added symbol at
each of d+1 levels, and two staging relays retain one further copy. In each
boundary the inherited invoice adds `4(6B)+5(6B)=54B` and the new descriptor
staging adds `21(3B)+21(3B)=126B`. Their sum is180B per edge. Eight finite cases
check this identity without modifying the source program. This is a boundary
of the proposed corollary, not a counterexample to the selected theorem.

## Evidence and exact remaining work

Normal and optimized Python replay pass114 chain cases: p=5,9,17; M=1,2,4;
depths0,1,2,4; dirty ancestor prefixes0,17,257; plus15 repeated four-level
invocations on each prefix and depth31 at p9/M4 on all three prefixes.
All15 reuses have identical retained backing. The three prefix variants have
the same3,101,268 physical-action total, with retained cells4816,5105,9185,
respectively: only pre-existing prefix capacity changes. Six actual execution
mutations reject: false BLANK delimiter, destruction before output copy,
aliasing occupiedZ as empty return slot, corrupted resumed output, omitted
return-role retirement and a wrong physically restored phase bit. Every check
uses explicit exceptions, not optimization-disabled assertions. Normal and
optimized modes reproduce byte-identical RESULT/CONTROLS receipts.

Nine additional unequal-subjob cases suspend a prepared parent query and execute
a real query at different physically supplied p/M in the reused child segments:
parent(17,4)/child(5,1), parent(5,4)/child(17,2), and parent(9,4)/child(9,1), on
all three dirty-prefix lengths. The child result is copied completely to the
relay before pop and delivered to parent role8 after pop, while every prepared
parent byte/head, including the original Z and counters, is restored. The parent
then finishes its own full-sized query.
These deliberately do not install a smaller subjob output as the parent's
complete Z: production splitting/assembly must establish that semantic link.

These checks are not a production supplier or independent mathematical review.
To close the selected handoff, the following are still necessary:

1. Bind the actual selected compiled program's event/role/owner dispatch to a
   finite encoded continuation grammar. The present unary chain is a complete
   test grammar, not that program. Full compiled O/Q and simultaneous raw-unit
   classes cannot be replaced by the eight local ports or raw418 fields.
2. Bind actual complete-row child splitting and original-owner destination
   installation. This prototype preserves whole fields of unchanged M; it does
   not route the selected child shape or spectators itself.
3. Instantiate the retained child/chart/translation endpoint, locality and
   scratch contracts on these coded streams, or give a fully charged codec to
   its actual representation. The identity leaf is only a named boundary test.
4. Derive production local peaks and descriptor sizes, then apply PR5404's
   coordinatewise history formula and the selected compiler's lifetime proof.
   Include marker setup, staging, extra role8, all4 relays and warm entry K0.
5. Supply global numerical headroom and precision. The local checked addition
   cannot establish that assumption.

The positive result is that the seven-symbol/inner-blank/occupied-Z ABI seam is
constructively bridgeable with paid fixed-tape operations. It removes a concrete
representation obstruction, but it does not by itself close owned_erasure.
