# Characteristic-four blocks of depth two carry at most four sources

Claim type: a finite exhaustive census supporting a scoped obstruction. This
blocks the direct construction of ten sources from two depth-two five-source
blocks. It does not exclude a ten-source depth-four walk.

A characteristic-four block is a word in which each of k source labels occurs
exactly four times. Its raw prefix counts are Q_t in {0,1,2,3,4}^k. Depth at most
two means every nonzero binary mask m equals Q_a + Q_b modulo four for some
0 <= a <= b <= 4k. Boundary zero pads a one-read representation; the final
boundary can be identified with zero for evaluating residues.

## Census and symmetry

Relabelling sources preserves the property, so enumerate words with source
labels ordered by first occurrence. This is one representative for each source
permutation orbit. The number of canonical words is

    (4k)! / ((4!)^k k!).

For k=5 this is 2,546,168,625. No rotation or reversal quotient is used.

A search state is a word prefix of length d, its current raw count vector n,
the set of previous raw prefix vectors p, and the binary masks already served
by a pair of previous boundaries. Each child increments one coordinate n_j<4;
a previously unused label can be introduced only when every lower label has
already been introduced.

## Safe future-cut relaxation

For any unserved mask, a future representation has either two boundaries at
or after the current boundary or one previous and one future boundary.

If both boundaries are future and n_j >= 3, their two raw counts on source j
are each >=3 and <=4. Sums 6,7,8 yield binary residue only at 8, with bit zero.
Consequently all masks represented by two future boundaries belong to the
subcube fixing bit zero on every coordinate with n_j>=3. This is an
*overapproximation*: further restrictions are intentionally ignored.

For a fixed earlier boundary p, a future boundary has a raw count r_j with
n_j <= r_j <=4. Since p_j <= n_j, possible binary bits are exactly the table
below. The row p_j=3 has no possibilities.

| Earlier raw count p_j | Possible bit zero | Possible bit one |
|---|---|---|
| 0 | always, via future count 0 or 4 | only if n_j<=1, via future count 1 |
| 1 | only if n_j<=3, via future count 3 | always, via future count 4 |
| 2 | only if n_j<=2, via future count 2 | only if n_j<=3, via future count 3 |
| 3 | impossible | impossible |
| 4 | always, via future count 4 | impossible |

For example, when p_j=2 and n_j=3, only bit one remains possible; when n_j=4,
neither bit remains possible. The Cartesian product of these per-coordinate
sets is another overapproximation, since it ignores whether one future
boundary can realize all coordinate counts simultaneously in a fixed suffix.

Take the union of the already served masks, the two-future-boundary subcube,
and these one-old/one-future subcubes for every old p. If it omits any mask,
no continuation of this prefix can reach depth two. Pruning that subtree is
sound. Prefixes containing a count 3 can be omitted from the old-boundary
list because their row in the table has no allowed bit.

## Exact accounting

Suppose h labels have appeared. A canonical prefix has

    (4k-d)! / ((k-h)! product_j (4-n_j)!)

canonical completions. The division by (k-h)! permutes only the unseen labels;
each full word on those labels has one first-occurrence ordering. At each
pruned subtree, add this quotient to the accounted count. For a coverage threshold T, if at least T masks have
already been served, every continuation remains a solution, so the same
quotient counts solutions. Prune when the future-possible union has fewer
than T masks. This is the same safe relaxation with a cardinality target. Otherwise visit its children. Matching the accounted total to
the closed-form family size is an additional census control.

## Sharp maximum and complete catalog

The replay counts masks including zero. Threshold 30 has no solution, and
threshold 29 has exactly four canonical solutions. Thus the maximum number
of nonzero masks is 28, and MAXIMIZERS.json is complete up to source
relabelling. The verifier directly checks all four distinct canonical words,
all missing-mask sets and their four permutation rounds. No rotation or
reversal symmetry is assumed.

The threshold-30 census visits 8,462,068 nodes and prunes 6,451,947 subtrees.
The threshold-29 census visits 8,715,495 nodes and prunes 6,632,616 subtrees.
Both account for all 2,546,168,625 canonical words. The full-coverage mode is
retained as a control, and the k=4 census gives 421 solutions among
2,627,625 canonical words. The unpruned calibration rows
(k, canonical words, full-cover solutions) are (1, 1, 1), (2, 35, 33) and
(3, 5775, 547). Every threshold is compared with the unpruned histogram at
these small sizes, giving 14 threshold comparisons.

## Optional independent native replay

The registered standard-library verifier needs no compiler. The separately
written raw-coordinate engine is retained for independent opt-in replay.
The second CLI argument enables pruning and the third is the mask threshold,
including zero. From the repository root:

```sh
cc -O3 -Wall -Wextra -Werror -pedantic -std=c11 research/connector-char4-floor-obstructions/independent_depth2.c -o /tmp/imb-depth2-independent
/tmp/imb-depth2-independent 5 1 30
/tmp/imb-depth2-independent 5 1 29
/tmp/imb-depth2-independent 4 0 16
```

It recomputes the sharp counts and every depth-histogram entry independently.
The four-source command accounts for every canonical word with negative
feasibility pruning disabled and returns 421 solutions. Already-satisfied
prefixes may still aggregate their canonical completions. Native output is a cross-check; the general pruning proof and
canonical accounting remain part of the scoped finite claim.

## Consequence

Source deletion preserves depth at most two: erase the four events of an
unwanted source and project the readout boundaries. Therefore failure at
five sources excludes every larger depth-two block. Four sources are
attained by two concatenated two-source depth-one blocks from #4248, so the
maximum depth-two source count in characteristic four is exactly four.
This does not exclude a coupled ten-source depth-four walk. Depth-three
seven-source blocks remain open.
