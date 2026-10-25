# Independent dense-guard review before primary implementation inspection

Context: canonical main `12fa8c5c844be21bfefb38a19503fbd867a11244`,
priority7; retained Cinna Davis PR4100 `CRT.md` dense-guard paragraph and
`check_batched_crt.py::good/linear_guard`. No primary scanner code was read
before this oracle was fixed. Source SHA256 is pinned in the oracle.

## Predicate and bit order

Let B=2^G and let r active digits occupy the low rG bits of complete H-bit
control fields U,T, with H>=rG. For each target position p_i in Y define

    v_i = floor(Y/2^(p_i+1)) modulo 2^(K-1).

The guard is good exactly when every active U/T digit differs from B-1
and every `v_i` satisfies

    2B <= v_i < 2^(K-1)-2B.

The lower boundary is inclusive and the upper boundary strict. Target
parity at p_i is omitted. The complete K-bit guard intervals are disjoint
and fit within Y. On a physical MSB-first scan the comparison bits for a
guard run from p_i+K-1 down to p_i+1; the target bit itself is skipped.
Comparison flags retain the first unequal bit. An all-ones flag is reset
at each active digit boundary. Upper unused control bits and all other
Y spectators must be ignored even when dirty.

This factorized predicate does not require a permutation, source switch
evaluation, modular arithmetic, sparse-hole extraction or record sorting.
The literals are numerical address bits and comparison thresholds. A mask
must declare whether one means good or bad, and must follow the complete
address-counter order exactly once, including zero and the all-ones address.

## Complete independent oracle

`independent_guard_oracle.py` uses integer quotient/remainder expressions,
rather than a stencil scanner, and compares every address against both
authenticated source predicates. Address order is numeric MSB U|T|Y,
`address=(u*2^H+t)*2^Y+y`.

The first fixture has G1,K5,H2,Y10, positions(0,5): L14 and all16,384
addresses. Both U/T fields must be zero. Each 4-bit comparison field has
eight accepted values4,...,11, while both target parities are free. There
are exactly256 good and16,128 bad addresses.

The second has G2,K7,H3,Y9, position1: L15 and all32,768 addresses. Each
control has six accepted values (the low two-bit digit must differ from3,
while its high bit is arbitrary). The six-bit comparison has48 accepted
values8,...,55. Target parity, lower Y bit0 and upper Y bit8 are free.
There are exactly13,824 good and18,944 bad addresses.

The oracle records good-mask hashes in both binary-byte and ASCII-bit
representations, plus an ASCII bad-mask hash. It checks196,608 target-parity
and dirty-spectator invariance toggles, twelve explicit interval boundaries,
and witnesses for strict-lower, inclusive-upper, parity-in-comparison and
omitted-higher-active-digit mutations. A separate dirty-upper-control
witness is accepted, whereas an actual all-ones low active digit is rejected.

These are complete U|T|Y **predicate projections**, not complete three-H-field
reservoir placement or payload-permutation executions. Appending an omitted
back field adds independent spectator bits; no production placement claim
is inferred from the reduced fixtures.

## Scanner review obligations

For an admitted ordered finite-alphabet stencil, its cell count must be O(L)
with fixed alphabet/role types. All comparisons and counters need an explicit
sequential implementation, without a free numerical L, M or random-access
position register. The binary counter must emit exactly2^L masks and terminate
on final overflow, without repeating zero. Every read/write/head return,
descriptor pass, mask write and final rewind must be paid.

Final overflow makes a binary counter zero; it does **not** blank its tape.
If the contract promises erased private work, a literal final erase/return
pass is required. Output-mask preservation and original-stencil preservation
are separate from private cleanup. A host stencil builder is not a uniform
paid builder unless its own lowering is supplied. The scanner theorem may
instead take an admitted stencil as input, with that boundary explicit.

An O(ML) scan bound becomes O(V) only with the source relation L=O(R),
V=MR, such as L,R=Theta(p). It does not pay exceptional key evaluation,
extraction, sorting, reinsertion, full E preparation or multiplication.

## Credit and scope

Cinna Davis supplies the dense-guard comparison and linear-pass proposal.
The source NOTICE retains the guard/compact-control lineage. This is separate
OpenAI Codex semantic review, not independent human review or formal-kernel
verification. The selected frontier and kappa are unchanged.
