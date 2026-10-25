# Arbitrary natural and edge subspace cuts leave the S4 gap open

For the fixed mixed S4 tuple `(2143,3142,4231,2143)`, arbitrary subspace cuts
of the natural four-dimensional module, together with all subspace cuts of
the binary six-dimensional unordered-pair module, have exact cone value
`4 p1+2 p2+4 p3` at every nonnegative generator tariff. This is 18 at `(2,1,2)`.
Adding them to PR2998's full permutation coordinate-cut class still gives
exactly 20. Separate scalar words cost 21. The actual circuit optimum remains
open at 20 or 21; no supplier or kappa improvement is claimed.

[PROOF.md](PROOF.md) proves the natural-module inequality over every field
and gives the complete binary edge proof. Only characteristic-two cuts are
admitted for binary formal words. Each cut uses one module copy, uniformly
over all scalar roles including every restored dirty role. Coupled-copy
subspaces and larger representations remain open.

This answers a bounded part of PR2998's explicitly excluded arbitrary-subspace
direction. Its coordinate-cone theorem and attaining potential retain their
original credit. New here is that these broader subspace classes are redundant
for this mixed-tuple objective throughout the stated tariff cones.

## Evidence and reproduction

From the repository root, Python 3.12 and the standard library:

```sh
python3.12 -I -Werror -B scripts/research_package.py --package research/s4-subspace-cut-boundary
```

Set TMPDIR to an owned external scratch directory for behavioral controls.
Direct Git-free source-export commands are:

```sh
python3.12 -I -Werror -B research/s4-subspace-cut-boundary/verify.py
python3.12 -I -Werror -B research/s4-subspace-cut-boundary/independent.py
python3.12 -I -O -Werror -B research/s4-subspace-cut-boundary/test_package.py
```

The span-extension checker and a code-disjoint RREF/quotient-rank checker
agree on all 67 binary natural and 2,825 binary edge subspaces. They compare
full membership-set hashes, every seven-permutation profile and its count,
and the full slack histogram in [RESULT.json](RESULT.json). The second
checker also covers all 212 natural subspaces over F3 and 1,120 over F5.
The all-field statement uses the written proof, not extrapolation.

Six behavioral groups run actual optimized CLIs. They reject changed sources,
over-capacity input, a false bound, Boolean receipt aliases, an omitted
noncoordinate domain, a changed target, an invalid dual and malformed JSON.
[VALIDATION.md](VALIDATION.md) records scope and bounded-runtime deviations.
Normal replay writes no scientific artifacts.

[SOURCES.json](SOURCES.json) pins unchanged main inputs at
`6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority revision six. No pending
Git object, network, solver or predecessor executable is required.
[TASK.json](TASK.json) records the fixed card and refined scope.

## Boundary and stopping decision

Stop this one-copy natural/edge cut search. More cuts in these classes cannot
strengthen the bound. Coupled-copy subspaces, larger modules or another
invariant change the hypothesis and need their own valid paid-call contract.
The edge theorem covers F2 only. Native acquisition/restoration, a complete
physical invoice, hosting, precision/tape, compiler/supplier admission and
the outer multiplication theorem remain open.

## Open next questions

Can a subspace coupling several copies, or a larger representation, give a
tuple cut exceeding four times the sum of its generator cuts? Start with one
explicit characteristic-two module and subspace and report all seven cuts.
That would escape the common dual here. No such cut is supplied.

Does the actual arbitrary-dirty-role circuit cost 20 or 21? Start with equality
in the inherited ordered-pair bound, or a complete formal twelve-letter word
with eight exterior letters. A cut-cone result does not decide that question.

## Credit

Nick Petalas. Credit Arham Tahir/PR2998, Adam Gall/PR1941, Ross Richardson/
PR1966/1989 and his retained permutation-cut archive, Nick Petalas/PR2583,
and the eumemic/Ali Romman/David Govea and other contributor lineage retained
in the pinned sources. Frozen predecessors are unchanged. Apache-2.0.
Assistance is disclosed in TASK.json. Separate implementations in this session
are author checks, not independent human review.
