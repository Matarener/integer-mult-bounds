# Exact shortest depth-five chain connectors for #4281's eleven open residues

**Claim type: exhaustive finite computation for the lower bounds, and finite
certificates for the upper bounds. No new κ.** It closes #4281's open
question and my #4341's.

## Object

[PR #4281](https://github.com/CrocSwap/integer-mult-bounds/pull/4281)
(petalas) gives the shortest unsigned depth-five dirty chain connector
`z_l += B_l z_{l−1}`, `l = 1..5`, where the word adds `c·B5B4B3B2B1·x` to
`y`. For `5 ≤ m ≤ 8` its search found 5m words only for
`(5,1)`, `(6,3)`, `(7,1..4)` and `(8,1..4,6)`. It left eleven pairs undecided,
calling them "a search failure, not a bound".
[#4341](https://github.com/CrocSwap/integer-mult-bounds/pull/4341) noted
that an exhaustive BFS at `m = 5` would need a 30 GB table.

## Results

| m | c | shortest length | evidence |
| ---: | --- | ---: | --- |
| 5 | 2 | **30 = 6m** | nothing at 25; witness at 30 |
| 5 | 3, 4 | **35 = 7m** | nothing at 25 or 30; witnesses at 35 |
| 6 | 1 | **30 = 5m** | witness (#4281's search missed it) |
| 6 | 2, 4, 5 | **36 = 6m** | nothing at 30; witnesses at 36 |
| 7 | 5 | **35 = 5m** | witness (missed by search) |
| 7 | 6 | **42 = 6m** | nothing at 35; witness at 42 |
| 8 | 5, 7 | **40 = 5m** | witnesses (missed by search) |

With #4281's rows, the depth-five minimum is now known for every `c` at
`2 ≤ m ≤ 20`.

- **The premium sits on `c ≡ −1`.** At `m = 4..7`, the residue `−1` is never
  attained at `5m`. It costs `7m` at `m = 4, 5` and `6m` at `m = 6, 7`.
- **The premium is gone from `m = 8`.** Every residue attains the floor `5m`
  there.

## Method: the commutation decomposition

Calls `l` and `k` commute when `|l − k| ≥ 2`. So a word's interval counts
`N[i..j]` (#4281's Lemma 1) depend only on three things:

- the subword `M` of calls 2, 3 and 4;
- for each call 1, the number `a` of calls 2 before it;
- for each call 5, the number `b` of calls 4 before it.

For each call 3 in `M`, let `k2` and `k4` be the numbers of calls 2 and 4
before it. Then every count is a sum over those calls 3. For example,
`N15 = Σ_a Σ_b Σ_3 (k2−a)⁺(b−k4)⁺`; the full list is in the header of
`residues.c`.

For one call-count vector, `residues.c` enumerates every `M` that passes its
own conditions, every multiset of levels for the 1s and the 5s, and the
resulting `N15` residues. It prints the complete set of reachable `c`, with a
witness word for each.

- **Lower bounds.** A residue missing from every count vector of a length is
  impossible at that length.
- **Length gaps.** Lemma 1 rules out lengths that are not multiples of `m`.

**Cross-checks against exhaustive BFS.**

- The decider's minima over all count vectors equal the BFS minima:
  - 16 at `m = 2`;
  - 24 and 24 at `m = 3`;
  - 28, 24, 28 at `m = 4`, including the residue-dependent case.
- Python reruns `m = 2` and `m = 3` up to 21 calls. The C build covers `m = 3`
  up to 24 and `m = 4` up to 28.

**Witnesses.** Every one is checked by the unitriangular product and by
literal replays with random noncommuting 2×2 maps. Most come from the
decider. Those for `(7,6)`, `(8,5)` and `(8,7)` come from `anneal.c`, a
search only, and the witnesses are what certify them.

## Not covered

- **`m > 20`.**
- **Exhaustive runs at `m = 8`.** None was needed there.
- **Physical price.** Any physical price, admission or caller.

## Reproduce

```sh
python3.12 -B research/depth5-connector-residues/verify.py
cc -O2 -DM=7 -o residues research/depth5-connector-residues/residues.c && ./residues 7 7 7 7 7
```

The first prints `PASS_DEPTH5_CONNECTOR_RESIDUES` in about 3 minutes, using
only the standard library. It checks that the recorded complete runs, which
carry the lower bounds, were made with this `residues.c` (by SHA256). They
are local evidence: the `m = 7` balanced run took 93 s, and CI does not
repeat them.

## Open next questions

None for `m ≤ 20`.

## Credit

The connector model, Lemma 1 and #4281's witnesses are Nick Petalas's,
building on #4249 and #4263. Prepared by Ryanson Jonathan with substantial
Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
