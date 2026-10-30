# Full-fiber low-type commit on a literal fixed-tape machine

## Actual consumer and precise closure boundary

The pinned PR4989 helper462/frame506 route writes a cover address as
`G=G0+qG1`, N=8f, D=N^2, with G0 in GL_N(F_q). After its emitted high linear
word and old-low carry shifts, `low_type_commit` changes the low label to
`G0 S mod q`, where S is the actual S8 tensor I_f, or its inverse. The inherited
interpreter updates this label with host matrix arithmetic. The physical
full-array representation is a contiguous bit stream indexed in order by

`(G0, G1[0], ..., G1[D-1], z)`

with low types in lexicographic row-major order, every high coordinate in
`[Q]`, Q=q^(w-1), and the complete remaining spectator tuple flattened into
`[Z]`. Thus T=|GL_N(F_q)|, H=Q^D Z and V=T H. All bits are arbitrary. There is
no tagged-record restriction and no sparse payload assumption.

This package implements exactly the missing low-type commit consumer, source
installation, and old-cache retirement. The unchanged high-coordinate and
carry suppliers are **named composition premises** below. No literal composed
machine for every high leaf, first-coordinate OLD repair, native call, P3 stock
or full selected supplier is claimed. This distinction is intentional: a
physical full-fiber consumer is a new result beyond descriptor preparation,
while a complete route would additionally need those actual supplier calls
and their caller binding. The low-commit machine is not merely an API join.

## Finite type compilation and layout binding

For an admitted odd prime q, the compiler reduces the rational source S modulo
q, checking all denominators are units and S invertible. It enumerates every
q^(N^2) matrix in lexicographic order and retains the invertible ones by modular
elimination. The ordered list L has exactly T elements. It computes
`pi(i)=index(L[i] S mod q)`; inverse direction uses S^-1. Right multiplication
is a bijection of GL, so pi is a permutation. `compile_types` performs exactly
this pre-input operation; it accepts no runtime width or payload.

The compiler also emits the canonical b-bit digits of every old low matrix,
b=ceil(log2 q), giving an owned old-cache stream of K=T D b bits. This is a
complete low-type cache layout; the old label is an enumerated finite control
case, not copied productive payload. Its allocation and initialization are
not free: the separate `compile_cache` program checks blank cells, writes and returns
the marked K-bit cache in at most 5K+16 transitions before any descriptor use. It remains live throughout all dependent
old-low descriptor reads and until the completed low-commit output is installed.
The commit stage consumes that correctly owned marked cache, checks every bit
against its compiler-known old value, and only then proceeds. This is an
explicit boundary: a caller with only one per-fiber cache must serialize that
layout conversion and pay K; it may not claim this machine accepts its old
single-cache ABI unchanged.

The instruction program unrolls pi^-1 as finite state control, with no runtime
permutation table lookup. Its length is O(T^2+K+D). A conservative pre-input
work envelope is O(q^D N^3 (log q)^3 + T^2 D log q + D) exact bit operations,
plus rational source reduction and inverse preparation. Schoolbook modular
elimination may be bounded more loosely by an additional log q factor without
changing the fixed-parameter conclusion. No GL8(Fq) enumeration is executed in
our bounded validation, and these enormous finite constants are not asserted
practical or already admitted by P3.

## Machine contract and generated fiber length

The seven-symbol instruction set, assembler, binary-to-unary macro and primary
interpreter are retained byte-for-byte from David Arias's PR2776 line. Every
runtime instruction is a single-symbol branch, single-cell write, unit move,
fixed jump, halt or reject. There are D+8 tapes: the owned source, blank output,
preserved canonical binary Q and Z descriptors, owned old cache, binary work,
fiber-length counter, D high-coordinate counters and one spectator counter.
All physical tape roles are distinct. Each has an independently supplied origin.
The source and cache have LEFT/RIGHT delimiters and initial head at first bit;
all private tapes start wholly blank at origin. Supplying blank ownership is a
premise, not inferred from inspection of one cell. Invalid-input rejection need
not roll back a partially written source.

The machine first initializes private left markers and validates all K old-cache
bits and its right endpoint, returning that head. It converts Q to each of D
unary counters and Z to one unary counter using the inherited paid converter.
Nested unit-counter loops emit one UNIT on the H tape for each tuple of high
coordinates and spectator value. There are exactly Q^D Z leaves. The program
then appends RIGHT and restores every loop counter and H head. No runtime
multiplication, exponentiation, random addressing or free extent table occurs.
The finite compiler emits the loop nests iteratively, so it has no recursive
Python-depth limitation in D. Q=1 is supported as a calibration boundary;
actual source routes have Q>=3. The proof covers all positive Q,Z and D>=1.

## Complete payload permutation, installation and cache lifetime

A segment loop advances the source head exactly H cells by consuming and
rewinding the unary H counter. A copy segment branches on every source bit,
writes that bit to the next output cell, and advances both heads. A skip segment
only validates and advances the source. The machine first scans all T source
segments and requires RIGHT at exactly V; this validates complete shape before
source mutation.

For output block k it rewinds the preserved source, skips pi^-1(k) segments,
and copies its next segment. Exactly one complete block goes to each output
position. Within each block every high coordinate and spectator position is
unchanged, so the push map is `(i,h,z)->(pi(i),h,z)` for arbitrary payload bits.
This is a sequential multipass construction. The potentially T-fold rescan
cost is charged, not hidden behind a gather primitive.

After output completion, source and output heads are returned. One sequential
pass overwrites each original source cell from output while erasing that output
cell. The source right marker is checked at the same length. The output RIGHT
and LEFT markers are erased and its head returns to its blank origin. The
source remains the same physical owner, with transformed contents and original
head. Only now is the old-cache region erased, including both markers, and its
head returned to its allocation origin. All unary counters and binary work are
also erased and returned. The Q,Z descriptors are unchanged byte-for-byte with
their original heads. No productive output or old cache is discarded before its
last read. Erasure of the old cache is legal because it is owned control data,
not an arbitrary borrowed stream.

## Explicit transition and visited-space bounds

Write K=TDb for the source-specific old cache, or any declared finite cache
length for the generic commit. One converter costs at most 44n transitions.
The D Q counters and Z therefore cost at most 44(DQ+Z), at most 44(D+1)H.
The nested emission loops and their rewinds cost at most 16(D+1)H: at each
level the sum of its iterations and rewind lengths is at most a constant times
H, because every prefix has at least one completion. Initialization and final
counter erasure add at most 16(D+1)H+32(D+1).

A segment costs at most 16H+8 including its H-counter rewind, whether copied
or skipped. Validation uses T segments. Gathering uses
`sum_k (pi^-1(k)+1)=T(T+1)/2` segments, plus T source rewinds, each at most
3V+3. Output/source installation, marker removal and returns cost at most
24V+24. Cache validation and return use 5K+4 transitions; erasure from its first
bit uses 7K+5, hence 12K+9 together. We allow 16K+16 independently
of payload volume, including arbitrarily long generic caches. With H>=1 and
V=TH, the following deliberately loose envelope covers all these instructions:

`transitions <= 128(T+D+1)V + 16K + 16 + 128D`.

The implemented separate cache initializer adds at most 5K+16. It visits
K+3 cache cells because it steps one cell beyond RIGHT before returning;
the commit alone visits K+2. The combined space envelope below absorbs that
extra cell. For fixed
N,q, both terms are O_(N,q)(V), since K=TDb<=Db V. This does not assert a small
constant or a whole supplier recurrence.

Source and output consume at most 2V+4 visited cells; the H counter consumes
H+2; the D Q counters and one Z counter consume at most (D+1)H
plus their markers. The two input descriptor lengths and the maximum binary
work length are each at most H, adding at most 3H and their markers. Old cache
consumes K+2. Thus the payload-dependent part is at most (D+7)V;
the following envelope leaves another V plus explicit marker/head slack. The conservative checked envelope is

`visited cells <= (D+8)V + 2K + 64(D+1)`.

It includes cells subsequently erased. Tape translations change no interval
length. Runtime width enters through Q and payload H, not program size.

## Composition with the actual carry route, without hiding unresolved leaves

Let the supplied high linear route map G1 to `G1 S mod Q` while preserving
old G0. For each of D cells the supplied descriptor/carry routine adds
`C=(G0 S_mod(qQ) - (G0 S_mod(qQ) mod q))/q mod Q`, calculated from the **old**
low cache. This is exactly the pinned PR4989 arithmetic. After all those
shifts, low commit moves the whole high/spectator block from G0 to G0S mod q.
The rebuilt address is therefore `(G0+qG1) S mod qQ`. Inverse source direction
uses the inverse matrix, its own old cache and its own carry values; it cannot
reuse forward descriptors. Thus composition is an all-input group permutation
under these explicit upstream primitive contracts.

The inherited frontend costs at most
`T D (64Db + 256 bit_length(Q) + 2048)` transitions for actual S8 tensor I_f.
With correctly isolated complete fibers, the inherited later-target shear
contributes at most 1024 D V. Translating high coordinate zero still requires
the two completed OLD swaps around its later-target shear, costing
`2 T A_OLD(H,w)` plus actual installations. Those OLD calls, isolation, complete
high-route leaves, descriptor construction for all extents, and their physical
caller integration are **not implemented by the low-commit machine** and are
not zero. Its new K cache and finite-state constants must also enter P3. The
full route cannot be declared physically admitted from this local result.

## Evidence and scope

The verifier executes both directions on **all 48 low types of GL2(F3)**, with
complete high/spectator payloads for Q=1 and Q=3, D=4, Z=1 or 2, translated
origins and arbitrary bit patterns. A separate exact local interpreter agrees
with the inherited machine on reduced complete cases. All eight bit inputs of
a three-block case are exhausted. Source-bound S8 forward/inverse modular
checks cover actual N=8 low inputs, q=3/5/7 and w=2/4; those are source-binding
checks, not executions of the astronomically large actual full GL8 array.
The written loop/ownership invariants, not finite extrapolation, give the all-Q
statement. Missing source bits, stale old cache, zero extent and nonpermutation
compiler inputs reject. No native, selected-frontier, Lean or Docker replay is
claimed. All predecessor mathematical and machine assumptions remain explicit.
