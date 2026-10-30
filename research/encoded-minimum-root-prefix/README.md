# Encoded minimum root prefix

This implements PR5688's minimum root-prefix search on the actual Count
tapes, then supplies all 29 RootPlan fields to the unchanged RootLayer.
It closes the predecessor's encoded integration gap. The complete kappa
calculation does not change.

The [proof](PROOF.md) gives the search invariants, caller contract and
positive costs. The [evidence](EVIDENCE.md) separates exact bounded checks,
complete reduced payloads and omitted production obligations. Source pins
are in [SOURCES.json](SOURCES.json); each retained archive member is in
[SOURCE-INDEX.json](SOURCE-INDEX.json).

The search uses no input-dependent host integer decoder. It returns the
least q with `ceil(2^(Kq)/S)*S < 2^(Kq+1)`, where `S=F^D(M-q)`.
The unchanged physical caller executes a stock-six case with four original
rows and six padded rows. The exact endpoint, borrowed state, empty pools
and erased owned fields all pass. Repeated use and nonzero-padding rejection
are tested. These fast payloads use the declared reduced parameter law and
complete C2 fixture, not the production O73/GL64 backend.

## Reproduce

Use Python 3.12 and its standard library:

```sh
python3.12 -B scripts/research_package.py --package research/encoded-minimum-root-prefix
```

The four commands report `PASS_ENCODED_MINIMUM_ROOT_PREFIX_ARITHMETIC`,
`PASS_ENCODED_MINIMUM_ROOT_PREFIX_ROOTS-DIRECT`,
`PASS_ENCODED_MINIMUM_ROOT_PREFIX_ROOTS-TWO` and
`PASS_ENCODED_MINIMUM_ROOT_PREFIX_ROOTS-SIX`. The runner then reports
`PASS_REGISTERED_RESEARCH_PACKAGE`. Its declared total cap is 1,200 seconds.
A Git-free export uses the same four commands in VERIFY.json.

The archive holds the exact historical source closure required by the
physical cohort. Its historical selected record is isolated inside the
archive. Loading it does not change the live selected frontier. The source
activation adapters remain inherited code; this package adds no runtime
patch or changed source execution body.

## Credit

Ali Romman, with substantial OpenAI Codex assistance. Apache-2.0. No subagents.
This uses the same assistant family as
[PR #5688](https://github.com/CrocSwap/integer-mult-bounds/pull/5688), which
supplied the numeric minimum, root field argument and one-axis theorem.
This is not an independent human audit of that theorem.

Jose Manuel's [PR #3385](https://github.com/CrocSwap/integer-mult-bounds/pull/3385)
supplied the physical controller, Count cohort, complete root and C2 fixtures.
`compute` is adapted from that source. commdata2338's
[PR #5515](https://github.com/CrocSwap/integer-mult-bounds/pull/5515)
supplied the exact reached-depth rule. Nick Petalas's
[PR #4865](https://github.com/CrocSwap/integer-mult-bounds/pull/4865)
and Sagar Thakrar's
[address refinement](https://github.com/CrocSwap/integer-mult-bounds/blob/df0137efd35e11b4445734bf612bdd4c7ebc330c/research/complex-root-address-refinement/PROOF.md)
supply the retained geometry and address context. All source notices and
nested predecessor archives remain intact.

## Open next questions

- Recompute a complete QQ16 or signed caller invoice at the changed core
  geometry. A shorter prefix alone does not establish an exponent gain.
- Review the all-size physical refinement against the pinned Count and
  native contracts. Reduced complete payloads do not discharge it.
