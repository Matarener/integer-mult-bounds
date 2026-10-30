# Actual native phase fusion: 1024 fewer real writes at f=1

At the actual PR3945 lender333 boundary, a lazy signed-affine warp followed by its next rank-one child gives the same four arbitrary caller-array outputs as a materialized warp. Against a materialized comparator that already shares consumer loads and phase negations, it saves **1024 real writes** and no real reads or negations. Recursive-child and owner-width deltas are zero. This finite runtime traffic result does not establish a native tariff, total cost, a general-f lift, an admitted supplier or a new κ.

[PROOF.md](PROOF.md) states the exact boundary, actual canonical-frame compensation from PR4002, complete counted runtime vector, eight-word constructive scratch schedule, setup/address limitations and comparison scope. [RESULT.json](RESULT.json) is replayed rather than trusted. All2048 complex basis columns of the four-array map agree for all three declared implementations. The exact source warp and successor child and all512 columns of each compensated frame are independently checked. Eight semantic controls must reject. The stronger comparator was added after adversarial review; the larger read/NEG gains of the stage-separated comparator are not claimed as intrinsic savings.

## Reproduce

From repository root:

```sh
python3 scripts/research_package.py --package research/staged544-paid-native-fusion --check-only
python3 scripts/research_package.py --package research/staged544-paid-native-fusion
```

The ready manifest runs standard-library Python normal and `-O`, each bounded to600 seconds. Direct read-only replay is `python3 -B research/staged544-paid-native-fusion/verify.py`; use an isolated bytecode cache for direct runs. `generate.py OUTPUT` optionally regenerates BOUNDARY.json with the retained compiler; it is not part of independent verification. `--record` is an explicit author-only receipt generator and is not registered.

The historical base20ecf2891d80b5acf18d980b2164fb44ea7faa90 records priority6 and selected κ0.001672660197076918; it is provenance only. [SOURCES.json](SOURCES.json) pins all external public bytes by commit/path/Git blob/SHA256. Their public PR heads may not be ancestors of main, so the package verifier checks retained exact bytes; generic provenance pins cover the base card and selected record. Package-local files automatically select this replay. An official committed export supports Git-free replay; full source provenance validation uses Git history.

## Open next questions

Structured fields are in [TASK.json](TASK.json).

1. Can this actual lazy interface be lifted to the general-f native representation with bounded address/control, precision and dirty scratch? Start by specifying the source owner's allowed physical operations for lender333 and mapping each loop to them. The current f=1 contract is the blocker.
2. Does the1024-write benefit survive all setup and an optimized downstream consumer/child implementation? Start with a declared tariff and a stronger fused comparator, then charge table composition,512-point cycle preparation and address arithmetic. A measured wall-clock claim is presently unsupported.
3. Can a useful general-f implementation affect the full supplier bound? Preserve the rank-one child and exact source widths, rerun the source-bound owner/native/parent chain, and only then evaluate the selected inequality. The present recursive/owner deltas are zero.

## Credit and assistance

New dense circuits, compensation checks, boundary construction and proof: Chris R / Clear1nsight with substantial OpenAI Codex assistance, Apache-2.0. ToikY's [PR4002](https://github.com/CrocSwap/integer-mult-bounds/pull/4002), head d593941ea0a4926021cba9d01fe60500579e464f, supplies the explicit K/J phase-tag handoff. [PR3987](https://github.com/CrocSwap/integer-mult-bounds/pull/3987), head fc536202fdaa924158789a5ef59ac079bbe21922, supplies exact signed recipes and the independently written sparse evaluator. Dugongue's [PR3945](https://github.com/CrocSwap/integer-mult-bounds/pull/3945), head91f81d131252db704f945891da1ea54e29d46b8b, supplies the actual two native words and compiler lineage. Retained notices preserve dataisfire, CinnaDavis, Tekalign, icekylinx, DreamingOfClouds, Sagar Thakrar, roger-sato, ArhamTahir and earlier named authors; see frozen/NATIVE-LINEAGE-NOTICE, frozen/SOURCE-CREDITS.md and frozen/NOTICE-PR3945.md. Original source notices are copied unchanged and remain their authors' statements. The in-session adversarial review was another OpenAI agent, not independent human or third-party review.
