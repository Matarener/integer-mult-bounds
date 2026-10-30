# Independent P104 high-rank and private native subset

This package preserves and makes portable one completed qualification of exactly
182 ordered native frame pairs in Ali Romman's [PR5545](https://github.com/CrocSwap/integer-mult-bounds/pull/5545),
head `18968423711fd902aaee1099979497d55603e1dc`. It covers 246 local paid
occurrences, all 178 previously uncovered rank>=4 pairs and all 11 private
returns (including four lower-rank pairs). It changes no source word, complete
paid/target profile, economic ceiling, selected record or kappa.

Canonical base: `32890bc5de034ab8fc93ac88ead7279a6a416d04`.
[PR5548](https://github.com/CrocSwap/integer-mult-bounds/pull/5548) and
[PR5550](https://github.com/CrocSwap/integer-mult-bounds/pull/5550) supply the
inherited 42-pair receipts, source/compiler bindings and forward caller layer.
Those receipts are retained as inputs, not rerun or claimed newly independent.
Combined coverage is 224 of 2,981 pairs and 254 of 3,624 local paid occurrences.
The explicit residual is 2,757 public rank1-3 pairs / 3,370 paid occurrences:
1,876 rank1, 523 rank2 and 358 rank3. Main adapters are a separate category.

## Evidence and proof boundary

The original normal/-O pair completed in 24.449 seconds with sampled peak
86.71 MiB under the 150-second/512-MiB guard. All 186,143 scientific bytes
matched, without exclusions: SHA256
`fa2fe7ce93e72569f611ca810f440e6b77d92221350c51b7b6ab19ca34d6c64b`.
These are original local receipts; portable and hosted replay status must be
reported separately at the publication commit. No hosted replay is implied here.

The unchanged checker compares all 18 signed Pauli images and an independent
exact integer Gaussian-dyadic column. For validated Clifford gates, equal Pauli
conjugations imply a scalar quotient; the nonzero exact column fixes that
scalar, including absolute phase. See [PROOF.md](PROOF.md). Thirteen scoped
fault controls reject phase, inverse, boundary, direction, rank, missing paid
occurrence and corrupt sources. Mode equality is reproducibility, not a second
independent algorithm or independent human/formal review.

The complete local paid profile remains
`{1:2428,2:557,3:389,4:112,5:107,6:17,7:13,9:1}`; inherited complete caller
bill remains 69,912 paid jobs / 12,814 productive fields. Remaining native maps,
uniform precision/tape/storage, owned-erasure framework and complete compiler/
outer applicability remain open. The source all-input/all-width convention
and tensor substitution are retained premises. No complete P104 admission follows.

## Reproduce

Python3.12, standard library, Linux/POSIX. From repository root:

```sh
python3 -B scripts/research_package.py --package research/p104-native-subset-independent-audit --check-only
python3 -B scripts/research_package.py --package research/p104-native-subset-independent-audit
```

The registered commands run normal and optimized Python serially. Each uses
a 70-second isolated scientific subprocess and a 512-MiB virtual-address cap;
root execution also retains the shared serial RSS/time guard. Fresh private
bytecode paths prevent stale pyc substitution. The capsule keeps original
checker and inventory bytes plus only their exercised runtime closure; imported
predecessor `main()` functions are not executed. No network or pending Git
object is needed by the standalone verifier. Generic metadata provenance needs
full base history. Canonical compiler/literal modules are live declared inputs,
byte-equal to retained capsule modules. INPUTS/REQUEST, nomination, inventory,
previous complete receipts, expected output and original evidence are all
covered by CAPSULE-INVENTORY.json before scientific import. The frozen original
runner is retained to authenticate REQUEST; the portable verifier launches the
original checker directly and never overwrites old receipts.

A static check invokes `verify.py --integrity-only`; it authenticates bytes
without loading the native compiler or running science. This does not validate
the mathematics. Static fault probes separately block subprocess launch and
prove modified inputs fail before science. Source export reproduction uses the
same direct verifier with the two canonical live inputs retained.

## Open next questions

The structured questions in [TASK.json](TASK.json) identify the residual native
bands, source transfer and retained resource/applicability premises. Reassess
before selecting a band: no whole-residual resource budget is claimed.

The newer [PR5551](https://github.com/CrocSwap/integer-mult-bounds/pull/5551),
head `79072da5404a01056df2af2e4132324b01c72366`, proposes a changed physical
word and map set. This package qualifies only the frozen PR5545 domain. It
supplies no PR5551 admission or automatic transfer of pair/occurrence coverage.
Compare exact changed frames and ownership before reusing any receipt; review
the changed economic mechanism as a separate task.

## Credit

Ali Romman/#5544/#5545; Gareth Davidson/#2305; David Arias/#2152;
Cinna Davis/#2219/controller; Jacob Alan Sussman, zxv, Cao Yifan and retained
Clifford/native/geometry/tensor/compiler/analytic contributors. The compiler
and literal gate definitions are credited reuse. New inventory, independent
check and publication: Chris R/Clear1nsight with substantial OpenAI Codex
assistance. Apache-2.0; source notices remain intact. No independent human or
formal acceptance claimed.
