# Exact batching of unique-destination dirty XOR sweeps

This contribution was produced by Nick Petalas. Apache-2.0.

**Scoped proof with exact finite corroboration; no new κ.** For a finite
ordered list of in-place XORs with distinct destinations, serial execution
equals entry-snapshot execution on every dirty input exactly when no event
reads a cell written by an earlier event. Every failed guard has a concrete
single-basis-input discrepancy. A safe reordering exists exactly when the
directed source-to-destination graph is acyclic.

The contribution is the exact batching contract, necessity proof and executable
witness guard. Read-before-write dependency scheduling and topological sorting
are standard background; no historical-priority claim is made for those ideas.
Rohan Arun's [PR409](https://github.com/CrocSwap/integer-mult-bounds/pull/409)
already uses read-before-write as a sufficient premise for a particular
rational entrance-shear word; [PR413](https://github.com/CrocSwap/integer-mult-bounds/pull/413)
retains it. The additional step here is necessity with a final-state witness
and an exact safe-ordering criterion under the Boolean unique-write contract.
Neither predecessor's word or reported bound is replayed here.

## Contract and theorem

Let `V` be any finite set of cells and let each payload be an element of any
nonzero vector space `W` over `F2`. In particular, payloads may be arbitrary
dirty bit strings or Boolean functions on a common address set. They may be
correlated. For an ordered word of `m` events, write

```text
event j: x[t_j] <- x[t_j] XOR x[s_j]
```

Require `t_j != s_j` and require every `t_j` to be distinct. No other
operations, hidden writes or changes of coordinate encoding occur inside
the word. Extra cells are allowed and remain untouched unless named.

The snapshot endpoint is the linear map `S` defined by
`S(x)[t_j] = x[t_j] XOR x[s_j]`, with every right-hand value taken from the
entry state; unselected cells retain their entry values. Let `P` be the
literal serial in-place map.

**Theorem 1.** The following are equivalent:

1. `P(x)=S(x)` for every input `x in W^V`.
2. There are no indices `i<j` with `t_i=s_j`.

If condition 2 fails, let `j` be its first failing event and let `i<j` be
the unique event writing `s_j`. Put a nonzero value `b` in cell `s_i` and
zero in every other entry cell. Then `P(x)[t_j] XOR S(x)[t_j] = b`.
Thus failure is semantic on arbitrary dirty inputs, not merely a dependency
warning. The all-zero input still passes every word and cannot test this claim.

### Proof

If condition 2 holds, every source read still equals its entry value. Each
destination also has its entry value until its only write. Each update
therefore equals its snapshot update, and no later event changes that
destination. This proves sufficiency.

For necessity, choose the first failing `j`. Every event before `j` reads an
entry value. The unique event `i` writing `s_j=t_i` consequently leaves

```text
current[s_j] = entry[s_j] XOR entry[s_i].
```

It is not written again. At event `j`, destination `t_j` has never been
written, because destinations are distinct. The serial and snapshot values
at that cell differ by exactly `entry[s_i]`. No later event can change
`t_j`. Setting only `entry[s_i]=b` proves the claimed final discrepancy.
This also covers a two-cycle where `s_i=t_j`. The payload argument is
coordinatewise and needs no independence assumption on a particular input.
It establishes operator equality, or exhibits one input refuting it. ∎

**Theorem 2.** Fix the event set and retain the same unique-destination
contract. Some permutation of the events has endpoint `S` if and only if
the graph with edges `s_j -> t_j` is acyclic.

If a safe order exists, Theorem 1 requires every edge leaving a cell to
precede the edge entering that cell, whenever both exist. A directed cycle
would impose a strict cyclic order on its edges, which is impossible.
Conversely, in a DAG process vertices in reverse topological order and
execute the event entering each vertex, if present. Every edge leaving a
cell then precedes its unique incoming edge, so no source has been written
before it is read. Theorem 1 applies. Distinct destinations make `S`
independent of the event permutation. ∎

## Smallest examples and scope boundaries

For `a,b,c` initially arbitrary, the word

```text
b ^= a; c ^= b
```

returns `c XOR b XOR a` in the last cell; the snapshot contract requires
`c XOR b`. Reversing those two events implements the snapshot exactly.
The two-cycle `a ^= b; b ^= a` has no safe reordering.

Repeated destinations are outside both theorems. In three cells the word
`(b ^= a; c ^= b)` repeated four times is the identity, as is its snapshot
sum. It has chronological conflicts whose discrepancies later cancel.
The verifier checks this boundary and the public guard rejects such a word.
Self-XOR is also rejected. Its erasure semantics is outside the invertible
update contract.

The algorithms in [batching.py](batching.py) are:

- `first_conflict`: validate the contract and scan once, returning the two
  event indices, entry basis cell and final discrepancy cell, or `None`.
- `safe_order`: remove sinks with a heap and emit their incoming events;
  return a permutation or `None` for a directed cycle.
- `execute`: literal serial or snapshot execution on dirty bit strings.

The guard uses `O(|V|+m)` storage and time bounded by the input validation
and scan. The ordering routine uses `O(|V|+m)` storage and
`O(|V|+m log(|V|+1))` time. The implementation admits at most 4,096 cells,
at most one event per cell, and payload entries of at most 256 bits.
The written theorems cover every finite cell set and every such `W`.

## Evidence and reproduction

The standard-library verifier enumerates every ordered admitted word on one
through five cells and directly constructs both full Boolean operators.
It uses a separate transitive-closure oracle for cycles, then checks the
returned ordering against the full operators. It executes every unsafe
basis witness on literal bits, rather than accepting only a conflict flag.

Observed exhaustive totals are 160,579 words, 4,833 safe orders and 155,746
unsafe orders with 155,746 executed witnesses. Of these words, 141,736
have a directed cycle. Each word is counted with its order; these are not
counts of unlabelled graphs. The replay also checks 512 dirty two-bit
payload executions, 16 invalid-input rejections and six boundary controls.
The latter include a 4,096-cell chain and cycle, the largest payload bit,
and the repeated-write cancellation example. The all-size result rests on
the written proof, not extrapolation from these counts.

From the repository root:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/unique-write-xor-batching/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/unique-write-xor-batching/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/unique-write-xor-batching
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/unique-write-xor-batching --check-source-history
```

Use the host's CPython 3.12 path elsewhere. The first two commands print
`PASS_UNIQUE_WRITE_XOR_BATCHING`, the complete derived totals and SHA256
of every regular package file. They write no files and work without Git.
No receipt is handwritten or used as a substitute for recomputation.
Registered replay runs both modes with 120-second command limits.

## Connection to the current bottleneck and predecessor credit

The selected `owned_erasure` and `compiler` assumptions require legal
chronological physical operations. Jose Manuel's
[PR2195](https://github.com/CrocSwap/integer-mult-bounds/pull/2195),
`selected-bit-local-ring-sweeps`, distinguishes pointwise owner injection
from separation of complete high packets and supplies an alias countermodel.
Adam Gall's [PR2088](https://github.com/CrocSwap/integer-mult-bounds/pull/2088)
constructs physical private snapshots with separately charged storage and
transports. Their results, counts and native guards are cited premises or
motivation and are not audited or replayed here.

This package supplies a different, conditional admission test: **after** a
caller has emitted its actual cells and proved global destination uniqueness,
the guard decides whether its serial reads may be replaced by entry reads.
Disjoint read and write sets suffice, but are unnecessary. For example,
`c ^= b; b ^= a` is safe despite overlap. A directed cycle obstructs every
in-place ordering in this class before routing costs are considered.

This does not prove uniqueness, packet separation, selected source provenance,
COPY/ERASE restoration, paid routing, recursive workspace or child closure for
any actual GL64 sweep. It changes no selected source, supplier or frontier.
No complete multiplication theorem, selected assumption discharge or native
cost saving is claimed. The exact scopes of #2195 and #2088 remain theirs.
Credit their alephnan, eumemic, DreamingOfClouds, source/compiler/owner and
retained native lineage without transferring those results to this package.

Scientific base is canonical main
`a5bff3bf133e482541c09eba4e773884bdb2b1b7`, priority revision 8. The selected
κ there is `781451/250000000`. [TASK.json](TASK.json) retains the original
`uniform-transfer-audit` card and marks this reusable side result as changed
scope. [SOURCES.json](SOURCES.json) pins the catalogue, selected record and
the two contextual predecessor texts as historical provenance. The new proof
is self-contained and imports no predecessor executable.

Live overlap covered 310 open PR bodies and 5,906 Discussion records with
complete remote pagination. Sparse local search covered 91 of 8,623 tracked
notes, so omitted notes were not treated as searched. Separate main-wide
README and merged-PR searches checked the distinctive unique-write, dirty
XOR, snapshot and read-before-write terms. This is bounded overlap evidence,
not proof of novelty or scientific acceptance.

## Implementation limits

No recursion, generated code, dynamic evaluation or asynchronous work is
used. The fixed package-local import makes isolated `-I` execution explicit.
All public contracts use exceptions that remain active under `-O`; the
verifier's mathematical invariants use explicit checks. Every enumeration
has fixed finite bounds. Functions are below 60 physical lines.

Python allocates collections during execution, a Power of Ten rule-3
deviation. Public words have at most 4,096 events, public values at most
256 bits each, and each exhaustive oracle case has at most five cells.
Cases are processed one at a time. No allocation-free or hard real-time
claim is made. Warning-strict normal and optimized runs are the available
diagnostics; no third-party static analyzer or Lean build is required.
Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. Emit one named physical packet sweep, prove its global destination
   uniqueness and apply the guard. This could settle one actual batching
   decision. Begin with its exact physical coordinate encoding; that emitter
   and a complete routing invoice are missing here.
2. Classify a bounded repeated-write family. This could admit schedules
   excluded by this contract. Begin with full operators and the eight-event
   cancellation example; the first-conflict proof no longer freezes its
   output when later writes are permitted.

The structured questions are in [TASK.json](TASK.json). Research stops at
this first verified criterion.
