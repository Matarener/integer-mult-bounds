# Receipt for the four queue-oct24a holds, and the changed head of #5427

**Task:** `overlap-receipt`, refined to one existing intake receipt.
**Base:** canonical main `32890bc5de034ab8fc93ac88ead7279a6a416d04`.
**No new κ. No closure, merge, or ledger edit.**

The 2026-10-24 queue snapshot
`docs/research/pr-intake-evidence/queue-oct24a-20261024.json` records 20
decisions, of which four are `waiting_revision`: #4580, #4612, #5427 and
#5432. The central ledger on this base still has those four open,
partially reviewed, and not installed. Three of those recorded heads were
still the GitHub heads when this note was written. **#5427 was not.**

## What the retained receipt says

| PR | Author on the receipt | Recorded head | Retained on this base |
|---|---|---|---|
| [#4580](https://github.com/CrocSwap/integer-mult-bounds/pull/4580) | Matarener | `55de56abdfd9cd7fb83758241793c18b9ae9ce71` | nothing |
| [#4612](https://github.com/CrocSwap/integer-mult-bounds/pull/4612) | Matarener | `0e0df631da41a1f9ed3489e8df532189c2643cbf` | nothing |
| [#5427](https://github.com/CrocSwap/integer-mult-bounds/pull/5427) | Matarener | `389578f2d3ef075495ce76f08100ac50e18f7d40` | nothing |
| [#5432](https://github.com/CrocSwap/integer-mult-bounds/pull/5432) | hevlyo | `6532b45ce9f3259d7408594ec480a140ec81e0e2` | nothing |

#5427's unresolved question is still Clear1nsight's Part 1 qualification:
the head claims rational-span consequences from one modular calculation, the
counterexample is `A=[p]`, `b=1`, and Part 2 is not independently accepted.
Credit for that comment stays with Chris R / Clear1nsight. Credit for the
ZQY census stays with Mark / Matarener.

## What changed after the receipt

GitHub on 2026-10-25 showed #5427 at
`e0192de5d97e5ac09f42d26d9ceedee6377c77e2`
(updated 2026-10-24T17:50:50Z). That commit's parents are exactly

- `dacc35b1f35c2b4bc2e3910520ba5cf46a020bed` — "Compute every ZQY span exactly over Q instead of modulo 2^61-1", whose parent is the recorded head `389578f2`;
- `32890bc5de034ab8fc93ac88ead7279a6a416d04` — this receipt's base.

`dacc35b1f` is not contained in the base. The recorded hold therefore
describes `389578f2` and does not describe the head that was live during
this check. The intake rule that a different head wakes an entry applies
to #5427 only. It does not, on these pins, apply to #4580, #4612 or #5432:
those three GitHub heads matched the receipt on the same observation.

On `dacc35b1f` the false sentence "non-membership modulo p therefore
implies non-membership over the rationals" is gone from `PROOF.md`. The
proof states the `A=[p]`, `b=1` counterexample. `verify.py` no longer
assigns `P = (1 << 61) - 1` or takes a modular inverse. Its `Span.add`
reports that `1` lies in the rational span of `p = 2^61-1`. An independent
one-line check agrees: `p ≡ 0` modulo `p`, while `(1/p)·p = 1` over `Q`.

## Author-checker replay, not acceptance

At `e0192de5`, in `/tmp` on CPython 3.12.3:

```sh
python3 -I -W error -B research/zqy-observation-not-retained/verify.py
```

exited 0 and printed `PASS_ZQY_OBSERVATION_NOT_RETAINED`. The script
compares its recomputation with the committed `RESULT.json`, so the
recorded ranks matched that run. This is one replay of Matarener's
checker. It is not an independent census, not a review of Part 2's
EARLY/LATE or caller-output reading, and not a reason to merge. The
`--left-depth 2` run and the optimised command were not run. The package
was absent from base `32890bc5`.

## Reproduce this receipt

```sh
python3 -B research/pr5427-hold-head-receipt/verify.py
python3 -B scripts/research_package.py --package research/pr5427-hold-head-receipt --check-only
```

Expected marker: `PASS_PR5427_HOLD_HEAD_RECEIPT`.

The checker reads the two receipt files, checks the commit parents above,
and runs the one-column rational dependence on the repaired `Span` class.
It does not contact GitHub. A later push of #5427 can move the live head
without changing this historical observation.

## Open next questions

Re-read #5427 at `e0192de5` before any closure. The arithmetic sentence that
blocked `389578f2` is not the text of `dacc35b1f`, but Part 2 was never
accepted, and a passing author checker is not that acceptance. The blocker
is a maintainer review of the new head; this receipt does not perform it.

## Credit

The queue-oct24a snapshot and the ledger rows are the maintained intake
record on `32890bc5`. Clear1nsight wrote the Part 1 qualification at
`389578f2`. Mark / Matarener wrote the ZQY package and the exact-Q repair.
The package scaffold is Douglas Colkitt's. Prepared by unpaidmoon with
substantial Cursor Grok assistance. Apache-2.0. No selected-frontier change.
