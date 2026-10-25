# One width-3 interior has boundary-order half-bandwidth 5

On an equal-weight path of bandwidth 3, deleting one interior and keeping
the survivors in increasing index leaves a Schur complement of
half-bandwidth 5. The same 5 occurs for interiors of length 3, 4, and 6.
The original-index span of the farthest new entry grows from 8 to 11.

No new kappa is claimed. This is one finite section, not an all-size
bandwidth theorem.

## Boundary order

`GAUSSIAN.md` says that interior neighbors are separated by `W`, so
eliminating interiors leaves a Schur matrix of bandwidth `O(W)` in boundary
order. `vendor/FINE-PRIME.md` says an eliminated interior joins only its two
neighboring `O(W)`-size separators. The order measured here is the
increasing order of the surviving indices.

The path has diagonal 1 and value `-1/12` at distances 1, 2, and 3. Its
off-diagonal absolute row sum is `1/2`. Four vertices sit on each side of
the interior, so each side has the three vertices that meet the interior
and one vertex farther out.

## The three interiors

| Interior | Farthest new entry | Boundary distance | Original distance |
| --- | --- | --- | --- |
| `{4,5,6}` | `-1/1560` between 1 and 9 | 5 | 8 |
| `{4,5,6,7}` | `-1/1404` between 1 and 10 | 5 | 9 |
| `{4,5,6,7,8,9}` | `-13/92380` between 1 and 12 | 5 | 11 |

On the length-4 interior the half-bandwidth is exactly 5. The row of vertex
0 in the complement equals its original row, so it has no entry to 8, 9,
10, or 11. The complement is the complementary block of the inverse. Its
upper triangle is

```
0-1: -1/12,  0-2: -1/12,  0-3: -1/12,
1-2: -32/351,  1-3: -43/468,  1-8: -1/468,  1-9: -1/702,  1-10: -1/1404,
2-3: -47/468,  2-8: -5/468,  2-9: -1/351,  2-10: -1/702,
3-8: -1/52,  3-9: -5/468,  3-10: -1/468,
8-9: -47/468,  8-10: -43/468,  8-11: -1/12,
9-10: -32/351,  9-11: -1/12,
10-11: -1/12.
```

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/boundary-order-width3/verify.py
python3 -B scripts/research_package.py --package research/boundary-order-width3
```

The verifier authenticates both pinned notes and checks the three
complements.

## Open next questions

These weights are constant on the band. The caller rows are truncated
Gaussians. One finite Gaussian section would show whether its farthest
separator entry stays nonzero.

## Credit

Cinna Davis wrote the boundary-order sentence in the PR4100 Gaussian note
and the separator sentence in its fine-prime note. The width-2 measurement
is the preceding audit. The width-3 complements are this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
