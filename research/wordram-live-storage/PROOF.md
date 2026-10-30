# Address reuse preserves the complete forward program

## Hypotheses checked by the transformation

Let P be a finite direct-address 64-bit Word RAM program. Its body uses only
`one`, `add`, `sub`, `mul` and `bltz`. Every branch goes forward to a body
instruction. A straight-line suffix zeros each logical temporary once, then
zeros each scratch cell except the distinguished zero cell, then accepts.
The suffix is matched byte for byte as an instruction list.

For a logical temporary t, let f(t) be its first body write and l(t) its last
body read or write. Every t has a first write. Every semantically required
read of t follows that first write strictly. The reads of `sub d a a` are
empty because its result is zero for every a, including arbitrary incoming
dirt. All other arithmetic operands and branch conditions are required reads.
No branch skips any first write: for each branch at i to j, no f(t) satisfies
i < f(t) < j. The scanner checks these conditions before allocation.

Assign each temporary t a physical cell m(t), chosen from the original
temporary address set, disjoint from every input, output and scratch cell.
Require m(t) != m(u) whenever the closed intervals [f(t),l(t)] and
[f(u),l(u)] intersect. Rewrite each temporary address operand using m;
leave every other address and every branch label unchanged. The source has
no indirect accesses, so address renaming cannot change an address computed
at runtime.

## Simulation in the body

Consider any incoming memory for the compact program. Give the original
program the same incoming values in all non-temporary cells. Incoming logical
temporary values can be arbitrary and need not equal their physical cells.
The initialization condition makes those values irrelevant to required reads.

All first writes execute. A forward path could skip one only by a branch
jumping across it, which the checked condition forbids. Both programs start
at index zero. Induct on their executed instructions. At each reached index,
the programs agree in every non-temporary cell and in the represented value
of every initialized temporary whose interval has not ended.

A required temporary read lies in its own interval and therefore uses a cell
distinct from every other simultaneously relevant temporary. Its physical
value equals the original logical value. Non-temporary operands also agree.
Thus the arithmetic result or branch condition agrees. A zeroing subtraction
has the same result without needing equality of its two equal-address inputs.
At the first write of a new interval, its cell can hold irrelevant previous
dirt, but the result does not depend on that dirt. No write to its physical
cell can destroy another relevant temporary, because their intervals would
intersect at that index. The invariant is preserved.

Consequently, both executions take the same branches and have identical
opcodes and instruction counts through the body. The proof works modulo
2^64 and covers the ISA's signed branch interpretation, since the condition
word is identical. Strictly forward control bounds execution by the number
of static instructions; no termination premise about the operands is needed.

## Cleanup and exterior memory

On entry to the suffix, no temporary has any remaining body use. Each mapped
instruction `sub m(t) m(t) m(t)` sets its cell to zero. Repeated zeroings are
harmless. Every cell in the image of m occurs at least once, so all compact
temporaries finish zero. Scratch cleanup and outputs agree with the original
program because their addresses have not changed and their incoming suffix
values agree. The unchanged zero scratch cell inherits its original contract.

The only compact destinations are the mapped temporary cells and original
non-temporary destinations. In the pinned multiplier, the latter are scratch
and output cells. Therefore the input cells and every other address retain
their incoming values. This includes each original temporary address that is
outside the smaller image of m. Arbitrary exterior memory and arbitrary initial
owned dirt are allowed. The compact routine owns a smaller arena; it does not
promise to zero the abandoned addresses of the original ABI.

## Allocation size and the source-bound result

Sort the intervals by start. Retire an active interval only when its end is
strictly before the next start. Reuse a retired slot if one exists; otherwise
allocate one new slot. This gives a valid coloring of the closed intervals.
Whenever a new slot is needed, every earlier slot is active, so that many
intervals overlap at the new start. Hence the number of slots equals the
maximum overlap. Any allocation obeying these same closed-interval rules
needs at least that many cells. A separate difference-event sweep computes
the maximum and an index attaining it.

For David Ganz's pinned balanced 256-by-256 hexadecimal-digit multiplier,
the scanner covers all 507,701 instructions, 17,920 logical temporary
intervals and the exact cleanup suffix. The generated allocation uses 1,282
cells. Its overlap witness is index 140274. The compact program's canonical
instruction encoding has SHA256
`fcf6d3a599ff7c79d939c6c591423888eaca21cc935a810054719ee9b01ce6de`.
Every one of these counts is regenerated from the pinned source.

The simulation proves preservation for every incoming memory. Applying
PR #5466's original bounded multiplication theorem therefore gives a
multiplier for every admitted operand pair, with 16,638 fewer temporary
words, the same 20 scratch words and 513 output words, and the same dynamic
instruction count on each input. We do not re-prove the inherited NTT,
modular arithmetic, carry or integer-recovery theorem. There is no new
asymptotic exponent or unrestricted storage optimality conclusion.

## Implementation bounds

The new compiler rejects more than 1,000,000 instructions or 20,000
temporaries. Its loops scan bounded instruction, operand, interval and event
collections; the heap retirement loop has at most one removal per interval
over the whole allocation. No recursion is used. Functions are below 60
physical lines. Contracts use explicit exceptions and remain enabled under
optimized Python. Captured predecessor source is compiled only after its
SHA256 pins pass, without consulting bytecode caches.

Managed Python allocation is a deviation from fixed-memory execution for
the offline compiler and verifier. Their live collections are bounded by
the instruction and temporary capacities and the nine fixed test fixtures.
The emitted runtime program introduces no allocation instruction or indirect
dispatch. The authenticated source loader's dynamic module construction is
limited to three named, pinned modules. The original source's implementation
and its proof obligations remain inherited rather than rewritten here.
