# A paid two-active-column kernel for the actual complex RHS pair

JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.

## Decision and source contract

NARROW the completed PR5483 real/imaginary RHS bridge to the unchanged
`physical-boundary-pages` consumer's avoidable padded-column arithmetic.
Its actual caller has R=2. For B>2 its B-by-B RHS blocks have B-2 columns
identically zero, but the predecessor executes B³ scalar products per matrix
product. A further normalized-Core integration would retain this cost; it does
not remove it. This change refines the ordinary scalar arithmetic of that
consumer. It is not a recursive paid-job, supplier, or kappa improvement.

The exact input/output interface is unchanged: four inverse/coupling page
streams, encoded n,R=2,B,w,P and one padded batch-major RHS stream; a protected
full padded return; borrowed ports restored; owned work cleared and retained
backing charged. The exact reference remains the supplied LU(round_P(S)).
The scalar old `BandedSolve` is numerically different and is not substituted.
Source bytes at base32890bc5de034ab8fc93ac88ead7279a6a416d04 are pinned.

`PairBoundaryPages` inherits the entire owner, source/metadata validation,
page setup, wide-word formula, two pass orders, predecessor retention, row
reversals, rounding, return consumption and cleanup. Only the exact product
method changes. At B<=2 it delegates to the original product, with a charged
encoded branch. At B>2 its operand contract is that columns2,...,B-1 of the
second factor are zero. The runtime checks that contract on physical signed
records. The theorem specializes the inherited owner to R=2, not arbitrary
many-field calls. Unsupported nonzero inactive columns fail closed; no broad
replacement contract for arbitrary R is asserted.

As before, owned scratch is blank on entry and has sufficient fixed-pool
capacity. Arbitrary *disjoint borrowed dirty spectators* are preserved. No
claim of arbitrary dirty contents inside the source's owned scratch is made.
Heads and metadata satisfy the inherited canonical-entry conditions.

## Column invariant and exact arithmetic

In one admitted R=2 RHS batch, all columns after the first min(2,B) are zero.
The initial padding check establishes this. Every matrix product multiplies
from the left, so an identically zero input column remains zero. Subtracting
it from the corresponding zero RHS column gives zero. All predecessor
rounding operations preserve zero. Reversal permutes whole rows, not columns.
Thus induction on solved blocks and then on the two ordered passes establishes
the same invariant at **every** product invocation. At B=1, there are two
one-column batches and the inherited product is used; at B=2 there is one
full-width batch and the inherited product is used.

For B>2, `active_transpose` performs two complete sequential scans of the
second factor. Each scan reads all B² signed records, rejects a nonzero
inactive entry and copies the selected active column. The resulting tape
holds exactly two columns in the same order as the first two columns of the
original full transpose. All scans and head returns are physical.

For each first-factor row, `product` copies the same B records to the same
bounded row role. For each active column it reads the same B pairs, calls the
same physical scalar child in the same k=0,...,B-1 order, and applies the same
exact signed `add` after each term. The same wide signed writer emits the
completed sum. There is no new rounding, summation order or precision choice.
Inactive columns instead emit the exact signed zero that the old all-zero
dot product would have produced, including its full physical width. The full
B² output extent and every downstream loop are unchanged.

Induction over terms proves equality of each active partial sum, not merely
the final matrix identity. Inactive products/sums are exactly zero. Thus all
inherited intermediate headroom bounds remain sufficient, including
`wide=2w+ceil(log2 B)+2`. The output is bit-for-bit the predecessor product.
The column invariant then proves equality of both complete rounded passes
and the full padded return. Relative to this block function, added numerical
error is exactly zero. This result neither closes original-S perturbation nor
identifies the function with old scalar BandedSolve.

## Complete ordinary arithmetic and movement bill

Write K=ceil(n/B), J=ceil(2/B). The complete consumer still makes exactly
m=2(2K-1)J matrix products. The dense baseline makes mB³ physical signed
scalar calls. The refinement makes

    m B² min(B,2)

calls, namely 4(2K-1)B² for B>2. These are ordinary physical multiplication
calls, not recursive native jobs. Every coefficient page, normalization point,
row reversal, validation, owner scan and cleanup outside `product` is retained.

Let M(w) upper-bound one inherited signed multiplication, and
L=1+ceil(log2(n+B+w+P+2)). For B>2 a refined product pays:

- 2B² signed-record reads to form/validate the two-column transpose;
- B² first-factor records, 2B² active term-pair visits and scalar calls;
- B² full wide output records, including B(B-2) explicit zeros;
- all row/transpose rewinds, Count comparisons/indexing, signs/additions,
  scratch clearing and successful head restoration.

The retained `read_fixed`, `write_fixed`, signed arithmetic and Count routines
therefore give the conservative bound

    O(B² [M(w)+(w+log(B+2)) L³])

per refined product, in addition to the unchanged full-consumer bill. This
replaces the baseline cubic product component, not the entire first-pass or
preparation complexity. The extra zero-validation comparison and active-branch
control are included. No host payload decoding, random gather, unmetered jump
or new tape allocation occurs inside the sealed physical call.

For R=2 the arithmetic part becomes O(ceil(n/B)B²), rather than
O(ceil(n/B)B³). This is a local cost refinement. It does not by itself give a
better asymptotic supplier than the old scalar boundary solver or the desired
seven-product/many-field design. B<=2 retains the original arithmetic count
and a small, paid descriptor branch; no strict finite improvement is claimed
there. Strict measured dominance for every integer n,B,w is not asserted.

The two-column transpose occupies2Bw data bits instead of B²w. The row role,
all full B² input/output matrices and complete padded ABI remain. Additional
encoded control is O(log B). The inherited 256-role boundary pool and scalar
child owner are unchanged. Because physical backing retains its high-water
capacity, a caller may not subtract erased storage or assume a prior large
call shrinks after reuse. The theorem gives the reduced transpose demand and
an inherited O(B²w) whole-consumer workspace bound, not a universal smaller
leading constant for every allocation history.

The actual B4 gate compares fresh matched owners and repeats the refined
owner with the same packet. It includes the entire `run`, protected output
clear/marker erasure and `idle`; it counts reads/writes/unit moves on **all**
constructed tapes, including borrowed parameter actions and scratch. It sums
full retained capacity of every owner-created tape, including the word child
and unused/erased backing. Common Core first-pass, page preparation and RHS
packing are unchanged and separately retained; their costs do not vanish.
The observer accesses tape arrays solely to compare data/capacity and never
feeds those values into the physical execution. Python control steps are not
mislabelled as tape instructions: the written bound above pays their encoded
and finite control work, while finite receipt vectors report the three actual
meter categories only. This is not a literal compiled machine-code theorem.

## Actual caller and discriminating finite cases

The retained PR5483 source helper executes unchanged `Core.gather` and
`Core.first_cell` on both components. The supplied-factor fixture at P16/w32
has five source rows, three interior rows and two boundary rows. Its block
answer differs from its RHS, so a skipped consumer cannot explain equality.
The B4 case exercises both zero columns and incomplete padded rows.

A second supplied-factor fixture uses eight source rows in two cells (5,3),
three interior rows and five boundary rows. Additional exact1/32 neighboring
boundary couplings produce a nonzero cross-block dependency at B4. The actual
Core first passes execute, and the independent exact construction forms
S, round_P(S), and its LU reference. This is an explicit supplied-factor
extension for cross-block coverage, not a claim to execute the original
periodic Gaussian coefficient producer or its production analytic bounds.
Both complete physical consumers and a separate Fraction block oracle agree
on every returned padded word. B1/B2 cases retain the fallback boundaries.

A separate physical product fixture has nonzero active sums, cancellation,
negative terms and zero inactive columns. It distinguishes omitted second
columns and premature per-term rounding. Actually changing a third-column
input to nonzero must reject, clear temporary leases and allow a valid reuse.
Full borrowed snapshots and a nonzero unrelated dirty tape are unchanged.

The finite B4 adoption decision requires lower complete metered tape work
and no increase in matched fresh-owner retained backing; it does not accept
only a smaller scalar-call count. RESULT.json records exact values and limitations. B1/B2 preserve the original
product algorithm and outputs but pay the encoded dispatch overhead; no cost
improvement is claimed for those fallback sizes.
Finite tests corroborate the source-relative all-size argument; they are not
independent human or formal-kernel acceptance.

## Open next questions and credit

1. Bind a block-aware second-cell reconstruction and normalized Core error/width
   ledger before installing this function as a complete Core replacement.
2. Identify a real many-field supplier before generalizing the two-component
   contract. Its layout, field multiplicity and retained stock cannot be invented.
3. A genuinely fast seven-product kernel still needs its exact tape quadrants,
   parked recursion, precision and complete paid comparison.

Credit Jose Manuel/jmbarrancoml's physical Gaussian Core, inverse-block handoff,
word runtime and supplied-factor fixture; PR5483's actual pair binding and
physical layout; Vlado Vojdanovski's block proposal; Cinna Davis;
Chafik Boukhalfa's branch-free interior source; and the retained Gaussian,
FFT, Harvey–van der Hoeven and fixed-tape lineage. PREDECESSOR records exact
public PR5483 hashes for the copied/adapted source helpers. They are retained
package bytes, not a runtime dependency on an unmerged Git object. No frozen
predecessor, selected frontier or numerical allowance is changed.
