# Independent review of the common-map tensor-pairing bound

**Audit confirmation. No new decoder, supplier or kappa.** Selected conditional
kappa stays `0.001672660197076918`.

This package re-derives the argument in sections 2–5 of
[PR #3928](https://github.com/CrocSwap/integer-mult-bounds/pull/3928), head
`2b2daaecac95e1048923d22fda51ccd01780565f`, the review requested by
[discussion comment 19030180](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19030180).
It does not import that pull request's code. The claim under review stands:
no counterexample turned up.

## What was checked

Let `G0 = [[2, 1], [1, 2]]` and `G4 = G0` tensored with itself four times,
indexed by 4-bit words. Then `G4[i, j] = 2^(4 - d(i, j))`. The pairing
`B[i, j] = (G4[i, j] + 1) mod 2` is 0 exactly on the complement `j = i xor 15`,
and 1 elsewhere, including the diagonal.

Over `F2`, `B` squares to the identity. Both scanners multiply the 16 by 16
matrix; the primary also row-reduces it. The rank is 16. A bilinear pairing of
9-bit labels has matrix rank at most 9, for any source map, reader map and
bilinear form. The full sixteen-point pairing therefore does not embed in the
nine-bit alphabet.

For a principal set `S`, write `p` for the number of included complement pairs
and `s` for the number of singletons. The primary scanner checks all 65,536
subsets. The rank is `2p` when `s = 0` and `2p + 1` when `s > 0`. The largest
set with rank at most 9 has size 12.

A common injective map into norm-2 E8 root lines is stricter. Distinct lines
have doubled inner products in `{-4, 0, 4}`; the scanner checks every pair
among the 120 lines. Pairing 1 forces orthogonality and pairing 0 forces inner
product `±1`. The complement relation is a matching, so the real Gram matrix
is block diagonal with blocks `[2]` and `[[2, ε], [ε, 2]]`, `ε ∈ {-1, 1}`.
Those blocks have eigenvalues 2, and 1 and 3. The Gram matrix is positive
definite of rank `|S|`. The roots lie in `R^8`, so `|S| ≤ 8`.

The bound is attained by eight explicit roots in the 112-line complement of
the coordinate frame `{±e_{2i} ± e_{2i+1}}` (eight lines). Their within-pair
products are `±1` and every cross-pair product is 0, matching `B` on tensor
indices `(0, 15, 1, 14, 2, 13, 3, 12)`.

## Scalar mismatch

The predecessor identity is `D T^T = 2 G4`. Indices 0 and 1 are a cross pair
of this witness, so the root Gram entry is 0, but `G4[0, 1] = 8`. The required
coefficient is 16. Dividing the Gram by 8 leaves coefficient 2, still not 0.
Restricting the tensor factors to this geometric witness does not give the
tensor scalar identity. The second scanner recomputes the same three numbers.

## Scope challenges that did not become counterexamples

Injectivity is necessary for the eight-point statement. Tensor indices
`(0, 15, 1, 2, 3, 4, 5, 6, 7)` preserve `B` when 0 and 15 go to the distinct
lines `e0 - e2` and `e0 - e3` and the other seven indices share the line
`e1 - e4`. All three lines lie in the 112-line complement. Dropping
distinctness really does admit nine indices.

Different source and reader maps are outside the Gram argument. The proof
already says so. The size-12 rank-screen witness is not a missed common-map
embedding: its four singleton rows, restricted to the set, are identical, and
the restricted pairing has rank 9. Equal rows of a rank-9 Gram matrix
`A H A^T` force those labels to coincide once `H` is invertible and the rows
of `A` span `F2^9`. Separately, indices
`(0, 15, 1, 14, 2, 13, 3, 12, 4)` do have nine distinct rows and nine distinct
abstract labels `(508, 506, 496, 488, 448, 416, 256, 128, 511)`. E8 geometry,
not binary rank, is what excludes that nine-point set.

## What was not checked

PR #3566's root-to-port bijection and the selected archive's port labels were
not re-derived. "Attained at selected port indices 0, 76, 28, 86, 103, 17, 10,
11" remains a claim of PR #3928. This review shows the eight roots lie in the
standard 112-line complement, which is the geometric model of P112, not that
those integers are the archive's port numbers.

No separate-map search, no dirty-input decoder, no COPY bill, no supplier and
no new kappa. The eight-term all-pairs floor is untouched.

## Reproduce

Python 3.12, standard library, from the repository root:

```sh
python3.12 -B research/tensor-pairing-common-map-review/verify.py
python3.12 -B research/tensor-pairing-common-map-review/independent.py
python3.12 -B research/tensor-pairing-common-map-review/test_verify.py
python3.12 -B scripts/research_package.py --package research/tensor-pairing-common-map-review
```

Expected markers:

```text
PASS_TENSOR_PAIRING_COMMON_MAP_REVIEW full_rank=16 subsets=65536 rank_screen_max=12 common_map_cap=8 witness_gram_rank=8 scalar_before=16 scalar_normalized=2 root_entry=0 abstract_labels=9 noninjective_indices=9 no_new_kappa
PASS_TENSOR_PAIRING_COMMON_MAP_REVIEW_INDEPENDENT square=I16 witness_cross=0 coefficient=16 normalized=2 labels=9 no_new_kappa
PASS_TENSOR_PAIRING_COMMON_MAP_REVIEW_TESTS controls=3
```

Ordinary replay is read-only. On CPython 3.12.3 the three direct commands
finished in under a second.

## Open next questions

1. Can two different 9-bit maps embed one principal set of size 9 through 12
   and still match `2 G4`? The common-map cap does not forbid it. A first step
   is one fixed nine-point index set. A label pair is not yet a decoder.
2. Do other common injective eight-point witnesses also miss `2 G4` on a cross
   pair, or is the mismatch special to this frame? Classifying them needs the
   PR #3566 port pin before the selected labels can be cited.

## Credit

The theorem and the eight-root witness are ToikY's PR #3928, following
homelab-05 / 1337isnot1337 PR #3895 and Gonzalo Mier's PR #3566 port bijection.
The E8 frame convention follows the retained P112 model. This re-derivation
was prepared by unpaidmoon with substantial Cursor Grok assistance. It is not
an independent human or formal-kernel review. Apache-2.0.
