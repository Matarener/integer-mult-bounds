# Independent check of the depth-three and depth-four chain-connector tables

**Claim type: an independent finite check of three open PRs, by exhaustive
search and certificate verification. No new κ.**

## Object

Three open PRs by Nick Petalas give the shortest unsigned dirty chain
connector `z_l += B_l z_{l−1}` at depths three and four. None of them rechecks
the others:

- **[#4249](https://github.com/CrocSwap/integer-mult-bounds/pull/4249),
  depth three:** the minimum is `3m` for every `m ≥ 2`, except `(2,1)`,
  `(3,2)` and `(4,3)`, which need `4m`. It gives an explicit Lemma 3 word
  family and a (6,5) word. It also gives the depth-four values
  12, 18, 20 and 25 at `m = 2..5`.
- **[#4263](https://github.com/CrocSwap/integer-mult-bounds/pull/4263),
  depth four:** `4m` for `6 ≤ m ≤ 32`, with 486 words.
- **[#4280](https://github.com/CrocSwap/integer-mult-bounds/pull/4280),
  depth four:** `4m` for `33 ≤ m ≤ 64`, with 1,520 records in a compressed
  row model (Lemma 2: a partition λ and profiles ρ, β).

#4280 says that together these make the depth-four minimum "known exactly
for 2 ≤ m ≤ 64", while noting that #4249 and #4263 are "not rechecked here".

## Model

A positive word is correct for `c` exactly when its product of
`I + E[l][l−1]`, in the unitriangular group mod `m`, equals `I + c·E[D][0]`.
This is Lemma 1 of those PRs. Each call then appears a positive multiple of
`m` times, so `Dm` is a floor.

## Results

| Claim | Check here | Result |
| --- | --- | --- |
| #4249: depth-three minima | exhaustive BFS, `m = 2..8` | `3m`, except `4m` at `(2,1)`, `(3,2)`, `(4,3)` |
| #4249: the Lemma 3 word | every `5 ≤ m ≤ 400` and every residue (79,794 words), with its stated choice of `a` for `c = m−1`; the (6,5) word | all correct |
| #4249: depth-four table | exhaustive BFS, `m = 2..4` | 12, 18, 20 |
| #4263: 486 words, `6 ≤ m ≤ 32` | length `4m`, balanced, group product | all correct |
| #4280: 1,520 records, `33 ≤ m ≤ 64` | decoded into words from Lemma 2's definitions, then length, balance and group product | all correct |

**Literal replays.** These use random dirty registers in `(Z/m)²` and random
noncommuting `2×2` maps. They cover the depth-three words at
`m = 5, 8, 12, 97`, and the depth-four words at `c = 1` and `c = m−1` for
every `m`.

**Coverage.** Every pair `(m, c)` with `6 ≤ m ≤ 64` and `1 ≤ c < m` has a
depth-four witness of length `4m`.

**Controls.** Changing `ρ(1)` in a #4280 record, or dropping a call, makes the
word incorrect.

**The decoding is independent.** The decoder reads only #4280's Lemma 2
definitions:

- the column heights of λ give the 2/3 path;
- a call 1 at row level `r` follows `m − r` calls 2;
- a call 4 at level `b` follows `b` calls 3.

All 1,520 decoded words are correct, which checks the record format and the
witnesses together.

## Not covered

- The depth-four value 25 at `m = 5`. A pure-Python BFS over `5^10` states is
  slow. My separate C BFS in
  [#4341](https://github.com/CrocSwap/integer-mult-bounds/pull/4341)
  reproduces 25 as a control.
- #4280's Lemma 3 (prime `m` needs three short rows) and #4279's count-vector
  classification.
- Any `m > 64` at depth four, and any physical price.

## Reproduce

```sh
python3.12 -B research/chain-connector-tables-check/verify.py
```

It prints `PASS_CHAIN_CONNECTOR_TABLES_CHECK` in about 35 seconds, using only
the standard library. The two witness files are vendored byte-identically and
SHA256-checked; see `vendor/NOTICE.md`.

## Open next questions

None from this check. The open all-`m` question at depth four belongs to
#4280: no uniform family is known.

## Credit

The connector model, the lemmas, the depth-three construction, all witnesses
and the row model are Nick Petalas's (#4249, #4263, #4280). Prepared by
Ryanson Jonathan with substantial Claude Code (Claude Opus 5.5) assistance.
Apache-2.0.
