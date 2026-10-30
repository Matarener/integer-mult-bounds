# Independent final H25 evidence review

**ACCEPT_LOCAL_COMBINED_QUALIFICATION.** The retained evidence satisfies the declared complete wall/CPU target and noise gates. This was a read-only artifact/source audit: no scientific imports, compilation, replay or additional performance run.

## Samples and independently recomputed result

The actual spent-before ledger preserves the predeclared **B1 C1 C2 B2 B3 C3** order from `control/QUALIFICATION-v4.json`. Every sample binds stage `558eebbc1dc65e42bbcb3ffd9973f8bc86641a3539493ecc1d53d8077c39cdbc` and the reviewed runner. CPU is raw GNU time user plus system; wall is the outer runner's elapsed time.

| Sample | Wall seconds | CPU seconds |
| --- | ---: | ---: |
| B1 | 27.168587597 | 27.09 |
| C1 | 21.477875710 | 21.42 |
| C2 | 21.178499807 | 21.13 |
| B2 | 27.378558369 | 27.30 |
| B3 | 27.143407927 | 27.06 |
| C3 | 24.773106943 | 23.27 |

Wall medians are **27.168587597 → 21.477875710 seconds**, a **20.94592465% reduction**. The 5.690711887-second saving exceeds the maximum within-arm range, 3.594607136 seconds. CPU medians are **27.09 → 21.42 seconds**, a **20.93023256% reduction**; the 5.67-second saving exceeds the maximum range, 2.14 seconds. Both reductions exceed 15%. All values reproduce `validation/COMBINED-GATE.json`. The slower C3 remains included. No pilot percentage is added or substituted, and nested phase timings are not summed as savings.

## Source, correctness and complete cost evidence

All **160 staged files** match their declared bytes and modes; actual lane, integration and runner hashes match the independent source review. Original and new source-custody receipts agree. Actual driver and immutable reference-driver identities remain separate. Combined normal and optimized finite passes precede the first qualification sample.

All six science records equal the original anchor. Direct hashing verifies **36 retained files**: the complete typed return, exact side witness, ordered rank trace, side result, certificate and original stdout for each sample. Common typed-return SHA256 is `542e4fd73d38b88122d1bf0fffa5f3b092cc4681a14012162daef47e89363cfd`; witness SHA256 is `4b170c1dbfc33c7cb141a2284c6fd69eac7b6d100971d3e9ee625502b5893f82`. Every full run records 238,685 native complements and 59,959 native Gram calls with zero arithmetic fallbacks. Ordered-complement digest/count/byte receipts agree; the complete stream is summarized rather than retained, so this audit does not independently rehash its 55,839,507 underlying bytes.

Every candidate contains both successful cold builds, original controls and the complete new union inside the measured process. Native binary hashes agree with build receipts. The new union matches the preceding normal finite record, including 23 set cases and five source-pin policy cases, 1,659 guard mutation/action pairs, trace controls and five encoder-entry rejection actions. The original observer remains independent. Every baseline retains its native build and original controls. Each candidate records one admitted/expired lease, 2,300 private sets and the actual local Fraction source/profile. Source authentication, portability reference hashing, setup, observations, serialization and receipts remain paid.

The complete ledger has **22 retained attempts totaling 332.099907814 seconds**, including the failed optimized control attempt at **2.822723142 seconds**. Every spent-before value reconciles. Qualification runs remain below 180 seconds and the 1-GiB sampled process-group cap; the largest observed qualification sample is 450,019,328 bytes. These are recorded resource observations, not proof against unobserved instantaneous peaks.

## Metadata corrections and boundaries

Two documentation findings were resolved transparently. The old prequalification census survives as `validation/CALL-CENSUS-PILOTS.json`; the final census now binds the v4 C1 lease and combined gate. The original admission's intermediate review digest was not retained. `control/ADMISSION-REVIEW-PROVENANCE.json` acknowledges that gap, preserves the original admission and binds verified readonly final-review snapshots; it does not claim recovery of the missing intermediate text. Neither correction changes measured sources or samples.

No remaining blocker was found for this local qualification. The result concerns this frozen historical full caller on local CPython 3.12.3, including its observations and validation bill. It establishes neither universal performance nor a bare-CLI, selected-frontier or kappa improvement. Publication-wrapper review and actual hosted correctness/digest validation remain separate obligations.
