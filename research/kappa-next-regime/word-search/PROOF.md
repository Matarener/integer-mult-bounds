# Exact last-use covector and cleanup argument

All scalar identities in this file are over F2. Register identifiers refer to
the compact 659-register R437 word. Native frame transports and complete
physical pricing are separately checked; an algebraic identity alone does not
license a frame transition.

## A shared dirty covector

Let `a` and `b` contain arbitrary values, including arbitrary dirty input. A
consumer that performs

\[
u\leftarrow u+b,\qquad u\leftarrow u+a
\]

can instead consume `a+b` once. Put `a <- a+b` before the chosen consumers and
remove their reads of `b`. Their resulting values agree exactly with the old
word. This remains valid when other commuting updates of each consumer occur
between the two old terms. The preimage checks require that the consumer has
no intervening observer and that neither carrier is rewritten across the
paired uses.

For the three emitted changes, the chosen carrier's complete remaining A read
list is respectively `[1996,2001,2008]`, `[2038,2044]`, or `[2079]` in the old
scalar A indexing. None is a COPY-retained helper, and B never reads any of the
three changed carriers. Thus their remaining changed values are unobserved by
productive targets and captures. Every consumed combination agrees with the
original at its actual observation.

The scalar A preimages are fixed in `candidate/CONSTRUCTION.json`. Six reads
are removed and three aggregate gates are inserted. Their carriers and second
sources are distinct: `(463,322)`, `(469,271)`, `(468,371)`. Two collections
update helper 413, but their observation contracts compose: neither aggregate
is a carrier for the other rewrite. Exact complete-word replays of all seven
nonempty subsets establish that no claimed tariff is counted twice.

## Dirty restoration is emitted in C

Write `z` for sources and helpers, and `y` for productive target accumulators.
The new A/scatter/B word still has the interleaved block form

\[
z\mapsto U'z,\qquad y\mapsto y+J'x+K'h.
\]

The local exact audit checks `J'=I` and `K'=D`. D is unchanged, so its initial
helper compensation cancels precisely. No target feeds a source or helper.
The new C is the literal inverse of every non-target A/B instruction, in
reverse order at the FULL frame. It therefore implements `(U')^{-1}` and
restores every source and every arbitrary dirty helper input. In particular,
it includes the inverse of each new aggregate; characteristic two makes that
inverse the same XOR instruction.

Leaving a dead carrier changed during the rest of A/B does not discard its
value. Its inverse belongs to the already required FULL cleanup. The complete
emitted native record stream includes these three inverse instructions. No
extra zero buffer or helper family is introduced. The independent interface
checker confirms H1, H2, H3, H4 and H5 without a generalized exception.

## Exact rank itineraries and tariff

Only the following six ordered helper paths change. The source's start and end
frames, all target paths and all ordered SOURCE paths remain the same.

| Register | Old dimension path | New dimension path |
|---:|---|---|
| 271 | `0,1,4,6,7,8` | `0,1,2,6,7,8` |
| 322 | `0,1,2,4,6,7,8` | `0,1,2,6,7,8` |
| 371 | `0,1,2,4,6,7,8` | `0,1,2,6,7,8` |
| 463 | `0,1,4,8` | `0,1,2,4,8` |
| 468 | `0,1,7,8` | `0,1,6,7,8` |
| 469 | `0,1,4,8` | `0,2,4,8` |

Dimensions do not replace geometry: `candidate/PATH-DELTA.json` lists every
actual old/new frame ID, and the native frame audit checks exact rational
containment at each emitted MOVE. Summing their positive dimension jumps
gives

\[
\Delta=2H_1-2H_2-3H_3+3H_4+H_5-H_6,
\qquad \sum_r r\Delta_r=0.
\]

The first two individual covectors have strict improvements for every
`0 < a < 1` under the local rank tariff: strict concavity of `r^(1-a)` gives
`1+4^(1-a) < 2^(1-a)+3^(1-a)` and
`2^(1-a)+4^(1-a) < 2*3^(1-a)`. The third and combined tariffs are nominated
numerically at the current endpoint and must be priced with the parent's
complete exact interval engine. This file does not substitute an approximate
sum for an exact supported endpoint.

The new gates use only frames 122, 184 and 391 already in the source catalogue.
The single changed old event is the birth `469 ^= SOURCE92`, from frame94 to
frame184. Moving that query respects SOURCE92's complete future path; its
ordered sequence of frames is unchanged. There are still nine COPY captures
at the same frames, with the same productive source rows and arbitrary-dirty
scalar contract.

## Limit of the claim

These arguments certify a finite, explicit local supplier transformation and
its exact recursive profile under the retained native transport contract.
Global physical owners, every paid idle, the native catalogue, prefix/ROW
charges, the exact bit endpoint and the complex/outer composition require the
parent continuation's separate source-bound checks. The inherited all-size
realization, compiler and analytic assumptions remain assumptions unless a
separate proof explicitly discharges them.
