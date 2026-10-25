# Actual whole-array cell0 carry without the two OLD adapters

## 1. Exact source and changed premise

The pinned helper462/frame506 matcher is S8, lifted as A=S8 tensor I_f,
N=8f, D=N², q an odd prime, w>=2, Q=q^(w-1), b=ceil(log2 q).
Exact rational inspection gives

    S8[:,0]=2e5,       S8^-1[:,0]=e4,
    A[:,0]=2e_(5f),    A^-1[:,0]=e_(4f).

Consequently, in row0, the forward new low cell0 is 2u mod q and its
high carry is floor(2u/q) in {0,1}, u=G0[0,5f]. The inverse low cell0 is
v=G0[0,4f] and its carry is zero. These statements hold for every low matrix,
hence every invertible G0 and every lane count f. No rational-quarter case
occurs in this column. The independent source check computes S8^-1 and checks
the columns; the tensor identity is the all-f proof. Inverse here means the
actual inverse LOW factor; it is not the inverse of the isolated forward carry
layer without that factor's other high operations.

PR3343 already implements bounded signed one-axis rotation by encoded splits
and two monotone buckets, with a paid source-level O(BQS+I) proof. We reuse that
geometry and credit it. A proposed new arbitrary-offset primitive was withdrawn:
this actual column never has an unbounded carry. The missing task in PR5332
and PR5487 is the physical source-to-consumer join. This package supplies a
literal whole-T array controller, not a new rotation algorithm.

## 2. Whole-T contract

Let T be a positive runtime count, d a fixed positive compile-time fiber depth,
Z a positive runtime spectator extent, S=Q^(d-1)Z, H=QS, V=TH. The compiler
parameters are q,f,d and direction; default d=D. Its input banks are:

- one marked Boolean payload in lexicographic [T]×[Q]^d×[Z] order, length V;
- one marked old-low cache, T successive row-major N×N low matrices, each digit
  encoded in exactly b LSB-first bits, total TDb bits;
- canonical marked positive binary T,Q,Z descriptors;
- distinct owned blank work banks and a blank low0-output bank.

All input heads start at their first data cell. Marks use the retained literal
machine alphabet. The actual application sets d=D, T=|GL_N(F_q)|, Q=q^(w-1),
and takes the existing complete cache in the same low-type order as its payload.
It does not require per-fiber markers, supplied S/H counts, a free transpose,
a callback, a free gather, a type lookup or an OLD oracle. Each cache record
need only be correctly paired with its payload fiber; GL enumeration is not
performed by the running machine. GL membership is a source premise, not a
validation claim. The generic contract also permits other positive Q and d;
reduced fixtures using it are labelled and do not materialize GL8 payloads.

The result in the **same original payload owner** is

    out[t,(x+C_t mod Q),z] = in[t,x,z],   0<=z<S,

where C_t is selected from that fiber's actual old cache as in Section1.
The complete old cache and T,Q,Z descriptors are unchanged and their heads
restored. A distinct marked owned tape retains the T low0 output digits in
order, with its head restored; these are available to a later full low commit.
Every private cell, including fiber markers, counters and the global output,
is erased and its head returns to its original blank origin. Unused banks are
untouched. The claim assumes sufficient disjoint owned backing; it bounds all
visited cells but does not prove a global recursive allocator.

## 3. Literal construction and induction

The program has 17+d tapes and seven symbols, independent of runtime T,Q,Z.
Each instruction is a local symbol branch/write, unit head move, fixed jump,
halt or reject. Pre-input Python assembly resolves labels and finite q-dependent
branches using iterative pre-input loop assembly (no Python recursion-depth
limit); the running program has no integer addressing or host arithmetic.
The authenticated PR2776 counter/shear macros are executed directly as emitted
instructions, not invoked as unpriced runtime functions.

First convert T,Z and d-1 copies of Q to unary using the retained paid binary
converter. Nested counter loops append exactly Q^(d-1)Z marks to S_COUNT.
At depth i the counter prefix has visited exactly its lexicographic product;
the innermost Z loop appends one mark per tuple. This proves the suffix count
without a supplied product descriptor. Every reset is a literal backward walk.

For each of the T fibers, the outer unary counter drives these steps:

1. Install private markers and convert Q to a fresh unary left length. Copy
   exactly Q complete S-bit records from the advancing global source to a local
   bank. Write its endpoint and rewind it. This pays for creating the only local
   fiber markers; the global source has no internal marks.
2. Read the selected b old-cache bits at fixed offset (5f)b forward or (4f)b
   inverse. A finite decoder rejects that digit if it is >=q, writes its new-low
   result to the advancing low0-output bank, and chooses the C=0/1 branch.
   Every branch then advances to the next cache record, paying exactly the
   fixed record traversal. It neither changes nor retires the old cache.
3. Start split lengths (Q,0). For C=1 one literal transfer gives (Q-1,1).
   Split the local bank into its first (Q-C)S and last CS bits. Emit the latter
   then the former into a separate local output, consuming the buckets. This
   is precisely the bounded PR3343 geometry, implemented by PR2776 microcode.
   For C=0 it still makes and accounts for distinct local output.
4. Copy the complete local output to the advancing global output bank. Erase
   all local banks, their markers and both split lengths. Advance the type
   counter. Global source/cache positions now begin the next paired fiber.

The loop invariant is: the first t output fibers have the stated permutation,
the first t low0 digits have been emitted, global source/cache heads have moved
by tH and tDb, all earlier private fibers are blank, and old cache/source bytes
are unchanged. Each step preserves it. At t=T the code checks the two global
input endpoints, closes and rewinds the output, cache and low0 result, rewinds
the original source, then overwrites that same source by a sequential consuming
copy of the global output. It erases the global output including its marker,
restores the source head, and erases all persistent counters. The final owner
identity is unchanged; no later owner swap or disposal is left implicit.

`initialize_actual_T` supplies an optional literal initializer for the actual
fixed T=product_(i=0)^(N-1)(q^N-q^i). It writes that compiled constant into a
blank descriptor using <=4 bit_length(T)+6 transitions and then returns the
head. Since bit_length(T)<=Db, its cost is <=4Db+6. It enumerates no matrices.
Its one tape can be mapped to the controller's T input. If the caller already
owns that descriptor, initialization is not repeated.

## 4. Complete conservative tariffs

Let d>=1, V=TQ^d Z, and K=TDb. For the literal table, including descriptor
conversion/product construction, every full-array pass, staging, installation,
rewind and private erasure, the following intentionally loose bounds hold:

    transitions <= 2048(d+1)V + 32K + 256(d+1),
    visited cells <= (d+20)V + 2K + 128(d+1).

These are not measured-fit constants. Here is a sufficient path-count ledger.
The retained converter costs c(n)=24n-7 popcount(n)+15 bit_length(n)+12<=44n.
A retained S-bit record copy costs at most 12S+4; its unary length loop and
rewind add at most 6k+7 to k records, so one segment costs <=22kS+7 for k>0,
and <=7 when k=0. Every rewind of a marked tape at relative position h is
3h transitions. Backward erasure through the origin costs <=4(h+1).

- All initial unary conversions and the nested suffix construction fit
  256(d+1)V. Each of at most d nesting levels traverses at most the final S
  tuples plus its Q or Z counter extents; Q,Z,T,S<=V. Initial markers and
  conversions are included.
- Within a fiber, staging and the split/merge together use five segments,
  totalling at most 66H+35. Consuming append uses 6H+1. All local resets,
  markers, Q conversion, length transfer and erasures bring the total below
  512H, with small constant work absorbed using H>=1. This includes private
  bucket regions even though their symbols have already been consumed.
- The digit decoder and fixed-stride movement cost <=8Db+16 per record;
  the final whole-cache and low-result rewinds together cost <=4K+8. With
  T<=V their aggregate is bounded by 16K+32V+16.
- Final whole-owner installation/erasure and head returns cost <=32V+16.
  Persistent counter cleanup fits 64(d+1)V+64(d+1).

Adding these bounds is below the displayed transition allowance. The optional
actual-T initializer adds <=4Db+6 separately, or may be absorbed by unused
slack in 32K. No data-dependent host step is omitted from these paths.

For space, the global source/output consume 2V, and local source/output/buckets
at most 4H. Across different fibers the separate bucket maxima can sum to H+S, so their
visited regions are not bounded by a single live H. The suffix counter has S cells; Q-loop counters have (d-1)Q,
the split counters at most Q+1, type/Z counters T+Z, conversion scratch at
most max(log2 T,log2 Q,log2 Z)+1, and descriptor widths at most T+Q+Z.
The old cache and retained low0 result total K+Tb<=2K. Markers, endpoints,
visited erased tails and the fixed extra cells fit 128(d+1). These pieces fit
(d+20)V+2K+128(d+1); erased cells remain charged. The same upper bound absorbs
actual-T initialization. No numerical work word or recursive child is used.

Pre-input table size is O(qDb+d), including explicit cache strides per decoded
value, and is independent of T,Q,Z,w. This is a nonzero q,f-dependent compiler
cost. Default depth D can be generated without enumerating GL_N(q).

## 5. Source invoice and exact boundary

PR5332's first0 adapter was two completed OLD swaps around the later-target
c=0 shear, with real installation/transport. On T fibers its conditional bill
was 2T A_OLD(H,w)+A_later0+M_adapter. The new whole-array cell0 layer has no
OLD invocations and the explicit A_join above, so under the same source/cache
ordering contract the replacement difference is

    Delta = A_join - (2T A_OLD(H,w)+A_later0+M_adapter).

This signed equation does not assert Delta<0 for every tariff or size. It
removes two OLD dependencies per fiber from this added repair; it is not a
change to the selected primitive's recursive child profile. No selected
receipt is repriced. If a downstream caller expands these OLDs into recursive
paid calls, it must recompute its **entire signed invoice** with A_join and its
real allocation/preparation costs before claiming any saving or new kappa.

All other high linear movement, other coordinate carries, complete low-type
commit/cache retirement, caller allocation/backing, native refinement and P3
remain outside this package. Existing correctly paired full old-cache bytes are
input, not freely generated here. This contribution closes the contiguous-T
cell0 layer including its local fiber boundaries and final installation; it
does not claim the complete LOW route or supplier.

## Evidence and remaining questions

Forty full-array fixtures run in two independent interpreters; arbitrary bits,
complete small basis inputs, several T fibers, nonzero spectators, actual
q5/w4 carry1 selection, inverse selection and f2 strides are included. Depth64
and256 table controls use Q1 and are explicitly not actual odd-q GL payload
replays. No full GL8 or Q^64 array is materialized. The all-size result rests
on the loop invariants and tariff proof above, not these reduced tests.
Source corruption, wrong result writes, wrong selector direction, occupied
workspace and trailing cache controls reject in normal and optimized modes.

Next: link the remaining high/carry/low-commit layers in source order with their
complete signed invoice and actual backing reserve. Repeating rotation or
bounded-carry arithmetic is unnecessary. A selected-stage gain requires that
larger caller proof, not this component's zero OLD count.

Credit Tekalign/PR3343 and Jose Manuel/PR2915 for bounded carry geometry;
David Arias/PR2776 for literal machine/counter macros; PR5332/5487 for source
carry and low-commit boundaries; retained BIT/ROW lineage. Loader follows the
authenticated PR5019 loading pattern. Prepared by JoyboyBrian with substantial
OpenAI Codex assistance. Apache-2.0. No independent human/formal acceptance.
