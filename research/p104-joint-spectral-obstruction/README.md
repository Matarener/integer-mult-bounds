# Joint bank mixing does not remove the dyadic Gram spectral obstruction

This contribution was produced by Nick Petalas. It is a scoped written proof
with finite exact corroboration. No new kappa is claimed.

Chris R / Clear1nsight's [PR #3979](https://github.com/CrocSwap/integer-mult-bounds/pull/3979)
leaves joint bank mixing outside its exclusion of a free spectral split of the
P104 Gram pair. The new result closes that particular escape when one persistent
Gaussian-dyadic invertible code is used at both endpoints. The code can mix both
banks and any finite number of arbitrary scratch coordinates, provided all
scratch returns identically.

For the complete pair F = upper(-I tensor A) lower(A tensor I), reduction modulo
13 gives ranks 1664, 128 and zero for F-I, its square and its cube. Its nilpotent
Jordan blocks have sizes 3, 2 and 1 with multiplicities 128, 1408 and 18432.
A spectral-projector pair with coefficients alpha beta = 169 has rank at most
832 after subtracting the identity. Similarity and identity scratch preserve
the discrepancy.

Every exact Gaussian-dyadic endpoint correction consequently has matrix rank
at least 832, or at least 1664 when both coefficients vanish modulo 13, including
alpha = beta = 13. Both bounds are attained in the modular relaxation. An exact
dyadic attaining correction is not supplied. Matrix rank is not a native-call
tariff or a complete recursive invoice.

[PROOF.md](PROOF.md) gives the general n,r statement, the kernel calculation,
the stable obstruction and the exact modular sharpness argument. The predecessor
premises n = 104, A² = 13A and rank(A modulo 13) = 8 are cited and source-bound.
Its original code, counts and proofs are not replayed or audited here.

## Reproduce

From the repository root, using CPython 3.12 and its standard library:

```sh
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -B research/p104-joint-spectral-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -I -W error -O -B research/p104-joint-spectral-obstruction/verify.py
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/research_package.py --package research/p104-joint-spectral-obstruction
/Users/nick/git/integer-mult-bounds/.venv/bin/python3.12 -B scripts/check_research_commit.py --package research/p104-joint-spectral-obstruction --check-source-history --check-modes
```

Another CPython 3.12 executable may replace the local path. Direct output is a
generated JSON receipt bound to package and premise-file hashes, followed by
`PASS_P104_JOINT_SPECTRAL_OBSTRUCTION modular_repair=832 balanced=1664 no_new_kappa`.
The launcher also checks metadata and exact source pins.

The finite checks cover 20 literal atomic tensor pairs over five prime fields,
80 small direct-sum assemblies, all 9216 canonical P104 components and all 21632
Jordan coordinates. An explicit coordinate permutation matches the 832 projector
arrows to the attaining modular repair. Seventy-five stable fixtures cover every
zero-product coefficient residue pair with zero, one and three restored scratch
coordinates. Controls retain a rational normalization using 1/13, an omitted
stage, unreturned scratch and invalid square-zero source parameters.

The program reads one pinned premise file. It builds no dense matrix larger
than 32 by 32; the full canonical witness uses bounded coordinate dictionaries.
Python allocates managed objects during the finite run. These explicit size
bounds replace a fixed-allocation implementation. Every function is below
60 lines, and the registered commands enable warnings as errors and exercise
normal and optimized execution. No external static analyzer is required.

## Limits

One common code at entry and exit, the Gaussian-dyadic coefficient ring and
identity return of the entire scratch space are essential. New interleaved
operations, distinct endpoint codes, other spectral targets and odd-denominator
codes are not excluded. No physical producer/consumer implementation or paid
rank conversion follows from this endpoint invariant.

No selected native, caller, compiler, precision, storage, tape or analytic replay
was run. Independent human and formal proof-kernel review are unclaimed. The
selected frontier and frozen predecessors are unchanged.

## Open next questions

Can an exact Gaussian-dyadic correction attain rank 832? Start with the displayed
n = 2, r = 1 integral matrix in the proof and require the same dyadic-invertible
code at both endpoints. A modular solution alone does not establish a lift.
Only after an exact endpoint exists should its native access and complete paid
restoration costs be priced. [TASK.json](TASK.json) records the question and
blocker explicitly.

## Predecessor credit

Chris R / Clear1nsight owns PR3979's tensor code, original bank-separate
obstruction, scalar words and invoice. PR3961 supplies the preceding code
mismatch; PR3882, PR3940, PR3943 and PR3954 retain the caller lineage. ToikY's
literal-word audit and the native, geometry and compiler authors credited by
PR3979 retain their contributions. No predecessor construction credit is claimed.
Nilpotent Jordan classification and rank inequalities are classical. New work
is under Apache-2.0.
