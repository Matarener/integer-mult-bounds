# Two-clique relays still cost eight

This is a scoped proof with exact finite corroboration. In the confined REL
model, a block of two mutually orthogonal four-port cliques needs exactly
eight units of owned paid frame descent. Arbitrary finite chains, branching,
merging, cancellation and public re-ascents do not lower this bill. Both a
four-move construction and an eight-move relayed construction attain eight.
No new kappa or selected-frontier change is claimed.

DreamingOfClouds's [PR6170](https://github.com/CrocSwap/integer-mult-bounds/pull/6170),
`P104-LEMMAS.md` section 11.5, proves the isolated-move floor and explicitly
leaves chains and moves outside the group unresolved. This closes the
confined-chain case and also permits general confined acyclic relay graphs.
The outside-reaching case remains open. No predecessor census, frontier
word, invoice or theorem is re-verified as this contribution.

## Result and its boundary

Let Gamma be the binary Gram mask of the ports, interpreted over Q. For
every finite REL network whose gathering and landing frames lie in the
block span, the new cumulative information bound is

```text
rank_Q(C Hadamard-product Gamma)
  <= sum_moves [dim pi(gather) - dim pi(landing)]
  <= sum_moves [dim gather - dim landing] = owned paid.
```

Here C is the complete rational source/receiver map and pi is the binary
two-dimensional quotient identifying the two cliques. Correctness requires
the Hadamard product to be I_8. The bound therefore gives owned paid >= 8.
[PROOF.md](PROOF.md) proves the statement for any finite two-clique port set.

The proof uses an inclusion-preserving rational representation of the five
binary quotient subspaces and maintains a cumulative row space. This is
needed because one term in a legal chain can have Hadamard rank two while
its own paid descent is only one. Counting that term independently would
miss its predecessor's cost. The checker includes this exact counterexample.

The attaining endpoint has rank four, C=[[I_4,I_4],[I_4,I_4]], but still costs
eight. Thus the low completion rank in the proposed block construction
cannot itself produce a cheaper confined owned layer.

## Exact finite evidence

The new concrete P104 block is

```text
A = 73, 239, 336, 502
B = 81, 247, 328, 494
W = span_F2(81, 502, 239, 73).
```

The pinned predecessor word is read only for its port definition. The replay
checks membership of these eight ports, their complete Gram table and:

- All 67 subspaces of W and all 513 nested frame pairs, including equality.
  There are 128 local-source and 128 receiving-functional checks.
- Two attaining networks, including every source-coordinate column of their
  complete rank-four endpoint and identity Hadamard shadow.
- 512 deterministic sixteen-move networks, containing 18,885 nonzero parent
  edges, 4,429 branching parents and 4,407 moves with multiple parents.
  Literal coordinate evaluation agrees with the packet calculation.
- All 512 binary three-by-three rational matrices against a separate minor
  rank oracle, five rejected invalid networks, and the shared-cost control.

The relay fixtures are not an exhaustive network census. The all-finite-network
claim is the written proof. The finite runs test its representation and
invariant, with explicit exceptions that remain active under optimization.
The replay prints a generated receipt bound to every package file's SHA256.
No receipt is handwritten and the verifier writes no files.

## Reproduce

From the repository root, with CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/p104-two-clique-relay-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/p104-two-clique-relay-floor/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-two-clique-relay-floor
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-two-clique-relay-floor --check-source-history
```

Another CPython 3.12 path can replace the local interpreter. The scientific
marker is `PASS_P104_TWO_CLIQUE_RELAY_FLOOR`. The runner also checks exact
source pins and metadata. The publication preflight checks committed bytes
and source-history availability. These are different checks.

## Limits and implementation bounds

All gathering and landing frames must remain inside W. Two same-class ports
can have different pairing functionals outside W, breaking the rational
representation's reader condition. The proof grants free public re-ascents
and arbitrary rational scalar coefficients, so it excludes a larger class
than confined dyadic REL networks. It supplies no physical scalar word,
native implementation, full productive/paid invoice or supplier admission.
The five selected framework assumptions remain. No selected cold replay,
Lean, Docker or historical scientific suite is required or claimed.
Independent human and formal proof-kernel review are unclaimed.

The finite reference implementation fixes eight ports, at most sixteen moves,
binary dimension at most nine, and rational matrices at most 64 by 16. The
registered fixtures use coefficients in {-1,0,1}. Matrix input parts are
capped at 2,048 bits. There is no recursion, dynamic code evaluation, network
access or subprocess creation. Functions stay below 60 physical lines.
The checks run with warnings treated as errors, normally and under `-O`.

Power-of-Ten rule 3 has a managed-runtime deviation. Python allocates Fraction
and container objects during these finite replays. Fixed frame, port, move
and coefficient domains bound live state, and no network history is retained
across cases. The source is one pinned finite compressed JSON file, opened
with a context manager. The replay exercises the maximum move count and
invalid frame/arrival/receiver contracts. A fixed-capacity arithmetic backend
would be needed if this became a production checker with external inputs.

## Open next questions

Can an outside-reaching network reduce the eight-unit cost? First specify
one gathering/landing network and the exact source and receiving maps, then
test the rational-lift reader condition. The blocker is that classwise
pairing functionals agree only on W. Any physical successor must also pay
public helper lifetimes, restoration, native access and all other charges.
The structured question is in [TASK.json](TASK.json).

## Provenance and credit

This contribution was produced by Nick Petalas. Apache-2.0.

DreamingOfClouds PR6170 supplies the open two-clique question and REL
contract, including its local-source, landing and paid definitions. Its
isolated-move result is a cited predecessor, not an audit deliverable. Ali
Romman's PR5599 supplies the retained port definition. Matarener's P104
geometry and the retained P104/native/helper/controller/caller lineage keep
their credit. Linear rank bookkeeping and the rational rank-two subspace
representation use classical linear algebra.

The base is canonical main `a5bff3bf133e482541c09eba4e773884bdb2b1b7`.
[SOURCES.json](SOURCES.json) binds the exact source blobs and SHA256 values.
The selected record and catalogue are historical provenance; only the port
definition is a live external input. Task scope is explicitly changed from
the card's selected-word experiment to this targeted obstruction.

The advance [CLAIM](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19279674)
follows checks of live handoffs, active Discussions, open/merged PRs, recent
account contributions and local target reservations. The cached open snapshot
covered 338 PRs and 5,957 Discussion records with complete pagination. The
sparse local scan searched 84 notes and omitted 8,539; distinctive Git searches
against main and separate merged-PR searches supplemented it. These searches
do not cover unpublished work or prove global novelty.
