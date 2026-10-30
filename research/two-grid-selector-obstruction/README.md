# A sharp obstruction for every two-grid precision selector

For a two-grid update with coarse-input admission q in hZ, an injective
selector can use coarse precision anywhere **if and only if h divides the
difference of the two increments**. This holds for arbitrary selector sets,
including nonperiodic and noncomputable choices. It is a scoped mathematical
proof with exact finite corroboration, not a new kappa or supplier.

Let coarse and fine increments be a and b in fine-grid units, delta=a-b,
and S contained in hZ be the inputs selected for coarse execution. Then

```text
F(q) = q+b+delta*1_S(q)
injective  iff S+delta is contained in S
surjective iff S is contained in S+delta
bijective  iff S+delta=S
```

If h does not divide delta, every coarse choice q has an explicit collision
partner q+delta, which is ineligible for coarse. If h divides delta, choosing
coarse on hZ and fine elsewhere is a bijection. [PROOF.md](PROOF.md) gives
the complete argument and a nonperiodic injective, nonsurjective example.

## What this adds

woklerx's [PR #1845](https://github.com/CrocSwap/integer-mult-bounds/pull/1845)
proves that one coarsest-compatible policy loses information on a named PR628
leaf. It also classifies periodic residue-translation policies. Its open
question asks whether useful target-adaptive precision can retain injectivity
without a branch transcript.

Here **every** selector using only those two precisions is excluded from
making any coarse choice on the same whole source-one, zero-imaginary-target
slice. The cited coarse and fine increments are -10/32 and -11/32, with
coarse admission q even for target q/32. Thus h=2 and delta=1, and the
collision partner is always q+1. The new proof assumes the predecessor's
admission, increment and restoration statements. It neither imports nor
replays the predecessor implementation.

The scope change from `uniform-transfer-audit` is explicit in [TASK.json](TASK.json).
An adaptive precision compiler needs injectivity before its saved precision
can enter a complete caller. This theorem resolves one narrow obstruction;
it does not construct or price that compiler. The
[advance claim](https://github.com/CrocSwap/integer-mult-bounds/discussions/1166#discussioncomment-19227538)
records the same scope.

## Evidence and reproduction

The standard-library verifier independently enumerates literal output images
and compares their multiplicities with the new set-inclusion criterion.
Periodic cases use every admission-respecting subset for h=2 through 8,
period h*k with k=1 through 6, and delta=-2h through 2h. Finite-support
cases use every subset of hZ intersected with [-6,6] for h=2 through 6,
and delta=-6 through 6. Their integer images include every possible
cross-branch collision partner, so these cases do not assume wraparound.
An additional application check constructs explicit witnesses using the
cited increments; it is not a leaf replay.

Normal and optimized local checks agree on 18,522 periodic parameter-policy
fixtures and 543,774 literal residue images, including 13,440 admission
obstructions. They also agree on 2,392 finite-support fixtures and 46,552
literal integer images, plus 1,025 cited-premise collision witnesses and ten
controls. Each direct command took about 0.07 seconds locally; this timing
only records that the registered timeout is ample, not a speedup claim.

Semantic controls distinguish inclusion from equality and its reverse,
show attainment for divisible increments and the need for admission,
and cover zero and negative differences. Invalid replay parameters reject.
Every run emits its computed counts and a receipt bound to SHA256 hashes
of all six package files. No receipt is handwritten or stored in the package.

From the repository root, using CPython 3.12.15 locally:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/two-grid-selector-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -O -W error -B research/two-grid-selector-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/two-grid-selector-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/two-grid-selector-obstruction --check-source-history
```

Another CPython 3.12 interpreter may replace that absolute path. The expected
scientific marker is `PASS_TWO_GRID_SELECTOR_OBSTRUCTION`. Both registered
commands have a 60-second timeout and write no files. Exact provenance pins
are in [SOURCES.json](SOURCES.json); there are no external executable inputs.

## Limits and verification discipline

The universal theorem rests on the written proof. Finite enumeration
corroborates it. The leaf application is conditional on PR1845's stated
source slice and does not independently validate it. A policy may choose
fine precision everywhere on that slice and use coarse elsewhere.
Larger precision menus, different increments, stored branch information,
different sources, restricted reachable domains and auxiliary outputs can
escape this two-branch model. Clipping and saturation are not covered.
No selected frontier, physical native operation, complete invoice or
multiplication theorem is changed. Independent human and formal proof-kernel
review, the selected cold replay, Lean and Docker are unrun.

The code has no recursion, subprocesses, dynamic evaluation or persistent
state. Loops have fixed bounds in the listed domains. One periodic case
stores at most 48 image residues; one finite-support case evaluates at most
25 integers. File hashing is bounded to six files of at most 1 MiB each.
Functions stay below 60 lines. Explicit checks remain enabled under -O.
Python allocates exact integers and collections during this bounded offline
replay, a documented memory-allocation deviation from allocation-free execution.
Warning-strict normal and optimized checks are registered.

## Open next questions

- Can three or more actual admitted precisions avoid the forced collision?
  First obtain the additional increment and admission lattice and test disjoint
  translated branch images. Their physical selection/restoration bill remains
  unknown.
- Does a useful actual caller reach a restricted target set excluding every
  forced partner? First pin one call site and prove its source-conditioned
  reachable set. Reachability and its maintenance costs are the blockers.

These are structured in [TASK.json](TASK.json). This package reserves neither
follow-up and starts no further construction campaign.

## Credit

This contribution was produced by Nick Petalas. Credit woklerx for PR1845's
question, admitted increments, residue-translation theorem and PR1451's prior
mixed-precision inverse boundary; Chafik Boukhalfa for the PR628 leaf;
Gareth Davidson for its retained fixed-grid caller and proof; and Ali Romman's
PR621 and the retained kernel lineage. Elementary translation and partition
facts are background mathematics. The new claim is the arbitrary-selector
classification with admission and its conditional all-policy exclusion on
the named slice. New work is Apache-2.0.
