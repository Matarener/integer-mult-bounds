# R437 streamed leaf ownership under the canonical caller's allocator

The complete #5055 streamed leaf/XOR interval can run under one already
installed caller scratch pool with an enlarged reserve and supplied persistent
roles, preserve its five persistent producer Counts,
and deliver the full result through the unchanged `Machine.commit`. This
closes a local allocation/commit part of [#5187's caller-ownership
handoff](https://github.com/CrocSwap/integer-mult-bounds/discussions/4682#discussioncomment-19144606).
It is a **partial construction with a source-relative ownership lemma**.
Full recursive dispatch, source traffic and supplier admission remain open.

The standalone #5187 adapter rejects if placed directly inside `Machine.run`'s
allocation scope: it tries to allocate its full-output Tape while the caller
forbids new physical tapes. A blanket empty-pool check at every prefix would
also reject the five live producer Counts. These are documented boundary
mismatches, not counterexamples to #5187's standalone theorem.

[adapter.py](adapter.py) executes the unchanged #5055 producer/consumer code
objects with supplied allocation bindings. It borrows four persistent physical
roles (full output, saved prefix, current prefix and reader), uses the canonical
installed pool for all temporary tapes, and preserves the exact five producer
lease identities across each local consumer. Every remaining lease retires
before macro return. The returned raw output is explicitly cleared after the
original `Machine.commit`, which does not itself retire a raw result.

[PROOF.md](PROOF.md) gives the invariant, remaining resident ledger and exact
commit/retirement tariff. Conditional on #5187's inherited source lifetime bound,
a sufficient scratch capacity is **q²+141**. This is 13 above the unchanged
Machine constructor's q²+128; those roles and the four supplied persistent roles
must be provided and charged by a future dispatch integration. The pool backing
bound includes the producer's `bit_length(N)` term. No source count, paid
histogram, reverse coefficient, κ or selected record is changed.

## Evidence

The complete q=3, w=2, dimension=2 fixture executes all 243 physical prefixes,
including the duplicate old prefix, and all 19,683 source/dirty-target bits.
All 1,458 actual coefficient callbacks remain. Output equals both the retained
eager packet/XOR execution and the predecessor's independent permutation oracle.
No numerical Word is decoded to drive the tested runtime.

| Checked boundary | Result |
|---|---:|
| Canonical scratch inventory | 150 physical tapes |
| Observed peak live leases (not a capacity proof) | 32 |
| Acquisitions, all retired | 261,492 |
| Producer lease identities preserved at each prefix | 5 |
| Pool backing after first / last prefix | 1,289 / 1,290 cells |
| Full output / canonical destination backing | 19,684 cells each |
| New rejecting controls | 11 |
| Literal commit/retirement tariff cases | 289 |
| Added record-cell actions before commit | 403,060 |

The controls include borrowed-output and scratch aliases, dirty persistent
roles, an uninstalled or under-reserved pool, a live lease at the actual CALL
guard, the original standalone mismatch, a premature global-empty guard,
omitted retirement and replacement of a producer lease at the same slot.
The original complete fixture and its seven source/payload controls are kept;
the harness changes exactly one module-binding assignment and deletes no checks.
Failure-only callback runs receive a separate checker counter with otherwise
identical function code and closure values. They do not contribute to the
successful callback count or its ownership receipt.

[RESULT.json](RESULT.json) is the deterministic receipt. A separate complete
fixture comparison counts every touched record tape: the original streamed
interval uses 45,830,745 record-cell actions and the installed-pool interval
uses 46,233,805, exactly attaining the 403,060 surcharge bound. Index and residue
Word traffic agree componentwise. This is a finite local cost comparison;
the universal source traffic T and the production caller bill remain open.
The additional owned-record meter covers only the named owned roles, including
commit, and is labelled separately. The exact commit formula is derived in the
proof and checked for every 0<=output length, previous destination length<=16.

## Reproduce

Python 3.12; standard library only, serial execution. From repository root:

```sh
python3 -B scripts/research_package.py --package research/r437-canonical-workspace --check-only
python3 -B scripts/research_package.py --package research/r437-canonical-workspace
```

The registered hook runs normal and optimized modes, each with a 180-second
limit. Both print `PASS_R437_CANONICAL_WORKSPACE`. Direct commands also work in
a committed export with the declared inputs:

```sh
python3 -I -W error -B research/r437-canonical-workspace/verify.py
python3 -I -W error -O -B research/r437-canonical-workspace/verify.py
```

`--write` regenerates the receipt deliberately. [SOURCES.json](SOURCES.json)
pins 418 live files plus catalogue/selected provenance. The predecessor loader
uses its retained historical selected record in a temporary source projection;
the current selected record is never rewritten. Normal/optimized and exported
replay status is recorded in the task metadata and submission validation.

Base main: `32890bc5de034ab8fc93ac88ead7279a6a416d04`, priority revision 7.
The claim is in discussion #4682. [TASK.json](TASK.json) narrows the
`r437-carrier-integration` card to this ownership implication.

## Open next questions

1. **Install one actual source-bound dispatch interval.** Identify four
   available persistent canonical roles and provide the additional scratch
   reserve (or prove a smaller sufficient reserve). Then join actual producer,
   Program, leaf and destination scheduling to this adapter, with all input,
   output, producer, parked-parent and terminal-marker residents charged.
   This matters because an exercised allocation/commit API is not a full
   `Machine.run`. The actual schedule and role availability are the blockers.
2. **Price the unchanged source traffic T.** Begin with one source-bound leaf
   and its coefficient history, then add the producer and exact commit tariff.
   The local pooling surcharge is available, but the all-parameter callback,
   Context/codebook and full-node traffic are not established here.

No admitted root, full node or recursive return is executed. The actual CALL
is tested only on its early live-lease rejection path. The dimension-64
SOURCE87 calibration, full high-prefix domain, original q127 instance,
precision/stock, native/compiler/ordinary/outer admission and Lean are not
replayed. The source lifetime/extent theorem remains an explicit inherited
premise. Arbitrary-exception rollback and a full fixed-control lowering are
outside scope. No independent human or formal-kernel review is claimed.

## Credit

Prepared for commdata2338 (@commdata2338), with substantial OpenAI Codex assistance.
New adapter, boundary proof, checker and note are Apache-2.0.

- Krzysztof Wójt, [#5187](https://github.com/CrocSwap/integer-mult-bounds/pull/5187),
  head `f7c4d65b11e658fa093f0bac9f5f4b8ca346a4b8`: standalone workspace,
  source lifetime/backing premise and the explicit caller handoff.
- JoyboyBrian, [#5055](https://github.com/CrocSwap/integer-mult-bounds/pull/5055),
  final source `08a8be5e1387156446394694f768937d15f0e1ba`, and #4981: complete
  streaming, prefix fusion, dirty-payload fixtures and independent oracles.
- Jose Manuel / jmbarrancoml: physical caller, ScratchPool, source-role bound,
  canonical commit and CALL guards; David Arias: logical caller. The relevant
  caller source commit is `61f4d7ce898fcb64e89c55519f5b3a340e8e7368`.
- Chris R / Clear1nsight, #4067/#4176: paid R437 carrier and integration;
  unpaidmoon, #4147: reverse coefficient; ai-nanachi, Rohan Arun, Ali Romman,
  Sagar Thakrar, Nick Petalas, ywz65 and the retained source/geometry/hosting
  lineage. This account's #3223 audited a different NODE/peel/return boundary.

All frozen source notices remain intact. Substantial OpenAI Codex assistance
covered derivation, implementation, checking and writing.
