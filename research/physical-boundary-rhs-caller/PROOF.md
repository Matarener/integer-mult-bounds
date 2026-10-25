# Actual two-component Gaussian RHS boundary

JoyboyBrian, substantial OpenAI Codex assistance. Apache-2.0.

## Decision and exact source boundary

NARROW the explicit `physical-boundary-pages` handoff to its missing RHS
layout, using the actual `Core.gather` and `Core.first_cell` methods at base
32890bc5de034ab8fc93ac88ead7279a6a416d04. The predecessor has a complete
inverse-block consumer and a charged classical kernel. It has no actual RHS
layout adapter. A separate seven-product kernel does not solve this boundary.
This contribution removes that missing adapter for the real and imaginary
components of **one** actual Core invocation. It is not a many-field supplier.

The exact first-pass contract is the one in `gaussian_core.py`: read the
complete complex source, validate its disk bound in the real pass, select and
scale the listed rows, execute each interior solve, subtract its boundary
couplings, and round the resulting RHS once. `first_pass_pair` invokes those
unchanged methods and retains their full row/count/page-extent checks. It
parks the first component while producing the second, and erases each selected
interior stream after its first pass. Borrowed source and page heads return.
The caller has not yet run its second-cell reconstruction or normalization.

The exact reference for the executed fixture is LU(round_P(S)), with S the
Schur complement of its supplied exact principal matrix. The block page
producer computes exact inverses of these factors and rounds once, unchanged.
The fixture is adapted from Jose Manuel's supplied-factor consumer check at
p=4, P=16, width=32; it is not a production Gaussian catalogue or an analytic
precision certificate. The nontrivial five-row fixture selects [0,1,3,4,5]
from six complex rows, has three interior rows, and yields two boundary rows.
Both actual interior calls execute. A one-row fixture exercises incomplete
rows and incomplete component columns at B=4. B=1 exercises separate batches.

## Quantified layout proposition

Let n,B,w be positive encoded integers. Let two distinct borrowed tapes hold
exactly n literal w-bit records each, in the actual Core real and imaginary
boundary-row order. These records are opaque to this adapter; it does not
interpret a sign, magnitude, or numerical grid. Metadata and payload tapes
are disjoint, every supplied payload head is at the first body cell (head 1),
and every supplied tape is a valid complete canonical stream. Entry heads
are checked before layout reads. The fixed scratch pool has sufficient free
roles for the declared Count operations and output leases.
Let K=ceil(n/B), N=KB, J=ceil(2/B), and A=NJ B w.

`pack` returns, for batch b, row i, local column j, the record from component
bB+j and row i when i<n and bB+j<2; otherwise it returns w zero bits. Both
component inputs are restored, including their heads. `unpack` on a valid
consumer output with zero padded rows and columns returns exactly the two
n-record component streams in original order and restores its borrowed input.
It rejects nonzero padding and every trailing or short stream. Both helpers
transfer owned pool leases to their caller; callers must clear them before
pool reuse. On a detected invalid stream, acquired output leases are cleared.
The successful-domain theorem does not promise rollback of arbitrary faults
inside the inherited arithmetic runtime.

Proof: for a fixed batch, both input heads start at record zero. For each
in-range component its unique local column is visited exactly once per actual
row, so its head advances by one whole record. Components outside that batch
are never copied. Each batch additionally scans both entire input streams,
checking their exact extents, and restores their heads. Thus induction on rows
and batches gives exactly the stated padded order, including B=1. Every bit
copy uses a current-symbol read, a local append and a unit move. Zeros are
written physically. No host index, payload conversion, random lookup or free
head jump is used. The inverse visits the same triples in the same order,
appending each actual component record to its own stream and rejecting any
nonzero discarded bit. Each component is visited in increasing row order,
so the two output streams have the original order. All loops use the retained
encoded Count/indices implementation on the fixed pool.

## Unchanged consumer and numerical scope

For exact factors satisfying the predecessor's adjacent-block support and
positive setup-pivot hypotheses, the unchanged `prepare_pages` and
`BoundaryPages.run` apply the predecessor's literal rounded inverse-block
function. Packing and unpacking copy all actual bits exactly, so this
composition introduces **zero additional numerical error** relative to that
function. This statement does not compare that function with scalar
`BandedSolve`. Their rounding sites differ: the predecessor's actual
four-row P=6 witness gives -13/64 for the old second entry and -12/64 for the
blocked second entry. Relabeling that output as an unchanged Core result
would be invalid. The full second-cell reconstruction and a revised complete
Core error allowance are still adoption obligations.

For identity padding, the padded coordinates remain zero: exact padded factors
are block diagonal between actual coordinates and identity coordinates;
their inverses preserve that separation, and entrywise rounding preserves
zeros. Every product and recurrence therefore keeps padded RHS coordinates
zero. This justifies `unpack`'s stronger zero-padding check on a conforming
consumer. This is a source-relative argument, not an independent audit of
the entire predecessor numerical theorem.

## Complete cost boundary

Every cost below is charged; none is replaced with a free host gather.
Let L=1+ceil(log2(n+B+w+2)). The layout copies 2nw actual payload bits,
physically emits A-2nw padding bits, validates 2Jnw borrowed bits and restores
all heads. Its inverse reads A bits, emits 2nw bits and restores heads. All
owned outputs must then be cleared. Ignoring encoded-counter work, total
local read/write/unit-move work is O(A+Jnw), including those clears. Encoded
indexing, products, division, comparisons and additions give the conservative
bound O((A+Jnw+1)L^3) using the retained elementary Count arithmetic; numerical
parameters are never decoded into host loop bounds. J<=2, so the two-component
layout is O((KB^2w+nw+1)L^3). It is not claimed optimal in B.

The complete caller bill is:

1. actual first-pass Core work for both components, including the first
   parked RHS, encoded page parsing, selection, two interior solves in the
   five-row fixture, coefficient reads and all temporary cleanup;
2. exact-reference factor construction and unchanged physical inverse-block
   page setup, separately funded as preparation;
3. the layout work above, initial/final marker work and ownership scans;
4. unchanged consumer work: exactly 2(2K-1)J B^3 scalar multiplications,
   its transposes, row reversal, padding checks, copies and erasure;
5. explicit consumption of the consumer's protected output and all packed,
   scattered, RHS and matrix/page leases.

The adapter exposes 2nw RHS bits, A packed bits, A returned bits and 2nw
scattered bits at their coexistence peak: **2A+4nw** payload bits, in addition
to inherited core, factor-page, consumer and scalar-child scratch. Four
factor page streams occupy 2(2K-1)B^2w bits. No cleared backing is released or
subtracted from the space bill. Encoded descriptors and fixed-pool high-water
capacities are additional, not zero. An enclosing call must add the actual
source/page/dirty frame and inherited scratch bounds. The finite receipt
reports every constructed tape's retained cells, including checker-created
source/setup tapes; this deliberately conservative number is not the
universal space coefficient or a Python heap measurement.

The executed read/write/move phase vectors are measured on the inherited
Tape meters. They count numerical/metadata tape actions as well as payload;
the non-instrumented Python finite-control steps are represented by the
written conservative bound, not misreported as an exact instruction total.
Independent checker decoding is outside those phase meters and is prohibited
inside measured execution by `no_decode`. Supplied-factor fixture generation
is checker preparation, not an implemented original-Gaussian coefficient
producer. The complete supplier's preparation/amortization, numerical error,
fast seven-product tariff and all-size outer transfer remain unknown here.

## Controls and evidence boundary

The independent exact Fraction first-pass reference checks both RHS streams.
The predecessor's separately written Fraction block oracle checks all actual
returned components after physical unpacking. A distinct literal-bit fixture
checks the padded permutation without importing the caller arithmetic.
Actual corruptions test nonzero padding, short/trailing streams, metadata and
payload aliases, component-order discrimination and successful reuse after
rejection. Borrowed sources/pages and nonzero dirty spectator backing/heads
are compared in full. Normal and optimized commands retain explicit checks.
Finite receipts corroborate this scoped proof; they are neither formal-kernel
nor independent human review and establish no new kappa.

## Open next questions

- Install a block-aware second-cell consumer and prove its complete numerical
  difference budget against the original reference. First propagate the
  predecessor's rounding witness through one actual second-cell return.
- Replace the classical product only with an actual fixed-tape seven-product
  implementation retaining this ABI, quadrant movement and parked backing.
- For an actual many-field supplier, first identify its real input layout and
  field multiplicity. This R=2 adapter supplies no arbitrary-R field batching.

Credit Jose Manuel/jmbarrancoml for the physical Gaussian Core, word runtime,
supplied-factor fixture and original numerical block handoff; JoyboyBrian's
physical-boundary-pages predecessor; Vlado Vojdanovski's block proposal;
Cinna Davis; Chafik Boukhalfa's branch-free interior reference; and the
retained Gaussian/FFT/Harvey–van der Hoeven and tape-runtime lineage.
All original source bytes and notices remain unchanged.
