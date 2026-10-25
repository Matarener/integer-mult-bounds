# Shortest unsigned depth-four chain connector, 6 <= m <= 32

This finite certificate answers open question 1 of
[#4249](https://github.com/CrocSwap/integer-mult-bounds/pull/4249) for
characteristics 6 to 32. The contribution was produced by Nick Petalas.

The complete calls are `z_l += B_l z_{l-1}` for l = 1, 2, 3, 4, with x = z_0
immutable and z_1, z_2, z_3 and y = z_4 holding arbitrary dirty data. The maps
are arbitrary and the coefficients lie in a nonzero unital ring of exact
characteristic m. For a nonzero residue c the word must restore z_1, z_2 and
z_3 and add `c B4 B3 B2 B1 x` to y. There are no sign or inverse calls.

```text
shortest length = 4m   for every 6 <= m <= 32 and every c != 0 (mod m)
```

The per-call floor is 4m. #4249 found that depth four costs more than this
floor in small characteristic: exact search there gives 12, 18, 20 and 25
calls at m = 2, 3, 4 and 5. This package shows that the premium is gone at
m = 6 and stays gone through m = 32, for all 486 pairs (m, c). With the m <= 5
values from #4249, the depth-four minimum is known exactly for 2 <= m <= 32.

| m | 2 | 3 | 4 | 5 | 6 to 32 |
|---|---:|---:|---:|---:|---:|
| shortest length | 12 = 6m | 18 = 6m | 20 = 5m | 25 = 5m | 4m |
| source | #4249 | #4249 | #4249 | #4249 | this package |

Claim type: **finite certificate** for each listed (m, c). No all-m theorem,
no new κ, no supplier admission and no change to the selected frontier.

## Argument

**Lemma 1 (floor; #4249, Lemmas 1 and 2).** Write N[i..j] for the number of
scattered occurrences of the subword i(i+1)...j in the word. The word is correct
for c iff every N[i..j] is 0 mod m, except N[1..4] which is c mod m. Since
N[l..l] is the number of calls l, each call appears a multiple of m times, and
at least once because N[1..4] is nonzero. So every correct word has at least 4m
calls. Equivalently, the product of the generators I + e_{l,l+1} in UT5(Z/m)
must equal I + c e_{1,5}.

So a word with exactly m copies of each call that meets the interval
conditions has the shortest length 4m. [witnesses.json](witnesses.json) gives
one for every pair (m, c) with 6 <= m <= 32 and 1 <= c < m.

**Lemma 2 (three interleavings).** Calls l and l' commute unless |l - l'| = 1,
so a word is determined, up to its action, by three sequences: x_j, the number
of calls 1 before the j-th call 2; y_k, the number of calls 2 before the k-th
call 3; and z_l, the number of calls 3 before the l-th call 4. Write
X(s) = x_1 + ... + x_s and Y(s) = y_1 + ... + y_s. Then

```text
N[1..2] = Σ x_j      N[2..3] = Σ y_k        N[3..4] = Σ z_l
N[1..3] = Σ_k X(y_k)  N[2..4] = Σ_l Y(z_l)
N[1..4] = Σ_l Σ_{k <= z_l} X(y_k)
```

*Proof.* A call 3 completes N[1..3] once for each 1-2 pair before it, which is
X(y_k) for the k-th call 3. The other lines follow in the same way, one level
at a time. ∎

The verifier checks Lemma 2 against direct counting on 2,000 random balanced
words. It is only used to state the open question below; the certificate does
not depend on it.

### What did not give an all-m law

A uniform construction was attempted and not found. These attempts are recorded
so the next contributor does not repeat them:

- Minimum-block witnesses: the smallest number of blocks `l^e` in a 4m
  witness is 13 to 18 at m = 6, depending on c, and 16 for every c at m = 7.
  At m = 7 the six minimum-block witnesses use only two mirrored {1,2,3}
  skeletons, with the calls 4 split over three gaps. For a fixed skeleton the
  conditions on the three gap multiplicities are linear mod m.
- That m = 7 skeleton, with letter sequence 3 2 3 2 3 1 2 3 2 3 1 2 1, one
  large block per call and every other block of length 1 or 2, does not give a
  uniform family. Two such skeletons cover every residue at m = 9 with three
  gaps; none covers every residue at m = 10, and none at m = 11.
- With x_j = j - 1 and z_l = l - 1 (odd m) and a single interior block of
  y-values, no solution exists with up to four interior values at m = 7 to 15.
  Up to seven values gives only a few residues.
- With z restricted to two interior picks and y to one interior block of three
  values, solutions exist at m = 7 and 13, via a cube root of unity
  (y-block (1, q, q²)), but not at m = 9 or 11.
- Several block designs make Y(s) - s equal the weighted 1-2-3 count at every
  gap, which forces c = 0.

These were local exploratory searches; their scripts are not part of the
package.

## Evidence and reproduction

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/depth4-chain-connector/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/depth4-chain-connector/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/depth4-chain-connector
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/depth4-chain-connector --check-source-history
```

Any CPython 3.12 can replace the local interpreter path. The verifier writes no
files. It prints a JSON receipt with the SHA-256 of every package file and
input, then `PASS_DEPTH4_CHAIN_CONNECTOR moduli=27 witnesses=486`. It checks:

- For every witness: length 4m and exactly m copies of each call.
- The interval conditions of Lemma 1, by one chronological counting pass.
- Separately, the UT5(Z/m) matrix product equals I + c e_{1,5}.
- Two literal replays per witness, 972 in all, with dirty registers in
  (Z/m)^2 and random 2x2 maps. These maps generally do not commute. The replay
  checks that z_1, z_2 and z_3 are restored and y gains exactly c B4 B3 B2 B1 x.
- Six rejection controls on the witness for (m, c) = (7, 3): a wrong
  coefficient, a dropped call, a swap of adjacent noncommuting calls, the
  reversed word, one extra call, and the floor predicate.
- Lemma 2 on 2,000 random balanced words.

[search_witnesses.py](search_witnesses.py) is how the witnesses were found.
It runs simulated annealing over balanced words, seeded by (m, c), with
`search_witnesses.py M C`. It is not part of the replay. The verifier checks
the words themselves, so it does not matter how they were found.

## Limitations

The result covers only 6 <= m <= 32. It is a finite certificate per (m, c),
not an all-m theorem. The m <= 5 values are #4249's and are not rechecked
here. Independent human and formal proof-kernel review are unclaimed. Every
call carries its complete implementation price. Admission, dispatch, routing of
the three intermediates and word-dependent physical costs are extra. No
supplier caller, precision analysis, outer multiplication theorem or new κ is
supplied.

## Attribution and scope

The chain model, the interval-count reduction, the floor and the m <= 5
depth-four minima come from
[#4249](https://github.com/CrocSwap/integer-mult-bounds/pull/4249). The
depth-two chain and its 2m floor come from
[#4231](https://github.com/CrocSwap/integer-mult-bounds/pull/4231) and
[#4236](https://github.com/CrocSwap/integer-mult-bounds/pull/4236). Ross
Richardson's [#943/#934 lineage](../universal-connector-boundary/README.md)
supplies the complete-call dirty-connector interface. The new results here
are the 486 witnesses, the exact minimum 4m for 6 <= m <= 32, Lemma 2 as
stated and the recorded failed families. Subword counts and unitriangular
matrices are classical tools; no novelty is claimed for them. Exact pins are in
[SOURCES.json](SOURCES.json).

The `connector-alphabet-change` card is explicitly changed to this side
question, as in #4249. The alphabet stays unsigned and complete; only the chain
gets one more call. Apache-2.0.

## Open next questions

The structured questions in [TASK.json](TASK.json) give first steps and
blockers.

1. Is the depth-four minimum exactly 4m for every m >= 6? A parametric family
   of the sequences x, y, z of Lemma 2 would prove it. The failed families above
   show which simple shapes do not work.
2. Does the per-call floor km hold at depth k >= 5 for all large m, and from
   which m on?
3. Does any concrete recursive caller route through three dirty intermediates
   with a favorable complete invoice for these 4m calls?
