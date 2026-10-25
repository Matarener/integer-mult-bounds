# Independent terminal-to-owner cost bridge for PR3945

This independently corroborates the finite cost bridge in Dugongue's
[PR3945](https://github.com/CrocSwap/integer-mult-bounds/pull/3945) at
`91f81d131252db704f945891da1ea54e29d46b8b`. No discrepancy was found in the
specified domain. Both final providers freshly yield
`2482 H1 + 712 H2 + 218 H3 + 109 H4 + 20 H5 + 8 H8`. The 26 terminal extensions
add exactly one dimension each. Across the actual T360 schedule, every one of
84,240 affected rank-32 bins changes from `4+9+9+9+1 idle` to `5+9+9+9`.

The complete independently reconstructed difference is
`51840 H1 - 42120 H2 - 19440 H3 + 22680 H4`, with rank mass zero. The resulting
profile is `{1:8041680,2:2306880,3:729648,4:353160,5:69120,8:25920,48:137952}`.
These are the predecessor's claimed values, now checked through a separately
implemented bridge. This package contributes independent evidence and a reusable
checker, not a new construction, root, or selected frontier.

## What was checked independently

The checker imports no predecessor executable code. It enumerates all points
of each binary subspace, measures dimensions by cardinality, and tests native
binary transport on explicit 512-point permutations. It derives the local
invoice directly from the words and never reads their `report` histogram.

It compares the exact old/new interleaved free programs, keeping native events
at their actual scalar cuts and deleting only identity scales. The initial
contract, corrections, cuts and all other caller fields also agree. This proves
relative equality of the abstract scalar/permutation operators for every dirty
input and private-buffer state. It does **not** replay native Gaussian/Clifford
phase recipes or independently establish predecessor validity. Native phase
admission remains a separate obligation.

The full external-input run checks every one of 1,321,920 old/new helper roles,
6,480 source windows and 725,760 physical bins. Reverse event queries derive
source windows; coordinate bitmaps certify disjoint placement, chronological
coordinate order, compact occupancy and exact idle remainders. The audit checks
same-call physical family distinctness and disjoint windows of reused families.
It preserves every time/helper/owner/child/port identity, derives every helper
width from the actual terminal and entrance subspaces, and combines the new
local invoice with the actual call dispatch and idle bill. This connects the
changed local word to the literal schedule rather than accepting a matching
aggregate profile.

`RESULT.json` contains the full source-bound receipt. `LOCAL-RESULT.json` records
the default local replay separately. `LEDGER.json` records every covered cost
category and explicitly marks unresolved costs. `PROOF.md` explains the audited implication. `VALIDATION.json` records exact
commands, environment and replay timing. The free-operator check is structural
and universal within its abstract semantics; there is no sampled dirty-vector
claim and no physical phase equivalence claim.

## Reproduce

Python 3.12 or later, standard library only. The ordinary registered replay uses
four byte-exact frozen words (about 294 KB) and freshly checks both local invoices,
relative free operators and 11 rejection controls:

```sh
python3 -B research/staged544-terminal-owner-bridge-audit/verify.py
python3 -O -B research/staged544-terminal-owner-bridge-audit/verify.py
```

It prints `PASS_LOCAL_BRIDGE_ONLY`; the literal owner audit is explicitly
`NOT RUN`. A default CI pass is therefore not a fresh full-owner replay.

The full owner inputs are an intentional external dependency, avoiding another
13 MB copy of the two literal fills. `EXTERNAL-SOURCES.json` pins each of the 12
public inputs by repository, immutable commit, exact path, byte size and SHA256.
Download into a nonexistent directory, then run the full audit:

```sh
python3 -B research/staged544-terminal-owner-bridge-audit/fetch_sources.py --output-dir /tmp/pr3945-owner-inputs
python3 -B research/staged544-terminal-owner-bridge-audit/verify.py --source-root /tmp/pr3945-owner-inputs
python3 -O -B research/staged544-terminal-owner-bridge-audit/verify.py --source-root /tmp/pr3945-owner-inputs
```

The downloader's PASS certifies only acquisition. It refuses an existing output
directory and verifies all bytes before writing its completion receipt. The full
checker rechecks every immutable input before doing mathematics. It reads inputs
without changing them; `--output /new/path.json` optionally writes a new result
and refuses to replace an existing file. An unavailable remote source remains
an unavailable full replay, never a controls-only substitute.

The full run additionally rejects six mutations through the actual owner audit:
changed owner identity, a family collision despite matching old/new identities,
a closed source window, a shifted coordinate interval, missing dispatch, and a
local-to-complete invoice mismatch. Rejection reasons are checked. All mutations
are in-memory; frozen inputs are preserved.

## Scope and source impact

This is a refined `independent-moment` audit at main
`20ecf2891d80b5acf18d980b2164fb44ea7faa90`, priority revision 6. The audited PR3945
head was checked live; the repository's default catalogue and selected record
are pinned as provenance in `SOURCES.json`. The predecessor snapshot is an
external exact-byte input, not an asserted ancestor of this PR. The new package
changes no predecessor, release engine, source archive or selected record.

Overlap was checked against the live PR3945 discussion and the shared batch's
662 open-PR bodies (complete PR pagination at 06:59 UTC on 2026-10-19), plus bounded
rendered discussion access. The active independent-audit claim is
[on PR3945](https://github.com/CrocSwap/integer-mult-bounds/pull/3945#issuecomment-6261600388).
This is intentional independent verification of that author's construction;
PR3941/3942/3957 concern fixed-exit retiming and do not admit this changed terminal
inventory. The newer PR3955/3958/3959 claims use changed hypotheses/compositions
and do not replace this precise bridge check. No exhaustive novelty claim is made.

No new root isolation, complete ordinary/outer release, physical native phase,
uniform all-size compiler, source/hosting implementation, precision/stock/tape/
recovery coefficients, analytic or BIT hypotheses were checked. Unknown costs
are not zero. The complete finite paid histogram is corroborated; complete
supplier admission and a multiplication theorem are not established here.

## Open next questions

The next discriminating audit is the changed native phase/interface admission:
pin the exact changed native input, compare its entrance/exit phase obligations
and all-column recipes, and trace its receipt into the source-bound outer release.
Start with one changed terminal's literal native recipe and the corresponding
owner role. This matters because abstract binary permutation equality does not
itself establish physical Gaussian/Clifford implementation. The full inherited
native source closure and uniform model premises remain dependencies. Extending
the terminal search is not justified merely by this bridge's corroboration.

## Credit

Chris R / Clear1nsight, with substantial OpenAI Codex assistance. Apache-2.0.
The construction, promoted terminal identities and original full invoice belong
to Dugongue / PR3945. Preserve dataisfire PR3734; zxv PR3682; Ross Richardson
PR3605; Erwan Secousses / ChaloupeMusic PR3815 and retained PR3638; hexapode
PR3802/3875; Sagar Thakrar PR3687; roger-sato PR3693 and Arham Tahir's underlying
audit. The scalar/native source lineage includes Jeremy Kothe, Lyy-iiis,
philippeVV and the other contributors in the retained `NOTICE-PR3945.md` and
`SOURCE-CREDITS.md`. Their exact notices accompany the four frozen data inputs.
