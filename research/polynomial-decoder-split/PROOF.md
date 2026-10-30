# Maximum split extraction by nested matroid intersection

## Statement

Let `H_0,...,H_(c-1)` be arbitrary `v` by `v` matrices over `F2`, with
`v,c >= 1`. A split consists of square nonsingular minors `H_a[U_a,W_a]`
whose original row sets are pairwise disjoint and whose original column sets
are separately pairwise disjoint. Its size is `sum_a |U_a|`. There is a
deterministic polynomial-time algorithm returning a maximum split and sets
`S,T` with

```text
size = 2v - |S| - |T| + sum_a rank H_a[S,T].                 (1)
```

The package implements this construction on the explicit capacity domain in
the README. This is a constructive specialization of classical induced
matroids and matroid intersection, not a new general min-max theorem.

## The two oracle levels

Let `X` and `Y` be row and column color copies, each indexed by `(a,i)`, and
let `H=blockdiag_a H_a`. Write `Q_X,Q_Y` for the partition matroids allowing
at most one copy of each original index.

For a row set `A subset X`, define `A` independent in `N` when there is a
`Q_Y`-independent set `B subset Y` such that `H[A,B]` is square nonsingular.
Schrijver's [Theorem 3.3](https://ir.cwi.nl/pub/9901/9901D.pdf#page=12)
states that a matrix linking system induces a matroid in this way. The
hypotheses hold here: `Q_Y` is a finite matroid, the linking system consists
of nonsingular submatrices of a single matrix over a single field, and the
empty pair is allowed. Thus `N` is a matroid, of rank at most `v`.

There is an explicit independence oracle for `N`. Restrict `H` to rows `A`
and regard its columns as a linear matroid `L_A`. Compute a maximum common
independent set of `L_A` and `Q_Y`. Its size is `rank_N(A)`: a common
independent column set of size `k` contains a nonsingular `k` by `k` minor
on some subset of `A`, and conversely every linked independent row subset
supplies such columns. In particular, `A` is independent precisely when
that size equals `|A|`. If `|A|>v`, the answer is immediately false.
For a set contained in one color, distinct original columns are automatic,
so ordinary row rank suffices. The executable uses this exact shortcut.
It also rejects a set immediately if its rows are dependent within any color:
those rows remain dependent in the full block diagonal matrix.

The outer computation intersects `Q_X` with `N`. For an optimal outer set
`A`, invoke the inner computation once more to recover a column set `B`
of size `|A|` with `H[A,B]` nonsingular. In a block diagonal matrix,
nonsingularity forces equal row and column counts in every color. Otherwise
a color with more rows than columns has dependent selected rows. The
determinant then factors into nonzero color-block determinants. The two
partition conditions give the required disjointness. Conversely every split
gives a common independent outer set. Hence this extracts a maximum split.

## The classical intersection subroutine

For two matroids `M1,M2` on `E` and a common independent set `I`, use the
following directed exchange graph. Sources are `x outside I` for which
`I+x` is independent in `M1`, and sinks are those for which it is independent
in `M2`. An arc `y -> x`, with `y in I` and `x outside I`, tests
`I-y+x` in `M1`. An arc `x -> y` tests that exchange in `M2`.

Breadth-first search returns a shortest source-to-sink path. Symmetric
difference with its vertex set preserves both independences and increases
size by one. This is the classical shortest augmenting-path theorem for
unweighted matroid intersection. The implementation also checks both
independences and the size increment after each augmentation.

If no path exists, let `R` be every vertex reachable from any source. Then

```text
|I| = rank_M1(E minus R) + rank_M2(R).                       (2)
```

For clarity, a standard span argument gives this terminal identity. Every
outside element not in `R` is spanned in `M1` by `I minus R`; otherwise it
would be a source or its fundamental circuit would give an arc from a
reachable member of `I`. Similarly each outside element of `R` is spanned
in `M2` by `I intersect R`, since it is not a sink and its entire fundamental
circuit is reachable along the `M2` arcs. These spans prove (2), because
the indicated subsets of `I` are independent. Shortest-path augmentation,
including the necessity of avoiding shortcuts, is the classical result
presented in [Goemans's notes, section 6](https://math.mit.edu/~goemans/18453S17/matroid-intersect-notes.pdf).
The code uses exactly the arc and source conventions above.

## Recovering an original-index cut

At outer termination, set `D=X minus R`. Equation (2) reads

```text
P = rank_QX(D) + rank_N(X minus D),
```

where `P` is the maximum split size. Saturate `D` by deleting every color
copy of each original row represented in `D`. This preserves its partition
rank and can only decrease the induced rank on the complement. Every such
rank sum still upper-bounds the outer optimum by matroid weak duality, so
the sum remains exactly `P`. If `S` is the set of original rows not deleted,
we now have

```text
P = v - |S| + rank_N(copies(S)).                            (3)
```

Run the inner intersection on all rows `copies(S)`, using `M1=L_copies(S)`
and `M2=Q_Y`. Let `R_Y` be its terminal reachable set. By (2),

```text
rank_N(copies(S)) = rank H[copies(S),Y minus R_Y]
                    + rank_QY(R_Y).
```

Saturate `R_Y` by adding every column copy of each represented original
column. The partition rank is unchanged; the remaining matrix rank can only
decrease. Matroid weak duality again prevents strict decrease of the sum.
Writing `T` for the original columns not represented in `R_Y` gives

```text
rank_N(copies(S)) = sum_a rank H_a[S,T] + v - |T|.
```

Substitution in (3) proves (1). Both saturations use whole original-index
groups. No equality between row and column cuts, or between selected row and
column indices, is assumed.

## Independent certificate soundness

Any split and any `S,T` satisfy the upper bound in (1). Deleting rows outside
`S` and columns outside `T` from each packed minor reduces rank by at most
the number deleted. The disjointness conditions charge each original row
and column at most once. The surviving rank is bounded by the corresponding
`H_a[S,T]` rank, and summing proves the bound. Therefore nonsingular disjoint
minors and an equal-valued cut certify optimality without trusting either
intersection routine, its matroid interpretation, or a general min-max
implementation. `certify` implements this check. The verifier independently
checks every returned certificate using permutation determinants for the
exhaustive small domain and dense binary row operations on larger fixtures.

## Termination and resource bounds

Put `N=cv`. Each intersection has at most `v` augmentations and one terminal
graph. A graph construction makes `O(N^2)` independence queries, stores at
most `N^2` arcs, and searches each vertex at most once. Only four specific
oracle roles occur: a row partition, the induced row oracle, a column linear
oracle, and a column partition. The inner linear rank uses at most `N`
vectors of at most `N` bits. Direct elimination costs `O(N^3)` bit operations.
An inner run therefore costs `O(N^6)` bit operations. The outer run makes
`O(N^3)` oracle calls, giving the conservative bound `O(N^9)` overall.
This bound includes graph construction and additional certificate checks;
it is an upper bound rather than a measured or optimized runtime claim.

The outer routine computes its induced-matroid answers before constructing
each exchange graph. The graph then consults a bounded lookup table. Inner
calls therefore finish before the outer graph call begins, with no recursive
call cycle through the shared graph routine. There are at most `N(v+1)`
table entries per round, each keyed by at most `v+1` indices. The table is
discarded after the round, giving `O(N^3)` stored indices and `O(N^2)` vector
bits, plus graph/object overhead. No cache grows across rounds. The executable
checks `v<=32`, `c<=8`, and `N<=96` before any graph construction. All
iteration bounds follow from these dimensions, `capacity+1` graph rounds,
or bounded permutations/subsets in the verifier. It writes no artifacts.

## Implementation constraints

Power-of-Ten deviations are confined to the managed Python implementation.
Rule 3, fixed allocation, cannot hold literally because Python allocates
integers and collections during exact rank and set operations. The explicit
input capacities, no persistent cache, polynomial live-state bound and
serial oracle lifetimes and per-round table bound this allocation. A fixed-buffer implementation
would be the next step if hard memory guarantees were needed.

Rules 8 and 9 permit the verifier's explicit local import and the four named
oracle roles plus their finite lookup adapter as documented deviations. The local import loads only
this package's `solver.py`, supports isolated `-I` execution, and is recorded
by the generated source hashes. The callbacks implement the classical
two-matroid oracle contract with no runtime registration or user-supplied
code. Replacing them with specialized duplicated routines would add scope
without changing their finite target sets. Normal and optimized warning-strict
replays exercise every target. No native compiler diagnostics apply; Python
warning-strict execution and package/source-history checks are the available
diagnostics. No unrelated shared code is changed.

Produced by Nick Petalas. Classical results and predecessor credit are given
in the README. Independent human and formal proof-kernel review are unclaimed.
