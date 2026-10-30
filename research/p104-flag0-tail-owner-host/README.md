# Flag 0's published tail cut admits a self-owned X0 host schedule with zero endpoint repayment

**Finite owner/host schedule certificate. No new exponent.**

Open [#3669](https://github.com/CrocSwap/integer-mult-bounds/pull/3669) leaves
as OQ2 whether the published promote/add/restore at events 5758/5759/5807 admits
an owner/host schedule for the `X0` read that restores arbitrary dirt without
repaying the unrestored channel endpoints. This package answers yes for that
local cut.

## Result

Schedule **S0** assigns `owner = X0` (self) on the full host chart for the ADD
at event 5759. On the published #2089 tail word:

| Fact | Value |
|---|---|
| Promote / add / restore | 5758 / 5759 / 5807 |
| Coefficient | `-1/2` (matches `CORRECTION-ROWS` row 34, source 0) |
| Host chart at the ADD | `FULL = [1,…,256]` for both `X0` and `Y34` |
| Unique source owner among registers named by the ADD | `X0` |
| Dirty-helper (`D`/`G`/`Q`/`C`) touches in the window | **0** |
| `X0` destination events after the 4,058-event channel | **0** (last write 1486) |
| Endpoint repay of `X0`/`Y34` toward their initials | **false** / **false** |
| Frames after restore | `X0=FULL`, `Y34=RANK8` (channel finals) |

Dirt restoration: the window never touches a dirty helper, so the channel's
already-restored 72 dirty helpers stay restored. Endpoint repayment: after 5807
both registers sit at their channel finals, not at `[232]` / `[]`.

**Obstruction.** Restoring `X0` to its initial frame `[232]` before event 5759
while keeping the published ADD (annotated `FULL`) violates the common-chart
rule. Endpoint repayment of `X0` cannot precede the read on this word.

Selected κ stays `0.001672660197076918`. No global 104×104 owner map. Distinct
from the deferred #3669 OQ1 +2 head-span repair and from open [#3532](https://github.com/CrocSwap/integer-mult-bounds/pull/3532).

Details are in [PROOF.md](PROOF.md).

## Reproduce

```sh
python3.12 -I -B research/p104-flag0-tail-owner-host/verify.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-owner-host/verify.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-owner-host/independent.py
python3.12 -I -O -Werror -B research/p104-flag0-tail-owner-host/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-flag0-tail-owner-host
```

`verify.py` is read-only. Admission goes through `need()` and still fires under
`-O`. `independent.py` imports neither `verify.py` nor the native checker.

## Credit

Credit #3669 for OQ2, Cinna Davis / #2089 for the tail word, jwr404's
`p104-tail-flag0-*` readings for the unbound-owner gap and frame facts this
package cites, #3349 for the unrestored-endpoint census, and the reviewed #1991
channel. Prepared by Wentao Li with substantial AI assistance.

## Open next questions

1. Does the same self-owned zero-repay pattern hold for every target window?
2. What host rank mass does a copied-host alternative cost under unrestored
   endpoints?

[TASK.json](TASK.json) gives first steps and blockers.
