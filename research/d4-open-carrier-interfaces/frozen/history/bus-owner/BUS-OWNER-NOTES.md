# Local moving-owner factors and restored-helper borrowing

These are local exact interfaces. No global supplier or kappa improvement is
asserted. The geometric input is the actual positive-gauge h7 D4 bus; the
separate h6 O2 bus supplies the restored-helper example.

## Pure h7 carrier factor

Write the four source groups as `(A,B,C,h)` with four independent fields each.
The open pure bus gives

`(A,B,C,h;YA,YB,YC) -> (h,A,B,C;YA+A,YB+B,YC+C)`.

Every field, including all target and helper inputs, is arbitrary. The literal
reverse word restores all 28 inputs over the integers. There are no feature
Hadamards in this variant.

At a physical source slot p the entrance is the positive `C_p`, and the
endpoint is `F7 C_(Op)^-1`. The helper enters in canonical UA and ends in
canonical VC=UA+UB. Tracking each original value to its actual destination
gives genuine native channels of ranks `3,5,5,5` per coordinate:

| Old value | Destination | Actual native rank |
| --- | --- | --- |
| h | source A | 3 |
| source A | source B | 5 |
| source B | source C | 5 |
| source C | helper | 5 |

Each channel was lowered with the pinned exact Clifford compiler, checking
the full binary tableau and Gaussian zero-state, including the global phase.
The 16-channel factor has histogram `{3:4,5:12}` and coverage72. Unchanged
target values contribute another60. The literal local query histogram is
`{1:8,2:40,3:20}`, mass148. The target-C delivery occurs at VC, so its route is
`[2,1,2]`; replacing that route by a direct `[2,3]` would preserve mass but
would not describe the actual delivery cut. The local uncovered mass is
`148-72-60=16`.

This factor is positive local evidence for a changed whole-value owner
journal: all endpoints are literal field permutations and monomial-wrapped
native channels. It does not establish the journal through the outer caller.
Original h has moved into an active source-A family; original source-C now
occupies the former helper family and ends at a rank4 frame. Restoring fixed
physical labels, or silently completing source-C to its old rank6 data cap,
changes the invoice.

The fixed physical helper endpoint UA->VC has rank1. Rank3 belongs to the
changed value route h->sourceA. They are different contracts.

## A literal width3 helper compiler

`bus_width3_compiler.py` makes the width3 helper interface concrete without
requiring a persistent owner permutation. For coordinate i let

`R_i = (F7 C_(OA_i)^-1) E_UA^-1 = L_i F3 M_i`

be its actual exact lowering, with L_i and M_i monomial. Apply `M_i^-1` to
the helper's raw incoming field before the bus. Its arbitrary entering dirt
changes; completed target and original-source responses do not. After the
bus, the old helper value occupies source-A_i. Apply `L_i^-1` there. Its
complete channel is now exactly F3, including the global phase.

Undo the bus's pure four-cycle by three raw whole-field SWAPs per coordinate.
These swaps carry each physical value's actual frame with it. They restore
the original family IDs, with helper F3 progress and unchanged target
responses. They deliberately change the source endpoint types:

- old A returns to its original family with source-B's native cap;
- old B returns with source-C's native cap;
- old C returns with the helper's VC endpoint.

All twelve actual source channels retain rank5. This is not restoration of
the old source caps. The new compiler costs12 whole-array SWAPs per local
call (36 signed VALUE ADDs and12 negations), plus four input and four output
monomial adapters. Their primitive/tape costs remain to be bounded. They
introduce no further recursive query. Treating a raw array swap as a clean
logical swap between fixed unequal native types would be incorrect; here
the changed types are part of the explicit boundary.

The normalized F3 can be assigned to any three owner-bank coordinate axes.
Tensor the exact h7 identity with spectator identities, then conjugate by
a coordinate permutation P taking its first three axes to the owner slot.
The two wrappers become `M_i^-1 P^-1` on input and `P L_i^-1` on output.
They are literal monomial operators on the full bank. Internal bus contacts
remain in the active data chart; no independent uncharged helper contact
chart is assumed.

For m47 and14 sequential replicas, choose14 disjoint3-axis slots, reserve
four spectator axes, and leave five axes for the terminal native remainder.
There are four fixed physical banks per stage,36 in total, with exact
replica/stage owner records in `BUS-WIDTH3-COMPILER.json`. Together with1344
public families the stock is1380, or `W=690/7` per replica. Each bank advances
42 axes through the helper compiler and pays its remaining rank5 query.
This establishes the local whole-bank packing boundary. A repeated ordinary
caller must still accept the changed source endpoint operators; the old
paired caller is not admitted by this packing result.

## Zero-residual helpers at arbitrary owner frames

Suppose a local word has helper entrance operator E, restores its helper
literally, and has all other completed outputs independent of the entering
helper dirt. Let an idle whole physical family currently contain an arbitrary
value v, in any native owner frame J. Define the local dirty symbol
`d=E^-1 v`. This is an interpretation of an arbitrary input, not an executed
conversion. Running the same local word returns `E d=v` and leaves the
completed public outputs independent of d. There is no entry/exit query
`E J^-1` to pay, because none is performed. All internal E-relative queries,
VALUE operations, access and return remain paid.

The assertion holds on full arrays, including spectator coordinates: E and
the local word act as the identity on those spectators. It requires a
disjoint idle family and exclusive access over the complete local word.
The borrowed owner receives zero native progress credit.

The h6 O2 bus has four such helpers. For the nine-call B4 chronology with
8 ports, there are64 public families,16 active per call and48 inactive.
`zero_residual_hosting.py` assigns four whole X families from pair
`(active_pair+1) mod4`. It verifies every local forward/negative-B boundary on
all64 independent integer columns and its literal inverse, and returns every
borrowed family before the following idle advance or bridge. Thus the four
helpers need no extra payload under this local borrowing contract. This does
not establish the asymmetric native global caller or its prefix precision.

## Complex versus BIT geometry

The complex h6 contacts are binary subspaces UA and UB, both rank3, with
common radical R of rank2. A Clifford canonical frame can use those
degenerate binary subspaces. The old BIT native operator instead exchanges
address halves on a self-adjoint projector over admitted odd address fields;
its image is nondegenerate. Its source/target nesting would require
`UA <= (UB)^perp`, while `UA intersect UB` contains R. That is incompatible
with nondegeneracy of UA. The same binary rank3 contact invoice therefore
does not by itself produce a BIT word. This is only a transfer gate for this
specific geometry and native projector grammar. A changed geometry or a new
compiler remains open.

## The common-plane issue

Actual O7 has fixed space of dimension1, generated by127 with norm1, and a
6-dimensional alternating moving space. The old paired seed planes
`span(p,Op)` have Gram I2 and are not O invariant: O sends Op to a third
independent line. An order3 orthogonal map on I2 would be the identity, since
the only two norm-one vectors are its coordinate axes. Thus an invariant
spectator2 does not show that the old shared P/Q seed and `m=2+5L` chronology
are preserved. A new O-equivariant chronological caller must be derived.
