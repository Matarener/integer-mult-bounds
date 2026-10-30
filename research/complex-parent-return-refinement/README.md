# Conditional parent-return refinement for the physical complex controller

This package independently reviews the suspension/return boundary of Jose
Manuel's PR #3385, head `7e5a187214126d31afc241a8f89f4a652352b58c`.
Assuming a child returns its completed packet with primitive and bank scratch closed,
the original controller restores the suspended parent's dense tape words
and encoded descriptors, resumes at the saved next instruction, and replaces
only that child's target packet. The proof applies at arbitrary finite
recursion depth under the explicit premises in [PROOF.md](PROOF.md).

The target is a missing composition implication: correctness of a native
child endpoint alone does not prove that its physical caller preserves
the rest of the parent. This is a conditional source-relative refinement,
not a proof of the entire physical supplier or an outer multiplication
theorem. The original R480/T16 controller is the only implementation reviewed.

## Exact boundary and evidence

The retained source methods are `Machine.prepare_child`, `enter_child`,
`return_node`, and `Parking.park`/`restore`, with the actual bank, Tape and
Count implementation. The proof describes the encoded frame and shows that
restoring a frame consumes exactly its suffix while preserving every older
frame. Immutable finite source control reconstructs the saved group; the
saved instruction identifies the one returned target.

Preservation concerns each dense body word and its canonical head. An unused
role's erased marker is deliberately rearmed to `LEFT` before parking, and
allocated trailing blank capacity need not be byte-identical. Neither is
logical parent data. The saved-header guard checks a child instruction; it
does not authenticate arbitrary corruption of the owned stack.

The exact replay compares unchanged source transitions with independently
computed role and descriptor expectations. Reduced valid layouts make
nonzero spectator fields, spacing, owner selection and child ranks
observable. Opaque child results are declared endpoint hypotheses, not
Gaussian arithmetic evaluations. Separate dense-word tests exercise nested
parking independently of numerical payload size. `RESULT.json` records
the completed fixtures and failure controls.

The two admitted cuts have ranks one and two, respectively a private and
a bank target, 25 parked roles, and packets of 4,096 and 16,384 bits. Their
owner packets are checked against independent input slices before suspension.
Twelve nested seven-role codec frames exercise every admitted body symbol
and preserve every older prefix. The source-mutation controls alter the
child's trailing spectator length, returned target and saved PC; the last
deliberately selects another matching child instruction to distinguish
transition correctness from the source's header guard.

For the original selected inventory the proof counts 732 parked roles, so
a frame holding `B` body symbols has exactly `4B+733` encoded symbols.
That identity is not a complete time or space invoice.

The source's existing `check_machine.py` checks complete reduced Gaussian
endpoints, root borrows and scratch closure; its fixtures set front, before,
after and back spectator lengths to zero. This review adds intermediate
parent-state and continuation invariants rather than repeating its native
or arithmetic endpoint checks. PR #3442's adjacent native/helper audit and
the active T74 adaptation are outside this scope.

## Reproduction

From the repository root, using CPython 3.12:

```sh
python3 -B scripts/research_package.py --package research/complex-parent-return-refinement --check-only
python3.12 -B scripts/research_package.py --package research/complex-parent-return-refinement
python3 -B scripts/check_research_commit.py --package research/complex-parent-return-refinement --check-source-history
```

`VERIFY.json` registers normal and isolated/optimized/warnings-as-errors
runs. `SOURCES.json` pins the unchanged PR #3385 files to their original
commit and blobs, and retains the original cohort's current-main inputs.
Authentication of an inherited primitive is not an independent proof of
that primitive's contract. Frozen source tests are retained for coverage
comparison; no claim is made that their entire suite was executed here.

## Attribution and coordination

Jose Manuel (`jmbarrancoml`), with substantial OpenAI Codex assistance,
supplies PR #3385 and its source-relative interpreter. The original
`inputs/pr3385/SOURCES.json` preserves its predecessor ledger, including
the credited physical leaf, scalar, parking, normalization and ownership
protocols. All retained files are unchanged and preserve their notices.

This independent conditional argument and replay are by Sagar Thakrar,
with substantial OpenAI Codex assistance and separate same-session proof,
executable-control and adversarial-review agents. Same-session AI review
is not independent human acceptance or formal kernel checking. Apache-2.0.

Canonical investigation: [2238#19009893](https://github.com/CrocSwap/integer-mult-bounds/discussions/2238#discussioncomment-19009893),
following the released [review handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19008571).
The changed-T74 caller remains with its [active owner](https://github.com/CrocSwap/integer-mult-bounds/discussions/2612#discussioncomment-19009513).

## Open next questions and limits

The complete selected native/factory refinement, full production guard,
height and time invoice, normalized root and outer integer packing remain
outside this transition proof. No production O73/GL64 payload is executed;
no selected frontier or κ changes.

The active T74 adaptation has a different private inventory and schedule.
Transfer this invariant only after binding that implementation's exact
source and checking every premise; this package does not review it.

For the original controller, the next useful independent step is to connect
the proved return invariant to the exact owner/view direction and fixed-prime
factory contracts, then complete the root refinement with the inherited
precision and cost hypotheses still explicit.
