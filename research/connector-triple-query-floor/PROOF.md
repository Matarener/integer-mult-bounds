# Proof notes: triple steps and the five-source query floor

The verifier enumerates sets. This note records the inequalities those
numbers are attached to. It is not a second census.

## Prefix length

A closed walk of `L` steps has `L + 1` prefix positions with the last equal
to the first, so its image `P` satisfies `|P| <= L`. Each unordered pair of
distinct prefixes contributes one difference. Covering 31 nonzero masks
requires `C(|P|, 2) >= 31`. `C(8, 2) = 28` is short, so `|P| >= 9` and
`L >= 9`.

`P XOR P` is unchanged by adding a constant to every prefix. For any
nonempty `P` and any `t in P`, the translate `P + t` contains `0` and has
the same difference set. The sets that contain `0` are therefore enough.
There are `C(31, 8) = 7,888,725` of them. The program finds that none is a
difference basis of `F_2^5`, and that 28 is the maximum number of distinct
nonzero differences. Including `0` gives at most 29 of the 32 masks, which
matches the maximum stated by the pair-source package. Hence `|P| >= 10`
and `L >= 10`.

Each of the 31 outputs still needs two readout calls. The query count is at
least `62 + L >= 72`. The bound never inspects the Hamming weight of a
step. Weight 3, 4, and 5 are included.

## Leaves at length 10

An unused source keeps every difference inside a coordinate hyperplane,
which has 15 nonzero vectors. Every source incidence `m_j` is therefore a
positive even integer, so `m_j >= 2` and `W = sum m_j >= 10`.

`W` is also the sum of the `L` step weights. For `L = 10`, that sum equals
10 only if every step has weight 1. A step of weight at least 2 forces
`W >= 11`. Even summands make `W` even, so `W >= 12`.

The only nondecreasing 5-tuple of even integers `>= 2` summing to 12 is
`(2, 2, 2, 2, 4)`. Against prices `(1, 4, 10, 16, 28)`, the cheap assignment
costs `4*1 + 2*(4+10+16+28) = 120`. A length-10 step has weight at most 5,
so `W <= 50`. The verifier enumerates every admissible multiplicity type
for each even total from 14 through 50. Each of those bills is at least
122.

The published 10-point set covers. Whether a triple-using walk meets leaf
bill 120 is left open. The query lower bound does not depend on that
witness.
