# Losing-first displacement-two retiming: contract and exact reduction

This is a source-bound finite certificate with a written argument. It is not a
formal-kernel proof or full multiplication/supplier admission. The scalar move
rules, frame lattice and sign argument are credited reuse from PR3886/3942.
The new domain fixes first final displacement exactly two and excludes neutral
first profiles. Both literal PR3734 providers are checked separately.

## Fixed contract

Move one existing ADD across exactly two consecutive scalar instructions inside
one original A-after-prelude, B-between-native-warps, or restore corridor. The
crossed instructions are ADDs satisfying the sufficient commutation condition,
or nonzero SCALEs with exact coefficient conjugation. Choose every legal binary
common first frame. The intermediate word must satisfy the unchanged boundaries
and have a nonzero, exactly sign-certified losing raw recursive profile.

Then retime any existing ADD to any cut in its allowed scalar corridor, with
any legal common binary frame. There is no second distance bound. The first
moved ADD may be selected again. All other instructions/frames, entrances,
target and centre cuts, native maps/cuts, helper identities and exits, wrappers
and caller contracts remain fixed. No gates or buffers are added or removed.
Cleanup is rederived as the inverse of the edited programme with the inherited
buffer substitution. A final word must satisfy the same boundary contract.

The raw objective is sum n_r r^(1-a), for real 0<a<1, with f(0)=0. Costs are
compared from the original word: first_delta + second_delta. A locally cheaper
second move is not sufficient when it merely repays the losing first move.

## Complete first frames

For an ADD at original index i, the only first insertion cuts are i-2 and i+3.
After deletion, the final index is cut-(cut>i), so the absolute displacement is
exactly two. Every cut must lie in the scalar corridor found by the unchanged
PR3886 sufficient crossing predicate. Native warps and phase/prelude boundaries
are never crossed.

For either touched register, remove the original event and read its predecessor
frame P and next constraint Q. A common new frame F must satisfy
L=P1+P2 <= F <= H=Q1 intersect Q2. Every admissible dimension is priced, with
removal and insertion costs reconstructed from these frames. First price cells
with a zero signed histogram are excluded explicitly: they are not losing
starts. PR3886's independently regenerated single-move census proves the
remaining first profiles are non-improving; the exact prefix certificate makes
each nonzero one strictly losing throughout 0<a<1.

For every retained dimension the primary enumerates *all* subspaces F in [L,H]
by successive one-vector extensions, deduplicated as full bit masks. This is
complete by induction on dim(F/L). The quotient has dimension at most three
in the pinned domain. A declared bound of four raises an error if exceeded;
there is no silent truncation or arbitrary representative first orientation.
A separate subset-XOR quotient-basis oracle checks every distinct source
interval/dimension in both providers.

Every retained literal first word is traced against fixed boundary equalities
and compared with the separately retained frame auditor. Rejections, if any,
are recorded; unrelated exceptions are not interpreted as legal exclusions.
The receipts retain first states and exact intermediate profiles.

## Which second moves require new prices

The argument is PR3942's changed-first-frame reduction and applies to any first
distance, not only its radius-one census.

If the second move selects the same ADD, deleting it leaves the original order
and frames of every other instruction. Sufficient scalar crossings compose
inside one connected corridor and SCALE conjugation factors telescope. The
final word is an original single-ADD candidate, so the regenerated PR3886
census covers it. Literal undo controls check this collapse and show that
omitting the first loss would manufacture a false improvement.

If the second ADD touches neither first register, the projected frame sequences
on its two registers are unchanged by moving the first ADD. That first ADD is
always a commuting, disjoint event. Removal/insertion constraints and scale
factors for the second move have original-word counterparts. Thus its delta
is an original single-move delta and the combined delta is a sum of two
nonnegative ones. Overlapping time intervals and different phases do not
invalidate this register argument.

The new census therefore enumerates every second ADD sharing at least one
register with the first, in all three phases, excluding only the same ADD.
Its scalar corridor is recomputed in the actual intermediate word, without
an extra radius cutoff. Removal and insertion costs are reconstructed for all
second cuts and dimensions, then the first loss is added before sign testing.
Once the first subspace is fixed, the second price depends only on dimension:
all frames between its L and H have the same climb ranks. Enumerating dimensions
covers every second price, rather than every distinct complete circuit.

The pricing relaxation may include a virtual climb at a fixed check. Such a
charge vanishes on every actually legal final word. A non-improvement proof
for the larger price set therefore also applies to every legal final word.
No candidate is admitted as a full physical supplier merely by being priced.

## Exact dirty-state algebra

For ADD g=I+c E_ds and ADD h=I+b E_uv the sufficient crossing rule is
s != u and v != d (using h's destination/source u/v). Equivalently neither
ADD's destination is the other's source; their elementary cross products
vanish, so they commute on arbitrary register values. Nonzero SCALE crossings
conjugate c exactly, multiplying/dividing by the crossed scale according to
direction and whether it scales destination or source. All coefficients are
exact dyadic rationals.

Every admitted first move receives an additional exact rational matrix check
on its complete three-instruction before/after block. Each participating
register starts as an independent symbol, including arbitrary dirty helpers.
Equality is therefore an identity on all dirty inputs, not a zero-helper test.
Unchanged surrounding scalar and native free operators compose with this
identity. The same elementary identities justify every legal second crossing.
Original frame/boundary checks ensure those identities use legal staged calls.
Inverse cleanup is derived from the literal edited sequence. Non-target
instructions never read target registers under the audited contract, so deleting
target-only writes preserves the helper block operator. The buffer substitution
is injective on restored helper identities. Equality of the forward helper
operator therefore also preserves its rederived inverse on arbitrary buffer
symbols and the cleanup boundary; it does not assume zero dirty helpers.

The retained complete interpreter additionally replays the baseline and a
deterministic first/middle/last sample per phase, including actual final second
moves. Every whole-word replay includes 632 live inputs and 91 independent dirty
buffers, both orientations, reverse pull-back and cleanup boundaries. Sample
coverage is labelled explicitly; it is the universal block identities and
boundary argument, not sample frequency, that establish the full first class.
Retained auditors are credited reuse, not newly independent interpreters.

## Exact signs and what the result means

For each combined signed child histogram d of zero rank mass, define
C_k=sum_r d_r min(r,k) and S_j=sum_(k<=j) C_k. PR3886's credited curvature
identity expresses its real-power moment difference as

    sum_j S_j (theta_j-theta_(j+1)),
    theta_k=2 f(k)-f(k-1)-f(k+1).

For 0<a<1 these curvatures are positive and strictly decreasing. The last theta
is set to zero only for the finite summation identity. Nonnegative S_j prove
non-improvement for the whole interval. The executable checks exact integer
rank mass, caps and prefixes; a separate implementation reconstructs them.
A failed sufficient sign test is an unresolved case, never automatically a
counterexample or an improvement. The verifier preserves witnesses and fails
rather than issuing PASS if any combined sign remains uncertified.

When every emitted combined type passes, the reduction and finite certificate
prove that the declared losing-first displacement-two class cannot lower this
raw moment. No all-distance, all-rewrite or global optimality claim follows. In particular,
neutral frame-preserving displacement-two starts are excluded here and are not
fully covered by PR3941's adjacent fixed-frame domain or PR3942's radius-one
domain. Even together these results do not close the entire radius-two class.

## Complete local bill and remaining obligations

The receipts record the original recursive profile, children/rank mass, every
intermediate profile, all combined signed profiles, helper width inventory,
entrance/exit fingerprints, scalar/native primitive inventory and coefficient
bit bounds. A constructive finite bound for every final retimed scalar coefficient adds
the absolute binary SCALE exponents in its unchanged corridor to the source
numerator/denominator bit lengths. Distinct retimed ADDs obey this separately;
two selections of the same ADD telescope to one original move. This is an upper
bound on this finite class, not a uniform precision or tape tariff. Retimings add no instruction, helper or private dirty buffer; rank
mass and helper widths remain fixed. The intermediate child count and moment
can be worse, and that increase is charged in the combined comparison.

The inherited outer profile is authenticated source evidence only. Fresh native
Gaussian/Clifford phase, physical hosting/allocation and whole-owner chronology,
uniform precision/stock/tape, all-size compiler, supplier/outer, analytic and BIT
obligations are unknown or inherited as labelled, never priced at zero. Fixed
positive normalisers and common bills preserve the raw ordering; a rewrite
that also reduces a common physical cost is a different comparison. No new
kappa, supplier admission, independent human review or kernel proof is claimed.
