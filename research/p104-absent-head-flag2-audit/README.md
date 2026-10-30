# Absent-head flag 2: published channel never hosts basis head 488

**Scoped obstruction. No new exponent.**

Open #3349 already counts that the basis head meets the target final on only
four of 208 matched flags. This package pins one of the other 204: flag 2
(`X1` → `Y84`, basis head `488`).

On the published 4,058-event word, `X1` starts at `[488]` and drops `488` at
transport event 494. Every annotated `Y84` frame avoids `488`, the `Y84` final
excludes `488`, and no event names both endpoints. The published channel
therefore cannot chronologically host a basis-head coefficient or dirty-restore
that source line into the matched target along this flag's geometry.

Selected κ stays 0.001672660197076918. Details and limits are in
[PROOF.md](PROOF.md).

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -I -B research/p104-absent-head-flag2-audit/verify.py
python3.12 -I -O -Werror -B research/p104-absent-head-flag2-audit/verify.py
python3.12 -I -O -Werror -B research/p104-absent-head-flag2-audit/independent.py
python3.12 -I -O -Werror -B research/p104-absent-head-flag2-audit/test_package.py
python3.12 -B scripts/research_package.py --package research/p104-absent-head-flag2-audit
```

`verify.py` is read-only. Admission goes through `need()` and still fires under
`-O`. The two scanners do not import each other.

Pinned main: `6f100d4bb5083f8c35d96fd95a539811c62f245c`. Input hashes are in
[SOURCES.json](SOURCES.json).

## Credit

Nick Petalas / #2981, the #3349 restoration census, jwr404 / #3242, and the
reviewed #1991 channel. Prepared by Wentao Li with substantial AI assistance.

## Open next questions

Can a changed schedule host basis head 488 in `Y84` long enough to dirty-restore
the source line, and what does that cost against the channel bill? This package
only shows the published annotated word never hosts that head on the matched
target.
