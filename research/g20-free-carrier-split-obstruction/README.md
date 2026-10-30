# G20 split obstruction with a free choice of physical carrier

On the fixed final G20 word of Ali Romman's [PR5708](https://github.com/CrocSwap/integer-mult-bounds/pull/5708),
allowing a cut carrier outside the helper endpoint group exposes no additional
independent split. All **1,981 newly admitted contexts have zero boundary
pairing**. This answers the common-frame part of the different-physical-role
question in [PR5679](https://github.com/CrocSwap/integer-mult-bounds/pull/5679),
Open next question 1. Paid changes of frame and changed words remain open.

Claim type: finite exact certificate with a scoped algebraic proof. No new
kappa, supplier admission or complete multiplication theorem is claimed.
This contribution was produced by Nick Petalas.

The prior census required an actual helper-group role in the cut bank.
The new test uses the entire common-frame bank and every helper-only prefix
functional and suffix direction, even when the bank contains no such helper.
Among the 1,981 added contexts, 46 have both kernels nonzero and 45 have a
nonzero internal pairing. All still have zero boundary pairing. A change of
carrier alone cannot make the boundary outputs independent.

## Evidence and reproduction

The standalone verifier imports no predecessor executable. It authenticates
the exact source word and frames, covers 14,795 event cuts on 685 fields,
and deduplicates 7,870 exact group/frame linear-algebra contexts. All boundary
pairing matrices are zero. The retained endpoint groups have sizes 413, 1
and 1. There are 645 rational frame classes.

Every kernel has equation, independence and opposite-pivot rank-completeness
checks. The 516 controls include exhaustive dependency spaces for 512 small
inputs and a positive split with no helper role in the cut bank. The result
and controls pass under normal and optimized Python.

From the repository root, the local interpreter path is:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/g20-free-carrier-split-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/g20-free-carrier-split-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/g20-free-carrier-split-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/g20-free-carrier-split-obstruction --check-source-history
```

Any CPython 3.12 interpreter can replace that path. Only the standard library
is needed. Expected scientific marker:
`PASS_G20_FREE_CARRIER_SPLIT_OBSTRUCTION`. The context-summary digest is
`ba0e0a6915ab530a5f4f31c8ddcf54055325aaa1521bc7057b776f92d085b276`.
The proof and coverage argument are in [PROOF.md](PROOF.md).

## Limits and predecessor credit

The result concerns one unchanged normalized scalar word, the existing
common-frame banks, individual helper endpoint groups and ordinary binary
boundary bases. Its zero matrix also excludes scalar extensions in
characteristic two. Mixed-frame bases, different endpoint groups, added
contacts, address-dependent recoding and a changed word are not excluded.
No native/operator admission, complete caller or recursive price is replayed.
Independent human and formal proof-kernel review are unclaimed.

Credit Ali Romman for PR5679's split construction and explicit open question,
PR5708's changed word and prior helper-pivot census, and PR5609's cut method
on the older word. Those results are cited and used as specifications, not
audited as the deliverable. The new step is the expanded carrier domain and
its exact boundary obstruction on the final word. Retain the source credit
to Dugongue, ai-nanachi, compact436 and all native, controller, helper,
ordinary and stock predecessors named in those packages. New material is
Apache-2.0.

## Open next questions

- Can a paid multi-frame boundary give one nonzero eligible boundary pairing
  on this exact word? Start with one frame conversion and its inverse, then
  account for the changed query ranks, public targets, routes and restoration.
  Neither such a channel nor a favorable complete bill is supplied here.
- Can one changed contact make a nonzero boundary pairing in one of the 46
  new contexts with nonzero kernels? First inspect the exact prefix/suffix
  supports at those cuts, then prove the changed endpoint and price it. A
  different carrier within the unchanged bank cannot suffice.

The first steps and blockers are recorded in [TASK.json](TASK.json).

## Verification design

All loops have finite source-size bounds. The verifier limits inputs to
16 MiB, fields to 700, events to 20,000, frame dimension to eight, frame
records to 2,000 and distinct contexts to 30,000. It writes no files and
has no recursion, subprocesses, dynamic imports or generated code. Each
function is below 60 lines. Explicit invariant checks remain active with
`-O`. Registered replay uses isolated mode and warnings as errors.

Python allocates integers, rational values and collections during execution,
so fixed steady-state allocation is a managed-runtime deviation from Power
of Ten rule 3. The source limits, finite elimination widths and context cap
bound the live collections. This command is a bounded research check, not a
long-lived service; a fixed-storage implementation would be a separate
requirement if larger instances are introduced. Interpreter and standard
library internal allocation are not instrumented. The scientific result
is independent of a memory-performance claim.
