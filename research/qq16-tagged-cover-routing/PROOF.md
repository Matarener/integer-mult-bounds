# A constructive tagged-stream cover router

This is an informal mathematical proof with a cell-metered executable model.
The separate Lean theorem proves the algebraic inverse only. It does not
formalize the tape controller, its cost, or a complete multiplication supplier.

## Exact entry contract and theorem

Fix positive integers n, lambda and B, an invertible binary n-by-n matrix g,
and a binary column delta. Let D be any nonempty finite set of binary n-by-n
matrices closed under right multiplication by g and g inverse. No membership
oracle or enumeration of the ambient matrix space is supplied to the machine.
Put M = |D|, r = n lambda, N = 2^r, S = MN, d = n^2+r, and L = d+B+2.

Each record consists of d tag bits, a colon, B arbitrary payload bits, and a
semicolon. Tags encode the owner matrix column by column, with row bits in
increasing order, followed by lambda n-bit payload addresses. The stream has
one left fence ^ and one right fence $. Initially it contains exactly one
record for every (owner,address) in D times (F_2^n)^lambda, in lexicographic tag
order. Payload bits are unrestricted. The tagged layout is an explicit entry
hypothesis; an untagged caller is not silently converted for free.

The data tape and three work tapes have heads at their respective origins.
Each work window has C = SL+2 initially blank cells. Every tape exterior is
arbitrarily dirty. The fixed alphabet is {blank,0,1,^,$,:,;}.

Write h = g inverse, u = h delta, and

    q = n nnz(h) + r (1 + wt(u)).

There is a four-tape finite-control program, depending only on n, lambda, g
and delta, which genuinely halts, returns all heads to their origins, restores
all three work windows to blank, and leaves all tape exteriors unchanged.
Its data output has the original sorted tags and payload

    output(a,z_1,...,z_lambda)
      = input(a g, z_1 XOR a delta, ..., z_lambda XOR a delta).

Its transition count is at most

    T = S [(2d+2) q + (32d+32) L] + 64(d+1).

At most 4C tape cells are used, including the input window; the work requirement
is three clean windows, not the single global buffer posited in PR3270.
The program family is nonuniform in n, lambda, g and delta. The statement is
uniform in M, B and all valid payload values. It is not an all-size uniform
compiler theorem. In particular, no unpriced universal interpreter is assumed.

## 1. The correct push tag

For an input record (e,w), give its output record tag

    a = e h,                 z_j = w_j XOR e(h delta).

Then a g = e and z_j XOR a delta = w_j, by associativity and characteristic
two. This proves the desired pullback convention. Owners here are matrices:
replacing e by a 73-bit vector changes the source contract.

The Lean theorem `QQ16CoverRoute.semidirect_pull_push` verifies exactly this
identity, without assuming that e is invertible. The source finite inverse
checks are separate from that universal statement.

The push map is a bijection on the actual record set because D is right-closed.
It never pads to all 2^(n^2) matrices or treats one 512-coordinate local kernel
as a full cover. Arbitrary correlations between record payloads are harmless.

Each output owner bit is an XOR of input owner bits. Repeating the columns of h
for each of n rows uses n nnz(h) input-bit reads. The r address outputs each
read their old address bit and the wt(u) relevant owner-row bits. Hence q is
exact, including all owner-dependent translation terms.

## 2. Relabel with actual head moves

`Machine.relabel` copies input into the first work tape. For each output tag bit,
its fixed coefficient positions are visited from the current record origin and
returned from individually. A read at position p costs p outward moves, one
read, p return moves and one parity update, at most 2d+2 transitions. It is not
a constant-cost array lookup. The parity is one finite-control bit.

The output tag is then written, and the record payload is copied sequentially.
The controller scans to the semicolon; it never stores B or a payload word in
finite control. The non-parity work is bounded by 8L per record. Setup, the
right fence, and both origin returns give a total bound

    S [(2d+2)q + 12L] + 12.

The coefficient lists are compilation parameters. Their generation and the
source inverse calculation do not occur inside an input-dependent execution.
They define a fixed machine, rather than an unknown runtime oracle.

## 3. Stable binary partition and radix order

For one tag position j, inspect that bit and return to the same record origin.
Append the complete record to queue 0 or queue 1, using two forward-only work
tapes. Then rewind, concatenate queue 0 followed by queue 1 into the first work
tape, and clear each consumed queue cell. Equal-bit records retain their order.
The input and output lengths are equal even when one queue is empty.

Here is a conservative action bill for a single partition. Reads, writes,
finite parity updates and unit head moves are individually charged; moving two
heads counts twice.

| Part | Bound, excluding fixed fence overhead |
|---|---:|
| Inspect tags and copy all records into the two queues | 6SL |
| Rewind input and both queues, with marker reads | 4SL |
| Copy records back and clear consumed queue cells | 6SL |
| Return/clear queue left fences | 2SL |
| Return the working tape head | 2SL |

The fixed fence operations use fewer than 64 actions, so `32SL+64` bounds the
whole pass. The left fence of a queue is cleared only after it has been reached.
Clearing it earlier would invalidate the dirty-exterior/origin argument.

Perform stable partitions at positions d-1, d-2, ..., 0. Inductively, after
processing position j, the records are ordered by the suffix beginning at j.
Thus all tags are sorted at the end. This is a streaming construction of sorting;
it does not call a random-access sorting oracle. The incorrect forward-order
control is included in the executable checks.

## 4. Copy back, clean and halt

Copy the sorted stream back onto the data tape while blanking the consumed
working cells. Keep its left fence until the final return. Both heads return
in lockstep using the data tape's intact left fence, then the last working fence
is blanked. This costs at most `8SL+12` actions. The queues are already blank.
The output tags equal the initial tag set and order, by the bijection in part 1.

Combining the three bills gives

    S [(2d+2)q + (32d+20)L] + 64d + 24,

which is below the advertised bound. Every visited position belongs to its
reserved window: forward copies stop at the right fence, and rewinds stop at
an intact left fence. The only writes are in these windows. This proves the
arbitrary-dirty-exterior assertion, not merely a zero-exterior test case.

Every input-dependent loop is driven by a finite symbol and an end fence.
The finite tag-position loops and coefficient reads can be unrolled for the
fixed parameters. The remaining stored values are finitely many symbols and
one parity bit. Consequently this is an ordinary finite-control multitape
program; read/write/move instructions compile to literal transitions, and the
last control state has no outgoing transition. No payload array, unbounded
index, head reset or global arithmetic instruction is hidden in control.

A direct unrolling has O(dq+d^2) instruction sites, independent of M and B.
This is a fixed-machine description claim, not a billed uniform program-loader
implementation. Code ingestion/control storage in an admitted recursive caller
remains outside the present contract.

## 5. Reuse of the MathProof tape results

The construction uses the absolute-coordinate unit-move semantics already
present in `MultitapeAbsolute20261014`, with each read represented by a stationary
transition and each move by one unit. The public portable `Absolute` module
proves equality of its transition count with the head-relative machine model.

`MultitapeFrameRule20261014` supplies the precise finite-footprint principle:
completed runs transfer to arbitrary matching exteriors, retaining genuine
halting. Our marker argument supplies its footprint premise. The executable
meter also rejects every exterior access in its finite tests.

`MultitapeTapeEmbedding20261014Next` supplies `lift_runs`, `lift_halts` and
`preserves_extra`: a four-tape run embeds into a larger fixed tape bank at the
same time, with arbitrary spectator tapes unchanged. It justifies reusing three
work tapes while other field tapes remain idle. The caller must still provide
exclusive clean work windows and the tagged entry layout.

The shared DAG retrieves these canonical source declarations as SOURCE_ONLY;
that label is preserved. Their public portable proof versions were separately
kernel/audit checked in the PR2235 repair, under its own exact source manifest.
No new physical theorem is attributed to that old kernel receipt. PRECEDENTS.json
records the source hashes, statements used, public paths and evidence boundaries.

## 6. Independent tape origins, with no conversion claim

For any four integer origins a_i, supply the same local stream and work-window
contents at cells a_i through a_i+C-1, with head i initially at a_i. The identical
finite controller has the same cost, restores the work windows, returns head i
to a_i, and preserves every exterior. This is a useful placement corollary for
larger tape banks; the origins need not agree.

Proof: replace each cell function c_i(x) by c_i(x-a_i) and its head h_i by
h_i+a_i. The scanned symbol is unchanged. A unit move changes both heads by
the same ±1; a write changes exactly the translated cell. Induction on each
literal transition therefore conjugates the run, with the identical state and
exact time. The terminal table lookup is also unchanged, so genuine halt is
preserved. Window membership and exterior equality translate with the cells.
This is the `relocate_step`/`relocate_completed` symmetry found in the canonical
`MultitapeRelocation20261015` source; its current inspection evidence is recorded
separately from the three publicly hash-matched toolkit modules.

Both heads and the supplied tape contents are translated. The corollary does
not move an existing head to another entry window for free or prepare a layout.
No caller conversion or allocator has been added to the routing bill.

## Application to the literal B1 cover maps

The pinned joint-query certificate has 27,019 B1 events, 528 cover-map calls and
512 distinct map labels. All 512 right-action matrices g are invertible. For n = 73 and
lambda = 1, d = 5402. Separately represented matrix calculations reconstruct every
inverse and the sum of occurrence-weighted relabel reads, Q = 5,451,056.

Here W denotes the actual stored bit width of one real component, including
sign/format bits; no numerical-grid guard is silently identified with it.
With B = 2W and N = 2^73, summing the routing bounds and one control handoff per call
gives the following conditional per-owner bill for those 528 calls:

    N (182578176 W + 552230342688) + 182578704.

This is a safe per-owner upper bound: divide the total bill by M and use M ≥ 1
for its fixed overhead. Owner-set closure is a premise, not reconstructed from a
materialized list of all cover owners. This prices only the cover-map subsequence, assuming that each call receives
the tagged ABI and three clean work windows. It does not execute the other B1
events or establish that an admitted caller can allocate the layout. The common
four-tape footprint per call is `4 [M N (5402+2W+2)+2]` cells. Work buffers can
be reused serially, so they are not multiplied by 528. The tags and the two
extra buffers relative to PR3270 must not be dropped from an invoice.

This is a constructive sufficient physical reference contract. It is not a
favorable complete supplier budget or a new kappa. PR3339's owner/idle continuation,
entry conversion, arithmetic, retention, the F17 consumer and all-size compilation
remain distinct costs and obligations. A further implementation round must first
bind and price one actual caller, rather than treating those costs as zero.
