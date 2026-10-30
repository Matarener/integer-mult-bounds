# A matched full-chart optimization of P104 joint compensation

Completing the persistent Y bank once, doing all three scalar layers in a
common full chart, and restoring its terminal chart reduces PR3978's prepared-
cut positive-child bill from **32448 to 21632**, while eliminating all private
copies and temporary arrays. Both words implement the exact same physical
operator with the same original input tags and arbitrary dirty helpers.
The new word adds 21632 restoring doubles, with the same 1049152 unit array additions.
This is a reduction in native child count and private storage; scalar work
remains paid.

The identity is D_K C D_T=Cphys, where D_T=diag(I,T), D_K=diag(I,T^-1) and
C=U(A_r-I)S(I)U(A_c-I). See [PROOF.md](PROOF.md) for chronological charts,
phase-exact retained native-child recipes, restricted scope, full primitive
invoice and conditional gate. [RESULT.json](RESULT.json) records the checks.
This combines global chart completion with elementary operator factorization.

The improvement is local to the **same explicitly prepared physical cut** as
[PR3978](https://github.com/CrocSwap/integer-mult-bounds/pull/3978), exact head
48e2e44d8785be8204d8c4b719850332f4f9abe0. Its unchanged proof/result are exported
with hashes/Git blobs. No actual chronological P104 producer, opposite native
orientation or global interstage alignment is supplied. Under the inherited
named complete invoice, the excess decreases from 33280 to 22464 and still fails.
No native optimum, runtime gain, supplier or new kappa is claimed.

## Reproduce and verification scope

Standard-library Python 3.12:

    python3.12 -B scripts/research_package.py --package research/p104-full-chart-joint
    python3.12 -B scripts/check_research_commit.py --package research/p104-full-chart-joint --check-source-history

VERIFY.json declares bounded checks. The primary validates exact ordered
noncommutative identities, original physical input tags, all 208 local donor
columns, canonical 104 physical labels and 10816 tensor lines, and both
rank-one boundary recipes on 876096 binary basis vectors. The separate checker
compares 32 Gaussian columns and 8 arbitrary dirty columns, executes the literal
in-place scalar word, compares 56 finite native columns and rejects physical
order, donor-restoration and phase faults. Finite f=1 formulas are only checks;
the general-f implementation retains one C_f child, not an exponential scalar
expansion. Signed-floor and recursive admission remain separate obligations.
Actual normal/optimized CLI controls validate private fixtures before rejecting
receipt/source/predecessor mutations. These are scoped checks, not human or
proof-assistant certification.

## Selection and overlap

User-assigned changed scope under revision 6 `p104-side-correction`, base
20ecf2891d80b5acf18d980b2164fb44ea7faa90. The coordinator refreshed 702 open PR
bodies including drafts, live handoffs and canonical main at the new round;
worker checked the current source/head and repository helper. Canonical claim:
https://github.com/CrocSwap/integer-mult-bounds/pull/3954#issuecomment-6263112891
Discussion/closed-diff coverage is bounded. The raw-full caller, source-tag and
other parallel studies are distinct. No frozen predecessor or frontier file
is modified.

## Open next questions

TASK.json asks whether one actual producer/consumer boundary can absorb a
conversion without changing original physical source identity, helper returns
or the complete gate. First bind named owners and exact entrance/exit charts.
Remaining blockers include the missing prepared producer, interstage alignment,
native orientation/phase, physical scalar/routing/control/tape costs and
finite-width/precision/recovery/all-size admission. Stop expansion under the
unchanged failed gate; a common full chart alone does not erase source tags.

## Credit

Chris R/Clear1nsight owns PR3978's original compensator and copied route, following
PR3954/3940/3882/3943. Retain Rohan Arun/#1972, Chafik Boukhalfa/#1991,
Adam Gall/#1940,1337isnot1337/#3894, ToikY/#3956/#3966/#3996, and 3961/3962/3965
for their distinct boundary, coverage and copy audits. Retain Josie Elliston,
Sagar Thakrar, Douglas Colkitt, Dominik Scholz and the canonical E8/native/
Clifford/compiler/caller source lineage. New matched optimization prepared for
Chris R/Clear1nsight with substantial OpenAI Codex multi-agent assistance.
Apache-2.0. Selected frontier unchanged.
