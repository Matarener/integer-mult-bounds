# Independent audit of the first asynchronous helper hub

This checks one temporal implication in Ali Romman's PR #5786 at
`6b936acd68a7e0f9062037900f0fe9bc4b6fdd25`, on its exact PR #5774 source
`7d6ec0cdef31d0c37b7d2563e709979caa0d5eae`. It answers the first-step review
request in [Discussion #5600](https://github.com/CrocSwap/integer-mult-bounds/discussions/5600#discussioncomment-19202381).
The [audit claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/5600#discussioncomment-19203981) distinguishes this from the active different-output-owner construction. The new result is an independently implemented source-data audit and quantified
scalar implication, not a new construction or conditional bound.

The fixed object is pivot 696, frame 1031, cut time2=27044. Collection reads
field 696 at 27026. Four injections read the retained difference buffer into
696/697 at 27044, owned 770 at 27501, and 699 at 27516. The odd time is inside
actual source query 13750; event numbers apply only to this frozen source.

The complete temporal row is `c=e696^T`, and the complete delivery column is
`d=e696+e697+e699+e709+e733+2e133`, with `c*d=1`. Role 133 is an eligible
helper hole: main roles are derived from the actual live ports and their
offset 112 partners, rather than treating every role below 224 as main.
The independent oracle checks all 789 axes and establishes commutation of the
actual boundary basis with the literal source endpoint. Individual injection
contributions need not have helper-only support; their exact sum does.

The actual owned query is `MOVE 770:591->597`. Frame dimensions are 8, 5, 1
through the inserted frame 1031. Its descending subspaces give paid ranks
`7 -> (3,4)`, so the **access-query delta only** is `H3+H4-H7`, where
`Hr=r^t`. The helper target splits into ranks 5 and 4. The full step invoice
also owes boundary bases, scalar swaps, owned initialization/erasure and
routing. This package does not price that full invoice or claim a gain.

[PROOF.md](PROOF.md) states the quantified hypotheses and the two-swap
difference-buffer argument. The buffer contains `z-x_h` before its charged
CLEAR; it is not asserted to vanish by reversible scalar algebra. INIT/CLEAR
retain the inherited owned-erasure assumption. A static pairing alone is not
a physical or chronological construction.

## Reproduction and evidence

Python 3.12 and the standard library suffice. The two implementations import
no predecessor implementation and do not import each other.

```sh
python3.12 -I -W error -B research/p104-async-first-hub-audit/verify.py
python3.12 -I -O -W error -B research/p104-async-first-hub-audit/oracle.py
python3.12 -B scripts/research_package.py --package research/p104-async-first-hub-audit
```

`verify.py` uses complete rational prefix/suffix histories and an independently emitted first-step scalar/frame witness, with frame/lifetime checks and meaningful rejection controls. `oracle.py` uses
a reversed read functional and four separate forward perturbations, then
checks the necessary source identity columns and pivot output row. See
[RESULT.json](RESULT.json) and [ORACLE.json](ORACLE.json) for exact receipts.
The literal first-split witness checks all 625,681 endpoint positions on 791 formal inputs, 25 owned lifetimes and a peak of 12 live owned fields. It explicitly emits both swaps, buffer INIT/CLEAR and the query subdivision. It checks all 622,521 original source endpoint positions as a separate prerequisite. Seven controls reject omitted collection, owned injection, causal order, source binding, paid access, new buffer CLEAR and a swap sign. Default execution compares the entire canonical JSON RESULT/ORACLE receipts, including boolean/number type distinctions; `verify.py --emit` is an explicit candidate-generation mode and writes no files.

The package vendors only the 122,348-byte source word and the 3,840-byte PLAN,
not a copy of either predecessor implementation. Both raw SHA256 and Git
blob identifiers are authenticated independently; the decoded word also has
a canonical JSON SHA256. [SOURCES.json](SOURCES.json) records exact origin
commits, paths and byte bindings. Generic provenance rows bind the main task
catalogue and selected context. The vendored-data checks do not establish
publication ancestry or imply that the predecessor's complete export ran.

Main was refreshed to `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority 8.
[Task](TASK.json) records the explicit change from a formalization card to this
finite exact source-binding audit. No Lean build was run. The exact selected-source inputs were materialized and the current baseline passed `PASS_RESEARCH_BASELINE_BINDINGS_ONLY` on Python 3.12.14. This authenticates selected source bindings and metadata only; no native selected replay or supplier admission follows.

## Open next questions

- Independently check native maps and absolute phases for this subdivision,
  and bind all scalar/buffer/route costs to the full first-step invoice.
  Temporal equality and ranks alone do not prove that binding.
- Then audit steps 2/3 on their own exact input words; source event indices
  change after each construction. The complete caller, ordinary compiler,
  precision and analytic framework assumptions remain outside this audit.

The structured next question and its blockers are in [TASK.json](TASK.json).
No all-size theorem, supplier admission, new kappa or frontier change follows.

## Credit

Ali Romman, with OpenAI Codex assistance, supplied the asynchronous
construction, plans and retained-copy source word. Retain flyingviper's
boundary bases, Joel Pulikkan/GamingPuzzled's basis work and every native,
controller, compiler and BIT predecessor in [NOTICE](NOTICE). New audit and
proof: ToikY with substantial OpenAI Codex assistance, using separate bounded
implementation and read-only proof/review contexts. Apache-2.0.
