# Binary head-distance continuation frames

New construction and proof produced by Nick Petalas. Apache-2.0.

## Statement and exact contract

Use Mihir Srivastava's PR #5364 local segment contract, retained at
`fd74da128f0e5ab702a8fe7b2b00e1a316bb22ad`. There are sixteen disjoint payload
tapes, a control tape, a descriptor tape and reverse scratch. The same nine
symbols suffice. Each parent payload is an arbitrary contiguous binary word
of length s_i after its local marker, with head at h_i in [0,s_i]. Let
H_i=s_i-h_i, H=sum H_i, L=sum bitlength(H_i) and P=sum popcount(H_i), with
bitlength(0)=0. A fixed sixteen-bit mask records presence. Absent roles are
empty, but a present role may be empty. The opaque binary descriptor has
length d and starts at its local beginning. Control is at its blank top;
scratch is blank at its local beginning. Ancestor prefixes are arbitrary and
inaccessible. Markers and tape identities are supplied entry conditions.

The new push/pop construction has exactly the predecessor's restoration
postcondition, for every finite properly nested successful call tree. Its
control frame has exactly

    d + 35 + L

symbols, instead of the predecessor's d+35+H. Scratch needs at most
max(d, max_i bitlength(H_i)) working symbols across a matched boundary.
Scratch is empty at every child entry and parent return. During nested
execution the same physical scratch tape is reused, so its historical extent
is the maximum over frames, not a sum over active frames. Parent payload
extents and their historical backing are unchanged by this result.
The scratch interval includes its marker and the terminal blank in addition
to the stated number of working symbols, so it has at most that maximum
plus two cells. Erasure does not deallocate any visited cell.

Let the seventeen child words, including its descriptor, have lengths t_j
and return head offsets g_j in [0,t_j]. Put W=sum t_j and G=sum g_j. Counting
each read, write and unit move separately, the complete matched boundary is
exactly

    22d + 24H - 10P + 22L + 613 + 2G + 5W.             (1)

It is therefore at most

    22d + 46H + 613 + 7W.                              (2)

The action bound includes all child and scratch erasure. Child computation,
descriptor production and designated output delivery have separate costs.
Intended output must be delivered before destructive pop, as in #5364.
There is a larger linear action constant in exchange for smaller headers.
This is a local constructive refinement, not a new whole-caller allocation,
binary compilation, supplier admission, exponent saving or multiplication
theorem. No global tape-reserve improvement follows without rebinding the
actual caller and accounting for all payload and historical extents.

## Binary counter with finite control

The counter is little endian on reverse scratch, immediately after its local
marker. It starts as an empty word representing zero. For each physical step
right while parking a payload head, increment it by changing the initial run
of ones to zeros and the next zero or blank to one, then rewind to the local
marker and step right. This stores the number of actual head movements;
no numeric payload offset, length or saved pointer is controller state.

If an increment crosses t trailing ones, its cost is 3t for their
read/write/move actions, two actions for the final read/write, and 2t+3
for rewind. Thus it costs 5t+5. Among the first h increments from zero,
the sum of trailing-one counts is

    sum_{a>=1} floor(h/2^a) = h-popcount(h).

The sum counts each carry across each bit position exactly once. Hence the
complete increment cost is 10h-5popcount(h). The counter never exceeds
bitlength(h) cells.

After parking, scan the counter to its terminal blank, then read it
backward. Emit each bit to control, most significant first, encoding zero
as `u` and one as `:`. Erase each counter bit as it is read, and return to
its local beginning. For ell counter bits, the forward scan costs 2ell+1,
the backward transfers cost 6ell, and the final marker return costs three.
The exact transfer cost is 8ell+4, including the empty counter.

The frame grammar is

    [ descriptor : b_0 B(H_0) ; ... b_15 B(H_15) ; ]

where B is the indicated most-significant-first encoding and B(0) is empty.
Positive encodings start with `:`. Presence flags use 0/1, disjoint from
count digits. Although `:` also terminates the descriptor, parsing is
unambiguous: fixed role order and each presence bit separate the contexts.
All thirty-five fixed symbols of the earlier grammar remain; H unary
symbols become L binary symbols. This proves the frame-length formula.

At pop, consume each role's count backward into scratch. The resulting
word is little endian and has the original fixed width ell. Consuming the
ell count digits costs 6ell, the next presence bit costs three, and rewind
costs 2ell+3. The presence bit is retained in finite control while returning
the corresponding payload head.

For decrement, change each initial zero to one and move right until a one
or terminal blank is read. If a one is found, replace it with zero and
rewind. This subtracts one in the unchanged fixed-width word. Starting
from a positive integer j, the initial zero-run length is its 2-adic
valuation. Its cost is 5v_2(j)+5. The h positive decrements therefore cost
10h-5popcount(h), by the same floor sum. Each successful decrement also
causes one physical payload step left and a read of that parent bit.

When the word is zero, all ell digits are temporarily changed to ones.
The terminal blank identifies this case. Walk backward, erasing those
ones, stop at the local marker and step right. Including the forward scan,
this final failed decrement costs exactly 6ell+4. It returns false with
scratch empty. There is no full-width zero test on every decrement; that
would introduce an unnecessary H log H action bound.

The code's only variable controller data are current symbols, a Boolean
decrement result, fixed role indices and the sixteen-bit mask. Count
arithmetic resides on tape. Helper call depth is fixed; all helpers can
be duplicated at their finitely many call sites. Mathematical nested-call
induction is not runtime recursion. The Python simulator's dictionaries,
integer heads and snapshots belong to the test machine, not the controller.

## Restoration and nesting

The descriptor transfer, its two reversals, local child cleanup and parent
suspension markers are the unchanged #5364 recipe. The new role loops
replace only recording and consuming the return distance. After j parking
steps the payload head is h_i+j and the counter represents j. The first
blank occurs at j=H_i. Thus the child marker is placed at the exact parent
end and the saved count is correct. Parent payload symbols are never written.

After child cleanup, erase that suspension marker. The payload head is now
at the parent end s_i. Each of H_i successful decrements moves it one cell
left. Its final position is exactly h_i, and each visited parent cell is
binary. The final failed decrement erases all counter cells. The saved
presence bit restores that role's mask bit, including occupied empty roles.

The unchanged descriptor return restores the original opaque word and its
head. Consuming `[` leaves control at the original blank top. All new
control and scratch cells are blank, and older control symbols are untouched.
This proves one matched pair. Induction on any finite properly nested call
tree proves the same assertion at every depth, since each inner matched
pair restores the complete entry state required by its parent's remainder.
No claim is made for malformed storage, failed children or unmatched calls.
Invalid calls need not be transactional.

## Derivation of the complete invoice

The inherited `emit` and `take` cost three actions. A local rewind from
offset x costs 2x+3. Clearing a child of length t from head g costs
2g+5t+7, including empty children and all delimiter/blank reads.

For one role, push costs presence emission three, payload scanning 2h+1,
increments 10h-5popcount(h), counter transfer 8ell+4, suspension-marker
write and movement two, and terminator emission three. Its total is
12h-5popcount(h)+8ell+13. The inherited descriptor/frame setup costs
8d+13, with one added initial scratch-blank read. Consequently

    push = 8d + 12H - 5P + 8L + 13*16 + 14.

For one role, pop costs six actions for its terminator and payload marker,
8ell+6 for loading its count and presence bit, 10h-5popcount(h) for the
positive decrements, 2h for payload return, and 6ell+4 for the final zero
cleanup. Its total is 12h-5popcount(h)+14ell+16. The inherited descriptor
and frame remainder is 14d+16, including the scratch-blank test. Hence

    pop = 14d + 12H - 5P + 14L + 16*16 + 16
          + sum_j (2g_j+5t_j+7),

where there are seventeen child segments. Adding the two formulas yields
(1). Since L<=H, P>=0 and G<=W, (2) follows for all nonnegative extents.
These are symbolic tape-action identities, not elapsed-time benchmarks.

## Verification and implementation boundaries

The new verifier executes the new controller on the pinned predecessor's
unit-action Tape simulator. It does not execute the predecessor's verifier
or census. Independently computed binary strings, complete nineteen-tape
snapshots and the displayed exact formulas are the oracles. A new controller
object is created before return. Finite cases corroborate the written
all-size proof; they are not a proof-kernel result.

All loops in the controller are bounded by the declared finite tape segments,
return distances, bit lengths or the fixed sixteen roles. In valid calls
these decrease to a delimiter or a zero count. In the bounded verifier,
payload lengths are at most 4097 in power-boundary cases and 4096 in its
sixteen-role illustration; depth is at most 31 and prefixes at most 4096.
The interpreter necessarily allocates managed Python objects; finite input
bounds limit that test allocation. The finite-control program uses only its
fixed tapes. The inherited simulator and helper implementation are unchanged.
No repository-wide diagnostics or allocation refactor is part of this result.
Dynamic imports are confined to authenticated, explicitly declared source
paths; the four negative controls temporarily replace two named functions
or damage one fixture symbol, and restore the original functions afterward.

The standard binary carry argument is classical. The new result is this
complete continuation-contract refinement, including the nine-symbol grammar,
shared scratch, explicit restoration and exact space/action tradeoff.
Mihir Srivastava retains #5364's contract, descriptor recipe and simulator;
Ali Romman retains #5356/#5368's related stack/output construction; zxv
retains #5404's complete historical-backing result. JoyboyBrian's segment
boundary, Jose Manuel's sequential primitives, Douglas Colkitt's guard/repair,
Cinna Davis's caller, Matarener's cover/stock and Sagar Thakrar's parent-return
lineage retain their predecessor credit. None is reverified as the deliverable.
