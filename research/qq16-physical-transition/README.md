# Actual first QQ16 query-copy tape boundary

At PR4015's actual first streamed query, event1708 adds Z10 into Z2, which has
remained zero since its paid CLEAR1697. This source-bound result implements
that exact step as a closed bitwise copy between explicitly supplied tagged
bank-major windows, with source, tags, exterior and all heads preserved.

For S=M*2^(n*lambda), d=n²+n*lambda, L=d+2W+2, C=SL+2,
inter-bank displacement H=C+gap and P=2SW payload bits, the literal one-bit
shuttle costs P READ, P WRITE and 2PH+2(d+2) MOVE actions. It removes P redundant
destination reads under the identical transfer schedule. No arithmetic scalar
or native child is removed, and the resulting query remains live.

The same audit pins the preceding map1706 and negative q19 line1707. It gives
concrete header, stride and tape-head witnesses showing that PR3394's tagged
cover-router output does not meet PR3884's bare six-tape Gaussian-axis input.
A signed q19 basis witness also rejects replacing the whole native event with
a bare coordinate axis. A paid representation/native-wrapper adapter remains
necessary; summing those predecessor tariffs does not complete the transition.

This is a conditional local physical step and a precise direct-composition
obstruction. Actual caller window provision, numerical widths, native/map
placement, other operations and supplier admission remain unproved. The chosen
bank-major shuttle is quadratic in full-cover size and is not promoted as a
favorable global layout. No new kappa or general optimality claim.

Reproduce from the repository root:

    python3 -I -B research/qq16-physical-transition/verify.py
    python3 -I -O -B research/qq16-physical-transition/test_verify.py
    python3 -B scripts/research_package.py --package research/qq16-physical-transition

See PROOF.md for the exact contract, all terms of the bill, attribution,
comparison limits, physical obstruction and open next questions. PREDECESSORS
pins retained pending-head data/text; no pending executable is imported.

## Open next questions

Bind a real caller's heads/windows and signed grid around
the first q19 normalization, then construct and price its layout conversion
and return. Family-level ownership/coverage must be supplied independently of
this local access protocol. Substantial OpenAI Codex assistance is disclosed.
