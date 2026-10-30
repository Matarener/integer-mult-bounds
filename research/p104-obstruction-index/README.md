# The live P104 map omits its two on-main replays

**Partial. No new exponent.**

The family record points at
[p104-live-support-map.md](../../docs/research/p104-live-support-map.md).
That map separates the event-touch result in #3242 from the frame-support
result in #3259. It does not name either on-main replay.

| Claim | Replay on main | Excluded | Still open |
|---|---|---|---|
| Event touch | `research/p104-channel-touch-restoration-audit` | Every target is first touched at or before event 410, and every source at or after event 488. No endpoint frame returns to its initial frame. | A chronological correction that restores arbitrary dirt without repaying that frame loss. |
| Frame support | `research/p104-pooled-cut-independent` | Under the fixed-cover contract, `(Y71,X102)` is absent and its coefficient is `-1/2`. | Changed covers, changed helper contracts, added storage, or an altered channel. |

The touch note names the support replay. The support note does not exclude
those changed contracts, and it is not a multiplication theorem. Ordering
first touches does not establish subspace support. A support path does not
establish when a coefficient moves.

## What was executed

The checker authenticates the four notes and compares those sentences. It
does not replay either proof and it does not edit the map.

`scripts/research_baseline.py` needs
`research/community-frontier1094-audit/ASSEMBLY.json`, which this checkout
does not have. The orientation used here is the family record's link to the
map.

## Scope and evidence

Original card: `scope-navigation`, priority revision 6, refined to this
two-replay index. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the family record, the map and the two
replay notes. No selected frontier file changes.

## Reproduce

From the repository root, CPython 3.12:

```sh
python3.12 -B research/p104-obstruction-index/verify.py
python3.12 -B research/p104-obstruction-index/test_verify.py
python3.12 -B scripts/research_package.py --package research/p104-obstruction-index
```

## Open next questions

These two replays are the missing cross-reference. Editing the map would
leave this index.

## Credit

The touch audit was prepared by Wentao Li. The support note credits dcharb78
/ PR 3182 for the cut and Nick Petalas / PR 2981 for the covers. The map is
the contributor snapshot the family record cites.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
