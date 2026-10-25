# Present-head flag 9: published channel hosts basis head only after source drop

**Scoped obstruction. No new exponent.**

Open [#3349](https://github.com/CrocSwap/integer-mult-bounds/pull/3349) shows the
basis head meets the target final on only four of 208 matched flags. Open
[#3392](https://github.com/CrocSwap/integer-mult-bounds/pull/3392) pins one of
the other 204 (absent-head flag 2). This package pins one of those four:
flag 9 (`X4` → `Y23`, basis head `196`).

On the published 4,058-event word, `X4` starts at `[196]` and drops `196` at
transport event 500. Every annotated `Y23` frame before the terminal transport
avoids `196`. The head appears on `Y23` only in the after-frame of event 3489 —
2,989 events after the source drop. No event names both endpoints, and neither
frame is restored. The published channel therefore cannot chronologically
dirty-restore that source line into the matched target along co-hosted
basis-head geometry, even though the target final contains the head.

Selected κ stays 0.001672660197076918. Details and limits are in
[PROOF.md](PROOF.md).

## Reproduce

```sh
python3.12 -I -B research/p104-present-head-flag9-audit/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-flag9-audit/verify.py
python3.12 -I -O -Werror -B research/p104-present-head-flag9-audit/independent.py
python3.12 -I -O -Werror -B research/p104-present-head-flag9-audit/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-present-head-flag9-audit
```

`verify.py` is read-only. Admission goes through `need()` and still fires under
`-O`.

## Credit

Credit Nick Petalas / #2981, jwr404 / #3242, #3349 for the 4/208 present-head
census, and #3392 for the complementary absent-head obstruction. Prepared by
Wentao Li with substantial AI assistance.

## Open next questions

Can a changed schedule co-host basis head 196 on `X4` and `Y23` long enough to
dirty-restore the source line, and what does that cost against the channel bill?
This package only shows the published annotated word introduces that head on the
matched target after the source has already abandoned it.
