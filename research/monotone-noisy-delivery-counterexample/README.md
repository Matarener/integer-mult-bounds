# A 119-versus-120 monotone delivery counterexample

This contribution was produced by Nick Petalas. Apache-2.0.

**Claim type: finite certificate in the fixed immutable-channel scalar
quotient.** An explicit 22-channel witness has delivery profile

    H0 + 14 H7 + 7 H8.

It realizes the complete eight-mode response in the retained PR5745 quotient.
The nondecreasing tariff H0=0, H1=...=H7=1, H8=H9=15 gives cost **119**
against the eight-call comparator **120**. Thus the quotient's 8H8 floor
cannot extend to arbitrary finite channel counts under every positive
nondecreasing tariff. No optimal channel count or new kappa is claimed.

The new identity combines fourteen grade-seven frames and one ground frame
into mode (0,0,0,0,1,1,1,1). Seven cited clean grade-eight directions complete
the other modes with immutable payloads. [WITNESS.json](WITNESS.json) gives
all 69 contacts and coefficients; [PROOF.md](PROOF.md) gives the contract,
linear identity and exact assembly. [RESULT.json](RESULT.json) is generated
by the verifier and bound to the source, witness and verifier hashes.

## Scope and predecessor credit

Nicholas Stone's [PR5845](https://github.com/CrocSwap/integer-mult-bounds/pull/5845)
at `7b8ed4b168890d90e100e75a4062174a145be246` poses the continuation to
three-frame sums and ten or more channels under arbitrary monotone tariffs.
The initially proposed three-frame question remains open here. This first
positive witness uses 22 channels; its channel count is not optimized.

Ali Romman's [PR5745](https://github.com/CrocSwap/integer-mult-bounds/pull/5745)
at `e82b64e91e57c838ff2028bcf2219203966bf9ed` supplies the canonical
delivery model and clean grade-eight directions. Its retained temporal
response code was used for discovery. Verification uses a separate forward
impulse implementation and imports no predecessor executable. The predecessor
obstruction censuses are not replayed or submitted as this contribution.

The certificate is compatible with PR5845's at-most-nine-channel theorem and
Ali Romman's [PR5823](https://github.com/CrocSwap/integer-mult-bounds/pull/5823)
arbitrary-channel concave-power floor. Its tariff is outside that power class.
Also retain [PR5808](https://github.com/CrocSwap/integer-mult-bounds/pull/5808),
flyingviper's PR5720/PR5755, Cao Yifan, Cinna Davis, Dugongue and every source
contributor credited in the unchanged archive. Full attribution and the
distinction between these results are in PROOF.md.

## Reproduction

From the repository root, using CPython 3.12 and the standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -B research/monotone-noisy-delivery-counterexample/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -W error -O -B research/monotone-noisy-delivery-counterexample/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/monotone-noisy-delivery-counterexample
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/monotone-noisy-delivery-counterexample --check-source-history
```

An equivalent CPython 3.12 path works on another machine. In a sparse checkout,
first materialize `research/filtered-native-kappa004/inputs`, the sole live
input, with `git sparse-checkout add research/filtered-native-kappa004/inputs`.
The archive already belongs to main; no pending predecessor commit is needed
for replay. SOURCES.json pins its exact bytes and the revision-8 baseline.

Expected output starts `PASS_MONOTONE_NOISY_DELIVERY` and reports 22 channels,
69 contacts, all 22,585 source events, 2,192 retained mode equalities, eight
rejection controls, charge 119 and comparator 120. Both registered commands
run the same full scientific check, normally and with assertions disabled.
Their local timings and interpreter environment accompany the PR evidence;
the generated receipt records the actual environment used to create it.

## Limitations

This is a positive witness in a necessary scalar quotient. A full native
operator identity and a physical restoration circuit are not supplied.
Of 358 ground helpers exempted by the cited model, 113 have a nonzero residual
after the displayed payload substitution. The certificate restores all 112 Y
responses and all 50 non-ground-helper responses, and all nine C-slot impulse
responses vanish, including the eight owned slots. It does not restore the
113 exempt residuals physically. Delivery prices alone exclude payload
preparation, scatter arithmetic, channel ownership/return, precision, stock,
tape movement and the complete supplier/caller invoice. No selected frontier
or inherited framework assumption changes.

The verifier uses direct forward evaluation of the word and has no recursive
or unbounded search. Its memory policy has a managed-runtime deviation:
Python/Fraction allocates during replay. Live scalar state is bounded by
641 rows times 22 channel coefficients, with eight payload coordinates and
69 contacts; controls run sequentially. Source bytes are hash-fixed. The
compensating check is the complete normal/optimized replay. A future change
to dimensions or streaming behavior must revisit these bounds. Warning-strict
Python and the repository metadata/source checks provide the available
diagnostics; no repository-wide configuration changes are made.

Independent human and formal proof-kernel review are unclaimed.

## Open next questions

1. Do three, or any fewer than fifteen, low-grade frames have a nonzero clean
   response in this exact quotient? Start with a triple-span search that retains
   literal contacts. No exhaustive triple computation or minimum-channel proof
   is supplied here.
2. Can this joint response lift to exact native operators and physically
   compensate the 113 exempt helper residuals? Start with the full native action
   for the fourteen named grade-seven charts and price the resulting cleanup.
   Scalar fixed-vector responses do not imply operator equality or a favorable
   complete bill.

The relevance, first steps and blockers are also in [TASK.json](TASK.json).
