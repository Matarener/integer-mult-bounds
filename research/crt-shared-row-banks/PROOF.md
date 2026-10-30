# Cross-row ROM reentry with fixed historical extents

## Statement and premises

Fix an admitted node of the two-width CRT caller in PR #5625. Keep its axis
source, widths, moduli, eight protected numerical words, precision P and row
sequence. Supply one clean ROM bank with the 52 distinct role backings of
PR #5519, separate from source, protected words, numerical workspaces and staging.
Assume the source RowEntry, ROM producer, joined-query and paid source-update
theorems cited in PR #5625. This proof builds on them; it does not re-prove them.

For any finite compiled row sequence with q >= 1 active rows, the changed
caller executes the same row permutations and returns each ROM role blank
across its entire allocated extent before the next row. It retains one ROM
bank instead of q distinct banks. Every other row workspace remains retained
and billed. Malformed executions and failure rollback are outside the theorem,
as in the predecessor.

## The interface

`adapt_source` makes five exact, guarded substitutions in the authenticated
joined-query source. They add a bank parameter and owner reference, acquire
that bank before constructing the four header wrappers, replace the fresh
service allocation, and release ownership after query retirement. Every
runtime tape read, write, move, producer instruction and source-update call is
unchanged. The original source files and their credit lines retain their bytes.

`BankPool` is a model of supplied blank physical tapes with a single owner.
It rejects a simultaneous second lease and a release of a different bank.
The role map and wiring are compiled topology. Acquire and release touch only
fixed ownership metadata, with no tape-content scan, copy or erasure. Runtime
coordinates remain on the predecessor's tapes. The external verifier observes
blankness and physical identity; those observations provide no runtime values.

The source's numerical workspaces, coordinate tape, countdown tape and result
tape are freshly constructed per query. The staging tape from PR #5625 remains
shared as before. The construction does not assert reuse of those other roles.

## Historical-extent induction

Use the credited role table in PR #5519, PROOF.md, section "Exact retained
footprint of this shared ROM bank". For N=2^H and
J=N(H^2+3H+1), preallocate:

* 44 scalar roles and three ordinary headers, P+2 cells each;
* offset header, P+3 cells;
* arena, 5PJ+2 cells;
* spool, N(2H-1)+2 cells;
* complete layers, (N+1)(2H-1)+2 cells;
* selected ROM, N+2 cells.

Here H is the largest active right-axis width in the compiled sequence.
The predecessor proves these per-role extents are nondecreasing in height,
are independent of runtime offset values, and bound every successful visited
cell. No successful path steps beyond the displayed right marker. Their sum is

    B(P,H) = 5P 2^H(H^2+3H+1) + 2^H(4H-1) + 48P + 2H + 104.

This formula and its rolewise derivation are predecessor results. The new
use is to supply the same physical roles to the next RowQuery constructor.

Initially all allocated cells are blank. Couple an invocation to the credited
fresh-bank execution by equal symbols and heads on each visited prefix. Extra
cells are blank and lie beyond that execution's maximal visited cell. Unit
reads, writes and moves therefore take the same branches and produce identical
outputs. The preallocated version never needs to extend a list. The inherited
producer retirement clears its used private prefixes; the joined caller erases
layers, ROM and all headers. Untouched suffixes remain blank. Query close then
retires the result and numerical Entry before releasing the bank lease.
Thus the entire historical extent, rather than just the latest prefix, is
blank at release. New header and observer wrappers begin at physical origin
zero, and producer execution initializes each role head at zero as before.
This is the entry contract for the next row. Induction proves reentry for every
finite compiled sequence. An idle row neither acquires nor changes the bank.

The source-update consumer still copies the live output to separate staging,
closes the query, and then changes the owned source. Consequently bank reuse
does not extend the source borrow or erase a needed result. The credited
current-state composition theorem now applies row by row. A full level and its
reverse restore the same source and protected dirty words.

## Complete retained-work accounting

For a fixed admitted node, active H is the same for every active row. If any
right axis is long, it is active in every row and determines H. If all right
axes are short, they are either all idle or all active, and active H is their
common width. This uses the source two-width contract.

Let E_j count row j's numerical owned backing, X_j its three non-bank joined
ports, and S the one staging extent. Count physical identities once, including
blank retired backing. For q >= 1 active rows, the distinct-bank contract uses

    S + sum_j (E_j + X_j + B(P,H)).

The new interface uses

    S + sum_j (E_j + X_j) + B(P,H).

The exact reduction is (q-1)B(P,H), positive for q >= 2. This is a statement
about the declared ROM change; it does not replace the sum of numerical
workspaces by a peak. Source backing, eight protected words and any exterior
reserve remain additional in both expressions. For an entirely idle sequence,
no bank is needed; the supplied-bank theorem above assumes an active row.

Every tape instruction is preserved, so the predecessor's active-row time
allowance and source-update charges still apply. The bank is supplied already
blank and counted at its complete capacity. This is not a free dirty-allocation
or erasure algorithm. Fixed ownership control adds no tape actions. A full
binary transition compiler and its representation overhead remain unprovided.

## Executed evidence and limits

The main fixture is the two-target complete level with moduli (5,7,3,2),
widths (3,3,2,2), initial state (3,2,1,1), precision 11 and H=2. It executes
ten rows, six active rows and twelve physical producer calls. Each active bank
has 3,084 cells. Exact physical-identity accounting gives 8,894 retained work
cells; replacing the one bank by six distinct equal banks gives 24,314 cells.
The reduction is 5 times 3,084, or 15,420 cells. Both counts retain every
numerical query object and every other allocated work backing.

The mixed-height control uses right widths (3,2) and two consecutive row-one
queries. Each query executes the long target and then the short target on the
same bank. The second query reuses the identical backing. It checks complete
source round-trip, all protected inputs, ownership, fixed capacities, all
numerical and joined retirement, and every historical blank suffix. Five
negative controls reject overlapping ownership, the wrong release object, a
nonblank arena-tail cell, a changed extent and a mismatched source seam.
RESULT.json is generated from these executions and binds the implementation
and input manifest by SHA256. It is not a handwritten receipt.

This is a source-bound scoped construction and composition proof, supported by
finite execution. Initial clean supply, arbitrary dirty acquisition, shared
numerical banks, changing precision, whole-tree and exceptional-key execution,
binary lowering, full supplier admission and the five selected framework
assumptions remain separate. No new multiplication theorem or kappa is claimed.
No independent human or proof-kernel acceptance is claimed.

## Implementation constraints

All new functions are below 60 physical lines. New loops use the fixed 52-role
inventory, the five source substitutions, the bounded source manifest, or the
fixed 10-row/2-row fixtures. Source pins are checked before loading executable
premises. Failures propagate as ValueError; there is no recovery guarantee
for malformed production executions.

Power-of-Ten rule 3 deviation: Python allocates managed objects while the
verifier runs. Physical bank capacity is fixed before execution at B(P,H), and
all other retained backing is enumerated by identity. The bounded fixture and
fixed role table bound live data; Python interpreter memory is outside the
finite-symbol cell claim. Follow-up is an explicit binary implementation before
using this result as a binary-space theorem.

Power-of-Ten rules 8 and 9 deviation: the source-bound adapter compiles a
changed query module using the predecessor's module loader. There is no runtime
input interpolation. Only five fixed substitutions of SHA256-authenticated
source are allowed, each with exactly one occurrence. Source drift rejects.
The exact transformed source remains inspectable through `adapt_source`.
A future upstream constructor parameter could remove this scoped compilation;
predecessor code is immutable in this contribution.

Diagnostics use Python warnings as errors in normal and optimized runs. The
registered source metadata, committed-byte and source-history checks remain
separate from the mathematical theorem premises. No repository-wide code
cleanup or predecessor replay is part of this contribution.

## Related prior numerical owner

JoyboyBrian's PR #5505 constructs reuse of the separate 63-role numerical
owner, including changing precision and paid marker reinstatement. It leaves
complete physical ROM/level integration open. This construction changes the
52-role ROM bank across paid source-update rows and does not compose that
numerical owner. The two results concern different role inventories and
lifecycle seams; no numerical reuse is claimed here.

## Credit

This contribution was produced by Nick Petalas. Credit Ali Romman, commdata2338,
JoyboyBrian, ToikY, Hiroki KUMAZAKI, Cinna Davis and all source notices and
retained predecessors as linked in PR #5625 and PR #5519. The bank formula,
rolewise maximum principle and original caller theorems are not claimed as new.
Apache-2.0.
