# Independent fixed-word proof review excerpt

This exact section is extracted from the unchanged completed review retained
at source/completed-gates-review/REVIEW.md. Other kernel/cubic sections are
outside this contribution.

## Fixed-graph trajectory theorem

For equal-dimensional subspaces let `d(U,V)=mf-dim(U intersection V)`.
The intersection dimension inequality proves its triangle inequality;
invertible linear maps act isometrically. Thus an edge operator G and
endpoint Lagrangians L_u,L_v have tariff

    d(L_v,G L_u)=native_rank(T_v^-1 G T_u)

when `L_x=T_x Z`. Permitting arbitrary Lagrangians at ADD nodes is a
relaxation of the literal requirement that both operands have the same
actual frame representative. For a path, pulling each node frame back by
the chronological partial holonomy makes the sum telescope by triangle
inequality to `d(Z,G_path Z)`. Partitioning every edge once into
boundary-to-boundary paths then gives the sum of these holonomy ranks as
a lower bound, without counting an edge twice or interpreting a path as an
independent value/caller-matrix coefficient.

The literal input/output boundaries are fixed at Z. The statement is valid
for general Clifford frame gauges on all mf coordinates, including gauges
that mix tensor coordinates. Tensor structure is used only to lift the
fixed source holonomy ranks by a factor f, not to restrict the allowed
retiming frames. Global Gaussian phases do not affect the subspace metric,
but the complete literal circuits and their tensor-phase corrections are
retained and independently checked.

The eight original straight-pairing source words have independently checked edge-disjoint exhaustive
partitions and physical-label traversals. Pauli DEFAULT and ISOLATED have
sharp floors 60 (q=2) and 112 (q=3), equal to their source rank bills and
endpoint stocks. Repaired SIMPLIFIED and admitted two-site have only the
weaker floors 62 and 118; these are not optimality certificates for those
words. The separate crossed-pairing witnesses below strengthen precisely
these weaker floors. No all-q extrapolation is made from these finite fixtures.

The scalar SWAP gadget `x+=y; y-=x; x+=y; y*=-1` is an exact all-input
transposition. Crossing strands at its first ADD and keeping the remaining
pairings straight preserves an inherited holonomy partition when expanding
a literal SWAP. Identity segments inserted by the gadget remain edges and
are counted. The final sign SCALE is a paid scalar scan. Reversing this
operation for an existing gadget is conditional on its internal routing
inducing the required crossing; no invariant for arbitrary scalar rewrites
is claimed. The source replay expands all 72 actual SWAPs separately and
checks one identity insertion per fixture. It is a same-engine replay,
distinct from this review's independent edge/operator traversal.

This theorem fixes the source unary holonomies, common-frame ADD graph and
literal owner/input/output boundary. A changed response, nonlocal scalar
rewrite across native sites, new dirty helpers/interactions, changed right
input chart or owner contract needs a new certificate. The metric controls
rank mass, not the concave positive-exponent moment or native lowering.

## Stronger finite crossed-pairing witnesses

The subsequently frozen `../trajectory-pairing-search/` witnesses are also
independently admitted. The four unchanged source words now have floors:

| Family | q | Paths | Rank of every holonomy per f | Floor | Source mass |
| --- | ---: | ---: | ---: | ---: | ---: |
| Repaired SIMPLIFIED | 2 | 6 | 12 | 72 | 80 |
| Repaired SIMPLIFIED | 3 | 8 | 16 | 128 | 136 |
| Admitted two-site | 2 | 6 | 12 | 72 | 76 |
| Admitted two-site | 3 | 8 | 16 | 128 | 132 |

`pairing_audit.py` rebuilds every graph edge from literal source events and
checks it is identical to the predecessor straight graph. It decodes each
saved crossing mask against the actual chronological ADD ordinals, constructs
new exhaustive edge-disjoint paths, and compares their operators with a
separate direct crossed-strand traversal. It binds the author's final saved
certificate field by field: source/event hashes, paths, literal circuits,
signed tableaux, all-f phases, ordered source-unary ordinals and literal
inverse circuits with inverse phase vectors. Every path has full ambient
B-rank. Toggling one actual routing bit fails the saved holonomy witness;
the original edge-omission and f=2 phase mutants are separately rejected.

Thus arbitrary Clifford-frame retiming of each listed fixed graph has rank
mass at least stock for every positive f, even if its frames mix tensor
coordinates. This supersedes 62/118 as the best retained lower bounds for
these graphs. It does **not** prove masses 76/132 or 80/136 optimal, nor does
it bound all equivalent scalar words, changed responses, helper couplings
or endpoint contracts. Since each path rank is at most the ambient rank,
these witnesses maximize the graph-pairing certificate objective; that is
distinct from minimizing the native invoice. No search is rerun in this
independent audit. The proposal counts are historical discovery records,
not proof coverage. No new native supplier recipe is needed for a lower
bound holonomy, which is not an executable child proposal.

