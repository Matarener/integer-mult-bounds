# An exact ten-H1 floor for one backward helper block

The proposed `H1 + H1 -> H2` saving cannot be realized inside one precise
eight-field block of the selected backward provider. Every exact replacement
in the model below needs **ten rank-one climbs**, and the existing block
attains that bill. This is a local obstruction with an attaining construction;
it does not improve kappa or exclude a larger redesign.

The block is the dependency closure of roles `{19,300,301}` within zero-based
provider events **[9044,9116)**. It has eight fields and 28 relevant events:
ten H1 climbs, sixteen ADDs and two SCALEs. Intervening events on disjoint
fields remain unchanged.

## Result and scope

Allow any finite rational ADD/SCALE factorization, including temporary basis
changes and arbitrary intermediate binary subspaces. Keep the eight fields,
arbitrary entering values, entry/exit frames and monotone climbs. No new warp,
auxiliary field, descent, chart-changing exchange, cross-column conversion or
changed output contract is allowed.

Six fields start at lines and end at planes, requiring six H1 climbs. Fields
300 and 301 start at frame zero and end at distinct planes. If either jumped
directly to its exit plane, only the other zero-frame field could carry its
initial two-dimensional information to the other exit planes. Those outputs
require rank-two dependence, while one carrier supplies rank at most one.
Both helpers therefore need two H1 climbs: the minimum is `6 + 2 + 2 = 10`
for every `0 < t < 1`. See [the proof](PROOF.md).

This permits a changed ADD graph, beyond the fixed-word reorder and adjacent
swap searches in [PR #5465](https://github.com/CrocSwap/integer-mult-bounds/pull/5465).
Its R13 sections 3–4 motivate the experiment, but illustrate the forward word.
The forward x19-to-plane430 witness is zero backward; this package uses the
actual backward tape and two different rank witnesses.

Base: canonical main `32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority 7.
Selected conditional kappa remains `0.003027288235`. The provider's decompressed
source hash binds the canonical frames. [SOURCES.json](SOURCES.json) pins exact
inputs at the canonical base. The pending [#5465 R13 note](https://github.com/GamingPuzzled/integer-mult-bounds/blob/b123ff44a211b9fc96b9f8fd1538e9965a95b34e/research/frontier-word-reorder-ceilings/r13-reorder/README.md)
is a motivation/overlap reference, not a proof premise or replay input. Its
SHA256 is `f5da8c86df033f0697d305ac4a9798ba60ab1a765e5701648560628a36ad1f62`;
no unmerged Git object is required for verification.
[TASK.json](TASK.json) records the narrowed historical card and stopping rule;
the card's 5% supplier-expansion gate is not claimed satisfied.

## Reproduction and evidence

Python 3.12 and the standard library suffice. From the repository root:

```sh
python3 -B scripts/research_package.py --package research/helper300-eight-field-floor
```

The primary verifier reconstructs the local operator and tests the source-bound
rank-cut hypotheses. The separately authored source checker reconstructs the
matrix without importing the primary verifier. Both include semantic failure
controls; normal and optimized executions are registered. The primary checker
also evaluates the inherited forward window as an orientation control; the
claimed selected-provider result is backward. It compares recomputed evidence
with `RESULT.json`; use `verify.py --write-result` only to regenerate that file. Exact finite checks
support the written arbitrary-factorization proof; they are not a program
enumeration or proof-assistant certificate.

Physical all-width interpretation is conditional on the inherited native chart
contract. No complete provider/caller replay, new phase construction, compiler
funding, Lean audit, independent human review or new exponent is claimed.
Restoring the block's rows and charts preserves the unchanged continuation,
including later cached-centre checkpoints, by composition.

The [canonical investigation](https://github.com/CrocSwap/integer-mult-bounds/discussions/5470)
records the claim and handoff. Targeted live PR and Discussion searches found
no matching submitted scope; hidden comments and unpublished work are outside
that coverage. The selected source-binding baseline passed; historical ceiling
arithmetic is not transferred to the current supplier.

## Open next questions

1. Extending the same seed through `[9044,9137)` yields twenty fields. Extract
   its entry/exit geometry and rank cuts before synthesis. It could expose
   another zero-frame carrier or useful changed output plane; its full bill
   and protected contacts remain to be checked.
2. For a changed transport or auxiliary field, specify the complete producer
   and consumer contract and price it first. One extra H1 already costs more
   than the proposed single merge saves, so a profitable escape needs another
   compensating saving. No such transport or larger construction is supplied.

Structured questions and blockers are in [TASK.json](TASK.json).

## Credit

Credit Cao Yifan's #4610 native word, Dillon Amburgey's #5402 coupled provider,
Ali Romman's cached-centre relations, Chris R/Clear1nsight's #5413 completion
and source validation, GamingPuzzled's #5465 bottleneck analysis, and the
retained native/compiler lineage. Historical helper-basis screens by tomdif
on the older #1286 provider are related predecessors, not the same local
obstruction. The cut-rank argument uses elementary linear algebra; no priority
claim is made for that general method.

Prepared by **apoursh**, with substantial OpenAI Codex assistance from one
coordinator and three workers for synthesis, mathematical audit, and independent
source reconstruction. AI-worker separation is not independent human review.
New work is Apache-2.0; predecessor notices are retained.
