# Complete whole-group cost stage

This is the finite cost stage for the 135 remaining support classes in
`SUPPORT-TRANSFER.json`. Together with that file's separately checked catalogue
and transfer reductions, it excludes a saving from replacing any three literal
canonical projectors by at most five rational rank-one terms. It does not exclude
larger replacements, changes of fitting matrix or physical cover, or a global
decoder below 334. It neither improves the multiplication bound nor certifies a
new value of kappa.

All programs here use only Python's standard library and make no network calls.
They read pinned scientific inputs from the repository. The certificate is
`COSTS.json`; its 6,075 claimed minima and compact coverage digests are independently
recomputed, not accepted as lower bounds merely because they are stored.

## Physical geometry and complete orientations

The pinned `research/p112-rational-decoder-gate/CANDIDATE.json` partitions the
112 ports into one residual line G0 and 37 orthonormal triads. Its 57 disjoint
canonical projector supports come from the three matching axes of each of 18
paired triads, the three individual axes of G37, and the residual port added to
target 21 (zero-based). The independent replay reconstructs these supports from
the group lists and compares them with the literal candidate. The primary replay
reads the literal support list directly.

For physical group subsets A and B, the charge is the binary rank of their
**complete group-span pairing**. It is not the rank of the selected ports alone.
The sum of the 57 original charges is 334. Repeated physical groups among the
three targets are retained and unioned, and G0 always has dimension one.

There are 29,260 unordered literal target triples. Targets with identical ordered
physical-group signatures have the same cost problem; sorting those signatures
gives 1,519 classes, retaining their multiplicities. Each class is expanded through
all six target orders. Thus the replay covers 9,114 oriented signature cases and
175,560 ordered literal triples. A first-appearance numbering of physical groups,
together with each group's dimension, gives 45 incidence shapes. In particular,
reordering targets is not silently discarded as a presumed symmetry of a marked
support class.

For every signature geometry, compute the tariff matrix on all subsets of its
physical groups. There are 2,202 distinct physical spans across these cases. For
each incidence shape take the entrywise minimum of all its oriented matrices.
The 45 resulting matrices have 93,780 entries in total. This lower envelope is
optimistic: different entries can attain their minima in different geometries.
It is a valid cost lower bound, but an inexpensive assignment in it is not a
construction in any actual geometry.

The primary implementation obtains canonical binary bases and computes Gram
ranks by elimination. The independent implementation instead represents a span
by its annihilator, as a 512-bit set of vectors in F2^9. Unioning spans intersects
their annihilators. It computes

    rho(L,R) = dim(L) - dim(L intersect R-perp)

by exact set intersections and cardinalities, and checks the symmetric formula
with L and R exchanged. It imports none of the primary implementation.

## Enumerating every allowed support invoice

For each marked support class, each target port independently chooses one of its
listed inclusion-minimal source supports and one of its inclusion-minimal reader
supports. For every query term, union the physical groups containing those ports.
The source and reader states are five-tuples of physical-group masks. Repeated
groups across targets are unioned before any cost quotient. Zero support outside
the three targets is sufficient by the separate support-reduction proof.

Larger supports cannot lower a whole-group pairing rank, so minimal supports
suffice. Duplicate states are removed. States may also identify masks having
identical full tariff rows: symmetry ensures their columns are identical as well,
so this quotient preserves every complete source-reader invoice. In particular,
the quotient is not applied before physical union operations.

For every pair of source state L and reader state R, price exactly

    sum(t=0..4) tariff(L[t], R[t]).

There is no heuristic search, floating point, or early exit on a merely feasible
value. Each stored minimum is checked both as a lower bound for every state pair
and as an attained value among those combinatorial states. Attainment here means
an invoice in the support-state relaxation; a nonrepresentable matroid is never
thereby claimed to yield a rational decoder.

## Complete screen and actual-geometry follow-up

All 45 times 135 = 6,075 envelope minima are checked exactly. Of these, 6,015 are
at least the corresponding canonical three-target invoice. The remaining 60
shape/class cells require actual-geometry pricing.

Regenerate every actual oriented matrix belonging to those open shapes, quotient
only identical complete matrices within the same shape, and preserve case
multiplicities. This gives 7,542 distinct matrices covering 8,466 ordered signature
geometries. Combining them with the relevant open support classes yields 27,304
jobs. Every exact minimum equals its original three-target invoice. There are
therefore no cheaper support assignments in any remaining cell.

The actual-coverage digest binds every sorted tuple `(shape, full-matrix SHA256,
multiplicity)`. The minima digest binds every sorted `(shape, matrix SHA256,
support-class index, exact minimum)`. The verifier first regenerates the full
universe and checks its counts and coverage; a digest of a selected subset is
insufficient. Likewise each envelope binds its incidence, dimensions, geometry
multiplicity, literal multiplicity, original charge and full matrix digest.

## Carry-free integer checks

The programs enumerate the same full Cartesian set of state pairs as scalar
arithmetic would. They encode many independent right-state invoices in one large
integer to keep a standard-library replay practical. Every tariff is between zero
and nine, so a five-term invoice c lies between zero and 45.

The primary implementation uses eight-bit lanes. For a claimed minimum m,
`127+m-c` has its high bit clear exactly when c is at least m; `128+m-c` has its
high bit set exactly when c is at most m. Each guarded digit lies between 82 and
173, so subtraction causes no inter-lane borrow. It checks the first condition
in every lane of every row and the second condition in at least one lane.

The independent implementation uses seven-bit lanes and additive guards.
`c+64-m` has its high bit set exactly when c is at least m; `c+63-m` has its high
bit clear exactly when c is at most m. These digits lie between 18 and 109, so
there is no inter-lane carry. All input ranges are checked explicitly, including
under `python -O`; scientific checks do not use removable assertions.

The cost controls compare both implementations with direct scalar Cartesian
minima on 82 deterministic small cases, including costs zero and 45. Each engine
must reject both an understated and an overstated minimum. Additional controls
reject omission of five target orientations, replacing the residual line's
dimension by three, deleting an incidence shape, and changing a tariff entry.

## Replay

From the repository root:

```sh
python3 -I -O -B research/p112-triad-matroid-boundary/costs.py
python3 -I -O -B research/p112-triad-matroid-boundary/independent_costs.py
python3 -I -O -B research/p112-triad-matroid-boundary/test_cost_controls.py
```

The complete package must also run its registered matroid/support replay. Loading
the 135 frontier rows is not a substitute for verifying how they cover all
permitted marked matroids.

Both implementations and the independent replay were prepared with substantial
OpenAI Codex assistance. Their agreement and mutation controls are finite
computational evidence, not a proof-assistant formalization or a claim of human
independent review.

## Open next questions

The cost certificate makes another local five-query search on these same three
canonical projectors unproductive. Six-query triple replacements, four-or-more
target replacements, changed fitting matrices and changed physical covers remain
outside this statement. A useful next test must specify which of those hypotheses
it changes and still price complete source and reader groups, including G0.
