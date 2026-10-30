# Paid CRT source update and row reentry

The physical current-row output now updates the same owned axis-record tape
and feeds the next row without host serialization. A paid temporary stream
lets the old borrowed-source query close before the owned source changes.
The proof covers any admitted fixed-node row sequence. Complete forward and
reverse levels run on the same tape and restore it byte for byte.

This closes the source-update handoff in PR5519/5496. Complete kappa is unchanged.
No whole-tree or three-epoch key implementation is claimed.

Read [PROOF.md](PROOF.md), [reentry.py](reentry.py), [RESULT.json](RESULT.json)
and [SOURCES.json](SOURCES.json).

```sh
python3 -B scripts/research_package.py --package research/crt-paid-row-reentry
```

Use Python 3.12 and the standard library. Expected markers:
`PASS_CRT_PAID_ROW_REENTRY rows=40 producer_calls=30 controls=5`
and `PASS_REGISTERED_RESEARCH_PACKAGE`.

Four uninterrupted forward/reverse fixtures cover padded intermediates, two
right targets, a nonroot node, idle rows and invalid-left offset disabling.
Every retired row workspace remains counted. The predecessor's exact 52-role
bank count is used once for each distinct active row. All staging, source-update
and retirement work is charged. No cross-row bank reuse is assumed.

The source numerical and ROM theorems are inherited hypotheses. The retained
logical caller is the test oracle and supplies no runtime values. This is
same-agent verification, not independent human or formal acceptance.

## Open next questions

Bind the updated owned coordinates to one complete exceptional-key epoch
sequence, with its changing-left-state source conversions, protected numerical
widths and restoration. Each epoch must use its actual current state; the
single-node proof does not authorize reuse of an old offset.

A shared row workspace could reduce the sum of retained capacities. It needs
an explicit reentry interface for every source-owned role and a historical
extent proof. The present implementation already closes the functional boundary
with a complete conservative bill and does not assume that future optimization.

Predecessor credit and limits are in PROOF.md. Ali Romman with substantial
OpenAI Codex assistance. Apache-2.0.
