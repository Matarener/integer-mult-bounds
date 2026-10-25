# One-point pair ceiling on n=7 weight splits

**Negative result.** On every basic-identity survivor in `F_2^7`, the coset-wide
one-point completion of the pair product is at least `need`. The strict test
that rejects a branch when every missing parity-legal point leaves the product
below `need` therefore deletes nothing. The bound is realized at `(9,9)`.

Selected frontier, κ, and `f(7)` are unchanged. A finite certificate is not a
length-22 census and not a multiplication theorem.

Original card: `census-pruning-audit` (priority revision 6, base
`bb4bccbf42844d2801487450727c2f63e10d1d0f`). Scope is **refined**. The card's
first experiment, the word `01021323`, is already in open PRs #3821 and #3699.
This package takes the next uncovered obligation from the length-22 handoff: a
partial form of the pair identity in
[MATH.md](../f7-weight-parity-census-correction/MATH.md) section 3. The delivered
form is the exact one-point window, not another enumeration. Details, the
monotonicity case split, and the witness are in [PROOF.md](PROOF.md). Source
pins are in [SOURCES.json](SOURCES.json).

## Result

For a surviving split `(s, t)`, with `E` already of size `s` and `O` of size
`t - 1`,

```
max_{p not in O} (S + f(p)) >= need = ceil((s*t - Q) / 2),
```

where `Q = 64`, `S` is the partial pair product, and `f(p)` is the product added
by one new odd point. The missing point may sit on either side; both
orientations are rows.

The proof has four pieces.

1. Inserting `p` increases the product by `f(p) = sum_{q in O} A_{p xor q}`.
2. `sum f = |O|·C(|E|,2)` over the odd coset and `sum f = 2S` over `O`, so the
   outside average is exact.
3. `S` is at least the integer flattening bound coming from `sum C(r_y, 2) = 2S`.
4. While at least two outside points remain, that lower bound is weakest at the
   smallest admissible `S`, because raising `S` by one drops the ceiling by at
   most one.

Every survivor with both parts at most 64 satisfies the resulting inequality
(3820 rows). In the parts-at-most-11 window the bound is:

| split | need | h | split | need | h |
|---|---:|---:|---|---:|---:|
| (6,11) | 1 | 3 | (10,8) | 8 | 9 |
| (7,10) | 3 | 4 | (10,9) | 13 | 15 |
| (7,11) | 7 | 7 | (10,10) | 18 | 20 |
| (8,10) | 8 | 9 | (10,11) | 23 | 26 |
| (8,11) | 12 | 13 | (11,6) | 1 | 5 |
| (9,9) | 9 | 9 | (11,7) | 7 | 7 |
| (9,10) | 13 | 15 | (11,8) | 12 | 14 |
| (9,11) | 18 | 20 | (11,9) | 18 | 20 |
| (10,7) | 3 | 5 | (11,10) | 23 | 27 |
|  |  |  | (11,11) | 29 | 33 |

`(8,9)` and `(9,8)` never enter the table: `B0 = 1` and `need = 4`.

### Equality witness

`E = {0, 3, 5, 9, 10, 33, 34, 40, 43}` and
`O = {1, 4, 16, 21, 64, 69, 81, 84}` have `|E| = 9`, `|O| = 8`, `S = 4`, and
`f(p) = 5` at every remaining odd point. Every one-point completion has product
9, which equals `need` for `(9,9)`. `O` is rebuilt by a deterministic greedy
scan (increasing odd pool, strict improvement of `(S, max f, index)`). Replacing
`84` by `2` moves the ceiling to 17.

`(7,11)` and `(11,7)` meet `need` only after the integer ceiling. The floor of
the same quotient is 6, which is below 7. No realized set is claimed for those
two rows. `(9,9)` divides exactly, so the floor swap does not move it.

## Limitations

- The maximum is over the whole odd coset. A prefix walk can add only a neighbor
  of the current vertex, and that smaller maximum can still lie below `need`.
- States in which both sides are more than one point short are not bounded here.
- The `F_2^4` check of `sum C(r_y, 2) = 2S` repeats a lemma already in PR #3827.
  The new exhaustive checks are the sums of `f` and the completion increment.
- The `(9,9)` witness is a parity-legal pair of sets, not a prefix walk. It shows
  the coset-wide one-point test is sharp. It is not a counterexample to a
  walk-level exclusion. PR #3818 claims a different union-support exclusion of
  `(9,9)`, and PR #3731 claims census exclusions of `(11,7)`, `(10,8)`, and
  `(11,8)`. This package does not confirm or revisit those claims.
- The word `01021323` is recomputed only as a fixture of the pinned MATH.md
  example (weight split `(4,4)`, bit-0 split `(6,2)`, excess 8). It is not a new
  reconstruction.
- No length-22 census was run. Nothing here places `f(7)` in `{22, 24}`.

## Reproduce

Python 3.12, standard library only, from the repository root:

```sh
python3 scripts/research_package.py --package research/f7-one-point-pair-ceiling --check-only
python3.12 scripts/research_package.py --package research/f7-one-point-pair-ceiling
```

`verify.py` recomputes the survivor table, the monotonicity residues, the
witness and its greedy odd set, exhaustive subset checks for `n = 3` and `n = 4`,
and the `01021323` fixture. `test_verify.py` repeats the `(9,9)` and `(7,11)`
arithmetic with literals, rejects the floor swap, and rejects the edited witness.
Checks raise `CheckFailure` rather than using `assert`.

## Open next questions

1. Does the same ceiling, restricted to the `n` hypercube neighbors of the current
   prefix vertex, fall below `need` on any open length-22 split? The coset-wide
   maximum is an upper bound on that walk-legal maximum, so a neighbor
   restriction can still prune. First step: on one open split, evaluate `S + f(p)`
   only at the neighbors of each vertex of an explicit partial prefix whose
   coset-wide ceiling equals `need`. Blocked here because legal extensions are
   walk steps and this package does not search walks.
2. Does an exact two-point completion ceiling strictly prune `(9,9)`? One point
   before the leaf is the strongest exact window that still never prunes. First
   step: lower-bound `S + f(p) + f(r) + A_{p xor r}` over odd pairs outside a
   7-point odd set paired with a 9-point even set. A greedy sample reached 17,
   above `need` 9, and that sample is not a lower bound.

## Credit

The pair identity, the basic row test, and the word `01021323` come from Nicholas
Stone's package `research/f7-weight-parity-census-correction` (substantial
OpenAI Codex assistance; Apache-2.0). The length-22 partial-identity request is
the handoff in discussion #1166. Parallel census PRs #3821, #3699, #3827, and
#3818 were left in place. Prepared by unpaidmoon with substantial AI assistance
(Cursor Grok), including the averaging argument and this verifier. No independent
human or formal-kernel review.
