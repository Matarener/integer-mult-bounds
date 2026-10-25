# One P104 encoder fiber on axis 0 of U

**Partial audit. No new κ.** Selected κ stays `0.001672660197076918`.

## Scope and evidence

Original card: `p104-side-correction`, scope **changed**. The card asks for a
chronological correction program. This package does not write one.

[Discussion #1166 comment 19035716](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19035716)
asks for an inspection of the literal-index bridge or for one physical
consumer. PR #4125 did the bridge and left the events unread. Its open
question is to compare one frozen encoder fiber from the PR #3996 word bytes
with axis 0 of `U`, without calling that checker.

That comparison holds for bank `0`, column `0`:

- `U = [[I_8, B/2], [0, I_96]]`, with `B` rebuilt from the canonical fixture.
- The frozen builder `frozen/word_builder.py` is the PR #3996 vendored copy of
  the PR #3979 builder, SHA256
  `27bae82fe247fe49b8fc3b5efbd429e2c8c0ee8f56cc4ace748cbb681a5abacc`.
- Its encoder has 203008 events. The 576-event axis-0 program occurs once, at
  offset 41600. Interpreting that slice gives `U`, not `U^{-1}`, `U^t`, or
  `U^{-t}`.

The argument is in [PROOF.md](PROOF.md). Pins are in [SOURCES.json](SOURCES.json).
The checker in PR #3996 is not imported. The other fibers and both Gram words
are not replayed. Algebraic agreement is not a native-call price.

## Reproduce

From the repository root, Python 3.12:

```sh
python3.12 -B scripts/research_package.py --package research/p104-axis0-encoder-fiber
```

Expected markers: `PASS_P104_AXIS0_ENCODER_FIBER` and
`PASS_P104_AXIS0_ENCODER_FIBER_TESTS`.

## Open next questions

1. Do the other 103 bank-0 axis-0 fibers differ from column 0 only by the
   column index? That would cover the `U_r` sweep on one bank. First step:
   localize column 1 and compare it with column 0 after substituting the
   column. Nothing blocks that check; it was left out to keep this package to
   one column.
2. Does one repeated consumer of `(N-P) ⊗ M` pay less than rebuilding the
   uncoded Gram pair? PR #4125 already shows rational rank 10816 on each
   omitted side. First step: price one consumer of the exhibited inverse of
   `N-P` on a single bank. Blocked here because no consumer or complete
   allowance is named.

## Credit

The fixture and port order are the retained P104 native channel. The encoder
schedule and builder bytes are Chris R / Clear1nsight, PR #3979, head
`a8a1d744811cd7d1f9c43ec7ccbae85ef9695b61`, as vendored by ToikY, PR #3996,
head `b8dd4e04bf8490aca121abc7ba0e503651db6c97`. The index convention and the
one-fiber question are that PR and PR #4125. The slice search and the
interpreted comparison are new.

Prepared by unpaidmoon with Cursor Grok 4.7 assistance. No independent human
review. Apache-2.0.
