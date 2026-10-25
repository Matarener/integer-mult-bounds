# Complete direct 584 commuting-retiming cover

All addresses are zero-based positions in the two pinned PR 3133 words. This is
a finite statement at binary address dimension nine. It is not a theorem about
all supplier words, all helper eliminations, or all dimensions.

## Changed word and exact algebra

The original word contains

```
B48:   168 += 584/2
B753:  584 += 439
B1196: 168 -= 584/2
R82:   584 -= 439
```

The last two operations occur in B and restore respectively. The helper has
arbitrary initial dirt. Remove B48 and B753, replace B1196 by `168 -= 439/2`,
and remove R82. Remove helper584 from the live/helper inventory and regenerate
the inverse-reverse cleanup after every retiming. In the full fixed word the
two helper reads contribute `p/2 - (p+q)/2 = -q/2`, and the restoration returns
the helper. The exact interpreter checks this assertion against the complete
word, including all surrounding operators; it does not assume isolated scalar
cancellation is sufficient.

The original-cut word and the first and last contact-class representatives
are replayed in both orientations over the rational free group algebra. Each
live input and arbitrary dirty helper is an independent column; native warp
symbols are independent noncommuting invertible operators. Forward endpoints
are `y += x`; the same-order inverse-transpose endpoints are `x -= y`. All
other live rows are identities and all ninety private cleanup rows are zero.
The supplied cleanup is executed literally and compared to an independent
inverse-reverse derivation. These finite symbolic identities imply equality
under every substitution of invertible operators, but do not admit the frames.

## Exact family

Only four additions with common source 439 may move:

| Destination | Original B address | Addition |
|---|---:|---|
| 168 | 1196 | `168 -= 439/2` (the new direct read) |
| 150 | 772 | `150 -= 439/2` |
| 56 | 802 | `56 -= 439/2` |
| 115 | 1244 | `115 -= 439/2` |

All other scalar instructions remain in their original relative order. No
read crosses a B boundary, no correction gates are added, and every native
slot retains its physical register and position. Native operators, phases,
entrance/exit frames, and all helper entrance/terminal frames may change freely.
Non-native scalar frames may be chosen arbitrarily subject to the inherited
common-frame and monotone consecutive-contact inclusions. This is a generous
feasibility relaxation: a contradiction already rules out a paid realization.

For two nonzero transvections `d += a*s` and `e += b*t` on distinct endpoints,
the matrices commute precisely when `s != e` and `t != d`. A nonidentity
scale commutes with the selected transvection precisely when it touches
neither endpoint. These criteria follow by multiplying their elementary
matrices. The four movable reads commute pairwise. No native slot touches
their source or destinations, and no remaining fixed B gate touches source 439.
The verifier checks these premises on both pinned words.

Remove the four movable reads and the two deleted gates to obtain a fixed
sequence. Each selected read can cross precisely the contiguous interval of
fixed gates commuting with it around its original cut. It cannot cross the
first noncommuting gate on either side by the allowed adjacent swaps. The
maximal original-address insertion windows are

```
168: [0,1301]    150: [0,1292]    56: [560,1245]    115: [0,1373].
```

An insertion at address j is immediately before original B gate j. The fixed
sequence's integer cuts omit the removed gates; the verifier derives those
cuts directly rather than treating the displayed addresses as an input.

## Finite quotient and completeness

For each read, partition its legal cut interval at every fixed contact of its
destination. A slot is the closed integer interval after one contact and before
the next. The four slot counts are respectively `8,4,1,8`. The carrier has no
fixed contact in B, so a contact class is exactly:

1. one slot for each movable destination; and
2. one of the 24 orders of the four reads on carrier 439.

For a chosen order with slot intervals `[l_i,u_i]`, feasible nondecreasing cuts
exist iff the greedy recurrence `c_i=max(l_i,c_(i-1))`, starting at zero, never
exceeds `u_i`. Necessity follows inductively: every feasible cut is at least
its greedy counterpart. Sufficiency is the produced cut sequence. Equal cuts
are allowed, with the specified carrier order fixing the order at that cut.
Of `8*4*1*8*24 = 6144` choices, exactly 1002 are feasible for each provider.

Every allowed adjacent-commutation placement has one of these slot/order
descriptions, hence a generated representative. Conversely each generated
representative lies in all four maximal windows, so commuting each read to
its chosen cut yields an allowed placement. Within one class, every physical
register has the same ordered contact list. Changing cuts inside a slot only
crosses gates disjoint from that destination, and the carrier order is fixed.
Thus all common-frame/monotone inclusion constraints are the same up to event
renaming. One infeasibility witness per class covers every allowed placement.

## Independent physical path certificates

For each representative, the retained certificate identifies a nonzero vector
v and a sequence of literal physical events. The checker reconstructs events
from the changed word itself, with native warp entrance/exit events separated.
Input r has frame span(port[r]); target r+112 has terminal frame port[r]^perp
in F2^9. These actual source/target contracts remain fixed.
It requires that:

* v belongs to the exact fixed source frame;
* the sequence is strictly chronological;
* each adjacent pair consists of consecutive touches on a common physical
  register (no intervening read, write, scale or native warp is omitted);
* no interior event is a native warp boundary; and
* v does not belong to the exact fixed endpoint frame.

Monotone inclusion along each consecutive-register edge propagates v. A common
scalar event uses one frame for its involved registers. Therefore propagation
forces v into the endpoint frame, contradicting the last check. This argument
uses only necessary frame inclusions and not a floating objective, graph
optimizer, heuristic failure, or a claimed native phase calculation.

All 2004 final certificates pass this literal checker. Every path starts at an
original input port and ends at a target output; none uses a native boundary or
a helper entrance/terminal boundary. Each is therefore independent of every
native operator, phase, native entrance/exit rank, and helper entrance/terminal
frame at the existing positions. These boundaries can all be relaxed at once.

For discovery, 660 classes per provider first had port-to-target certificates,
and 342 had certificates ending at native slots on registers 285/381. The latter
were insufficient for this stronger statement. They were replaced by new paths
after relaxing all native boundaries and every helper terminal boundary. The
additional discovery paths end at targets 124 (206 cases), 159 (67), 215 (30),
192 (19), 212 (12), and 129 (8). The final verifier consumes only the complete
2004 port-to-target certificate set; it does not rerun that discovery search.

The checker expressly rejects a valid fixed-native-boundary certificate when
it is offered for the stronger port-to-target contract. It also checks that an
actual inserted native reset breaks a formerly consecutive scalar path. Thus
neither a fixed-slot obstruction nor a path jumping across a new reset can be
used to exclude a larger model silently.

No invertibility, equal native entry/exit dimensions, phase realization or cost
is needed for this necessary-condition obstruction. Free changes at existing
native slots and helper boundaries still cannot repair it. Changing the scalar
network, adding or moving native slots, changing input ports or target output
contracts, or crossing a noncommuting gate with corrections remains outside
this result. No claim is made about those larger models.

## Meaning of the result

The direct helper elimination is an exact arbitrary-dirty algebraic identity,
but none of the complete commuting-retiming family has legal monotone frames
even with the stated native/helper boundary relaxation. There is consequently
no cost gain or
conditional κ to claim from this family. A changed scalar-network/consumer contract
requires a new exact word, native operator/phase proof and complete cost invoice.

This is a written finite coverage argument plus exact executable evidence.
There is no Lean/kernel proof, all-parameter supplier theorem, new selected
frontier, or global no-go theorem.
