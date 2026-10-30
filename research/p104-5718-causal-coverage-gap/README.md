# The fixed #5719 causal certificate does not cover merged #5718

**Audit, not a new κ.** The selected conditional exponent stays
**0.00310045** (`#5599`). This package does not admit or reject the `#5718`
construction. It shows that one published coverage certificate does not apply
to that word.

## Result

Let `W0` be the authenticated PR5684 word used by
[PR #5719](https://github.com/CrocSwap/integer-mult-bounds/pull/5719), and let
`W1` be the authenticated word of merged
[PR #5718](https://github.com/CrocSwap/integer-mult-bounds/pull/5718).

The published `#5719` checker accepts `W0` and returns
`PASS_FIXED_CAUSAL_LEDGER_AND_TYPED_CONTACTS_ONLY`. On the bytes of `W1`,
renamed to the filename it requires, the same checker returns exit 3 and
`BINDING_UNRESOLVED`, with `scientific_falsifier` false and
`coverage_complete` false. The refusal is the pinned 106,613-byte cap. It is
not a scientific verdict on `#5718`.

An independent census of the same authenticated bytes then separates what
transfers from what does not.

| Premise named by the `#5719` certificate | On `W1` |
|---|---|
| Schema `p104-r22-reframe/1`, public count 743 | Schema `p104-terminal-main-split-short-cleanup/1`, public count 744, program length 25,546 |
| Strict frame chain, dimensions 0, 1, 3 at frames 3, 598, 396 | Same chain |
| Nine anchor events, each unique at its index | Four anchors occur nowhere. The other five occur once, at displacements 91, 91, 89, 90, and 92 |
| Sole field-712 write in `[823, 14983)` is `ADD 712,747,1` at frame 598 | The sole write there is `ADD 712,748,1` at frame 598, index 13,663 |
| Field-715 moves `3 → 598 → 396` | Those two moves are absent. The only move off frame 3 is `MOVE 715,3,396` at index 15,072 |
| No field-715 observer in `[823, 14983)` | Index 911 is `ADD 206,715,2` at frame 3 |
| One field-340 write in `[11202, 14983)`, the credited provenance `ADD` | Two writes: `ADD 340,344,1` at frame 70, index 11,260, and the credited `ADD` at index 11,293 |
| No field-340 write in the numeric interval `[14654, 14983)` | Still true, and not a transferred proof: index 14,654 and index 14,983 are different operations, the old read now lies inside the interval at 14,744, and the old cut lies at 15,075 |

The owned `INIT`/`CLEAR` frame sequences of roles 743 through 751 on `W0`
match roles 744 through 752 on `W1` exactly. Role 743 is unused on `W1`.
Role 747 on `W1` therefore reproduces role 746 on `W0`, not role 747. A
uniform label shift describes the lifetimes. It does not make the
certificate's field-747 claim true, and it does not restore the missing
715 chart path.

The frozen candidate of
[PR #5717](https://github.com/CrocSwap/integer-mult-bounds/pull/5717) is a
third word, SHA256
`9fd67dd89ed24a644257cd9aef06934ed4c6fbe0441804684a968868f2ef66a8`. Its
published binding names that hash. This package does not rerun the adapter,
so it does not confirm or refute the `#5718` author's report that the adapter
passed.

## Task and overlap

Base `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8. Card
`supplier-boundary-audit`, scope **refined** to the `#5718` delta named in
that card's first experiment.

This is item 4 of the eligible list below. The nearest packages are the
inputs: `research/p104-temporal-fixed-independent-audit` states in prose that
its certificate does not transfer, and `research/p104-two-boundary-helper-split`
is the successor. Neither package evaluates the old anchors on the new word.
`research/p104-caller-owned-interface` authenticates a different candidate.

Ordered eligible list for session r56, rebuilt on 2026-10-27 against
`de5ec2e7a6074068452f45b1a191b5c72832df4a`. Open handoffs from the 19 October
index (discussion comments 19030045, 19030047, 19030049, and 19030053) come
first and are dropped: the `(w, q, v_N)` consumer, the fresh T385 wrapper,
the L546 six-tape bill, and the single-ADD retiming class are already
delivered by this account or closed on main. No newer finite handoff index
replaced that list. The priority table is the revision-8 "Next bounded
decisions" table in `docs/research/current-priorities.md`. A row stays while
its stated next decision is still open. Catalogue cards not named by that
table were not reached. Dropped before the cut: work this account already
delivered, results closed on current main, and topics already on a fork
`cursor/*` branch.

1. Complex helpers (`p104-side-correction`, `coverage-law-change`): one
   uncovered helper group and causal cut with a complete caller bill.
2. BIT (`bit-helper-contract`): review the `#5679`/`#5708` chain before
   another G20 search.
3. New decoders and interfaces: one complete changed producer/consumer
   contract with an optimistic full signed bill.
4. **This package.** Supplier audit of merged `#5718` against the `#5719`
   certificate and the `#5717` candidate hash.
5. All-size audit (`uniform-transfer-audit`): one selected assumption at its
   actual caller.
6. Verification tooling (`replay-runtime`).

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 scripts/research_package.py --package research/p104-5718-causal-coverage-gap --check-only
python3 -B research/p104-5718-causal-coverage-gap/verify.py
python3.12 scripts/research_package.py --package research/p104-5718-causal-coverage-gap
```

`verify.py` prints

```text
PASS_P104_5718_CAUSAL_COVERAGE_GAP absent_anchors=4 displacements=91,91,89,90,92 observer_read=911 owned_shift=1 direct_715_move=15072 checker_binding_refusal=true no_new_kappa=true
```

The checker hashes the five live inputs before reading them. It reruns the
published `#5719` program on `W0` and on a temporary copy of `W1`. The
injection control replaces one event of `W0` in memory: a destination-only
field-715 `ADD` stays allowed, and `ADD 206,715,2` at index 900 is the only
reported observer. A one-frame change to the shifted role-748 birth is
rejected by the lifetime comparison.

Not run: the `#5718` scientific replay, the `#5717` adapter, the `#5599`
caller replay, Lean, and Docker.

## Open next questions

1. Does a rebased ledger, using the direct field-715 move from frame 3 to
   frame 396 and classifying the extra field-340 write at index 11260, hold
   on `W1`? The old certificate cannot be that ledger. First write a new
   subject from the anchors recorded here and scan `W1` alone. Nothing here
   prices that scan or the `#5718` caller.
2. Does the published `#5717` adapter accept `W1` under an explicit `+1`
   label map? The frame sequences match that shift, and the packaged
   candidate hash does not. First point the adapter at `W1` and record the
   map it uses. Its entry point currently authenticates a different word.

## Credit

The fixed subject and checker are from Chris R / Clear1nsight,
`research/p104-temporal-fixed-independent-audit`, following Ali Romman's
PR5713 and Joel Pulikkan / GamingPuzzled's PR5684 word. The successor word is
from flyingviper, `research/p104-two-boundary-helper-split`. The third
candidate hash is from `research/p104-caller-owned-interface`. No file from
those packages is modified.

Prepared by unpaidmoon with substantial Cursor Grok assistance. Apache-2.0.
