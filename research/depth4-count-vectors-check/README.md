# Independent check of #4279's depth-four count vectors, m = 2..5

**Claim type: an independent exhaustive finite computation in a bounded box.
No new κ.** It corroborates #4279's theorem and does not replace its
all-length reduction.

## Object

[PR #4279](https://github.com/CrocSwap/integer-mult-bounds/pull/4279) (Nick
Petalas) classifies the call-count vectors `n = (n_1, …, n_4)` of the unsigned
depth-four dirty chain connector at `m = 2..5`. Its theorem: a vector is
attained by a correct word, for any nonzero `c`, exactly when every `n_l` is a
multiple of `m` and `n` dominates a member of

```text
P(2) = {(2,4,4,2)}
P(3) = {(3,3,9,3), (3,6,6,3), (3,9,3,3)}
P(4) = {(4,4,8,4), (4,8,4,4)}
P(5) = {(10,5,5,5), (5,10,5,5), (5,5,10,5), (5,5,5,10)}
```

It follows that the cheapest bill puts the premium on the middle calls at
`m ≤ 4`, and on any one call at `m = 5`. #4279's completeness step is a finite
reduction to the middle letters, checked by its own computer search. No
outside check existed.

## Method

`R(n)` is the set of products of positive words with exactly `n_l` calls `l`,
in the lower unitriangular group mod `m`; call `l` adds row `l−1`, with its
diagonal 1, to row `l`.

- **Coset compression.** The adjacent entries of every element of `R(n)` are
  `n_l mod m`, so `R(n)` lives on the six other entries.
- **Recursion.** `R(n) = ⋃_l g_l·R(n − e_l)`.
- **Attainment.** `n` is attained for `c` exactly when `I + c·E[4][0] ∈ R(n)`.

This is a different route from #4279's middle-letter reduction. It runs over
every count vector with entries `≤ 3m`, which covers every member of `P(m)`.

## Results

For each `m` and each residue `c`, within the box:

- the minimal attained vectors are exactly #4279's `P(m)`;
- the attained set is exactly the multiples of `m` that dominate `P(m)`;
- `P(m)` does not depend on `c`.

| m | attained vectors per residue (box) | engine |
| --- | --- | --- |
| 2 | 36 | Python and C |
| 3 | 54 | Python and C |
| 4 | 72 | C |
| 5 | 80 | C (21 s, about 128 MB) |

**Bills.** #4279's four cheapest-bill formulas equal `min_{v ∈ P(m)} v·p` at
2,000 random positive rational price vectors. At unit prices this gives the
lengths 12, 18, 20 and 25.

## Not covered

- Vectors outside the box. #4279's reduction covers every length, and this
  check does not re-derive it.
- `m ≥ 6`, where #4279 cites #4263 (checked separately in
  [#4343](https://github.com/CrocSwap/integer-mult-bounds/pull/4343)).
- Any physical price.

## Reproduce

```sh
python3.12 -B research/depth4-count-vectors-check/verify.py
cc -O2 -DM=5 -o countdp research/depth4-count-vectors-check/countdp.c && ./countdp
```

The first prints `PASS_DEPTH4_COUNT_VECTORS_CHECK` in about 19 seconds,
using only the standard library. It reruns m = 2 and 3 in Python, and checks
that `evidence/COUNTDP-RUNS.txt` was recorded for this `countdp.c` (by
SHA256), agrees with Python at m = 2 and 3, and classifies correctly at m = 4
and 5. The C runs are local evidence; CI does not recompile them.

## Open next questions

None from this check.

## Credit

The model, the theorem, `P(m)` and the bills are Nick Petalas's (#4279,
building on #4249 and #4257). Prepared by Ryanson Jonathan with substantial
Claude Code (Claude Opus 5.5) assistance. Apache-2.0.
