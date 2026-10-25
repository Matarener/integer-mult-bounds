# Independent BFS for #4281's depth-five chain connector minima

**Claim type: an independent exhaustive finite computation and certificate
check. No new κ.** It reproduces the one part of #4281 that its CI does not
rerun.

## Object

[PR #4281](https://github.com/CrocSwap/integer-mult-bounds/pull/4281)
(petalas) finds the shortest unsigned depth-five dirty chain connector `z_l +=
B_l z_{l−1}`, `l = 1..5`. Its claims:

- **m = 2 and 3:** the minimum is `8m`, by exhaustive BFS;
- **m = 4:** 28 for `c = 1, 3` and 24 for `c = 2`;
- **m = 5 to 20:** 173 witnesses of length `5m`.

The m = 4 lower bounds come from a BFS over `4^15 ≈ 1.07·10⁹` group elements.
#4281 runs that BFS only as an opt-in command needing about 20 GB, so CI never
repeats it, and nothing else had.

## Model

A positive word is correct for residue `c` exactly when its product of the
generators `I + E[l][l−1]` in the unitriangular group mod `m` equals
`I + c·E[5][0]`. This is #4281's Lemma 1, here in lower-triangular form. BFS
distance from the identity is therefore the exact minimum.

## Results

| Case | This package | #4281 |
| --- | --- | --- |
| depth 5, m = 2 | 16 (Python and C) | 16 |
| depth 5, m = 3 | 24, 24 (C) | 24 |
| depth 5, m = 4 | **28, 24, 28** for `c = 1, 2, 3` (C, 51 s, 1.07 GB) | 28, 24, 28 (opt-in) |
| depth 4, m = 2..5 (control) | 12, 18, 20, 25 (Python for m ≤ 4, C for all) | #4249's values |

**Witnesses.** All 173 vendored witnesses pass three checks:

- the length is `5m`, with each call used `m` times;
- the group product is correct;
- three literal replays, with random dirty registers in `(Z/m)²` and random
  noncommuting `2×2` maps, restore `z_1..z_4` and add exactly
  `c·B5B4B3B2B1·x` to `y`.

Every `c` is present for `9 ≤ m ≤ 20`. The three m = 4 words have lengths 28,
24 and 28 and are correct.

**Controls.** Dropping a call, or swapping two adjacent noncommuting calls,
makes a witness incorrect.

## Method and independence

Nothing is imported from #4281, and its numpy BFS is not used.

- **`bfs.c`** is a separate implementation: a `uint8` distance table over
  base-`m` digit states, with layer scans. It stops once every target residue
  is reached.
- **`verify.py`** has its own standard-library BFS for the small cases. It also
  checks that `evidence/BFS-RUNS.txt` was recorded for this exact `bfs.c`, by
  SHA256.

The C runs are **local evidence**: Apple clang 21, arm64, macOS. CI reads the
recorded output and does not recompile.

## Not covered

- The residues at m = 5 to 8 that #4281's search did not find, and every
  m > 20.
- Any physical price, admission or caller.

## Reproduce

```sh
python3.12 -B research/depth5-connector-independent-bfs/verify.py
cc -O2 -DM=4 -DD=5 -o bfs research/depth5-connector-independent-bfs/bfs.c && ./bfs
```

The first prints `PASS_DEPTH5_CONNECTOR_INDEPENDENT_BFS` in about 9 seconds.
The second takes about a minute and 1.1 GB of memory, and prints the m = 4
distances.

## Open next questions

1. **Decide the eleven missing residues at m = 5 to 8.**
   - *Why it matters:* #4281 calls them search failures, not bounds. A BFS
     shows whether the floor `5m` is attainable there.
   - *First step:* `bfs.c` at m = 5, which has `5^15 ≈ 3.1·10¹⁰` states, needs a
     30 GB table. A meet-in-the-middle search to depth `5m/2` is the cheaper
     route.
   - *Blocked by:* memory on this machine.

## Credit

The connector model, Lemma 1, the witnesses and the m = 4 words are Nick
Petalas's (#4281, building on #4249 and #4263). Prepared by Ryanson Jonathan
with substantial Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
