# Full-stock certificates by crossed ADD pairings

For the four pinned complete words below, any retiming by general Clifford
frames with common frames at the fixed scalar ADD gates and fixed literal
physical input/output boundaries has native rank mass at least stock:

| Source word | q | Ambient m | Banks n | Floor n*m | Saved source mass |
| --- | ---: | ---: | ---: | ---: | ---: |
| Repaired SIMPLIFIED | 2 | 12 | 6 | 72 | 80 |
| Repaired SIMPLIFIED | 3 | 16 | 8 | 128 | 136 |
| Admitted two-site | 2 | 12 | 6 | 72 | 76 |
| Admitted two-site | 3 | 16 | 8 | 128 | 132 |

Every displayed rank is multiplied by f. The statement is all-positive-f
for these finite q fixtures, not an all-q construction or theorem. It does
not establish the optimality of the larger saved source invoices. It does
exclude reducing any of these fixed-graph words *below* stock by a frame
retiming, including a retiming with frames that mix tensor coordinates.

The source, complete arbitrary-input domain, phases, native recipe admission
and literal inverse are unchanged. This package supplies a new lower-bound
witness, not a new caller. It does not infer any mathematical result from a
numerical optimizer's convergence or from failure to find a construction.

## The pairing freedom

Use the graph and distance lemma in the frozen predecessor
`../pauli-caller-retiming/TRAJECTORY-PROOF.md`. Each ADD is a common-frame
node, each maximal unary segment is an edge, and all physical input/output
boundaries have the coordinate Z Lagrangian. The source's nontrivial output
operator is already part of the fixed chronological unary word; it is not
replaced by a free final gauge. Scalar coefficients commute with address
operators and all actual ADD coefficients are nonzero.

At each ADD node both incoming strands end at the same Lagrangian L_v and
both outgoing strands start there. In a proof certificate they may be paired
straight or crossed. This is a pairing of graph edges; it does not assert
that independent field values have been swapped or copied by the ADD.
The fixed literal BANK_SWAP gates still transport actual strand identities.

The graph is chronological. Therefore choosing a bijective straight/crossed
pairing at each ADD partitions every edge into exactly n directed paths
from fixed physical boundaries back to fixed physical boundaries. Each path
may end at a different bank from where it began. No internal directed cycle
can arise because time strictly advances at internal graph nodes.

For each path with holonomy G=G_l ... G_1 the triangle inequality gives

    sum_path d(L_v, G_e L_u) >= d(Z,G Z) = native_B_rank(G).

Every edge is in exactly one path. Summing therefore lower-bounds the entire
native rank bill. The proof requires the fixed ADD/common-frame graph and
unary holonomies. It is not a bound for arbitrary words realizing the same
overall matrix, nor for a changed helper or input/output contract.

## The exact witness

`FULL-STOCK-CERTIFICATES.json` specifies one straight/cross bit for every
ADD event in each source word. The chronological bitstring, actual source
event ordinals and source event hash are all retained. It also specifies
every graph edge, path edge list, signed holonomy tableau, complete literal
coordinate circuit, its literal inverse, and its all-f scalar phase vector.

In the q2 witnesses all six holonomies have B-rank12. In q3 all eight have
B-rank16. Hence each path reaches its largest possible native rank m and
the sum equals n*m. This also proves that these witnesses maximize the
path-pairing objective, since no m-coordinate Clifford has B-rank above m.
Maximizing that certificate objective is distinct from minimizing the actual
retimed source bill; the latter may remain strictly above stock.

The bounded proposer searched only these graph-pairing bits. It stopped as
soon as a full-stock bitstring was found: repaired q2/q3 after103/366 exact
rank proposals and admitted two-site q2/q3 after165/633. These counts describe
discovery, not exhaustive coverage or a probabilistic theorem. Admission
rebuilds every source unary circuit and edge, then independently traverses
the chronological physical strands with crossed pairing to check each full
operator product, signed tableau, tensor phase and source-unary order.

An f-fold source holonomy is its saved coordinate circuit tensor power
times a scalar phase. Its B-rank is therefore f times the saved rank.
The metric proof is in the full mf-coordinate symplectic space, so the
candidate frame gauges themselves need not have a tensor-product form.
Exact inverse tableaux and inverse scalar phase vectors are retained.
No selected-native lowering of a newly synthesized operator is needed:
these holonomies certify a bound and are not proposed executable children.

## Controls and reopening scope

The all-straight pairing reproduces the old weaker floors62 and118 and is
rejected as a full-stock witness. Removing a stored edge rejects exact
partition coverage. Omitting an actual nontrivial BANK_SWAP transport
changes the independent literal crossed-strand replay and is rejected.
The admission producer passes in normal and optimized Python; no essential
checks disappear with assertions.

New unary responses or holonomies, nonlocal scalar rewrites across native
operations, additional helper interactions, or changed physical boundary
contracts remain outside this fixed-word result. The earlier contiguous
scalar-SWAP identity splicing argument can preserve any of these improved
witnesses when its internal pairing is chosen consistently. No new kappa,
positive-exponent moment, compatible BIT supplier, owner allocation,
rounding, source-access, machine-controller or storage claim follows.
