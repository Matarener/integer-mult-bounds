# Prove a six-ADD floor for isolated G20 bank exchanges under general binary bases

Scoped negative result: every isolated four-wire exchange with arbitrary
invertible two-wire bank bases needs at least six unit ADDs. The complete
36-endpoint shortest-length histogram is {6:2, 7:8, 8:24, 9:2}, with attaining
words for every endpoint. This answers a restricted part of PR5840's released
general-GL2 question; it does not claim a new kappa or a global CNOT minimum.

The pinned PR5840 controller has fourteen chain ADDs and four isolated
two-bank exchanges per side. The certificate proves its 76-ADD boundary pair
cannot be shortened while those chain instructions and component isolation
are retained, even granting arbitrary invertible endpoint bases. A joint
chain/exchange rewrite, cross-component gates, extra scratch, changed physical
tariffs or general bases before the entire boundary remain outside this result.

## Evidence and reproduction

```sh
python3 -B scripts/research_package.py --package research/g20-isolated-exchange-floor
```

Expected: normal and optimized runs print `PASS_G20_ISOLATED_EXCHANGE_FLOOR`.
The new generator exhausts GL(4,2) by row-addition BFS. The separate checker
classifies all 65536 binary matrices by column spans, checks all 20160
invertible states and 241920 right-addition edges, and verifies every attaining
word on all sixteen inputs. Five semantic controls reject false distance,
singular-state substitution, a deleted ADD, unequal source targets and a
changed exchange wire. Generation is deterministic and has an empty-queue
stopping rule; no candidate search failure is presented as an impossibility
theorem. Exact distances are certified in the finite declared model.

The package records normal/optimized registered verification, byte-exact
regeneration, and an offline exported replay. See VALIDATION.json for actual
commands and limits. No full caller/native replay, historical suite, Lean or
Docker is needed or claimed for this scalar-only result. Full physical
source descriptors, compiler, stock, precision/tape and analytic admission
remain separate; all five selected framework assumptions remain.

## Pins, coordination and credit

Base: `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority 8. OS seed 16,
BIT supplier track. Source PR5840: `6a043d0fc0199ee5b24c61f883f1943eaf6424be`,
controller blob `73fa9f40a032f11dabf357eba69066fcf9bf0a02`; exact SHA256 and
vendored bytes are in SOURCES.json. The source commit is pinned via its
retrieved controller and is not an offline Git-history dependency. The
selected conditional kappa remains .00310045.

Recent #1166 handoffs, released Discussion5804, live GL2/G20 PR and Discussion
searches were inspected. This extends PR5840's permutation normal form with
an exact general-basis isolated-module obstruction; it does not repeat its
four-role word fixed-point checks. The advance claim is retained locally
because `addDiscussionComment` was denied by the integration. Overlap coverage
is bounded and cannot cover unpublished work.

Credit Ali Romman's PR5840 construction and released question; PR5834,
PR5807/5828, PR5708/5671, ai-nanachi PR5512, Dugongue, ToikY and all retained
native/controller/compiler/BIT authors. Source notices are preserved. New
certificate, independent checker and scoped proof: Charan ., with substantial
OpenAI Codex assistance; no subagents or independent human/kernel acceptance.
Apache-2.0. No merge, closure or selected-frontier change.
