# Mixed 5,6,6 shortening fails at common cut 36

An explicit 36-coordinate common cut and three residual P112 vectors of
binary support ranks exactly 5,6,6 have code intersection dimension exactly
two over every characteristic-zero field. This answers PR3368's next-cut
question with a literal coefficient-realizable counterexample. Combined
with its conditional cut-35 theorem, the sufficient threshold 35 is optimal
under the predecessor's inherited premises.

[PROOF.md](PROOF.md) gives the construction and field transfer.
[WITNESS.json](WITNESS.json) contains all supports, values, coefficient
columns and the single cut. [RESULT.json](RESULT.json) records the exact
ranks 8,3,9 and intersection dimension 2. The new counterexample only needs the pinned
canonical geometry. [PREDECESSOR.json](PREDECESSOR.json) identifies the
verbatim explanatory cut35 proof retained in vendor/. Frozen inputs and the
selected record are unchanged.

The normal-plane live union has 78 sites. Three disjoint fiber sections have
sizes 10,16,16. Their fixed coefficient identities are

    c_a restricted = q2+q3,
    c_b restricted = q1-q2.

The remaining 76 coordinates include 34 common zero sites. All cut/support
indices refer to sorted full 120-root indices, and all are actual live P112
sites. This distinction is checked, not assumed from index ranges.

## Reproduce

From the repository root, with standard-library CPython 3.12:

```sh
python3.12 -W error -B scripts/research_package.py --package research/p112-mixed566-cut36-witness
```

The registered commands separately run the bounded witness reconstruction,
primary exact certificate verifier, separate root/label and integer
constraint reconstruction, and behavioral controls. Direct commands for a
Git-free export are

```sh
python3.12 -W error -B research/p112-mixed566-cut36-witness/construct.py
python3.12 -W error -B research/p112-mixed566-cut36-witness/verify.py
python3.12 -W error -B research/p112-mixed566-cut36-witness/crosscheck.py
python3.12 -W error -B research/p112-mixed566-cut36-witness/test_controls.py
```

The controls accept the original certificate and a valid sign-gauge change,
reject nine actual CLI mutants, and reject altered/linked geometry sources.
Set TMPDIR to your external run directory to choose where disposable control
fixtures live. The scripts remove their fixtures. construct.py also accepts
`--output PATH` outside the repository to save its deterministic candidate.

## Limits

This is an actual support/code counterexample. No new kappa, literal caller,
full C5, native/physical implementation, restoration/hosting/consumer bill,
supplier admission or selected-frontier change is claimed. Historical
capacity/cut35 replays, Lean, Docker, the selected cold replay, independent
human review and proof-kernel formalization are unrun. The two checkers share
the specified root convention and certificate, so their agreement is
computational corroboration with the stated scope.

## Open next questions

An actual decoder caller may constrain the deleted coordinates more strongly
than an arbitrary common cut. To use or exclude this witness for that caller,
first identify its exact discarded pieces and coefficient columns and test
whether they realize this 36-set. That caller contract is the blocker. No
larger arbitrary-cut census or new construction round is justified by this
sharpness result alone. Structured details are in [TASK.json](TASK.json).

## Credit

Nick Petalas, with the PR3368/3353/3325/3299/3295/3324/3292 and sharp A2
incidence20 lineage; PR3278/3269/3267/3260/3262; David Arias; DreamingOfClouds
and PR3154; joaqcoo and the E8/P112/root-simplex sources. Apache-2.0.
Automated assistance was used for research and implementation. No independent
human or proof-kernel review is claimed.
