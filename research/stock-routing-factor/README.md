# The cover-routing sentence names no constant width factor

**Partial. No new exponent.**

The finite-cover note says that fixed port routing uses a constant number of
old width-`O(w)` interchanges. That paragraph does not name a constant `c_R`.
The reviewed PR185 text repeats ordinary width-`O(w)` calls for fixed cover
routing. Its high-part exchange has width `k=O(w log e)`, which is not a
constant multiple of `w`. The vendored PR387 proof says the parent needs no
external row multiplier, and that the retained 252 allowance is unused slack.

The published native stage-2 routing room is `4777557234646`. Comparing
`log2(c_R)` with that room stays uninstantiated, because these texts do not
name `c_R`. No cutoff margin is recomputed.

## What was executed

The checker pins the finite-cover paragraph, the two PR185 width sentences,
the PR387 row-multiplier sentence, and the published stage-2 table row. It
accepts a named `c_R`, an explicit “width at most N”, or a numeric multiple
of `w` as a constant factor. The routing paragraph has none of those.

## Scope and evidence

Original card: `selected-stock-envelope`, priority revision 6, refined to this
missing routing factor. [TASK.json](TASK.json) records the scope change.
[RESULT.json](RESULT.json) is the executed receipt and is not rewritten.
[SOURCES.json](SOURCES.json) pins the cover note, the PR185 review, the PR387
proof, and the margin-chain note that publishes the room. No selected frontier
file changes.

Upstream checkpoint: `6f100d4bb5083f8c35d96fd95a539811c62f245c`, priority
revision 6, checked 2026-10-18 04:36 UTC. Canonical main and the fork main
were at that commit. This is the second card of draw
`1cd876d46fd0914d48e990ae5ea76c29` on the adversarial-audit track. The latest
handoff comments are completed releases, not an open request on this card.

## Reproduce

From the repository root, standard-library Python 3.12:

```sh
python3.12 -B research/stock-routing-factor/verify.py
python3.12 -B research/stock-routing-factor/test_verify.py
python3.12 -B scripts/research_package.py --package research/stock-routing-factor
```

The replay finishes in under a second.

## Open next questions

The three pinned texts do not name a constant `c_R`. Another copy of the same
`O(w)` sentence would not instantiate the stage-2 room comparison.

## Credit

The finite-cover sentence is in `notes/three-stage-cover-bit.tex`. The width
sentences are in the reviewed PR185 proof and the vendored PR387 proof. The
stage-2 room is the published native row in Kumagi's stock-margin chain.
Josie Elliston's stock audit and the stage-2 handoff retain their own credit
for the cutoff receipt this note does not recompute.

Prepared by jwr with substantial Cursor agent assistance. No independent human
review is claimed. Apache-2.0.
