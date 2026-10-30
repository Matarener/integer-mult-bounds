# One counter for two coordinate phases

Scoped constructive proof, produced by Nick Petalas. Apache-2.0.

## Contract

There are exactly five positive coordinate cardinalities q_i. Their immutable
canonical descriptors store q_i-1, least significant bit first, between `^` and
`$`. A singleton has an empty descriptor. Write

```text
L_i = bit_length(q_i-1), R_i = 2^L_i,
D = sum_i L_i, N = product_i R_i, M = product_i q_i.
```

Each coordinate has one separate work tape with L_i owned zero bits between
markers. All descriptor/work heads start at their first bit, or at `$` when
empty. There is a separate immutable input tape and a fresh owned output tape.
Their heads also start at the first data position. The input is the M-bit
genuine rectangle for padding, or an arbitrary N-bit padded rectangle for
restriction. The output has adequate owned space. Origins may differ by any
integer. Cells outside the delimited/owned intervals are protected.

The alphabet is `{0,1,^,$,_}`. Operations read one symbol, write one symbol or
move one head by one cell. Finite-control state stores the five phase bits and
fixed program state. The metered reference also charges one `emit` action per
row and one `advance` action per visited coordinate. Testing five flags is one
fixed finite-control transition, independent of widths. There is no decoded
cardinality, width, coordinate, address, or unit-cost arithmetic in the machine.

On successful return the output is lexicographic zero padding, or restriction
to the genuine subrectangle. Input and descriptors retain every byte, all
twelve heads return, and all D counter bits are zero. Output is retained.
This is a well-formed successful-entry contract, not an adversarial parser or
failure-restoration theorem.

## Coordinate construction

Suppress the coordinate subscript. The unchanged descriptor is the L-bit word
for q-1. Its bitwise complement is exactly

```text
(2^L-1)-(q-1) = R-q = B.
```

This is a fixed-width identity, including L=0. `load` obtains that complement
in one sequential pass and remembers only whether any copied bit was one.
It restores both heads. No descriptor for B is retained.

Initialize the counter to q-1 and the phase to genuine. At coordinate position
x the invariant is

```text
0 <= x < q:    phase = genuine, counter = q-1-x;
q <= x < R:   phase = padding, counter = R-1-x.
```

`borrow` subtracts one modulo 2^L and reports underflow. In either phase a
positive counter decrements without a carry to the next coordinate.
At the last genuine position it underflows. Load B by complementing the
descriptor. If B is nonzero, subtract one once, enter the padding phase, and
report no coordinate carry. The next position is x=q and its counter is
B-1=R-1-q, as required. That preparatory subtraction cannot underflow.

If B is zero, there is no padding position. Reload q-1, remain genuine,
and report a coordinate carry immediately. At the last padding position,
underflow likewise reloads q-1, resets the genuine phase, and reports a carry.
These exhaust the cases and prove the invariant and reset for every q>=1.
For q=1, L=0, the first subtraction underflows on `$`, the complement is
empty/zero, and the coordinate carries after its one genuine position.
For q=R, the complement is all zero and no spurious padding position is emitted.

## Rectangle, ownership and termination

The last coordinate advances fastest. Its carry advances the preceding one,
and so on. The invariant shows that each coordinate makes exactly R_i visits
per cycle and resets. Induction over this fixed five-level odometer gives
exactly N visits in lexicographic padded order, then one outer carry.
A visit is genuine precisely when all five phase bits say genuine, equivalently
when every coordinate is less than q_i. Thus genuine visits appear in the
original lexicographic order. Padding reads its next source bit exactly there
and writes zero elsewhere. Restriction reads every input bit and writes its
next output bit exactly at genuine visits. Arbitrary padded bits are discarded.

All work writes target the five counter tapes. Descriptor and input tapes are
read-only. `borrow`, `load`, and `clear` restore their starting heads by scanning
to `^`; no head jump is free. After the outer carry all counters contain their
initial q_i-1 and all phases are genuine. Clearing the same five intervals
returns D zeros. Both payload heads rewind over their used intervals. Marker
positions, protected cells and the immutable tapes are fixed. The argument is
unchanged by translated origins and permits immediate reuse of the zero work.

Every marker loop traverses at most L_i+1 cells per forward pass and L_i+1
on rewind. Every countdown phase has at most R_i visits. The outer payload
loop has exactly N visits. These are encoded finite bounds from the entry
contract; the machine does not decode them into host integers.

## Uniform complete action bound

We count literal reads, writes, unit moves and the explicit finite-control
charges described above. Constructor/counter initialization and final cleanup
are included. Descriptor construction and physical allocation are external.

A load, with either polarity, costs exactly 8L+8 actions. It uses L+1 descriptor
reads, one counter-end read, L writes, 2L forward moves, then two rewinds,
each with L+1 reads and L+2 moves. Clearing costs 5L+4 actions.

If a decrement reaches j zero bits before a one, it costs 5(j+1) actions.
Underflow at zero costs 5L+4, at most 5(L+1). For positive integers 1 through m,
the total number of visited bits is

```text
sum_(v=1)^m (1+nu_2(v))
  = m + sum_(j>=1) floor(m/2^j) <= 2m.
```

In one complete coordinate cycle, genuine-phase subtractions run through
q-1,...,0. If B>0, the padding initialization and its later subtractions run
through B,...,0. Their combined visits are at most

```text
2(q-1)+(L+1) + 2B+(L+1) = 2R+2L.
```

If B=0 the genuine subtractions alone obey the same upper bound. With two
loads per cycle, all coordinate work after initialization costs at most
10R+26L+16. For L>=1, L<=R/2 and R>=2, so this is at most 31R. For L=0,
the literal empty-counter cycle costs 20=20R. Hence 32R bounds every case.

Coordinate i completes N/(R_i times the product of its inner R_j) cycles,
at most N/R_i. All five coordinates therefore cost at most 160N actions.
Padding or restriction payload traffic, including both rewinds and endpoint
checks, is 4M+4N+8 <= 8N+8. There are N emit and at most 5N advance charges.
Initialization and final clearing cost 13D+60. The total is consequently

```text
<= 174N+13D+68 <= 192N+16D+80.
```

No measured timing enters this bound. The constant is sufficient, not optimal.
The proof is uniform in the five positive cardinalities.

## Resource comparison and scientific scope

The new machine uses five descriptor tapes, five counter tapes and two payload
tapes, for twelve distinct tapes. Its mutable counter contents occupy D cells,
plus ten fixed counter delimiters. The cited PR2636 interface uses five
descriptor tapes, ten counter tapes and two payload tapes, with 2D counter cells
and twenty counter delimiters. It gives a 1024N+128D+128 sufficient bound.
Those predecessor resources are cited from its written contract, not recomputed
or audited. The contribution is the new two-phase sharing construction and the
proof above. No minimum-tape or optimal-action claim is made.

The scan remains a component. It requires canonical aggregate descriptors,
owned zero work and fresh output. It does not produce these resources, execute
the completed fast exchange, park ancestors, join a selected recursive caller,
or supply a complete precision/stock/tape invoice. It does not discharge a
selected framework assumption, change the selected frontier or claim a new
kappa or a complete integer-multiplication theorem.

## Executable evidence and code limits

The independent oracle enumerates mixed-radix coordinates with host arithmetic;
it imports no predecessor implementation. The machine reference reads only
its tape API. The verifier checks 516 full scans, 1300 additional exhaustive
payload scans, and 257 complete coordinate cycles. Thirteen controls cover
short/long/nonbinary input, wrong coordinate count/phase, counter/descriptor
symbols and width, immutable writes, nonunit moves, resource exhaustion,
a wrong complement, and omitted cleanup. Counts are generated by the checker.
Normal and optimized modes retain every check.

Python's object allocation, integer instrument counters and fixture arrays are
reference-model deviations from allocation-free operation. The claimed tape
machine owns only the intervals specified above. Verification is bounded by
258 fixed shapes of maximum padded volume 1024, exhaustive payload lengths
at most nine, and q<=257 in the coordinate oracle. Each metered run has an
explicit action cap. The call graph is nonrecursive and functions have fewer
than 60 physical lines. The tape dispatch and metering callback have fixed
local targets. Mutation controls temporarily replace two local functions and
restore them in `finally`. Dynamic import loads only the new local machine.
Warning-strict normal/optimized replay and syntax/function-size checks are the
available diagnostics. A compiled finite-state transition table, proof-kernel
check and independent human review are unclaimed.
