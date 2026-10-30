# Allocate a minimum helper pool

Use fixed, checked lifetimes to allocate reusable helper slots. The tool assigns
slot ranges and supplies a simultaneous-live-set witness for the minimum pool
size. It does not infer when a source helper becomes safe to reuse.

```sh
python3 -B scripts/allocate_helper_lifetimes.py LIFETIMES.json > allocation.json
```

The input has schema `integer-mult-helper-lifetimes/v1`, a nonempty `contract`
string, and a `lifetimes` list. Each row has a unique `id`, integer `start` and
`end`, and positive integer `width`. A lifetime is half-open: `[start,end)`.
Release at an end occurs before allocation at the same time. Include cleanup,
restoration, and any required guard time inside the lifetime.

The contract must permit freely assignable unit slots and noncontiguous ranges.
For example, width four can use `[0,2)` and `[4,6)`. If a native interface requires
one contiguous block, this model does not apply. Routing and alignment costs are
not part of the allocation objective.

Copy the report's `certificate` object to `certificate.json` for separate replay:

```sh
python3 -B scripts/allocate_helper_lifetimes.py LIFETIMES.json \
  --verify certificate.json
```

The allocator processes starts in time order, releases all expired ranges, and
uses free ranges before extending the pool. It never expands a width into unit
objects. If an allocation extends the pool, all existing slots are then live,
so the new capacity equals the simultaneous live width. Otherwise capacity does
not change. The final capacity therefore equals the maximum live width.

The certificate includes all assigned ranges plus a time and the exact live set
at that time. The independent checker replays occupied ranges, checks each
declared width, rejects collisions, and verifies that the live-set width equals
the pool capacity. Every allocation needs at least that many slots at that time.
This gives matching feasible and lower-bound witnesses for optimality.

For lifetimes `(0,2,2)`, `(0,4,2)`, `(0,2,2)`, and `(2,3,4)`, the last width-four
helper reuses two separated ranges. Six slots suffice and are necessary. This is
an arithmetic example; it does not prove a source cleanup operation.

Limits: 512 lifetimes, endpoints in `0..10^12`, widths in `1..10^60`, 1 MiB input,
and 32 MiB replay certificate. Invalid input or a false certificate exits 2
without a success report. Exact input bytes are bound by SHA-256.

Certificate capacities and slot endpoints can reach `512 * 10^60`, the sum
of all allowed widths. The certificate reader accepts that aggregate bound;
the lifetime input keeps its `10^60` width limit. For example, two simultaneous
helpers of width `10^60` produce a `2 * 10^60` certificate that can be replayed
through `--verify`. Oversized integer tokens remain bounded before conversion.

## Frozen P104 example

`tests/fixtures/helper-lifetimes-pr5717.json` copies the eleven rows in
`field_maps[0].owned_lifetimes` from `research/p104-caller-owned-interface/expected/candidate.json.gz`
at main commit `de5ec2e7a6074068452f45b1a191b5c72832df4a`. The compressed
source SHA-256 is `2f22c811a85f5a37a6658ba0a21705aee55fc848a8aa85ddd5fefced8e1f460b`. Each row keeps
its start and end, has width one, and uses its row index plus role as the ID.
The allocator proves a two-slot minimum, matching the frozen local schedule.
This test does not repeat PR5717's source cleanup, native map, or whole-caller replay.

## Open next questions

Extract safe lifetimes from a checked native trace. Bind assigned slots back to
that trace and replay it after renaming. Charge routes, CLEARs, and restoration.
PR5717 checks an actual P104 owned schedule; this utility does not replace that
source-specific evidence or certify a new κ.

Credits: classical interval coloring, the T74 cleanup pool and lower-bound
witness in PR2655, the P104 owned-interface audit in PR5717, and their retained
predecessors. Prepared for Ali Romman with OpenAI Codex assistance. Apache-2.0.
Aggregate-capacity replay repair and CLI regression controls by
josecarlosgonzalezroque-design with substantial OpenAI Codex assistance.
