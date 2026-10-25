# A directed attempt to realize the improved complex clock profile

**No new controller or κ is admitted.** This scope tests a specific geometry
that would greatly reduce the remaining complex budget, then changes the
coefficient and bridge model when the integral controller test fails.

The width agent's exact packing relaxation favors
`Δ=(1,1,1,2,2,3,5,6,6)`. Each pair advance Δ produces 224 scalar-port bins of
rank `8Δ` per replica. With the legitimate complex word and helper inventory,
its normalized moment at κ=0.001745 still exceeds one by
`0.000003728657046922735778904115`, about `0.243888` weighted rank per replica.
It is therefore a promising companion to a local-word improvement, not by
itself a sufficient endpoint. Source:
`../bit-geometry/COMPLEX-CLOCK-PACKING.json`.

## Exact integral controller test

`orbit_profile_witness.py` uses the sibling complete equal-clock GL(F2) orbit
model. It retains the full idle histogram and runs an exact scalar-free clock
feasibility test before expanding each scalar state. It does not enumerate a
bounded list of bridges or coefficients.

The target profile was exhausted: **914,356 orbit/profile states, no witness**,
in 41.2 seconds. `TARGET-PROFILE-ORBIT.json` pins both scripts and records the
counts. The original profile `(1,1,1,2,2,4,4,6,6)` passes the same program in
2,326 states; its explicit finite path is independently replayed by `review.py`.

The reduction to currently occupied clock destinations relies on the sibling
K4 nine-idle minimum when interpreting this as an integral-controller
obstruction. A redundant stop at an unoccupied level could otherwise alter a
prescribed histogram; removing it would produce an eight-idle controller,
which that completed integral orbit search excludes. Sources are
`../bit-geometry/controller-orbits/K4.json` and
`../bit-geometry/CLOCK-MODEL-PROOF.md`.

Non-integral dyadic and rational bridges do not reduce modulo two and remain
outside this finite obstruction. Independent primal and bottom maps also
remain outside it. No automatic lift from a finite-field witness is asserted.

## A rational three-pair shortcut and a direct four-pair attempt

`K3-TRIANGLE-PROOF.md` rules out one proposed seven-call, five-idle triangle
over arbitrary rational or dyadic coefficients. The first interface forces
`b=0,c²=1`. At the next interface the accessible top-Y direction lies outside
the bottom-Y row space, so the next forward call cannot lower the rank. This
is a proof about that topology, not a general dyadic floor.

The four-pair numerical attempt uses a concrete clock topology with the target
profile. After the first two calls it applies one three-pair interface, followed
by four two-pair interfaces at clocks two, four, five, and seven. The pair
advances before final cleanup are `2,2,1,5,1,6`; cleanup adds `6,3,1`.

`rational_topology_probe.py` parameterizes one full-dimensional
`SL3 × SL2⁴` chart with 20 unrestricted real shear coefficients. Its exact
Jacobian rank for the SL3 chart is eight, checked with rational arithmetic.
Twelve numerical starts found no exact rational endpoint; the best squared
diagonal-block residual remained about two.

The explicitly changed model in `independent_topology_probe.py` gives the
primal and bottom maps independent coefficients, for 40 parameters. Eight
starts reduce the residual much further, but none gives an exact endpoint.
`continuation_probe.py` shows why the smallest numerical residual is not a
construction:

| Stage | Squared diagonal-block residual | Coefficient norm | Full matrix condition number |
|---|---:|---:|---:|
| Best initial independent fit | 6.21×10⁻⁶ | 21.1 | 1.78×10⁶ |
| First continuation | 2.10×10⁻⁶ | 1,048 | 1.12×10¹⁰ |
| Second continuation | 2.01×10⁻⁶ | 44,604 | 1.81×10¹³ |

A fixed-coordinate refinement also fails. All 24 rounded rational endpoints
from the paired, independent, and continuation runs have nonzero exact
diagonal blocks. The exact acceptance gate rejects them. Numerical failure
does not prove impossibility of this chart, and certainly does not exclude
other rational or independent-map topologies.

## Replay

The lightweight source and exact-control review is read-only:

```sh
OPENBLAS_NUM_THREADS=1 python -B research/kappa-1745-continuation/complex-controller/review.py --output /tmp/controller-review.json
```

It authenticates the stored numerical sources, replays the positive finite
path, recomputes all 24 rational rejections, checks the SL3 chart rank and the
two Laurent determinant identities, and records the external dependencies.
It does not rerun the negative enumeration. To do that from the repository root:

```sh
python -B research/kappa-1745-continuation/complex-controller/orbit_profile_witness.py --output /tmp/target-controller-orbit.json
```

Elapsed times are observational and not proof-relevant. Numerical solver traces
can vary with the numerical runtime; their exact rational rejection is the
retained admission decision. No hosted program, bridge precision invoice, or
outer recursion claim is attached to any of the rejected fits.

## Open next questions

An exact dyadic controller with a different topology, or a finite exact
controller with independent primal/bottom maps, remains a genuine changed
premise. A useful next candidate should be checked symbolically before large
floating optimization: the observed degeneration shows that small residuals
can be purchased by very poor conditioning.

The target profile would still need a local-word gain of approximately
0.243888 weighted rank per replica. A new topology needs the literal monotone
standard flags, exact scalar endpoint, complete helper and residual inventory,
and all bridge and precision costs before it can be combined with such a gain.

This scope preserves the CrocSwap/integer-mult-bounds controller lineage,
including Johnny Franks / report M and the recipe-floor work. The direct orbit
engine and economic target are credited to this continuation's width agent.
The directed traceback, rational topology attempt, and three-pair obstruction
were developed with substantial OpenAI assistance. Earlier frozen construction
and operator-audit scopes were not modified.
