# Streamed leaf ownership at the installed caller-pool boundary

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
Apache-2.0. This is a source-relative successful-input lemma and a partial
construction, conditional on the explicitly cited predecessor contracts.

## Exact scope and premises

Pin the source bytes in SOURCES.json at main
`32890bc5de034ab8fc93ac88ead7279a6a416d04`. The relevant functions are
`r437-streaming-directory/streaming.py:visit,run`,
`selected-bit-physical-caller/scratch_pool.py:ScratchPool,Lease`, and
`selected-bit-physical-caller/macro_machine.py:Machine.commit,call,run`.
The generic fixture also executes the retained packet engine, leaf primitives
and XOR consumer. No predecessor source is changed.

Use #5055's complete successful-input contract: fixed compiled radix q and
dimension d, a valid q^w Context, C positive physical old-prefix occurrences of
h fields, sufficient supplied numerical arenas, and complete source and dirty
target fibres. Equal byte prefixes at different positions remain separate
occurrences. Let N=C*q^((w-1)d²), and let v be the complete local fibre bit count,
including spectators. The trace is a closed, nonrecursive, prefix-local leaf.
Its coefficient callback is synchronous, restores borrowed records and returns
owned numerical results. No callback, observer or event producer may retain a
lease, reenter the interval, alter allocation bindings or invoke a recursive
child. Arbitrary exceptions are outside the success theorem.

Inherit #5187's source lifetime premise: the completed local leaf/XOR consumer
needs at most A0=q²+136 simultaneous scratch roles, with its stated Program,
stack and Word extent bounds. This package does not independently prove that
whole source-call-graph bound or revalidate native/compiler correctness.

The caller supplies one already installed ScratchPool of capacity A>=q²+141,
with no live leases, and four ordinary physical tapes: full output, saved old
prefix, current prefix and reader counter. They have blank contiguous bodies,
blank tails and heads just after LEFT, and are disjoint from scratch, explicit
borrowed inputs and all other live owners. The adapter must be imported during
setup, before the pool installer changes module allocation bindings. These
requirements are part of the proposed new boundary, not assertions that an
unchanged production Machine already supplies them.

## Why the standalone boundary is insufficient

The original `Machine.run` keeps `self.pool.install()` active throughout root
loading and dispatch. It forbids physical Tape/Arena construction. In contrast,
#5187's Workspace allocates its full output by raw `Tape()` while inactive,
then installs a private pool only during each local consumer. Literal invocation
inside the canonical installer therefore rejects at full-output construction,
before any payload callback. The finite control records the original exception
and the two already allocated fibre/single Count leases. This is an expected
interface mismatch; #5187 explicitly leaves the caller join open and promises
no exception rollback.

Merely using the caller pool everywhere and retaining a per-prefix `empty()`
check would also be wrong. The streaming producer must keep five Count leases
alive during a callback. Finally, replacing all three persistent producer tapes
with ordinary ephemeral leases would invalidate the repeatedly cleared reader
counter. Its source `Counter.close` clears that same physical tape after each
old-prefix read. It must remain an owned persistent role until the producer ends.

## Construction and ownership invariant

`adapter.run_into` specializes the **unchanged code objects** of #5055's `run`
and `visit`. The first outer Tape allocation returns the supplied full-output
role. The two within-consumer direct allocations acquire scratch leases. The
three producer allocations return saved/current/reader roles, in their source
order. All other source allocation sites and default factories are handled by
the caller's existing installer. There is no nested installation and no new
physical Tape or Arena inside the interval.

The five persistent leases at each callback entry are:

| Owner | Value / purpose | End of lifetime |
|---|---|---|
| `run.fibre` | complete fibre cardinality v | run's final cleanup |
| `run.single` | one local prefix | run's final cleanup |
| `visit.expected` | complete prefix count N | returned to run and closed |
| `visit.emitted` | number already emitted | visit's final cleanup |
| `visit.outer` | remaining old occurrences | visit's final cleanup |

The copied `highs` Count has closed before this cut. The persistent reader is a
raw tape, and the odometer uses numerical Words, so neither contributes a sixth
lease. Direct inspection of `Count.product`, `Count.literal` and `Layout.fibre`
bounds setup by seven simultaneous leases; cleanup adds none. The q²+141 reserve
therefore covers setup as well as the at-most-five-plus-A0 consumer phase.

At prefix entry let S be the finite slot-to-lease identity map of those five
owners. At successful local exit require the live map to be exactly S, with the
same active objects, and all other physical scratch roles blank at their origins.
Equality of counts alone is insufficient: replacing a persistent owner with a
new lease at the same slot must reject. The verifier contains that control.

Each new local lease starts at a blank origin, uses the exact source tape
operations, and retires at its original last use. The producer roles are not
selected for scratch reuse. The source consumer only borrows the fibre/single
Counts and current prefix, restoring their bytes and heads. It does not access
expected/emitted/outer. Thus the finite identity guard agrees with a stronger
source invariant preserving the entire producer state. The verifier separately
compares every resident's bytes and head at all 243 local boundaries; the
runtime does not inspect their byte arrays.

Induction over the complete prefix order now gives exactly #5055's returned
payload, callback order within each prefix, and duplicate-prefix multiplicity.
The original source cleanup retires all five long-lived leases at macro exit.
The three producer tapes are blank, the pool is empty, and only the supplied
full-output tape remains nonblank. The source, target and old-directory bytes
and required heads are preserved by the inherited successful-input contract.

This argument is uniform in N and payload contents under the premises; the
finite fixture is corroboration, not a proof of source admission at all widths.

## Backing and costs that remain paid

Let I,L be index/residue Word bit widths, b the code width, P the largest
possibly extended Program body, and H the largest validated callback depth.
Set B=b+1+d²(L+1)+1 and

```
s = max(2I+4, L+3)
M = max(v, (h+1)B, P, (2H+3)s, I+3, L+3,
        bit_length(v)+3, bit_length(N)+3).
```

#5187 supplies the local consumer terms. The new `bit_length(N)+3` term covers
the producer Counts and product setup now resident in the shared pool: C and
the high cardinality are both at most N, and positive product prefixes never
exceed their final product. Normalization's extra blank/right edge is included.
For a fresh capacity-A pool its retained backing is at most A(M+2). Previously
allocated backing remains charged; adding entry backing is conservative.
The three raw producer tapes retain at most `(2h+1)B+I+7` cells, including
markers and conservative erased edge cells. These are sufficient bounds, not
optimal ones. The fixture has 1,289 pool cells after its first prefix and 1,290
after the last: constancy after the first prefix is not an invariant of this join.

The full output still retains Nv+2 cells. The full source and dirty target,
old directory, Program, geometry, numerical arenas, Context/codebook and any
suspended parents remain separate residents. The canonical destination and
any larger prior backing also remain charged. In particular the full output
does not become scratch of size v, and no full packet is discarded from the bill.

Let T be all record-cell traffic of the original standalone #5055 interval,
K the number of leases and J the number of temporary Callback.close calls.
Each acquire adds one read, and the inherited close adaptation adds at most
28J actions. A prefix boundary checks A-5 idle tapes, at two reads and two moves
each. Four entry role guards, three exit role guards and the final pool guard
give the conservative source-relative bound

```
T_join <= T + K + 28J + 4(A-5)N + 4A + 28.
```

This is an incremental pooling bound, not a closed all-parameter formula for T.
For the complete q3 fixture, the checker measures every created and borrowed
record tape in an additional unchanged-source execution and in the new
interval. It finds T=45,830,745 and T_join=46,233,805, attaining the bound
K+4(A-5)N+4A+28=403,060 with K=261,492, A=150, N=243 and J=0.
Both numerical arena traffic vectors agree exactly. This finite source invoice
does not replace the all-parameter obligation for T.
Finite role selection, guards and source-specific specialization retain the
predecessor's fixed compiled-control interpretation. Preparing A+4 blank roles
requires their LEFT writes and origin moves once; those are separate setup.
Existing physical traffic, copies, erasure and numerical Word actions remain.

The unchanged Machine constructor provides q²+128 scratch tapes. Applying this
sufficient reserve requires **13 additional scratch roles**, plus supplying the
three producer roles and full-output role. Their production allocation, parking
choice and terminal marker erasure have not been installed or priced globally.
No measured 32-lease peak is used to replace the sufficient reserve.

## Literal canonical commit and source retirement

The actual `Machine.commit` copies a raw result into its canonical destination
but clears the result only when it is a Lease. Hence this adapter's raw full
output must be explicitly cleared after commit. The fixture executes the
unchanged method with a minimal receiver containing the real destination tape;
it is not a full Machine.run or a simulated root/child execution.

For distinct tapes initially at their origins, a returned body of n bits and
a previous destination body of t bits, literal commit followed by source clear
uses exactly

```
reads  = 2t + 7n + 10
writes =  t + 2n
moves  = 2t + 6n + 14.
```

Indeed target.clear contributes `(2t+3,t,2t+4)`. append_tape contributes
`(4n+3,n,3n+4)`, target.rewind contributes `(n+1,0,n+2)`, and source.clear
contributes `(2n+3,n,2n+4)`. Summing proves the displayed identity, including
n=0 or t=0. All 289 pairs 0<=n,t<=16 are checked against the literal method.
Clearing either tape does not shrink retained backing. A subsequent empty-pool
guard costs another 4A actions; the full canonical boundary has other work.

## What this does not establish

No complete node, admitted root, recursive CALL/RETURN or full SOURCE87 payload
is executed. The original CALL is exercised only on a live-lease rejection path;
the entire canonical commit is executed. A source-specific dispatch must still
identify four available persistent roles, enlarge or independently tighten the
pool reserve, bind the producer/consumer schedule and source Program, and prove
parking/terminal ownership with every resident retained. Source traffic T,
Context/codebook setup, all-size numerical arenas, precision/stock, native and
compiler admission, and outer recovery remain separate. The #4067 added ADDs
and paid histogram are unchanged; #4147's coefficient is not rederived.
