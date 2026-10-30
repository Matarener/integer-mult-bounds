# Present-head flag 1: the basis head reaches the target only after its last update

**Scoped obstruction. No new exponent.**

Open [#3349](https://github.com/CrocSwap/integer-mult-bounds/pull/3349) shows the
basis head is in the target final on only four of the 208 matched flags:
`(0, 1, 9, 43)`. Open [#3443](https://github.com/CrocSwap/integer-mult-bounds/pull/3443)
pins flag 9. This package pins flag 1 (`X0` → `Y7`, basis head `232`).

On the published 4,058-event word, `Y7` holds `[]`, `[95]` and `[95, 486]` before
its last event. None of these lists `232`, and none spans it over GF(2). The head
enters `Y7` only in the after-frame of the terminal transport at event 3473. All
six adds into `Y7` (events 19 through 2797) run in charts that exclude the head
direction. No event names both `X0` and `Y7`, and neither frame is restored.

The source side behaves differently from what a literal reading suggests. `X0`
starts at `[232]`, and its first transport (event 591) lists
`[8, 32, 64, 128, 256]`. That drops `232` from the list but not from the span,
because `232 = 8 ^ 32 ^ 64 ^ 128`. Every one of the 22 `X0` annotations spans the
head. The native channel's frames are binary subspaces with nested transports, so
the span reading is the chart-independent one.

Both endpoints first host the head direction together at event 3473, and `Y7` has
no event after that. The published channel therefore never updates or touches the
matched target while both endpoints host the basis-head direction. Chronological
dirty restoration along co-hosted basis-head geometry is unavailable on this
word. In span, the obstruction is entirely on the target side.

Selected κ stays 0.001672660197076918. Details and limits are in
[PROOF.md](PROOF.md).

## Reproduce

```sh
python3.12 -I -B research/p104-present-head-flag1-audit/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-flag1-audit/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-flag1-audit/independent.py
python3.12 -I -O -Werror -B research/p104-present-head-flag1-audit/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-present-head-flag1-audit
```

`verify.py` is read-only. Admission goes through `need()` and still fires under
`-O`. `test_package.py` corrupts temporary copies of the certificate and of one
pinned input and checks that both scanners reject them under `-O`.

## Credit

Credit Nick Petalas / #2981 for the flag matching, the reviewed #1991 channel
lineage for the witness, jwr404 / #3242 for the schedule receipt, #3349 for the
present-head census, #3443 for the flag-9 method, and #3392 for the absent-head
counterpart. Prepared by Wentao Li with substantial AI assistance.

## Open next questions

1. Can a changed schedule put `232` into `Y7`'s span before its last add (event
   2797) while `X0` is still live, and what does that cost against the channel
   bill?
2. Do flags 9 and 43 follow the same pattern in span, with the source keeping the
   head direction and the target gaining it only at its terminal transport? If
   so, #3443's literal source drop is a chart change, and the present-head
   obstruction is a target-side property.

[TASK.json](TASK.json) gives first steps and blockers for both.
