# Two cuts exclude the proposed six-frame nonlinear seed

This scoped mathematical proof establishes the sharp rank-mass bound `s >= 2W`
for the six rational frames

```text
S = {0, I, J, J+I, B, B+I},
J = [[0,1],[-1,0]],       B = [[0,0],[-1,1]].
```

Five roles therefore require cost at least ten. Searching for a cost-nine
nonlinear circuit inside this alphabet cannot answer the open construction
question in Jose Manuel / jmbarrancoml's
[PR #1757](https://github.com/CrocSwap/integer-mult-bounds/pull/1757).
That source proposes `J` and `B` as a possible seed because they have no common
flag. The new result shows that this seed, with its identity translates and
`0,I` endpoints, still has a sharp cut obstruction. Larger frame alphabets
and arbitrary rational combinations of the seed matrices remain outside scope.

The new proof and checker were produced by Nick Petalas. Independent human and
formal proof-kernel review are unclaimed. No new kappa, supplier, selected-frontier
change or complete multiplication theorem is claimed.

## Contract and theorem

Use PR #1757's fixed finite acyclic pointwise circuit model. There are `W`
independent input symbols over one finite alphabet of size at least two. Every
required output is its prescribed input under one fixed role permutation `rho`,
on every assignment. Count all arbitrary dirty roles among these inputs.
Gates may be nonlinear and need only be deterministic. Each gate has one common
frame on all its ports; every source and sink also has a frame. All frames
belong to `S`. Charge every physical wire segment `e=(u,v)`, including terminal
and untouched wires, by

```text
r_e = rank_Q(M_v - M_u),       s = sum_e r_e.
```

For each demand `w`, require
`M_out(rho(w)) - M_in(w) = I`. There are no uncharged observations,
message-bearing side channels, postselection or input-dependent topologies.

**Theorem.** Every such circuit satisfies `s >= 2W`. Equality is attainable
within this class. Thus the five-role minimum is ten when topology may vary.

## Exact certificate and proof

Assign each frame two Boolean labels:

| Frame | First label | Second label |
|---|---:|---:|
| `0` | 0 | 0 |
| `I` | 1 | 1 |
| `J` | 0 | 0 |
| `J+I` | 1 | 1 |
| `B` | 0 | 1 |
| `B+I` | 1 | 0 |

In this frame order the complete rank-distance matrix is

```text
       0 I J J+I B B+I
  0    0 2 2  2  1  2
  I    2 0 2  2  1  1
  J    2 2 0  2  1  2
 J+I   2 2 2  0  1  1
  B    1 1 1  1  0  2
 B+I   2 1 2  1  2  0
```

Write `d_H` for Hamming distance between the two-bit labels. Every entry obeys
`d_H(labels(A),labels(C)) <= rank_Q(C-A)`. A two-by-two difference has rank two
when its determinant is nonzero, rank one when it is nonzero with determinant
zero, and rank zero otherwise. These rules verify the table directly.

The only ordered pairs in `S` with difference `I` are `(0,I)`, `(J,J+I)` and
`(B,B+I)`. All three have Hamming distance two. Each of the two labelings
therefore separates every prescribed source/sink demand.

Apply PR #1757's weighted partition theorem to these two unit-weight labelings.
Its cut inequality charges at least `W` crossing edges for each labeling.
The Hamming inequality bounds the sum of the two crossing indicators on any
edge by its rank charge. Hence

```text
s >= number of first-label crossing edges
   + number of second-label crossing edges >= W + W = 2W.
```

This is a new finite frame certificate applied to the cited cut theorem.
The conclusion covers every topology and number of gates satisfying the
contract; it is not an inference from a failed circuit search.

For sharpness, take `W` direct wires from source `w` to sink `rho(w)`, with
source frame `0` and sink frame `I`. Each wire costs two and copies its symbol.
For `W >= 3`, assign three source/sink pairs the three different identity-shift
types instead. This attains the same bound while using all six frames.
Sharpness is over this circuit class, not every fixed topology.

For every `0 < alpha < 1`, the normalized optimistic rank invoice satisfies

```text
(1/W) sum_e (r_e/2)^alpha >= (1/W) sum_e r_e/2 >= 1.
```

This alphabet therefore cannot give strict contraction under that invoice
before nonnegative implementation charges. This is a circuit-class
obstruction, not an integer-multiplication lower bound.

## Why this goes beyond a common flag

The commutator is `J B - B J = [[-1,1],[1,1]]`, of determinant `-2`.
A common invariant line over a characteristic-zero extension would let both
matrices be simultaneously upper triangular. Their commutator would then
have zero diagonal and determinant zero. They therefore have no such line.
A common affine frame offset does not help: differences from frame `0` would
still triangularize `J` and `B`. Thus the excluded alphabet has no common flag.
This certificate does not assert that all rank metrics admit these cuts.

## Reproduce and evidence

From the repository root, with CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/six-frame-seed-cut/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/six-frame-seed-cut/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/six-frame-seed-cut
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/six-frame-seed-cut --check-source-history
```

The verifier prints `PASS_SIX_FRAME_SEED_CUT` in a generated JSON receipt.
It checks all 36 ordered rank pairs by determinant and separate rational row
elimination, all three identity shifts, the explicit certificate, and all
4,096 assignments of two Boolean labels to six frames. Exactly sixteen
assignments obey the edge budgets and separate all identity demands in both
bits. Eleven controls reject malformed labels, changed edge budgets, changed
labels and incomplete/reordered endpoint lists. The commutator check confirms
the declared common-flag boundary. The receipt hashes all five package files
and the cited source bytes. Default replay writes no files, uses no Git or
external programs, and works in an export containing the declared input.

The finite checks certify the matrix table and cuts. The all-circuit statement
is the written application of the predecessor's theorem. The original theorem,
its circuits and reported counts are cited, not audited. No Lean, native
supplier or selected cold replay is run.

The checker uses fixed two-by-two matrices, six frames, at most 4,096 label
assignments and eleven controls. Every function is below sixty lines. Explicit
exceptions keep checks enabled under optimized Python. Python and `Fraction`
allocate dynamically; bounded finite data replace static allocation in this
offline checker. This managed-runtime deviation supplies no real-time or
physical-memory guarantee. Warning-strict runs are registered in
[VERIFY.json](VERIFY.json).

## Scope and attribution

[TASK.json](TASK.json) records the changed `bit-new-register-model` scope,
priority revision eight, the advance claim and stopping rule. The card's first
source-binding command passed. This side result addresses one nonlinear seed;
it does not implement the card's nonabelian native register program. Main was
pinned at `19fdb086ea96af9a9f87936a2b888e10af4ed810`. Exact predecessor and
historical card/selected-record pins are in [SOURCES.json](SOURCES.json).
Live open PRs, Discussions and cached overlap were checked; all main README
paths were additionally searched. Unpublished work and arbitrary code diffs
remain outside that coverage.

Jose Manuel / jmbarrancoml supplies PR #1757's nonlinear cut theorem, weighted
partition criterion and seed question. Navinor supplies PR #825's earlier
common-flag XOR obstruction. The retained upstream finite shear contract and
routing/cleanup lineage retain the credit stated in those sources.
CubeJerry's PR #907 distinguishes arbitrary rank metrics from cut metrics;
its counterexamples and distortion results are cited, not replayed. Cut
counting and rational matrix rank are classical methods. The new contribution
is this six-frame certificate, its all-topology application and checker.
No general literature-priority claim is made. Apache-2.0.

## Open next questions

1. Which added rational frame defeats this certificate and still permits a
   complete cost-nine five-role circuit? First include that frame and all new
   identity shifts in the weighted cut feasibility problem. Failure of these
   two cuts alone does not establish feasibility or exclude other cut bounds.
2. Can a complete nonlinear permutation circuit outside this alphabet achieve
   `s < 2W`? Publish the DAG, complete scalar truth table and every charged
   frame edge before claiming a gain. A physical implementation, complete
   invoice, compiler and outer admission remain separate obligations.

No follow-up is reserved. Structured first steps and blockers are in TASK.json.
