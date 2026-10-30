# First profitable target rank with one paid unit per piece

This contribution is produced by Nick Petalas. Claim type: **scoped proof with
exact finite corroboration**. It does not improve kappa or change the selected
frontier. New material is Apache-2.0.

At power exponent `99/100`, replacing one rank-R productive target by a proper
positive integer partition, while adding one paid rank-one recursive child for
each resulting target, can improve the complete signed bill **exactly when
R>=288**. The first witness is `288=96+96+96`.

```text
profit = sum_i r_i^(99/100) - R^(99/100) - number_of_pieces
R <= 287: every proper partition has profit < -0.004077
R  = 288: (96,96,96) has 0.006289 < profit < 0.006290
```

[PROOF.md](PROOF.md) reduces the all-partition lower bound to 286 explicit
Jensen inequalities at rank 287. Integer-root enclosures certify each one and
the positive witness. Balancing and strictly decreasing power increments extend
the witness to all larger ranks. The proof has no piece-count or menu limit.

This specializes Ali Romman's [PR #5769](https://github.com/CrocSwap/integer-mult-bounds/pull/5769)
complete fee-charged target-partition contract. That finite optimizer caps the
replaced rank at 256. The present unit-fee model has no profitable rank inside
that cap at this exponent; the first opportunity is 288. This is a new arithmetic
screen, rather than a replay or audit of the optimizer. The result tells a
contributor using this fee model to seek lower or shared fees before searching
small target partitions. It grants independent targets and adds no other fees,
so extra nonnegative costs can only strengthen the rejection below 288.

## Reproduce

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/unit-fee-target-threshold
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/unit-fee-target-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/unit-fee-target-threshold/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/unit-fee-target-threshold --check-source-history
```

Another CPython 3.12 interpreter can replace the absolute path. Expected marker
in the JSON stdout receipt: `PASS_UNIT_FEE_TARGET_THRESHOLD`. The receipt
contains all 286 dyadic rejection bounds, the witness bounds, finite coverage
counts and SHA256 of every package file. Redirect stdout outside the checkout
if retaining it. `verify.py --check-receipt PATH` recomputes the result and checks
both the supplied receipt and the current source hashes. Replay writes no files.

## Scope and limitations

The exponent is fixed at 99/100, a one-percent raw power-saving screen. It is
not the selected supplier exponent or the nine-row outer budget. One recursive
rank-one child per resulting piece is an explicit additional-fee hypothesis;
ordinary scalar ADD charges and shared fees are different models. The result
does not exclude no-fee target refinements, including selected #5599, or any
construction with paid removals, other productive credits or changed boundaries.

Independent useful targets, native/source maps, chronological delivery, dirty
restoration, owned lifetimes, complete compiler/precision/tape/outer admission
and the full multiplication theorem are unproved here. No predecessor verifier,
selected cold replay, Lean proof or physical supplier was run. Independent human
and formal proof-kernel review are unclaimed. The five selected framework
assumptions remain.

## Open next questions

- At the actual source-bound supplier exponent, what is the first profitable
  rank under the same fee? Start with balanced partitions and certify the two
  adjacent rank signs. This would tailor the screen to a real caller; the
  correct tariff and exponent must first be pinned.
- Can a real helper split share one paid route across its targets, rather than
  paying one child per piece? Start with one literal helper/cut and derive its
  complete invoice. Independent target realization and dirty restoration are
  the blockers; this arithmetic theorem supplies neither.

## Credit and provenance

Credit Ali Romman #5769, head `a869fed1b3ab00ffcddd3791c579c408594325f8`,
for the fee-charged partition definition, original-target debit and finite
optimizer. Credit classical concavity, Jensen and integer balancing, and the
signed-invoice framework, mightyOil's T16 audit and their retained predecessors.
[SOURCES.json](SOURCES.json) records exact reference-document bytes and the
base catalogue/selected-record pins. The source document is reference-only;
this self-contained theorem has no unmerged runtime or Git-object dependency.

Related work includes Charan . #5702's thirteen fixed H9 helpers funding one
shared extra child, Arham Tahir #1605 and Aaron Wang #3110's paid-child reblocking
contracts, and Ali Romman #5341's paid-increment fragmentation. Those models and
quantities differ; their reported numbers are not replayed as this deliverable.
The account's #5901 concerns incomparable invoice pools, rather than existence
of an improving unit-fee partition. It supplies no premise used here.
