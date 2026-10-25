# Boolean translation for one simple22 B template

Fix a restored ten-step low word with multiplicities (4,2,2,2), one of the
77 specified representatives. Let its prefix low vertices be l_0,...,l_9.
The high coordinates must each occur four times. Their twelve steps, together
with the ten low steps, give a 22-step word. No assumption about gap lengths,
native capacity or optimistic coverage pruning is used below.

## Ordered paths and exact counts

A simple full word stays at low vertex l_j during its j-th high run. That run
cannot repeat a high vertex. It is therefore an ordered simple path in Q3,
with at most seven edges. Conversely every such path is admitted. The generator
lists every ordered subset of the seven nonzero vertices following zero, and
keeps exactly the adjacent sequences. These are all 112 paths, including the
empty path. All eight translations are available, except that the first path
starts at zero. Translating the high origin to zero preserves the problem.

Each block selects exactly one translated path. The at-most-one clauses use
a cumulative flag: selecting any earlier member forces every later member
false. The at-least-one clause then gives exactly one. Its selected path
fixes all eight occupancy bits, three start/end bits and twelve unary count
bits. Count bit k is true exactly when that coordinate occurs at least k times
in that path. A simple Q3 path uses any one coordinate at most four times:
there are only four disjoint edges with that coordinate direction.

The global count encoder represents, for every prefix of its input bits,
"at least k true inputs" for k=1,...,5. Its recurrence is

```text
S(i,k) <=> S(i-1,k) OR (input_i AND S(i-1,k-1)).
```

The k=1 base is prefix disjunction; impossible early counts are false.
All displayed equivalences have both CNF directions. Induction proves the
recurrence. Requiring S(final,4) and not S(final,5) gives exactly four high
steps in each coordinate. Exhaustive truth tables through five inputs check
this encoder independently against the ordinary number of true bits.

## Joins, simplicity and occupancy

Equality of each path's end bits with the next path's start bits, cyclically,
gives one restored high walk. The low word is already restored. The first
high start is zero. Reconstruct each selected high run, then its prescribed
low step. Its full prefix vertices are exactly the translated vertices of
that path paired with low vertex l_j, including the high endpoint before
the low step.

A selected path is internally simple. Two blocks at different low vertices
cannot collide. Between blocks with the same low vertex, pairwise negative
occupancy clauses prohibit a shared high vertex. Thus all 22 full prefix
vertices are distinct. Conversely every simple word with this low projection
satisfies those clauses.

For each full vertex v, the point variable is equivalent to the disjunction
of the block occupancies at v. For each nonzero difference d and unordered
pair {v,v+d}, a witness variable is equivalent to the conjunction of the two
point variables. The disjunction of all 64 witnesses is required. Hence the
CNF requires exactly that every nonzero element of F2^7 occurs in P+P.
Zero occurs because P is nonempty. These constraints imply universality and
are satisfied by every universal prefix set. They do not replace coverage
with a pair-count bound.

## High-coordinate symmetry

All three high totals are four. Permuting the three high coordinates preserves
joins, simplicity, coverage and this target. Rename them in order of their
first occurrence in the complete concatenated high word. This preserves the
low template. The `used` bits state whether a coordinate occurred in an earlier
block. A chosen path may use coordinate a only if every smaller coordinate
already occurred earlier or appears earlier in that same path. These clauses
admit precisely that first-appearance convention. Every feasible word has
such a renaming, so this restriction does not remove all representatives of
any feasible word. The controls with unequal high totals or fixed paths disable
this symmetry, and misuse is explicitly rejected.

Together the preceding implications prove equisatisfiability between each
named template problem and its generated CNF. Exact arithmetic defines every
clause; no floating-point calculation is involved.

## Checked exclusion and its boundary

For each of B1 through B4, the replay generates the bound CNF, obtains an UNSAT
trace from the pinned solver and independently checks it with pinned DRAT-trim.
An incomplete solver is not admitted. A false solver verdict without an accepted
trace is not admitted. The exact CNF hashes in `RESULT.json` and the checked
proof records in `OBSERVED.json` therefore support the four stated exclusions,
under this written translation argument and the certificate checker's contract.

This is not a proof-assistant verification of the encoder or checker. The
other 73 templates and the predecessor's coding/classification, non-simple
branch and reduction steps are outside this conclusion. In particular this
package does not independently prove the complete f(7)=24 theorem.
