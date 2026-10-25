# Channel first-touch order and endpoint frame restoration

**Scoped audit. No new exponent.**

The #3259 support cut is already certified on pinned main by
`research/p104-pooled-cut-independent`. This package instead replays the
published 208-flag matching against the 4,058-event channel witness.

Under that matching and witness, every target is first touched at or before
event 410, every source is first touched at or after event 488, no event
names both an X register and a Y register, and zero of the 104 source frames
and zero of the 104 target frames return to their initial frames.

The population bound and the unrestored X0/Y34 example agree with jwr404's
PR #3242 receipt. The new census is that the frame failure covers every
endpoint, and that the basis head meets the target final on only 4 of 208
flags. Details, the matched gap of 84, and the limits of the claim are in
[PROOF.md](PROOF.md).

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -I -O -Werror -B research/p104-channel-touch-restoration-audit/verify.py
python3.12 -I -O -Werror -B research/p104-channel-touch-restoration-audit/independent.py
python3.12 -I -O -Werror -B research/p104-channel-touch-restoration-audit/test_package.py
```

`verify.py` is read-only. Admission goes through `need()` and still fires
when Python is started with `-O`. The two scanners do not import each other.

Pinned main: `6f100d4bb5083f8c35d96fd95a539811c62f245c`. Input hashes are in
[SOURCES.json](SOURCES.json).

## Credit

Nick Petalas / #2981 for the flags, Nick Petalas / #3259 and dcharb78 / #3182
for the support cut that this package leaves in place, and jwr404 / #3242 for
the chronology receipt under audit. Prepared by Wentao Li with substantial
AI assistance.

## Open next questions

Can a chronological correction deliver the published coefficients and restore arbitrary dirt without repaying the frame loss? This census shows every endpoint frame fails to return. It does not construct or price that repair.
