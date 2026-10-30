# Three coupled contacts improve the PR5565 P104 cascade

## Source and statement

The input is the exact PR5565 word at
`9af814164b9dfc21f19ec737959d67cb71488c95`, by Pierre-Loic Doulcet
(hexapode). It includes both stages of the commuting-contact cascade.
[SOURCES.json](SOURCES.json) pins this word and the retained price engine.
The event-lattice search from DreamingOfClouds's PR5568 supplied the
construction method. This package supplies the new four-site frame step
and its complete certificate on the later word.

The construction preserves every scalar instruction, coefficient and
position in the scalar sequence. It preserves all 208 main endpoints,
all helper starts, all owned lifetimes and all 104 literal ports. It
changes three ADD charts and the final frame of helper 307.
[CHANGES.json](CHANGES.json) gives these four declarations. All event
indices below refer to the zero-based PR5565 source program.

At each of 18 local calls, the paid change is

```text
-2 H2 + 2 H3 - 2 H4 + H5.
```

The target change is `H4 - H5`. The complete conditional claim is
kappa = 0.00308595, tested at 0.0030859505. The five framework assumptions
and the source helper-endpoint conditions remain inherited. The selected
record is unchanged.

## Exact chart geometry

The new frame U has basis `[30,44,459]` and dimension three. It is frame
1089 in the new word. The source has 1089 frames, indexed 0 through 1088.
The following identities use complete binary spans, not basis-list equality:

```text
U = span(frame 345 union frame 355)
  = frame 728 intersection frame 235.
```

The relevant source frames are:

| Frame | Basis | Dimension |
| --- | --- | --- |
| 3 | `[]` | 0 |
| 345 | `[30,487]` | 2 |
| 355 | `[30,44]` | 2 |
| 728 | `[30,44,76,391]` | 4 |
| 235 | `[30,44,74,385]` | 4 |
| 236 | `[6,24,42,74,385]` | 5 |
| 775 | `[7,25,43,75,139,267]` | 6 |
| 795 | `[12,18,32,64,391]` | 5 |
| 127 | standard nine-axis basis | 9 |

The changed contacts are:

| Event | Scalar instruction | Old frame | New frame |
| --- | --- | --- | --- |
| 14374 | `ADD 319 += 85` | 728 | U |
| 14399 | `ADD 507 += 319` | 728 | U |
| 16628 | `ADD 307 -= 85` | 236 | 235 |

The new first two contacts let register 85 bypass frame 728. It can then
meet helper 307 at frame 235. Helper 307 no longer needs its last rank-one
transport and can finish at dimension four. This is a coupled change:
the last contact cannot move down to frame 235 while 85 retains frame 728.

The exact paths between unchanged accesses are:

| Register | Old path | New path |
| --- | --- | --- |
| 85 | `345 -> 728 -> 236 -> 127` | `345 -> U -> 235 -> 127` |
| 319 | `355 -> 728 -> 775` | `355 -> U -> 775` |
| 507 | `3 -> 728 -> 795` | `3 -> U -> 795` |
| 307 | `235 -> 236` | stays at `235` |

All arrows are strict subspace inclusions. Every unchanged intervening
register access is retained. The constructor checks the four source
values, changes their charts, and replaces transports only in gaps with
a changed endpoint. It removes eight transports and inserts seven. The
result has 25,132 events and the same 21,686 scalar/owned events.

## Arbitrary-input identity and native interfaces

Let C_F be the native chart for frame F. Write a physical field as C_F z,
where z is its abstract row. A transport from A to B applies C_B C_A^-1
and leaves z unchanged. An ADD at one common chart forms the same abstract
row sum. A SCALE has the same property. Thus each legal changed itinerary
implements the same abstract scalar word.

The exact replay checks a common chart at every scalar contact and strict
nesting at every public transport. It checks all 743 original input
coefficients in every output. Every helper row returns its own arbitrary
input, and the main shears remain unchanged. A separate dense dyadic
transpose replay checks the reverse operator.

Helper 307 starts at frame 3 in both words. Its target changes from the
rank-five map C_236 to the rank-four map C_235. Its input stays independent
of all other inputs. No helper input is set to zero or discarded. Every
other productive target stays fixed.

The native replay checks every paid map, helper target and main adapter:
rank, signed Pauli images and absolute phase. The factorwise tensor rule
gives the same chart identity at every positive width under the retained
native framework. These checks do not, by themselves, prove the full
multiplication theorem or provide independent acceptance of the framework.

## Complete paid and target change

The four register changes give these local paid deltas:

| Register | Paid delta |
| --- | --- |
| 85 | `H1 - H2 - H4 + H5` |
| 319 | `H1 - 2H2 + H3` |
| 507 | `-H1 + H2 + H3 - H4` |
| 307 | `-H1` |

Their sum is `-2H2 + 2H3 - 2H4 + H5`. The local paid rank mass and target
rank mass both decrease by one. The complete rank-mass surplus remains
760. Paid jobs decrease by 18, from 66,726 to 66,708. The 12,814 productive
fields remain independent.

Write h_r(k) = r^(1-k), with h_0(k) = 0. If M is target moment minus paid
moment, then

```text
M_new(k) - M_parent(k)
  = 18 * (2 h_2(k) - 2 h_3(k) + 3 h_4(k) - 2 h_5(k)).
```

For 0 < k < 1, this is strictly positive. To see this, the decreasing
vector `(5,5,3,3,0)` has partial sums `(5,10,13,16,16)`, and
`(4,4,4,2,2)` has partial sums `(4,8,12,14,16)`. The first vector
majorizes the second. Strict concavity of x^(1-k) therefore gives
`2 h_5 + 2 h_3 < 3 h_4 + 2 h_2`. The zero term is used only in this
proof; it is not an uncharged job in the construction.

The predecessor raw crossing is in
`(0.00308521055201, 0.00308521055202)`. The new crossing is in `(0.00308595175070, 0.00308595175071)`.
The raw gain is between 7.4119868e-7 and 7.4119870e-7. The raw headroom
above the claimed endpoint is between 1.75070e-9 and 1.75071e-9. The verifier reconstructs both
predecessor histograms from the new bill and the declared deltas, then
checks the predecessor crossing again. Two rational moment engines check
the new tested endpoint.

The derivative certificate proves that the complete new moment is strictly
decreasing on `[0,0.0034]`. Its upper crossing endpoint is the raw funding
ceiling for this fixed invoice on the retained BIT band. No ceiling for
other words or suppliers is claimed.

## Full caller, verification and limits

The unchanged caller has 18 forward local calls, 15 query shears and
3,120 whole idle jobs. The physical replay checks the actual 104 ports,
main routes, central squares, output ranks and whole-idle maps. The price
code derives the invoice from those events and checks it again from the
controller paths. It includes helper targets, normalizers, main adapters,
all routes, scalar operations, owned copies and erasures.

The retained price engine changes only claim, predecessor-comparison and
exact paid-count declarations. LITERAL-CHANGES.diff records every change.
No source checker is weakened or patched at runtime. The PR5545 source
capsule and all 33 payload files are authenticated before import.

The compiler checks all three tail ratios, completion, splitting, the
integer threshold, retained BIT stock and all 54 strict plus four
functional outer predicates. New negative controls reject a missing
transport, a wrong scalar coefficient, an old contact frame, an old helper
exit, a wrong intermediate subspace and an unchanged word presented as an
improvement. Source controls also reject a wrong native phase, insufficient
BIT saving and an old cutoff.

The five inherited assumptions remain: native all-column implementation,
owned erasure, uniform compiler closure, precision/fixed-tape costs and
analytic recovery. The helper-endpoint contract retains its source review
status. The uniform word and complete rounded multiplier are not
materialized. The same assistant performed discovery and verification;
this is not independent scientific review or proof-kernel acceptance.

Ali Romman with substantial OpenAI Codex assistance. Apache-2.0.
All retained source notices and predecessor credit remain in the package.
