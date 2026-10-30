# One coordinate excludes helper469's invertible endpoint recoding

On the selected PR6030 word, helper469 cannot replace its chart3->593->713
interval with a direct MOVE3->713 using any finite rational receiver-only
ADD/SCALE programs in its two maximal endpoint windows. Every available donor
and the receiver's entry row have zero coefficient on public input1; the
required restored row has coefficient1/2. The feasible receiver multiplier set
is empty, including all nonzero rational multipliers. See [PROOF.md](PROOF.md)
and the exact [certificate](RESULT.json).

This answers the receiver-recoding case explicitly excluded by
[PR6069](https://github.com/CrocSwap/integer-mult-bounds/pull/6069), only for
helper469 events14357..14417. It does not repeat the predecessor's764-interval
census. The initial unchanged-receiver holder proposal was withdrawn because
PR6069 already covers it. Canonical investigation:
[discussion6078](https://github.com/CrocSwap/integer-mult-bounds/discussions/6078).

The verifier independently reconstructs the source rows with standard-library
rational arithmetic. It authenticates the selected word, verifies maximal
contact-free windows and source chart/lifetime semantics, gathers569 legal
timestamped generators, checks the complete receiver row, and compares the
committed deterministic certificate. No pending-source code is imported.
Independent controls replay input1 literally at every legal donor slot and exercise
a synthetic recoding positive plus zero-multiplier, wrong-version, wrong-chart,
changed-input-column and omitted-restoration negatives. Both scripts are
registered in normal and optimized Python. Only the prefix through the restoration boundary is replayed; no full native,
physical caller, selected invoice, Lean or Docker replay is performed.

## Reproduction

From the repository root, with Python3.12 or later and no dependencies:

```sh
python3.12 -B scripts/research_package.py --package research/p104-helper469-receiver-recoding
python3 -B scripts/check_research_commit.py --package research/p104-helper469-receiver-recoding --check-source-history
```

The direct verifier also works in a Git-free export containing the package
and its one declared word input. It writes no files:

```sh
python3 -B research/p104-helper469-receiver-recoding/verify.py
```

SOURCES.json pins the selected word, catalogue card and selected-result record
at main721c03822c421b7f7fcbb2598993b947c4d88419, priority8. The pending
PR6069 head and exact proof hash are contextual provenance in PROOF.md;
there is no hidden dependency on its local Git object. The parent investigation
checked live overlap before claiming this changed hypothesis; this does not
claim novelty against unpublished work or every historical closed PR.

## Open next questions

A further construction would have to change a donor program or another stated
boundary. Before opening a new search, identify a route delivering nonzero
input1 coefficient and a favorable complete cost allowance, including native,
productive-target, ordinary and restoration costs. No such route is supplied.
The structured question, relevance, first step and blocker are in TASK.json.
This is a stopping point for receiver-only recoding of this interval.

## Credit and limitations

Prepared for JoyboyBrian with substantial OpenAI Codex assistance; Apache-2.0.
Credit Jonathan Capalbo/PR6069 for the accumulated endpoint-span argument and
its explicit receiver-recoding boundary; Nick Petalas/PR6033 for the carrier
cost context; DreamingOfClouds/PR6030 for the selected word and inherited rung
removals; Ali Romman/PR5827 and all retained P104 authors for the scalar/native
construction. Sparse rational replay here is independently implemented.

This is an author-checked finite scalar exclusion and a mathematical argument
for its stated endpoint program class. It is not independent human scientific
acceptance, supplier admission, a new kappa, or the full multiplication theorem.
