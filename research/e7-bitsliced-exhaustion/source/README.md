# All minimum E7 frame relations: two quadratic types

There are exactly **1638** twelve-line supports for a nonzero characteristic-zero
E7 frame relation. They form **two** root-reflection orbits, of sizes **630**
and **1008**. Each support has one scalar family of relations. Both families
are trace-zero quadratics, of ranks six and two. This completes the equality
question left by Nick Petalas's PR5238. No new kappa is claimed.

[PROOF.md](PROOF.md) gives the exact statement and the characteristic-zero
argument. [RESULT.json](RESULT.json) gives the representatives, orbit hashes,
ranks and coverage. [SOURCES.json](SOURCES.json) pins the retained geometry
and predecessor proof. [verify.py](verify.py) recomputes the full census.

For the slice perpendicular to `(2,0,0,0,2,0,0,0)`, representatives are
`x0^2+x1^2+x2^2+x3^2-x4^2-x5^2-x6^2-x7^2` and
`(x0-x1)(x2-x3)`. Their nonzero evaluations have equal magnitude, with six
of each sign. Rational orthogonal transport covers every E8 root slice.

## Why this helps the decoder work

PR5238 proves minimum support twelve but leaves equality open. The new
classification supplies all sparse equality obstructions at that boundary.
It also shows that the diagonal type alone does not cover all obstructions.
It does not supply the separate arbitrary-deletion extension lemma in the
[released handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1502#discussioncomment-19145642).
No decoder floor or physical caller follows without that missing implication.

## Verification

Python 3.12 and its standard library suffice.

```
python3.12 -B scripts/research_package.py --package research/e7-minimum-support-classification
python3.12 -B scripts/check_research_commit.py --package research/e7-minimum-support-classification
```

Expected: `PASS_E7_MINIMUM_SUPPORT_CLASSIFICATION`,
`PASS_REGISTERED_RESEARCH_PACKAGE`, and `PASS_RESEARCH_COMMIT_BYTES`.
The normal and optimized checks each enumerate all 134217727 nonzero binary
codewords. They check all 63 reflection generators on all 135 frames, the
complete two-orbit partition, exact rational lift ranks, quadratic ranks,
ambient transport, 24 coordinate omissions and four corruption controls.
The verifier authenticates retained sources before it executes them.
It writes no source file. The registered time cap is 600 seconds per mode.

The same assistant supplied the proof and checker. These are exact finite
checks plus a written proof, not independent human or formal acceptance.
No native or selected cold replay, outer admission, full historical suite,
Lean or Docker run was used. Full source-history preflight is unavailable
in this shallow checkout; exact bytes and immediate source ancestry are
separate checks. Selected files are unchanged.

## Open next questions

1. Does every live-frame relation after at most seven P112 deletions extend
   to an ambient trace-zero quadratic? Retain all deletion quantifiers.
   The equality classification does not prove this separate extension.
2. At the next incidence boundary, which of the two equality types is
   compatible with the literal deleted frame and pivot conditions? Start
   from the two explicit representatives and charge every omitted line.
   No new deletion census or reservation is made here.

## Credit and scope

Nick Petalas's [PR5238](https://github.com/CrocSwap/integer-mult-bounds/pull/5238)
supplies the minimum bound, root and frame code, and quadratic injectivity.
Its source files are retained byte for byte, with all source notices.
The originating handoff is JoyboyBrian's. The retained lineage includes
Josie Elliston, Andrey Mas, Aaron Wang, Brett Halligan, themilkman216 and
DreamingOfClouds; their individual contributions remain in the source note.
New equality census, orbit classification, characteristic-zero extension,
proof and checks: Ali Romman with substantial OpenAI Codex assistance.
Apache-2.0.

Canonical base: `df0137efd35e11b4445734bf612bdd4c7ebc330c`, priority revision 7.
The selected source check passes at conditional kappa 0.00310045. This package
changes no selected result and reserves no physical construction.
