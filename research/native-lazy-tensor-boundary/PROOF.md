# Uniform lazy tensor routing at the actual lender333 boundary

JoyboyBrian, with substantial OpenAI Codex assistance. Apache-2.0.

## Source contract and quantified statement

The frozen predecessor PROOF and BOUNDARY are inputs, not newly certified native
recipes. They identify PR3945 `warps[4]=(1081,333,G,U,E)`, the three consumers
B1081/1082/1083 with signs -,-,+, and the next lender333 transition at B1097.
Its signed affine monomial M has translation458 and global phase i^3. The next
native transition is L C0 R. The predecessor establishes these literal local
interfaces and absence of intervening observations of333. We retain that premise.

For every integer f>=1 let N=512^f, and tensor **each individual operator**.
On arbitrary independent complex arrays v,d1,d2,d3, the required boundary is

    d_j -> d_j + sign_j M_f v;
    v -> L_f (C0)^tensor f R_f M_f v.

Set F=RM. The lazy schedule computes the three destination updates directly at
M's permuted addresses, leaves v unmaterialized, then applies F_f, the unchanged
paid child and L_f. Functoriality `(RM)^tensor f=R_f M_f` proves equality at every
width. This is not tensorization of a sum. The translation is applied separately
to every column; phases add modulo4, so the global i^3 becomes i^(3f).

All four array outputs agree before the common suffix. Therefore an identical
deterministic rounded suffix would also agree, but this does not establish that
suffix's accuracy or cost. Earlier consumers of destination arrays see exactly
the same values. The source owner's no-intervening-observation premise is vital.

## Uniform address algorithm without an N-entry table

Decode each fixed base monomial into p(x),q(x) on512 symbols. Exact cycle census
gives orders d_M=12,d_R=24,d_F=28,d_L=252. A tensor permutation applies p separately
to the f base512 digits. Its order divides d for every f, even with mixed digit
cycle lengths. Phases do not alter the permutation order and are never discarded.

For a monomial of order d, retain d fixed tables

    table_k[a] = (p^k(a), q(p^k(a))), 0<=k<d.

These contain512d pairs, independent of f. For a packed address x, maintain d
packed addresses p_f^k(x) and d phase sums sum_j q(p^k(x_j)) modulo4. Initialize
at x=0 in df digit steps. When digit j changes a->b, replace its contribution
using `(p^k(a) XOR p^k(b)) << 9j` and update the phase by subtracting the old and
adding the new table phase. Both shifts are explicit ABI operations. Every
address fits9f bits; table indices and shift counts fit an additional fixed
constant number of such words. No multiplication or unbounded array operation
is an instruction.

At x, scan all d addresses for their minimum. If x is that minimum, its orbit
appears exactly once. Find its length ell by the first return to x, then rotate
its source values in place: hold the old value at x, load the next old value
before overwrite, store the appropriately rotated held pair, and advance. The
phase attached to each original position is already in the maintained lane.
Fixed coordinates with nonzero phase must still execute. Fixed phase-zero
coordinates may be skipped only for a plain monomial, never when their consumers
need that value. This implementation uses two complex held values, destination
working pairs and sign selection; eight owned real scratch words suffice as in
the predecessor. No full clean array and no borrowed dirty array is assumed.

The lazy consumer scan uses one lane `(p(a),q(a))`, without a leader search.
Packed addresses/phase registers and the f-digit odometer are control workspace,
not productive data. They are initialized and cleared. At most252 packed address
and252 phase registers, f digit words and constant loop words suffice when the
common L pass is included. The fixed tables use at most252*512 pairs per pass,
plus retained base tables. These metadata are owned and retained for the word,
then cleared or retained under an explicitly persistent owner contract. They
are not free storage. A word needs9f+O(1) address bits and the independent scalar
precision width; ordinary bounded RAM permits both within a fixed number of
words when f and precision are O(log n). No fixed-tape translation is asserted.

## Complete bounded routing invoice and comparison

Let U_f=sum_{j=0}^{f-1} floor((N-1)/512^j). Exactly U_f odometer digits change in
one full scan; U_f<512N/511. Each lane-digit replacement uses two fixed-table
pair reads, one digit XOR, one shift, one packed XOR, two phase add/subtractions
and one mask. Initializing a lane uses f table/shift/phase steps. These are
specified bounded-word primitives, not a unit-cost whole-array permutation.

The strong materialized comparator combines M with its three consumers, sharing
source loads and prepared signs, then applies R. The lazy word scans consumers
using M and applies F. The common child and L suffix are identical and retain
all their actual costs; they are not removed from the complete invoice.

| Noncommon category | Materialized | Lazy |
|---|---:|---:|
| orbit/consumer lanes |12+24=36|1+28=29|
| initial lane-digit steps |36f|29f|
| lane-digit replacements |36U_f|29U_f|
| leader comparisons |(11+23)N=34N|27N|
| source real reads |4N|4N|
| source real writes |4N|2N|
| consumer real reads and writes |6N each|6N each|
| consumer ADD and prepared NEG |6N and2N|6N and2N|
| second pass phase NEG |N|N|

M,R,F have no base fixed coordinates, hence none at any positive tensor width.
R and F each have128 entries of every phase. Convolution of their phase counts
is uniform at every width; quarter-turns need0,1,2,1 real negations, whose mean
is1. Thus their second-pass NEG counts both equal N. Consumer signs are prepared
once and shared with M's materialization in the strong comparator. The comparison
does not claim avoidable read or negation savings.

Loop and orbit discovery are also charged. Both schedules have two full scans,
2U_f digit carries,2N iterations, and2N visited source/consumer positions. Their
per-cycle length searches cost at most N comparisons per monomial; the exact
count is N minus the number of full-order cycles. The baseline's two searches
cost at least(2-1/12-1/24)N, while the lazy search costs at most N. Thus no unpaid
extra length-search penalty hides in the lazy bound. Cycle-start/exit work is
bounded by a fixed number of instructions per processed coordinate. No data-
dependent branching or lookup on caller values is used. Resetting owned control
registers is linear in lane count plus f and does not reverse the inequality
when both comparators reserve the same maximum-sized workspace.

Preparation is not zero: all base recipe decoding, cycle census, orbit tables,
F composition, allocation, initialization and final clearing must be paid. F
composition takes1024 base table reads,512 writes and512 mod4 additions. The
noncommon expanded table totals are36*512 versus29*512 pairs. We do **not** infer
net machine time from these categories. A conservative complete ordinary-RAM
invoice is

    setup K + c_route U_f + c_leader N + c_data N
      + identical_paid_child(f,precision) + identical_L(f,precision),

with the displayed exact route/data coefficients and all register/loop costs
included by their stated per-coordinate bounds. K is a fixed constructively
finite setup bill for the chosen literal implementation and tariff, independent
of f. A crossover may be stated only after this actual K and primitive tariffs
are fixed. This paper proves a uniform traffic saving2N and reduced principal
routing work, not a measured total-time speedup, optimal tariff, or native-cost
admission. The O(N) address theorem closes the predecessor's exponential-table
risk without silently giving preparation or control a zero price.

## Scalar magnitude and remaining interface

Before the common child, all monomials preserve complex coordinate magnitude;
if incoming magnitudes are <=B, destinations are <=2B. Sign selection and ADD
require the corresponding guard capacity. The unchanged tensor child has exact
infinity norm2^(f/2); after it the source is at most2^(f/2)B. Its internal rounding,
word growth and accelerated recursive execution are separate contracts. Our
algorithm touches neither recursive rank nor owner width. Native allocation,
whole supplier compilation, fixed tapes, precision recovery and the selected
frontier are not established by this RAM construction.

## Verification and scope

The proof above supplies the all-f quantifier. The independent out-of-place
oracle checks all four dense actual arrays at f=1 and distinguishes wrong global
phase, translation and reversed composition. Small permutations with mixed cycle
lengths/fixed phases exhaust addresses through four tensor factors; exact lane
counts are checked against the formula. Eight actual f=2 columns cross digit
carries and verify source composition. Full actual f=2 arrays, common native
child/supplier replays, formal kernels and machine timing are not claimed.

## Executable-reference versus RAM tariff

Python is a semantic and route-counter reference, not an instruction-for-instruction
implementation of the scalar tariff. In particular `rotate` eagerly constructs
phase alternatives in Python, while the stated RAM schedule selects/reuses the
required signed operands. The exact NEG categories are for that declared schedule,
not measured Python unary operations or CPU instructions. Only explicitly
instrumented route/store counts are reported as executable counters.
