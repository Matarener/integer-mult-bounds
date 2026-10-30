# Validation and bounded implementation

The universal result is the proof in PROOF.md. The finite checks establish the
literal geometry and exercise the argument; they do not quantify over all fields
or all finite lists. No independent human or proof-kernel review is claimed.

## Checks

The primary validates the selected labels' SHA256 and Git blob, the retained
PR3370 certificate's hashes, the sixteen-group partition and every orthonormal
entry. It covers all 496 pairs and 80,240 reader-support subsets contained in
the two target halves. It verifies both C>=d_A and C>=d_B, and records the
complete histogram of 2C-d_A-d_B. Extra reader coordinates can only increase
rank, so the written proof covers readers outside these finite subsets.

Ninety-six rational realizations use 2,4,7 dense directions. Their 21,504 exact
coefficient checks cover all 112 rows in the independent two-indicator basis,
which is equivalent to checking all matrix entries. Four- and seven-query
fixtures include nonzero readers outside the target with total zero delivery.
Sixteen same-group two-query examples attain the bound. A separate control
splits one direction into proportional repeated queries. The fixture receipt
retains both the removed pair bill and the stronger dense-query lower bound.

The separate implementation imports no primary algebra. It uses explicit
nine-coordinate dot products and dense elimination on transposed matrices,
recomputes every support-subset histogram bin, and checks 118,285 coefficient
tuples over F2,F3,F5,F7, including 4,854 coordinate-axis deliveries. It calculates
a literal one-plane reader cost 2 and source self-cost 8, illustrating the exact
difference from PR3383's tariff. That term alone realizes no target operator.

Five behavioral groups check the forbidden axis boundary, damaged target
identity, damaged outside cancellation, rank bounds, repeated directions,
same-group attainment, and four actual optimized CLI corruptions. The CLI
controls alter the live bytes, retained bytes, expected receipt and a repinned
invalid partition. Each fails with its stated reason. Test copies use copyfile,
so read-only source modes do not propagate to private test copies. No source
file, symlink or shared interpreter mode is changed.

Local verification uses registered CPython 3.12.15 and optimized CPython 3.15.0
with warnings as errors. Ruff 0.17.1 checks E,F,B,UP,SIM,C4,PIE,RSE,RUF, with
formatting checks. Publication additionally compares the exact committed
package/input bytes and declared source history, then replays the committed
Git-free export. The final PR/report records performed results. Hosted CI,
Lean, Docker, the selected full cold replay and all historical suites are not
claimed as local checks for this isolated theorem package.

## Code bounds and deviations

All retained code is confined to this package. Source JSON reads are capped at
1 MiB; metadata at 32 KiB and the receipt at 64 KiB. Groups have sizes 4,6,8, giving
32 indicators, 496 pairs and at most 256 subsets per pair. A pair has at most 8
target ports. Full source/reader lists contain at most 112 ports. Binary rank
uses at most 112-by-112 bits in the primary and 16-by-16 entries in the separate
census. Rational fixture query counts are 2,4,7, with a checked maximum 16 at
the internal fixture boundary. Finite-field enumeration has at most 7^6 tuples.
Every loop follows one of these finite bounds, and all functions stay below
60 physical lines. File handles and temporary directories use context managers;
subprocesses have 60-second or registered 120-second timeouts. Failures propagate
as exceptions or nonzero process results. Checks remain active under `-O`.
No recursive calls, dynamic code generation or background processes are used.

Power-of-Ten rule 3 deviation: CPython allocates integers, fractions, JSON and
containers during operation. The limits above bound live data; the census
retains only a small histogram, and the 96 fixtures form a bounded receipt.
The standard runtime's internal allocations are not instrumented. Follow-up
would require a different runtime if fixed-capacity execution becomes a claim.

Rules 8 and 9 deviation: the control suite loads exactly the sibling verify.py
using importlib, and unittest dispatches exactly the five declared tests.
This provides direct behavioral boundary checks without widening the production
CLI. The source target is fixed, not user-selected; the call graph is finite.
Follow-up is an explicit importable package if these routines gain consumers.
The independent checker has no such import.

Rule 10 scope: the cited Python warning and Ruff configurations were run. No
compiled implementation or separately configured static type checker is added;
the interpreter and third-party runtime internals are outside this package's
analysis. No diagnostic suppression was introduced. The package manifest
reruns all three scripts with warnings as errors in its registered environment.

Build the Lever shaped the retained deterministic support census and replay.
Prove It Works shaped the source authentication, actual-reader prices, corrupt
CLI checks and committed-source export replay. Separate Before Serializing
Shared State shaped the isolated package/output paths and advisory locks on
worker ownership and shared Git/reservation mutations.
