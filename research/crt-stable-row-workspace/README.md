# Stable numerical and ROM backing for the actual CRT row consumer

This closes PR5625's fixed-node workspace-reuse question at an explicit
constructor interface. The actual paid numerical and ROM row pipeline now
reuses 118 stable roles while the source-update routine keeps its original
retire-before-write order. The first predecessor fixture executes ten rows,
including idle rows, reaches `(1,2)`, then restores `(1,1)` and every source byte.
The same backings retain 2,299 cells, including staging. No kappa changes.

[PROOF.md](PROOF.md) gives the quantified source-relative ownership argument,
all constructors/aliases, historical-tail induction, and a width-only per-role
envelope. It retains the predecessor arithmetic, query and retirement theorems
as hypotheses. This is a written proof and finite implementation check, not a
proof-assistant result or a complete multiplication theorem.

`query.py` is the original query with exactly six auditable substitutions in
`SEAMS.json`. `workspace.py` implements the stable role interface. The verifier
reconstructs the query bytes, executes the real numerical/ROM programs, checks
all 118 identities and historical extents, and compares each row to the existing
logical Caller oracle. The actual fixture includes shorter canonical reentry
after longer extent. Eleven negative controls cover stale offsets through the
actual producer, premature source mutation/reentry, retained tail data, aliasing,
incorrect max-total accounting, and the inherited source-update faults.

Run from repository root with Python 3.12 for the registered runner, standard library only:

```sh
python3.12 -B scripts/research_package.py --package research/crt-stable-row-workspace
```

Registered normal and optimized replays each take approximately 3 seconds on the
author's machine. `RESULT.json` contains exact deterministic per-role capacities
and all ten row invoices. Host snapshots/decoding are confined to the verifier.
No predecessor full suite, Lean, Docker, selected replay or dependency install
is needed for this scoped check.

## Source and novelty

PR5625, Ali Romman, exact head `c36a72644322913866041e061912893a8f210ad5`,
retains distinct fresh row banks and asks explicitly about workspace reuse.
PR5496 (JoyboyBrian) supplies the joined query, PR5353 (Ali Romman) the mixed
RowEntry, and PR5519 (commdata2338) the 52-role ROM bank count. The numerical
Entry and encoded ROM producer retain their JoyboyBrian attribution and all
credited predecessor sources, including Cinna Davis's CRT implementation.
PR6082's Raw.shuttle work is credited for the rolewise historical-capacity
accounting principle; its binary u/t consumer is a different lifecycle. This
package supplies the previously missing actual RowQuery constructor map and
adapter rather than claiming the generic max identity as new.

The public claim is [discussion 4709](https://github.com/CrocSwap/integer-mult-bounds/discussions/4709#discussioncomment-19234415).
All source inputs are pinned at canonical main
`721c03822c421b7f7fcbb2598993b947c4d88419`, priority 8; selected PR6030 remains
unchanged. Source/history/export checks authenticate those bytes and packaging,
not the all-size predecessor hypotheses. No shared source file is edited.

## Open next questions

1. Independently audit the written historical-tail/constructor proof against
   the pinned producer retirement contracts. Start with the118-role map and
   the six source substitutions; this remains source-relative pending that audit.
2. Tighten the deliberately loose 52B ROM envelope into individual scratch-role
   formulas if a complete consumer price needs that coefficient. The present
   exact finite capacities do not establish sharp all-size formulas.
3. Connect reentry across changing node precision or exceptional-key epochs.
   First specify ownership and shape changes at that caller; the fixed-node
   proof does not authorize those transitions.

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.
