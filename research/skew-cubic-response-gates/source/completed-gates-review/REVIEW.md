# Independent review of the completed kernel and trajectory gates

No correctness defect was found in the covered mathematical statements. There
is one notation clarification: every product written `B_(2q)...B_4` in the
kernel proof means the **even-index product**

    B_(2q) B_(2q-2) ... B_4.

Inserting the odd B factors would make the telescope false already at q=3.
The frozen producer implements the even-index product correctly. This review
does not modify the source package or any earlier independent audit.

The two primary sources are
`../general-clifford-retiming/kernel-search/PROOF.md` and
`../pauli-caller-retiming/TRAJECTORY-PROOF.md`. The contiguous scalar-gadget
derivative and the separately requested cubic-response trace gate were also
reviewed. Exact source hashes are in `SOURCE-PINS.json`.

## Fixed two-site skew-kernel implication

Write `E_q=B_(2q) B_(2q-2)...B_4`. The source's recurrence has the exact
telescoping identity

    F_(2q)^-1 T_q = E_q F_3^-1.

For its induction step use `P_(2r) N_(2r)=N_0 P_(2r)`, the commutation of
J with N_s for s>=2, and `Jbar=N_1 J N_1^-1`. The odd fresh inverse from
`F_(2r)^-1` cancels the explicit `N_(2r-1)` in the transport; it does not
produce an additional odd B factor. The base is `T_2=P_4 Jbar`.

The deleted correction is `C=F_(2q) Du^-1 F_(2q)^-1`, where
`Du=E_q B_3 J`. Therefore

    L=C T_q P_3
     =F_(2q) J^-1 B_3^-1 F_3^-1 P_3
     =-N_(2q) N_(2q-1) ... N_3.

The last equality retains the whole-field sign from `J^-2=-I` and
`N_3^2=-I`. Thus `ell=nu(L)=4q-4`. Also `R=T_q^-1 P_(2q)` has rank rho,
and the transport product gives `rho <= (q-1)b+2(q-2)`. For a physical
monomial first replacement U, the required second replacement
`V=L U^-1 R` has rank at least `ell-rho` (and in fact at least
`abs(ell-rho)`). This uses no right input gauge.

The Q relation is phase sensitive:

    Q=J^-1 P_1 N_0^-1 J^2=J P_1 N_0^-1,
    (N_1 Q^-1 N_1^-1)(N_1 J)=N_1 N_0 P_1.

Consequently `w+v>=4`, while `v<=min(2+a,2+b,4)`. The baseline N bill is
`2[k(n-1)+1]+2(q-1)=8q^2+10q+2`. The other ranks are two uncompleted J,
three completed Jbar per repeated block, one Q inverse, and the later
replacement. Its complete rank bill satisfies

    M=8q^2+10q+2+2a+3qb+w+s,
    D=n(4q+v)-M
      <=(2q+3)v-(4q+6)-2a-(2q+1)b <= 0.

For v>=2, substitute `a,b>=v-2`; the resulting expression is exactly zero.
For v<=2 it is at most `(2q+3)(v-2)`. There is no even-rank premise. The
saved odd rank-one skew kernel is a valid equality case. The rank-zero
address-swap example whose completed conjugate has rank four also confirms
why the `3qb` charge cannot be replaced by `3qa`.

This is a written all-q implication of the specified scalar topology,
event inventory and isolated-transport recurrence. The repeating-block
source-to-event/controller binding remains a hypothesis beyond q=2,3;
the review does not turn it into an unconditionally serialized all-q caller.
The exact event fixtures at q=2,3 are independently bound to all original
columns, both literal inverse orders, the complete transported column and
inverse row, and the local replacement including Gaussian tensor phases.
The finite q=2..8 operator grid is corroboration of the written identities,
not the proof of their all-q domain.

This rank bill is unweighted. Turning it into a supplier moment requires
the stated equal-volume full-bank child normalization and a compatible
recursive target. Rank alone does not price ADDRESS/scalar scans, source
access, rounding, owners or tape. New selected native recipes for the
failed kernel candidates are not admitted by this review.

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

## Cubic quadratic-identity gate

The separately requested cubic proof is valid over the stated Gaussian
rational domain. If a unitary Clifford U with entries in Q(i) satisfies
`U^2+U+I=0` on the entire bank, its primitive cubic-root multiplicities
must be equal because its trace lies in Q(i). Hence
`Tr(U)=-2^(M-1)` and `|Tr(U)|^2=2^(2M-2)`.

On the fixed-label space `ker(S_U-I)`, the Pauli conjugation signs form a
character: the same Pauli multiplication phase appears on both sides and
cancels. Its sum is either zero or the size of that binary space. The
nonzero trace of Ad_U equals `|Tr(U)|^2`, so
`rank(S_U-I)=2`. Its B block is an off-diagonal submatrix, yielding
`native_rank(U)<=2`. This does not impose a support or tensor assumption.

The proposed base J has exactly the source matrix, circuit phase,
`J^3=I`, and rank one. Independent exact entrywise tensor replay for f=1..4
confirms that the quadratic relation fails from f=2 onward; at f=2 its
residual has trace six. Thus a response family with native rank proportional
to unbounded f cannot retain that two-power identity over Q(i). Three-power
callers, non-Clifford responses, restricted-input quotients or non-Gaussian
root-of-unity scalars are outside this conclusion.

## Verification distinction

`audit_gates.py` does not import the kernel proposal constructor or the
trajectory graph constructor. It independently compiles/traverses the saved
literal sources, uses a separate exact bank-column/inverse-row model, and
checks all four kernels at q=2,3 plus an algebraic rank grid q=2..8.
`replay_sources.py` separately re-executes the authors' read-only validator
functions (140 native-circuit inverse pairs, eight trajectory fixtures,
72 SWAP expansions, four cubic tensor fixtures, four crossed full-stock
pairing certificates). These are recorded as
same-engine replays, not independent algorithms. Normal and `-O` pass;
workspace modules execute exactly their hashed source bytes with historical
assertions active, ignoring bytecode caches. The controls reject an omitted
edge and an f=2-only wrong phase, preserve the odd-rank example, and detect
the completed/uncompleted rank distinction. All earlier audits and source
artifacts remain unchanged. No formal-kernel proof or new kappa is claimed.
