# First hosted-query copy: a paid local tape step and the missing adapter

This closes one literal physical access/return obligation of PR4015 under an
explicit local window contract. It also identifies why the existing cover-router
and Gaussian-axis implementations do not supply that contract by composition.
It does not provide the actual global caller's windows or a complete native step.

## Exact source boundary

PR4015 head `0fff81d8997cef646538bcd4f60d7d455cf93b8e` has 3,813 events.
These are zero-based indices in that complete recovery word, not the outer
execution schedule. Its first streamed query uses port1, q=19, and work bank
Z10. The exact event slice is:

| Event | Operation |
|---|---|
|1697|CLEAR Z2 into the query2/F16 frame|
|1704|CLEAR Z10 into current/F17|
|1705|Z10 += W1|
|1706|stage2 port1 forward affine cover map on Z10|
|1707|negative rank-one line at q=19 on Z10|
|1708|Z2 += Z10|
|1709–1711|Z3 += Z10; Z5 -= Z10; Z9 -= Z10|

No event between1697 and1708 references Z2. Thus1708 is exactly the copy
Z2 := Z10, preserving Z10; it requires no read of the old Z2 value. Its source
and destination are both in F16 (axes9 through24) under the inherited full
phase proof. The original paid CLEAR1697 remains charged. Z2 becomes a live
query sum; it is not restored to zero or reinitialized by this optimization.
Later contributions still use ADD. The package authenticates the whole frozen
word and receipt, checks this intervening-reference census, and checks the
actual signed recipe. It does not rerun or claim a new proof of the full decoder.

## Explicit local tagged-window contract

Use the tagged record format stated by Dugongue/PR3394; this is a chosen
boundary hypothesis, not a claim that PR4015 already produces that format.
For positive integers n, lambda, M and stored component width W>=2, define

    S = M 2^(n lambda),  d = n^2+n lambda,
    L = d+2W+2,  C = SL+2,  H = C+gap,  gap>=0.

There are S records. Each has d tag bits, colon, W real-component bits,
W imaginary-component bits, and semicolon; left/right fences surround it.
Tags represent the same ordered owner/address set in both banks. Both
component fields use the same signed little-endian scale and width. The copy
is exact for arbitrary bits, so it needs no arithmetic range, divisibility or
carry premise. The source native call still needs its own signed-grid and
range proof; those premises have not been established here.

On one physical tape, Z10 occupies [a,a+C-1], Z2 occupies
[a+H,a+H+C-1], and the intervening gap is included in a traversable reserved
envelope. All five other tapes are arbitrary spectators. The only active head
starts at a. Z2 payload bits are zero by the logical source boundary. Both
banks have intact valid tags/fences; Z10 contains the completed event1707
result in the agreed encoding. Other content, including the gap, tags, and
exterior, is arbitrary subject to those format premises.

This supplies no buffer and does not claim that abstract reserved-family IDs
establish these physical windows. It is a conditional implementation of1708.
In particular, the fact that the tagged router returns its head to its origin
is insufficient to prove that a completed native1707 does the same.

## Literal controller and exact bill

Compile a fixed schedule for these parameters and offsets. No address lookup
or instantaneous head reset occurs. The controller has one payload-bit register.
For every payload offset x, in increasing record/bit order:

1. Move by unit steps to a+x and READ one bit.
2. Move by unit steps to a+H+x and WRITE that bit.

Finally move by unit steps back to a and halt. There are P=2SW payload bits.
The first offset is x0=d+2; the last is xlast=(S-1)L+d+2+2W-1.
All source positions precede all destination positions. Initial travel is x0;
each paired transfer costs H; between transfers the cost is
H-(xnext-xprevious); the last return costs H+xlast. Therefore

    MOVE = x0 + PH + (P-1)H - (xlast-x0) + H+xlast
         = 2PH+2(d+2).
    READ = P, WRITE = P,
    TOTAL = 2P(H+1)+2(d+2).

Every visit remains inside the supplied envelope. Reads occur only in source
payload cells; writes occur only in destination payload cells. Hence all tags,
source content, gap and exterior are unchanged. The final head is a, and the
five spectator tapes and heads are unchanged. Each destination bit equals its
matching source bit, so the full encoded value and F16 query state are correct.
No initialization or cleanup is omitted: CLEAR1697 is inherited and paid;
there is no scratch allocation or dirty helper to return; the head return is
included. Nonuniform schedule compilation/control description is explicit and
unpriced as an all-size program-loading obligation. Counted READ/WRITE/MOVE
cell actions are not the total time of an admitted uniform compiler.

The same paired-transfer protocol with a destination READ immediately before
each WRITE has identical movement and P additional reads. Source-proved zero
removes exactly **2SW READ actions**. This is a comparison to that explicitly
defined redundant-read protocol, not a claim of a general bit-adder tariff or
a change to PR4015's scalar allowance. The saving does not return in cleanup:
Z2 is intentionally retained as its query value.

For any other permutation of the same paired transfers, telescoping gives
2PH+2xfirst. Thus starting at the smallest payload offset minimizes motion
within this one-bit shuttle class. This does not optimize other layouts,
multiple heads, buffered/cached payloads, fused passes or general algorithms.
The bound is quadratic in S for this bank-major layout. Consequently this
literal implementation is a conservative reference and an unattractive
full-cover access choice, not evidence for a favorable complete supplier.

## The precise obstruction before this copy

PR3394's actual tagged-map exit has one payload tape, three blank work tapes,
all heads at their respective origins, and the original sorted tags/fences.
PR3884's entry requires two distinct untagged real/imaginary data tapes with
contiguous W-bit components, four owned discardable scratch tapes, and all
six heads at their individual entry origins. Its numerator divisibility and
signed range conditions are caller premises.

A direct composition already fails at the first symbol: the tagged tape's
origin contains `^`, not a two's-complement bit. Relocating the origin to its
first payload does not solve the problem. Real components have tagged stride
L=d+2W+2 but the bare real tape requires stride W. Translation changes an
origin, not a stride. For the actual n=73, lambda=1 and illustrative W=4,
d=5402 and L=5412. The first real component begins at5404. Its tagged successor
begins at10816, whereas a bare stream reads its successor at5408, the first
imaginary component. The fixture real1=0, imag0=1 witnesses a wrong read even
after the initial-origin issue is repaired. Moreover, one tape's interleaved
payload is not two independent data tapes: an injective spectator-tape
embedding cannot manufacture a second head on it. These are failures of the
verbatim predecessor ABI composition, not impossibility of a paid reformat.

There is also an independent algebraic trap. Event1707 uses the actual
negative q=19 recipe: both basis column lists are
[19,2,4,8,16,32,64,128,256] and its left offset is19. PR3884's bare coordinate
axis must not replace this entire native event. On input2*real_delta0, the
negative q19 line has nonzero coordinates0 and19; the negative axis0 line has
nonzero coordinates0 and1. W>=3 satisfies the witness's even-numerator and
signed-range conditions. The checker verifies all512 real basis columns of
the supplied positive-axis-plus-two-wrapper recipe. This is a local operator
witness; it does not supply the physical wrapper placement or the full cover.

ToikY/PR4002 supplies compensated canonical binary-lift phase tags. This
particular source recipe instead consists of explicit permutation wrappers
and a Gaussian rank-one child, with the negative affine offset already paid
symbolically. No K-to-J canonical-lift substitution is made here, so importing
those tags would not repair the tagged/raw storage mismatch. A future changed
native implementation must rebind its own phases and physical costs.

It follows that adding PR3394's map tariff, PR3884's 32NW axis tariff, and this
copy tariff is **not** a completed1706→1707→1708 implementation. A specific
producer/adapter must first supply the untagged layout, distinct data heads,
four owned scratch windows, actual signed grid, both native wrappers, and a
returned common tagged representation/head for the accumulation. None is
charged zero. PR2722/2794's scalar word-address movement models also do not
supply this bit-layout conversion.

## Evidence, decision and open next questions

The checker imports no predecessor executable. It authenticates retained
head/blob/SHA data and text before use, checks the full source slice and zero
lifetime, meters every bit action in translated dirty-exterior fixtures,
compares the complete typed receipt, and rejects wrong offset, missing return,
source/tag overwrite and an intervening query use. Boundary tests cover source,
manifest and typed-receipt changes and normal/optimized read-only Git-free use.
Finite fixtures corroborate the general telescoping/footprint argument.

Decision: close this exact copy protocol and stop the direct old-tariff
composition. The next useful step is a caller-owned layout adapter around the
actual q19 signed recipe, with head endpoints and width supplied by the caller;
repeating unbound sweep optimizations does not close that gap. The remainder
of the decoder, output ownership, physical allocation, numerical error,
productive-family coverage and both recursive suppliers remain open. No new
kappa, general tape lower bound, formal-kernel or human review is claimed.

Credit PR4015's streaming/output-bank work; ywz65/PR2707 and Arham Tahir/PR2681
for the native/full-recovery source; Ali Romman's QQ16 lineage; Dugongue/PR3394
for tagged matrix-owner routing; Clear1nsight/PR3884 for the signed-bit axis;
Nick Petalas/PR2722 and Arham Tahir/PR2794 for distinct fixed-address methods;
and ToikY/PR4002 for the separately scoped phase-tag handoff. New analysis and
checker by Chris R / Clear1nsight with substantial OpenAI Codex assistance.
Apache-2.0. No predecessor execution or scientific admission is implied by
retaining its proof text and recipe data.
