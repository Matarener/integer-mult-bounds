# Flag 0 has no forward one-register relay

**Partial. No new exponent.**

Flag 0 names source `X0`, target `Y34` and basis head 232. In the published
channel, `X0` leaves frame `[232]` at event 591. `Y34` first contains 232
at event 3500. At that event `X0` sits on the coordinate basis

```text
[1, 2, 4, 8, 16, 32, 64, 128, 256]
```

which does not contain 232. The registers named with both endpoints are
`Q3`, `Q4` and `Q6`. `Y34` meets them at events 130, 131 and 133. `X0`
meets them at events 3798, 3850 and 3954, after `Y34` has finished. The
forward relay count is zero.

## What was executed

The checker walks the published program for these two registers. It does
not rebuild the 208-flag matching and it does not emit a new instruction.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is flag 0 in the joint-flag
certificate and the channel witness.

## Scope and evidence

Original card: `p104-side-correction`, priority revision 6, refined to this
flag-0 cut. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the witness, the flag certificate and the
schedule note. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/p104-flag0-relay/verify.py
python3.12 -B research/p104-flag0-relay/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-flag0-relay
```

## Open next questions

The head window and the three shared registers are this flag's cut. A
second flag would be another word.

## Credit

Nick Petalas supplied the 208-flag certificate. Chafik Boukhalfa supplied
the channel lineage through PR 1991, as the schedule note credits. The
relay question is the open question of `research/p104-flag-channel-schedule`.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
