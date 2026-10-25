# Validation scope

Environment: CPython 3.12, Windows. Standard library only. Direct isolated optimized replay uses `python3 -I -O -B research/exact-unit-gauges/verify.py`. Checks raise explicit exceptions and remain active under -O. The registered package replay and Git-free export are also checked. Linux execution is not available in this session and is not claimed.

The verifier authenticates both retained source inputs, reconstructs four actual source blocks and both inverse-transpose orientations, checks every emitted instruction using exact Fraction arithmetic and the source scalar pricer, and validates independent integer flow certificates. It checks 320 symbolic local columns, 100 deterministic random matrices and 10 finite exhaustive potential grids. The finite grids are cross-checks, not a global-optimality proof; PROOF.md supplies the latter for the declared gauge family.

Failure controls reject altered flow, missing inverse scale, missing initial/final owned-field clear, shifted source window, non-dyadic coefficients and illegal native SCALE. No new recursive calls or productive temporary credits. No full rebuilt multiplication certificate, norm/conditioning replay, independent human review, Lean proof or new κ claim.
