# Independent review of the staged544 new-gap reduction

**Negative result.** No new κ. The selected conditional κ stays
`0.001672660197076918`. This is an audit of one reduction, not a supplier
and not a universal two-ADD obstruction.

## Scope and evidence

PR #3942 certifies that a radius-one first ADD, followed by any legal second
ADD, does not improve the raw rank moment on either pinned PR #3734 provider.
Its released handoff asks for an independent challenge of the
interaction/new-gap reduction and of exhaustive first-frame coverage.
`verify.py` does not import `search.py`.

On both providers the checker establishes:

- Every radius-one first-move interval has quotient rank at most 3. A closed
  quotient basis spans the upper frame, and a separate one-vector walk finds
  exactly the Gaussian number of intermediate subspaces. There are 1292
  intervals: 1078, 186, 3 and 25 of quotient ranks 0, 1, 2 and 3.
- Every fixed-frame adjacent pair that shares a register has equal declared
  frames. The 181 unequal shared pairs are nested on the trace: the later
  gate's incoming frame is the earlier gate's frame, so they are not
  fixed-frame swaps.
- For every scalar-legal third ADD at the swapped interior cut:
  - if it meets both swapped gates, its price list equals a separately coded
    bridge formula;
  - if it meets only the right gate, only the left gate, or neither, that
    price equals the original-word price at the cut named in PROOF.md §3
    (after both, before both, or the same cut).
- The bridge rows that are not identically zero are exactly the four published
  restore rows `(section=restore, pair=182/191/192/193, third=178, dimension=8)`
  with delta `(0, 2, -1, 0, ...)`. Each passes the predecessor nonnegative
  curvature certificate, so none is a raw-moment saving.
- Counts tied to the published census: 4709 fixed pairs, 14966 scalar-legal
  bridge gates, 14693 bridge dimensions.

One published nonzero row was recomputed from `apply_move` plus a fresh trace.
Replacing the predicted cut of an only-left gate by the interior cut changes
the price, so the localisation test is not vacuous. Two disjoint ADDs cross
exactly when their endpoint pairs are disjoint; that is the interaction
reduction's crossing hypothesis, checked as algebra on `crosses`, not as the
11.9-million-row variable census.

The variable-frame second-move census and same-gate collapse are not replayed.
Longer first displacements, illegal intermediate words, and changed native
boundaries stay outside PR #3942 and outside this review.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/staged544-two-add-reduction-review/verify.py
python3.12 -B scripts/research_package.py --package research/staged544-two-add-reduction-review
```

Expected marker:

```text
PASS_STAGED544_TWO_ADD_GAP_REVIEW
```

The two provider words and `vendor/retiming.py` are the bytes of PR #3942 at
`1416f8cd6bfb2f2eb9aa5cc22f0388a85fdbac91`. `verify.py` checks their SHA256
before use. Recorded local runtime is about 30 seconds. Not run: the
predecessor's 11.9-million-row variable census, Lean, Docker, and the selected
cold replay.

## Open next questions

1. **Disjoint second moves.** Prove or price the section-2 claim that a second
   ADD on registers missed by the first moved gate has delta equal to its
   original single-move delta. The crossing algebra is checked here; the
   summed histograms are not. The blocker is the size of that census.
2. **Same-gate collapse.** Show that choosing the moved ADD again undoes every
   radius-one first move, not only a sample. A failed undo would be a word the
   reduction never prices.

## Credit

The reduction, trace, and both provider words are Chris R / Clear1nsight, PR
#3942, with the PR #3886 single-move rules and the PR #3734 providers from
dataisfire. Jeremy Kothe's retiming line, Dugongue's rank-two exchange, and
the frame-contract auditors credited in that package are unchanged. New review
code by unpaidmoon, with substantial assistance from Cursor Grok 4.7.
Apache-2.0. No independent human or formal-kernel review is claimed.
