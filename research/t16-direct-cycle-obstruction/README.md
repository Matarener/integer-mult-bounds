# Direct four-bin cycles cannot lower PR3359's idle moment

An exact integer certificate rules out a cheaper direct four-helper rotation
across four bins on [PR3359](https://github.com/CrocSwap/integer-mult-bounds/pull/3359),
head `3bdc260e996fd3a94dcb7560b68f2c61d2253d80`. It proves the stronger statement
for any permutation with exactly one original helper leaving and entering each
affected bin, at every concave cost on ranks 0 through 48, including rank-zero
bins. The recursive child cost is zero at rank zero. There is no new kappa claim.

The favorable relaxation drops family and active-pair conflicts, while retaining
actual event windows, original widths and bin capacities. All 9,284,615 integer
hinge inequalities hold on the complete 720-state, 197,545-edge graph.
[PROOF.md](PROOF.md) derives the concave-cost conclusion from those inequalities.
This replaces a bounded search failure with an independently replayable scoped
obstruction.

The statement does not cover multiple original departures or arrivals at one
bin. The tests independently replay the supplied neutral pair and triple in
[PR3366](https://github.com/CrocSwap/integer-mult-bounds/pull/3366). Its shared bin loses two width-8 helpers and gains widths 7 and 9,
so the improvement is outside this theorem. See the proof's boundary control.
We do not repeat that search, pricing or full admission.

## Reproduce

From the repository root, with standard-library Python 3.12:

```sh
python3.12 -Werror -B scripts/research_package.py --package research/t16-direct-cycle-obstruction
python3.12 -Werror -B research/t16-direct-cycle-obstruction/verify.py
python3.12 -O -Werror -B research/t16-direct-cycle-obstruction/test_verify.py
```

Expected: `PASS_T16_DIRECT_CYCLE_OBSTRUCTION edges=197545 inequalities=9284615`,
six passing behavioral groups normally and optimized, and
`PASS_REGISTERED_RESEARCH_PACKAGE` from the launcher. Set `TMPDIR` to a
session-owned output directory to contain launcher/control scratch. The direct
verifier writes nothing unless explicitly passed `--write` to regenerate its
result. No solver, C++ toolchain, pending Git object or network call is needed.

`predecessor.patch.json` reconstructs the complete PR3359 payload from canonical
PR2169 data with 217 checked preimages. Its canonical digest matches the retained
original result. [SOURCE-EXPORT.json](SOURCE-EXPORT.json) binds those exports;
[SOURCES.json](SOURCES.json) pins all seven canonical runtime inputs. The
independent original auditor checks all 69,120 starting roles and rebuilds the
actual source windows before the graph is formed. [RESULT.json](RESULT.json)
contains the exact graph, source and potential digests and complete audit.

## Validation and limits

The certificate uses exact integers and a written concavity argument. Controls
reject a missing hinge, reordered states, zeroed or noninteger potentials,
changed source bytes, wrong widths and wrong family identities. A separate
uncompressed synthetic calculation checks every hinge's edge maximum. The
concurrent fixed five-role witness checks the theorem's actual boundary.

This is not a full supplier or multiplication theorem. The selected result is
unchanged. No fresh complete eleven-stage invoice/native replay, new root,
packing optimum, formal-kernel verification or independent human review is
claimed. A new owner map requires renewed source binding and a new certificate.
The selected inherited all-size/compiler, common-label/mutable-source, hosting,
precision/tape, exact-recovery, analytic and BIT premises are not resolved here.

## Open next questions

Interacting moves can cross this boundary. The concurrent five-role control is
one concrete example; its complete pricing and admission belong to its own
contribution. A useful next question is whether the same hinge potentials, or a
new set, hold on a named successor map after that interaction. First reconstruct
that exact payload, then run this graph construction and certificate check.
Failure only identifies an unresolved inequality, not an improving legal move.
Do not start another seed search over direct PR3359 rotations. Structured scope
and the next test are in [TASK.json](TASK.json).

## Credit

Nick Petalas. Apache-2.0. Credit Pierre/hexapode for PR3359's map and composed
cycles, Nick Petalas for PR3354/PR3338 and the concurrent fixed five-role witness,
Philippe Van Velzen for PR2169, Josie Elliston for the independent owner/window
auditor, Hao Yan for the T16 controller, Gonzalo Mier, George Lydakis, Rohan Arun,
Jeremy Kothe and the retained selected-source lineage. Original predecessor
proof, README and result are preserved with their notices.
