# A conditional Y-feedback route and its restoration obligation

This note concerns the exact scalar specialization of the retained native
word. It does not certify a physical feedback construction or a new bound.
`y_cleanup.py` checks the following facts against the two source members
already declared in `SOURCES.json`; `y-cleanup.json` records its result.

Write `r = R[5]^T`, using zero-based mode numbering. The retained matrix has

    R R^T = 56 I8,
    C = I112 - R^T R/4,
    R C = -13 R,
    C^-1 = I112 - R^T R/52.

The inverse follows from `(R^T R)^2 = 56 R^T R`. Consequently, if a proposed
pure Y-feedback route has endpoint response `deltaX = -C deltaY`, then the
unique residue producing the desired `deltaX = -r m` is

    deltaY = -r m/13.

The checker verifies this identity on all112 entries. It establishes a
possible scalar mechanism, conditional on such a route and on subsequent
legal restoration of Y. The denominator13 is not a dyadic scale and must be
handled by the actual arithmetic and precision contract.

All112 Y fields start at ground and finish at rank8. The56 nonzero entries
of this particular residue occupy56 distinct final rank8 hyperplanes;
every pair joins to the full rank9 space. Rank1 frame72 is contained in28 of
these destinations, while frames114 and115 are each contained in24.

Thus a ground or rank1 provider does not grant an ordinary tail cleanup.
A direct monotone lift from a rank1 provider to a containing rank8
destination traverses seven additional ranks; for the other destinations,
that direct monotone route is unavailable. Already-paid native paths,
shared relays, or a coupled change to the program could behave differently
and are not excluded by these facts. Any such proposal must supply the
actual payload at the destination's frame, restore every original field,
and include the complete routing and arithmetic cost.
