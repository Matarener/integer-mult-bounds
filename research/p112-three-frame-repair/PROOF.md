# Sharp sixteen-group minimum with ten original frames retained

## Statement and scope

Use the 112 distinct binary unit labels in the selected
`research/adaptive-kernel-demotion/inputs/DATA-PHASES.json`.
The form is the ordinary dot product in `F2^9`. An admissible group is a
nonempty even subset whose Gram matrix is the identity. A partition consists
of pairwise disjoint admissible groups covering all 112 ports. An original
frame is retained only when its exact eight-port set is one complete group.
Reordering its ports has no effect on retention.

Fix the thirteen eight-frames in the exact PR3356 certificate. Among partitions
retaining at least ten of these frames, the minimum number of groups is sixteen.
Consequently a partition with at most fifteen groups must disturb at least four
of the thirteen originals. The theorem concerns these fixed source sets.
Unrestricted fifteen-group attainment is not decided.

## Reduction to 286 finite cover problems

An identity Gram matrix makes its vectors linearly independent. A group has at
most nine vectors in `F2^9`, and even cardinality therefore limits its size to
2, 4, 6 or 8. This justifies the complete enumeration cutoff without a search
assumption.

Suppose a partition with at most fifteen groups retains at least ten originals.
Choose ten retained frames. Removing them leaves precisely the other three
original frames plus the eight tail ports, hence 32 ports. The remaining
partition uses at most five admissible groups. All possible choices of the
three omitted originals are the `binomial(13,3)=286` triples tested here.
This reduction also covers partitions that retain eleven, twelve or thirteen
originals; choose any ten of their retained groups.

Both implementations exhaust every one of these 32-port domains and find no
cover by at most five groups. It follows that no partition in the stated class
has at most fifteen groups.

The retained PR3370 certificate has sixteen groups, all of which are directly
checked for disjointness, coverage and identity Gram matrix. Eleven original
eight-frames are retained. This witness belongs to the class retaining at least
ten, so sixteen is attained and the lower bound is sharp. Its unchanged
construction is credited to Tekalign.

## Complete group enumeration

The primary implementation encodes labels as nine-bit integers and calculates
the pairing by intersection parity. Its iterative clique enumeration maintains
a chosen orthogonal set and higher-index candidates orthogonal to every chosen
vertex. Each increasing sequence of mutually orthogonal vertices is visited
exactly once. Every positive even size is emitted, up to eight.

The independent implementation expands labels into nine explicit coordinates,
forms its dense dot-product table, and enumerates increasing vertex tuples.
It imports no primary code. The two complete sorted mask inventories agree in
every case through a canonical digest; equality is a consistency control, not
a substitute for either enumeration's completeness argument.

## Primary search and pruning

The primary search stores the uncovered port mask, the available-group bitset
and the remaining slot count. Available groups are exactly those disjoint from
the previously selected groups, subject to the size bound below. Selecting a
group removes its ports and every intersecting candidate group. At a nonempty
state, any exact cover must use a group containing the chosen uncovered vertex.
The implementation chooses the vertex with the fewest currently available
groups and branches over all those groups.

If `r` ports remain with `k` slots, reject `r>8k`. Every group in a feasible
cover must have size at least `r-8(k-1)`, since the other groups cover at most
`8(k-1)` ports. Groups below this minimum may be removed permanently along that
branch: after choosing a group of size `s<=8`, the new minimum is the old
minimum plus `8-s`, so it cannot decrease. No parity, support-shape, symmetry
or source-slot heuristic excludes a branch.

The visited key is the uncovered mask and remaining slots. This is sufficient.
Disjointness depends only on the uncovered mask, and inherited size filters are
no stronger than the current necessary minimum. Thus the available groups after
the current filter depend only on that key. Duplicate states have identical
possible completions. Marking a state on expansion is sound for this finite
reachability search: every child of its first expansion remains in the stack,
and group selection strictly decreases the uncovered set. Empty uncovered sets
are accepted, including covers using fewer slots; an exhausted stack rejects.

## Separate remaining-mask and complement search

The independent search represents available groups as ordinary mask lists.
At every state it uses a fixed vertex order determined once by initial group
counts, then checks each candidate's containment in the remaining port mask.
It does not use active-group bitsets, conflict tables or the primary's dynamic
minimum-choice calculation. It shares only the proved capacity inequality.

If the remaining set is itself an admissible group, it accepts. With two slots
left it tests each group through the chosen vertex and checks whether its exact
complement is in the complete group set. Otherwise it branches on every
contained group through that vertex. Duplicate uncovered-mask/slot states are
memoized. These cases exhaust all possible completions, including ones using
fewer than five groups. Exhausting the stack is the only negative exit.

The source-bound primary replay visits 533,382 states including duplicate pops,
with 470,919 distinct expanded keys. The independent search visits 2,314,084
states including duplicate pops, with 2,113,759 distinct expanded keys. The
largest single-case pop counts are 24,477 and 326,276. These are exact search
counts, not runtime or performance claims. Every per-case count is retained.

## Resource bounds and falsification controls

Both algorithms raise an error on budget or capacity exhaustion. They never
convert a timeout or unknown state into an exclusion. Each case permits at most
one million search pops, 8,192 groups and 100,000 queued states. Enumeration
also has a one-million-pop cap. All 286 cases finish below these limits.
Explicit budget-exhaustion controls verify the error exit.

Behavioral checks compare both solvers with complete subset oracles on all
128 possible four-port even-group families at zero, one and two slots. Thirteen
small geometric domains are separately enumerated from every subset and checked
at all five slot counts. Positive controls include the actual retained
sixteen-group witness and its five-group residual. Invalid domains, duplicate
ports, a broken Gram identity, malformed masks and three actual optimized CLI
mutations are rejected. These checks address acceptance behavior rather than
merely mirroring search internals.

## Scientific boundary

Pairing within each even orthonormal group and using one indicator query per
parity class gives two queries per group. The result therefore excludes thirty
queries for that recipe while retaining ten originals. It is not a lower bound
on arbitrary scalar fitting matrices for all matchings. The binary geometry
argument supplies no physical native program or multiplication theorem.

The complete-plane one-total tariff is still 224 for these group constructions.
PR3383's weighted spanning argument also fixes that minimum for recoding within
each such indicator row space. No saved physical cost follows from this group's
count restriction. Source acquisition, coefficients, frames, dirty restoration,
hosting, precision/tape, uniform all-size/compiler premises, supplier admission
and outer transfer remain separate. No selected-frontier change or new kappa
is claimed. We stop at the fixed three-frame domain.
