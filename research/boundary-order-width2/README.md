# One width-2 interior has boundary-order half-bandwidth 3

On an equal-weight path of bandwidth 2, deleting one interior and keeping
the survivors in increasing index leaves a Schur complement of
half-bandwidth 3. The same 3 occurs for interiors of length 2, 4, and 6.
The original-index span of the farthest new entry grows from 5 to 9.

No new kappa is claimed. This is one finite section, not an all-size
bandwidth theorem.

## Boundary order

`GAUSSIAN.md` says that interior neighbors are separated by `W`, so
eliminating interiors leaves a Schur matrix of bandwidth `O(W)` in boundary
order. `vendor/FINE-PRIME.md` says an eliminated interior joins only its two
neighboring `O(W)`-size separators. The order measured here is the
increasing order of the surviving indices.

The path has diagonal 1 and value `-1/8` at distances 1 and 2. Its
off-diagonal absolute row sum is `1/2`. Three vertices sit on each side of
the interior, so each side has the two vertices that meet the interior and
one vertex farther out.

## The three interiors

| Interior | Farthest new entry | Boundary distance | Original distance |
| --- | --- | --- | --- |
| `{3,4}` | `-1/504` between 1 and 6 | 3 | 5 |
| `{3,4,5,6}` | `-1/1664` between 1 and 8 | 3 | 7 |
| `{3,4,5,6,7,8}` | `-121/887692` between 1 and 10 | 3 | 9 |

On the length-4 interior the half-bandwidth is exactly 3. The vertex at 0
has no Schur entry to 7, 8, or 9. The complement is the complementary block
of the inverse. Its upper triangle is

```
0-1: -1/8,   0-2: -1/8,
1-2: -239/1664,   1-7: -5/1664,   1-8: -1/1664,
2-7: -121/14976,  2-8: -5/1664,
7-8: -239/1664,   7-9: -1/8,
8-9: -1/8.
```

## Reproduce

From the repository root, standard-library Python 3.12 or newer:

```sh
python3 -I -B research/boundary-order-width2/verify.py
python3 -B scripts/research_package.py --package research/boundary-order-width2
```

The verifier authenticates both pinned notes and checks the three
complements.

## Open next questions

The same path at width 3 is not measured here. One interior of length 4
would show whether the half-bandwidth is 5.

These weights are constant on the band. The caller rows are truncated
Gaussians.

## Credit

Cinna Davis wrote the boundary-order sentence in the PR4100 Gaussian note
and the separator sentence in its fine-prime note. The length-9 arc audits
left this measurement open. The width-2 complements are this audit.

Prepared by jwr with substantial Cursor agent assistance. No independent
human review is claimed. Apache-2.0.
