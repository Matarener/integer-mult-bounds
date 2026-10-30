# Sharp 5/3 bounds for two binary helper-controller classes

This package gives a scoped negative result and a sharp binary construction.
It proves two distinct bounds on Q outputs per FULL call. The complete kappa
calculation does not improve.

- **Global support theorem:** commuting rank-three stage projectors, with each
  query term supported on its stage and of type `J_2(0) direct-sum [1]`, give
  at most `5*f/3` Q outputs from f FULL terms. The proof also permits D-only
  target coordinates and needs no call order.
- **Finite adaptive theorem:** a grammar with at most three live coordinates
  permits outside-support helper feedback and paid THIN queries. Its 94-state,
  10,035-edge graph has exact maximum `(Q outputs - THIN calls)/FULL = 5/3`.

Read [the proof and exact scope](PROOF.md),
[the integer potential and attaining word](CERTIFICATE.json), and
[the deterministic verification receipt](RESULT.json). The two theorems have
different hypotheses. The finite graph is not an exhaustive model of native
controllers. A three-FULL, five-output example attains both bounds; its full
binary polynomial endpoint is checked.

A later local-only
[catalyst extension](https://github.com/CrocSwap/integer-mult-bounds/discussions/4930#discussioncomment-19156336)
reports 188 states and 32,110 edges with the same 5/3 bound. It permits one
completed Q coordinate to remain live and credits the released 94-state
search. This package does not claim that broader result or that its own
finite grammar is the largest checked class.

## Reproduce

Python 3.12 or later and its standard library are sufficient. No native source,
network call, solver, or pending PR is a runtime dependency.

```sh
python3.12 -B scripts/research_package.py --package research/binary-helper-five-thirds
python3.12 -O -B research/binary-helper-five-thirds/verify.py
```

The first command ends with:

```text
PASS_REGISTERED_RESEARCH_PACKAGE research/binary-helper-five-thirds outcome=negative-result
```

The direct verifier prints `PASS_BINARY_HELPER_FIVE_THIRDS` in its JSON result
and compares the result with `RESULT.json`. It checks all 20,020 raw graph
transitions, the integer potential, the sharp binary polynomial word, and
28,224 two-term support cases. Meaningful perturbations must fail: a changed
potential, omitted state, unpaid THIN query, invalid native direction, and
wrong endpoint coefficient. Normal and optimized Python use explicit checks.

For a trusted source export, run the same direct verifier after extraction.
The registered runner needs Git history for the provenance pins. The direct
verifier does not. `--write` regenerates the receipt and is an authoring option.

## Scope and effect on kappa

The current publication base is `32890bc5de034ab8fc93ac88ead7279a6a416d04`.
The selected record and task card at that base are historical provenance in
[SOURCES.json](SOURCES.json). The assigned task changed from caller design to
publication of these scoped bounds; [TASK.json](TASK.json) records that change.

There is no new recursive invoice or claimed kappa. The operation ratio is
not a multiplication exponent. The source interface, fixed cover maps,
owned state, complex phases, recursive pricing, and supplier admission are
not checked here. No selected source or frontier file is changed. Earlier
floating-point tariff screens are excluded from the proof and verifier.

The original search also tested larger finite components, kernel packets,
D-only Gram factors, and fresh-axis cuts. Those bounded records are retained
in the coordinated closeout archive. They supply no general impossibility
claim and are not dependencies of this package.

## Open next questions

The one-catalyst finite extension already has a local result at the link
above; repeating that census is not the proposed next task. A useful next
question is whether a source-compatible packet outside the global support
hypothesis and outside both finite grammars can beat the bound. First give
its exact binary matrices and full source obligations. A favorable matrix
word would still need a signed complex identity and complete paid and target
accounting. This package does not reserve that work.

A separate review can check the component proof and the grammar-to-native
boundary. The program certifies the finite graph, not the physical scope of
all possible native words. These questions are also recorded in TASK.json.

## Credit

Cinna Davis / 1337isnot1337 supplied the earlier commuting-projector tangent
reduction and support-pair obstruction in the
[productive-controller proof](https://github.com/CrocSwap/integer-mult-bounds/blob/32890bc5de034ab8fc93ac88ead7279a6a416d04/research/productive-controller-basis-search/GLOBAL-PROOF.md).
The present rank-three component argument changes that two-coordinate
support model. The earlier package retains credit for the controller, native,
mixed-target, Clifford, and outer-recursion contributors.

Dillon's [PR #5388](https://github.com/CrocSwap/integer-mult-bounds/pull/5388)
motivated the early helper-observation interface. The physical source and
wrapper work remain separate from this abstract binary certificate. The
later catalyst extension is credited above as broader finite coverage.

New proof, code, and certificate by Ali Romman, with substantial OpenAI Codex
assistance. Parallel Codex workers checked the component argument and the
separation from the rank-four simple-graph model. This is not independent
human review. New work is under Apache-2.0.
