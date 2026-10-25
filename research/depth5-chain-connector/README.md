# Shortest unsigned depth-five chain connector: small m and 9 <= m <= 20

This package answers open question 2 of
[#4263](https://github.com/CrocSwap/integer-mult-bounds/pull/4263) for depth
five in a bounded range of characteristics. The contribution was produced by
Nick Petalas.

The complete calls are `z_l += B_l z_{l-1}` for l = 1, ..., 5, with x = z_0
immutable and z_1, ..., z_4 and y = z_5 holding arbitrary dirty data. The maps
are arbitrary and the coefficients lie in a nonzero unital ring of exact
characteristic m. For a nonzero residue c the word must restore z_1, ..., z_4
and add `c B5 B4 B3 B2 B1 x` to y. There are no sign or inverse calls.

| m | 2 | 3 | 4 | 5 to 8 | 9 to 20 |
|---|---:|---:|---:|---|---:|
| shortest length | 16 = 8m | 24 = 8m | 28 (c = 1, 3), 24 (c = 2) | 5m for the listed c only | 5m for every c |
| evidence | exhaustive BFS | exhaustive BFS | exhaustive BFS (opt-in) + words | witnesses | witnesses |

- **m = 2, 3:** the minimum is 8m, well above the per-call floor 5m. At depth
  four the same characteristics cost 6m (#4249).
- **m = 4:** the minimum depends on c. It is 24 = 6m for c = 2 and 28 = 7m for
  c = 1 and c = 3. Shortest words are recorded for each c; the optimal ones read
  back from the search double calls 2 and 3 (c = 1, 3) or call 3 (c = 2).
- **m = 5 to 8:** the floor 5m is attained for (5, 1), (6, 3), (7, 1..4) and
  (8, 1..4, 6). For the other eleven residues in this range the bounded search
  found no 5m word; that is a **search failure**, not a lower bound.
- **9 <= m <= 20:** the floor 5m is attained for every nonzero c (162 pairs).

So the depth-five premium is larger than at depth four and lasts at least to
m = 4 for every residue. It is gone for every residue from m = 9 to m = 20.
Whether it persists for some residues at m = 5 to 8 is open.

Claim types: **exhaustive finite computation** for the minima at m = 2, 3, 4
(the m = 4 lower bound is an opt-in run, see below), and a **finite
certificate** for each listed witness. No all-m theorem, no new κ, no supplier
admission and no change to the selected frontier.

## Argument

**Lemma 1 (floor; #4249).** Write N[i..j] for the number of scattered
occurrences of the subword i(i+1)...j in the word. The word is correct for c
iff the product of the generators I + e_{l,l+1} in UT6(Z/m) equals
I + c e_{1,6}, iff every N[i..j] is 0 mod m except N[1..5], which is c mod m.
Each call therefore appears a positive multiple of m times, so every correct
word has at least 5m calls, and lengths between multiples of m are impossible.

A word with exactly m copies of each call that meets the interval conditions
therefore has the shortest length 5m.

**Exact minima.** Breadth-first search from the identity over all
m^15 elements of UT6(Z/m), with the five generators as edges, gives the
distance to every I + c e_{1,6}. Any positive word reaching that element is a
correct word, and conversely, so the BFS distance is the exact minimum. The
same routine at depth four reproduces #4249's 12, 18, 20 and 25 at m = 2..5 as
a positive control.

**Observation.** A cyclic rotation of a correct word is correct: if
w = a v then v a = a^{-1} (a v) a, and I + c e_{1,6} is central. Rotations
were not used to produce witnesses.

## Evidence and reproduction

From the repository root, with CPython 3.12 and numpy:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/depth5-chain-connector/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/depth5-chain-connector/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/depth5-chain-connector
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/depth5-chain-connector --check-source-history
```

Any CPython 3.12 with numpy can replace the local interpreter path. The
verifier writes no files. It prints a JSON receipt with the SHA-256 of every
package file and input, then
`PASS_DEPTH5_CHAIN_CONNECTOR bfs_cases=6 witnesses=173 m4_words=3`. It checks:

- BFS minima: depth five at m = 2, 3; depth four at m = 2..5.
- For every witness: length 5m and exactly m copies of each call; the interval
  conditions by one chronological counting pass; separately, the UT6(Z/m)
  matrix product; and two literal replays with dirty registers in (Z/m)^2 and
  random, generally noncommuting 2x2 maps, checking that z_1..z_4 are restored
  and y gains exactly c B5 B4 B3 B2 B1 x.
- Full rows: every c from 1 to m - 1 is present for 9 <= m <= 20.
- The three m = 4 words, at lengths 28, 24, 28, by the same three checks.
- Five rejection controls on the (m, c) = (14, 1) witness: a wrong coefficient,
  a dropped call, a swap of adjacent noncommuting calls, one relabelled call
  and one extra call.

The m = 4 lower bounds need a BFS over 4^15 ≈ 1.07 × 10^9 elements. It takes
about 9 minutes and 20 GB of memory, so it is opt-in and not a registered
check:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/depth5-chain-connector/verify.py --exhaustive-m4
```

It asserts the distances {1: 28, 2: 24, 3: 28}. This path ran to completion
locally (CPython 3.12.15, numpy 2.5.4, macOS arm64) in 8 min 52 s and printed
`PASS_DEPTH5_CHAIN_CONNECTOR bfs_cases=7`. An equivalent standalone BFS gave the
same distances and saved the distance table from which the m = 4 words were
read back. Hosted CI does not run this path, so the m = 4 lower bounds are
local evidence that a reviewer can rerun with the command above.

[search_witnesses.c](search_witnesses.c) is the simulated-annealing search that
found the 5m witnesses (`cc -O2 -o anneal search_witnesses.c -lm`, then
`./anneal 5 M C SEED TRIES SWEEPS`). It is not part of the replay; the verifier
checks the words themselves. Three rounds were run: 40 restarts of 3 × 10^6
sweeps for 4 <= m <= 20, then 60 × 6 × 10^6 and 150 × 8 × 10^6 on the
residues still missing.

## Limitations

The m = 4 lower bounds rest on the opt-in exhaustive run described above, which hosted CI does not repeat. The
missing residues at m = 5 to 8 and every m > 20 are not decided. Each witness
is a finite certificate for its own (m, c); no all-m theorem is claimed.
Independent human and formal proof-kernel review are unclaimed. Every call
carries its complete implementation price. Admission, dispatch, routing of the
four intermediates and word-dependent physical costs are extra. No supplier
caller, precision analysis, outer multiplication theorem or new κ is supplied.

## Attribution and scope

The chain model, the interval-count reduction, the floor argument and the
depth-four minima at m = 2..5 come from
[#4249](https://github.com/CrocSwap/integer-mult-bounds/pull/4249); the
depth-four floor for 6 <= m <= 32 and the depth-five question come from
[#4263](https://github.com/CrocSwap/integer-mult-bounds/pull/4263), whose
annealing objective search_witnesses.c adapts. Ross Richardson's
[#943/#934 lineage](../universal-connector-boundary/README.md) supplies the
complete-call dirty-connector interface. The new results here are the
depth-five minima at m = 2, 3, 4, the residue dependence at m = 4, and the 173
floor witnesses. Subword counts, unitriangular matrices and BFS are classical
tools; no novelty is claimed for them. Exact pins are in
[SOURCES.json](SOURCES.json).

The `connector-alphabet-change` card is explicitly changed to this side
question, as in #4249 and #4263. The alphabet stays unsigned and complete; only
the chain gets one more call. Apache-2.0.

## Open next questions

The structured questions in [TASK.json](TASK.json) give first steps and
blockers.

1. What are the exact depth-five minima at m = 5, 6, 7, 8 for the eleven
   residues with no 5m witness here? A meet-in-the-middle search over balanced
   prefixes and suffixes could exclude 5m without the full m^15 BFS.
2. Is the depth-five minimum exactly 5m for every m >= 9?
3. Why does the m = 4 minimum depend on c? A 2-adic obstruction might be
   provable by hand and might recur at m = 8.
