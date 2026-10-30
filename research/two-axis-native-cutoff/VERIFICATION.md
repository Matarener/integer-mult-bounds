# Verification record

Environment: CPython 3.12.13, Linux x86_64, standard library only, 2026-10-25.
The scientific base and publication refresh both resolve canonical main to
`32890bc5de034ab8fc93ac88ead7279a6a416d04`. PR5369 remains merged at
`18354f41de4dc7bfda4692e814cf1d91a6d619ef`; its source bytes, relevant
instructions, priorities and selected record were unchanged.

These checks passed:

```sh
python3.12 -B scripts/research_package.py --package research/two-axis-native-cutoff --check-only
python3.12 -B scripts/research_package.py --package research/two-axis-native-cutoff
python3.12 -I -O -B research/two-axis-native-cutoff/verify.py
python3.12 -B scripts/check_research_commit.py --package research/two-axis-native-cutoff --check-source-history
python3.12 -B scripts/export_research_package.py export --package research/two-axis-native-cutoff --output /tmp/imb-two-axis-cutoff.tar
python3.12 -B scripts/export_research_package.py check /tmp/imb-two-axis-cutoff.tar
```

The official committed export was extracted with Python's `data` tar filter
to a fresh directory outside the checkout. Its verifier passed using the
absolute interpreter path, `-I -O -B`, `PATH=/nonexistent` and empty
`PYTHONPATH`. The exported package needs neither Git nor predecessor code
imports. Normal and optimized runs compare the entire deterministic receipt.
Proof-relevant checks use explicit exceptions, so optimization cannot remove
them. Committed-byte/source-history and export checks authenticate transport
and provenance; they do not establish mathematical acceptance.

The receipt covers 128 character minima against all 625 count normal forms,
fixed-width realizations through 13, 24 affine maps, 128 phase polynomials,
576 affine sign-composition checks, 3,072 phase pullbacks, all 15 nonempty
pointwise stabilizers, all 1,364 relevant below-threshold ordered tuples,
and 2,856 direct phase-projector sums on count classes through width 9.
All four first witnesses have diagonal entry one and 24 distinct signed
outputs. Controls detect missing signs, an omitted quadratic phase,
tensor-powered external coefficients and phase-only false acceptance.

The analytic Fourier/stabilizer argument and multiplicity formula in
PROOF.md establish the all-width theorem and necessity. Finite results
corroborate these arguments; this is not an extrapolation of a small-width
census. Automated subagents separately derived the proof, implemented the
literal checker and reviewed the kernel/test-set implications. This is
substantial AI-assisted evidence, not independent human or proof-kernel
acceptance. No general-axis theorem, physical invoice, complete native
supplier/outer/selected cold replay, Lean or Docker run is claimed.

Hosted CI is separate from this local verification record and is reported
on the pull request. The frozen predecessor and selected frontier remain
unchanged.

Submission overlap refresh: 379 open PR bodies at 06:25:52 UTC and 4,797
Discussion records through 06:27:01 UTC, both with complete pagination.
All 7,402 tracked base local notes were searched, along with this package's
then-untracked README/TASK notes; no coverage warnings were reported. The
original #5369 result/handoff, the complementary one-axis audit, related
full-Clifford/caller work and this round's own claim were distinguished.
No matching sharp two-axis theorem appeared in that coverage. Arbitrary
code diffs and unpublished work remain outside the search.
