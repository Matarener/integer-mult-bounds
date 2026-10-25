# Multi-target composition at the current CRT row boundary

This is an independent, source-relative audit of JoyboyBrian's PR #5496,
head `a99afd7e0024af8367d5a2f6f4d2da57a1d13dd5`. The unchanged program and
the exact claim audited are retained in `vendor/`. We found no defect in
the implication below. The inherited numerical and ROM-producer theorems
remain hypotheses; this is not an independent acceptance of those theorems,
of #4100, or of a complete multiplication algorithm.

## Statement and inherited contracts

Let `d` be a power of two, `ell >= 2`, and `h_i in {ell-1,ell}`. At every
axis let `2 <= s_i < 2^h_i`, with all moduli pairwise coprime, and let
`0 <= x_i < 2^h_i`. Fix an admitted tree node `[a,a+n)`, `n=2^level >= 2`,
with `b=a+n/2`, and a global row `0 <= g < 2ell-1`. Put

    P = 1 + sum_{a <= i < a+n} h_i.

Use the sequential axis-record format of PR5353, eight distinct protected
numerical ports, the fixed compiled topology, and initially blank new
owned backing. The source and all ports have their specified entry heads.
Assume these two source contracts:

1. **Numerical Entry.** PR5353/PR5219/PR5053 produce one P-bit `(c_i,v_i)`
   record for **every** right axis `b <= i < a+n`, including idle axes.
   If the left coordinates are valid, their current child is the unique
   `k in [0,M)`, `M=product_{a <= j < b} s_j`, satisfying

       k = x_i product_{a <= j < i} s_j (mod s_i),  a <= i < b.

   If any left coordinate is padded, `k=0`. Each offset is

       c_i = k (product_{a <= j < i} s_j)^(-1) mod s_i.

   `v_i` is the complete-rotation output, not the micro-row output.
   Entry supplies its stated input preservation, numerical ownership and
   retirement guarantees.
2. **ROM producer.** PR5092 accepts its encoded headers with `W>=h+3`,
   legal modulus, selector and offsets; it returns the canonical complete
   Beneš layers and selected row on the supplied output backings. It
   preserves its headers, returns all heads to zero, and erases private
   work. Blank tails beyond the current records are permitted. Its literal
   loops terminate at their record markers, rather than the allocated list
   length. This last fact is also directly visible in `microcode.py`.

The conclusion is the original #5496 multi-target interface: if at least
one right axis is active, `RowQuery` returns the exact current micro-row
output for every right axis in order, copying idle axes unchanged. It
uses one producer bank throughout that row, returns the borrowed bytes
and heads, and retires all joined owned work on `close`. An all-idle row
performs no tape work and allocates no numerical or ROM bank.

This quantifies over all admitted parameters and padded current values,
conditional on the two contracts. The finite executions below corroborate
the implication; they are not the reason the quantifier holds.

## Width and synchronized-row checks

Admissibility forces every `h_i >= 2`: there is no integer `s_i` with
`2 <= s_i < 2^1`. A node contains another axis besides any chosen target,
so `P >= h_i+3`. Thus `W=P` meets the unchanged ROM producer's guard,
including the minimum case `P=5,h_i=2`. The encoded constants `h_i` and
the local row fit P bits. Offsets are in `[0,s_i)` by the Entry contract.

For a long axis the local row is `g`. For a short axis the two global
rows `ell-1,ell` are idle; the remaining local rows are `g` before that
gap and `g-2` afterward. This lists `0,...,2h_i-2` exactly once. On every
active row the target bit

    min(local, 2h_i-2-local)

equals the corresponding global schedule bit `min(g,2ell-2-g)`. These
are the exact predicates and formulas used by the source loop.

## Induction over the literal axis loop

Immediately before parsing axis j, maintain these facts:

* The borrowed source head is at that axis's ROOT, with all bytes unchanged.
  The unary guide is back at its initial head.
* The numerical result head is at the first unconsumed right-axis record.
  Exactly one record has been consumed for each earlier **right** axis,
  whether active or idle. Axes outside the node consume no result record.
* The open output stream consists of exactly the processed right-axis
  outputs, each in its declared `h_i` bits and followed by `|`; its head
  is at the next blank output position.
* Coordinate/countdown scratch and all four headers are blank at origin.
  After every completed active target, the same physical producer roles
  are blank at origin, including both outputs and every previously exposed
  tail. The numerical result remains live until the entire loop ends.

The first state follows from Entry's return and the fresh joined ports.
There are three induction steps.

**An axis outside the right half.** The loop reads its declared width,
modulus and coordinate once, changes no source byte, and advances to the
next ROOT. It consumes no numerical record and emits nothing.

**An idle right axis.** The loop copies its h-bit coordinate to the
coordinate port, skips exactly P offset bits and their delimiter, then
skips exactly P complete-rotation bits and their delimiter. It checks and
crosses RECORD_END. The coordinate is appended unchanged to the output,
followed by `|`, and its scratch is erased. In particular, skipping the
ROM call does **not** skip the numerical record. This is the boundary a
single-target/all-idle test does not exercise: there can be a later active
axis whose record must still be aligned.

**An active right axis.** The loop copies the current modulus, offset,
and compiled row/width to the producer's four headers, padded against the
same unary P guide. It separately copies the current coordinate into the
coordinate and countdown ports. The preceding width argument establishes
the producer's complete header domain. The private bank and output roles
are blank by the invariant, so the producer contract applies on the
original backing objects.

The selected ROM contains exactly `2^h_i` row bits. At ROM position j,
until selection, the countdown equals `x_i-j`. A nonzero word is
decremented with ordinary borrow propagation; zero selects the current
row bit and disables further countdown changes. Since `x_i<2^h_i`,
selection occurs exactly once before the ROM end marker. Both heads
return, and countdown scratch is erased. XOR at the compiled target bit
therefore gives exactly this micro-row's output. There is no `x_i<s_i`
guard: intermediate padded coordinates must still be queried.

The complete-layer output, selected ROM and all four headers are erased
before the next axis. An erase crosses the current R and returns to L;
all previously exposed cells beyond that R were blank at entry and are
unchanged. The producer's private roles already returned blank. Thus the
whole old backing, rather than just the shorter new prefix, is again
blank. The complete-rotation field is consumed without supplying the
micro-row answer. Output emission and coordinate erasure reestablish the
invariant. Growing and shrinking target widths make no change to this
argument; P is fixed for the node.

At termination, both source and numerical result have their final end
marker. Their rewinds restore the required heads, and the output receives
R. The output stream contains every right target exactly once, in order.
`close` erases this stream and invokes the original Entry retirement once.
The all-idle branch has no Entry context and returns before tape access;
its `close` is also empty. This proves the stated implication.

Offsets depend on the current **left** child and all preceding moduli.
The right target loop neither changes that child nor needs an offset
recomputed from a changed right coordinate. This does not authorize
reusing an offset across the three distinct current-left states of an
exceptional reverse key; PR4716's stale-offset objection remains intact.

## Cost and ownership boundary

Retain the entire original invoice: one Entry invocation/retirement,
one complete ROM production for each active axis, and all adapter work.
No full-layer output is dropped merely because the consumer selects one
row. With A the active right axes and

    L = 2 + sum_i (3h_i+4),
    F = L + (n+1)(P+2)
        + sum_{i in A} [(2^h_i+1)(h_i+1)
                       + 2^h_i(2h_i-1) + 2h_i+4],

the literal loops have O(F) adapter tape work: one source scan and rewind,
O(P) headers/result consumption per target, O(2^h_i h_i) countdown scans,
and disposal of both outputs. The checker isolates adapter cell actions
from Entry and ROM work and compares them with the source's `4096F`
allowance. This is stronger finite diagnostic coverage than checking only
the much larger combined bound. We do not independently certify the
source's full finite-control constant or its inherited arithmetic tariff.

## Exact retained footprint of this shared ROM bank

The literal source permits a sharper statement than #5496's conservative
sum of per-invocation storage bounds. For a nonempty active set, let
`H=max_{i in A} h_i`, `N=2^H`. The exact retained cell count of its 52-role
ROM service bank, including the four caller-owned headers, is

    B(P,H) = 5 P 2^H (H^2+3H+1)
             + 2^H(4H-1) + 48P + 2H + 104.                 (1)

This is a count of finite-symbol **tape cells** of the pinned source
program. It excludes the numerical Entry, the three other joined ports,
borrowed axis/dirty words, interpreter metadata and any externally supplied
blank reserve. It is not a bit-space theorem for an unbuilt binary compiler.

Here is a derivation from the actual producer, rather than an inference
from its output contract alone. At tree depth k there are `2^k` nodes of
size `2^(h-k)` and height `t=h-k`. Each node has three scalar arrays and
`2t-1` layer arrays, hence `2^(h-k)(2t+2)` arena records. Summing over
`t=1,...,h`, and adding the shared N-slot stack, gives exactly

    J = N [sum_{t=1}^h(2t+2)+1] = N(h^2+3h+1).

This arena inventory is already part of ToikY's PR4192 lineage and
PR5092's proof. The new footprint statement assembles all literal roles,
markers and serializations and proves their repeated-bank maximum; it
does not claim the arena count or the general rolewise-maximum principle
(already in Ross Richardson's retained-backing audits) as new discoveries.

The successful singleton-offset call has the following retained extents:

| Role(s) | Number | Cells in each role |
|---|---:|---:|
| Scalar roles in the literal REGS tuple | 44 | `P+2` |
| Arena, five P-bit words per record | 1 | `5PJ+2` |
| Offset-major spool | 1 | `N(2h-1)+2` |
| Complete layers with one separator per layer | 1 | `(N+1)(2h-1)+2` |
| Selected row ROM | 1 | `N+2` |
| Width, modulus, selected-layer headers | 3 | `P+2` |
| Singleton offset header | 1 | `P+3` |

Every listed extent is attained: initialization writes every scalar role
and every arena record, and serialization writes every spool, layer and
ROM bit plus its markers. None depends on the offset value or on the
canonical network's particular bits. Conversely, no admitted execution
visits beyond these extents. Scalar `each`, copy, comparison, carry/borrow,
shift and erase routines stop at their fixed-width markers. Arena accesses
scan complete five-word records through R and return; their indices
select records without moving to a computed physical address. Initializers
append the displayed counts. Spool scans end immediately after the last
network bit; output appends end at their R slots. No routine steps past
those slots on a successful path. `execute` only extends a backing when
a unit movement first reaches its next cell, and never shortens a list.
This proves the table's exact high-water counts for fresh one-cell blank
private/output roles, the initialization used by RowQuery.

At fixed P each row of this table is nondecreasing in h. For a sequence
of target widths, each physical role therefore has exactly its extent at
the largest width seen. This **componentwise monotonicity**, together with
the reuse invariant, proves (1) by summing the table at H. Simply taking
the maximum of arbitrary aggregate storage bounds would be invalid; that
general shortcut is not used. An all-idle row allocates no service bank
and has count zero, not (1).

The other three joined ports have the exact total

    X = 2(H+2) + sum_{b <= i < a+n} h_i + n/2 + 2.        (2)

Coordinate and countdown each attain H bits plus two markers. With a
nonempty active set, the largest right-axis width is also active: long
axes are always active, and if all axes are short they are either all
active or all idle. This uses the retained two-width family. The returned
stream has one L, all right-coordinate bits, one separator per right
axis and one R. These three backings are disjoint from the service bank;
the header and ROM observer wrappers alias it and are counted once.
Thus `B+X` is exact for the joined non-numerical backing. Erasure returns
blank cells but does not reduce either quantity.

The h=3 -> h=2 fixture at P=11 retains **9,086 bank cells** after its
second call. Charging only the last target's fresh requirement, 3,084,
omits 6,002 retained cells. The reverse order grows 3,084 -> 9,086.
At P=5,h=2 the exact bank is 1,476 cells. The checker verifies every role's
extent at every actual invocation, (1), (2), the disjoint storage partition
and these rejecting controls. The numerical Entry remains separately
charged. Arbitrary changing-precision numerical histories (JoyboyBrian's #5505) and
separately allocated later RowQuery instances are outside this lemma.

## Independent finite oracle and controls

No #5496 verifier, retained Caller oracle, `decode_group` or source Beneš
routine is executed. The finite CRT oracle enumerates k satisfying the
displayed congruences, and enumerates the unique permitted offset. For
each small permutation, the network oracle exhausts all binary color
tuples and takes the lexicographically least tuple satisfying both input
and output perfect matchings. Each component has two complementary
colorings, so this is exactly color zero at its least vertex, independently
of the source DFS's order. Recursing on the two matched children therefore
reconstructs the canonical layers by a separate code path. All small
oracle layers are also composed directly and checked against the rotation.

Read-only observers decode actual producer headers and inspect its actual
outputs before disposal. They check complete layers, selected row, header
preservation, returned heads, private blanking, identical backing objects,
and historical tails. They never provide a successful execution's values,
tables or branches. Input serialization belongs to the test harness and
is not billed as a new machine implementation.

The actual cases cover two active targets, growing and shrinking widths,
an idle axis before/after an active one, invalid left padding, current
padded targets, all-idle behavior, and a nonroot node at `W=h+3` equality.
Seven execution mutations distinguish stale offsets, wrong row, suppressed
padded queries, missing full-layer disposal, missing result retirement,
skipping an idle offset record and replacement backing. Two algebraic
discriminators separate current-child semantics and the full right prefix;
two storage controls reject last-width-only and omitted-spool bills;
one receipt control separates JSON booleans from integers.

The exact values and counts are frozen in RESULT.json. No h=4 pipeline,
uninterrupted whole level, production-size geometry, raw compact S,
three-epoch key, binary numerical compiler, full E(p,ell) tariff, native
supplier, outer theorem or formal-kernel check is established here.

## Credit

The theorem being audited and the joined implementation are JoyboyBrian's
#5496. Ali Romman supplies #5353's RowEntry. JoyboyBrian supplies #5092's
ROM producer and #5053/#5219's numerical producer/entry. Hiroki KUMAZAKI
supplies the current-state CRT contract (#4716) and the #4169/#4174 audits;
ToikY supplies the explicit-width mixed caller (#4195) and the arena
refinement (#4192); Cinna Davis supplies #4100's CRT/Beneš construction.
The retained physical/repair lineage includes Tekalign, Jose Manuel,
Ryanson Jonathan, unpaidmoon, Douglas Colkitt and John-Michael Smith.

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex
assistance. Apache-2.0. No independent human or formal-kernel review is claimed.
