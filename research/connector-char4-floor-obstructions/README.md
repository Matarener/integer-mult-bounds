# Characteristic-four connector floor obstructions

For the unsigned dirty connector of
[PR #4231](https://github.com/CrocSwap/integer-mult-bounds/pull/4231), let
N(c) be the largest source count k at which every source operator and every
nonzero binary-mask output operator can be called exactly c times while
restoring the arbitrarily dirty connector. The complete-call floor is
c(k + 2^k - 1).
[PR #4248](https://github.com/CrocSwap/integer-mult-bounds/pull/4248)
attains nine sources in characteristic four and supplies the deletion lemma.
[PR #4255](https://github.com/CrocSwap/integer-mult-bounds/pull/4255)
proves N(4) <= 20.

This package establishes:

- **9 <= N(4) <= 17.** A cube-union and triple-class argument excludes every
  eighteen-source floor walk, closing all parity-repeat cases with exact
  integer bounds below 262,144 masks including zero.
- **The maximum depth-two source count is four.** More sharply, a balanced
  five-source block serves at most 28 of the 31 nonzero masks using two
  prefix readouts. Exactly four words, up to source relabelling, attain 28.
- An all-ones readout normal form has eight possible source inventories
  across four gaps. It gives 19,448 inventory-type count vectors at k = 10,
  while leaving internal event orders to search.

The upper bound is a scoped written proof with bounded controls. The
five-source maximum and catalog are exhaustive finite results. They do not
exclude ten sources in a general depth-four walk. There is no new κ,
selected-frontier change or complete multiplication theorem.

## Interface and necessary conditions

A characteristic-four floor walk has length 4k and uses each immutable source
exactly four times. Every nonzero binary mask m must be a sum of four
possibly repeated boundary prefix vectors modulo four. This is #4231/#4248's
prefix criterion. Zero is obtained by reading the zero boundary four times.

Modulo two, a four-readout multiset reduces to an even subset of at most four
parity prefixes. Repeated parity-prefix values can be identified without
changing that set of parity sums. The full mod-four condition also constrains
how many prefixes can lie in a translate of the binary cube.

## Upper bound: N(4) <= 17

[PROOF17.md](PROOF17.md) gives the complete argument. Its cube-intersection
lemma improves the cyclic repeat charge to 2S<=r, and extends to free-coordinate
slabs and unions of cubes with the same parity. It then counts three levels
of triple sums: exact modulo-four values, components connected by one-coordinate
carry changes, and parity classes.

Colexicographic representatives and source-event pair graphs bound these
classes. The resulting count excludes all eighteen-source parity-repeat
cases except r=2,4,5. If the theoretical cube cap is attained in one of those
cases, the source budget forces one or two literal triple-source runs. Their
axis-deletable prefix indices sharpen the component count. If the cube cap
is not attained, a conservative four-per-axis bound closes the same cases.
The six final upper counts are all below 262,144.

[axis_obstruction.py](axis_obstruction.py) replays all initial cases, the tail,
and both branches of each residual case. [n4_controls.py](n4_controls.py)
checks the strengthened cube, graph, class and incidence lemmas on bounded
families. The underlying written argument is uniform in the walk.

## A normal form for future construction searches

Take four readout boundaries for the all-ones mask and rotate the source walk
to begin at the first. Every prefix is translated by the same vector, so each
four-prefix sum changes by four times that vector, which vanishes modulo four.
The four cyclic gaps partition the source events.

For each source, its gap inventory (a, b, c, d) has total four and satisfies
3a + 2b + c = 1 modulo four. Exactly eight of the 35 weak compositions satisfy
this equation: the cyclic rotations of (3, 0, 0, 1) and (0, 2, 1, 1).
Every source misses at least one gap. Repeated readouts give empty gaps and
remain allowed.

Up to source relabelling, the inventory-type counts have C(k+7, 7)
possibilities, giving 19,448 at k = 10. This counts inventories, not event
orders. Each gap's prescribed multiset still needs an internal ordering.
When labels are fixed by inventory type, first-occurrence symmetry can be
imposed only within equal-type classes. No ten-source exclusion follows.

## Sharp depth-two obstruction

A block has depth at most two if every binary mask is a sum of at most two
of its prefix-count vectors modulo four. Boundary zero pads shorter reads.
Two concatenated two-source depth-one blocks from #4248 attain four sources.

The complete first-occurrence-canonical census at five sources accounts for
all 20! / ((4!)^5 * 5!) = 2,546,168,625 words. None reaches 30 masks including
zero, and exactly four reach 29. [MAXIMIZERS.json](MAXIMIZERS.json) lists those
four words, their missing nonzero masks and their four-permutation structure.
Each is checked directly. The count of four plus four distinct valid canonical
witnesses proves catalog completeness up to source relabelling only.
Rotation and reversal are not quotiented out.

[DEPTH2.md](DEPTH2.md) gives the safe future-cut relaxation, exact subtree
accounting and replay details. The threshold-30 census visits 8,462,068 nodes
and prunes 6,451,947 subtrees. The threshold-29 census visits 8,715,495 nodes
and prunes 6,632,616 subtrees. Both account for the complete canonical family.
Source deletion preserves depth at most two, so failure at five sources
excludes every larger depth-two block. This closes the concatenation route
using two five-source depth-two blocks, while allowing coupled depth-four
searches.

## Reproduction

From the repository root with CPython 3.12:

```sh
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/connector-char4-floor-obstructions/verify.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/connector-char4-floor-obstructions/independent_check.py
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/connector-char4-floor-obstructions
~/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/connector-char4-floor-obstructions --check-source-history
```

Expected main marker:
`PASS_CONNECTOR_CHAR4_FLOOR_OBSTRUCTIONS N4<=17 depth2_max=4 depth2_k5_coverage=28`.
Both principal registered checkers also run with optimized Python and explicit checks.
The main verifier recomputes [CERTIFICATE.json](CERTIFICATE.json), including
the eighteen-source triple-class cases and residual branches, the earlier
76-case cube arithmetic control, the inventory enumeration, full-coverage
controls, the sharp depth-two censuses and the maximizer catalog. Certificate
regeneration is available through `verify.py --write-certificate`.
Each checker prints a generated receipt bound to all package files.

The main cube control checks all 70 labelled two-source words at all 16
translations and all 34,650 labelled three-source words at all 64 translations,
for 2,218,720 translations. It also checks 4,000 deterministic larger words
at 100 translations each. The separately written component checker uses
literal coordinate states on 21,120 cases, directly checking the outside
components, disjoint repeated-parity charges and arithmetic table. It also
checks every maximizer independently.

The depth-two Python replay checks its future-cut tables directly and compares
with an unpruned coordinate evaluator through three sources at every mask
threshold. A separately written iterative C engine agrees with every field
of both sharp five-source censuses and accounts for all 2,627,625 four-source
canonical words with negative feasibility pruning disabled, finding 421
full-cover solutions. Already-satisfied prefixes may still aggregate their
canonical completions. Its opt-in
commands are in DEPTH2.md; it is not a registered CI obligation.
Predecessor constructions and exclusions are cited dependencies, not new
audit deliverables. Their exact heads and README hashes are recorded as
citations in [SOURCES.json](SOURCES.json).

## Limitations

N(4) remains open within 9 <= N(4) <= 17. There is no ten-source witness and
no exclusion of ten through seventeen sources. The single-cube bound alone
leaves too many possibilities at eighteen sources; the triple-class proof
uses collections of cube intersections to close that case. Moreover, the
72-event finite witness in [CUBE-SHARPNESS.json](CUBE-SHARPNESS.json) has
72 distinct parity prefixes and 22 prefixes in the unshifted binary cube.
Thus H(18,0)=22 is attained, so that uniform intersection cap cannot be
lowered at this corner. This is not a floor-attainment witness. The depth-two
census concerns only that block depth and characteristic four.

The interface has immutable sources, unsigned calls and every nonzero binary
mask output. No physical caller, primitive tariff, admission, dispatch or
precision obligation is instantiated. Independent human and formal
proof-kernel review are unclaimed.

The Python checkers allocate bounded integers and temporary collections.
In depth_two.py, walk_tables and inspect_state use preallocated tables and
an explicit 21-frame stack for k <= 5, with no recursion. CPython allocation
is a managed-runtime deviation from fixed-allocation operation. Fixed
dimensions, explicit iteration bounds, capacity checks and normal/optimized
replays bound and check the live state. A strict allocation-free consumer
would require the native fixed-array implementation instead of widening
this Python contract. The axis controls fix eighteen sources and one hundred
control words; the general incidence controls use at most nine sources and
at most C(36,3) triple values in their bounded component worklists. These
modules use the same managed-runtime deviation and explicit iteration bounds.
No unbounded input or concurrent mutation is accepted.

## Open next questions

Structured first steps and blockers are in [TASK.json](TASK.json).

1. Find a ten-source floor walk in the eight-inventory normal form, or prove
   ten sources fail. The four maximizing depth-two blocks give a complete
   small seed catalog for coupled searches; concatenating two five-source
   depth-two blocks cannot work.
2. Improve the triple-class and cube-union count at seventeen sources, or
   find a further structural restriction on its possible walks.
3. Identify a concrete characteristic-four caller and price its complete
   interface before using a larger abstract batch in a recursive supplier.

## Credit

This package was produced by Nick Petalas. The interface and floor are
#4231's. The nine-source lower bound and deletion lemma are #4248's;
the deletion argument extends #4232's characteristic-three version.
The parity-boundary counting approach builds on #4255. The connector
interface and prefix criterion originate in Ross Richardson's #943/#934
lineage. Independent human and formal proof-kernel review are unclaimed.
Apache-2.0.
