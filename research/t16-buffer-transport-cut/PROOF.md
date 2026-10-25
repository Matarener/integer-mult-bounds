# A fixed-chronology cut for the last two buffers

This is a scoped obstruction to a specific continuation of Pierre's PR3388,
exact commit `684d347c0e6e578b8ab600d2e680ad6701cf7fa0`. It is not a packing
optimum or an obstruction to other T16 constructions.

## The permitted strategy

Keep PR3388's final 144-call chronology and its 69,120 whole-helper roles.
A bin is an `(owner_replica, child, port)` with the child's fixed capacity.
Initially there is one completely empty capacity16 bin, one completely empty
capacity32 bin, and 4,880 completely empty capacity 48 bins. All other
capacity 48 bins are full. The exact idle profile is
`{1:2382, 3:118, 16:1, 32:1, 48:4880}`.

A neutral transport moves ALL current occupants of one nonempty bin into a
completely empty bin of the SAME capacity, then compacts their offsets. The
source becomes the new empty bin. The source may be partially occupied: its
entire occupant bundle moves intact, and its smaller idle remainder moves to
the destination. Every such transport preserves the complete idle histogram.
Arbitrarily many transports, repeated visits and interleaving the capacity
classes are allowed. Within each capacity class the original nonempty bundles
remain intact and only change locations.

The final operation would split ONE intact full capacity 48 bundle between the
empty16 and empty32 bins, filling both and leaving its source empty48. Its
paid delta would be `-H16-H32+H48`, which strictly improves the moment for every
`0<a<1`. For `p=1-a` in `(0,1)`, strict subadditivity gives
`48^p < 16^p+32^p`. This favorable arithmetic does not establish a legal move.

Before that final operation, moving only part of a bundle, mixing bundles,
using a nonempty destination, moving between different capacities, or changing
the chronology is outside the strategy. In particular, the theorem does not
exclude a simultaneous nonneutral redistribution that ultimately has the same
delta.

## A finite closure bounds arbitrarily long histories

For a capacity16 bin b, let E(b) be the set of call indices strictly inside
its actual source-event window, with the active data pair excluded. Ignore all
per-call family conflicts, offsets and other bin interactions. This grants
extra moves and therefore cannot exclude a physically permitted history.
For every originally nonempty capacity16 bin c, let T(c) be the call indices
of its original whole occupant bundle.

Start R with the original empty16 location. Repeatedly add c whenever
`T(c) subset E(b)` for some b already in R. This least fixed point is finite;
every productive round adds a bin, so at most 7,168 rounds suffice.

Every location reached by the actual empty16 buffer lies in R, including
histories that revisit bins and move different bundles into an old location.
Proof: consider the first actual visit outside R, if one exists. Its source
bin c has never previously been empty. The allowed operations can change a
bin's contents only by making it the empty source or the empty destination.
Thus this previously unvisited source still holds its original bundle. The
previous empty location b belongs to R, so the permitted evacuation implies
`T(c) subset E(b)`. The fixed-point rule already puts c in R, a contradiction.
Other capacity classes cannot change capacity16 contents under these rules.

This is an upper bound on physical reachability. Membership in R does not
assert that a corresponding family-valid physical history exists.

## Source-bound finite certificate

The primary verifier authenticates all retained PR3388 source files and its
canonical-main inputs, reconstructs PR3381, and checks every one of the sixteen
PR3388 intermediate maps with the retained whole-helper owner auditor. The final
canonical owner payload is
`8e5940efdf9026ec41200e6dc7132e3736f2d63f84d5e4e24d82d8db03967f4e`.
It compares every final row and the complete final plan with the committed
fixtures before deriving the closure.

There are 7,168 capacity16 bins and 7,167 original nonempty bundles. Starting
at `(1,2,46)`, the closure adds 858 bins, then 37, then none. Its 896 locations
are exactly all 112 ports of owner/child types

```text
(0,0) (0,2) (1,0) (1,2) (8,0) (8,2) (9,0) (9,2)
```

The four distinct E(b) are call-index prefixes of lengths 5, 6, 9 and 10.
Each original full48 bundle is inspected against every one of those windows.
The largest total width eligible for any window has this distribution:

| Eligible width | Original full48 bundles |
|---:|---:|
| 0 | 2,185 |
| 4 | 12 |
| 9 | 91 |

These counts sum to all 2,288 original full48 bundles. Even the best bundle
has only 9 eligible width. A literal witness to the maximum is the original
bundle at `(14,8,23)`. No subset can supply the required 16.

Neutral capacity 48 transports cannot evade the bound: they move these same
intact original bundles among capacity 48 locations. Grant the capacity32
buffer ANY destination or eligibility whatsoever. The final split still
needs16 eligible width for the capacity16 buffer, whereas every possible
full48 bundle supplies at most9. Therefore the permitted strategy is
impossible at the fixed PR3388 chronology.

## Independent check and limits

`independent.py` imports no primary or retained Python module. It reconstructs
the 30 source events per replica from the canonical template, derives child
capacities from the selected pending-axis data, and computes eligibility as
explicit sets. A queue of eligibility classes replaces the primary bin-level
bit-mask fixed point. It independently obtains the same 896 bins, four classes,
2,288 full48 bundles and width histogram. The fixture owner hash binds it to
the exact published PR3388 payload; the primary replay separately proves the
fixtures equal the retained source reconstruction.

Behavioral controls exhaust all 576 three-bin/two-call systems and every
reachable permutation state, including returns to previously visited bins.
Other controls admit a two-round partial-occupancy route and detect the
width9-to16 escape when the permitted window changes. Actual CLI mutations
reject changed retained code, owners, result, repinned chronology and live input.
These checks support the finite computation and proof implementation. The
first-visit argument supplies the unbounded-history implication.

No new supplier or kappa is claimed. The selected result is unchanged.
PR3388's strict physical admission, exact moment prices, outer transfer and
conditional multiplication theorem are not independently rerun here because
this proof supplies no changed owner map. All-size/compiler, native realization,
common-label/mutable-source, hosting, precision/tape and analytic premises remain
separate. No formal-kernel or independent human review is claimed.
