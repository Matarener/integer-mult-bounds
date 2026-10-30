# Present-head flag 43: the target hosts the flag's tail before its head, and the head only after the last update

**Scoped obstruction. No new exponent.**

Open [#3349](https://github.com/CrocSwap/integer-mult-bounds/pull/3349) shows the
basis head is in the target final on only four of the 208 matched flags:
`(0, 1, 9, 43)`. Open [#3443](https://github.com/CrocSwap/integer-mult-bounds/pull/3443)
pins flag 9 and open [#3451](https://github.com/CrocSwap/integer-mult-bounds/pull/3451)
pins flag 1. This package pins flag 43 (`X21` → `Y59`, basis head `15`), the
last present-head flag outside the flag-0 coefficient cascade.

On the published 4,058-event word, `Y59` passes through six preterminal frames,
from `[]` to `[95, 447, 6, 32, 20]`. None lists `15` and none spans it over
GF(2). The head enters `Y59` only in the after-frame of the terminal rank-3
transport at event 3525. All 15 adds into `Y59` (events 223 through 3364) run in
charts that exclude the head direction; ten of them run in the empty chart. No
event names both `X21` and `Y59`, and neither frame is restored.

The new fact is on the target side. `Y59`'s last two updates (events 3231 and
3364) run in charts that already span tail vectors of the same flag, `{32}` and
then `{6, 18, 32}`. At both updates `X21`'s live frame has rank 9 and spans them
too. So both endpoints co-host part of the flag's basis geometry while `Y59` is
still being updated, but the head direction is missing until the single terminal
step. The obstruction is specific to the head, not a consequence of the target
filling late.

On the source side, `X21` starts at `[15]`, and its first transport (event 570)
lists `[3, 4, 8, 128, 256]`. That drops `15` from the list but not from the
span, because `15 = 3 ^ 4 ^ 8`. All 22 `X21` annotations span the head. This
answers #3451's second open question for flag 43: in span the source keeps the
head direction and the target gains it only at its terminal transport.

Both endpoints first host the head direction together at event 3525, and `Y59`
has no event after that. The published channel therefore never updates or
touches the matched target while both endpoints host the basis-head direction.
Chronological dirty restoration along co-hosted basis-head geometry is
unavailable on this word.

Flag 43 is not a reprint of flags 1 or 9 (drop/arrive/gap 570/3525/2955 against
591/3473/2882 and 500/3489/2989); both scanners refuse a tuple equal to either.
The source-side schedule shape does repeat #3451's `X0`, so the new content is
the target chronology and the tail co-hosting.

Selected κ stays 0.001672660197076918. Details and limits are in
[PROOF.md](PROOF.md).

## Reproduce

```sh
python3.12 -I -B research/p104-present-head-flag43-audit/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-flag43-audit/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-flag43-audit/independent.py
python3.12 -I -O -Werror -B research/p104-present-head-flag43-audit/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-present-head-flag43-audit
```

`verify.py` is read-only. Admission goes through `need()` and still fires under
`-O`. `test_package.py` corrupts temporary copies of the certificate and of one
pinned input and checks that both scanners reject them under `-O`.

## Credit

Credit Nick Petalas / #2981 for the flag matching, the reviewed #1991 channel
lineage for the witness, jwr404 / #3242 for the schedule receipt and #3363 for
the relay census, #3349 for the present-head census, #3443 and #3451 for the
flag-9 and flag-1 methods, and #3392 for the absent-head counterpart. Prepared
by Wentao Li with substantial AI assistance.

## Open next questions

1. Can a changed schedule put `15` into `Y59`'s span at or before its last add
   (event 3364) while `X21` is still live, and what does that cost against the
   channel bill? The terminal step has rank 3 and the chart at 3364 already
   hosts `{6, 18, 32}`, so the head is one rank step away.
2. Is tail-before-head hosting specific to flag 43 among the present-head flags,
   and does it occur on absent-head flags? #3451's certificate shows no flag-1
   basis vector in `Y7`'s preterminal span.

[TASK.json](TASK.json) gives first steps and blockers for both.
