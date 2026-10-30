# Exact contiguous helper storage: 5q versus peak 4q

For the eight fixed half-open lifetimes below, each width multiplied by any
positive real q, the minimum capacity for one fixed contiguous block per helper
is exactly **5q**. Freely split fixed slot sets need exactly **4q**. Thus even
complete advance knowledge of the lifetimes leaves a 25% contiguous-storage
surcharge and an additive gap q.

This is a scoped mathematical proof with finite corroboration. It gives an
explicit obstruction at the contiguous-block boundary excluded by Ali Romman's
[PR #5763](https://github.com/CrocSwap/integer-mult-bounds/pull/5763), head
`cee2336bc3a20c586b1dbb55152d97a114c657a6`. That allocator permits separated
ranges. Its theorem and implementation are cited, not audited or rerun here.
The general dynamic storage allocation problem is classical; this package
contributes this explicit scaled family and its exact optimum, not the general
observation that contiguity can cost space.

## Contract and instance

An address range is half-open. A helper keeps its assigned address range or
ranges throughout its lifetime. Simultaneously live helpers must have disjoint
address sets. Addresses lie in [0,H). Allocation before the run may use all
lifetimes. Movement during a lifetime is excluded. There is no alignment
restriction. With integer q, all displayed endpoints are integer addresses.

The table gives times, widths divided by q, a contiguous capacity-5q layout,
and a split capacity-4q layout. Every displayed address is multiplied by q.

| Helper | Lifetime | Width | Contiguous range | Split ranges |
|---|---|---:|---|---|
| A | [0,8) | 1 | [0,1) | [0,1) |
| B | [2,12) | 1 | [1,2) | [1,2) |
| C | [4,14) | 1 | [4,5) | [2,3) |
| D | [6,10) | 1 | [2,3) | [3,4) |
| X | [0,2) | 3 | [1,4) | [1,4) |
| Y | [2,4) | 2 | [2,4) | [2,4) |
| Z | [10,12) | 2 | [2,4) | [0,1), [3,4) |
| W | [12,14) | 3 | [0,3) | [0,2), [3,4) |

The loads on the successive intervals starting at times 0,2,4,6,8,10,12
are 4q,4q,3q,4q,3q,4q,4q. Hence the split layout attains the necessary peak
capacity 4q. The contiguous column directly proves an upper bound of 5q.

## Lower bound for arbitrary real addresses

First set q=1. Any real contiguous layout can be compressed to an integer
layout of no greater capacity. Order all helpers by their original bottom
address, breaking ties arbitrarily. For each helper in that order, put its new
bottom at the maximum new top among its earlier time-overlapping neighbors,
or at zero if there are none. These bottoms are integers. Induction shows that
each new bottom is at most its original bottom: each earlier overlapping top
was originally below this helper's original bottom. Every overlapping pair
keeps its order and remains disjoint. Therefore every new top is at most the
corresponding original top.

If a real layout had H<5, this compression would give integer capacity at most
4. A,B,C,D are simultaneously live on [6,8). Their four unit blocks must
therefore fill the four cells 0,1,2,3.

1. X has width 3 and overlaps A. Thus A occupies an end cell.
2. W has width 3 and overlaps C. Thus C occupies the other end cell, since A
   and C overlap each other.
3. Y has width 2 and overlaps A,B. Its two cells are exactly the eventual
   C,D cells, which must therefore be adjacent.
4. Z has width 2 and overlaps B,C. Its two cells are exactly the eventual
   A,D cells, which must therefore be adjacent.

D cannot be adjacent to both end cells of a four-cell line. This contradiction
excludes every H<5, including noninteger addresses. The displayed layout attains
5. Dividing all widths and addresses by any positive real q reduces the general
case to q=1, so the optimum is 5q.

No claim of a smallest obstruction by helper count, a worst-case approximation
ratio, or novelty of the general storage-allocation phenomenon is made.

## Evidence and reproduction

From the repository root, use CPython 3.12. The verifier needs only its standard
library and writes no files unless `--receipt` is supplied.

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/contiguous-helper-storage-gap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -O -W error -B research/contiguous-helper-storage-gap/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/contiguous-helper-storage-gap
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/contiguous-helper-storage-gap --check-source-history
```

Expected marker: `PASS_CONTIGUOUS_HELPER_STORAGE_GAP`. The replay checks both
layouts and every event load; all 8! = 40320 total address orders with exact
longest-path compression; and, independently, all 9216 integer placements at
capacity 4. The order enumeration returns minimum capacity 5. Exact rational
scales and invalid-layout controls check scaling, collisions, contiguity and the
half-open boundary. Normal and optimized commands use explicit checks, not
Python assertions. An optional generated receipt binds the package file hashes.
The written proof supplies the unbounded positive-real quantifier; the finite
checks do not replace it.

## Relation to current research

The selected baseline command passed with `PASS_RESEARCH_BASELINE_BINDINGS_ONLY`
at main `de5ec2e7a6074068452f45b1a191b5c72832df4a`, priority revision 8. It reported
selected kappa .00310045 and admitted BIT saving .0034. This was orientation,
not a supplier replay. The random picker suggested portable replay work; the
explicit boundary in #5763 supplied this mathematical side question instead.
The original card is preserved in TASK.json with `scope_status: changed`.

The result prevents a peak-width certificate from being transferred silently
to a fixed contiguous native interface. It does not establish that a selected
supplier requires contiguous blocks, infer any actual supplier's storage bill,
construct routes or cleanup, optimize chronology, or improve kappa. Physical
ownership, restoration, tape movement, precision and all-size compiler premises
remain outside the claim. No predecessor scientific replay was run.

## Open next questions

- Can one actual native caller use split fixed ranges with its complete route
  and address-description bill? Start with a source-pinned helper access trace
  and lower each split access. Safe lifetimes and a declared native interface
  are prerequisites.
- Can a restricted family of native helper lifetimes always attain peak width
  with contiguous blocks? First identify a source-derived interval restriction
  that excludes the eight-helper pattern. No such source restriction is assumed
  here.

The corresponding structured questions are in TASK.json. The first exact gap
was retained without expanding the construction search.

## Credit and implementation bounds

This result was produced by Nick Petalas. Ali Romman supplied #5763's split-range
interface and its explicit contiguity boundary. Its context credits the T74 pool
of #2655 and the owned-lifetime audit #5717; those results are not needed by this
self-contained proof. The general model is classical dynamic storage allocation,
as described by [Naor, Orda and Petruschka, 2000](https://cris.technion.ac.il/en/publications/dynamic-storage-allocation-with-known-durations-4/).
No predecessor code is copied. Apache-2.0.

The verifier uses no recursion or dynamic dispatch. Its finite inputs have eight
helpers, at most two address segments per helper, seven time slabs, 40320 total
orders and 9216 coordinate assignments. Each function stays below 60 lines.
Python allocates integers, tuples and dictionaries during replay, so fixed
allocation in Power of Ten rule 3 is a managed-runtime deviation. The enumerated
domains bound live state; no list of all orders or layouts is retained. Warning-
strict normal and optimized replays provide the available runtime diagnostics.
A static native implementation would require a separate fixed-storage review.
