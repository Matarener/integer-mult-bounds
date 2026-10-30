# Present-head flag 0: the coefficient-cascade target hosts the head only after its last update

**Scoped obstruction. No new exponent.**

Open [#3349](https://github.com/CrocSwap/integer-mult-bounds/pull/3349) shows the
basis head is in the target final on only four of the 208 matched flags:
`(0, 1, 9, 43)`. Open [#3451](https://github.com/CrocSwap/integer-mult-bounds/pull/3451)
pins flag 1 and leaves flag 0 to the coefficient cascade on `Y34`. This package
pins flag 0 (`X0` → `Y34`, basis head `232`) with both literal-frame and GF(2)-span
chronology.

On the published 4,058-event word, `Y34` never lists or spans `232` before its
last event. The head enters `Y34` only in the after-frame of the terminal
transport at event 3500. All fifteen adds into `Y34` (events 129 through 3369)
run in charts that exclude the head direction. No event names both `X0` and
`Y34`, and neither frame is restored.

The source side behaves differently from what a literal reading suggests. `X0`
starts at `[232]`, and its first transport (event 591) lists
`[8, 32, 64, 128, 256]`. That drops `232` from the list but not from the span,
because `232 = 8 ^ 32 ^ 64 ^ 128`. Every one of the 22 `X0` annotations spans the
head. At event 3500, `X0` already sits on the coordinate basis, which does not
list `232`, but still spans it. The native channel's frames are binary subspaces
with nested transports, so the span reading is the chart-independent one.

Both endpoints first host the head direction together at event 3500, and `Y34`
has no event after that. The published channel therefore never updates or touches
the matched target while both endpoints host the basis-head direction.
Chronological dirty restoration along co-hosted basis-head geometry is
unavailable on this word ahead of the published `I-G/2` tail add. In span, the
obstruction is entirely on the target side.

Selected κ stays 0.001672660197076918. Details and limits are in
[PROOF.md](PROOF.md).

## Reproduce

```sh
python3.12 -I -B research/p104-present-head-flag0-audit/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-flag0-audit/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-flag0-audit/independent.py
python3.12 -I -O -Werror -B research/p104-present-head-flag0-audit/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-present-head-flag0-audit
```

`verify.py` is read-only. Admission goes through `need()` and still fires under
`-O`. `test_package.py` corrupts temporary copies of the certificate and of one
pinned input and checks that both scanners reject them under `-O`.

## Credit

Credit Nick Petalas / #2981 for the flag matching, the reviewed #1991 channel
lineage for the witness, jwr404 / #3242 for the schedule receipt, #3349 for the
present-head census, #3451 for the flag-1 span method, #3443/#3456 for the
other present-head chronologies, #3392 for the absent-head counterpart, and
open #3575 for the literal flag-0 relay cut that this package extends with the
span reading. Prepared by Wentao Li with substantial AI assistance.

## Open next questions

1. Can a changed schedule put `232` into `Y34`'s span before its last add (event
   3369) while `X0` is still live, and what does that cost against the channel
   bill ahead of the published `I-G/2` tail add at event 5759?
2. Does the published full-frame promote/add/restore at events 5758/5759/5807
   admit an owner/host schedule for the `X0` read that restores arbitrary dirt
   without repaying the unrestored channel endpoints?

[TASK.json](TASK.json) gives first steps and blockers for both.
