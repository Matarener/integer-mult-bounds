# Commuting moves cannot retarget a staged544 line

This is a finite obstruction on two pinned words, plus one scalar identity.
It is not a supplier, a kappa bound, or a theorem about every circuit.

The move contract is `apply_move` from the vendored tracer: one ADD stays in
its section, crosses only gates accepted by `crosses`, and may replace its
common frame. Entrances, warps, and every other gate's frame stay fixed.
`crosses` is the scalar normal form: an ADD crosses another ADD when neither
destination is the other's source, and it crosses a nonzero scale on a
touched register. It does not cross a warp.

## 1. Witness for every rank-1 ADD

On each provider, 735 ADD gates have a rank-1 common frame `M`. For each such
gate `g` the checker finds an operand register `r` whose incoming frame is
already `M`, and an event that first put `M` into `r`:

| Witness | Gates | What creates `M` on `r` |
|---|---:|---|
| Entrance | 653 | `r` starts inside `M` |
| Map | 70 | A warp map, earlier in the same section or in an earlier section |
| Dependence | 12 | An earlier rank-1 ADD that does not commute with `g` |

These three classes partition the 735 gates. Both providers give the same
counts and the same twelve dependence pairs. The two provider files are not
equal.

The twelve pairs are adjacent ADDs in section `A`. The later gate reads the
register written by the earlier gate, so `crosses` fails in both directions:

| Producer | Consumer | Register |
|---:|---:|---:|
| 2027 | 2028 | 240 |
| 2029 | 2030 | 242 |
| 2181 | 2182 | 256 |
| 2183 | 2184 | 258 |
| 2335 | 2336 | 272 |
| 2337 | 2338 | 274 |
| 2489 | 2490 | 288 |
| 2491 | 2492 | 290 |
| 2643 | 2644 | 304 |
| 2645 | 2646 | 306 |
| 3569 | 3570 | 400 |
| 3723 | 3724 | 416 |

## 2. The witness survives every commuting move

**Persistence.** `tracing` accepts a word only when every non-map event's
frame contains that register's incoming state. A map may replace the state.
Its frame belongs to a warp, and `apply_move` neither relocates a warp nor
edits frame. Thus, once register `r` contains a subspace `M`, every later
non-map event on `r` still contains `M`, up to the next map. An ADD whose
incoming state contains `M` can be given only a frame that contains `M`.
A gate that commutes past `g` and lands on `r` while `r` already contains `M`
is under the same restriction, so it does not erase `M`.

**Finite hypotheses.** On both providers, for every rank-1 ADD and its witness
register, every frame from the witness source through that register's incoming
state contains `M`. An entrance or dependence window contains no map. A map
window starts at the witness warp and contains no second map. The checker
tests these facts; it does not enumerate move sequences.

**Theorem.** After any finite sequence of `apply_move` steps, every originally
rank-1 ADD still has a common frame containing its original line.

The proof is induction on the original index in the section. The witness
source still supplies `M` before the gate, and no warp on the witness register
can enter the open interval after that source: warps do not move, and
`crosses` rejects passing a warp.

- **Entrance.** The start frame is immutable and contains `M`. The window has
  no map, so every event on the register before the gate is a climb or a
  check. Persistence keeps `M`.
- **Map.** The witness warp is immutable, fails `crosses` with the gate, and
  sits earlier in the section or in an earlier section. Its map frame contains
  `M`. Persistence keeps `M` from that map until the gate.
- **Dependence.** The producer is an earlier rank-1 ADD and neither order
  commutes, so the order is invariant. By induction its frame still contains
  `M`. The window has no map. Persistence keeps `M` until the consumer.

In each case the incoming state contains `M`, so every legal frame of the gate
contains `M`. No legal image is a line disjoint from `M`. In particular, no
sequence of commuting moves realizes the crossed-line pattern on these words:
that pattern replaces `M` by a disjoint line on both gates.

## 3. The crossed-line identity has histogram delta zero

The pattern left open by PR #3964 is still a real scalar identity. It just
does not occur under this move contract, and it does not improve the bill.
PR #4122 already invoices a richer swap-and-restore identity at delta zero
and explicitly does not search these providers. The calculation below is the
#3964 synthetic control, not a second claim on that invoice.

On helpers `h = 300` and `s = 301`, with fixed terminal frame `span(e1, e2)`:

```text
h += 1 * s    frame span(e1)
h += 1 * s    frame span(e1)
```

Replacing both frames by `span(e2)` keeps every opcode, operand, and
coefficient. Each helper climbs `0 → line → line → plane`: two rank-1 children
per helper, four rank-1 children altogether, before and after. The histogram
delta is zero. Either one-edit intermediate is illegal, because `span(e1)` and
`span(e2)` are incomparable. The same rejection is reproduced by the vendored
tracer; its fixed target-register epilogue is identical on both words, so the
full tracer bill is unchanged as well.

An unchanged histogram is not a kappa gain. The favorable exchange
`H1 - 2 H2 + H3` is a different signed row and is not this delta.

## 4. What is not claimed

Noncommuting rewrites are outside `apply_move`. Frames that properly contain
the old line are outside the theorem. Cleanup, native phases, owners, and
all-size transfer are not repriced, because no disjoint-line move exists to
price. The selected conditional kappa stays `0.001672660197076918`.
